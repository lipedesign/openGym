# Shared pieces of the HexGym body pipeline: the muscle model (labels, seams, relief) and the looks.
import bpy, math, heapq
from mathutils import Vector, Matrix

def log(*a):
    print("[hex]", *a, flush=True)

def lin(h, a=1.0):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (a,)

# ================================================================ muscle structure
# label -> (group key used by the openGym body map, name, size). Every label exists once per side.
MUSCLES = {
    "chest_up":     ("chest",       "Peitoral, parte superior", "L"),
    "chest_low":    ("chest",       "Peitoral, parte média e inferior", "L"),
    "delt_front":   ("deltoids",    "Deltoide anterior", "M"),
    "delt_side":    ("deltoids",    "Deltoide lateral", "M"),
    "delt_rear":    ("deltoids",    "Deltoide posterior", "M"),
    "biceps":       ("biceps",      "Bíceps", "M"),
    "triceps":      ("triceps",     "Tríceps", "M"),
    "brachiorad":   ("forearm",     "Braquiorradial", "S"),
    "forearm_flex": ("forearm",     "Flexores do punho", "S"),
    "forearm_ext":  ("forearm",     "Extensores do punho", "S"),
    "traps_up":     ("trapezius",   "Trapézio superior", "M"),
    "traps_mid":    ("trapezius",   "Trapézio médio", "M"),
    "traps_low":    ("trapezius",   "Trapézio inferior", "S"),
    "scap":         ("upper-back",  "Romboides e infraespinal", "M"),
    "lats":         ("upper-back",  "Latíssimo do dorso", "L"),
    "erector":      ("lower-back",  "Eretores da espinha", "M"),
    "abs_1":        ("abs",         "Reto abdominal, 1º gomo", "S"),
    "abs_2":        ("abs",         "Reto abdominal, 2º gomo", "S"),
    "abs_3":        ("abs",         "Reto abdominal, 3º gomo", "S"),
    "abs_low":      ("abs",         "Reto abdominal, parte inferior", "S"),
    "obliques":     ("obliques",    "Oblíquo externo", "M"),
    "serratus":     ("serratus",    "Serrátil anterior", "S"),
    "glute_max":    ("gluteal",     "Glúteo máximo", "L"),
    "glute_med":    ("gluteal",     "Glúteo médio", "M"),
    "hip_flex":     ("hip-flexors", "Flexores do quadril", "S"),
    "rect_fem":     ("quadriceps",  "Reto femoral", "L"),
    "vast_lat":     ("quadriceps",  "Vasto lateral", "L"),
    "vast_med":     ("quadriceps",  "Vasto medial", "M"),
    "adductors":    ("adductors",   "Adutores", "M"),
    "biceps_fem":   ("hamstring",   "Bíceps femoral", "L"),
    "semitend":     ("hamstring",   "Semitendíneo e semimembranáceo", "L"),
    "gastro_med":   ("calves",      "Gastrocnêmio, cabeça medial", "M"),
    "gastro_lat":   ("calves",      "Gastrocnêmio, cabeça lateral", "M"),
    "soleus":       ("calves",      "Sóleo", "S"),
    "tibialis":     ("tibialis",    "Tibial anterior", "S"),
}
AMP = {"L": 0.0085, "M": 0.006, "S": 0.0038}   # relief height of each muscle belly (m)

def base_of(label):
    if label is None: return None
    b = label.split(".")[0]
    return "serratus" if b.startswith("serratus") else b

FWD = Vector((0, -1, 0))

class Skeleton:
    """Rest-pose joint positions in the body mesh space (T-pose, front = -Y, left = +X)."""
    def __init__(self, arm):
        RW = arm.matrix_basis.copy()          # the Fix parent was identity when the body was built
        self.J = {}
        for b in arm.data.bones:
            self.J[b.name] = RW @ b.head_local
        J = self.J
        self.spine = [J[n] for n in ("Pelvis", "Spine1", "Spine2", "Spine3", "Neck")]
        self.zP, self.zSh = J["Pelvis"].z, (J["L_Shoulder"].z + J["R_Shoulder"].z) / 2

    def spine_y(self, z):
        S = self.spine
        if z <= S[0].z: return S[0].y
        for a, b in zip(S, S[1:]):
            if a.z <= z <= b.z:
                return a.y + (b.y - a.y) * (z - a.z) / max(1e-6, b.z - a.z)
        return S[-1].y

def _seg(p, a, b):
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    r = p - (a + ab * t)
    if r.length > 1e-9: r.normalize()
    return t, r

def label_of(p, bn, sk):
    """Which muscle a rest-pose surface point belongs to (None = skin, bone or joint)."""
    J = sk.J
    s = "L" if p.x > 0 else "R"
    sx = 1 if s == "L" else -1
    ax = abs(p.x)
    z = p.z
    def L(name): return name + "." + s
    if bn is None or bn in ("Head",) or bn.endswith(("_Wrist", "_Ankle", "_Foot")):
        return None
    sh = J[s + "_Shoulder"]
    # deltoid cap: around the shoulder joint, lateral to the deltopectoral groove
    if bn in (s + "_Collar", s + "_Shoulder") and (p - sh).length < 0.112 and p.x * sx > sh.x * sx - 0.048:
        dy = p.y - sh.y
        return L("delt_front" if dy < -0.022 else "delt_rear" if dy > 0.026 else "delt_side")
    torso = bn in ("Pelvis", "Spine1", "Spine2", "Spine3", "Neck", s + "_Collar")
    if torso:
        cy = sk.spine_y(z)
        th = math.degrees(math.atan2(ax, -(p.y - cy)))      # 0 front, 90 side, 180 back
        low = 0.05 + 0.5 * max(0.0, ax - 0.05)               # lower border of the pec
        if z > 0.19 and th > 72 and ax < 0.17:
            return L("traps_up")
        if th < 64 and 0.006 < ax < 0.172 and low <= z < 0.228 - 0.3 * max(0.0, ax - 0.11):
            return L("chest_up" if z > 0.168 else "chest_low")
        if th < 42 and ax < 0.068 and -0.25 < z < low - 0.004:
            return L("abs_1" if z >= 0.0 else "abs_2" if z >= -0.06 else "abs_3" if z >= -0.12 else "abs_low")
        if 44 < th < 108 and 0.0 <= z < min(low, 0.125):
            return L("serratus%d" % int(z / 0.034))
        if 34 < th < 118 and -0.215 < z < 0.0:
            return L("obliques")
        if th > 118:
            edge = 0.03 + 0.55 * (z + 0.03)
            if 0.09 <= z < 0.19 and ax < 0.1:
                return L("traps_mid")
            if -0.03 <= z < 0.09 and ax < edge:
                return L("traps_low")
            if 0.05 <= z < 0.19 and ax < 0.172:
                return L("scap")
        if th > 96 and -0.12 <= z < 0.05:
            return L("lats")
        if th > 128 and -0.2 <= z < -0.03 and ax < 0.066:
            return L("erector")
        if th > 122 and J[s + "_Hip"].z - 0.15 < z < sk.zP + 0.035 and ax < 0.2:
            return L("glute_max")
        if 84 < th <= 140 and sk.zP - 0.07 < z < sk.zP + 0.075 and ax > 0.075:
            return L("glute_med")
        return None
    def ang(r):
        m = r.dot(Vector((-sx, 0, 0)))
        return math.degrees(math.atan2(m, r.dot(FWD)))       # 0 front, +90 medial, -90 lateral, 180 back
    if bn == s + "_Hip":
        t, r = _seg(p, J[s + "_Hip"], J[s + "_Knee"])
        a = ang(r)
        if abs(a) > 108 and t < 0.17: return L("glute_max")
        if t < 0.14 and 8 < a < 72: return L("hip_flex")
        if abs(a) < 22 and 0.1 < t < 0.9: return L("rect_fem")
        if -116 < a <= -22 and 0.1 < t < 0.93: return L("vast_lat")
        if 22 <= a < 78 and 0.56 < t < 0.95: return L("vast_med")
        if 22 <= a < 140 and 0.06 < t < 0.72: return L("adductors")
        if abs(a) >= 126 and 0.15 < t < 0.93: return L("biceps_fem" if a < 0 else "semitend")
        return None
    if bn == s + "_Knee":
        t, r = _seg(p, J[s + "_Knee"], J[s + "_Ankle"])
        a = ang(r)
        if -72 < a < 2 and 0.08 < t < 0.78: return L("tibialis")
        if abs(a) > 114 and 0.04 < t < 0.56: return L("gastro_med" if a > 0 else "gastro_lat")
        if (abs(a) > 72 and 0.56 <= t < 0.82) or (72 < abs(a) <= 114 and 0.24 < t < 0.56): return L("soleus")
        return None
    def ang_arm(r):
        return math.degrees(math.atan2(r.z, r.dot(FWD)))      # 0 front, 90 up, -90 down, 180 back
    if bn == s + "_Shoulder":
        t, r = _seg(p, sh, J[s + "_Elbow"])
        a = ang_arm(r)
        if abs(a) < 56 and 0.2 < t < 0.93: return L("biceps")
        if abs(a) > 114 and 0.14 < t < 0.93: return L("triceps")
        return None
    if bn == s + "_Elbow":
        t, r = _seg(p, J[s + "_Elbow"], J[s + "_Wrist"])
        a = ang_arm(r)
        if -26 < a < 32 and 0.02 < t < 0.6: return L("brachiorad")
        if -155 < a <= -26 and 0.04 < t < 0.78: return L("forearm_flex")
        if 32 <= a < 165 and 0.04 < t < 0.78: return L("forearm_ext")
        return None
    return None

TETRA = [Vector(v).normalized() for v in ((1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1))]

def densify(body, levels=2):
    """Subdivide the body at rest (vertex groups carried over) so muscles can have clean borders."""
    saved = [(m, m.show_viewport, m.show_render) for m in body.modifiers]
    for m, _, _ in saved: m.show_viewport = m.show_render = False
    ss = body.modifiers.new("Dense", 'SUBSURF'); ss.levels = ss.render_levels = levels
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(body.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    body.modifiers.remove(ss)
    for m, v, r in saved: m.show_viewport, m.show_render = v, r
    for mat in body.data.materials: me.materials.append(mat)
    body.data = me
    log("dense verts", len(me.vertices), "groups", len(body.vertex_groups))
    return me

def build_muscles(body, sk, prim=(), sec=(), relief=1.0):
    """Label every vertex, carve the muscle relief, and write the attributes the looks read:
    lab (seam field), prim/sec (activation), labcol (debug colour)."""
    me = body.data
    n = len(me.vertices)
    gname = {g.index: g.name for g in body.vertex_groups}
    labels = []
    for v in me.vertices:
        bn = gname[max(v.groups, key=lambda g: g.weight).group] if len(v.groups) else None
        labels.append(label_of(v.co, bn, sk))
    nb = [[] for _ in range(n)]
    for e in me.edges:
        a, b = e.vertices
        nb[a].append(b); nb[b].append(a)
    # distance to the nearest border (multi-source Dijkstra over the surface)
    INF = 1e9
    dist = [INF] * n
    hp = []
    co = [v.co.copy() for v in me.vertices]
    for i in range(n):
        if any(labels[j] != labels[i] for j in nb[i]):
            dist[i] = 0.0; hp.append((0.0, i))
    heapq.heapify(hp)
    while hp:
        d, i = heapq.heappop(hp)
        if d > dist[i]: continue
        for j in nb[i]:
            if labels[j] != labels[i]: continue
            nd = d + (co[i] - co[j]).length
            if nd < dist[j]:
                dist[j] = nd; heapq.heappush(hp, (nd, j))
    maxd = {}
    for i, l in enumerate(labels):
        if l is not None and dist[i] < INF:
            maxd[l] = max(maxd.get(l, 0.0), dist[i])
    # relief: a rounded belly per muscle and a shallow groove along every border
    disp = [0.0] * n
    for i, l in enumerate(labels):
        d = dist[i] if dist[i] < INF else 1.0
        g = -0.0026 * max(0.0, 1.0 - d / 0.009)
        if l is not None:
            R = min(0.05, max(0.012, 0.6 * maxd.get(l, 0.02)))
            k = min(1.0, d / R)
            g += AMP[MUSCLES[base_of(l)][2]] * (1.0 - (1.0 - k) ** 2)
        disp[i] = g * relief
    disp = [(disp[i] * 2 + sum(disp[j] for j in nb[i])) / (2 + len(nb[i])) if nb[i] else disp[i] for i in range(n)]
    for i, v in enumerate(me.vertices):
        v.co = co[i] + v.normal * disp[i]
    me.update()
    # seam field: each muscle gets one of four directions (neighbours differ), the vector's length dips at borders
    keys = sorted({l for l in labels}, key=lambda x: (x is None, x or ""))
    adj = {k: set() for k in keys}
    for e in me.edges:
        a, b = labels[e.vertices[0]], labels[e.vertices[1]]
        if a != b: adj[a].add(b); adj[b].add(a)
    col = {}
    for k in sorted(keys, key=lambda k: -len(adj[k])):
        used = [col[o] for o in adj[k] if o in col]
        col[k] = min(range(4), key=lambda c: used.count(c))
    clash = sum(1 for k in keys for o in adj[k] if col.get(o) == col[k]) // 2
    vec = [TETRA[col[l]].copy() for l in labels]
    for _ in range(2):
        vec = [(vec[i] * 2 + sum((vec[j] for j in nb[i]), Vector())) / (2 + len(nb[i])) if nb[i] else vec[i] for i in range(n)]
    def member(l, wanted):
        if l is None: return False
        b = base_of(l)
        return b in wanted or MUSCLES[b][0] in wanted
    pv = [1.0 if member(l, prim) else 0.0 for l in labels]
    sv = [1.0 if (member(l, sec) and not member(l, prim)) else 0.0 for l in labels]
    for _ in range(2):
        pv = [(pv[i] * 2 + sum(pv[j] for j in nb[i])) / (2 + len(nb[i])) if nb[i] else pv[i] for i in range(n)]
        sv = [(sv[i] * 2 + sum(sv[j] for j in nb[i])) / (2 + len(nb[i])) if nb[i] else sv[i] for i in range(n)]
    import random
    rnd = random.Random(7)
    pal = {k: ((rnd.random() * 0.8 + 0.2), (rnd.random() * 0.8 + 0.2), (rnd.random() * 0.8 + 0.2), 1.0) for k in keys}
    pal[None] = (0.08, 0.08, 0.1, 1.0)
    for name in ("lab", "prim", "sec", "labcol"):
        if name in me.attributes: me.attributes.remove(me.attributes[name])
    a = me.attributes.new("lab", 'FLOAT_VECTOR', 'POINT')
    a.data.foreach_set("vector", [c for v in vec for c in v])
    me.attributes.new("prim", 'FLOAT', 'POINT').data.foreach_set("value", pv)
    me.attributes.new("sec", 'FLOAT', 'POINT').data.foreach_set("value", sv)
    me.attributes.new("labcol", 'FLOAT_COLOR', 'POINT').data.foreach_set("color", [c for l in labels for c in pal[l]])
    found = sorted({base_of(l) for l in labels if l})
    log("labels", len(keys), "muscles", len(found), "seam clashes", clash)
    log("missing", [m for m in MUSCLES if m not in found])
    return found

# ================================================================ looks
def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    return m, nt, nt.nodes.new("ShaderNodeOutputMaterial")

def sock(node, ident, out=False):
    for s in (node.outputs if out else node.inputs):
        if s.identifier == ident: return s
    raise KeyError(ident)

def put(nt, v, s):
    if isinstance(v, bpy.types.NodeSocket): nt.links.new(v, s)
    else: s.default_value = v

def mixc(nt, fac, a, b, blend='MIX'):
    m = nt.nodes.new("ShaderNodeMix"); m.data_type = 'RGBA'; m.blend_type = blend
    put(nt, fac, sock(m, "Factor_Float")); put(nt, a, sock(m, "A_Color")); put(nt, b, sock(m, "B_Color"))
    return sock(m, "Result_Color", True)

def attr(nt, name):
    a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_type = 'GEOMETRY'; a.attribute_name = name
    return a

def gt(nt, sock_, v):
    g = nt.nodes.new("ShaderNodeMath"); g.operation = 'GREATER_THAN'; g.inputs[1].default_value = v
    nt.links.new(sock_, g.inputs[0]); return g.outputs[0]

def zcolor(nt, base, s, p):
    return mixc(nt, gt(nt, attr(nt, "prim").outputs["Fac"], 0.5),
                mixc(nt, gt(nt, attr(nt, "sec").outputs["Fac"], 0.5), base, s), p)

def seam(nt, thr=0.8):
    ln = nt.nodes.new("ShaderNodeVectorMath"); ln.operation = 'LENGTH'
    nt.links.new(attr(nt, "lab").outputs["Vector"], ln.inputs[0])
    g = nt.nodes.new("ShaderNodeMath"); g.operation = 'LESS_THAN'; g.inputs[1].default_value = thr
    nt.links.new(ln.outputs["Value"], g.inputs[0])
    return g.outputs[0]

def toon_light(nt, thr=0.3):
    d = nt.nodes.new("ShaderNodeBsdfDiffuse"); d.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB"); nt.links.new(d.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW"); nt.links.new(s2r.outputs["Color"], bw.inputs[0])
    return gt(nt, bw.outputs[0], thr)

def emit_out(nt, out, col):
    em = nt.nodes.new("ShaderNodeEmission"); put(nt, col, em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])

def mat_body_flat(C, seam_mul=(0.66, 0.64, 0.74, 1)):
    m, nt, out = new_mat("FlatBody")
    lit = zcolor(nt, lin(C["base"][0]), lin(C["sec"][0]), lin(C["prim"][0]))
    sh = zcolor(nt, lin(C["base"][1]), lin(C["sec"][1]), lin(C["prim"][1]))
    col = mixc(nt, toon_light(nt), sh, lit)
    emit_out(nt, out, mixc(nt, seam(nt), col, seam_mul, 'MULTIPLY'))
    return m

def mat_body_line(bg, sec, prim, seam_col):
    m, nt, out = new_mat("LineBody")
    fill = zcolor(nt, lin(bg), lin(sec), lin(prim))
    emit_out(nt, out, mixc(nt, seam(nt, 0.78), fill, lin(seam_col)))
    return m

def mat_body_clay(base, sec, prim, glow=0.8):
    m, nt, out = new_mat("ClayBody")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = zcolor(nt, lin(base), lin(sec), lin(prim))
    put(nt, mixc(nt, seam(nt), col, (0.72, 0.7, 0.78, 1), 'MULTIPLY'), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.68
    b.inputs["Specular IOR Level"].default_value = 0.3
    b.inputs["Emission Color"].default_value = lin(prim)
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = glow
    nt.links.new(gt(nt, attr(nt, "prim").outputs["Fac"], 0.5), mul.inputs[0])
    nt.links.new(mul.outputs[0], b.inputs["Emission Strength"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m

def mat_body_labels():
    m, nt, out = new_mat("LabelBody")
    emit_out(nt, out, mixc(nt, seam(nt), attr(nt, "labcol").outputs["Color"], (0.02, 0.02, 0.03, 1)))
    return m

def mat_hull(name, col):
    m, nt, out = new_mat(name)
    emit_out(nt, out, col)
    m.use_backface_culling = True
    return m

def outline(obj, hull, thick):
    obj.data.materials.append(hull)
    sd = obj.modifiers.new("Outline", 'SOLIDIFY')
    sd.thickness = thick; sd.offset = 1.0; sd.use_flip_normals = True; sd.use_rim = False
    sd.material_offset = len(obj.data.materials) - 1
    sd.use_even_offset = False; sd.thickness_clamp = 1.0

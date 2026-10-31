# HexGym body model looks: the MuscleMap-labelled sculpt with seams and muscle activation.
import os, bpy, numpy as np
import hexlib as H

SEAMS = os.environ.get("HEX_SEAMS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work", "body", "seams_v2.npz"))

# what lights up: names are MuscleMap groups (openGym groups) or MuscleMap pieces
ACTS = {
    "none": ((), ()),
    "supino": (("chest",), ("frontDeltoid", "triceps")),
    "supino_inclinado": (("upperChest",), ("chest", "frontDeltoid", "triceps")),
    "elevacao_lateral": (("deltoids@lat",), ("upperTrapezius", "frontDeltoid")),
    "agachamento": (("quadriceps", "gluteal"), ("adductors", "hamstring", "lower-back")),
    "remada": (("upperBack", "rhomboids", "lowerTrapezius", "trapezius"), ("biceps", "rearDeltoid", "forearm")),
    "rosca": (("biceps",), ("forearm", "frontDeltoid")),
    "abdominal": (("upperAbs",), ("lowerAbs", "obliques")),
    # v2 regions (need HEX_SEAMS pointing at seams_v2.npz)
    "abdutora": (("gluteusMedius",), ("gluteal",)),
    "panturrilha_sentada": (("soleus",), ("calves",)),
    "rosca_martelo": (("brachialis", "forearm"), ("biceps",)),
    "puxada": (("upperBack", "teresMajor"), ("biceps", "rhomboids", "lowerTrapezius", "rearDeltoid")),
    "triceps_frances": (("tricepsLongHead",), ("triceps",)),
    "flexao_pescoco": (("sternocleidomastoid",), ()),
    "extensao_pescoco": (("neckBack",), ("upperTrapezius",)),
}


def load_fields(body, act):
    """corner attributes: sg/sp signed distance to group/piece borders, fp/fs > 0 inside the lit muscles"""
    f = np.load(SEAMS)
    lab, grp, slug = f["lab"], f["grp"], f["slug"]
    me = body.data
    vi = np.zeros(len(me.loops), np.int64); me.loops.foreach_get("vertex_index", vi)
    assert len(vi) == len(f["sp"]), "seams.npz does not match this mesh"
    nl = int(lab.max()) + 1
    lg, ls = np.full(nl, "", object), np.full(nl, "", object)
    lg[lab] = grp; ls[lab] = slug
    def member(names):
        M = np.zeros(nl, bool)
        for nm in names:
            if nm == "deltoids@lat": M |= ls == "deltoids"          # lateral head only
            else: M |= (lg == nm) | (ls == nm)
        M[0] = False
        return M
    prim, sec = ACTS[act]
    MP = member(prim); MS = member(sec) & ~MP
    pa, pb, sp = np.repeat(f["pa"], 3), np.repeat(f["pb"], 3), f["sp"]
    near = pa >= 0
    def fill(M):
        A, B = M[np.clip(pa, 0, None)], M[np.clip(pb, 0, None)]
        inside = np.where(M[lab[vi]], 0.01, -0.01)   # where three regions meet the nearest border may skip M
        u = np.where(A & ~B, sp, np.where(B & ~A, -sp, np.where(A & B, 0.01, inside)))
        return np.where(near, u, np.where(M[lab[vi]], 0.01, -0.01)).astype(np.float32)
    for name in list(me.attributes.keys()):
        if name in ("bdg", "bdp", "prim", "sec", "skin", "sg", "sp", "fp", "fs"): me.attributes.remove(me.attributes[name])
    for name, val in (("sg", f["sg"]), ("sp", sp), ("fp", fill(MP)), ("fs", fill(MS))):
        a = me.attributes.new(name, 'FLOAT', 'CORNER'); a.data.foreach_set("value", np.asarray(val, np.float32))


def zfill(nt, base, s, p):
    return H.mixc(nt, H.gt(nt, H.attr(nt, "fp").outputs["Fac"], 0.0),
                  H.mixc(nt, H.gt(nt, H.attr(nt, "fs").outputs["Fac"], 0.0), base, s), p)


GW = (0.0008, 0.0013)      # group seam: half width where the line starts to fade, and where it is gone
PW = (0.00045, 0.0009)     # piece seam


def line(nt, name, w):
    """1 on a seam, 0 away from it"""
    ab = nt.nodes.new("ShaderNodeMath"); ab.operation = 'ABSOLUTE'
    nt.links.new(H.attr(nt, name).outputs["Fac"], ab.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.interpolation_type = 'SMOOTHSTEP'
    nt.links.new(ab.outputs[0], mr.inputs["Value"])
    mr.inputs["From Min"].default_value = w[0]; mr.inputs["From Max"].default_value = w[1]
    mr.inputs["To Min"].default_value = 1.0; mr.inputs["To Max"].default_value = 0.0
    return mr.outputs["Result"]


def seamed(nt, col, g_mul, p_mul):
    c = H.mixc(nt, line(nt, "sp", PW), col, p_mul, 'MULTIPLY')
    return H.mixc(nt, line(nt, "sg", GW), c, g_mul, 'MULTIPLY')


def mat_clay(base, sec, prim, glow=0.7):
    m, nt, out = H.new_mat("HexClay")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = zfill(nt, H.lin(base), H.lin(sec), H.lin(prim))
    H.put(nt, seamed(nt, col, (0.5, 0.48, 0.6, 1), (0.74, 0.72, 0.82, 1)), b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.62
    b.inputs["Specular IOR Level"].default_value = 0.28
    b.inputs["Emission Color"].default_value = H.lin(prim)
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = glow
    nt.links.new(H.gt(nt, H.attr(nt, "fp").outputs["Fac"], 0.0), mul.inputs[0])
    nt.links.new(mul.outputs[0], b.inputs["Emission Strength"])
    nt.links.new(b.outputs[0], out.inputs["Surface"])
    return m


def mat_flat(C):
    m, nt, out = H.new_mat("HexFlat")
    lit = zfill(nt, H.lin(C["base"][0]), H.lin(C["sec"][0]), H.lin(C["prim"][0]))
    sh = zfill(nt, H.lin(C["base"][1]), H.lin(C["sec"][1]), H.lin(C["prim"][1]))
    col = H.mixc(nt, H.toon_light(nt), sh, lit)
    H.emit_out(nt, out, seamed(nt, col, (0.42, 0.4, 0.52, 1), (0.7, 0.68, 0.78, 1)))
    return m


def mat_line(bg, sec, prim, piece_col, group_col):
    m, nt, out = H.new_mat("HexLine")
    fill = zfill(nt, H.lin(bg), H.lin(sec), H.lin(prim))
    c = H.mixc(nt, line(nt, "sp", PW), fill, H.lin(piece_col))
    c = H.mixc(nt, line(nt, "sg", GW), c, H.lin(group_col))
    H.emit_out(nt, out, c)
    return m

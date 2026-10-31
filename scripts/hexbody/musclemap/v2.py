# Model v2: carves seven new regions per side out of the v1 labelling.
# Every rule is written against the skeleton (shoulder, elbow, knee, ankle, neck) and the body's own
# axes, never against hand-painted vertices, so the same rules can label another body (the female
# one) once it is rigged to the same skeleton.
#   1 gluteus medius   from gluteal (+ the flank just below the iliac crest)
#   2 soleus           from calves
#   3 brachialis       from triceps (lateral band, distal half of the arm)
#   4 teres major      from rotator cuff + lats (band along the scapula's lateral border)
#   5 sternocleidomastoid  from neck skin
#   6 back of the neck (splenius, levator scapulae)  from neck skin
#   7 triceps long head    from triceps (posterior-medial column)
# After the rules, each new border is pulled into the nearest groove of the sculpt, but only inside
# the area the new region came from, so no v1 border moves.
# Usage: v2.py posed.npz labels_v1.npy out.npy
import sys, json, os
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra, connected_components

HERE = os.path.dirname(os.path.abspath(__file__))
POSED, LAB, OUT = sys.argv[1:4]
JPATH = os.path.join(HERE, "labels.json")
J = json.load(open(JPATH))
TAB = {t["id"]: t for t in J["table"]}

NEW = [  # slug, group, parent slugs
    ("gluteusMedius", "gluteal"), ("soleus", "calves"), ("brachialis", "biceps"), ("teresMajor", "upper-back"),
    ("sternocleidomastoid", "neck"), ("neckBack", "neck"), ("tricepsLongHead", "triceps"),
]
# table rows for the new regions (ids after the v1 table); body side L = +x
if not any(t.get("slug") == "soleus" for t in J["table"]):
    nid = max(TAB) + 1
    for slug, grp in NEW:
        for side in ("left", "right"):
            J["table"].append({"id": nid, "kind": "muscle", "view": "back", "slug": slug, "group": grp,
                               "sub": True, "side": side, "piece": 0, "v2": True})
            nid += 1
# the rotator cuff counts for the shoulder, as it does in the app (research, catalogue fix 1)
for t in J["table"]:
    if t.get("slug") == "rotatorCuff": t["group"] = "deltoids"
TAB = {t["id"]: t for t in J["table"]}

d = np.load(POSED)
CO, NM, T = d["co"], d["nm"], d["tris"]
JN = list(d["jn"]); JH = d["jh"]
jp = lambda name: JH[JN.index(name)]
lab0 = np.load(LAB); lab = lab0.copy(); n = len(CO)
x, y, z = CO.T
slug0 = np.array([TAB[int(u)]["slug"] if u else "skin" for u in lab0])

def uid(slug, s):   # label id of a region on body side s (+1 left, -1 right)
    side = "left" if s > 0 else "right"
    if TAB_BY.get((slug, side)) is not None: return TAB_BY[(slug, side)]
    # v1 regions: find the unit actually used on that side
    m = (slug0 == slug) & (x * s > 0.004)
    v, c = np.unique(lab0[m], return_counts=True)
    return int(v[c.argmax()])
TAB_BY = {(t["slug"], t["side"]): t["id"] for t in J["table"] if t.get("v2")}


def limb(a, b, s):
    """t along the bone (0 at a, 1 at b), angle around it (0 front, +90 lateral, ±180 back), distance"""
    A, B = jp(a), jp(b); ax = B - A; Ln = np.linalg.norm(ax); ax = ax / Ln
    f = np.array([0, -1.0, 0]); f -= f.dot(ax) * ax; f /= np.linalg.norm(f)
    l = np.cross(ax, f)
    if l[0] * s < 0: l = -l
    v = CO - A; t = v @ ax / Ln; r = v - np.outer(v @ ax, ax)
    return t, np.degrees(np.arctan2(r @ l, r @ f)), np.linalg.norm(r, axis=1)


# Both bodies hang on the same skeleton at the same height, so joint frames match; what differs is where
# the MuscleMap figure put a border. HEX_FIG=female uses values measured on her body the same way:
#   brachialis: her figure's biceps wraps further round, so her triceps' lateral edge sits ~18 deg further back
#   teres major: the segment follows her rotator-cuff region (x 0.072-0.160, z 0.123-0.224 against
#                the male 0.067-0.158, 0.127-0.248), mapped point by point, band scaled with it
FIG = os.environ.get("HEX_FIG", "male")
PAR = {"male": dict(brach_shift=0.0, teres_a=(0.068, 0.145), teres_b=(0.150, 0.192), teres_w=0.017),
       "female": dict(brach_shift=18.0, teres_a=(0.073, 0.138), teres_b=(0.152, 0.177), teres_w=0.014)}[FIG]
masks = []   # (area, labels allowed inside it) for the groove pass
for s, P in ((1, "L_"), (-1, "R_")):
    side = x * s > 0.004
    # ---- arm: brachialis and triceps long head, both out of the triceps region
    t, th, r = limb(P + "Shoulder", P + "Elbow", s)
    tri = side & (lab0 == uid("triceps", s)) & (r < 0.08)
    u = np.clip((t - 0.40) / (0.93 - 0.40), 0, 1)
    brach = tri & (t > 0.40) & (t < 0.93) & (th > 30) & (th < 70 + PAR["brach_shift"] + 55 * np.sin(np.pi * u))
    hi = -75 - 75 * np.clip((t - 0.62) / 0.22, 0, 1)
    longh = tri & (t > 0.02) & (t < 0.84) & (th < hi)
    lab[brach] = uid("brachialis", s); lab[longh] = uid("tricepsLongHead", s)
    masks.append(tri)
    # ---- lower leg: soleus below and beside the gastrocnemius heads
    t, th, r = limb(P + "Knee", P + "Ankle", s)
    calf = side & (lab0 == uid("calves", s)) & (r < 0.09)
    tg = np.full(n, np.inf)
    med = (th >= -115) & (th <= -40); tg[med] = 0.33
    mb = th < -115; tg[mb] = np.interp(th[mb], [-180, -145, -115], [0.56, 0.60, 0.33])
    lat = (th >= 95) & (th <= 135); tg[lat] = 0.30
    lb = th > 135; tg[lb] = np.interp(th[lb], [135, 155, 180], [0.30, 0.50, 0.56])
    sol = calf & (t > tg)
    lab[sol] = uid("soleus", s)
    masks.append(calf)
    # ---- hip: gluteus medius in the upper outer quadrant, below the iliac crest
    phi = np.degrees(np.arctan2(x * s, -(y + 0.02)))          # 0 front, 90 side, 180 back
    # lower edge: the diagonal border of gluteus maximus; it meets the iliac crest (z -0.10) near phi 152,
    # so the medial end of the visible gluteus medius is a point, not a step
    zb = -0.12 - (145 - phi) * 0.003
    hipa = side & ((lab0 == uid("gluteal", s)) | ((lab0 == uid("lowerBack", s)) & (z < -0.095) & (phi < 152))) & (z > -0.32)
    gmed = hipa & (phi > 78) & (phi < 152) & (z > zb) & (z < -0.10)
    lab[gmed] = uid("gluteusMedius", s)
    masks.append(hipa)
    # ---- back: teres major along the lateral border of the scapula, up to the armpit
    A2, B2 = np.array(PAR["teres_a"]), np.array(PAR["teres_b"])
    q = np.c_[x * s, z]; ab = B2 - A2
    w = np.clip(((q - A2) @ ab) / (ab @ ab), 0, 1); dseg = np.linalg.norm(q - (A2 + np.outer(w, ab)), axis=1)
    backa = side & np.isin(lab0, [uid("rotatorCuff", s), uid("upperBack", s)]) & (y > -0.02)
    teres = backa & (NM[:, 1] > 0.15) & (dseg < PAR["teres_w"] - 0.003 * w) & (x * s > 0.062)
    lab[teres] = uid("teresMajor", s)
    masks.append(backa)
    # ---- neck: sternocleidomastoid from the sternum up to behind the ear; the back of the neck behind it
    phn = np.degrees(np.arctan2(x * s, -(y - 0.015)))       # 0 front, 90 side, 180 back
    rn = np.hypot(x, y - 0.015)
    neck = side & (lab0 == 0) & (z > 0.245) & (z < 0.40) & (rn < np.where(z < 0.31, 0.11, 0.085))
    pc = 12 + (z - 0.268) / (0.388 - 0.268) * 100
    hw = np.interp(z, [0.262, 0.30, 0.35, 0.392], [17, 15, 13, 10])
    scm = neck & (z > 0.262) & (z < 0.392) & (np.abs(phn - pc) < hw) & (rn < 0.075)
    nb = neck & ~scm & (phn > pc + hw) & (z < 0.385) & (rn < np.where(z < 0.31, 0.11, 0.075))
    lab[scm] = uid("sternocleidomastoid", s); lab[nb] = uid("neckBack", s)
    # bare skin left on top of the shoulders, next to the neck, is upper trapezius
    cap = side & (lab0 == 0) & (z > 0.25) & (z < 0.335) & ~neck & (np.abs(x) < 0.17) & (y > -0.03) & (rn < 0.16)
    lab[cap] = uid("upperTrapezius", s)
    masks.append(neck | cap)

print("rules:", {sl: int(sum((lab == uid(sl, s)).sum() for s in (1, -1))) for sl, _ in NEW})

# ---------- groove pass, inside each source area only
E = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); E.sort(1); E = np.unique(E, axis=0)
L = np.linalg.norm(CO[E[:, 0]] - CO[E[:, 1]], axis=1)
deg = np.bincount(E.ravel(), minlength=n).astype(float)
acc = np.zeros((n, 3)); np.add.at(acc, E[:, 0], CO[E[:, 1]]); np.add.at(acc, E[:, 1], CO[E[:, 0]])
el = np.zeros(n); np.add.at(el, E[:, 0], L); np.add.at(el, E[:, 1], L); el /= deg
conc = ((acc / deg[:, None] - CO) * NM).sum(1) / (el ** 2 + 1e-12)
for _ in range(4):
    a = np.zeros(n); np.add.at(a, E[:, 0], conc[E[:, 1]]); np.add.at(a, E[:, 1], conc[E[:, 0]])
    conc = 0.5 * conc + 0.5 * a / deg
g = np.clip(conc / np.percentile(conc[conc > 0], 90), 0, 1.5)
CORE, ALPHA = 0.007, 6.0

def graph(w, keep):
    k = keep & np.isfinite(w)
    return coo_matrix((np.r_[w[k], w[k]], (np.r_[E[k, 0], E[k, 1]], np.r_[E[k, 1], E[k, 0]])), shape=(n, n)).tocsr()

moved = 0
for area in masks:
    inside = area[E[:, 0]] & area[E[:, 1]]
    same = lab[E[:, 0]] == lab[E[:, 1]]
    bnd = np.zeros(n, bool); bnd[E[inside & ~same].ravel()] = True
    if not bnd.any(): continue
    dist = dijkstra(graph(L, inside & same), directed=False, indices=np.where(bnd)[0], min_only=True)
    seed = area & (dist >= CORE)
    for lb in np.unique(lab[area]):
        m = area & (lab == lb)
        if not (seed & m).any(): seed[m & (dist >= 0.6 * dist[m][np.isfinite(dist[m])].max())] = True
    wg = L * (1 + ALPHA * (g[E[:, 0]] + g[E[:, 1]]) / 2)
    _, _, src = dijkstra(graph(wg, inside), directed=False, indices=np.where(seed)[0], min_only=True, return_predecessors=True)
    idx = np.where(area & (src >= 0))[0]
    new = lab[src[idx]]; moved += int((new != lab[idx]).sum()); lab[idx] = new
    # every label keeps only its biggest patch inside the area
    for lb in np.unique(lab[area]):
        m = area & (lab == lb)
        sm = m[E[:, 0]] & m[E[:, 1]]
        _, comp = connected_components(coo_matrix((np.ones(sm.sum()), (E[sm, 0], E[sm, 1])), shape=(n, n)), directed=False)
        cs, cnt = np.unique(comp[m], return_counts=True)
        for c in cs[cnt < cnt.max()]:
            isl = m & (comp == c)
            nb = np.r_[E[isl[E[:, 0]] & ~isl[E[:, 1]], 1], E[isl[E[:, 1]] & ~isl[E[:, 0]], 0]]
            nb = nb[area[nb]]
            if len(nb): v, cc = np.unique(lab[nb], return_counts=True); lab[isl] = v[cc.argmax()]
print("groove pass moved", moved, "vertices")

# the figure is symmetric: the right side copies the left one inside the same source areas
from scipy.spatial import cKDTree
SL = ["triceps", "brachialis", "tricepsLongHead", "calves", "soleus", "gluteal", "lowerBack", "gluteusMedius",
      "rotatorCuff", "upperBack", "teresMajor", "sternocleidomastoid", "neckBack", "upperTrapezius"]
L2R = {uid(sl, 1): uid(sl, -1) for sl in SL}; L2R[0] = 0
left_area = np.zeros(n, bool); right_area = np.zeros(n, bool)
for i, area in enumerate(masks):
    (left_area if i < len(masks) // 2 else right_area)[:] |= area
li = np.where(left_area)[0]; ri = np.where(right_area)[0]
_, j = cKDTree(CO[li] * [-1, 1, 1]).query(CO[ri])
cand = np.array([L2R.get(int(v), -1) for v in lab[li[j]]])
ok = (cand >= 0) & np.isin(cand, [L2R[k] for k in L2R])
before = lab[ri].copy(); lab[ri[ok]] = cand[ok]
print("mirrored", int((lab[ri] != before).sum()), "right-side vertices")

out = {}
for sl, _ in NEW:
    out[sl] = [int((lab == uid(sl, s)).sum()) for s in (1, -1)]
print("final L/R:", out)
np.save(OUT, lab)
json.dump(J, open(JPATH, "w"), ensure_ascii=False)
print("table rows", len(J["table"]))

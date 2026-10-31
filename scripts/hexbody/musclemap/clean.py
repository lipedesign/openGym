# Tidies a per-vertex muscle labelling: skin parts merge into one, every muscle piece keeps only its
# biggest connected patch, and the borders are smoothed.
# Usage: clean.py posed.npz in.npy out.npy [smooth_iters]
import sys, json, os
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = os.path.dirname(os.path.abspath(__file__))
POSED, LAB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
ITERS = int(sys.argv[4]) if len(sys.argv) > 4 else 0
TAB = {t["id"]: t for t in json.load(open(os.path.join(HERE, "labels.json")))["table"]}
SKIN = {"head", "hair", "hands", "feet", "ankles", "knees"}
d = np.load(POSED); CO, T = d["co"], d["tris"]
n = len(CO)
E = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); E.sort(1); E = np.unique(E, axis=0)
ta = 0.5 * np.linalg.norm(np.cross(CO[T[:, 1]] - CO[T[:, 0]], CO[T[:, 2]] - CO[T[:, 0]]), axis=1)
VA = np.zeros(n); np.add.at(VA, T.ravel(), np.repeat(ta / 3, 3))     # surface area around each vertex
lab = np.load(LAB).copy()
lab[[TAB.get(int(i), {}).get("slug") in SKIN or int(i) <= 1 for i in lab]] = 0

# one unit per (muscle piece name, body side), shared by the front and back views;
# only the six-pack and the quadriceps heads keep their separate pieces
KEEP_PIECES = {"upperAbs", "quadriceps"}
def unit_key(t):
    side = t["side"]
    if side != "common":
        body = ("R" if side == "left" else "L") if t["view"] == "front" else ("L" if side == "left" else "R")
    else: body = "C"
    return (t["slug"], body, t["piece"] if t["slug"] in KEEP_PIECES else -1)
rep = {}
for i, t in sorted(TAB.items()):
    if t.get("kind") != "muscle": continue
    rep.setdefault(unit_key(t), i)
UNIT = {i: rep[unit_key(t)] for i, t in TAB.items() if t.get("kind") == "muscle"}
lab = np.array([UNIT.get(int(i), 0) for i in lab])


def neighbours_vote(lab, idx, exclude):
    """most common label among the neighbours of idx, ignoring `exclude`"""
    m = np.isin(E[:, 0], idx) | np.isin(E[:, 1], idx)
    a, b = E[m, 0], E[m, 1]
    pairs = np.r_[np.c_[a, lab[b]], np.c_[b, lab[a]]]
    pairs = pairs[np.isin(pairs[:, 0], idx) & (pairs[:, 1] != exclude)]
    if len(pairs) == 0: return None
    v, c = np.unique(pairs[:, 1], return_counts=True)
    return v[c.argmax()]


def keep_largest(lab):
    for _ in range(6):
        same = lab[E[:, 0]] == lab[E[:, 1]]
        G = coo_matrix((np.ones(same.sum()), (E[same, 0], E[same, 1])), shape=(n, n))
        nc, comp = connected_components(G, directed=False)
        changed = 0
        for lb in np.unique(lab):
            if lb == 0: continue      # skin is many separate patches (head, hands, feet, knees)
            m = lab == lb
            cs, ci = np.unique(comp[m], return_inverse=True)
            if len(cs) <= 1: continue
            area = np.bincount(ci, weights=VA[m])
            for c in cs[area < area.max()]:
                idx = np.where(comp == c)[0]
                v = neighbours_vote(lab, idx, lb)
                if v is not None: lab[idx] = v; changed += 1
        if not changed: break
    return lab


RAW = len(sys.argv) > 5 and sys.argv[5] == 'raw'
if not RAW: lab = keep_largest(lab)
if ITERS:
    labels, inv = np.unique(lab, return_inverse=True)
    H = np.zeros((n, len(labels)), np.float32); H[np.arange(n), inv] = 1
    Adj = coo_matrix((np.ones(2 * len(E), np.float32), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr()
    deg = np.asarray(Adj.sum(1)).astype(np.float32)
    for _ in range(ITERS):
        H = 0.5 * H + 0.5 * (Adj @ H) / deg
    lab = labels[H.argmax(1)]
    lab = keep_largest(lab)
print("pieces", len(np.unique(lab)), "skin verts", int((lab == 0).sum()))
np.save(OUT, lab)

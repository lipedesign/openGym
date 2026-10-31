# Per-vertex fields for shading: surface distance to the nearest border between muscle groups (bdg)
# and between any two pieces (bdp). The shader draws the seam lines from these.
import sys, json, os
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
HERE = os.path.dirname(os.path.abspath(__file__))
POSED, LAB, OUT = sys.argv[1:4]
TAB = {t["id"]: t for t in json.load(open(os.path.join(HERE, "labels.json")))["table"]}
d = np.load(POSED); CO, T = d["co"], d["tris"]; n = len(CO)
lab = np.load(LAB)
E = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); E.sort(1); E = np.unique(E, axis=0)
L = np.linalg.norm(CO[E[:, 0]] - CO[E[:, 1]], axis=1)
grp = np.array([TAB[int(u)]["group"] if u else "skin" for u in lab])
def border_dist(key):
    diff = key[E[:, 0]] != key[E[:, 1]]
    a, b, h = E[diff, 0], E[diff, 1], L[diff] / 2
    # a virtual source joined to both ends of every border edge at half the edge length
    rows = np.r_[E[:, 0], E[:, 1], np.full(len(a) * 2, n), a, b]
    cols = np.r_[E[:, 1], E[:, 0], a, b, np.full(len(a) * 2, n)]
    w = np.r_[L, L, h, h, h, h]
    G = coo_matrix((w, (rows, cols)), shape=(n + 1, n + 1)).tocsr()
    return dijkstra(G, directed=True, indices=n)[:n]
bdg = border_dist(grp); bdp = border_dist(lab)
np.savez(OUT, lab=lab, bdg=bdg.astype(np.float32), bdp=bdp.astype(np.float32), grp=grp,
         slug=np.array([TAB[int(u)]["slug"] if u else "skin" for u in lab]))
print("bdg p1/p50", np.percentile(bdg, [1, 50]).round(4), "bdp p1/p50", np.percentile(bdp, [1, 50]).round(4))

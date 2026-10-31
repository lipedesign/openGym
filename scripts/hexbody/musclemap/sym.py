# Mirrors the body-left labelling onto the body-right side so the figure is symmetric.
import sys, json, os
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
POSED, LAB, OUT = sys.argv[1:4]
TAB = {t["id"]: t for t in json.load(open(os.path.join(HERE, "labels.json")))["table"]}
CO = np.load(POSED)["co"]; lab = np.load(LAB)
L = CO[:, 0] > 0.004; R = CO[:, 0] < -0.004
# pair every unit on the left with its mirror unit on the right (same piece name, nearest mirrored centroid)
cen = {u: CO[lab == u].mean(0) for u in np.unique(lab) if u}
pair = {}
for u, c in cen.items():
    if c[0] <= 0: continue
    cands = [v for v, d in cen.items() if d[0] < 0 and TAB[v]["slug"] == TAB[u]["slug"]]
    if cands:
        m = c * [-1, 1, 1]
        pair[u] = min(cands, key=lambda v: np.linalg.norm(cen[v] - m))
tree = cKDTree(CO[L] * [-1, 1, 1])
_, j = tree.query(CO[R])
src = lab[np.where(L)[0][j]]
out = lab.copy()
out[R] = [pair.get(int(v), int(v)) if v else 0 for v in src]
print("pairs", len(pair), "changed", int((out != lab).sum()))
np.save(OUT, out)

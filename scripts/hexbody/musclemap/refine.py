# Snaps the projected muscle borders into the grooves of the sculpt.
# Each muscle keeps a confident core (away from its projected border); the cores then grow over the
# surface, and crossing a groove costs extra, so neighbouring muscles meet inside the grooves.
import sys
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

POSED, LAB, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
CORE = float(sys.argv[4]) if len(sys.argv) > 4 else 0.02     # metres kept as a confident core
ALPHA = float(sys.argv[5]) if len(sys.argv) > 5 else 6.0     # how much a groove costs to cross
d = np.load(POSED); CO, NM, T = d["co"], d["nm"], d["tris"]
lab = np.load(LAB)
n = len(CO)

E = np.vstack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); E.sort(1); E = np.unique(E, axis=0)
L = np.linalg.norm(CO[E[:, 0]] - CO[E[:, 1]], axis=1)

# groove signal: how far a vertex sits below the average of its neighbours, along its normal
deg = np.bincount(E.ravel(), minlength=n).astype(float)
acc = np.zeros((n, 3)); np.add.at(acc, E[:, 0], CO[E[:, 1]]); np.add.at(acc, E[:, 1], CO[E[:, 0]])
lap = acc / deg[:, None] - CO
el = np.zeros(n); np.add.at(el, E[:, 0], L); np.add.at(el, E[:, 1], L); el /= deg
conc = (lap * NM).sum(1) / (el ** 2 + 1e-12)          # ~ curvature, positive in valleys
def smooth(f, it=3):
    for _ in range(it):
        a = np.zeros(n); np.add.at(a, E[:, 0], f[E[:, 1]]); np.add.at(a, E[:, 1], f[E[:, 0]])
        f = 0.5 * f + 0.5 * a / deg
    return f
conc = smooth(conc, 4)
g = np.clip(conc / np.percentile(conc[conc > 0], 90), 0, 1.5)
print("groove signal p50/p90/p99", np.percentile(conc, [50, 90, 99]).round(2))

def graph(w):
    W = coo_matrix((np.r_[w, w], (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr()
    return W

# 1. distance of every vertex to the border of its own projected region (inside the region only)
same = lab[E[:, 0]] == lab[E[:, 1]]
border = np.zeros(n, bool); border[E[~same].ravel()] = True
Gin = graph(np.where(same, L, np.inf).astype(float))
Gin.data[np.isinf(Gin.data)] = 0; Gin.eliminate_zeros()
dist = dijkstra(Gin, directed=False, indices=np.where(border)[0], min_only=True)
dist[np.isinf(dist)] = 0
seed = dist >= CORE
for lb in np.unique(lab):
    m = lab == lb
    if not (seed & m).any():
        mx = dist[m].max(); seed[m & (dist >= 0.6 * mx)] = True
print("seed vertices", int(seed.sum()), "of", n)

# 2. grow the cores; crossing a groove is expensive
w = L * (1 + ALPHA * (g[E[:, 0]] + g[E[:, 1]]) / 2)
G = graph(w)
_, _, src = dijkstra(G, directed=False, indices=np.where(seed)[0], min_only=True, return_predecessors=True)
out = lab[src]
out[src < 0] = lab[src < 0]
print("changed", int((out != lab).sum()))
np.save(OUT, out)
np.save(OUT.replace(".npy", "_groove.npy"), g)

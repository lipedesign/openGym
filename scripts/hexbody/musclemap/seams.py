# Seam fields stored per triangle corner, so the shader can draw thin continuous seam lines and
# crisp activation fills along a smoothed border instead of the mesh-edge zigzag.
#
# For each kind of border (between muscle groups, between any two pieces):
#  1. the border is traced through the triangles (edge midpoints, triangle centroid at junctions);
#  2. the traced curves are smoothed (Taubin) and resampled densely;
#  3. every triangle near a curve picks the nearest border pair it touches, and each of its corners
#     gets the signed distance to that pair's curve (positive towards the pair's first piece).
# Linear interpolation of a signed distance crosses zero right on the curve, so |s| < w draws an even line.
# Usage: seams.py posed.npz labels.npy out.npz
import sys, json, os
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
POSED, LAB, OUT = sys.argv[1:4]
TAB = {t["id"]: t for t in json.load(open(os.path.join(HERE, "labels.json")))["table"]}
d = np.load(POSED); CO, T = d["co"], d["tris"]
lab = np.load(LAB)
m = len(T)
FAR = 0.008            # metres: triangles further than this from any border get an unsigned value
STEP = 0.0002          # resampling step along the curves
ITERS = 70             # Taubin smoothing passes

tn = np.cross(CO[T[:, 1]] - CO[T[:, 0]], CO[T[:, 2]] - CO[T[:, 0]])
tn /= np.linalg.norm(tn, axis=1, keepdims=True) + 1e-12
cent = CO[T].mean(1)


def field(key):
    K = key[T]                                                      # m x 3 region key per corner
    # ---- 1. trace: one node per mesh edge whose ends differ, one per junction triangle
    ed = np.stack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]], 1)    # m x 3 x 2 (edge c joins corner c, c+1)
    kd = np.stack([K[:, 0] != K[:, 1], K[:, 1] != K[:, 2], K[:, 2] != K[:, 0]], 1)
    es = np.sort(ed, 2)
    ekey = es[..., 0].astype(np.int64) * len(CO) + es[..., 1]
    uk, node_of = np.unique(ekey[kd], return_inverse=True)
    nid = np.full((m, 3), -1); nid[kd] = node_of
    pos = [(CO[uk // len(CO)] + CO[uk % len(CO)]) / 2]
    nn = len(uk)
    nd = kd.sum(1)
    junc = np.where(nd == 3)[0]
    jnode = np.arange(nn, nn + len(junc)); pos.append(cent[junc]); nn += len(junc)
    P = np.vstack(pos)
    segs, spair, stri = [], [], []
    # two-key triangles: the two differing edges are joined
    two = np.where(nd == 2)[0]
    for t in two:
        a, b = nid[t][kd[t]]
        ks = np.unique(K[t]); segs.append((a, b)); spair.append((ks[0], ks[1])); stri.append(t)
    for t, j in zip(junc, jnode):
        for c in range(3):
            ka, kb = sorted((K[t, c], K[t, (c + 1) % 3]))
            segs.append((j, nid[t, c])); spair.append((ka, kb)); stri.append(t)
    S = np.array(segs); SP = np.array(spair); ST = np.array(stri)
    # orient every segment so that cross(n, b - a) points to the pair's first key
    a, b = P[S[:, 0]], P[S[:, 1]]
    side_ref = np.array([CO[T[t]][K[t] == SP[i, 0]].mean(0) for i, t in enumerate(ST)])
    flip = (np.cross(tn[ST], b - a) * (side_ref - (a + b) / 2)).sum(1) < 0
    S[flip] = S[flip][:, ::-1]
    # ---- 2. smooth the curves: only nodes on a plain chain (degree 2) move
    deg = np.bincount(S.ravel(), minlength=nn)
    free = deg == 2
    nb = np.zeros((nn, 3)); cnt = np.zeros(nn)
    def lap(X):
        nb[:] = 0; cnt[:] = 0
        np.add.at(nb, S[:, 0], X[S[:, 1]]); np.add.at(nb, S[:, 1], X[S[:, 0]])
        np.add.at(cnt, S[:, 0], 1); np.add.at(cnt, S[:, 1], 1)
        return nb / np.maximum(cnt, 1)[:, None] - X
    X = P.copy()
    for _ in range(ITERS):
        X[free] += 0.5 * lap(X)[free]
        X[free] -= 0.53 * lap(X)[free]
    # ---- resample
    a, b = X[S[:, 0]], X[S[:, 1]]
    L = np.linalg.norm(b - a, axis=1)
    ns = np.maximum(1, np.ceil(L / STEP).astype(int))
    rep = np.repeat(np.arange(len(S)), ns)
    u = (np.arange(ns.sum()) - np.repeat(np.cumsum(ns) - ns, ns) + 0.5) / np.repeat(ns, ns)
    Q = a[rep] + (b - a)[rep] * u[:, None]
    tq = (b - a)[rep] / (L[rep, None] + 1e-12)
    side = np.cross(tn[ST][rep], tq)                                 # points to the pair's first key
    QP = SP[rep]
    # ---- 3. every triangle near a border picks the nearest pair that involves one of its keys
    tree = cKDTree(Q)
    mid = (a + b) / 2                                               # candidates: one point per segment
    dist, idx = cKDTree(mid).query(cent, k=24, distance_upper_bound=FAR)
    ok = np.isfinite(dist)
    idxc = np.where(ok, idx, 0)
    pa, pb = SP[idxc, 0], SP[idxc, 1]
    inv = ((pa[..., None] == K[:, None, :]) | (pb[..., None] == K[:, None, :])).any(2) & ok
    first = np.where(inv.any(1), inv.argmax(1), -1)
    tpair = np.full((m, 2), -1)
    hit = first >= 0
    tpair[hit] = SP[idx[hit, first[hit]]]
    # corners: signed distance to the chosen pair's curve
    s = np.full((m, 3), np.nan)
    pid = tpair[:, 0].astype(np.int64) * 100000 + tpair[:, 1]
    qid = QP[:, 0].astype(np.int64) * 100000 + QP[:, 1]
    order = np.argsort(qid); qs = qid[order]
    for p in np.unique(pid[hit]):
        tris = np.where(pid == p)[0]
        lo, hi = np.searchsorted(qs, p), np.searchsorted(qs, p, 'right')
        sel = order[lo:hi]
        tr = cKDTree(Q[sel])
        V = T[tris].ravel()
        dd, ii = tr.query(CO[V])
        g = sel[ii]
        sg = np.sign(((CO[V] - Q[g]) * side[g]).sum(1)); sg[sg == 0] = 1
        s[tris] = (sg * dd).reshape(-1, 3)
    # far corners: plain (unsigned) distance to the nearest border of any pair
    far = np.isnan(s)
    if far.any():
        dd, _ = tree.query(CO[T][far])
        s[far] = dd
    print(f"  nodes {nn} segs {len(S)} samples {len(Q)} near tris {int(hit.sum())} of {m}")
    return s.astype(np.float32), tpair.astype(np.int32)


gid = {}
grp = np.array([TAB[int(u)]["group"] if u else "skin" for u in lab])
gkey = np.array([gid.setdefault(g, len(gid)) for g in grp])
print("group borders"); sg, gpair = field(gkey)
print("piece borders"); sp, ppair = field(lab)
np.savez(OUT, sg=sg.ravel(), sp=sp.ravel(), pa=ppair[:, 0], pb=ppair[:, 1], lab=lab, grp=grp,
         slug=np.array([TAB[int(u)]["slug"] if u else "skin" for u in lab]))
for nm_, x in (("sg", sg), ("sp", sp)):
    print(nm_, "corners |s|<1mm", int((np.abs(x) < 0.001).sum()), "p50 mm", np.round(np.median(np.abs(x)) * 1000, 2))

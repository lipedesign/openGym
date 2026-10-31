# Paints the MuscleMap anatomy (MIT) onto the posed 3D body.
# Both figures become 2D silhouettes; torso and legs are matched row by row between landmarks
# (head top, neck, armpit, crotch, knee, ankle, sole); arms are matched along their own axis
# (top, elbow, wrist, fingertip). Inside each row, position is normalised by the local width.
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
POSED, OUT = sys.argv[1], sys.argv[2]
FIG = os.environ.get("HEX_FIG", "male")       # male | female (labels_f.json, labels_{view}_f.npy)
SUF = "" if FIG == "male" else "_f"
J = json.load(open(os.path.join(HERE, f"labels{SUF}.json")))
S = J["S"]; TAB = J["table"]
d = np.load(POSED)
CO, NM, TRIS = d["co"], d["nm"], d["tris"]
JN = list(d["jn"]); JH = d["jh"]
jp = lambda n: JH[JN.index(n)]
UPPER = {"biceps", "triceps"}; FORE = {"forearm"}; HAND = {"hands"}


def intervals(row):
    r = np.concatenate([[0], row.astype(np.int8), [0]])
    dd = np.diff(r)
    return list(zip(np.where(dd == 1)[0], np.where(dd == -1)[0] - 1))


def landmarks(M, c, A):
    rows = np.where(M.any(1))[0]; top, sole = rows[0], rows[-1]; H = sole - top
    lo, hi = int(top + 0.10 * H), int(top + 0.22 * H)
    def cw(r):
        for a, b in intervals(M[r]):
            if a <= c <= b: return b - a
        return 1e9
    neck = min(range(lo, hi), key=cw)
    shoulder = np.mean([np.where((A == k).any(1))[0][0] for k in (1, 2)])
    crotch = next(r for r in range(int(top + 0.4 * H), sole) if not M[r, c - 1:c + 2].any())
    return dict(top=top, neck=neck, shoulder=shoulder, crotch=crotch, sole=sole, H=H)


def arm_frame(A, k):
    ys, xs = np.nonzero(A == k)
    P = np.stack([xs, ys], 1).astype(float); o = P.mean(0)
    w, v = np.linalg.eigh(np.cov((P - o).T)); a = v[:, -1]
    if a[1] < 0: a = -a
    p = np.array([-a[1], a[0]])
    return o, a, p, P


def ts(P, o, a, p):
    Q = P - o
    return Q @ a, Q @ p


def width_profile(t, s, t0, t1, nb=80):
    edges = np.linspace(t0, t1, nb + 1); lo = np.full(nb, np.nan); hi = np.full(nb, np.nan)
    b = np.clip(((t - t0) / (t1 - t0) * nb).astype(int), 0, nb - 1)
    for i in range(nb):
        m = b == i
        if m.sum() > 3: lo[i], hi[i] = np.percentile(s[m], 1), np.percentile(s[m], 99)
    idx = np.arange(nb); ok = ~np.isnan(lo)
    lo = np.interp(idx, idx[ok], lo[ok]); hi = np.interp(idx, idx[ok], hi[ok])
    k = np.ones(5) / 5
    lo = np.convolve(np.pad(lo, 2, mode='edge'), k, 'valid'); hi = np.convolve(np.pad(hi, 2, mode='edge'), k, 'valid')
    centres = (edges[:-1] + edges[1:]) / 2
    return lambda tt: (np.interp(tt, centres, lo), np.interp(tt, centres, hi))


def row_maps(B):
    """per row: sorted list of intervals of the body mask"""
    return [intervals(B[r]) for r in range(B.shape[0])]


# ---------------------------------------------------------------- 2D figure, per view
CENTRE = {"male": {"front": 364.0, "back": 1081.5}, "female": {"front": 320.2, "back": 1142.5}}   # body midline, SVG x
ARMSLUGS = {"biceps", "triceps", "forearm", "hands", "deltoids", "frontDeltoid", "rearDeltoid"}
def figure(view):
    a = np.load(os.path.join(HERE, f"labels_{view}{SUF}.npy"))
    x0, y0 = J["vb"][view][:2]
    c = int(round((CENTRE[FIG][view] - x0) * S))
    if FIG == "female":
        # the ponytail sits outside the head: keep hair only over the skull, so the head, neck and
        # shoulder rows of the silhouette match the bald 3D head
        hb = J["boxes"]["front"]["head"]; hw = (hb[2] - hb[0]) / 2 * S
        hair = np.isin(a, [t["id"] for t in TAB if t.get("slug") == "hair"])
        xx_, yy_ = np.meshgrid(np.arange(a.shape[1]), np.arange(a.shape[0]))
        a = np.where(hair & ((np.abs(xx_ - c) > hw) | (yy_ > (hb[3] - y0) * S)), 0, a)
    M = ndi.binary_fill_holes(ndi.binary_closing(np.pad(a > 0, 8), iterations=6))[8:-8, 8:-8]
    slug = np.empty(len(TAB), object); slug[:] = ""
    for t in TAB:
        if "slug" in t: slug[t["id"]] = t["slug"]
    isarm = np.array([sl in ARMSLUGS for sl in slug])
    _, (iy, ix) = ndi.distance_transform_edt(a <= 1, return_indices=True)
    near = a[iy, ix]
    arm = M & isarm[near]
    xx = np.arange(a.shape[1])[None, :]
    A = np.where(arm, np.where(xx < c, 1, 2), 0).astype(np.int8)
    B = M & ~arm
    L = landmarks(M, c, A)
    ys, xs = np.nonzero((a > 1))
    sl = slug[a[ys, xs]]
    def mean_y(names):
        m = np.isin(sl, list(names)); return ys[m].mean() if m.any() else None
    if FIG == "female" and view == "front":
        # her figure keeps a wide gap down the linea alba that runs into the gap between the legs,
        # so the first empty midline row is at the chest; the crotch is the tip of the lower abs instead
        L["crotch"] = ys[sl == "lowerAbs"].max()
    L["knee"] = mean_y({"knees"}) if view == "front" else (np.percentile(ys[sl == "hamstring"], 98) + np.percentile(ys[sl == "calves"], 2)) / 2
    L["ankle"] = mean_y({"ankles"})
    arms = {}
    for k in (1, 2):
        o, ax, pp, P = arm_frame(A, k)
        t, s = ts(P, o, ax, pp)
        m = (A[ys, xs] == k)
        tt, _ = ts(np.stack([xs[m], ys[m]], 1).astype(float), o, ax, pp); ss = sl[m]
        upper = [n for n in UPPER if n in set(ss)]
        el = (np.percentile(tt[np.isin(ss, upper)], 97) + np.percentile(tt[ss == "forearm"], 3)) / 2
        wr = (np.percentile(tt[ss == "forearm"], 97) + np.percentile(tt[ss == "hands"], 3)) / 2
        arms[k] = dict(o=o, a=ax, p=pp, t0=t.min(), t1=t.max(), el=el, wr=wr, prof=width_profile(t, s, t.min(), t.max()))
    return dict(a=a, near=near, M=M, B=B, A=A, c=c, L=L, rows=row_maps(B), arms=arms)


# ---------------------------------------------------------------- 3D body seen from the front / back
R = 700.0  # px per metre for the mesh silhouette
PART = d["part"]   # 0 torso 1 armL 2 armR 3 legL 4 legR
def body_view(view):
    X = CO[:, 0] if view == "front" else -CO[:, 0]
    xmin, zmax = -1.0, CO[:, 2].max() + 0.02
    W, Hh = int(2.0 * R), int((zmax - CO[:, 2].min() + 0.04) * R)
    col = (X - xmin) * R; row = (zmax - CO[:, 2]) * R
    # arm id as seen in this view: 1 = viewer-left, 2 = viewer-right
    if view == "front": vk = np.select([PART == 2, PART == 1], [1, 2], 0)
    else: vk = np.select([PART == 1, PART == 2], [1, 2], 0)
    imgs = {k: Image.new("1", (W, Hh), 0) for k in (0, 1, 2)}; drs = {k: ImageDraw.Draw(imgs[k]) for k in imgs}
    tk = vk[TRIS]; tri_k = np.where((tk == tk[:, :1]).all(1), tk[:, 0], 0)
    for tri, k in zip(TRIS, tri_k):
        drs[int(k)].polygon([(col[i], row[i]) for i in tri], fill=1)
    Bm = ndi.binary_closing(np.array(imgs[0], bool), iterations=1)
    A = np.zeros(Bm.shape, np.int8)
    for k in (1, 2): A[ndi.binary_closing(np.array(imgs[k], bool), iterations=1)] = k
    M = Bm | (A > 0); Bm = Bm & (A == 0)
    c = int(round((0 - xmin) * R))
    L = landmarks(M, c, A)
    L["ankle"] = (zmax - jp("L_Ankle")[2]) * R
    arms = {}
    for k in (1, 2):
        o, ax, pp, P = arm_frame(A, k)
        t, s = ts(P, o, ax, pp)
        side = ("R" if k == 1 else "L") if view == "front" else ("L" if k == 1 else "R")
        def tj(n):
            v = jp(n); q = np.array([((v[0] if view == "front" else -v[0]) - xmin) * R, (zmax - v[2]) * R])
            return float((q - o) @ ax)
        arms[k] = dict(o=o, a=ax, p=pp, t0=t.min(), t1=t.max(), el=tj(side + "_Elbow"), wr=tj(side + "_Wrist"),
                       prof=width_profile(t, s, t.min(), t.max()))
    return dict(col=col, row=row, M=M, B=Bm, A=A, vk=vk, c=c, L=L, rows=row_maps(Bm), arms=arms, zmax=zmax)


# landmarks read by eye: (name, MuscleMap SVG y, body z in metres)
EXTRA = {"front": [("chest", 425, 0.11), ("navel", 580, -0.085), ("knee", 1006, -0.61)],
         "back": [("scap", 405, 0.10), ("glute_top", 630, -0.15), ("glute_fold", 778, -0.31), ("knee", 989, -0.64)]}
# female: the same features found on that figure (chest = breast fold, knee from her lower joint) and on
# her body by the same profile rules (pec/breast recession, navel dimple, buttock rise and fold)
if FIG == "female":
    EXTRA = {"front": [("chest", 423, 0.078), ("navel", 559, -0.10), ("knee", 1024, -0.65)],
             "back": [("scap", 377, 0.11), ("glute_top", 612, -0.15), ("glute_fold", 792, -0.325), ("knee", 994, -0.68)]}


def pw(v, src, dst):
    return np.interp(v, src, dst)


def map_view(view, idx):
    F = figure(view); Bv = body_view(view)
    keys = ["top", "neck", "shoulder", "crotch", "ankle", "sole"]
    if view == "back": keys.remove("crotch")
    src = [Bv["L"][k] for k in keys]; dst = [F["L"][k] for k in keys]
    y0 = J["vb"][view][1]
    for _, ysvg, z in EXTRA[view]:
        src.append((Bv["zmax"] - z) * R); dst.append((ysvg - y0) * S)
    o_ = np.argsort(src); src = list(np.array(src)[o_]); dst = list(np.array(dst)[o_])
    assert np.all(np.diff(dst) > 0), ("landmarks out of order", view, src, dst)
    out = np.full(len(idx), 0, np.int32); how = np.zeros(len(idx), np.int8)
    a, near = F["a"], F["near"]
    Hh, W = a.shape
    for n, i in enumerate(idx):
        cx, ry = Bv["col"][i], Bv["row"][i]
        r = int(np.clip(round(ry), 0, Bv["M"].shape[0] - 1)); cc = int(np.clip(round(cx), 0, Bv["M"].shape[1] - 1))
        k = int(Bv["vk"][i])
        if k:
            ba, fa = Bv["arms"][k], F["arms"][k]
            t, s = ts(np.array([[cx, ry]]), ba["o"], ba["a"], ba["p"]); t, s = t[0], s[0]
            lo, hi = ba["prof"](t); u = (s - lo) / max(hi - lo, 1e-6)
            t2 = pw(t, [ba["t0"], ba["el"], ba["wr"], ba["t1"]], [fa["t0"], fa["el"], fa["wr"], fa["t1"]])
            lo2, hi2 = fa["prof"](t2); s2 = lo2 + u * (hi2 - lo2)
            P2 = fa["o"] + t2 * fa["a"] + s2 * fa["p"]; px, py = P2
            how[n] = 2
        else:
            iv = Bv["rows"][r]
            if not iv:
                continue
            j = min(range(len(iv)), key=lambda q: 0 if iv[q][0] <= cx <= iv[q][1] else min(abs(cx - iv[q][0]), abs(cx - iv[q][1])))
            l, rr = iv[j]; u = (cx - l) / max(rr - l, 1)
            py = pw(ry, src, dst); r2 = int(np.clip(round(py), 0, Hh - 1))
            iv2 = F["rows"][r2]
            if not iv2: continue
            if len(iv2) == len(iv):
                l2, r2_ = iv2[j]
            else:
                # one side has the legs split and the other not yet: map the whole row span onto the whole row span
                l, rr = iv[0][0], iv[-1][1]; u = (cx - l) / max(rr - l, 1)
                l2, r2_ = iv2[0][0], iv2[-1][1]
            px = l2 + u * (r2_ - l2)
            how[n] = 1
        xi, yi = int(np.clip(round(px), 0, W - 1)), int(np.clip(round(py), 0, Hh - 1))
        out[n] = near[yi, xi]
    return out, how, F, Bv


ny = NM[:, 1]
front = np.where(ny < 0)[0]; back = np.where(ny >= 0)[0]
lab = np.zeros(len(CO), np.int32)
for view, idx in (("front", front), ("back", back)):
    o, how, F, Bv = map_view(view, idx)
    lab[idx] = o
    print(view, "landmarks fig", {k: round(float(v)) for k, v in F["L"].items()}, "body", {k: round(float(v)) for k, v in Bv["L"].items()})
    print(view, "arm els fig", [(round(F['arms'][k]['t0']), round(F['arms'][k]['el']), round(F['arms'][k]['wr']), round(F['arms'][k]['t1'])) for k in (1, 2)],
          "body", [(round(Bv['arms'][k]['t0']), round(Bv['arms'][k]['el']), round(Bv['arms'][k]['wr']), round(Bv['arms'][k]['t1'])) for k in (1, 2)])
    print(view, "unlabelled", int((o == 0).sum()), "arm-mapped", int((how == 2).sum()))
np.save(OUT, lab)
print("saved", OUT, "distinct ids", len(np.unique(lab)))

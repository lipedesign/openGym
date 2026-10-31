# Labels for the anatomy plates: where each muscle region sits on the flat front/back renders,
# which column its label goes to, and approximate spots for the regions proposed for v2.
# Usage: PLATE_V2=1 python3 body/plate.py  or  PLATE_FIG=female python3 body/plate.py
# Reads work/<body|body_f>/seams_v2.npz and out/flat-{front,back}-none* (body/render.sh), writes work/atlas/ (or HEX_ATLAS).
import json, os
import numpy as np
from PIL import Image

D = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.dirname(D), "work")
OUTD = os.environ.get("HEX_ATLAS", os.path.join(WORK, "atlas")); os.makedirs(os.path.join(OUTD, "img"), exist_ok=True)
V2 = os.environ.get("PLATE_V2") == "1"     # v2 body: real regions, new ones flagged, no proposal pins
FEM = os.environ.get("PLATE_FIG") == "female"   # female body (v2 only): reads work/body_f, writes *-v2-f
if FEM: V2 = True
BD = os.path.join(WORK, "body_f" if FEM else "body")
SFX = "-v2-f" if FEM else ("-v2" if V2 else "")
S = np.load(os.path.join(BD, "seams_v2.npz" if V2 else "seams.npz"), allow_pickle=True)
slug = S["slug"]

NAME = {
    "upperChest": "Peito alto", "chest": "Peito médio", "lowerChest": "Peito baixo",
    "frontDeltoid": "Deltoide frontal", "deltoids": "Deltoide lateral", "rearDeltoid": "Deltoide posterior",
    "biceps": "Bíceps", "triceps": "Tríceps", "forearm": "Antebraço",
    "upperAbs": "Reto abdominal", "lowerAbs": "Abdômen baixo", "obliques": "Oblíquo externo",
    "serratus": "Serrátil anterior", "upperTrapezius": "Trapézio superior", "trapezius": "Trapézio médio",
    "lowerTrapezius": "Trapézio inferior", "upperBack": "Dorsal", "rhomboids": "Romboides",
    "rotatorCuff": "Manguito rotador", "lowerBack": "Lombar", "gluteal": "Glúteos",
    "hipFlexors": "Flexores do quadril", "quadriceps": "Reto femoral", "innerQuad": "Vasto medial",
    "outerQuad": "Vasto lateral", "adductors": "Adutores", "hamstring": "Posterior de coxa",
    "calves": "Panturrilha", "tibialis": "Tibial anterior",
}
NEW = {"gluteusMedius": "Glúteo médio", "soleus": "Sóleo", "brachialis": "Braquial", "teresMajor": "Redondo maior",
       "sternocleidomastoid": "Esternocleidomastóideo", "neckBack": "Nuca", "tricepsLongHead": "Tríceps, cabeça longa"}
if V2:
    NAME.update(NEW)
    NAME.update({"triceps": "Tríceps lateral", "calves": "Gastrocnêmio", "gluteal": "Glúteo máximo"})
SKIP = {"front": {"upperBack", "rhomboids", "lowerBack", "rotatorCuff", "trapezius", "lowerTrapezius", "rearDeltoid", "hamstring", "gluteal", "triceps"},
        "back": {"upperChest", "chest", "lowerChest", "upperAbs", "lowerAbs", "frontDeltoid", "biceps", "hipFlexors", "quadriceps", "innerQuad", "tibialis", "serratus", "obliques"}}
if V2:
    SKIP["front"] |= {"teresMajor", "neckBack", "tricepsLongHead", "gluteusMedius"}
    SKIP["back"] |= {"sternocleidomastoid", "brachialis"}


def visible(A, grid=420, tol=0.012):
    uv, dep, fac = A["uv"], A["dep"], A["fac"]
    ix = np.clip((uv * grid).astype(int), 0, grid - 1)
    key = ix[:, 1] * grid + ix[:, 0]
    mn = np.full(grid * grid, np.inf)
    np.minimum.at(mn, key, dep)
    return fac & (dep <= mn[key] + tol)


def nearest(uv, idx, p):
    k = idx[np.argmin(((uv[idx] - p) ** 2).sum(1))]
    return uv[k]


def plate(view):
    base = os.path.join(BD, "out", f"flat-{view}-none") if V2 else os.path.join(BD, "out", "v1", f"flat-{view}-none")
    A = np.load(base + "_anchors.npz")
    uv, co = A["uv"], A["co"]
    vis = visible(A)
    im = Image.open(base + ".png").convert("RGBA"); W, Hh = im.size
    bb = im.getchannel("A").getbbox(); pad = 12
    bb = (bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad)
    crop = im.crop(bb); cw, ch = crop.size
    sc = 1100 / ch
    crop.resize((round(cw * sc), 1100), Image.LANCZOS).save(os.path.join(OUTD, "img", f"plate-{view}{SFX}.webp"), "WEBP", quality=86, method=6)
    def px(p):   # normalised render coords -> output image pixels
        return [round((p[0] * W - bb[0]) * sc, 1), round((p[1] * Hh - bb[1]) * sc, 1)]
    # image-left side of the body: front view shows the body's right (-x) there, back view its left (+x)
    left_of_image = (co[:, 0] < 0) if view == "front" else (co[:, 0] > 0)
    cand = {}
    for s in NAME:
        if s in SKIP[view]: continue
        m = vis & (slug == s)
        small = V2 and s in NEW               # the new regions are small; label them anyway
        if m.sum() < (60 if small else 250): continue
        cand[s] = {}
        for side, mm in (("L", m & left_of_image), ("R", m & ~left_of_image)):
            idx = np.where(mm)[0]
            if len(idx) < (30 if small else 120): continue
            cand[s][side] = nearest(uv, idx, uv[idx].mean(0))
        if not cand[s]: del cand[s]
    # columns: walk top to bottom, put each label where its neighbourhood is emptier
    order = sorted(cand, key=lambda s: np.mean([p[1] for p in cand[s].values()]))
    cols = {"L": [], "R": []}
    for s in order:
        y = np.mean([p[1] for p in cand[s].values()])
        def cost(c):
            if c not in cand[s]: return 1e9
            return sum(abs(y - yy) < 0.05 for _, yy in cols[c]) + 0.15 * len(cols[c])
        c = min(("L", "R"), key=cost)
        cols[c].append((s, cand[s][c][1]))
    labels = []
    for c, lst in cols.items():
        lst.sort(key=lambda t: t[1])
        ys = [t[1] for t in lst]
        gap = 0.034
        for _ in range(200):           # spread labels apart, keep them near their anchors
            for i in range(1, len(ys)):
                if ys[i] - ys[i - 1] < gap:
                    mid = (ys[i] + ys[i - 1]) / 2; ys[i - 1] = mid - gap / 2; ys[i] = mid + gap / 2
            ys = [min(max(y, 0.03), 0.97) for y in ys]
        for (s, _), y in zip(lst, ys):
            a = px(cand[s][c])
            labels.append(dict(slug=s, name=NAME[s], col=c, ax=a[0], ay=a[1], ly=round((y * Hh - bb[1]) * sc, 1), new=V2 and s in NEW))
    # proposed v2 regions: approximate spots on the current body
    z, x = co[:, 2], co[:, 0]
    def spot(mask, pick):
        idx = np.where(mask & vis)[0]
        if len(idx) == 0: return None
        sel = idx[pick(idx)]
        return px(nearest(uv, sel, uv[sel].mean(0)))
    trapz = z[slug == "upperTrapezius"].max()
    chin_band = (slug == "skin") & (z > trapz - 0.02) & (z < trapz + 0.06) & (np.abs(x) > 0.012) & (np.abs(x) < 0.045)
    v2 = []
    if V2:
        return dict(view=view, w=round(cw * sc), h=1100, labels=labels, v2=[])
    side_img = left_of_image if True else None
    if view == "front":
        v2.append(dict(n=5, name="Esternocleidomastóideo", p=spot(chin_band & side_img, lambda i: np.ones(len(i), bool))))
        bi = (slug == "biceps") & side_img
        zb = z[bi]
        v2.append(dict(n=3, name="Braquial", p=spot(bi, lambda i: (z[i] < np.percentile(zb, 30)) & (np.abs(x[i]) > np.percentile(np.abs(x[bi]), 50)))))
    else:
        g = (slug == "gluteal") & ~side_img
        v2.append(dict(n=1, name="Glúteo médio", p=spot(g, lambda i: (z[i] > np.percentile(z[g], 70)) & (np.abs(x[i]) > np.percentile(np.abs(x[g]), 45)))))
        cv = (slug == "calves") & side_img
        v2.append(dict(n=2, name="Sóleo", p=spot(cv, lambda i: z[i] < np.percentile(z[cv], 30))))
        rc = (slug == "rotatorCuff") & ~side_img
        v2.append(dict(n=4, name="Redondo maior", p=spot(rc, lambda i: (z[i] < np.percentile(z[rc], 30)) & (np.abs(x[i]) > np.percentile(np.abs(x[rc]), 50)))))
        v2.append(dict(n=6, name="Nuca (esplênios e levantador)", p=spot(chin_band & ~side_img, lambda i: np.ones(len(i), bool))))
        tr = (slug == "triceps") & side_img
        v2.append(dict(n=7, name="Cabeça longa do tríceps", p=spot(tr, lambda i: (z[i] > np.percentile(z[tr], 40)) & (np.abs(x[i]) < np.percentile(np.abs(x[tr]), 40)))))
    return dict(view=view, w=round(cw * sc), h=1100, labels=labels, v2=[v for v in v2 if v["p"]])


out = {v: plate(v) for v in ("front", "back")}
json.dump(out, open(os.path.join(OUTD, "plates_v2_f.json" if FEM else ("plates_v2.json" if V2 else "plates.json")), "w"), ensure_ascii=False, indent=1)
for v, d in out.items():
    print(v, d["w"], "labels", len(d["labels"]), [l["name"] for l in d["labels"]], "v2", [(x["name"], x["p"]) for x in d["v2"]])

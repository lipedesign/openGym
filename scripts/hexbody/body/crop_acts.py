# Crop the activation renders for the atlas as 900 px tall webp files.
# The v1 examples keep the whole body; the v2 examples are framed around what lights up.
# Usage: python3 body/crop_acts.py male|female
# Reads work/<body|body_f>/out (body/render.sh), writes work/atlas/img (or HEX_ATLAS/img), "-f" suffix for the female body.
import os, sys
import numpy as np
from PIL import Image

FIG = sys.argv[1] if len(sys.argv) > 1 else "male"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "work", "body_f" if FIG == "female" else "body", "out")
DST = os.path.join(os.environ.get("HEX_ATLAS", os.path.join(ROOT, "work", "atlas")), "img")
SFX = "-f" if FIG == "female" else ""
os.makedirs(DST, exist_ok=True)

V1 = ["q34-supino", "front-supino_inclinado", "front-elevacao_lateral", "q34-agachamento", "back-remada", "q34-rosca", "front-abdominal"]
V2 = ["q34b-abdutora", "back-panturrilha_sentada", "side-rosca_martelo", "back-puxada",
      "q34b-triceps_frances", "q34-flexao_pescoco", "back-extensao_pescoco"]


def save(cr, a):
    cr = cr.resize((round(cr.width * 900 / cr.height), 900), Image.LANCZOS)
    cr.save(os.path.join(DST, f"flat-{a}{SFX}.webp"), "WEBP", quality=86, method=6)
    print(a, cr.size)


def load(a):
    p = os.path.join(SRC, f"flat-{a}.png")
    if not os.path.exists(p):
        print("missing", p); return None
    return Image.open(p).convert("RGBA")


for a in V1:
    im = load(a)
    if im is None: continue
    bb = im.getchannel("A").getbbox(); p = 12
    save(im.crop((bb[0] - p, bb[1] - p, bb[2] + p, bb[3] + p)), a)

for a in V2:
    im = load(a)
    if im is None: continue
    A = np.asarray(im).astype(int)
    body = A[..., 3] > 10
    lit = body & (A[..., 2] - A[..., 0] > 45)
    ys, xs = np.nonzero(lit); by, bx = np.nonzero(body)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    w, h = x1 - x0, y1 - y0
    mx, my = max(0.45 * w, 0.18 * h), max(0.30 * h, 0.12 * w)
    x0, x1, y0, y1 = x0 - mx, x1 + mx, y0 - my, y1 + my
    if (x1 - x0) / (y1 - y0) < 0.45:            # too thin: widen around the centre
        c = (x0 + x1) / 2; hw = 0.45 * (y1 - y0) / 2; x0, x1 = c - hw, c + hw
    if (x1 - x0) / (y1 - y0) > 1.0:             # too wide: grow the height
        c = (y0 + y1) / 2; hh = (x1 - x0) / 2; y0, y1 = c - hh, c + hh
    x0 = max(x0, bx.min() - 12); x1 = min(x1, bx.max() + 12); y0 = max(y0, by.min() - 12); y1 = min(y1, by.max() + 12)
    save(im.crop((int(x0), int(y0), int(x1), int(y1))), a)

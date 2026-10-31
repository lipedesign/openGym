#!/bin/zsh
# Render one body for the atlas: the plain views (with anchors for plate.py), the v1 activation examples
# and one activation per v2 region, all with the v2 seams.
# Usage: body/render.sh male|female
# Overrides: BLENDER (binary), OUT (folder), RES (pixels, 1500), SAMPLES (32).
set -e
cd "${0:A:h}/.."
case ${1:-male} in
  male) W=work/body ;;
  female) W=work/body_f ;;
  *) echo "usage: $0 male|female"; exit 1 ;;
esac
B=${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}
O=${OUT:-$W/out}; RES=${RES:-1500}; SAMPLES=${SAMPLES:-32}
mkdir -p $O
export HEX_SEAMS=$PWD/$W/seams_v2.npz
r() { HEX_ANCHORS=${3:-} $B -b $W/hexbody_rig.blend -P blender/bodymodel.py -- flat $1 $2 $O/flat-$1-$2.png $RES $SAMPLES 2>&1 | grep -E "rror|Traceback" -A4 | head -8; echo "done $1 $2"; }
r front none 1; r back none 1; r side none
r q34 supino; r front supino_inclinado; r front elevacao_lateral; r q34 agachamento; r back remada; r q34 rosca; r front abdominal
r q34b abdutora; r back panturrilha_sentada; r side rosca_martelo; r back puxada
r q34b triceps_frances; r q34 flexao_pescoco; r back extensao_pescoco

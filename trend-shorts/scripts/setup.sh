#!/usr/bin/env bash
# One-time setup: npm packages, Python packages and VOICEVOX (core + onnxruntime + voice models).
# Usage: bash scripts/setup.sh [vvm numbers...]   (default: 15 = 青山龍星, 1 = 冥鳴ひまり)
set -euo pipefail
cd "$(dirname "$0")/.."

CORE=0.16.4
ORT=1.17.3
VV=voicevox
MODELS=("${@:-15 1}")

npm ci
pip install -q pyopenjtalk-plus

mkdir -p "$VV"
gh_dl() { # repo tag asset -> $VV/asset
  [ -s "$VV/$3" ] || curl -fsSL -o "$VV/$3" "https://github.com/VOICEVOX/$1/releases/download/$2/$3"
}
WHEEL="voicevox_core-$CORE-cp310-abi3-manylinux_2_34_x86_64.whl"
gh_dl voicevox_core "$CORE" "$WHEEL"
pip install -q "$VV/$WHEEL"

ORT_TGZ="voicevox_onnxruntime-linux-x64-$ORT.tgz"
gh_dl onnxruntime-builder "voicevox_onnxruntime-$ORT" "$ORT_TGZ"
[ -d "$VV/voicevox_onnxruntime-linux-x64-$ORT" ] || tar xzf "$VV/$ORT_TGZ" -C "$VV"

for n in ${MODELS[@]}; do gh_dl voicevox_vvm "$CORE" "$n.vvm"; done
echo "setup done. voices: $(ls $VV/*.vvm | xargs -n1 basename | tr '\n' ' ')"

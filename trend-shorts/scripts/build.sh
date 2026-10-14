#!/usr/bin/env bash
# Build one episode: narration → video → check sheet → description text.
# Usage: bash scripts/build.sh episodes/<slug>.json
set -euo pipefail
cd "$(dirname "$0")/.."
EP="${1:-episodes/polsia.json}"
SLUG="$(basename "$EP" .json)"
mkdir -p out

# Use a local Chromium when Remotion cannot download its own (e.g. restricted networks).
BROWSER_ARGS=()
for b in "${REMOTION_BROWSER:-}" /opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell; do
  if [ -n "$b" ] && [ -x "$b" ]; then BROWSER_ARGS=(--browser-executable="$b"); break; fi
done

# The episode must follow its template and the 1→10 rotation (SKIP_ROTATION=1 to bypass the order).
python3 script/template_check.py "$EP"

VOICEVOX_DIR="${VOICEVOX_DIR:-$PWD/voicevox}" python3 script/tts.py "$EP"
npx tsc --noEmit
npx remotion render TrendShort "out/$SLUG.mp4" "${BROWSER_ARGS[@]}" --log=error

# Check sheet: one still at the end of every narration line.
FRAMES=$(python3 -c "
import json; t = json.load(open('src/timeline.json')); c = 0
for l in t['lines']:
    d = round(l['seconds'] * 30); print(c + d - 6); c += d")
rm -rf out/check && mkdir -p out/check
i=0; for f in $FRAMES; do
  npx remotion still TrendShort "out/check/$(printf %02d $i).png" --frame="$f" --scale=0.33 "${BROWSER_ARGS[@]}" --log=error
  i=$((i+1))
done
python3 script/contact_sheet.py out/check "out/$SLUG-check.png"

python3 -c "
import json; t = json.load(open('$EP'))
print(t.get('description', '').rstrip() + '\n\n■ ナレーション\nVOICEVOX:' + t['voice']['name'])" > "out/$SLUG-description.txt"

echo "video:       out/$SLUG.mp4 ($(ffprobe -v error -show_entries format=duration -of csv=p=0 "out/$SLUG.mp4")s)"
echo "check sheet: out/$SLUG-check.png"
echo "description: out/$SLUG-description.txt"

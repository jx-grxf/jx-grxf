#!/usr/bin/env bash
# make-demo.sh — turn a screen recording into a README GIF + a social video.
#
# Record first:  ⌘⇧5 → "Record Selected Portion" → keep it 8–20s → save the .mov
# Then:          ./tools/make-demo.sh ~/Desktop/recording.mov ~/code/poise
#
# Produces, inside <repo>/.github/assets/:
#   demo.gif  — palette-optimised, ≤720px wide, for the README
#   demo.mp4  — H.264, for X / LinkedIn (both prefer video over GIF)
#
# Requires: ffmpeg  (brew install ffmpeg)

set -euo pipefail

IN="${1:-}"
REPO="${2:-.}"
START="${3:-0}"
DUR="${4:-}"
WIDTH="${DEMO_WIDTH:-720}"
FPS="${DEMO_FPS:-14}"

if [[ -z "$IN" || ! -f "$IN" ]]; then
  echo "usage: $0 <recording.mov> [repo-dir] [start-seconds] [duration-seconds]" >&2
  echo "  env: DEMO_WIDTH=720  DEMO_FPS=14" >&2
  exit 1
fi
command -v ffmpeg >/dev/null || { echo "ffmpeg not found — brew install ffmpeg" >&2; exit 1; }

OUT_DIR="$REPO/.github/assets"
mkdir -p "$OUT_DIR"

TRIM=(-ss "$START")
[[ -n "$DUR" ]] && TRIM+=(-t "$DUR")

PALETTE="$(mktemp -t palette).png"
trap 'rm -f "$PALETTE"' EXIT

echo "→ building colour palette…"
ffmpeg -hide_banner -loglevel error -y "${TRIM[@]}" -i "$IN" \
  -vf "fps=${FPS},scale=${WIDTH}:-2:flags=lanczos,palettegen=stats_mode=diff" \
  "$PALETTE"

echo "→ encoding demo.gif…"
ffmpeg -hide_banner -loglevel error -y "${TRIM[@]}" -i "$IN" -i "$PALETTE" \
  -lavfi "fps=${FPS},scale=${WIDTH}:-2:flags=lanczos[v];[v][1:v]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle" \
  "$OUT_DIR/demo.gif"

echo "→ encoding demo.mp4…"
ffmpeg -hide_banner -loglevel error -y "${TRIM[@]}" -i "$IN" \
  -vf "scale=1280:-2:flags=lanczos,format=yuv420p" \
  -c:v libx264 -profile:v high -crf 20 -movflags +faststart -an \
  "$OUT_DIR/demo.mp4"

gif_size=$(du -h "$OUT_DIR/demo.gif" | cut -f1 | tr -d ' ')
mp4_size=$(du -h "$OUT_DIR/demo.mp4" | cut -f1 | tr -d ' ')

echo
echo "✓ $OUT_DIR/demo.gif  ($gif_size)"
echo "✓ $OUT_DIR/demo.mp4  ($mp4_size)"

case "$gif_size" in
  *M) num=${gif_size%M}; if (( ${num%.*} > 9 )); then
        echo "⚠  GitHub soft-limits README images around 10 MB."
        echo "   Retry shorter, or: DEMO_WIDTH=600 DEMO_FPS=10 $0 $IN $REPO"
      fi;;
esac

echo
echo "Paste this into the README, directly under the badge block:"
echo
echo '<p align="center">'
echo '  <img src=".github/assets/demo.gif" alt="TODO: describe what the demo shows" width="720">'
echo '</p>'
echo

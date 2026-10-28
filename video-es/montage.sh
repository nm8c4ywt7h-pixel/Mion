#!/usr/bin/env bash
# Assemble une vidéo TikTok verticale au rythme "jump cut".
# Usage : ./montage.sh <dossier_rushs> <voix.mp3|-> <musique.mp3|-> <sous-titres.srt|-> <sortie.mp4>
#   - dossier_rushs : clips nommés 01.mp4, 02.mp4, ... (dans l'ordre du plan de tournage)
#   - un clip sur deux reçoit un zoom punch-in de 112 %
#   - musique : baissée automatiquement quand la voix parle (ducking)
#   - sous-titres : incrustés en gros, gras, contour noir
set -euo pipefail

CLIPS_DIR=$1; VOICE=$2; MUSIC=$3; SUBS=$4; OUT=$5
MAX_LEN=${MAX_LEN:-2.5}   # durée max d'un plan (s)
ZOOM=${ZOOM:-1.12}
ACCENT=${ACCENT:-&H0000D7FF}   # couleur ASS (BGR) des sous-titres : jaune-orangé

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT

i=0
for clip in "$CLIPS_DIR"/*.mp4; do
  zoom_filter=""
  if (( i % 2 == 1 )); then
    zoom_filter=",scale=iw*${ZOOM}:ih*${ZOOM},crop=1080:1920"
  fi
  ffmpeg -loglevel error -y -i "$clip" -t "$MAX_LEN" \
    -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920${zoom_filter},fps=30,setsar=1" \
    -an -c:v libx264 -preset veryfast -crf 18 "$TMP/$(printf %02d $i).mp4"
  echo "file '$TMP/$(printf %02d $i).mp4'" >> "$TMP/list.txt"
  i=$((i + 1))
done

ffmpeg -loglevel error -y -f concat -safe 0 -i "$TMP/list.txt" -c copy "$TMP/video.mp4"

vf="null"
if [[ "$SUBS" != "-" ]]; then
  cp "$SUBS" "$TMP/subs.srt"
  vf="subtitles=$TMP/subs.srt:force_style='FontName=DejaVu Sans,Bold=1,FontSize=16,PrimaryColour=${ACCENT},OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=0,Alignment=2,MarginV=110'"
fi

inputs=(-i "$TMP/video.mp4")
if [[ "$VOICE" != "-" && "$MUSIC" != "-" ]]; then
  inputs+=(-i "$VOICE" -stream_loop -1 -i "$MUSIC")
  af="[2:a]volume=0.35[m];[1:a]asplit[v][sc];[m][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[md];[v][md]amix=inputs=2:duration=first:normalize=0[a]"
elif [[ "$VOICE" != "-" ]]; then
  inputs+=(-i "$VOICE"); af="[1:a]anull[a]"
elif [[ "$MUSIC" != "-" ]]; then
  inputs+=(-i "$MUSIC"); af="[1:a]volume=0.6[a]"
else
  af=""
fi

if [[ -n "$af" ]]; then
  ffmpeg -loglevel error -y "${inputs[@]}" -filter_complex "[0:v]${vf}[vout];${af}" \
    -map "[vout]" -map "[a]" -shortest -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k \
    -movflags +faststart "$OUT"
else
  ffmpeg -loglevel error -y -i "$TMP/video.mp4" -vf "$vf" -c:v libx264 -crf 18 -movflags +faststart "$OUT"
fi
echo "OK -> $OUT"

#!/usr/bin/env bash
# Turn each cast into a still of its last screen: agg draws the frames, magick keeps the last one.
#     render.sh <cast dir> <out dir>
set -euo pipefail
in=$1; out=$2; mkdir -p "$out"
theme=121212,d9d6cf,1b1e1b,e5534b,57ab5a,e2b857,539bf5,b083f0,39c5cf,cdd1cc,6b6962,f47067,6bc46d,fbc04e,6cb6ff,dcbdfb,56d4dd,ece9e2
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
for cast in "$in"/*.cast; do
  name=$(basename "$cast" .cast)
  agg -q --font-family 'Inconsolata Nerd Font Mono' --font-size 18 --line-height 1.35 --theme "$theme" \
    --idle-time-limit 2 --last-frame-duration 1 "$cast" "$tmp/$name.gif"
  magick "$tmp/$name.gif" -coalesce "$tmp/$name-%04d.png"
  cp "$(ls "$tmp/$name"-*.png | sort | tail -1)" "$out/$name.png"
done

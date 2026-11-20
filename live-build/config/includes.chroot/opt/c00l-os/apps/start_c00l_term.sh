#!/bin/sh
# c00l_Term -- a real terminal (xterm) themed to match c00l_OS, with a tiny
# SFX hook on launch. A genuine shell: nothing here is emulated or faked.
set -e

SFX_DIR="/opt/c00l-os/assets/sfx"
if command -v paplay >/dev/null 2>&1; then
    paplay "$SFX_DIR/button.wav" >/dev/null 2>&1 &
elif command -v aplay >/dev/null 2>&1; then
    aplay "$SFX_DIR/button.wav" >/dev/null 2>&1 &
fi

ACCENT="#cd1c26"
CFG="/etc/c00l-os/config.json"
if [ -r "$CFG" ] && command -v python3 >/dev/null 2>&1; then
    PARSED=$(python3 -c "import json;print(json.load(open('$CFG')).get('accent','#cd1c26'))" 2>/dev/null) || true
    [ -n "$PARSED" ] && ACCENT="$PARSED"
fi

exec xterm \
    -class c00lTerm \
    -title "c00l_Term" \
    -fa "DejaVu Sans Mono" -fs 12 \
    -bg "#0a0a0c" -fg "$ACCENT" \
    -cr "$ACCENT" \
    -bw 2 \
    -geometry 100x30 \
    -e /bin/bash -l

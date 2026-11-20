#!/usr/bin/env python3
"""
sound_util.py -- shared SFX playback for every c00l_OS app.

Tries, in order: paplay (PulseAudio) -> aplay (ALSA) -> ffplay (ffmpeg).
Whichever is installed and working wins; if none work, playback is
silently skipped so a missing audio device never crashes an app.

Sound can be globally muted by writing {"sound": false} into
/etc/c00l-os/config.json (the setup wizard does this when the user
unchecks "Enable sound" at first boot).
"""
import json
import os
import shutil
import subprocess
import threading

SFX_DIR = "/opt/c00l-os/assets/sfx"
CONFIG_PATH = "/etc/c00l-os/config.json"

_player_cmd = None
for _cmd in ("paplay", "aplay", "ffplay"):
    if shutil.which(_cmd):
        _player_cmd = _cmd
        break

SOUNDS = {
    "button": "button.wav",
    "click": "clickfast.wav",
    "snap": "snap.wav",
    "hit": "hit.wav",
    "splat": "splat.wav",
    "collide": "collide.wav",
    "victory": "victory.wav",
    "slash": "swordslash.wav",
    "ping": "ping.wav",
    "ouch": "ouch.wav",
    "boot": "bass.wav",
}


def _sound_enabled():
    try:
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        return bool(cfg.get("sound", True))
    except Exception:
        return True


def play(name, blocking=False):
    """Play a named SFX (see SOUNDS). Fire-and-forget by default."""
    if _player_cmd is None or not _sound_enabled():
        return
    filename = SOUNDS.get(name, name)
    path = filename if os.path.isabs(filename) else os.path.join(SFX_DIR, filename)
    if not os.path.isfile(path):
        return

    def _run():
        try:
            if _player_cmd == "ffplay":
                cmd = ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]
            else:
                cmd = [_player_cmd, path]
            subprocess.run(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except Exception:
            pass

    if blocking:
        _run()
    else:
        threading.Thread(target=_run, daemon=True).start()


if __name__ == "__main__":
    import sys

    play(sys.argv[1] if len(sys.argv) > 1 else "button", blocking=True)

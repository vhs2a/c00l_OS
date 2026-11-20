#!/bin/sh
# Launched by lightdm (via /usr/share/xsessions/c00l-os.desktop) once the
# c00l user is auto-logged in. Starts the window manager, then hands off
# to shell.py, which is itself the wizard-or-panel session leader.
export XCURSOR_THEME=c00l-os-cursors
export XCURSOR_SIZE=32

openbox &
exec python3 /opt/c00l-os/apps/shell.py

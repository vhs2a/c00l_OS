#!/bin/bash
# Builds c00l_OS into a bootable .iso using live-build (Debian's official
# live-image build tool). Run this AS ROOT on a Debian or Ubuntu machine/VM
# with internet access -- NOT inside this chat's sandbox, which has no
# network access and can't build ISOs. See BUILD_TUTORIAL.md for the
# no-Linux-machine-needed alternative (GitHub Actions).
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this as root (sudo ./build.sh)" >&2
    exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

echo "==> Installing live-build (and friends) if missing..."
if ! command -v lb >/dev/null 2>&1; then
    apt-get update
    apt-get install -y live-build live-boot live-config
fi

echo "==> Cleaning any previous build state..."
cd "$HERE/live-build"
lb clean --purge || true

echo "==> Configuring the live image (Debian bookworm, amd64)..."
lb config \
    --architecture amd64 \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --iso-application "c00l_OS" \
    --iso-volume "c00l_OS"

echo "==> Building the ISO (this downloads packages -- needs internet, takes 15-40 min)..."
lb build

ISO=$(ls -t live-image-*.hybrid.iso 2>/dev/null | head -n1 || true)
if [ -z "$ISO" ]; then
    echo "Build finished but no .iso was found -- check the log above for errors." >&2
    exit 1
fi

mkdir -p "$HERE/out"
mv "$ISO" "$HERE/out/c00l_OS.iso"
echo
echo "==> Done! Your ISO is at: $HERE/out/c00l_OS.iso"
echo "    Write it to a USB stick (Rufus/balenaEtcher) or boot it directly"
echo "    in VirtualBox / QEMU / VMware. See BUILD_TUTORIAL.md for details."

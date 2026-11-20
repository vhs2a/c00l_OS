#!/bin/bash
# Builds c00l_OS into a bootable Debian Bookworm ISO using live-build.
# Run as root on Debian/Ubuntu with internet access.
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Please run this as root (sudo ./build.sh)" >&2
    exit 1
fi

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

echo "==> Checking/installing live-build dependencies..."
if ! command -v lb >/dev/null 2>&1 \
    || ! command -v debootstrap >/dev/null 2>&1 \
    || ! command -v xorriso >/dev/null 2>&1 \
    || [ ! -s /usr/share/keyrings/debian-archive-keyring.gpg ]; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        live-build \
        live-boot \
        live-config \
        debootstrap \
        xorriso \
        debian-archive-keyring \
        ca-certificates
fi

if [ ! -s /usr/share/keyrings/debian-archive-keyring.gpg ]; then
    echo "Error: Debian archive signing keyring is still missing." >&2
    exit 1
fi

if [ ! -d "$HERE/live-build" ]; then
    echo "Error: expected directory '$HERE/live-build' was not found." >&2
    exit 1
fi

echo "==> Cleaning any previous build state..."
cd "$HERE/live-build"
lb clean --purge || true

echo "==> Configuring Debian Bookworm (amd64) with official Debian mirrors..."
lb config \
    --ignore-system-defaults \
    --architecture amd64 \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --mirror-bootstrap "http://deb.debian.org/debian" \
    --mirror-chroot "http://deb.debian.org/debian" \
    --mirror-binary "http://deb.debian.org/debian" \
    --mirror-chroot-security "http://security.debian.org/debian-security" \
    --mirror-binary-security "http://security.debian.org/debian-security" \
    --keyring-packages "debian-archive-keyring" \
    --binary-images iso-hybrid \
    --iso-application "c00l_OS" \
    --iso-volume "c00l_OS"

echo "==> Building the ISO (internet access required)..."
lb build

ISO="$(find . -maxdepth 1 -type f -name 'live-image-*.hybrid.iso' -printf '%T@ %p\n' | sort -nr | head -n1 | cut -d' ' -f2-)"
if [ -z "$ISO" ] || [ ! -s "$ISO" ]; then
    echo "Build finished but no non-empty hybrid ISO was found." >&2
    echo "Check the live-build output above for the first error." >&2
    exit 1
fi

mkdir -p "$HERE/out"
mv "$ISO" "$HERE/out/c00l_OS.iso"

echo
echo "==> Done! Your ISO is at: $HERE/out/c00l_OS.iso"
echo "    Test it in VirtualBox/QEMU/VMware or write it to USB with Rufus."

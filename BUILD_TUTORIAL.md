# Building the c00l_OS .iso

Two paths. Path A needs nothing but a free GitHub account and a web
browser. Path B needs a Debian/Ubuntu machine or VM of your own.

---

## Path A — build it in the cloud with GitHub Actions (recommended)

You don't need Linux, a terminal, or anything installed on your own
computer for this. GitHub's own servers do the build.

1. **Create a free GitHub account** at github.com if you don't have one.
2. **Create a new repository** (github.com -> the "+" in the top right ->
   "New repository"). Any name, e.g. `c00l-os`. Public or private both
   work.
3. **Upload this whole project folder into it.** The easiest way with no
   command line: open your new repo's page -> "Add file" -> "Upload
   files" -> drag the entire `c00l_os_build` folder's contents in (make
   sure the `live-build/` folder and `.github/` folder both end up at the
   top level of the repo) -> commit.
   - If you do have `git` available: `cd c00l_os_build && git init && git add -A && git commit -m "c00l_OS" && git branch -M main && git remote add origin <your repo URL> && git push -u origin main`
4. **Run the build**: go to the repo's **Actions** tab. You should see a
   workflow called **"Build c00l_OS ISO"**. Click it, then click **"Run
   workflow"** (top right) -> **"Run workflow"** again to confirm.
   - If GitHub asks you to "enable workflows" for the repo first, click
     that — it's a one-time confirmation for new repos.
5. **Wait.** It takes roughly 20–40 minutes. You can watch it build live by
   clicking into the running job.
6. **Download the .iso**: once it finishes (green checkmark), click into
   that workflow run, scroll to **"Artifacts"** at the bottom, and
   download **`c00l_OS-iso`**. Unzip it — that's your `c00l_OS.iso`.

If it fails, download the **`build-log`** artifact from the same page and
look at the last ~50 lines — it's almost always one missing/renamed Debian
package (package names occasionally change between Debian releases).

---

## Path B — build it yourself on Debian/Ubuntu

Use a real Debian or Ubuntu machine, or a VM (VirtualBox/VMware/a cloud VM
all work). It needs internet access and about 10GB free disk space.

```bash
cd c00l_os_build
sudo ./build.sh
```

That installs `live-build`, configures the image, and runs the build.
When it finishes, your ISO is at `c00l_os_build/out/c00l_OS.iso`.

If you'd rather run the steps yourself:

```bash
sudo apt-get update
sudo apt-get install -y live-build live-boot live-config
cd c00l_os_build/live-build
sudo lb clean --purge
sudo lb config \
    --architecture amd64 \
    --distribution bookworm \
    --archive-areas "main contrib non-free non-free-firmware" \
    --binary-images iso-hybrid \
    --iso-application "c00l_OS" \
    --iso-volume "c00l_OS"
sudo lb build
```

The finished file is `live-image-amd64.hybrid.iso` in that same directory.

---

## Trying it out

**In a VM (fastest, safest — no USB stick needed):**
- VirtualBox: New VM -> type "Linux", version "Debian (64-bit)" -> when
  asked for a disk, point it at `c00l_OS.iso` as the boot/optical media,
  or just boot it directly with no hard disk attached at all (it's a live
  image, it doesn't need one to boot and show the desktop).
- QEMU: `qemu-system-x86_64 -m 4096 -cdrom c00l_OS.iso -boot d`

**On real hardware (USB stick):**
- Windows: [Rufus](https://rufus.ie) -> select the ISO -> select your USB
  drive -> Start. This **erases the USB drive**.
- Mac/Linux: [balenaEtcher](https://etcher.balena.io) -> same idea.
- Boot from that USB (usually F12 / F2 / Esc at startup for the boot menu,
  varies by PC).

You should land on the c00l_OS setup wizard: pick a username, a password,
an accent color, and whether sound effects are on. "Finish" drops you
straight into the desktop — the bottom bar is your taskbar; click
**c00l_OS** at the left to open Notepad, Minesweeper, the Terminal or the
browser.

---

## Making your account (and files) survive a reboot

A plain live USB/ISO boots into RAM and discards changes on reboot — by
design, so it's safe to try on any machine. If you want the account you
create and anything you save to actually persist across reboots, the
standard live-build way is a **persistence partition**:

1. After writing the ISO to a USB stick, create a second partition on the
   same stick (any tool that can resize partitions, e.g. GParted), formatted
   ext4, labelled `persistence`.
2. Put one file at its root, `persistence.conf`, containing just:
   ```
   / union
   ```
3. Boot with the `persistence` boot parameter (edit the boot entry at the
   boot menu, or add `persistence` to the kernel command line).

From then on, `/etc/c00l-os/config.json`, the account you created, and
anything you save under your home directory will survive reboots. This is
optional — everything in this project works fine without it, it just means
re-running the wizard each boot, like most live USB distros.

---

## Troubleshooting

- **Build fails with a missing/unknown package**: Debian occasionally
  renames packages between releases (e.g. `gir1.2-webkit2-4.1` vs
  `gir1.2-webkit2-4.0`). Open
  `live-build/config/package-lists/c00l-os.list.chroot` and swap in
  whatever the current Debian bookworm name is (`apt-cache search webkit2gtk`
  on a Debian box, or search packages.debian.org).
- **Boots to a black screen / no desktop**: usually means `lightdm` or
  `openbox` didn't start. Switch to a text console (Ctrl+Alt+F2) and log
  in as `c00l` (no password) to look at `/var/log/lightdm/` for the
  actual error.
- **No sound**: check `aplay -l` in the terminal lists an audio device —
  in a VM, make sure the VM's audio is enabled (VirtualBox: Settings ->
  Audio -> enable, controller "ICH AC97" tends to be the most reliable).
- **Wi-Fi**: there's no GUI picker; in `c00l_Term` run
  `nmcli device wifi connect "YOUR_SSID" password "YOUR_PASSWORD"`.

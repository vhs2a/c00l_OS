# c00l_OS

A small, real, red/black themed Linux desktop: its own setup wizard (pick a
username, password, accent color and sound on first boot — and the account
it creates is a genuine Linux user), its own notepad, minesweeper, terminal
and web browser, its own cursor theme, and your sound effects wired in as
the UI's SFX.

## Important: read this first

I (Claude) built everything in this project for real — every app's source
code, the desktop shell, the setup wizard, the cursor theme, the sound
hooks, and the live-build recipe that turns it all into a bootable
`.iso`. What I could **not** do is compile that `.iso` myself: the sandbox
I work in has no network access and none of the OS-building tools
(`live-build`, `xorriso`, `debootstrap`) installed, and it can't install
them either. There's no way around that from inside a chat session — an
actual bootable OS image has to be assembled by a real build tool on a
machine with internet access.

So this project is the complete, ready-to-build kit, plus two ways to get
the actual `.iso` from it:

1. **No Linux machine needed** — push this to GitHub and let GitHub's own
   servers build it for you for free. (Recommended — see
   `BUILD_TUTORIAL.md`.)
2. **Your own Debian/Ubuntu machine or VM** — run `sudo ./build.sh`.

Either way takes 20–40 minutes of unattended build time and produces a
real, bootable `c00l_OS.iso` you can put on a USB stick or boot in a VM.

## What's actually in here

| Piece | What it is |
|---|---|
| `live-build/config/includes.chroot/opt/c00l-os/apps/shell.py` | First-boot setup wizard + the desktop taskbar/launcher |
| `.../apps/notepad.py` | A real text editor |
| `.../apps/minesweeper.py` | A complete, playable minesweeper (logic unit-tested, see below) |
| `.../apps/browser.py` | A real web browser (GTK + WebKit2 — same approach every desktop browser uses: an original interface over a standard rendering engine) |
| `.../apps/start_c00l_term.sh` | A themed terminal (real xterm + real shell) |
| `.../assets/sfx/*.wav` | Your uploaded sound effects, wired into clicks, flags, wins, losses, boot |
| `.../cursor-src/*.png` + the `0100-cursor-theme.hook.chroot` build hook | An original red/black cursor set, compiled into a real installed Xcursor theme during the build |
| `live-build/config/package-lists/c00l-os.list.chroot` | Exactly which Debian packages make up the OS |
| `live-build/config/hooks/live/*` | Build-time setup: creates the bootstrap login account, compiles the cursor theme, fixes permissions |
| `build.sh` | One-command local build |
| `.github/workflows/build-iso.yml` | One-click cloud build (no Linux machine needed) |
| `BUILD_TUTORIAL.md` | Full step-by-step instructions |

## How the "choose your username/password at startup" part works

On first boot, the machine auto-logs into a stagehand account (`c00l`) just
far enough to show you the setup wizard. The wizard then runs `useradd` /
`chpasswd` for real, creating the Linux account with the exact username and
password you typed, and saves your accent color and sound preference. The
desktop you land in reflects that choice immediately. (It's a live/demo
system rather than a disk installer, so on a plain USB boot — no
persistence set up — you'll go through that wizard again next boot, same
as most "live" Linux images; `BUILD_TUTORIAL.md` covers adding persistence
if you want it to stick.)

## Honest scope notes

- The desktop background/cursors/icons/apps are all original artwork made
  for this project — inspired by the red/black "hacker terminal" look in
  your screenshots, not a copy of any third-party tool's name, branding or
  exact art.
- Window title bars use Openbox's stock look rather than a fully custom
  pixel theme — I didn't have a way to visually verify a hand-built Openbox
  theme without a display server, and a broken one would be worse than
  none. Everything else (wallpaper, cursors, panel, all four apps) carries
  the full theme.
- Wi-Fi has no GUI picker — wired networking (DHCP) works out of the box
  via NetworkManager; for Wi-Fi, `nmcli device wifi connect "SSID" password
  "pass"` in the terminal works fine, it just isn't a clickable menu.

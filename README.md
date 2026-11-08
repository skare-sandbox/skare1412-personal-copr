# skare1412-personal-copr

Spec sheets and helper scripts for my personal COPR, designed for
low-maintenance packaging: prefer sources and release artifacts
officially supported by upstream developers.

## Packages

| Package | Upstream | Source | Update procedure |
| ------- | -------- | ------ | ---------------- |
| afmf-linux | [serialexperimentslainnnn/afmf-linux](https://github.com/serialexperimentslainnnn/afmf-linux) | repack of official upstream rpm | bump version, refresh sha256 comment |
| discord-flatpak-rpc-bridge | [Arcitec/discord-flatpak-rpc-bridge](https://github.com/Arcitec/discord-flatpak-rpc-bridge) | git snapshot tarball, built from source | bump snapshot |
| euro-office | [Euro-Office/DesktopEditors](https://github.com/Euro-Office/DesktopEditors) | repack of official upstream rpm | bump version, refresh sha256 comment |
| heroic | [HeroicGamesLauncher](https://github.com/Heroic-Games-Launcher/HeroicGamesLauncher) | repack of official upstream rpm | bump version, refresh sha256 comment |
| msttcore-fonts-installer | [isboston/msttcore-fonts](https://github.com/isboston/msttcore-fonts) | repack of official upstream noarch rpm | bump version |
| nextcloud-office | [nextcloud-releases/Office-DesktopEditors](https://github.com/nextcloud-releases/Office-DesktopEditors) | repack of official upstream rpm | bump version |
| autohdr-vk | private | local tarball via `make-local-tarball.sh`, SRPM uploaded with copr-cli | re-run script, bump version |
| pyrofling | [Themaister/pyrofling](https://github.com/Themaister/pyrofling) | local tarball via `make-pyrofling-tarball.sh` (snapshot, no upstream tags) | re-run script with new date, update Version |
| volt-gui | [pythonlover02/volt-gui](https://github.com/pythonlover02/volt-gui) | repack of official release tarball (prebuilt, container-built) | bump version, refresh sha256 comment |
| vksumi | [reakjra/vkSumi](https://github.com/reakjra/vkSumi) | upstream git tag tarball, spec based on upstream's own `packaging/vksumi.spec` | bump version, refresh sha256 comment |
| scx-scheds-git | [sched-ext/scx](https://github.com/sched-ext/scx) | git snapshot of `main` (commit tarball), cargo workspace build; based on the CachyOS addons COPR spec, fixed for scx 1.1.4+ (needs clang >= 22) | bump `commit`/`commitdate` in the spec |
| scx-tools-git | [sched-ext/scx-loader](https://github.com/sched-ext/scx-loader) | git snapshot of `main` (commit tarball), cargo build + `xtask install`; based on the CachyOS addons COPR spec | bump `commit`/`commitdate` in the spec |

## Notes

- Packages whose source cannot be fetched by copr (private repos,
  git submodules, local checkouts) are built as SRPMs locally and
  uploaded with `copr-cli build <project> <srpm>`.
- Most repack specs carry a `sha256(Source0) = ...` comment near
  Source0; refresh it with `sha256sum` whenever Source0 changes.
- Vulkan layer packages (pyrofling, volt-gui, vksumi, autohdr-vk)
  install implicit-layer manifests into
  `%{_datadir}/vulkan/implicit_layer.d`; the layers stay dormant
  unless their enable environment variable is set
  (`PYROFLING=1`, `VOLT_ENABLE` via the volt launcher,
  `ENABLE_VKSUMI=1`, `AFMF_ENABLE=1`).
- The scx packages (`scx-scheds-git`, `scx-tools-git`) need network
  during `%build` (`cargo fetch --locked`), so the pipeline submits
  them with `--enable-net` via `scripts/<name>.copr-args`. They are
  pinned to the `fedora-45-x86_64` chroot via `scripts/<name>.chroots`
  because scx >= 1.1.4 refuses to build with clang < 22 and only
  Fedora 45+ ships a new enough clang — bump the `.chroots` files when
  upgrading Fedora, and make sure the `fedora-45-x86_64` chroot is
  enabled in the COPR project settings. The two packages satisfy each
  other through the virtual `scx-scheds` / `scx-tools` names.
  For one-off manual submissions, replicate the pipeline flags —
  without `--enable-net` the build chroot has no network and
  `cargo fetch --locked` in `%build` fails:
  `copr-cli build --nowait --enable-net --chroot fedora-45-x86_64 skare1412/personal <srpm>`
- Fedora 45 notes: the existing specs need no changes for F45 — they
  use `%{?dist}` and none of the macros removed/changed there
  (`%patchN`, `%gpgverify`, python macros; the `%cmake` cleanup only
  drops macro-injected variables, not explicit `-D`/`-G` flags).
  F45's RPM 6.1 builds v6-format packages and enforces signature
  checking on install; that only matters for local unsigned test
  installs (`rpm -i --nosignature ...`) — COPR signs everything, so
  `dnf` is unaffected. F45 ships Python 3.15, irrelevant here as no
  spec uses the python packaging macros.

## copr-packaging/scripts

- `make-local-tarball.sh <repo-path> <name> <version>` — turn a
  local/private git checkout into a Source0 tarball (git archive,
  no submodules).
- `make-pyrofling-tarball.sh [YYYYMMDD]` — vendor a pyrofling
  snapshot with the Granite submodule tree (FFmpeg submodule
  skipped: on Linux Granite links system ffmpeg-free).
- `build-and-submit.sh [chroot]...` — the full pipeline:
  `spectool -g -R` on every spec, `rpmbuild -bs` per spec, then
  `copr-cli build --nowait` per SRPM. One failing spec doesn't
  abort the rest. Optional per-package chroots: put them (one per
  line) in `scripts/<name>.chroots`; an empty file skips the
  package. Without overrides, chroots come from the arguments or
  the copr project defaults. Extra `copr-cli build` arguments per
  package (one per line) can be put in `scripts/<name>.copr-args`
  (used by the scx packages for `--enable-net`).
  `COPR_PROJECT` and `SPECS_DIR`
  environment variables override the defaults
  (`skare1412/personal`, `rpmbuild/SPECS`).

  Run it from a cron job / systemd timer for fully unattended
  updates, e.g. every Sunday night:

  ```
  30 2 * * 0  cd /path/to/skare1412-personal-copr && git pull --ff-only && copr-packaging/scripts/build-and-submit.sh
  ```

  Packages whose Source0 is a locally-made tarball (pyrofling,
  autohdr-vk) are only rebuilt when you re-run their tarball script
  and bump the spec Version — the pipeline itself is idempotent
  and resubmitting an identical SRPM just produces a new build of
  the same sources.

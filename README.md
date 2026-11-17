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
| bazaar | [World/bazaar](https://gitlab.gnome.org/World/bazaar) | upstream GitLab release tag tarball, built from source with meson | bump version, refresh sha256 comment |
| firebotv5 | [crowbartools/Firebot](https://github.com/crowbartools/Firebot) | repack of official upstream rpm | bump version, refresh sha256 comment |
| libdex | [GNOME/libdex](https://gitlab.gnome.org/GNOME/libdex) | official GNOME release tarball, built from source with meson | bump version, refresh sha256 comment (companion for bazaar; F44 only ships 1.1~alpha) |
| autohdr-vk | private | local tarball via `make-local-tarball.sh`, SRPM uploaded with copr-cli | re-run script, bump version |
| pyrofling | [Themaister/pyrofling](https://github.com/Themaister/pyrofling) | local tarball via `make-pyrofling-tarball.sh` (snapshot, no upstream tags) | re-run script with new date, update Version |
| volt-gui | [pythonlover02/volt-gui](https://github.com/pythonlover02/volt-gui) | repack of official release tarball (prebuilt, container-built) | bump version, refresh sha256 comment |
| vksumi | [reakjra/vkSumi](https://github.com/reakjra/vkSumi) | upstream git tag tarball, spec based on upstream's own `packaging/vksumi.spec` | bump version, refresh sha256 comment |

## Notes

- bazaar needs `libdex >= 1.2.0`, which Fedora 44 does not ship; the
  libdex companion package in this COPR fills that gap. The COPR
  buildroot resolves it from `copr_base` — but only once a libdex
  build has finished. On a fresh run, build libdex first and wait for
  it to appear in the repo before submitting bazaar
  (`build-and-submit.sh` submits bazaar after libdex via the
  `after:libdex` line in `scripts/bazaar.chroots`, but `--nowait`
  still means a concurrent first-time build can race; for the first
  build submit libdex on its own).
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
  package. Submission order: an `after:<other-package>` line in a
  `.chroots` file defers that package until `<other-package>` has
  been submitted in the same run (used for bazaar after libdex).
  Without overrides, chroots come from the arguments or
  the copr project defaults. `COPR_PROJECT` and `SPECS_DIR`
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

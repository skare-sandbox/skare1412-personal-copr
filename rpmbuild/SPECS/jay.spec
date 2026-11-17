# jay — tiling Wayland compositor written in Rust (upstream:
# https://github.com/mahkoh/jay, also published on crates.io as
# jay-compositor). Built from the official upstream git tag tarball
# with cargo.
# The build needs network access (cargo fetch --locked), so the
# pipeline submits this package with --enable-net via
# scripts/jay.copr-args, and pins it to the fedora-45-x86_64 chroot
# via scripts/jay.chroots (edition 2024; upstream wants the latest
# stable rustc).
# Update procedure: bump Version, refresh the sha256 comment, rebuild.

Name:           jay
Version:        1.15.1
Release:        1%{?dist}
Summary:        Tiling Wayland compositor written in Rust

License:        GPL-3.0-only
URL:            https://github.com/mahkoh/jay
Source0:        https://github.com/mahkoh/jay/archive/refs/tags/v%{version}/jay-%{version}.tar.gz
# sha256(Source0) = 630148643dbdb82fd082ff8e493f38d81a887d454b8f1d329c6d1b4b2f4ec713

BuildRequires:  gcc
BuildRequires:  rust >= 1.85
BuildRequires:  cargo
BuildRequires:  pkgconf-pkg-config
# Linked at build time via #[link(...)] in src/: libinput, libgbm,
# libudev, pangocairo/pango/cairo/gobject-2.0, fontconfig.
BuildRequires:  libinput-devel
BuildRequires:  mesa-libgbm-devel
BuildRequires:  systemd-devel
BuildRequires:  pango-devel
BuildRequires:  fontconfig-devel

# Loaded via dlopen at runtime (declared as dlopen notes in the ELF
# metadata); at least one renderer is required for anything to show up.
Requires:       vulkan-loader%{?_isa}
Requires:       mesa-libEGL%{?_isa}
Requires:       mesa-libGLES%{?_isa}
Requires:       sqlite-libs%{?_isa}
Requires:       xkeyboard-config
Recommends:     xdg-desktop-portal%{?_isa}
Recommends:     xorg-x11-server-Xwayland%{?_isa}

%description
Jay is a highly configurable tiling Wayland compositor with an
i3-like layout, Vulkan and OpenGL rendering, multi-GPU support and
screen sharing. It is configured via a TOML file (or a compiled Rust
config.so).

This package installs the `jay` binary, a `jay` wayland session and an
xdg-desktop-portal backend for screen casting and remote desktop. A
GPU driver (e.g. mesa-vulkan-drivers) is needed for rendering. Granting
CAP_SYS_NICE to the binary (`setcap cap_sys_nice=ep %{_bindir}/jay`)
is optional and improves responsiveness under load.

This package builds the official upstream release tag with cargo.

%prep
%autosetup -n jay-%{version}

%build
export CARGO_HOME=%{_builddir}/.cargo
cargo fetch --locked
cargo build --release --frozen

%install
install -Dm755 target/release/jay %{buildroot}%{_bindir}/jay
install -Dm644 etc/jay.desktop %{buildroot}%{_datadir}/wayland-sessions/jay.desktop
install -Dm644 etc/jay.portal %{buildroot}%{_datadir}/xdg-desktop-portal/portals/jay.portal
install -Dm644 etc/jay-portals.conf %{buildroot}%{_datadir}/xdg-desktop-portal/jay-portals.conf

mkdir -p %{buildroot}%{_datadir}/bash-completion/completions \
         %{buildroot}%{_datadir}/zsh/site-functions \
         %{buildroot}%{_datadir}/fish/vendor_completions.d
target/release/jay generate-completion bash > %{buildroot}%{_datadir}/bash-completion/completions/jay
target/release/jay generate-completion zsh  > %{buildroot}%{_datadir}/zsh/site-functions/_jay
target/release/jay generate-completion fish > %{buildroot}%{_datadir}/fish/vendor_completions.d/jay.fish

%files
%license LICENSE
%doc README.md
%{_bindir}/jay
%{_datadir}/wayland-sessions/jay.desktop
%{_datadir}/xdg-desktop-portal/portals/jay.portal
%{_datadir}/xdg-desktop-portal/jay-portals.conf
%{_datadir}/bash-completion/completions/jay
%{_datadir}/zsh/site-functions/_jay
%{_datadir}/fish/vendor_completions.d/jay.fish

%changelog
* Tue Nov 17 2026 Noel Knubel - 1.15.1-1
- Initial package for COPR, built from the upstream v1.15.1 release tag.

# scx-tools-git — scx_loader/scxctl built from sched-ext/scx-loader main.
# Based on sources/scx-tools-git from CachyOS/copr-linux-cachyos (the
# cachyos addons COPR builds this successfully on fedora-45); adjusted so
# the -git pair is self-contained: Requires the scx-scheds virtual, which
# scx-scheds-git provides. License fixed to SPDX, %license/%changelog added.
# Update procedure: bump commit/commitdate to a new main HEAD, rebuild.
# The build needs network access (cargo fetch --locked); the pipeline
# submits this package with --enable-net via scripts/scx-tools-git.copr-args.

%global commitdate 20261019
%global commit 2c9c3ee5449640956cbda9219079fb854ee3573a
%global revision 1
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           scx-tools-git
Version:        1.1.3.%{commitdate}.%{revision}.git.%{shortcommit}
Release:        1%{?dist}
Summary:        sched_ext loader and control tools built from upstream main

License:        GPL-2.0-only
URL:            https://github.com/sched-ext/scx-loader
Source0:        %{URL}/archive/%{commit}/scx-loader-%{commit}.tar.gz

BuildRequires:  gcc
BuildRequires:  git
BuildRequires:  python3
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang >= 17
BuildRequires:  llvm >= 17
BuildRequires:  lld >= 17
BuildRequires:  systemd-rpm-macros
BuildRequires:  bpftool
BuildRequires:  libseccomp-devel

Requires:       scx-scheds
Conflicts:      scx-tools
Provides:       scx-tools = %{version}
Provides:       scxctl = %{version}

%description
scx_loader is a D-Bus daemon for managing sched_ext schedulers
(start/stop/switch at runtime, via scxctl or a desktop frontend).
This package builds scx_loader and the other tools from the
sched-ext/scx-loader main branch.

%prep
%autosetup -p1 -n scx-loader-%{commit}

%build
export CARGO_HOME=%{_builddir}/.cargo
cargo fetch --locked
cargo build --release --frozen --workspace

%install
# Install all built executables (skip shared objects, dep files, xtask)
find target/release \
    -maxdepth 1 -type f -executable ! -name '*.so' ! -name 'xtask' \
    -exec install -Dm755 -t %{buildroot}%{_bindir} {} +

# Runtime assets (systemd unit, D-Bus service, polkit policy, config)
./target/release/xtask install --destdir %{buildroot}

%files
%license LICENSE
%{_bindir}/*
%{_unitdir}/scx_loader.service
%{_datadir}/dbus-1/system-services/org.scx.Loader.service
%{_datadir}/dbus-1/system.d/org.scx.Loader.conf
%{_datadir}/dbus-1/interfaces/org.scx.Loader.xml
%{_datadir}/polkit-1/actions/org.scx.Loader.policy
%{_datadir}/scx_loader/config.toml

%changelog
* Sun Nov 08 2026 Noel Knubel - 1.1.3.20261019.1.git.2c9c3ee-1
- Initial package, based on the CachyOS addons scx-tools-git spec.

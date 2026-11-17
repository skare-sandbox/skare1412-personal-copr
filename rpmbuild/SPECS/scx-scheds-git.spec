# scx-scheds-git — sched_ext schedulers built from sched-ext/scx main.
# Based on sources/scx-scheds-git from CachyOS/copr-linux-cachyos (the
# cachyos addons COPR), which currently fails to build: since scx 1.1.4
# the cid/arena-form schedulers refuse to compile with clang < 22
# (check_cid_clang in rust/scx_cargo), so clang/llvm/lld are required
# >= 22 here; python->python3, zlib-devel and pkgconf-pkg-config are
# added explicitly. License fixed to SPDX, %license/%changelog added.
# Update procedure: bump commit/commitdate to a new main HEAD, rebuild.
# The build needs network access (cargo fetch --locked); the pipeline
# submits this package with --enable-net via scripts/scx-scheds-git.copr-args.

%global commitdate 20261108
%global commit c0347f11c377181c31eb3bfbf5810719438a2541
%global revision 1
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           scx-scheds-git
Version:        1.1.4.%{commitdate}.%{revision}.git.%{shortcommit}
Release:        1%{?dist}
Summary:        sched_ext schedulers built from upstream main

License:        GPL-2.0-only
URL:            https://github.com/sched-ext/scx
Source0:        %{URL}/archive/%{commit}/scx-%{commit}.tar.gz

BuildRequires:  gcc
BuildRequires:  git
BuildRequires:  python3
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang >= 22
BuildRequires:  llvm >= 22
BuildRequires:  lld >= 22
BuildRequires:  bpftool
BuildRequires:  elfutils-libelf-devel
BuildRequires:  zlib-devel
BuildRequires:  jq-devel
BuildRequires:  protobuf-compiler
BuildRequires:  libseccomp-devel
BuildRequires:  openssl-devel
BuildRequires:  pkgconf-pkg-config

Requires:       elfutils-libelf
Requires:       libseccomp
Requires:       protobuf
Requires:       zlib
Requires:       jq
Requires:       scx-tools
Conflicts:      scx-scheds
Provides:       scx-scheds = %{version}

%description
sched_ext is a Linux kernel feature (6.12+) that lets CPU schedulers be
implemented in BPF and loaded at runtime. This package builds the
scheduler binaries (scx_bpfland, scx_lavd, scx_rusty, scx_layered, ...)
from the sched-ext/scx main branch, including the reworked scx_bpfland
(EEVDF-like with per-CPU EDQs).

Run a scheduler directly (e.g. `sudo scx_bpfland`) or manage them with
scx-tools-git (scx_loader / scxctl). Requires a kernel built with
CONFIG_SCHED_EXT.

%prep
%autosetup -p1 -n scx-%{commit}

%build
export CARGO_HOME=%{_builddir}/.cargo
cargo fetch --locked
cargo build \
     --release \
     --frozen \
     --workspace \
     --exclude scx_rlfifo \
     --exclude scx_mavd \
     --exclude scx_mitosis \
     --exclude scx_nitosis \
     --exclude xtask \
     --exclude scx_characterize \
     --exclude vmlinux_docify \
     --exclude scx_arena_selftests \
     --exclude scx_arena_libarena_selftests

%install
# Install all built executables (skip shared objects and dep files)
find target/release \
    -maxdepth 1 -type f -executable ! -name '*.so' \
    -exec install -Dm755 -t %{buildroot}%{_bindir} {} +

%files
%license LICENSE
%{_bindir}/*

%changelog
* Sun Nov 08 2026 Noel Knubel - 1.1.4.20261108.1.git.c0347f1-1
- Initial package, based on the CachyOS addons scx-scheds-git spec with
  clang/llvm/lld >= 22 and updated build requirements for scx 1.1.4+.

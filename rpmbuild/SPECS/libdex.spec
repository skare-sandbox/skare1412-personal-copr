# libdex — GNOME "Deferred Execution" futures library
# (https://gitlab.gnome.org/GNOME/libdex). Companion package: bazaar
# requires libdex >= 1.2.0, which Fedora 44 does not ship (it has
# 1.1~alpha). Built from the official GNOME release tarball.
# Update procedure: bump Version, update the sha256 comment, rebuild.

Name:           libdex
Version:        1.2.0
Release:        1%{?dist}
Summary:        Future-based programming library for GLib applications

License:        LGPL-2.1-or-later
URL:            https://gitlab.gnome.org/GNOME/libdex
Source0:        https://download.gnome.org/sources/libdex/1.2/libdex-%{version}.tar.xz
# sha256(Source0) = 69f5b244c21f6402831c3ab8af85a01772f72fb118677388436f12f32bfb06d9

BuildRequires:  meson >= 1.0.0
BuildRequires:  gcc
BuildRequires:  pkgconfig(gio-unix-2.0) >= 2.87
BuildRequires:  pkgconfig(liburing) >= 0.7
BuildRequires:  gobject-introspection-devel
BuildRequires:  vala
# -Dtests=false -Dexamples=false -Ddocs=false keep the build lean; the
# gdbus codegen extension is disabled (nothing in this COPR uses it),
# and so is the PyGObject override (-Dpygobject=false) — it would
# otherwise install gi/overrides/Dex.py, which we don't package.

%description
Dex is a library supporting "Deferred Execution" with the explicit
goal of integrating with GNOME and GTK-based applications. It provides
futures, promises, channels, queues, fibers, schedulers and utilities
for asynchronous programming on top of GLib.

This COPR package provides libdex 1.2.0 for Fedora releases that only
carry the 1.1 development snapshots; bazaar depends on it.

%prep
%autosetup -n libdex-%{version} -p 1

%build
# Fedora 44's default CFLAGS add -mtls-dialect=gnu2, which is known
# to break ucontext-based fiber libraries (RH bug 2263739): fibers
# crash marshaling GClosure calls off their swapped stacks. The GNOME
# runtime builds libdex without it (Flatpak builds work). Fall back to
# the traditional TLS dialect so native builds match.
export CFLAGS="${CFLAGS:-%{build_cflags}} -mtls-dialect=gnu"
%meson -Dtests=false -Dexamples=false -Ddocs=false -Dgdbus=disabled -Dpygobject=false

%meson_build

%install
%meson_install

%files
%license COPYING
%{_libdir}/libdex-1.so.1*
%{_libdir}/girepository-1.0/Dex-1.typelib
%{_datadir}/vala/vapi/libdex-1.deps
%{_datadir}/vala/vapi/libdex-1.vapi

%package devel
Summary:        Development files for libdex
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development files for the libdex "Deferred Execution" library.

%files devel
%{_includedir}/libdex-1/
%{_libdir}/libdex-1.so
%{_libdir}/pkgconfig/libdex-1.pc
%{_datadir}/gir-1.0/Dex-1.gir

%changelog
* Sun Nov 01 2026 Noel Knubel - 1.2.0-3
- Build with -mtls-dialect=gnu: F44's default gnu2 TLS dialect breaks
  libdex's ucontext fibers (crash in ffi_call on fiber stacks, RH bug
  2263739); the GNOME runtime builds libdex without it.

* Sun Nov 01 2026 Noel Knubel - 1.2.0-2
- Disable the PyGObject override (-Dpygobject=false): it installed
  gi/overrides/Dex.py, which was not packaged and failed check-files.

* Sun Nov 01 2026 Noel Knubel - 1.2.0-1
- Initial package for COPR (bazaar needs libdex >= 1.2.0).

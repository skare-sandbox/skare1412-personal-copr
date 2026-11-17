# bazaar — Flathub/Flatpak app store client (GNOME app, upstream:
# https://gitlab.gnome.org/World/bazaar). Built from the official
# GitLab release tag tarball with upstream's meson build.
# Update procedure: bump Version, update the sha256 comment, rebuild.

Name:           bazaar
Version:        0.9.10
Release:        1%{?dist}
Summary:        Flathub/Flatpak application store client

License:        GPL-3.0-only
URL:            https://gitlab.gnome.org/World/bazaar
Source0:        https://gitlab.gnome.org/World/bazaar/-/archive/v%{version}/bazaar-v%{version}.tar.gz
# sha256(Source0) = cc9d62b7fc2b1008f3096da29c6fdeb48126d419fc5d4bed067cf72a107db7ac

BuildRequires:  meson >= 1.0.0
BuildRequires:  gcc
BuildRequires:  vala
BuildRequires:  pkgconfig(gtk4) >= 4.22.1
BuildRequires:  pkgconfig(libadwaita-1) >= 1.8
# libdex >= 1.2.0 is not in F44; provided by the libdex package in
# this COPR (built from the official GNOME release tarball).
BuildRequires:  pkgconfig(libdex-1) >= 1.2.0
BuildRequires:  pkgconfig(flatpak) >= 1.9
BuildRequires:  pkgconfig(appstream) >= 1.0
BuildRequires:  pkgconfig(xmlb) >= 0.3.4
BuildRequires:  pkgconfig(yaml-0.1) >= 0.2.5
BuildRequires:  pkgconfig(libsoup-3.0) >= 3.6.0
BuildRequires:  pkgconfig(json-glib-1.0) >= 1.10.0
BuildRequires:  pkgconfig(glycin-2) >= 2.0
BuildRequires:  pkgconfig(glycin-gtk4-2) >= 2.0
BuildRequires:  pkgconfig(webkitgtk-6.0) >= 2.50.2
BuildRequires:  pkgconfig(gmodule-2.0)
BuildRequires:  pkgconfig(libsecret-1) >= 0.20
BuildRequires:  pkgconfig(libproxy-1.0) >= 0.5
BuildRequires:  pkgconfig(malcontent-0) >= 0.12.0
BuildRequires:  pkgconfig(gtksourceview-5) >= 5.17
BuildRequires:  pkgconfig(libsystemd) >= 245
BuildRequires:  pkgconfig(dbus-1) >= 1.12
BuildRequires:  pkgconfig(md4c) >= 0.5.1
BuildRequires:  blueprint-compiler >= 0.20.0
BuildRequires:  libxml2
BuildRequires:  gettext
BuildRequires:  desktop-file-utils
BuildRequires:  python3
# scripts/countries.py (countries.gvariant build step) needs both:
BuildRequires:  python3-babel
BuildRequires:  python3-gobject

# The .vapi files Vala needs ship inside the corresponding -devel
# packages pulled in by the pkgconfig() BuildRequires above.

Requires:       flatpak%{?_isa}
Requires:       glycin-loaders%{?_isa}
Requires:       hicolor-icon-theme

%description
Bazaar is an application store client for Flathub and other Flatpak
remotes, following GNOME HIG. It lists and installs desktop apps,
runtimes, fonts, extension points and system components, keeps them
updated, and integrates with GNOME Shell search.

This package builds the official upstream source release with meson.

%prep
%autosetup -n bazaar-v%{version} -p 1

%build
# Same fiber-safety fix as the libdex package: F44's default
# -mtls-dialect=gnu2 breaks ucontext fibers (RH bug 2263739).
# bazaar spawns dex fibers (cache_check_fiber etc.), so it needs the
# traditional TLS dialect too.
export CFLAGS="${CFLAGS:-%{build_cflags}} -mtls-dialect=gnu"
%meson

%meson_build

%install
%meson_install

# Upstream always builds the bge demo binary and libbge dev files;
# they are not part of the application package.
rm -f %{buildroot}%{_bindir}/bge-demo\
       %{buildroot}%{_includedir}/bge/*.h\
       %{buildroot}%{_libdir}/libbge.so\
       %{buildroot}%{_libdir}/pkgconfig/bge.pc

%find_lang bazaar

%files -f bazaar.lang
%license COPYING
%{_bindir}/bazaar
%{_bindir}/bazaar-daemon
%{_bindir}/bazaar-dl-worker
%{_libdir}/bazaar/libbazaar-login-page.so
%{_libdir}/libbge.so.0*
%{_datadir}/applications/io.github.kolunmi.Bazaar.desktop
%{_datadir}/metainfo/io.github.kolunmi.Bazaar.metainfo.xml
%{_datadir}/glib-2.0/schemas/io.github.kolunmi.Bazaar.gschema.xml
%{_datadir}/gnome-shell/search-providers/io.github.kolunmi.Bazaar.search-provider.ini
%{_datadir}/dbus-1/services/io.github.kolunmi.Bazaar.service
%{_datadir}/dbus-1/services/io.github.kolunmi.Bazaar.SearchProvider.service
%{_datadir}/icons/hicolor/*/apps/io.github.kolunmi.Bazaar*.svg
%{_userunitdir}/io.github.kolunmi.Bazaar.service

# Icon cache, desktop database and glib schemas are refreshed by rpm
# file triggers (hicolor-icon-theme, desktop-file-utils, glib2);
# no scriptlets needed.

%changelog
* Sun Nov 01 2026 Noel Knubel - 0.9.10-5
- Build with -mtls-dialect=gnu like libdex: F44's default gnu2 TLS
  dialect crashes dex fibers (RH bug 2263739).

* Sun Nov 01 2026 Noel Knubel - 0.9.10-4
- Also remove the libbge.so dev symlink in %%install (last
  unpackaged-file failure; the runtime libbge.so.0* stays packaged).

* Sun Nov 01 2026 Noel Knubel - 0.9.10-3
- Add python3-babel and python3-gobject BuildRequires: the upstream
  countries.gvariant build step needs Babel and PyGObject at compile
  time (was: 'Error: babel library not found').

* Sun Nov 01 2026 Noel Knubel - 0.9.10-2
- Note the libdex >= 1.2.0 build requirement (COPR libdex package).

* Sun Nov 01 2026 Noel Knubel - 0.9.10-1
- Initial package for COPR, built from the upstream v0.9.10 release.

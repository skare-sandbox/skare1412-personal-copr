# euro-office — repackaged from the official upstream binary rpm
# (unsigned community build of the same source as nextcloud-office).
# Same caveats as nextcloud-office-nextcloudoffice.spec: check the
# asset filename and release number when bumping the version.
# Profile data: ~/.local/share/euro-office/euro-office and
# ~/.config/euro-office (not migrated from OnlyOffice automatically).

# Upstream binaries are prebuilt/stripped: no debuginfo, and their
# embedded vendor rpaths are fixed up via QA_RPATHS in %%install.
%global debug_package %{nil}

# Same as nextcloud-office: filter bundled Qt6 plus the unbundled
# Oracle/Mimer/Postgres/MySQL/Firebird/ODBC client sonames out of
# auto-generated Requires (the official rpm suppresses soname deps
# entirely and hand-curates its list), and don't shadow Fedora's
# real Qt6 packages with the /opt copies' Provides.
%global __requires_exclude ^lib(Qt6.*|clntsh|mimerapi|pq|fbclient|mysqlclient|odbc)\\.so.*$
%global __provides_exclude ^lib(Qt6.*|clntsh|mimerapi)\\.so.*$

Name:           euro-office
Version:        9.3.8
Release:        0%{?dist}
Summary:        Euro-Office Desktop Editors (community build)

License:        AGPL-3.0-only
URL:            https://github.com/Euro-Office/DesktopEditors
Source0:        https://github.com/Euro-Office/DesktopEditors/releases/download/v%{version}/euro-office-euro-office-%{version}-0.x86_64.rpm
# sha256(Source0) = 1354f91ff0c2b13b414f671d965ddab4e732bbd38860455f85f01e8681463a86

BuildArch:      x86_64
BuildRequires:  cpio

Requires:       fontconfig
Requires:       hicolor-icon-theme
# Explicit deps curated from the OFFICIAL upstream rpm's own Requires
# list (it suppresses all auto soname deps; we keep ours but must
# match its fonts — they matter for document rendering). Everything
# else it lists (gtk3, atk, libX11, libxcb, xcb-util-*, libnotify,
# libstdc++, libxkbcommon-x11) is already covered by our auto deps.
Requires:       boost-filesystem
Requires:       curl
Requires:       dejavu-sans-fonts
Requires:       dejavu-sans-mono-fonts
Requires:       dejavu-serif-fonts
Requires:       liberation-mono-fonts
Requires:       liberation-narrow-fonts
Requires:       liberation-sans-fonts
Requires:       liberation-serif-fonts
Requires:       libXScrnSaver
Requires:       xdg-utils

%description
Euro-Office Desktop Editors: the AGPL European community fork of the
ONLYOFFICE office suite, built from the same source as Nextcloud Office
(unsigned community build). This package repackages the official
upstream rpm so it can be managed with dnf.

%prep
%setup -q -T -c -n euro-office-%{version}
rpm2cpio %{SOURCE0} | cpio -idmu --quiet

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a . %{buildroot}

# Don't let check-rpaths fail on the upstream binaries' vendor rpaths
# (bitmask: standard | invalid | $ORIGIN-position | empty).
export QA_RPATHS=$(( 0x0001 | 0x0002 | 0x0008 | 0x0010 ))

cat > std-dirs <<'EOF'
/bin
/etc
/etc/opt
/opt
/usr
/usr/bin
/usr/lib
/usr/lib64
/usr/libexec
/usr/local
/usr/sbin
/usr/share
/usr/share/applications
/usr/share/appdata
/usr/share/doc
/usr/share/icons
/usr/share/icons/hicolor
/usr/share/licenses
/usr/share/metainfo
/usr/share/mime
/usr/share/mime-info
/usr/share/pixmaps
/var
EOF
# rpm splits %files manifest lines on whitespace, so a filename with a
# space breaks the build. Escape spaces as "?" glob wildcards instead.
find %{buildroot} -mindepth 1 -printf '/%%P\n' \
    | grep -Fvx -f std-dirs \
    | sed 's/ /?/g' > %{name}.files

%files -f %{_builddir}/euro-office-%{version}/%{name}.files
%defattr(-,root,root,-)

%post
/bin/touch --no-create %{_datadir}/icons/hicolor 2>/dev/null || :

%postun
if [ $1 -eq 0 ]; then
    /bin/touch --no-create %{_datadir}/icons/hicolor 2>/dev/null || :
    gtk-update-icon-cache -qtf %{_datadir}/icons/hicolor 2>/dev/null || :
    update-desktop-database -q 2>/dev/null || :
fi

%changelog
* Sun Nov 17 2026 Noel Knubel - 9.3.8-0
- Updated package
* Sun Oct 25 2026 Noel Knubel - 9.3.6-5
- Match the official rpm's curated runtime deps: require the
  dejavu/liberation font packages (needed for document rendering;
  they get autoremoved with the old package otherwise), xdg-utils,
  curl, boost-filesystem and libXScrnSaver; also exclude the
  sqldrivers Postgres/MySQL/Firebird/ODBC client sonames so the
  install no longer drags in libpq, mysql8.0-libs and libfbclient2.

* Sun Oct 25 2026 Noel Knubel - 9.3.6-4
- Fix the dep-filter regex: Qt6 module libs are libQt6<Module>.so
  (libQt6Core.so, libQt6Quick3D.so, ...), so the alternation needs
  "Qt6.*" before ".so" — with plain "Qt6" only the Oracle/Mimer
  entries were filtered and the unbundled libQt6Quick3D still
  blocked the dnf transaction.

* Sun Oct 25 2026 Noel Knubel - 9.3.6-3
- Filter auto-generated Requires/Provides for the bundled Qt6 and
  the unbundled Oracle/Mimer client sonames so dnf can resolve the
  install transaction.

* Sun Oct 25 2026 Noel Knubel - 9.3.6-2
- Escape spaces in upstream filenames ("05_green leaf.pptx" theme
  source) as "?" globs in the generated %files list.

* Sun Oct 25 2026 Noel Knubel - 9.3.6-1
- Skip debuginfo (prebuilt stripped binaries), ignore vendor rpaths.

* Sun Oct 25 2026 Noel Knubel - 9.3.6-0
- Initial repack of the official upstream rpm for COPR.

# Spec file for COPR (Fedora). The upstream repo is private, so copr can
# never fetch it from GitHub (release URLs of private repos require auth):
# Source0 stays a plain filename, fed from local/copr storage.
#   scripts/make-vk-nv-low-latency2-layer-tarball.sh <version>
#     SSH-clones the repo and `git archive`s tag v<version> with the
#     top-level prefix %{name}-%{version}/ (must match the default %prep dir).
#   Submit either as a locally built SRPM (`copr-cli build <project> <srpm>`)
#   or by pushing spec + tarball to the package's copr dist-git repo and
#   listing the tarball in `sources` (copr fetches it from its own storage).
# Local test build: rpmbuild -ba with Source0 present in %_sourcedir.
#
# The layer installs as an opt-in implicit layer: it only activates when
# VK_NV_LOW_LATENCY2_ENABLE=1 is set in the environment.

Name:           vk-nv-low-latency2-layer
Version:        0.1.1
Release:        1%{?dist}
Summary:        VK_NV_low_latency2 (NVIDIA Reflex low latency) as an opt-in implicit Vulkan layer

License:        MIT
URL:            https://github.com/skare-sandbox/VK_NV_low_latency2_layer
Source0:        vk-nv-low-latency2-layer-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  vulkan-headers
Requires:       vulkan-loader

%description
Implements VK_NV_low_latency2 (NVIDIA Reflex low latency mode) as an implicit
Vulkan layer on top of any Vulkan 1.2 driver, ported from the radv driver
implementation. Works with a stock Mesa - no driver rebuild needed.

The layer is opt-in: it only loads when VK_NV_LOW_LATENCY2_ENABLE=1 is set
(or VK_INSTANCE_LAYERS=VK_LAYER_NV_low_latency2). Tunables:
VK_NV_LOW_LATENCY2_FRAME_LIMIT_FPS (frame rate cap), VK_NV_LOW_LATENCY2_HIDE_FOR
(comma-separated executable names to not advertise the extension for),
VK_NV_LOW_LATENCY2_DEBUG (logging).

%prep
%autosetup -q

%build
# %cmake sets the prefix to /usr; pass the Fedora libdir explicitly so the
# generated layer manifest bakes /usr/lib64/... as library_path.
%cmake -DCMAKE_INSTALL_LIBDIR=%{_libdir}
%cmake_build

%install
%cmake_install

%files
%license LICENSE
%{_libdir}/libVkLayer_NV_low_latency2.so
%{_datadir}/vulkan/implicit_layer.d/VkLayer_NV_low_latency2.json

%changelog
* Fri Nov 20 2026 Noel Knubel <skaredogged97@pm.me> - 0.1.1-1
- Update to upstream v0.1.1 (tarball built from tag v0.1.1)
- Fix %prep: drop the -n override; the tarball top dir is %{name}-%{version}

* Thu Nov 19 2026 Vibe <vibe@mistral.ai> - 0.1.0-1
- Initial package: opt-in implicit VK_NV_low_latency2 layer ported from radv

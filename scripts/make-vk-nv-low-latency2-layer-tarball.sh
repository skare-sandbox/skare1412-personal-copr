#!/bin/bash
# Script to create a tarball from the private VK_NV_low_latency2_layer git repo
# Usage: ./make-vk-nv-low-latency2-layer-tarball.sh [version]
#   version: optional version number (defaults to 0.1.1); the tarball is
#   `git archive`d from the release tag v<version> with the top-level
#   prefix vk-nv-low-latency2-layer-<version>/ (must match the spec's
#   default %prep dir %{name}-%{version}).
#   SOURCES_DIR env var overrides the output directory.

set -euo pipefail

VERSION="${1:-0.1.1}"
REPO_URL="ssh://git@github.com/skare-sandbox/VK_NV_low_latency2_layer.git"
TARBALL_NAME="vk-nv-low-latency2-layer-${VERSION}.tar.gz"
SOURCES_DIR="${SOURCES_DIR:-$HOME/rpmbuild/SOURCES}"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Creating tarball ${TARBALL_NAME} from ${REPO_URL}..."

# Clone the release tag
cd "${TMP_DIR}"
git clone --quiet --branch "v${VERSION}" --depth 1 "${REPO_URL}" VK_NV_low_latency2_layer

# Create the tarball with the prefix the spec's %prep expects
cd VK_NV_low_latency2_layer
mkdir -p "${SOURCES_DIR}"
git archive --format=tar.gz --prefix="vk-nv-low-latency2-layer-${VERSION}/" HEAD > "${SOURCES_DIR}/${TARBALL_NAME}"

echo "Tarball created: ${SOURCES_DIR}/${TARBALL_NAME}"
(cd "${SOURCES_DIR}" && sha256sum "${TARBALL_NAME}")

echo "Done!"

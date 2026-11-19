#!/bin/bash
# Script to create a tarball from the private VK_NV_low_latency2_layer git repo
# Usage: ./make-vk-nv-low-latency2-layer-tarball.sh [version]
#   version: optional version number (defaults to 0.1.0)

set -euo pipefail

VERSION="${1:-0.1.0}"
REPO_URL="ssh://git@github.com/skare-sandbox/VK_NV_low_latency2_layer.git"
TARBALL_NAME="vk-nv-low-latency2-layer-${VERSION}.tar.gz"
SOURCES_DIR="/home/skare/Projects/Fedora/copr/rpmbuild/SOURCES"
TMP_DIR=$(mktemp -d)

echo "Creating tarball ${TARBALL_NAME} from ${REPO_URL}..."

# Clone the repository
cd "${TMP_DIR}"
git clone --quiet "${REPO_URL}" VK_NV_low_latency2_layer

# Create the tarball with the correct prefix
cd VK_NV_low_latency2_layer
git archive --format=tar.gz --prefix="vk-nv-low-latency2-layer-${VERSION}/" HEAD > "${SOURCES_DIR}/${TARBALL_NAME}"

echo "Tarball created: ${SOURCES_DIR}/${TARBALL_NAME}"

# Cleanup
cd /
rm -rf "${TMP_DIR}"

echo "Done!"

#!/usr/bin/env bash
# Fetch sources, build SRPMs and submit them to COPR.
# Usage: build-and-submit.sh [chroot]...
#   Chroots default to none (copr project default). Examples:
#     build-and-submit.sh                      # submit all specs, project default chroots
#     build-and-submit.sh fedora-44-x86_64     # submit to specific chroot(s) only
#
# Per-spec overrides: put a one-line file named <name>.chroots in
# scripts/ with the chroots that package should build for. Skip a
# package entirely with an empty .chroots file. Extra copr-cli build
# arguments (one per line) go in <name>.copr-args, e.g. --enable-net
# for packages whose %build fetches from the network (cargo fetch).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPECS_DIR="${SPECS_DIR:-$HERE/../../rpmbuild/SPECS}"
COPR_PROJECT="${COPR_PROJECT:-skare1412/personal}"
CHROOTS=("$@")

shopt -s nullglob
specs=("$SPECS_DIR"/*.spec)
shopt -u nullglob
if [ ${#specs[@]} -eq 0 ]; then
    echo "No spec files in $SPECS_DIR" >&2
    exit 1
fi

echo "== Downloading Source archives =="
spectool -g -R "${specs[@]}"

echo "== Building SRPMs =="
built=()
for spec in "${specs[@]}"; do
    name="$(basename "$spec" .spec)"
    override="$HERE/$name.chroots"
    if [ -e "$override" ] && [ ! -s "$override" ]; then
        echo "-- $name: skipped (empty $name.chroots)"
        continue
    fi
    if rpmbuild -bs "$spec"; then
        built+=("$name")
    else
        echo "-- $name: SRPM build FAILED, continuing with the rest" >&2
    fi
done
if [ ${#built[@]} -eq 0 ]; then
    echo "No SRPMs built successfully." >&2
    exit 1
fi

echo "== Submitting to COPR ($COPR_PROJECT) =="
for name in "${built[@]}"; do
    srpm="$(ls -t "$HOME"/rpmbuild/SRPMS/"$name"-*.src.rpm 2>/dev/null | head -n1)"
    if [ -z "$srpm" ]; then
        echo "-- $name: no SRPM found, skipping submission" >&2
        continue
    fi
    args=(--nowait "$COPR_PROJECT" "$srpm")
    override="$HERE/$name.chroots"
    if [ -s "$override" ]; then
        while IFS= read -r chroot; do
            [ -n "$chroot" ] && args+=(--chroot "$chroot")
        done < "$override"
    elif [ ${#CHROOTS[@]} -gt 0 ]; then
        for chroot in "${CHROOTS[@]}"; do
            args+=(--chroot "$chroot")
        done
    fi
    argsfile="$HERE/$name.copr-args"
    if [ -s "$argsfile" ]; then
        while IFS= read -r arg; do
            [ -n "$arg" ] && args+=("$arg")
        done < "$argsfile"
    fi
    echo "-- $name: copr-cli build ${args[*]}"
    copr-cli build "${args[@]}"
done

echo "== Done =="

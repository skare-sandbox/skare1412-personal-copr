#!/usr/bin/env bash
# Fetch sources, build SRPMs and submit them to COPR.
# Usage: build-and-submit.sh [chroot]...
#   Chroots default to none (copr project default). Examples:
#     build-and-submit.sh                      # submit all specs, project default chroots
#     build-and-submit.sh fedora-44-x86_64     # submit to specific chroot(s) only
#
# Per-spec overrides: put a one-line file named <name>.chroots in
# scripts/ with the chroots that package should build for. Skip a
# package entirely with an empty .chroots file.
#
# Build order: put "after:<other-package>" lines into a <name>.chroots
# file (mixed with chroot lines is fine) to submit that package only
# after <other-package> has been submitted; submission still doesn't
# wait for the build to finish, so use this for packages that need a
# companion package to be *in the repo* (builddep resolves against the
# copr_base repo at build time). For a first-time companion build,
# build the companion separately first (see README).
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

submit_one() {
    local name="$1"
    local srpm
    srpm="$(ls -t "$HOME"/rpmbuild/SRPMS/"$name"-*.src.rpm 2>/dev/null | head -n1)"
    if [ -z "$srpm" ]; then
        echo "-- $name: no SRPM found, skipping submission" >&2
        return 1
    fi
    local args=(--nowait "$COPR_PROJECT" "$srpm")
    local override="$HERE/$name.chroots"
    if [ -s "$override" ]; then
        while IFS= read -r line; do
            [ -n "$line" ] && args+=(--chroot "$line")
        done < <(grep -v '^after:' "$override" 2>/dev/null || true)
    elif [ ${#CHROOTS[@]} -gt 0 ]; then
        for chroot in "${CHROOTS[@]}"; do
            args+=(--chroot "$chroot")
        done
    fi
    echo "-- $name: copr-cli build ${args[*]}"
    copr-cli build "${args[@]}"
}

echo "== Submitting to COPR ($COPR_PROJECT) =="
submitted=()
remaining=("${built[@]}")
progress=1
while [ ${#remaining[@]} -gt 0 ] && [ "$progress" -eq 1 ]; do
    progress=0
    next=()
    for name in "${remaining[@]}"; do
        deps=()
        if [ -s "$HERE/$name.chroots" ]; then
            while IFS= read -r dep; do
                [ -n "$dep" ] && deps+=("$dep")
            done < <(grep '^after:' "$HERE/$name.chroots" 2>/dev/null | sed 's/^after://' || true)
        fi
        ready=1
        for dep in "${deps[@]}"; do
            if [[ ! " ${submitted[*]} " == *" $dep "* ]]; then
                ready=0
                if [[ " ${remaining[*]} " == *" $dep "* ]]; then
                    echo "-- $name: waiting for $dep (after: order)"
                else
                    echo "-- $name: dependency $dep not built this run and not in submission set; submitting anyway" >&2
                fi
            fi
        done
        if [ "$ready" -eq 1 ]; then
            submit_one "$name" || true
            submitted+=("$name")
            progress=1
        else
            next+=("$name")
        fi
    done
    remaining=("${next[@]}")
done
if [ ${#remaining[@]} -gt 0 ]; then
    echo "Circular after: dependencies among: ${remaining[*]}" >&2
    exit 1
fi

echo "== Done =="

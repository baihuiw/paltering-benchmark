#!/usr/bin/env bash
# Restore the raw copies of the large result files from their gzipped versions (after a fresh clone).
set -euo pipefail
cd "$(dirname "$0")/.."

find results pilots/*/results archive/*/results -type f -name '*.gz' | sort | while read -r gz; do
  raw="${gz%.gz}"
  if [ ! -f "$raw" ] || [ "$gz" -nt "$raw" ]; then
    echo "gunzip  $gz"
    gunzip -k -f "$gz"
  fi
done

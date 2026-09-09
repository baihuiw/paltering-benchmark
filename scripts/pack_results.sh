#!/usr/bin/env bash
# Store every result file larger than 5 MB as a gzipped copy so the repository stays small enough for GitHub.
# The raw file stays on disk (the scripts read it) and is git-ignored; the .gz copy is what gets committed.
# Run this after any run or refill that changes a large file, then commit the .gz files.
set -euo pipefail
cd "$(dirname "$0")/.."

files=$(find results pilots/*/results archive/*/results -type f -size +5M ! -name '*.gz' ! -name '*.npz' ! -path '*/old_capture/*' | sort)

for f in $files; do
  if [ ! -f "$f.gz" ] || [ "$f" -nt "$f.gz" ]; then
    echo "gzip  $f"
    gzip -9 -k -f "$f"
  fi
done

# rewrite the ignore block in .gitignore
python3 - "$files" <<'EOF'
import sys, pathlib
files = sys.argv[1].split()
gi = pathlib.Path(".gitignore")
lines = gi.read_text().splitlines()
b = lines.index("# >>> large result files: raw copies are ignored, the .gz copies are tracked (scripts/pack_results.sh)")
e = lines.index("# <<< large result files")
lines[b + 1:e] = files
gi.write_text("\n".join(lines) + "\n")
print(f"{len(files)} raw files listed in .gitignore")
EOF

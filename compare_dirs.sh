#!/usr/bin/env bash
# Compare files with same names in two directory trees and report missing/different files
# Usage: ./compare_dirs.sh <dir1> <dir2>

set -euo pipefail

echo "======================================================================================================================================"
echo "--------------------------------------------------------------------------------------------------------------------------------------"
echo "======================================================================================================================================"

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <dir1> <dir2>"
  exit 1
fi

DIR1=$1
DIR2=$2

if [[ ! -d "$DIR1" || ! -d "$DIR2" ]]; then
  echo "❌ Both arguments must be directories."
  exit 1
fi

echo "🔍 Comparing directories:"
echo "  DIR1 = $DIR1"
echo "  DIR2 = $DIR2"
echo

# Get all relative file paths from both directories
mapfile -t FILES1 < <(cd "$DIR1" && find . -type f | sort)
mapfile -t FILES2 < <(cd "$DIR2" && find . -type f | sort)

# Combine and get unique list of all files seen in either directory
ALL_FILES=$(printf "%s\n%s\n" "${FILES1[@]}" "${FILES2[@]}" | sort -u)

# Compare files
for rel_path in $ALL_FILES; do
  file1="$DIR1/$rel_path"
  file2="$DIR2/$rel_path"

  if [[ ! -f "$file1" && -f "$file2" ]]; then
    echo "🚫 Missing in DIR1: $rel_path"
    continue
  elif [[ -f "$file1" && ! -f "$file2" ]]; then
    echo "🚫 Missing in DIR2: $rel_path"
    continue
  fi

  # Both exist → compare content
  if ! diff -q "$file1" "$file2" >/dev/null; then
    echo "⚠️  Difference found in: $rel_path"
    echo "----------------------------------------"
    diff --color=always -u "$file1" "$file2" || true
    echo
  fi
done

echo "✅ Comparison complete."

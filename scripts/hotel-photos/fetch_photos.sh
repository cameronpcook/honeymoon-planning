#!/usr/bin/env bash
# Fetches each hotel photo URL in manifest.json into a correctly named file.
# Run this from an environment with real internet access (e.g. your Claude Code
# session's GitHub Actions runner) - it will NOT work from a sandbox with
# blocked network egress, which is the whole reason this manifest exists.
#
# Usage: ./fetch_photos.sh [output_dir]

set -euo pipefail
OUT_DIR="${1:-./hotel_photos_downloaded}"
mkdir -p "$OUT_DIR"

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

python3 - "$OUT_DIR" <<'PYEOF'
import json, subprocess, sys, os

out_dir = sys.argv[1]
with open("manifest.json") as f:
    manifest = json.load(f)

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

ok, failed = 0, 0
for entry in manifest:
    if entry["status"] == "FAILED":
        print(f"SKIP  {entry['target_filename']}  (no usable URL - {entry['note']})")
        continue
    url = entry["image_url"]
    dest = os.path.join(out_dir, entry["target_filename"])
    print(f"FETCH {entry['target_filename']}  <-  {url}")
    result = subprocess.run(
        ["curl", "-sL", "-A", ua, "--max-time", "30", "-o", dest, url],
        capture_output=True, text=True
    )
    if result.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 1000:
        ok += 1
    else:
        failed += 1
        print(f"  -> FAILED (curl exit {result.returncode}, check network/URL)")

print(f"\nDone: {ok} downloaded, {failed} failed, out of {len(manifest)} total entries.")
PYEOF

#!/usr/bin/env python3
"""
Downloads every image listed in images/<destination>/manifest.json into that
same folder. Run by the "Fetch destination images" GitHub Action, which has
real internet access; not intended to work from a sandboxed dev session.

Each manifest.json is a flat {"local-filename.jpg": "source-url", ...} map.
Adding a new destination is just adding a new images/<slug>/manifest.json —
this script and the workflow that runs it don't need to change.
"""
import json
import pathlib
import sys
import urllib.request

USER_AGENT = "Mozilla/5.0 (compatible; HoneymoonPlanningSite/1.0; personal-use)"
TIMEOUT_SECONDS = 30


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def main() -> int:
    repo_root = pathlib.Path(__file__).resolve().parent.parent
    manifests = sorted((repo_root / "images").glob("*/manifest.json"))

    if not manifests:
        print("No images/*/manifest.json files found.")
        return 0

    failed = []
    for manifest_path in manifests:
        dest_dir = manifest_path.parent
        entries = json.loads(manifest_path.read_text())
        print(f"== {dest_dir.name} ({len(entries)} images) ==")
        for filename, url in entries.items():
            dest = dest_dir / filename
            print(f"  fetching {filename} ...")
            try:
                dest.write_bytes(fetch(url))
            except Exception as exc:  # noqa: BLE001 - report and keep going
                print(f"  FAILED {filename}: {exc}", file=sys.stderr)
                failed.append(f"{dest_dir.name}/{filename}")

    if failed:
        print("\nFailed downloads: " + ", ".join(failed), file=sys.stderr)
        return 1

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Downloads every image listed in images/<destination>/manifest.json, resizes
and re-compresses it for the web, and writes it into that same folder. Run by
the "Fetch destination images" GitHub Action, which has real internet access
and Pillow installed; not intended to work from a sandboxed dev session.

Each manifest.json is a flat {"local-filename.jpg": "source-url", ...} map.
Adding a new destination is just adding a new images/<slug>/manifest.json —
this script and the workflow that runs it don't need to change.

Every run re-downloads and re-optimizes every listed image (not just new
ones), so bumping MAX_DIMENSION/JPEG_QUALITY here and re-running reprocesses
everything already committed too.
"""
import io
import json
import pathlib
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

# Wikimedia (and most hosts) rate-limit or outright block requests that spoof
# a browser User-Agent - see https://meta.wikimedia.org/wiki/User-Agent_policy.
# Identify ourselves honestly instead, with a URL a human could follow up at.
USER_AGENT = (
    "HoneymoonPlanningSite/1.0 "
    "(+https://github.com/cameronpcook/honeymoon-planning) "
    "Python-urllib/3"
)
TIMEOUT_SECONDS = 30
REQUEST_DELAY_SECONDS = 1.0
RETRY_DELAYS_SECONDS = [5, 15, 30]  # backoff on 429s specifically

# The site never displays a photo wider than its 920px content column (~1600px
# on a 2x/retina screen, including the lightbox). Anything bigger is wasted
# bytes on every page load.
MAX_DIMENSION = 1600
JPEG_QUALITY = 82


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    last_error = None
    for attempt, delay in enumerate([0, *RETRY_DELAYS_SECONDS]):
        if delay:
            print(f"    rate-limited, waiting {delay}s before retry {attempt} ...")
            time.sleep(delay)
        try:
            with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code != 429:
                raise
    raise last_error


def optimize(data: bytes) -> bytes:
    """Re-encode as a resized, optimized, EXIF-stripped progressive JPEG."""
    with Image.open(io.BytesIO(data)) as img:
        img = img.convert("RGB")
        if max(img.size) > MAX_DIMENSION:
            img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
        out = io.BytesIO()
        img.save(out, format="JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        return out.getvalue()


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
                dest.write_bytes(optimize(fetch(url)))
            except Exception as exc:  # noqa: BLE001 - report and keep going
                print(f"  FAILED {filename}: {exc}", file=sys.stderr)
                failed.append(f"{dest_dir.name}/{filename}")
            time.sleep(REQUEST_DELAY_SECONDS)

    if failed:
        print("\nFailed downloads: " + ", ".join(failed), file=sys.stderr)
        return 1

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

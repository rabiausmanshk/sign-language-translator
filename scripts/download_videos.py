"""Stage 2: download ONLY the videos listed in the manifest from the big remote zip.
Run from the project root:
    python -m scripts.download_videos --dry-run     (only show how big the download is)
    python -m scripts.download_videos --limit 5     (download 5 videos as a test)
    python -m scripts.download_videos               (download everything; finished files are skipped)
"""
import argparse
import re
from pathlib import Path

import pandas as pd
from remotezip import RemoteZip

ZIP_URL = ("https://download.microsoft.com/download/b/8/8/"
           "b88c0bae-e6c1-43e1-8726-98cf5af36ca4/ASL_Citizen.zip")
OUT_DIR = Path("data/raw/asl_citizen_subset")
VIDEO_DIR = OUT_DIR / "videos"


def safe_name(name):
    """'123-THANK YOU.mp4' -> '123-THANK_YOU.mp4' (no spaces in local file names)."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def local_path(row):
    """Where a video lives on our disk: videos/<split>/<label>/<file>. Used by later stages too."""
    return VIDEO_DIR / row.split / row.label / safe_name(row.video_file)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()

    m = pd.read_csv(OUT_DIR / "manifest_core20.csv")
    if args.limit:
        m = m.head(args.limit)

    print("Connecting to the remote archive (this only reads the file list)...")
    with RemoteZip(ZIP_URL) as z:
        sizes = {i.filename: i.file_size for i in z.infolist()}
        m["bytes"] = m["zip_path"].map(sizes)

        absent = m[m["bytes"].isna()]
        if len(absent):
            print(f"WARNING: {len(absent)} manifest rows are not in the archive, skipping them:")
            print(absent["zip_path"].head().to_string(index=False))
            m = m.dropna(subset=["bytes"])

        print(f"{len(m)} videos, {m['bytes'].sum() / 1e6:.1f} MB in total")
        if args.dry_run:
            return

        downloaded = skipped = failed = 0
        for i, row in enumerate(m.itertuples(), 1):
            dest = local_path(row)
            if dest.exists() and dest.stat().st_size == row.bytes:
                skipped += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                with z.open(row.zip_path) as src, open(dest, "wb") as out:
                    out.write(src.read())
                downloaded += 1
            except Exception as e:
                failed += 1
                print("FAILED:", row.zip_path, "->", e)
            if i % 25 == 0:
                print(f"{i}/{len(m)} checked")

    print(f"Done. downloaded={downloaded} already_had={skipped} failed={failed}")


if __name__ == "__main__":
    main()
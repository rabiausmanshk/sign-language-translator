"""Stage 1: list the videos we need. Nothing is downloaded here.
Run from the project root:  python -m scripts.build_manifest
"""
from pathlib import Path

import pandas as pd

from common.vocabulary import GLOSS_TO_LABEL, LABELS

SPLITS = Path("data/raw/asl_citizen_metadata/ASL_Citizen/splits")
OUT_DIR = Path("data/raw/asl_citizen_subset")


def main():
    parts = []
    for split in ["train", "val", "test"]:
        df = pd.read_csv(SPLITS / f"{split}.csv")
        df = df[df["Gloss"].isin(GLOSS_TO_LABEL)].copy()   # keep only our signs
        df["split"] = split                                # remember the official split
        parts.append(df)

    m = pd.concat(parts, ignore_index=True)
    m["label"] = m["Gloss"].map(GLOSS_TO_LABEL)
    m["zip_path"] = "ASL_Citizen/videos/" + m["Video file"]  # where it lives inside the big zip
    m = m.rename(columns={"Participant ID": "participant", "Video file": "video_file", "Gloss": "gloss"})
    m = m[["split", "label", "gloss", "participant", "video_file", "zip_path"]]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    m.to_csv(OUT_DIR / "manifest_core20.csv", index=False)

    counts = m.groupby(["label", "split"]).size().unstack(fill_value=0).reindex(LABELS)
    print(counts.to_string())
    print("\ntotal videos:", len(m))
    print("signers per split:", m.groupby("split")["participant"].nunique().to_dict())
    print("\nfirst rows:\n", m.head(3).to_string(index=False))
    missing = [l for l in LABELS if l not in set(m["label"])]
    if missing:
        print("\nWARNING: no videos found for:", missing)


if __name__ == "__main__":
    main()
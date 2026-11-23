"""Filter the huge Google ASL Signs dataset down to YOUR 20 signs.
Run this inside a Kaggle notebook (dataset attached, so no giant download):
    !git clone https://github.com/<your-user>/sign-language-translator.git
    %cd sign-language-translator
    !python -m vision.prepare_google_asl --root /kaggle/input/asl-signs
Then download data/processed/google_asl_subset.npz and share it with the team.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from common.config import SIGNS
from vision.features import frames_from_google_parquet, preprocess


def build(root, out_dir="data/processed"):
    root = Path(root)
    train = pd.read_csv(root / "train.csv")           # columns: path, participant_id, sequence_id, sign
    idx_map = json.load(open(root / "sign_to_prediction_index_map.json"))
    missing = [s for s in SIGNS if s not in idx_map]
    if missing:
        sys.exit(f"These signs are not in the dataset, replace them in common/config.py: {missing}")

    train = train[train.sign.isin(SIGNS)]
    X, y, who = [], [], []
    for n, row in enumerate(train.itertuples(), 1):
        seq = frames_from_google_parquet(root / row.path)
        if len(seq) < 2:
            continue
        X.append(preprocess(seq))
        y.append(SIGNS.index(row.sign))
        who.append(row.participant_id)
        if n % 500 == 0:
            print(n, "/", len(train))

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "google_asl_subset.npz",
                        X=np.stack(X), y=np.array(y), participant=np.array(who))
    print("saved", len(X), "sequences")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    build(ap.parse_args().root)

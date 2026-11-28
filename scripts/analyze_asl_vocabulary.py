
from pathlib import Path
import re
import pandas as pd

# --------------------------------------------------
# PATHS
# --------------------------------------------------

DATA_DIR = Path("data/raw/asl_citizen_metadata/ASL_Citizen/splits")
OUTPUT_DIR = Path("data/processed/vocabulary_analysis")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Initial screening criteria, NOT final vocabulary rules
MIN_TRAIN_VIDEOS = 12
MIN_TRAIN_SIGNERS = 

# Our preferred everyday vocabulary
PREFERRED_SIGNS = [
    "HELLO", "BYE", "PLEASE", "THANKYOU",
    "YES", "NO", "WATER", "DRINK", "FOOD",
    "HUNGRY", "THIRSTY", "HOME", "WHERE",
    "WHO", "SICK", "SLEEP", "MOM", "DAD",
    "WAIT", "NOW"
]

SPLITS = ["train", "val", "test"]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def normalize_gloss(value):
    """Make gloss comparison independent of spaces,
    hyphens and punctuation."""

    return re.sub(r"[^A-Z0-9]", "", str(value).upper())


def load_metadata():

    all_data = []

    for split in SPLITS:

        file_path = DATA_DIR / f"{split}.csv"

        if not file_path.exists():
            raise FileNotFoundError(
                f"Missing metadata file: {file_path}"
            )

        df = pd.read_csv(file_path)

        required_columns = [
            "Participant ID",
            "Video file",
            "Gloss",
            "ASL-LEX Code"
        ]

        missing = set(required_columns) - set(df.columns)

        if missing:
            raise ValueError(
                f"Missing columns in {split}.csv: {missing}"
            )

        df["split"] = split
        all_data.append(df)

        print(f"{split.upper()} rows: {len(df)}")

    return pd.concat(all_data, ignore_index=True)


# --------------------------------------------------
# ANALYSE EVERY GESTURE
# --------------------------------------------------

def calculate_statistics(df):

    records = []

    for gloss, group in df.groupby("Gloss"):

        train = group[group["split"] == "train"]
        val = group[group["split"] == "val"]
        test = group[group["split"] == "test"]

        records.append({

            "gloss": gloss,

            "total_videos": len(group),

            "train_videos": len(train),
            "val_videos": len(val),
            "test_videos": len(test),

            "total_signers": group["Participant ID"].nunique(),

            "train_signers": train["Participant ID"].nunique(),
            "val_signers": val["Participant ID"].nunique(),
            "test_signers": test["Participant ID"].nunique(),

            "asl_lex_codes": group["ASL-LEX Code"].nunique()

        })

    stats = pd.DataFrame(records)

    stats = stats.sort_values(
        by=["train_videos", "train_signers"],
        ascending=False
    )

    return stats


# --------------------------------------------------
# MATCH OUR PREFERRED VOCABULARY
# --------------------------------------------------

def match_preferred_signs(stats):

    stats = stats.copy()

    stats["normalized_gloss"] = (
        stats["gloss"].apply(normalize_gloss)
    )

    matches = []

    for preferred in PREFERRED_SIGNS:

        key = normalize_gloss(preferred)

        found = stats[
            stats["normalized_gloss"] == key
        ]

        if found.empty:

            matches.append({
                "requested_sign": preferred,
                "actual_gloss": "NOT FOUND",
                "train_videos": 0,
                "train_signers": 0,
                "val_videos": 0,
                "test_videos": 0,
                "status": "NOT FOUND"
            })

        else:

            for _, row in found.iterrows():

                eligible = (
                    row["train_videos"] >= MIN_TRAIN_VIDEOS
                    and row["train_signers"] >= MIN_TRAIN_SIGNERS
                )

                matches.append({

                    "requested_sign": preferred,
                    "actual_gloss": row["gloss"],

                    "train_videos": row["train_videos"],
                    "train_signers": row["train_signers"],

                    "val_videos": row["val_videos"],
                    "test_videos": row["test_videos"],

                    "status": (
                        "INITIAL CANDIDATE"
                        if eligible
                        else "INSUFFICIENT DATA"
                    )
                })

    return pd.DataFrame(matches)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\nLoading ASL Citizen metadata...\n")

    df = load_metadata()

    print("\nTOTAL RECORDS:", len(df))

    print("Unique glosses:", df["Gloss"].nunique())

    print(
        "Unique participants:",
        df["Participant ID"].nunique()
    )

    print(
        "Duplicate video filenames:",
        df["Video file"].duplicated().sum()
    )

    print(
        "Missing values:\n",
        df[[
            "Participant ID",
            "Video file",
            "Gloss",
            "ASL-LEX Code"
        ]].isna().sum()
    )

    # Full statistics
    stats = calculate_statistics(df)

    stats_path = (
        OUTPUT_DIR / "gesture_statistics.csv"
    )

    stats.to_csv(stats_path, index=False)

    # Initial candidates based on training data
    candidates = stats[
        (stats["train_videos"] >= MIN_TRAIN_VIDEOS)
        &
        (stats["train_signers"] >= MIN_TRAIN_SIGNERS)
    ].copy()

    candidates.to_csv(
        OUTPUT_DIR / "candidate_gestures.csv",
        index=False
    )

    # Preferred vocabulary matches
    preferred = match_preferred_signs(stats)

    preferred.to_csv(
        OUTPUT_DIR / "preferred_vocabulary_matches.csv",
        index=False
    )

    # Display results
    print("\n" + "=" * 60)
    print("TOP 30 GESTURES BY TRAINING DATA")
    print("=" * 60)

    print(
        stats.head(30)[[
            "gloss",
            "train_videos",
            "train_signers",
            "val_videos",
            "test_videos"
        ]].to_string(index=False)
    )

    print("\n" + "=" * 60)
    print("PREFERRED VOCABULARY MATCHES")
    print("=" * 60)

    print(preferred.to_string(index=False))

    print("\n" + "=" * 60)
    print("INITIAL CANDIDATE COUNT:", len(candidates))

    print("\nFiles saved in:", OUTPUT_DIR.resolve())

    print("\nVocabulary analysis completed!")


if __name__ == "__main__":
    main()

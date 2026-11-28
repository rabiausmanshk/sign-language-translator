
from pathlib import Path
from remotezip import RemoteZip
import pandas as pd

URL = (
    "https://download.microsoft.com/download/b/8/8/"
    "b88c0bae-e6c1-43e1-8726-98cf5af36ca4/"
    "ASL_Citizen.zip"
)

OUTPUT = Path("data/raw/asl_citizen_metadata")

SPLITS = [
    "ASL_Citizen/splits/train.csv",
    "ASL_Citizen/splits/val.csv",
    "ASL_Citizen/splits/test.csv",
]

def main():

    OUTPUT.mkdir(parents=True, exist_ok=True)

    print("Connecting to ASL Citizen...")

    with RemoteZip(URL) as archive:

        available = set(archive.namelist())

        # Find and extract only the small CSV files
        for member in SPLITS:

            if member not in available:
                raise FileNotFoundError(
                    f"Missing archive member: {member}"
                )

            print(f"\nExtracting: {member}")

            archive.extract(member, path=OUTPUT)

        # Find the dataset usage terms if present
        for member in available:
            if member.lower().endswith("use.txt"):
                print(f"\nFound usage terms: {member}")
                archive.extract(member, path=OUTPUT)

    print("\nReading metadata...")

    for split in ["train", "val", "test"]:

        path = (
            OUTPUT
            / "ASL_Citizen"
            / "splits"
            / f"{split}.csv"
        )

        df = pd.read_csv(path)

        print(f"\n{'=' * 45}")
        print(f"SPLIT: {split.upper()}")
        print("Rows:", len(df))
        print("Columns:", df.columns.tolist())

        print("\nFirst five rows:")
        print(df.head().to_string(index=False))

    print("\nMetadata extraction completed!")
    print("Location:", OUTPUT.resolve())


if __name__ == "__main__":
    main()

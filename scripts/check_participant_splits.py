
from pathlib import Path
import pandas as pd

base = Path("data/raw/asl_citizen_metadata/ASL_Citizen/splits")

train = pd.read_csv(base / "train.csv")
val = pd.read_csv(base / "val.csv")
test = pd.read_csv(base / "test.csv")

train_people = set(train["Participant ID"])
val_people = set(val["Participant ID"])
test_people = set(test["Participant ID"])

print("TRAIN participants:", len(train_people))
print("VAL participants:", len(val_people))
print("TEST participants:", len(test_people))

print("\nOVERLAP CHECK")

print("Train-Val:", train_people & val_people)
print("Train-Test:", train_people & test_people)
print("Val-Test:", val_people & test_people)

print("\nOVERLAP COUNTS")

print("Train-Val:", len(train_people & val_people))
print("Train-Test:", len(train_people & test_people))
print("Val-Test:", len(val_people & test_people))

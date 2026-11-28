"""Our final sign vocabulary. This is the ONE place to change it.
Left  = label the app shows (and the folder name for our own recordings).
Right = exact gloss name used by ASL Citizen."""

GLOSS_MAP = {
    "hello": "HELLO", "bye": "BYE", "please": "PLEASE", "thankyou": "THANKYOU", "sorry": "SORRY",
    "yes": "YES", "no": "NO", "me": "ME", "you": "YOU",
    "want": "WANT1", "need": "NEED", "go": "GO", "help": "HELP",
    "eat": "EAT1", "drink": "DRINK1",
    "water": "WATER", "home": "HOME", "bathroom": "BATHROOM",
    "what": "WHAT1", "where": "WHERE",
}

LABELS = list(GLOSS_MAP)                                   # position = class number 0..19
GLOSS_TO_LABEL = {g: l for l, g in GLOSS_MAP.items()}
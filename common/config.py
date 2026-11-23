"""Single source of truth shared by ALL members. Change here, everyone gets it."""

# 20 signs chosen so they combine into useful sentences.
# prepare_google_asl.py checks each one exists in the dataset - swap if it complains.
SIGNS = [
    "hello", "bye", "please", "thankyou", "yes", "no",
    "water", "drink", "food", "hungry", "thirsty",
    "home", "where", "who", "sick", "sleep",
    "mom", "dad", "wait", "now",
]

SEQ_LEN = 32          # every sign is resampled to 32 frames
FLIP_INPUT = False    # mirror gotcha: if live accuracy << test accuracy, try True (everywhere!)

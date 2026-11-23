"""Record your own signs with the webcam.
Run from repo root:  python -m vision.collect_data --person rabia
Keys: SPACE = record one sample | n / p = next / previous sign | q = quit
Saves raw (T,144) arrays to data/my_recordings/<sign>/<person>_<time>.npy
"""
import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import mediapipe as mp

from common.config import SIGNS, FLIP_INPUT
from vision.features import frame_from_holistic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--person", required=True)
    ap.add_argument("--seconds", type=float, default=2.0)
    args = ap.parse_args()

    out_root = Path("data/my_recordings")
    mp_h, draw = mp.solutions.holistic, mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    i, recording, frames, t_end = 0, False, [], 0.0

    with mp_h.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holo:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            if FLIP_INPUT:
                frame = cv2.flip(frame, 1)
            res = holo.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            for lms, conn in [(res.left_hand_landmarks, mp_h.HAND_CONNECTIONS),
                              (res.right_hand_landmarks, mp_h.HAND_CONNECTIONS),
                              (res.pose_landmarks, mp_h.POSE_CONNECTIONS)]:
                draw.draw_landmarks(frame, lms, conn)

            sign = SIGNS[i]
            folder = out_root / sign
            folder.mkdir(parents=True, exist_ok=True)

            if recording:
                frames.append(frame_from_holistic(res))
                if time.time() >= t_end:
                    np.save(folder / f"{args.person}_{int(time.time())}.npy", np.array(frames))
                    recording = False

            show = frame if FLIP_INPUT else cv2.flip(frame, 1)   # mirror view for humans
            n = len(list(folder.glob(f"{args.person}_*.npy")))
            color = (0, 0, 255) if recording else (0, 200, 0)
            cv2.putText(show, f"{sign.upper()}  ({n} saved)  {'REC' if recording else 'ready'}",
                        (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.imshow("collect", show)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("n"):
                i = (i + 1) % len(SIGNS)
            elif key == ord("p"):
                i = (i - 1) % len(SIGNS)
            elif key == 32 and not recording:
                recording, frames, t_end = True, [], time.time() + args.seconds

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

"""Turn MediaPipe landmarks into fixed-size number arrays.
The SAME functions are used for (1) Google dataset, (2) your own recordings, (3) live webcam,
so training data and live data always look identical.
"""
import warnings
import numpy as np
from common.config import SEQ_LEN

POSE_IDS = [11, 12, 13, 14, 15, 16]      # shoulders, elbows, wrists
N_PTS = 21 + 21 + 6                       # left hand, right hand, 6 pose points
FEAT_DIM = N_PTS * 3                      # 144
SHOULDER_L, SHOULDER_R = 42, 43           # positions inside the 48 points


def _lm_to_arr(lms, n):
    if lms is None:                       # hand/pose not detected -> NaN
        return np.full((n, 3), np.nan, dtype=np.float32)
    return np.array([[p.x, p.y, p.z] for p in lms.landmark], dtype=np.float32)


def frame_from_holistic(results):
    """One live MediaPipe Holistic result -> (144,) vector."""
    lh = _lm_to_arr(results.left_hand_landmarks, 21)
    rh = _lm_to_arr(results.right_hand_landmarks, 21)
    pose = _lm_to_arr(results.pose_landmarks, 33)[POSE_IDS]
    return np.concatenate([lh, rh, pose]).reshape(-1)


def frames_from_google_parquet(path):
    """Google ASL Signs parquet (543 landmarks/frame) -> (T, 144)."""
    import pandas as pd
    df = pd.read_parquet(path, columns=["x", "y", "z"])
    n = len(df) // 543
    arr = df[["x", "y", "z"]].to_numpy(dtype=np.float32)[: n * 543].reshape(n, 543, 3)
    lh = arr[:, 468:489]
    pose = arr[:, 489:522][:, POSE_IDS]
    rh = arr[:, 522:543]
    return np.concatenate([lh, rh, pose], axis=1).reshape(n, -1)


def preprocess(seq, seq_len=SEQ_LEN):
    """(T,144) raw -> (seq_len,144): resample, centre on shoulders, scale by shoulder width."""
    seq = np.asarray(seq, dtype=np.float32).reshape(len(seq), N_PTS, 3)
    idx = np.linspace(0, len(seq) - 1, seq_len).round().astype(int)
    seq = seq[idx]
    missing = np.isnan(seq)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        center = np.nanmean(seq[:, [SHOULDER_L, SHOULDER_R]], axis=1)          # (T,3)
        width = np.nanmean(np.linalg.norm(
            seq[:, SHOULDER_L, :2] - seq[:, SHOULDER_R, :2], axis=1))
    center = np.nan_to_num(center)
    if not np.isfinite(width) or width < 1e-6:
        width = 1.0
    seq = (seq - center[:, None, :]) / width
    seq[missing] = 0.0                      # missing hand = zeros
    return np.nan_to_num(seq).reshape(seq_len, -1).astype(np.float32)

"""GUI backend (Kainat). Run from repo root:  uvicorn app.main:app --reload
Open http://127.0.0.1:8000
/video = webcam with live skeleton drawn (the Computer Graphics part)
/ws    = predictions + sentence (fake now, real after integration)
"""
from pathlib import Path

import cv2
import mediapipe as mp
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse

from app.mock.fake_stream import fake_stream
from common.config import FLIP_INPUT

app = FastAPI()
STATIC = Path(__file__).parent / "static"


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


def mjpeg():
    mp_h, draw = mp.solutions.holistic, mp.solutions.drawing_utils
    cap = cv2.VideoCapture(0)
    with mp_h.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holo:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if FLIP_INPUT:
                frame = cv2.flip(frame, 1)
            res = holo.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            draw.draw_landmarks(frame, res.left_hand_landmarks, mp_h.HAND_CONNECTIONS)
            draw.draw_landmarks(frame, res.right_hand_landmarks, mp_h.HAND_CONNECTIONS)
            draw.draw_landmarks(frame, res.pose_landmarks, mp_h.POSE_CONNECTIONS)
            show = frame if FLIP_INPUT else cv2.flip(frame, 1)
            _, buf = cv2.imencode(".jpg", show)
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n"
    cap.release()


@app.get("/video")
def video():
    return StreamingResponse(mjpeg(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.websocket("/ws")
async def ws(sock: WebSocket):
    await sock.accept()
    try:
        async for item in fake_stream():
            await sock.send_json(item)
    except WebSocketDisconnect:
        pass

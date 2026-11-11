import time
from typing import List
import time
import face_recognition
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from datetime import datetime

from database import get_attendance, get_samples, init_db, mark_attendance, save_samples
from face_service import MATCH_THRESHOLD, get_encoding

ENROLL_SAMPLES = 5   # photos needed to register
VERIFY_FRAMES = 3    # pictures needed to log in

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()
FAILED = {}       # employee_id -> times of failed attempts
MAX_FAILS = 5     # allowed failed face attempts
WINDOW = 600      # within 10 minutes


def too_many_fails(emp):
    now = time.time()
    FAILED[emp] = [t for t in FAILED.get(emp, []) if now - t < WINDOW]
    return len(FAILED[emp]) >= MAX_FAILS
FAILED = {}       # employee_id -> times of failed attempts
MAX_FAILS = 5     # allowed failed face attempts
WINDOW = 600      # within 10 minutes


def too_many_fails(emp):
    now = time.time()
    FAILED[emp] = [t for t in FAILED.get(emp, []) if now - t < WINDOW]
    return len(FAILED[emp]) >= MAX_FAILS

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect")
async def detect(image: UploadFile = File(...)):
    data = await image.read()
    encoding, count = get_encoding(data)
    return {"faces_found": count, "ok": encoding is not None}


@app.post("/enroll")
async def enroll(employee_id: str = Form(...), images: List[UploadFile] = File(...)):
    if len(images) < ENROLL_SAMPLES:
        return {"ok": False, "message": f"Send at least {ENROLL_SAMPLES} photos"}

    encodings = []
    for img in images:
        enc, count = get_encoding(await img.read())
        if enc is None:
            return {"ok": False, "message": "Every photo must show exactly one clear face"}
        encodings.append(enc)

    # safety check: all photos must be the same person
    distances = [
        round(float(face_recognition.face_distance([encodings[0]], e)[0]), 3)
        for e in encodings[1:]
    ]
    if any(d > 0.6 for d in distances):
        return {
            "ok": False,
            "message": "A photo looks different from photo 1. Retake the bad one.",
            "distances_to_photo_1": distances,
        }

    save_samples(employee_id, encodings)
    return {"ok": True, "message": f"Enrolled {len(encodings)} samples"}

@app.post("/verify")
async def verify(employee_id: str = Form(...), images: List[UploadFile] = File(...)):
    if too_many_fails(employee_id):
        return {"matched": False, "reason": "too_many_attempts"}

    saved = get_samples(employee_id)
    if not saved:
        return {"matched": False, "reason": "not_enrolled"}
    if len(images) < VERIFY_FRAMES:
        return {"matched": False, "reason": "need_more_frames"}

    distances = []
    for img in images:
        enc, count = get_encoding(await img.read())
        if enc is None:
            return {"matched": False, "reason": "no_clear_face"}
        distances.append(round(float(min(face_recognition.face_distance(saved, enc))), 3))

    matched = all(d < MATCH_THRESHOLD for d in distances)
    if not matched:
        FAILED.setdefault(employee_id, []).append(time.time())
    return {
        "matched": matched,
        "distances": distances,
        "reason": "ok" if matched else "face_mismatch",
    }
@app.post("/attendance/mark")
async def attendance_mark(employee_id: str = Form(...), images: List[UploadFile] = File(...)):
    if too_many_fails(employee_id):
        return {"ok": False, "reason": "too_many_attempts"}

    saved = get_samples(employee_id)
    if not saved:
        return {"ok": False, "reason": "not_enrolled"}
    if len(images) < VERIFY_FRAMES:
        return {"ok": False, "reason": "need_more_frames"}

    distances = []
    for img in images:
        enc, count = get_encoding(await img.read())
        if enc is None:
            return {"ok": False, "reason": "no_clear_face"}
        distances.append(round(float(min(face_recognition.face_distance(saved, enc))), 3))

    if not all(d < MATCH_THRESHOLD for d in distances):
        FAILED.setdefault(employee_id, []).append(time.time())
        return {"ok": False, "reason": "face_mismatch"}

    result = mark_attendance(employee_id)   # face matched, so save the time
    return {"ok": True, **result}


@app.get("/attendance/today")
def attendance_today():
    today = datetime.now().strftime("%Y-%m-%d")
    return {"date": today, "records": get_attendance(today)}

app.mount("/demo", StaticFiles(directory="static", html=True), name="demo")
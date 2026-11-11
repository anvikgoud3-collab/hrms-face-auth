# Face Login Module (HRMS)

Python (FastAPI) service that registers and verifies employee faces.
Stores only face numbers (128 values per sample), never photos.

## Run
    ## Setup (Windows, Python 3.10 to 3.12)
    python -m venv venv
    venv\Scripts\activate
    pip install dlib-bin
    pip install face_recognition_models Click numpy Pillow "setuptools<81"
    pip install face_recognition --no-deps
    pip install fastapi uvicorn python-multipart opencv-python requests

## Run
    uvicorn main:app --reload

Demo page: http://localhost:8000/demo/
Note: faces.db is not in the repository. Each person registers their own face on their own machine.

## API
| Endpoint | Sends | Returns |
|---|---|---|
| POST /enroll | employee_id + 5 or more photos (form-data, field "images") | { ok, message } |
| POST /verify | employee_id + 3 photos | { matched, distances, reason } |
| POST /attendance/mark | employee_id + 3 photos | { ok, action, time } or { ok: false, reason } |
| GET /attendance/today | nothing | { date, records: [employee_id, check_in, check_out] } |

verify reasons: ok, face_mismatch, not_enrolled, no_clear_face, need_more_frames, too_many_attempts
attendance actions: check_in, check_out, too_soon (wait 1 minute), already_done

## Safety rules built in
- 5 photos to register, 3 matching pictures to log in or mark attendance.
- Match limit 0.5 (strict). Only face numbers are saved, never photos.
- After 5 failed face attempts in 10 minutes, face login is blocked for that employee (counter resets when the server restarts).

reason values: ok, face_mismatch, not_enrolled, no_clear_face, need_more_frames

## How to add it to the dashboard
1. Copy the camera and capture code from static/index.html into a React component.
2. Set the API address (currently "") to the address this service runs on.
3. If matched is true, continue the normal login. If false, or the server cannot be reached, show the existing password form.
4. Add your dashboard's address to allow_origins in main.py (currently localhost:5173 and localhost:3000).

## Before production
The attempt counter is in memory. Move it to the database for production.
- Face matching alone must not create the login session. After matched is true, the backend should issue the login token or session itself.
- Add a login attempt limit and HTTPS.
- Get employee consent for face data and restrict who can read faces.db.
- This version has no liveness check, so a printed photo could fool it.
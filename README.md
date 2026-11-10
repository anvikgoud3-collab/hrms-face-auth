# Face Login Module (HRMS)

Python (FastAPI) service that registers and verifies employee faces.
Stores only face numbers (128 values per sample), never photos.

## Run
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    uvicorn main:app --reload

Demo page: http://localhost:8000/demo/

## API
| Endpoint | Sends | Returns |
|---|---|---|
| POST /enroll | employee_id + 5 or more photos (form-data, field "images") | { ok, message } |
| POST /verify | employee_id + 3 photos (form-data, field "images") | { matched, distances, reason } |

reason values: ok, face_mismatch, not_enrolled, no_clear_face, need_more_frames

## How to add it to the dashboard
1. Copy the camera and capture code from static/index.html into a React component.
2. Set the API address (currently "") to the address this service runs on.
3. If matched is true, continue the normal login. If false, or the server cannot be reached, show the existing password form.
4. Add your dashboard's address to allow_origins in main.py (currently localhost:5173 and localhost:3000).

## Before production
- Face matching alone must not create the login session. After matched is true, the backend should issue the login token or session itself.
- Add a login attempt limit and HTTPS.
- Get employee consent for face data and restrict who can read faces.db.
- This version has no liveness check, so a printed photo could fool it.
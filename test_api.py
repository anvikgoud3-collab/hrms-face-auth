import os
import requests

URL = "http://127.0.0.1:8000"
FOLDER = os.path.dirname(os.path.abspath(__file__))


def send(endpoint, employee_id, filenames):
    files = [
        ("images", (name, open(os.path.join(FOLDER, name), "rb"), "image/jpeg"))
        for name in filenames
    ]
    response = requests.post(
        URL + endpoint, data={"employee_id": employee_id}, files=files
    )
    return response.json()


print("Photos found here:", [f for f in os.listdir(FOLDER) if f.lower().endswith((".jpg", ".jpeg", ".png"))])

# Test A: register EMP001 with 5 photos
print("ENROLL:", send("/enroll", "EMP001",
      ["me1.jpg", "me2.jpg", "me3.jpg", "me4.jpg", "me5.jpg"]))

# Test B: log in as EMP001 with your own face
print("VERIFY (me):", send("/verify", "EMP001", ["v1.jpg", "v2.jpg", "v3.jpg"]))

# Test D: an employee who was never registered
print("VERIFY (unknown):", send("/verify", "EMP999", ["v1.jpg", "v2.jpg", "v3.jpg"]))
print("VERIFY (other person):", send("/verify", "EMP001", ["other.jpg", "other.jpg", "other.jpg"]))

print("ATTEND:", send("/attendance/mark", "EMP001", ["v1.jpg", "v2.jpg", "v3.jpg"]))
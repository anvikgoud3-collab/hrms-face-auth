import io
import numpy as np
import face_recognition
from PIL import Image, ImageOps

MATCH_THRESHOLD = 0.5   # lower = stricter
MAX_SIDE = 640          # shrink big photos so checks stay fast


def load_image(file_bytes):
    img = Image.open(io.BytesIO(file_bytes))
    img = ImageOps.exif_transpose(img)   # fix phone photos that are rotated
    img = img.convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))  # resize: this is what keeps it fast
    return np.array(img)


def get_encoding(file_bytes):
    """Returns (encoding, faces_found). Encoding is None unless exactly 1 face."""
    image = load_image(file_bytes)
    locations = face_recognition.face_locations(image, model="hog")
    if len(locations) != 1:
        return None, len(locations)
    encoding = face_recognition.face_encodings(image, known_face_locations=locations)[0]
    return encoding, 1
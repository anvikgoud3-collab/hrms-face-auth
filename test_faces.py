import face_recognition

def get_encoding(path):
    image = face_recognition.load_image_file(path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) != 1:
        print(path, "-> faces found:", len(encodings), "(need exactly 1)")
        return None
    return encodings[0]   # the 128 numbers that represent the face

def compare(path_a, path_b):
    a = get_encoding(path_a)
    b = get_encoding(path_b)
    if a is None or b is None:
        return
    d = face_recognition.face_distance([a], b)[0]
    print(path_a, "vs", path_b, "-> distance", round(d, 3),
          "MATCH" if d < 0.5 else "NO MATCH")

compare("me1.jpg", "me2.jpg")      # should be MATCH
compare("me1.jpg", "other.jpg")    # should be NO MATCH
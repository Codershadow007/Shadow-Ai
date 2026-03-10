import os
import base64
import cv2
import numpy as np

FACES_DIR = "faces"
os.makedirs(FACES_DIR, exist_ok=True)

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

def decode_image(image_data):

    image_data = image_data.split(",")[1]

    img_bytes = base64.b64decode(image_data)

    img_array = np.frombuffer(img_bytes, dtype=np.uint8)

    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return frame


def extract_face(frame):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        return None

    (x, y, w, h) = faces[0]

    face = gray[y:y+h, x:x+w]

    face = cv2.resize(face, (150,150))

    return face


def capture_face(username, image_data):

    frame = decode_image(image_data)

    face = extract_face(frame)

    if face is None:
        return False

    path = os.path.join(FACES_DIR, f"{username}.jpg")

    cv2.imwrite(path, face)

    return True


def recognize_face(image_data):

    frame = decode_image(image_data)

    unknown_face = extract_face(frame)

    if unknown_face is None:
        return None

    best_match = None
    best_score = 999999

    for file in os.listdir(FACES_DIR):

        path = os.path.join(FACES_DIR, file)

        known = cv2.imread(path, 0)

        if known is None:
            continue

        known = cv2.resize(known, (150,150))

        score = np.mean((known - unknown_face) ** 2)

        if score < best_score:
            best_score = score
            best_match = file.split(".")[0]

    # stricter threshold
    if best_score < 800:
        return best_match

    return None
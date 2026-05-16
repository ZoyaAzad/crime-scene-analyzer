import cv2

def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    cascade = cv2.CascadeClassifier(
        "assets/haarcascade_frontalface_default.xml"
    )

    faces = cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    output = image.copy()
    face_count = 0

    for (x, y, w, h) in faces:
        face_count += 1
        cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 255), 2)
        cv2.putText(
            output,
            f"FACE #{face_count}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

    return output, face_count
import cv2
import numpy as np

# -------------------------
# 1. Canny Edge Detection
# -------------------------
def canny_edges(image, t1, t2):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, t1, t2)
    return edges

# -------------------------
# 2. Contour Detection
# -------------------------
def detect_contours(image, min_area=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    output = image.copy()

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > min_area:
            cv2.drawContours(output, [cnt], -1, (0, 255, 0), 2)

    return output

# -------------------------
# 3. Thresholding
# -------------------------
def threshold_image(image, thresh_value):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(
        gray,
        thresh_value,
        255,
        cv2.THRESH_BINARY
    )

    return thresh
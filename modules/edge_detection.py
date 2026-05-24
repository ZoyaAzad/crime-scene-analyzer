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
def detect_contours(image, min_area):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # gentle internal blur
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    significant = [c for c in contours if cv2.contourArea(c) > min_area]
    result = image.copy()
    
    for i, c in enumerate(significant):
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        cv2.drawContours(result, [c], -1, (0, 255, 0), 2)
        cv2.rectangle(result, (x, y), (x+w, y+h), (0, 200, 255), 1)
        cv2.putText(result, f"#{i+1} {int(area)}px", (x, y-6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
    
    areas = [cv2.contourArea(c) for c in significant]
    return result, len(significant), areas  # return counts!

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
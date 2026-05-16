import cv2
import numpy as np

# -------------------------
# HSV Color Segmentation
# -------------------------
def segment_color(image, lower_bound, upper_bound):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    result = cv2.bitwise_and(image, image, mask=mask)

    return result, mask
import cv2
import numpy as np

def segment_color(image, lower, upper):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    
    # CRITICAL: morphological cleanup — removes noise dots
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)   # removes tiny specs
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # fills gaps in real stains
    
    # Find and draw contours of detected regions
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = image.copy()
    
    significant = [c for c in contours if cv2.contourArea(c) > 300]
    
    # Red overlay on detected stain regions
    overlay = result.copy()
    cv2.drawContours(overlay, significant, -1, (0, 0, 180), -1)  # filled red
    result = cv2.addWeighted(overlay, 0.4, result, 0.6, 0)        # semi-transparent
    cv2.drawContours(result, significant, -1, (0, 0, 255), 2)     # red border
    
    # Calculate coverage
    pixel_count = cv2.countNonZero(mask)
    total = mask.shape[0] * mask.shape[1]
    coverage = (pixel_count / total) * 100
    
    return result, mask, len(significant), coverage
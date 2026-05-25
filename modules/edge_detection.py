import cv2
import numpy as np


# ── 1. Canny Edge Detection ───────────────────────────────────────────────────
def canny_edges(image, t1, t2):
    gray  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, t1, t2)
    return edges


# ── 2. Sobel Edge Detection ───────────────────────────────────────────────────
def sobel_edges(image):
    """
    Sobel detects directional gradients — horizontal AND vertical edges separately.
    Better than Canny for showing the direction of force/impact on surfaces.
    Returns a colour-coded result: red=horizontal, blue=vertical, white=both.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Sobel in X direction (vertical edges — left/right gradients)
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    # Sobel in Y direction (horizontal edges — top/bottom gradients)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

    # Absolute values
    abs_x = cv2.convertScaleAbs(sobelx)
    abs_y = cv2.convertScaleAbs(sobely)

    # Combined magnitude
    combined = cv2.addWeighted(abs_x, 0.5, abs_y, 0.5, 0)

    # Colour-coded: show X in red channel, Y in blue channel
    result = np.zeros((gray.shape[0], gray.shape[1], 3), dtype=np.uint8)
    result[:, :, 2] = abs_x   # Red  = vertical edges (X gradient)
    result[:, :, 0] = abs_y   # Blue = horizontal edges (Y gradient)
    result[:, :, 1] = combined // 2  # Green = combined (dim)

    return result, abs_x, abs_y, combined


# ── 3. Contour Detection + Bullet/Impact Hole Detection ──────────────────────
def detect_contours(image, min_area):
    """
    Detects object contours AND flags near-circular ones as potential
    impact points (bullet holes, wound marks) using circularity ratio.
    Circularity = 4π × area / perimeter²  → 1.0 = perfect circle
    """
    gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges   = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    significant  = [c for c in contours if cv2.contourArea(c) > min_area]
    result       = image.copy()
    impact_count = 0
    areas        = []

    for i, c in enumerate(significant):
        area      = cv2.contourArea(c)
        perimeter = cv2.arcLength(c, True)
        x, y, bw, bh = cv2.boundingRect(c)
        areas.append(area)

        # Circularity — isoperimetric ratio
        circularity = 0.0
        if perimeter > 0:
            circularity = (4 * np.pi * area) / (perimeter ** 2)

        is_impact = circularity > 0.65 and area < 8000  # circular + not too large

        if is_impact:
            impact_count += 1
            # Orange box + warning label for circular shapes
            cv2.drawContours(result, [c], -1, (0, 140, 255), 2)
            cv2.rectangle(result, (x, y - 18), (x + bw, y), (0, 140, 255), -1)
            cv2.putText(result, f"⚠ IMPACT #{impact_count} ({circularity:.2f})",
                        (x + 2, y - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 0), 1)
        else:
            # Green box for regular objects
            cv2.drawContours(result, [c], -1, (0, 255, 0), 2)
            cv2.rectangle(result, (x, y), (x + bw, y + bh), (0, 200, 255), 1)
            cv2.putText(result, f"#{i+1} {int(area)}px",
                        (x, max(y - 6, 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

    return result, len(significant), areas, impact_count


# ── 4. Thresholding ───────────────────────────────────────────────────────────
def threshold_image(image, thresh_value):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, thresh_value, 255, cv2.THRESH_BINARY)
    return thresh
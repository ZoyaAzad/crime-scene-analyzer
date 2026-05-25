import cv2
import numpy as np


def segment_color(image, lower, upper):
    """
    Multi-range blood detection that catches:
    - Fresh bright red blood
    - Dried dark brownish-red blood  
    - Blood on textured surfaces (carpet, concrete)
    - Blood in low light / dark scenes
    
    Uses 3 HSV ranges simultaneously + user range,
    with conservative exclusions that don't eat real blood.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, w = image.shape[:2]

    # ── Range 1: User-defined (from sliders) ─────────────────────────────
    mask_user = cv2.inRange(hsv, lower, upper)

    # ── Range 2: Fresh/bright red blood ──────────────────────────────────
    # Bright red: high saturation, medium-high value
    fresh_lower = np.array([0,  120, 50])
    fresh_upper = np.array([10, 255, 220])
    mask_fresh  = cv2.inRange(hsv, fresh_lower, fresh_upper)
    # Red wraps around in HSV — also check the 170-180 end
    fresh_lower2 = np.array([170, 120, 50])
    fresh_upper2 = np.array([180, 255, 220])
    mask_fresh2  = cv2.inRange(hsv, fresh_lower2, fresh_upper2)
    mask_fresh   = cv2.bitwise_or(mask_fresh, mask_fresh2)

    # ── Range 3: Dried/dark blood ─────────────────────────────────────────
    # Brownish-red, lower saturation, darker value
    dried_lower = np.array([0,  40, 15])
    dried_upper = np.array([20, 180, 130])
    mask_dried  = cv2.inRange(hsv, dried_lower, dried_upper)
    # Also the high-hue end for very dark dried blood
    dried_lower2 = np.array([165, 40, 15])
    dried_upper2 = np.array([180, 180, 130])
    mask_dried2  = cv2.inRange(hsv, dried_lower2, dried_upper2)
    mask_dried   = cv2.bitwise_or(mask_dried, mask_dried2)

    # ── Range 4: Blood on dark surfaces (low V) ───────────────────────────
    dark_lower = np.array([0,  60, 10])
    dark_upper = np.array([15, 255, 80])
    mask_dark  = cv2.inRange(hsv, dark_lower, dark_upper)
    dark_lower2 = np.array([165, 60, 10])
    dark_upper2 = np.array([180, 255, 80])
    mask_dark2  = cv2.inRange(hsv, dark_lower2, dark_upper2)
    mask_dark   = cv2.bitwise_or(mask_dark, mask_dark2)

    # ── Combine all ranges ────────────────────────────────────────────────
    combined = cv2.bitwise_or(mask_user, mask_fresh)
    combined = cv2.bitwise_or(combined,  mask_dried)
    combined = cv2.bitwise_or(combined,  mask_dark)

    # ── Exclusions — CONSERVATIVE, don't remove dark pixels ──────────────

    # 1. Skin exclusion: only remove BRIGHT skin (V > 120)
    #    Dark skin-coloured regions are more likely blood than skin
    skin_lower = np.array([0,  25, 120])   # V must be > 120 to be skin
    skin_upper = np.array([20, 140, 255])
    skin_mask  = cv2.inRange(hsv, skin_lower, skin_upper)
    # Dilate skin mask slightly to catch edges
    skin_kernel = np.ones((3, 3), np.uint8)
    skin_mask   = cv2.dilate(skin_mask, skin_kernel, iterations=1)
    # Only remove skin pixels if they are NOT also in a dark region
    dark_region = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([179, 255, 100]))
    skin_safe   = cv2.bitwise_and(skin_mask, cv2.bitwise_not(dark_region))
    combined    = cv2.bitwise_and(combined, cv2.bitwise_not(skin_safe))

    # 2. Large uniform background exclusion
    #    Wood/walls are large smooth areas — remove only if region > 3% of image
    #    Use morphological opening with large kernel to find large uniform areas
    bg_kernel = np.ones((25, 25), np.uint8)
    large_bg  = cv2.morphologyEx(combined, cv2.MORPH_OPEN, bg_kernel)
    # Only subtract if it's genuinely large (background-sized)
    large_bg_pixels = cv2.countNonZero(large_bg)
    if large_bg_pixels > (h * w * 0.03):  # > 3% of image = background
        combined = cv2.bitwise_and(combined, cv2.bitwise_not(large_bg))

    # ── Morphological cleanup ─────────────────────────────────────────────
    clean_kernel = np.ones((4, 4), np.uint8)
    combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN,  clean_kernel)
    combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, clean_kernel)

    # ── Contour filtering ─────────────────────────────────────────────────
    contours, _ = cv2.findContours(
        combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    significant = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < 150:   # minimum size — catches small splatter too
            continue

        hull      = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)
        solidity  = area / hull_area if hull_area > 0 else 0

        # Reject only VERY large near-perfect rectangles (clear backgrounds)
        # Solidity > 0.97 AND area > 8% of image = definitely background
        if solidity > 0.97 and area > (h * w * 0.08):
            continue

        significant.append(c)

    # ── Rebuild clean mask ────────────────────────────────────────────────
    clean_mask = np.zeros_like(combined)
    cv2.drawContours(clean_mask, significant, -1, 255, -1)

    # ── Draw overlay ──────────────────────────────────────────────────────
    result  = image.copy()
    overlay = result.copy()
    cv2.drawContours(overlay, significant, -1, (0, 0, 160), -1)
    result = cv2.addWeighted(overlay, 0.35, result, 0.65, 0)
    cv2.drawContours(result, significant, -1, (0, 0, 255), 2)

    for i, c in enumerate(significant):
        x, y, bw, bh = cv2.boundingRect(c)
        area = cv2.contourArea(c)
        cv2.putText(result, f"S{i+1} {int(area)}px",
                    (x, max(y - 6, 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    pixel_count = cv2.countNonZero(clean_mask)
    total       = h * w
    coverage    = (pixel_count / total) * 100

    return result, clean_mask, len(significant), coverage
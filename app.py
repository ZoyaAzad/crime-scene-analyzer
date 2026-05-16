import streamlit as st
import cv2
import numpy as np
from PIL import Image

from modules.noise_reduction import gaussian_blur, median_filter
from modules.color_segment import segment_color
from modules.edge_detection import (
    canny_edges,
    detect_contours,
    threshold_image
)
from modules.enhancement import (
    histogram_equalization,
    adjust_contrast_brightness,
    sharpen_image
)

st.set_page_config(page_title="Crime Scene Image Analyzer", layout="wide")

st.title("CRIME SCENE IMAGE ANALYZER")

# ======================
# SIDEBAR CONTROLS
# ======================

uploaded_file = st.sidebar.file_uploader(
    "Upload Evidence Image",
    type=["jpg", "jpeg", "png"]
)

st.sidebar.header("Enhancement Controls")
contrast = st.sidebar.slider("Contrast", 0.5, 3.0, 1.0)
brightness = st.sidebar.slider("Brightness", -100, 100, 0)
apply_hist = st.sidebar.checkbox("Histogram Equalization")
apply_sharpen = st.sidebar.checkbox("Sharpen Image")

st.sidebar.header("Noise Reduction Controls")
kernel_size = st.sidebar.slider("Kernel Size", 3, 31, 9, step=2)
apply_gaussian = st.sidebar.checkbox("Gaussian Blur")
apply_median = st.sidebar.checkbox("Median Filter")

st.sidebar.header("Edge Detection Controls")
edge_mode = st.sidebar.selectbox(
    "Select Detection Method",
    ["None", "Canny Edges", "Contours", "Thresholding"]
)

t1 = st.sidebar.slider("Canny Threshold 1", 0, 255, 50)
t2 = st.sidebar.slider("Canny Threshold 2", 0, 255, 150)
min_area = st.sidebar.slider("Min Contour Area", 50, 5000, 500)
threshold_val = st.sidebar.slider("Threshold Value", 0, 255, 127)

st.sidebar.header("Color Segmentation (HSV)")
enable_color = st.sidebar.checkbox("Enable Color Detection")

h_min = st.sidebar.slider("Hue Min", 0, 179, 0)
h_max = st.sidebar.slider("Hue Max", 0, 179, 20)
s_min = st.sidebar.slider("Saturation Min", 0, 255, 100)
s_max = st.sidebar.slider("Saturation Max", 0, 255, 255)
v_min = st.sidebar.slider("Value Min", 0, 255, 50)
v_max = st.sidebar.slider("Value Max", 0, 255, 255)

# Reset button
if st.sidebar.button("Reset Image"):
    st.session_state.clear()
    st.rerun()

# ======================
# MAIN LOGIC
# ======================

if uploaded_file:

    image = Image.open(uploaded_file)
    image_np = np.array(image)

    # RGB → BGR
    image_cv = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

    # Always overwrite session image on new upload
    st.session_state.original_image = image_cv.copy()

    base_image = st.session_state.original_image.copy()
    processed = base_image.copy()

    # ======================
    # MODULE 1: ENHANCEMENT
    # ======================
    processed = adjust_contrast_brightness(processed, contrast, brightness)

    if apply_hist:
        processed = histogram_equalization(processed)

    if apply_sharpen:
        processed = sharpen_image(processed)

    # ======================
    # MODULE 2: NOISE REDUCTION
    # ======================
    if apply_gaussian:
        processed = gaussian_blur(processed, kernel_size)

    if apply_median:
        processed = median_filter(processed, kernel_size)

    # ======================
    # MODULE 3: EDGE DETECTION
    # ======================
    if edge_mode == "Canny Edges":
        processed = canny_edges(processed, t1, t2)

    elif edge_mode == "Contours":
        processed = detect_contours(processed, min_area)

    elif edge_mode == "Thresholding":
        processed = threshold_image(processed, threshold_val)

    # ======================
    # MODULE 4: COLOR SEGMENTATION
    # ======================
    mask = None

    if enable_color:
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])

        processed, mask = segment_color(processed, lower, upper)

    # ======================
    # SAFE DISPLAY CONVERSION
    # ======================
    if len(processed.shape) == 2:
        processed_display = processed
    else:
        processed_display = cv2.cvtColor(processed, cv2.COLOR_BGR2RGB)

    # ======================
    # UI OUTPUT
    # ======================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Original Image")
        st.image(image_np, use_container_width=True)

    with col2:
        st.subheader("Processed Image")
        st.image(processed_display, use_container_width=True)

    if enable_color and mask is not None:
        st.subheader("Detection Mask")
        st.image(mask, use_container_width=True, clamp=True)
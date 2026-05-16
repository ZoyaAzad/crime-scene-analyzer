import cv2

# Gaussian Blur (general smoothing)
def gaussian_blur(image, ksize):
    if ksize % 2 == 0:
        ksize += 1  # kernel must be odd
    return cv2.GaussianBlur(image, (ksize, ksize), 0)

# Median Filter (salt & pepper noise removal)
def median_filter(image, ksize):
    if ksize % 2 == 0:
        ksize += 1
    return cv2.medianBlur(image, ksize)
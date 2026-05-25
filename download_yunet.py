"""
Run once: python download_yunet.py
Tries multiple mirrors to download YuNet face detection model.
"""
import urllib.request, os, sys

os.makedirs("assets", exist_ok=True)
dest = "assets/face_detection_yunet_2023mar.onnx"

if os.path.exists(dest) and os.path.getsize(dest) > 100_000:
    print(f"  Already exists and looks valid: {dest}")
    sys.exit(0)

mirrors = [
    # Mirror 1 — direct file from opencv_zoo releases
    "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    # Mirror 2 — jsdelivr CDN (usually faster, bypasses GitHub rate limits)
    "https://cdn.jsdelivr.net/gh/opencv/opencv_zoo@main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    # Mirror 3 — raw via ghproxy
    "https://ghproxy.com/https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
]

def progress(count, block, total):
    if total > 0:
        pct = min(count * block * 100 // total, 100)
        print(f"\r  {pct:3d}%", end="", flush=True)

for url in mirrors:
    print(f"\nTrying: {url[:60]}...")
    try:
        urllib.request.urlretrieve(url, dest, reporthook=progress)
        size = os.path.getsize(dest)
        if size > 100_000:
            print(f"\n  ✓  Downloaded {dest}  ({size//1024} KB)")
            sys.exit(0)
        else:
            print(f"\n  ✗  File too small ({size} bytes), trying next mirror...")
            os.remove(dest)
    except Exception as e:
        print(f"\n  ✗  Failed: {e}")

print("""
All mirrors failed. Manual download instructions:
  1. Open: https://github.com/opencv/opencv_zoo/tree/main/models/face_detection_yunet
  2. Click 'face_detection_yunet_2023mar.onnx' → Download
  3. Place it in your  assets/  folder
  4. Re-run your app
""")

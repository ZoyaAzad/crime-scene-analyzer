"""
Run once: python download_body_models.py
Downloads fullbody and upperbody Haar cascades into assets/
"""
import urllib.request, os

os.makedirs("assets", exist_ok=True)

files = {
    "assets/haarcascade_fullbody.xml": (
        "https://github.com/opencv/opencv/raw/master/data/haarcascades/haarcascade_fullbody.xml"
    ),
    "assets/haarcascade_upperbody.xml": (
        "https://github.com/opencv/opencv/raw/master/data/haarcascades/haarcascade_upperbody.xml"
    ),
}

def progress(count, block, total):
    if total > 0:
        print(f"\r  {min(count*block*100//total, 100)}%", end="", flush=True)

for dest, url in files.items():
    if os.path.exists(dest):
        print(f"  already exists: {dest}"); continue
    print(f"  downloading {dest} ...")
    urllib.request.urlretrieve(url, dest, reporthook=progress)
    print(f"\r  OK  {dest}  ({os.path.getsize(dest)//1024} KB)")

print("\nDone.")
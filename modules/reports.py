import cv2
import os
from datetime import datetime

def save_report(original, processed, findings: list):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("reports", exist_ok=True)

    # Save processed image
    img_path = f"reports/evidence_{timestamp}.png"
    cv2.imwrite(img_path, processed)

    # Save text log
    log_path = f"reports/findings_{timestamp}.txt"
    with open(log_path, "w") as f:
        f.write("=" * 40 + "\n")
        f.write("  TRACELENS — FORENSIC ANALYSIS REPORT\n")
        f.write("=" * 40 + "\n")
        f.write(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-" * 40 + "\n")
        f.write("FINDINGS:\n")
        for finding in findings:
            f.write(f"  > {finding}\n")
        f.write("=" * 40 + "\n")

    return img_path, log_path
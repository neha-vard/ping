#!/usr/bin/env python3
"""
capture_and_alert.py
  • Live mode  : grab a frame from PiCamera2 every loop
  • Test mode  : grab a random image file from ./test-images
"""

import argparse
import os
import random
import time
from pathlib import Path
import cv2

from socketio import Client

# --- your helpers -----------------------------------------------------------
from detect import detect_face, detect_person
from known_model import predict
from unknown_model import predict_person

# Optional (only needed in live mode)
try:
    from picamera2 import Picamera2
except ImportError:
    Picamera2 = None          # Avoid import error on non‑Pi dev machines
# ---------------------------------------------------------------------------


def save_image(image: "ndarray", directory: str, prefix: str) -> str:
    """Saves an image to the specified directory with a timestamp-based filename."""
    if image is not None and image.size > 0:
        os.makedirs(directory, exist_ok=True)
        timestamp = int(time.time())
        filename = f"{prefix}_{timestamp}.jpg"
        filepath = os.path.join(directory, filename)
        cv2.imwrite(filepath, image)
        print(f"Saved image: {filepath}")
        return filepath
    return ""

# Function to grab one frame from PiCamera2 and save it
def get_frame_live() -> "ndarray | None":
    """Grab one RGB frame from PiCamera2 and save it."""
    if Picamera2 is None:
        print("PiCamera2 not available on this machine.")
        return None

    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()
    frame = picam2.capture_array()
    picam2.close()

    # Save the image to a folder and return the filepath along with the image
    if frame is not None:
        filepath = save_image(frame, "captured_images", "live_frame")
        return frame, filepath
    return None, ""

def get_frame_test(test_dir: Path) -> "ndarray | None":
    """Pick a random image file (jpg/png) from test_dir and load it with cv2."""
    files = [p for p in test_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}]
    if not files:
        print(f"No test images found in {test_dir}")
        return None
    img_path = random.choice(files)
    print(f"[TEST MODE] Using {img_path}")
    return img_path, cv2.imread(str(img_path))  # returns ndarray (BGR)


def main(test_mode: bool, test_dir: Path):
    # --- connect socket -----------------------------------------------------
    socket = Client()
    socket.connect("http://localhost:8080")

    get_frame = get_frame_test if test_mode else get_frame_live

    while True:
        img_path, image = get_frame(test_dir) if test_mode else get_frame()
        if image is None:
            time.sleep(5)
            continue

        # ---------- Face pipeline -------------------------------------------
        if detect_face(image) != -1:
            result = predict(img_path)
            if result != "No matches found.":
                msg = f"{result} is at the door!"
                socket.emit("alert", {"message": msg})
                print("Alert sent:", msg)
                time.sleep(10)
                continue

        # ---------- Person / occupation pipeline ---------------------------
        if detect_person(image):
            occ = predict_person(img_path)
            if occ != "unknown":
                msg = f"Unknown visitor! Identified as a {occ}."
                socket.emit("alert", {"message": msg})
                print("Alert sent:", msg)
                time.sleep(5)
                continue

        # ---------- Fallback ------------------------------------------------
        socket.emit("alert", {"message": "Unknown visitor!"})
        print("Alert sent: Unknown visitor!")
        time.sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ping capture & alert loop")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run in test mode: pick random images from ./test-images",
    )
    parser.add_argument(
        "--test-dir",
        default="test-images",
        help="Directory containing test images (used only with --test)",
    )
    args = parser.parse_args()
    main(test_mode=args.test, test_dir=Path(args.test_dir))

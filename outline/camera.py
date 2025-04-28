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
import picar_4wd as fc

from socketio import Client
import asyncio

# --- your helpers -----------------------------------------------------------
from detect import detect_face, detect_person
from known_model import predict
from unknown_model import predict_person
# ---------------------------------------------------------------------------

calibrating_up = True
offset_from_center = 0
calibration_count = 0

# Optional (only needed in live mode)
try:
    from picamera2 import Picamera2
except ImportError as e:
    print(f"[ImportError] could not load Picamera2: {e}")
    Picamera2 = None          # Avoid import error on non‑Pi dev machines

def brighten_image_adaptive(image: "ndarray", target_brightness: float = 130.0) -> "ndarray":
    """
    Brightens the image adaptively so that its average brightness reaches the target.
    - target_brightness: float between 0–255 (typical midtone target: 120–150)
    """
    if image is None:
        return None

    # Convert to grayscale to compute brightness
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = gray.mean()

    # If already bright enough, return original
    if mean_brightness >= target_brightness:
        return image

    # Scale factor (limited to avoid overexposure)
    factor = min(target_brightness / mean_brightness, 2.0)

    # Adjust brightness using convertScaleAbs
    return cv2.convertScaleAbs(image, alpha=factor, beta=0)

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
        frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        filepath = save_image(frame, "captured_images", "live_frame")
        print("returning proper image to program")
        return filepath, frame
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

def calibrate_upwards():
    fc.turn_right(1)
    time.sleep(0.2)
    fc.stop()

def calibrate_downwards():
    fc.turn_left(1)
    time.sleep(0.2)
    fc.stop()

def recalibrate():
    global offset_from_center
    global calibrating_up
    global calibration_count

    while offset_from_center > 0.0:
        calibrate_downwards()
        offset_from_center -= 0.2
    while offset_from_center < 0.0:
        calibrate_upwards()
        offset_from_center += 0.2
    
    calibrating_up = True
    offset_from_center = 0
    calibration_count = 0

def main(test_mode: bool, test_dir: Path):
    global offset_from_center
    global calibrating_up
    global calibration_count

    # --- connect socket -----------------------------------------------------
    socket = Client()
    socket.connect("http://localhost:8080")

    get_frame = get_frame_test if test_mode else get_frame_live

    while True:
        img_path, image = get_frame(test_dir) if test_mode else get_frame()
        
        if image is None:
            time.sleep(5)
            continue

        detect_face_confidence = detect_face(image)
        print(detect_face_confidence)

        # ---------- Face pipeline -------------------------------------------
        while detect_face_confidence == -1 or detect_face_confidence < 0.65:
            if calibrating_up:
                calibrate_upwards()
                offset_from_center += 0.2
                calibration_count += 1
                if calibration_count >= 3:
                    calibrating_up = False
                    calibration_count = 0
            else:
                calibrate_downwards()
                offset_from_center -= 0.2
                calibration_count += 1
                if calibration_count >= 5:
                    calibrating_up = True
                    calibration_count = 0

            img_path, image = get_frame(test_dir) if test_mode else get_frame()
            detect_face_confidence = detect_face(image)
            print(detect_face_confidence)
            time.sleep(2)
        
        recalibrate()

        print("check image against known people")
        img_bright = brighten_image_adaptive(image)
        img_bright_path = save_image(img_bright, "brightened_images", "brightened")
        result = asyncio.run(predict(img_bright_path))
        if result != "No matches found.":
            msg = f"{result} is at the door!"
            socket.emit("alert", {"message": msg})
            print("Alert sent:", msg)
            continue

        # ---------- Person / occupation pipeline ---------------------------
        if detect_person(image):
            print("check image occupation")
            occ = predict_person(img_path)
            if occ != "unknown":
                msg = f"Unknown visitor! Identified as a {occ}."
                socket.emit("alert", {"message": msg})
                print("Alert sent:", msg)
                continue

        # ---------- Fallback ------------------------------------------------
        socket.emit("alert", {"message": "Unknown visitor!"})
        print("Alert sent: Unknown visitor!")


if __name__ == "__main__":
    try:
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
    finally:
        fc.stop()

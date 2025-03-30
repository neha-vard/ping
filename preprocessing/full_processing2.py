import cv2
import mediapipe as mp
from picamera2 import Picamera2
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import argparse
import os
import time

def save_image(image: np.ndarray, directory: str, prefix: str):
    """Saves an image to the specified directory with a timestamp-based filename."""
    if image is not None and image.size > 0:
        os.makedirs(directory, exist_ok=True)
        timestamp = int(time.time())
        filename = f"{prefix}_{timestamp}.jpg"
        filepath = os.path.join(directory, filename)
        cv2.imwrite(filepath, image)
        print(f"Saved {prefix} image: {filepath}")


def process_face_image(image):
    """
    Detects and aligns a face using MediaPipe Face Detection and Face Mesh.
    
    Returns:
        np.ndarray: Cropped and aligned face image, or None if no face is detected.
    """
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_face_detection = mp.solutions.face_detection
    mp_face_mesh = mp.solutions.face_mesh

    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection, \
         mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1) as face_mesh:
        
        results = face_detection.process(rgb_image)

        if results.detections:
            mesh_results = face_mesh.process(rgb_image)

            if mesh_results.multi_face_landmarks:
                for face_landmarks in mesh_results.multi_face_landmarks:
                    left_eye = face_landmarks.landmark[33]
                    right_eye = face_landmarks.landmark[263]

                    h, w, _ = image.shape
                    left_eye_coords = (int(left_eye.x * w), int(left_eye.y * h))
                    right_eye_coords = (int(right_eye.x * w), int(right_eye.y * h))

                    delta_y = right_eye_coords[1] - left_eye_coords[1]
                    delta_x = right_eye_coords[0] - left_eye_coords[0]
                    angle = np.degrees(np.arctan2(delta_y, delta_x))

                    center = (w // 2, h // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                    rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h))

                    rotated_rgb_image = cv2.cvtColor(rotated_image, cv2.COLOR_BGR2RGB)
                    rotated_results = face_detection.process(rotated_rgb_image)

                    if rotated_results.detections:
                        for rotated_detection in rotated_results.detections:
                            bbox = rotated_detection.location_data.relative_bounding_box
                            x, y, w_box, h_box = (
                                max(0, int(bbox.xmin * w)), 
                                max(0, int(bbox.ymin * h)), 
                                min(w, int(bbox.width * w)), 
                                min(h, int(bbox.height * h))
                            )

                            cropped_face = rotated_image[y:y + h_box, x:x + w_box]
                            return cropped_face if cropped_face.size > 0 else None

                    print("Face not detected in rotated image.")
                    return None

                print("Face landmarks not detected.")
                return None

        print("No face detected.")
        return None

def detect_and_crop_person(image: np.ndarray, max_results: int = 5, score_threshold: float = 0.25) -> np.ndarray:
    """
    Detects a person using MediaPipe Object Detector and returns a cropped image.
    
    Returns:
        np.ndarray: Cropped person image, or None if no person is detected.
    """
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    base_options = python.BaseOptions(model_asset_path="efficientdet_lite0.tflite")
    options = vision.ObjectDetectorOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        max_results=max_results,
        score_threshold=score_threshold
    )

    detector = vision.ObjectDetector.create_from_options(options)
    detection_result = detector.detect(mp_image)

    for detection in detection_result.detections:
        category = detection.categories[0]
        if category.category_name == "person":
            bbox = detection.bounding_box
            x, y, w, h = (
                max(0, int(bbox.origin_x)), 
                max(0, int(bbox.origin_y)), 
                min(image.shape[1], int(bbox.width)), 
                min(image.shape[0], int(bbox.height))
            )

            cropped_image = image[y:y+h, x:x+w]
            return cropped_image if cropped_image.size > 0 else None

    return None

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--image', help='Path to an image file for detection.', type=str, default=None)
    args = parser.parse_args()

    if args.image:
        image = cv2.imread(args.image)
        if image is None:
            print(f"Error: Could not load image {args.image}")
            return
    else:
        picam2 = Picamera2()
        picam2.preview_configuration.main.size = (640, 480)
        picam2.preview_configuration.main.format = "RGB888"
        picam2.preview_configuration.align()
        picam2.configure("preview")
        picam2.start()

        image = picam2.capture_array()

    cropped_face = process_face_image(image)
    if cropped_face is not None:
        save_image(cropped_face, "faces", "face")
    
    cropped_person = detect_and_crop_person(image)
    if cropped_person is not None:
        save_image(cropped_person, "people", "person")

if __name__ == '__main__':
    main()

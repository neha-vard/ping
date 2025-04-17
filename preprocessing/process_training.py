import cv2
import mediapipe as mp
import numpy as np
import argparse
import os
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


def save_image(image: np.ndarray, directory: str, prefix: str):
    """Saves an image to the specified directory with a timestamp-based filename."""
    if image is not None and image.size > 0:
        os.makedirs(directory, exist_ok=True)
        timestamp = int(time.time())
        filename = f"{prefix}_{timestamp}.jpg"
        filepath = os.path.join(directory, filename)
        cv2.imwrite(filepath, image)
        print(f"Saved {prefix} image: {filepath}")
        return filepath
    return None


def process_face_image(image):
    """
    Detects and aligns a face using MediaPipe Face Detection and Face Mesh.
    
    Returns:
        np.ndarray: Cropped and aligned face image path, or None if no face is detected.
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
                            if cropped_face.size > 0:
                                return save_image(cropped_face, "faces", "face")
                    print("Face not detected in rotated image.")
        else:
            print("No face detected.")
    return None


def process_and_save_face(image, output_dir, prefix):
    """
    Wrapper to process face and save to a specified directory with a custom prefix.
    """
    result_path = process_face_image(image)
    if result_path:
        result_image = cv2.imread(result_path)
        return save_image(result_image, output_dir, prefix)
    return None


def batch_process_faces(input_dir: str, output_dir: str):
    """
    Processes all image files in a directory and saves cropped face images to output directory.
    """
    supported_extensions = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")
    os.makedirs(output_dir, exist_ok=True)

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_extensions):
            image_path = os.path.join(input_dir, filename)
            image = cv2.imread(image_path)
            if image is None:
                print(f"Warning: Failed to load {filename}")
                continue

            print(f"Processing {filename}...")
            processed_path = process_and_save_face(image, output_dir, os.path.splitext(filename)[0])
            if processed_path is None:
                print(f"No face detected in {filename}")
        else:
            print(f"Skipping unsupported file {filename}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing images to process.')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory to save processed face images.')
    args = parser.parse_args()

    batch_process_faces(args.input_dir, args.output_dir)
import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import argparse
import os
import time

def detect_face(image: np.ndarray) -> float:
    """
    Detects a face using MediaPipe Face Detection and returns the confidence score.
    
    Returns:
        float: The confidence score if a face is detected, -1 if no face is detected.
    """
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_face_detection = mp.solutions.face_detection

    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(rgb_image)

        if results.detections:
            # Return the confidence score of the first detected face
            return results.detections[0].score[0]  # Confidence score of the first detection
        return -1.0  # No face detected, return -1

def detect_person(image: np.ndarray, max_results: int = 5, score_threshold: float = 0.25) -> bool:
    """
    Detects a person using MediaPipe Object Detection.
    
    Returns:
        bool: True if a person is detected, False otherwise.
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
            return True  # Person detected

    return False  # No person detected
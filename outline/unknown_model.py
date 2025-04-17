import time
import os
import tensorflow as tf
import numpy as np
from PIL import Image


MODEL_PATH = "occupation_classifier.tflite"
LABELS = ["courier", "construction_worker", "police_officer", "firefighter"]
IMG_SIZE = (180, 180)
CONFIDENCE_THRESHOLD = 0.7

interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def predict_person(img_path):
    """Simulates model prediction by randomly selecting a label."""
    img = Image.open(img_path).convert("RGB")
    img = img.resize(IMG_SIZE)
    img_array = np.array(img, dtype=np.float32) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)

    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]

    best_idx = np.argmax(predictions)
    confidence = predictions[best_idx]
    if confidence < CONFIDENCE_THRESHOLD:
        prediction = "Unknown"
    else:
        prediction = LABELS[best_idx]

    print("Prediction probabilities:")
    for i, label in enumerate(LABELS):
        print(f"{label}: {predictions[i]*100:.2f}%")
    print(f"Final Prediction: {prediction}")

    os.remove(img_path)
    return prediction
  
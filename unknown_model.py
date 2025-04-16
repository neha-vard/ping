import random
import time

LABELS = ["Fireman", "Police Officer", "Delivery Person", "unknown"]

def predict_person(img_path):
    """Simulates model prediction by randomly selecting a label."""
    print(f"Simulating prediction for: {img_path}")
    time.sleep(1)  # Simulate model inference delay
    prediction = random.choice(LABELS)  # Pick a random label
    print(f"Prediction: {prediction}")
    return prediction
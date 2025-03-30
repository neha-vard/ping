import random
import time

LABELS = ["Neha", "Anya", "Priyanka", "Vy", "unknown"]

def predict(img_path):
    """Simulates model prediction by randomly selecting a label."""
    print(f"Simulating prediction for: {img_path}")
    time.sleep(1)  # Simulate model inference delay
    prediction = random.choice(LABELS)  # Pick a random label
    print(f"Prediction: {prediction}")
    return prediction

def register(img_path):
    """Simulate the registration of a new image (e.g., add to model, database, etc.)."""
    print(f"Registering image: {img_path}")
    
    # You can add logic here to process the image or update your model
    # For now, we just return a success message
    return f"Image registered successfully: {img_path}"

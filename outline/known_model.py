import base64
import requests

def predict(img_path):
    """Model prediction using DeepFace Facenet model."""
    print(f"Simulating prediction for: {img_path}")
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    url = "https://us-central1-cs437-deepface.cloudfunctions.net/run_deepface"
    payload = {
        "image_base64": image_base64
    }

    response = requests.post(url, json=payload)
    match = response.json()["match"]
    if match == None:
        return "No matches found."
    else:
        return match
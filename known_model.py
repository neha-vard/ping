import base64
import httpx
import asyncio

async def predict(img_path):
    """Model prediction using DeepFace Facenet model."""
    print(f"Prediction for: {img_path}")
    with open(img_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    url = "https://us-central1-cs437-deepface.cloudfunctions.net/run_deepface"
    payload = {
        "image_base64": image_base64
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=400)
        match = response.json()["match"]
        return match if match else "No matches found."
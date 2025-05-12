from google.cloud import storage
import base64
import os

BUCKET_NAME = "deepface-dataset"

def add_image(request):
    request_json = request.get_json()
    person = request_json.get("person")
    image_data = request_json.get("image_base64")

    if not person or not image_data:
        return {"error": "Missing person or image data"}, 400

    image_bytes = base64.b64decode(image_data)
    filename = f"{person}/image_{str(hash(image_data))[:6]}.jpg"

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"known_people_dataset/{filename}")
    blob.upload_from_string(image_bytes, content_type='image/jpeg')

    return {"message": f"Image added to {person}'s folder"}

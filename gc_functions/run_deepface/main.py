from google.cloud import storage
import os
import uuid
import base64
import tempfile
import pandas as pd

BUCKET_NAME = "deepface-dataset"
KNOWN_PEOPLE_BUCKET_PATH = "known_people_dataset"

def run_deepface(request):
    from deepface import DeepFace

    print("received request")

    request_json = request.get_json()
    image_base64 = request_json.get("image_base64")

    if not image_base64:
        return {"error": "Missing image"}, 400

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    db_root_dir = tempfile.mkdtemp()
    query_img_dir = tempfile.mkdtemp()

    db_path = os.path.join(db_root_dir, "db")
    os.makedirs(db_path, exist_ok=True)

    query_img_filename = f"{uuid.uuid4()}.jpg"
    query_img_path = os.path.join(query_img_dir, query_img_filename)

    with open(query_img_path, "wb") as f:
        f.write(base64.b64decode(image_base64))

    print(f"query image saved to: {query_img_path}")

    print("downloading images")
    blobs = list(bucket.list_blobs(prefix=KNOWN_PEOPLE_BUCKET_PATH))
    image_count = 0
    for blob in blobs:
        if blob.name.endswith(".jpg"):
            relative_path = os.path.relpath(blob.name, KNOWN_PEOPLE_BUCKET_PATH)
            local_path = os.path.join(db_path, relative_path)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            blob.download_to_filename(local_path)
            image_count += 1

    print("running deepface")
    results = DeepFace.find(
        img_path=query_img_path,
        db_path=db_path,
        model_name='Facenet',
        enforce_detection=False
    )
    print("done")

    if isinstance(results, list) and len(results) > 0 and not results[0].empty:
        df = results[0]
    elif isinstance(results, pd.DataFrame) and not results.empty:
        df = results
    else:
        print("No match found.")
        return {"match": None}

    query_basename = os.path.basename(query_img_path)
    df_filtered = df[df["identity"].apply(lambda x: os.path.basename(x) != query_basename)]

    if df_filtered.empty:
        print("no matches")
        return {"match": None}

    top_match = df_filtered.iloc[0]
    match_path = os.path.realpath(top_match["identity"])
    print(f"Match path: {match_path}")
    print(f"Distance: {top_match.get('distance')}")

    relative_path = os.path.relpath(match_path, db_path)
    parts = relative_path.split(os.sep)

    if float(top_match.get("distance", 1.0)) < 0.4 and len(parts) >= 2:
        person_name = parts[0]
        print(f"Match accepted: {person_name}")
        return {"match": person_name}
    else:
        print("Match rejected")
        return {"match": None}

import os
from deepface import DeepFace

def predict(img_path):
    """Model prediction using DeepFace Facenet model."""
    print(f"Simulating prediction for: {img_path}")
    data_dir = "known_people_dataset2"
    results = DeepFace.find(img_path=img_path, db_path=data_dir, model_name='Facenet')
    # os.remove(img_path)

    if results and not results[0].empty:
        top_match = results[0].iloc[0]
        match_path = top_match["identity"]
        person_name = os.path.basename(os.path.dirname(match_path))
        if float(top_match["distance"]) < 0.4:
            print(top_match["distance"])
            print(f"Prediction: {person_name}")
            return person_name
        else:
            return "No matches found."
    else:
        return "No matches found."

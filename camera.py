import time
from preprocessing import process_face_image, detect_and_crop_person
from known_model import predict
from unknown_model import predict_person
from socketio import Client
from picamera2 import Picamera2

# Connect to WebSocket server
socket = Client()
socket.connect("http://localhost:5000")

if __name__ == "__main__":
    while True:
        picam2 = Picamera2()
        picam2.preview_configuration.main.size = (640, 480)
        picam2.preview_configuration.main.format = "RGB888"
        picam2.preview_configuration.align()
        picam2.configure("preview")
        picam2.start()
        image = picam2.capture_array()

        # Check for face
        face_path = process_face_image(image)
        if face_path is None:
            time.sleep(5)
            continue

        result = predict(face_path)
        if result != "unknown": # Visitor is known
            message = f"{result} is at the door!"
            socket.emit("alert", {"message": message})
            print(f"Alert sent: {message}")
            time.sleep(10)
            continue

        # Identify occupation
        person_path = detect_and_crop_person(image)
        if person_path is None:
            time.sleep(5)
            continue

        result2 = predict_person(person_path)
        if result != "unknown": # Visitor is classified by occupation
            message = f"Unknown visitor! Identified as a {result2}."
            socket.emit("alert", {"message": message})
            print(f"Alert sent: {message}")
            time.sleep(5)
            continue
        
        message = f"Unknown visitor!"
        socket.emit("alert", {"message": message})
        print(f"Alert sent: {message}")
        time.sleep(5)
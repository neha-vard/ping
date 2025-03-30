import time
from preprocess import preprocess_image
from model import predict
from socketio import Client

# Connect to WebSocket server
socket = Client()
socket.connect("http://localhost:5000")

def capture_and_process():
    """Simulates capturing an image, processing, and predicting."""
    img_path = f"dummy_image_{int(time.time())}.jpg"
    print(f"Simulating image capture: {img_path}")

    # Simulated preprocessing
    processed_path = preprocess_image(img_path)

    # Simulated model prediction
    result = predict(processed_path)

    # Send alert with detected person (or unknown visitor)
    message = f"Detected: {result}" if result != "unknown" else "Unknown visitor detected!"
    socket.emit("alert", {"message": message, "image": processed_path})
    print(f"Alert sent: {message}")

if __name__ == "__main__":
    while True:
        capture_and_process()
        time.sleep(5)  # Run every 5 seconds (shorter for testing)

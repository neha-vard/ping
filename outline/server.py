import base64
from io import BytesIO
from PIL import Image
from flask import Flask
from flask_socketio import SocketIO, emit
import os
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def index():
    return {"status": "Server is running"}

# SocketIO event handler for alert (visitor alerts)
@socketio.on('alert')
def handle_alert(data):
    print(f"Alert received: {data['message']}")
    # You can send the alert back to the frontend if needed
    emit("alert", {"message": data["message"]}, broadcast=True)

@socketio.on('upload_image_bytes')
def handle_image_bytes_upload(data):
    name = data.get('name')
    image_data = data.get('imageData')

    if not name or not image_data:
        emit('image_registration_result', {'message': 'Missing name or image data'})
        return

    try:
        # Decode base64 to bytes
        image_bytes = base64.b64decode(image_data)

        # Convert bytes to an image file using PIL
        image = Image.open(BytesIO(image_bytes))

        # Save the image to disk (optional)
        save_path = os.path.join("known_people_dataset", f"{name}", f"{datetime.now().timestamp()}.jpg")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        image.save(save_path)

        # Emit result
        emit('image_registration_result', {'message': f"{save_path}"}, broadcast=True)

    except Exception as e:
        print("Error processing image upload:", e)
        emit('image_registration_result', {'message': 'Failed to process image.'})


if __name__ == "__main__":
    print("Starting WebSocket server...")
    socketio.run(app, host="0.0.0.0", port=8080)

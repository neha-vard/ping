from flask import Flask
from flask_socketio import SocketIO, emit
import requests

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
        # Save the image to cloud
        url = "https://us-central1-cs437-deepface.cloudfunctions.net/add_image"
        payload = {
            "person": name,
            "image_base64": image_data
        }

        # Emit result
        response = requests.post(url, json=payload)
        message = response.json()["message"]
        emit('image_registration_result', {'message': f"{message}"}, broadcast=True)

    except Exception as e:
        print("Error processing image upload:", e)
        emit('image_registration_result', {'message': 'Failed to process image.'})


if __name__ == "__main__":
    print("Starting WebSocket server...")
    socketio.run(app, host="0.0.0.0", port=8080)

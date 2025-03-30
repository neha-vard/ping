from flask import Flask
from flask_socketio import SocketIO, emit
import os
from model import register

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

# SocketIO event handler for image path upload (register new image)
@socketio.on('upload_image')
def handle_image_upload(data):
    image_path = data['imagePath']
    
    if image_path:
        print(f"Received image path: {image_path}")
        
        # Call register function from model.py with the image path
        result = register(image_path)
        
        # Emit a new event for image registration result
        emit('image_registration_result', {'message': f"{result}"}, broadcast=True)
    else:
        print("No image path found in the data.")

if __name__ == "__main__":
    print("Starting WebSocket server...")
    socketio.run(app, host="0.0.0.0", port=5000)

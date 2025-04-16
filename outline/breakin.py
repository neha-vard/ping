import random
import time
from socketio import Client

# Connect to the WebSocket server
socket = Client()
socket.connect("http://localhost:5000")

def simulate_sensor_reading():
    """Returns a simulated sensor reading (e.g., distance or IR value)."""
    # Normal baseline range is around 500 ± 10
    return random.randint(300, 500)

def is_unusual_pattern(prev, curr):
    """Detects if the difference between readings is unusually high."""
    return abs(curr - prev) > 100  # e.g., sudden spike/dip

def breakin_monitor():
    print("Starting break-in monitor...")

    last_reading = simulate_sensor_reading()
    time.sleep(0.5)

    while True:
        reading = simulate_sensor_reading()

        print(f"Sensor reading: {reading}")
        
        if is_unusual_pattern(last_reading, reading):
            message = "Possible break-in detected!"
            print("Alert sent:", message)
            socket.emit("alert", {"message": message})
            time.sleep(10)  # throttle alerting
        else:
            time.sleep(1)

        last_reading = reading

if __name__ == "__main__":
    breakin_monitor()

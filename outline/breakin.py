import random
import time
from socketio import Client
import RPi.GPIO as GPIO
import time, math
import threading
import picar_4wd as fc
import random
from socketio import Client
from datetime import datetime

PHOTO_SENSOR_PIN = 25 

class Speed():
    def __init__(self, pin):
        self.speed_counter = 0
        self.speed = 0
        self.last_time = 0
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.timer_flag = True
        self.timer = threading.Thread(target=self.fun_timer, name="Thread1")

    def start(self):
        self.timer.start()
        # print('speed start')

    def print_result(self, s):
        print("Rising: {}; Falling: {}; High Level: {}; Low Level: {}".format(s.count("01"), s.count("10"), s.count("1"), s.count("0")))

    def fun_timer(self):
        while self.timer_flag:
            l = ""
            for _ in range(100):
                l += str(GPIO.input(self.pin))
                time.sleep(0.001)
            # self.print_result(l)
            count = (l.count("01") + l.count("10")) / 2
            rps = count / 20.0 * 10
            self.speed = round(2 * math.pi * 3.3 * rps, 2)


    def __call__(self):
        return self.speed

    def deinit(self):
        self.timer_flag = False
        self.timer.join()


# Connect to the WebSocket server
socket = Client()
socket.connect("http://localhost:8080")

def count_attempts(pin, duration=1.0):
    """Count how many times the signal flips in a given duration (seconds)."""
    start_time = time.time()
    last_value = GPIO.input(pin)
    attempts = 0

    while time.time() - start_time < duration:
        current_value = GPIO.input(pin)
        if current_value != last_value:
            attempts += 1
            last_value = current_value
        time.sleep(0.0001)  # Sample every millisecond
    return attempts



def is_night_time():
    """Returns True if the current time is between 1 AM and 5 AM."""
    #BY THE WAY, THE PI IS NOT IN CST!!!! so u can j manually set it
    current_time = datetime.now()
    # print("Current system time:", current_time.strftime("%Y-%m-%d %H:%M:%S")) 
    return 1 <= current_time.hour < 5 
    # return True

def breakin_monitor():
    print("Starting break-in monitor...")
    speed_sensor = Speed(PHOTO_SENSOR_PIN)
    speed_sensor.start()

    last_reading = GPIO.input(PHOTO_SENSOR_PIN)
    # time.sleep(0.5)

    while True:
        reading = GPIO.input(PHOTO_SENSOR_PIN)
        # print(f"Sensor reading: {reading}")

        if reading != last_reading:
            print("Sensor interrupted!")

            attempts = count_attempts(PHOTO_SENSOR_PIN, duration=1.0)
            print(f"attempts in 1s: {attempts}")

            if attempts > 8:
                message = "Fast movement detected — possible break-in!"
                print("Alert sent:", message)
                socket.emit("alert", {"message": message})
                time.sleep(2)
            elif is_night_time():
                message = "Unusual activity detected between 1 AM and 5 AM! Someone might be trying to break in."
                print("Alert sent:", message)
                socket.emit("alert", {"message": message})
                time.sleep(2)  # it was getting annoying
            else:
                print("Detection: Someone is at the door!")

        last_reading = reading
        time.sleep(1)

if __name__ == "__main__":
    breakin_monitor()

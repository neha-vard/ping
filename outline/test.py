import RPi.GPIO as GPIO
import time

LEFT_ENCODER_PIN = 12  # D6
RIGHT_ENCODER_PIN = 13  # D7
PULSES_PER_REV = 20  # Change if your wheel has a different slot count

left_count = 0
right_count = 0

def left_callback(channel):
    global left_count
    left_count += 1

def right_callback(channel):
    global right_count
    right_count += 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(LEFT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RIGHT_ENCODER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(LEFT_ENCODER_PIN, GPIO.BOTH, callback=left_callback)
GPIO.add_event_detect(RIGHT_ENCODER_PIN, GPIO.BOTH, callback=right_callback)

try:
    while True:
        left_count = 0
        right_count = 0
        time.sleep(1)  # Measure over 1 second
        left_rpm = (left_count / PULSES_PER_REV) * 60
        right_rpm = (right_count / PULSES_PER_REV) * 60
        print(f"Left RPM: {left_rpm:.2f}, Right RPM: {right_rpm:.2f}")
except KeyboardInterrupt:
    print("Stopping...")
finally:
    GPIO.cleanup()
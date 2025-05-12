import picar_4wd as fc
import time

speed = 1
counter = 0

def main():
    global counter
    while True:
        fc.turn_left(speed)
        time.sleep(0.2)
        break

if __name__ == "__main__":
    try: 
        main()
    finally: 
        fc.stop()

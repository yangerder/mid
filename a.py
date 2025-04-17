import RPi.GPIO as GPIO
import time

TRIG = 23
ECHO = 24
LED_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time, end_time = 0, 0

    while GPIO.input(ECHO) == 0:
        start_time = time.time()
    while GPIO.input(ECHO) == 1:
        end_time = time.time()

    duration = end_time - start_time
    distance = (duration * 34300) / 2
    
    return distance

try:
    while True:
        distance = measure_distance()
        print(f"distance: {distance:.2f} cm")

        if distance < 50:
            GPIO.output(LED_PIN, True)
            time.sleep(0.1)
            GPIO.output(LED_PIN, False)
            time.sleep(0.1)
        elif distance < 100:
            GPIO.output(LED_PIN, True)
            time.sleep(0.5)
            GPIO.output(LED_PIN, False)
            time.sleep(0.5)
        else:
            GPIO.output(LED_PIN, False)

        time.sleep(0.2)

except KeyboardInterrupt:
    GPIO.cleanup()
    print("end")

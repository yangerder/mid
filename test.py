import RPi.GPIO as GPIO
import time

# Set GPIO pin (change this if needed)
LED_PIN = 12  # Update based on your wiring

# Set GPIO mode and configure the LED pin as output
GPIO.setmode(GPIO.BOARD)  # Change to GPIO.BCM if using BCM numbering
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    while True:
        print("LED is on")
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED on
        time.sleep(1)  # Wait for 1 second
        
        print("LED is off")
        GPIO.output(LED_PIN, GPIO.LOW)  # Turn LED off
        time.sleep(1)  # Wait for 1 second

except KeyboardInterrupt:
    print("\nStopped by user.")

finally:
    GPIO.output(LED_PIN, GPIO.LOW)  # Ensure LED is off before exit
    GPIO.cleanup()  # Reset GPIO settings

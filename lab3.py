import speech_recognition as sr
import RPi.GPIO as GPIO
import time
from gtts import gTTS
import os

def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language='en-US')
        print(f"Recognized: {text}")
        return text.lower()
    except Exception as e:
        print("Speech recognition failed:", e)
        return ""

def measure_distance():
    TRIG = 23
    ECHO = 24
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    GPIO.output(TRIG, False)
    time.sleep(0.5)

    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 17150, 2)
    print(f"Measured distance: {distance} cm")

    GPIO.cleanup()
    return distance

def speak_result(distance):
    text = f"The distance is {distance} centimeters"
    tts = gTTS(text=text, lang='en')
    tts.save("distance.mp3")
    os.system("play distance.mp3 > /dev/null 2>&1")

if __name__ == "__main__":
    command = recognize_speech()
    if "measure" in command or "distance" in command:
        dist = measure_distance()
        speak_result(dist)
    else:
        print("Invalid command. Please say something like 'measure distance'.")

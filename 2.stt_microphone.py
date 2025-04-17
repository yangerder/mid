import speech_recognition as sr
import os
from ctypes import *
from contextlib import contextmanager

# Suppress ALSA error messages on Raspberry Pi
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt): pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

# Set your OpenAI API Key
os.environ["OPENAI_API_KEY"] =

recognizer = sr.Recognizer()

with noalsaerr(), sr.Microphone() as source:
    print("Calibrating microphone...")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    print("Listening...")
    audio = recognizer.listen(source)

try:
    print("Whisper API result:")
    print(recognizer.recognize_openai(audio))
except sr.UnknownValueError:
    print("Could not understand the audio.")
except sr.RequestError as e:
    print(f"OpenAI Whisper API error: {e}")

import speech_recognition as sr
import pyttsx3
import subprocess
import keyboard
import time
import random
import os
from datetime import datetime
from PIL import ImageGrab  # used to take screenshots without invoking OS overlay

WAKE_WORD = "jarvis"

from TTS.api import TTS
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch").to(device)

import uuid
import os
from TTS.api import TTS
import simpleaudio as sa

tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch")

def speak(text):
    temp_file = f"voice_{uuid.uuid4().hex}.wav"
    tts.tts_to_file(text=text, file_path=temp_file)

    wave_obj = sa.WaveObject.from_wave_file(temp_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # wait until finished

    os.remove(temp_file)

WAKE_RESPONSES = [
    "Yes sir?",
    "I'm listening.",
    "Go ahead.",
    "What can I do for you?",
    "At your service.",
]

def random_wake():
    """Speak one random wake response."""
    speak(random.choice(WAKE_RESPONSES))

ENDING_RESPONSES = [
    "Task complete.",
    "All done.",
    "Mission accomplished.",
    "That’s taken care of.",
    "Finished, sir.",
]

def random_end():
    """Speak one random ending response."""
    speak(random.choice(ENDING_RESPONSES))

def _screenshot_filename():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = os.path.join(os.path.expanduser("~"), "Pictures", "JarvisScreenshots")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, f"screenshot_{now}.png")

def clip_that():
    speak("Clipping that")
    keyboard.press_and_release('ctrl+shift+s')
    random_end()

def launch_chrome():
    speak("Launching Chrome")
    time.sleep(0.1)
    try:
        subprocess.Popen("chrome")
    except Exception as e:
        speak("Failed to launch Chrome.")
        print("launch_chrome error:", e)
        return
    time.sleep(0.2)
    random_end()

def screenshot_capture():
    """
    Take a screenshot *without* calling the OS snip overlay.
    This uses PIL.ImageGrab so Windows' snip UI won't steal audio.
    """
    speak("Taking screenshot")   # speak FIRST
    time.sleep(0.05)

    try:
        img = ImageGrab.grab(all_screens=True) if hasattr(ImageGrab, "graball") else ImageGrab.grab()
        path = _screenshot_filename()
        img.save(path)
        print("Saved screenshot to", path)
    except Exception as e:
        speak("Screenshot failed.")
        print("screenshot_capture error:", e)
        return

    time.sleep(0.1)
    random_end()

def say_hello():
    speak("Hello sir!")
    random_end()


COMMANDS = {
    "open chrome": launch_chrome,
    "take screenshot": screenshot_capture,
    "screenshot": screenshot_capture,
    "hello": say_hello,
    "clip that": clip_that,
}

recognizer = sr.Recognizer()
mic = sr.Microphone()

def listen(timeout=None, phrase_time_limit=None):
    """
    Listen and return lower-cased recognized text.
    timeout: maximum seconds to wait for phrase to start (None = wait indefinitely)
    phrase_time_limit: max seconds for phrase itself (None = unlimited)
    """
    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return ""
    try:
        return recognizer.recognize_google(audio).lower()
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print("Speech recognition request error:", e)
        return ""

def main():
    print("Listening for wake word...")
    while True:
        text = listen(timeout=3, phrase_time_limit=4)
        if not text:
            continue

        print("Heard:", text)
        if WAKE_WORD in text:
            random_wake() 
            command = listen(timeout=5, phrase_time_limit=6)
            print("Command:", command)

            matched = False
            if command:
                for key_phrase in COMMANDS:
                    if key_phrase in command:
                        COMMANDS[key_phrase]()   # call handler
                        matched = True
                        break

            if not matched:
                speak("Sorry, I don't know that command.")
        time.sleep(0.1)


if __name__ == "__main__":
    main()


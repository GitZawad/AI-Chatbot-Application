import pyttsx3
import threading

def speak(text):
    def _speak():
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    
    # Run in a separate thread to avoid blocking the GUI
    thread = threading.Thread(target=_speak)
    thread.start()
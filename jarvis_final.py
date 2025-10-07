import speech_recognition as sr
import pyttsx3
import sounddevice as sd
import numpy as np
import tempfile
import wave
import datetime
import webbrowser
import wikipedia
import pywhatkit
import pyjokes
import os
import requests
import time

# ---- Text to Speech ----
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# ---- Record audio to temporary WAV ----
already_listening = False  # Flag to prevent repeated "Listening..."

def record_audio(duration=5, fs=44100):
    global already_listening
    if not already_listening:
        print("Listening...")
        speak("I am listening")
        already_listening = True

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    with wave.open(temp_file.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes((recording * 32767).astype(np.int16).tobytes())
    
    already_listening = False  # Reset flag after recording
    return temp_file.name

# ---- Speech Recognition ----
def listen():
    r = sr.Recognizer()
    audio_file = record_audio()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)
    try:
        command = r.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except:
        speak("Sorry, I could not understand.")
        return ""

# ---- Reminders ----
reminders = []

def set_reminder():
    speak("What should I remind you about?")
    task = listen()
    speak("At what time? Please say in HH:MM format")
    time_str = listen()
    reminders.append((task, time_str))
    speak(f"Reminder set for {task} at {time_str}")

def check_reminders():
    now = datetime.datetime.now().strftime("%H:%M")
    for task, t in reminders:
        if t == now:
            speak(f"Reminder: {task}")
            reminders.remove((task, t))

# ---- File Search / Open ----
def open_file_or_folder():
    speak("Please tell the path of the file or folder:")
    path = input("Enter path: ")
    if os.path.exists(path):
        os.startfile(path)
        speak(f"Opening {path}")
    else:
        speak("Sorry, the file or folder does not exist.")

# ---- Commands ----
def process_command(query):
    if "hello" in query:
        speak("Hello sir, nice to meet you.")
    elif "time" in query:
        now = datetime.datetime.now()
        speak(f"The time is {now.hour} {now.minute}")
    elif "date" in query:
        today = datetime.datetime.today()
        speak(f"Today's date is {today.day} {today.strftime('%B')} {today.year}")
    elif "wikipedia" in query:
        speak("Searching Wikipedia...")
        query = query.replace("wikipedia", "")
        try:
            result = wikipedia.summary(query, sentences=2)
            speak(result)
        except:
            speak("Sorry, no results found.")
    elif "open youtube" in query:
        webbrowser.open("https://www.youtube.com")
    elif "open google" in query:
        webbrowser.open("https://www.google.com")
    elif "play song" in query or "play music" in query:
        speak("Which song do you want to play?")
        song = listen()
        pywhatkit.playonyt(song)
    elif "calculator" in query:
        speak("Tell me the operation, for example 5 + 3")
        operation = listen()
        try:
            result = eval(operation)
            speak(f"The result is {result}")
        except:
            speak("Invalid operation.")
    elif "joke" in query:
        joke = pyjokes.get_joke()
        speak(joke)
    elif "reminder" in query:
        set_reminder()
    elif "open app" in query:
        speak("Which app should I open?")
        app = listen()
        try:
            os.startfile(app)
            speak(f"Opening {app}")
        except:
            speak(f"Sorry, I cannot open {app}")
    elif "news" in query:
        try:
            url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=78493088c7134e0a8b2e783ffb1e57b8"
            response = requests.get(url).json()
            articles = response["articles"][:3]
            speak("Here are the top news headlines:")
            for article in articles:
                speak(article["title"])
        except:
            speak("Sorry, cannot fetch news right now.")
    elif "open file" in query or "open folder" in query:
        open_file_or_folder()
    elif "stop" in query or "bye" in query:
        speak("Goodbye sir, shutting down.")
        return "stop"
    else:
        speak("You said " + query)

# ---- Main Program ----
if __name__ == "__main__":
    speak("Hello sir, I am Jarvis Final. How can I help you?")
    while True:
        check_reminders()
        query = listen()
        if query != "":
            if process_command(query) == "stop":
                break
        time.sleep(0.5)  # Short pause to prevent continuous "listening"

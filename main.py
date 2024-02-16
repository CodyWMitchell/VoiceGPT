import speech_recognition as sr
from gtts import gTTS
import os
import playsound
from dotenv import load_dotenv
from openai import OpenAI
import time

WAKE_WORD = "pluto"

def speak(text):
    """Speaks the given text using gTTS and plays it."""
    tts = gTTS(text=text, lang='en')
    filename = "voice.mp3"
    tts.save(filename)
    print(f"Bot: {text}")
    playsound.playsound(filename)
    os.remove(filename)


def listen():
    """Listens for microphone input and returns the recognized text."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            print(f"You: {text}")
            return text.lower()
        except Exception as e:
            print(f"Exception: {e}")
            return ""


def answer(text, client, conversation_history=[]):
    """Uses OpenAI to respond to the given text, incorporating context."""
    prompt = "\n".join(conversation_history + [text])
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful voice assistant. Keep responses between 1-3 sentences."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    response = completion.choices[0].message.content
    conversation_history.append(response)
    return response, conversation_history


def main():
    """Entry point for the assistant."""
    load_dotenv()
    client = OpenAI()

    speak(f"Please say {WAKE_WORD} to activate me")

    conversation_history = []

    while True:
        text = listen()

        if WAKE_WORD in text:
            speak("Please tell me how can I help you?")
            conversation_history = []  # Reset context on wake word
            while True:
                text = listen()

                if "goodbye" in text:
                    speak("Goodbye!")
                    break
                else:
                    response, updated_history = answer(text, client, conversation_history)
                    speak(response)
                    conversation_history = updated_history
                    time.sleep(1)
                    speak("You may continue our conversation, or say goodbye to exit.")

if __name__ == "__main__":
    main()

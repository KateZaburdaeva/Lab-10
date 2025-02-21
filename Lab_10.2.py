import json
import requests
import pyttsx3
import pyaudio
import vosk

class Speech:
    def __init__(self):
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 200)

    def say(self, text):
        self.tts.say(text)
        self.tts.runAndWait()

class Recognize:
    def __init__(self):
        model = vosk.Model('vosk-model-small-en-us-0.15')
        self.recognizer = vosk.KaldiRecognizer(model, 16000)
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

    def listen(self):
        while True:
            data = self.stream.read(4000, exception_on_overflow=False)
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                if 'text' in result and result['text']:
                    yield result['text']

def dictionary_query(word, command):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if command == "meaning":
            meaning = data[0]['meanings'][0]['definitions'][0]['definition']
            return f"The meaning of {word} is {meaning}."
        elif command == "example":
            example = data[0]['meanings'][0]['definitions'][0].get('example', 'No example found.')
            return f"An example of {word} is {example}."
        elif command == "link":
            return f"The link to the definition is {url}."
    return "Word not found."

def main():
    speech = Speech()
    recognizer = Recognize()
    
    speech.say("Starting")
    
    for text in recognizer.listen():
        print(f"Recognized text: {text}")
        parts = text.lower().split()

        if "close" in parts:
            speech.say("Goodbye")
            break

        if "find" in parts and len(parts) > 1:
            word = parts[parts.index("find") + 1]
            command = parts[2] if len(parts) > 2 else "meaning"
            response = dictionary_query(word, command)
            print(response)
            speech.say(response)
        else:
            speech.say("Please say 'find [word]'.")

if __name__ == "__main__":
    main()

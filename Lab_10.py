import requests
import pyttsx3
import pyaudio
import json
import vosk
import os
from vosk import Model, KaldiRecognizer, SetLogLevel
from io import BytesIO
from PIL import Image

SetLogLevel(0)
model = vosk.Model('vosk-model-small-ru-0.22')
rec = KaldiRecognizer(model, 16000)
engine = pyttsx3.init()

def get_image_data():
    try:
        response = requests.get("https://dog.ceo/api/breeds/image/random")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка при получении изображения: {e}")
        engine.say("Извините, произошла ошибка при получении изображения.")
        engine.runAndWait()
        return None

def show_image(data):
    image_url = data["message"]
    print(f"Показываю случайное изображение собаки: {image_url}")
    engine.say("Показываю случайное изображение собаки.")
    engine.runAndWait()

def save_image(data):
    image_url = data["message"]
    image_name = os.path.basename(image_url)
    try:
        with open(image_name, "wb") as f:
            f.write(requests.get(image_url).content)
        print(f"Изображение сохранено как {image_name}")
        engine.say("Изображение сохранено.")
        engine.runAndWait()
    except requests.RequestException as e:
        print(f"Ошибка при сохранении изображения: {e}")
        engine.say("Извините, произошла ошибка при сохранении изображения.")
        engine.runAndWait()

def get_breed(data):
    image_url = data["message"]
    breed = image_url.split("/")[-2]
    print(f"Порода собаки: {breed}")
    engine.say(f"Порода собаки: {breed}")
    engine.runAndWait()

def get_resolution(data):
    image_url = data["message"]
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        width, height = image.size
        print(f"Разрешение изображения: {width}x{height} пикселей")
        engine.say(f"Разрешение изображения: {width} на {height} пикселей")
        engine.runAndWait()
    except requests.RequestException as e:
        print(f"Ошибка при получении изображения: {e}")
        engine.say("Извините, произошла ошибка при получении изображения.")
        engine.runAndWait()
    except (IOError, OSError) as e:
        print(f"Ошибка при работе с изображением: {e}")
        engine.say("Извините, произошла ошибка при работе с изображением.")
        engine.runAndWait()


p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)

try:
    while True:
        audio = stream.read(8000)
        if rec.AcceptWaveform(audio):
            result = json.loads(rec.Result())
            command = result["text"].lower()
            print(f"Распознанная команда: {command}")

            data = get_image_data()
            if not data:
                continue

            if "показать" in command:
                show_image(data)
            elif "сохранить" in command:
                save_image(data)
            elif "следующая" in command:
                show_image(data)
            elif "назвать породу" in command:
                get_breed(data)
            elif "разрешение" in command:
                get_resolution(data)
            else:
                print("Извините, я не понимаю эту команду.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

# -*- coding: utf-8 -*-

import os
import speech_recognition as sr
from pydub import AudioSegment

def convert_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    audio_file = sr.AudioFile(audio_path)
    with audio_file as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language='ru-RU')  # Для русского языка
        return text
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Ошибка запроса к сервису распознавания речи; {e}"

def process_directory(directory):
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            filepath = os.path.join(directory, filename)
            text = convert_audio_to_text(filepath)
            results[filename] = text
            print(f"Файл: {filename}\nТекст: {text}\n")
    return results

if __name__ == "__main__":
    directory = '/home/Music/test/wav/'  
    results = process_directory(directory)

    # Сохранение результатов в файл
    with open('transcriptions.txt', 'w', encoding='utf-8') as f:
        for filename, text in results.items():
            f.write(f"Файл: {filename}\nТекст: {text}\n\n")

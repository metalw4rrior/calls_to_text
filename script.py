import os
import re
from collections import Counter
import speech_recognition as sr

def convert_audio_to_text(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            return text
        except sr.UnknownValueError:
            return "Не удалось распознать речь"
        except sr.RequestError as e:
            return f"Ошибка запроса к сервису распознавания речи; {e}"
    except Exception as e:
        return f"Ошибка при обработке файла: {e}"

def analyze_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(words)
    most_common_words = word_freq.most_common(10)
    
    bigrams = zip(words, words[1:])
    bigram_freq = Counter(bigrams)
    most_common_bigrams = bigram_freq.most_common(10)
    
    trigrams = zip(words, words[1:], words[2:])
    trigram_freq = Counter(trigrams)
    most_common_trigrams = trigram_freq.most_common(10)

    return most_common_words, most_common_bigrams, most_common_trigrams

def process_directory(directory):
    results = {}
    for filename in os.listdir(directory):
        if filename.endswith('.wav'):
            filepath = os.path.join(directory, filename)
            try:
                text = convert_audio_to_text(filepath)
                if text.startswith("Ошибка"):
                    print(f"Файл: {filename}\n{filename}\n")
                    continue
                most_common_words, most_common_bigrams, most_common_trigrams = analyze_text(text)
                results[filename] = {
                    'text': text,
                    'words': most_common_words,
                    'bigrams': most_common_bigrams,
                    'trigrams': most_common_trigrams
                }
                print(f"Файл: {filename}\nТекст: {text}\n")
            except Exception as e:
                print(f"Ошибка обработки файла {filename}: {e}")
    return results

if __name__ == "__main__":
    directory = '/home/kozlova/Music/test/calls_to_text/wav1/'  # Update with your directory path
    results = process_directory(directory)

    # Save results to file
    with open('transcriptions.txt', 'w', encoding='utf-8') as f:
        for filename, data in results.items():
            f.write(f"Файл: {filename}\nТекст: {data['text']}\n\n")
            f.write("Наиболее частые слова:\n")
            for word, freq in data['words']:
                f.write(f"{word}: {freq}\n")
            f.write("\nНаиболее частые биграммы:\n")
            for bigram, freq in data['bigrams']:
                f.write(f"{' '.join(bigram)}: {freq}\n")
            f.write("\nНаиболее частые триграммы:\n")
            for trigram, freq in data['trigrams']:
                f.write(f"{' '.join(trigram)}: {freq}\n")
            f.write("\n\n")

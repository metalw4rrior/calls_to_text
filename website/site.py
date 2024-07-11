from flask import Flask, render_template
import os
import glob
from collections import defaultdict, Counter
import re
import nltk
from nltk import ngrams
import pymorphy2

# Установка ресурсов nltk (можно выполнить один раз)
nltk.download('punkt')

app = Flask(__name__)

# Жёстко заданные пути к директориям
text_files_path = "/home/kozlova/Music/test/calls_to_text/text"

# Проверка существования папки с текстовыми файлами
if not os.path.exists(text_files_path):
    print(f"Ошибка: Папка с текстовыми файлами не найдена: {text_files_path}")
    exit(2)

# Инициализация pymorphy2
morph = pymorphy2.MorphAnalyzer()

# Список слов и фраз, которые нужно учитывать (связанные с транспортной инфраструктурой)
base_words_phrases = [
    "автобус", "транспорт", "перевозчик", "светофор", "парковка", "дорога", "пешеход", 
    "метро", "трамвай", "маршрут", "велосипед", "пешеходный переход", "остановка", 
    "перекрёсток", "шоссе", "платная дорога", "такси", "общественный транспорт", 
    "транспортная развязка", "скоростной режим", "дорожное движение", "дорожный знак",
    "ремонт дорог", "дорожные работы", "затор", "пробка", "движение", "парковочные места",
    "стоянка", "паркомат", "велодорожка", "подземный переход", "наземный переход"
]

# Функция для получения всех форм слова
def get_all_forms(word):
    parse = morph.parse(word)[0]
    forms = set()
    for lexeme in parse.lexeme:
        forms.add(lexeme.word)
    return forms

# Получаем все формы слов и фраз
include_words_phrases = set()
for phrase in base_words_phrases:
    words = phrase.split()
    forms = [get_all_forms(word) for word in words]
    for form_combination in zip(*forms):
        include_words_phrases.add(" ".join(form_combination))

# Функция для анализа текстовых файлов
def analyze_text_files():
    # Словарь для хранения всех слов, фраз, биграмм и триграмм по их леммам
    lemmas_dict = defaultdict(list)
    word_counts = defaultdict(Counter)

    # Чтение текстовых файлов и подсчёт слов, фраз, биграмм и триграмм
    for file_path in glob.glob(os.path.join(text_files_path, "*.txt")):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

            # Нормализация текста (приведение к нижнему регистру)
            text = text.lower()

            # Разделение текста на слова и фразы
            words = re.findall(r'\b\w+\b', text)
            phrases = re.findall(r'\b[\w\s]+\b', text)

            # Фильтрация слов и фраз по списку включений
            filtered_words = [word for word in words if word in include_words_phrases]
            filtered_phrases = [phrase for phrase in phrases if phrase in include_words_phrases]

            # Обработка слов
            for word in filtered_words:
                lemma = morph.parse(word)[0].normal_form
                lemmas_dict[lemma].append(word)
                word_counts[lemma][word] += 1

            # Обработка фраз
            for phrase in filtered_phrases:
                words_in_phrase = phrase.split()
                lemmas_in_phrase = [morph.parse(word)[0].normal_form for word in words_in_phrase]
                lemma_phrase = " ".join(lemmas_in_phrase)
                lemmas_dict[lemma_phrase].append(phrase)
                word_counts[lemma_phrase][phrase] += 1

            # Создание биграмм и триграмм с использованием nltk
            bigrams = list(ngrams(filtered_words, 2))
            trigrams = list(ngrams(filtered_words, 3))

            # Обработка биграмм
            for bigram in bigrams:
                bigram_str = " ".join(bigram)
                bigram_lemmas = " ".join(morph.parse(word)[0].normal_form for word in bigram)
                lemmas_dict[bigram_lemmas].append(bigram_str)
                word_counts[bigram_lemmas][bigram_str] += 1

            # Обработка триграмм
            for trigram in trigrams:
                trigram_str = " ".join(trigram)
                trigram_lemmas = " ".join(morph.parse(word)[0].normal_form for word in trigram)
                lemmas_dict[trigram_lemmas].append(trigram_str)
                word_counts[trigram_lemmas][trigram_str] += 1

    # Подсчёт частоты слов, фраз, биграмм и триграмм по леммам
    sorted_lemmas_dict = {lemma: sum(word_counts[lemma].values()) for lemma in lemmas_dict}
    # Сортировка по убыванию частоты
    sorted_lemmas_dict = dict(sorted(sorted_lemmas_dict.items(), key=lambda item: item[1], reverse=True))

    # Возвращаем отсортированный словарь для отображения на веб-странице
    return sorted_lemmas_dict

@app.route('/')
def index():
    # Анализируем текстовые файлы
    sorted_lemmas_dict = analyze_text_files()

    # Возвращаем HTML-шаблон с результатами анализа
    return render_template('index.html', lemmas_dict=sorted_lemmas_dict)

if __name__ == '__main__':
    app.run(debug=True)

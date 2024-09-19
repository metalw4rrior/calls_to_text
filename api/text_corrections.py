
# text_corrections.py

import re

# Словарь для исправлений
replacements = {
    "У стоматологии": "Стоматология",
    "Паркаус": "Паркхаус",
    "предположением": "предложением",
    "делите": "уделите",
    "апаратизирование": "протезирование",
    "серова": "Серова",
    "дегистратура": "регистратура",
    "зубочарисной": "зубочелюстной",
    "книга": "клиника",
    "на премию": "на приёме",
    "я смотрю": "осмотры",
    "0.2, да": "2D",
    "грильлич": "Гринвич",
    "подминка": "долго",
    "елема": "Eлена",
    "автобокзал": "автовокзал",
    "ультразвок": "ультразвук",
    "зариентировать": "соориенировать",
    "Гриныча": "Гринвича",
    "сече, листья": "всей челюсти",
    "биозаплаты": "бесплатно",
    "зарплаты": "оплаты",
    "спульпит": "пульпит",
    "в кинуть": "какие-нибудь",
    "ультратэн": "УльтраДент",
    "учреждений": "очередей",
    "астоматология": "Стоматология",
    "астоматологии": "стоматологии",
    "остоматолога": "у стоматолога",
    "и плантацию": "имплантацию",
    "плантация": "имплантация",
    "зубочерестные": "зубочелюстные",
    "рекомендация": "рекомендации",
    "вам были стоматологи": "давно были у стоматолога",
    "утерите": "уделите",
    "зубочарестной": "зубочелюстной",
    "ВД": "2D",
    "2Д": "2D",
    "":"",



}   

def replace_words(text: str, replacements: dict) -> str:
    for wrong_word, correct_word in replacements.items():
        text = re.sub(r'\b' + re.escape(wrong_word) + r'\b', correct_word, text, flags=re.IGNORECASE)
    return text


# text_corrections.py

import re

# Словарь для исправлений
replacements = {
    "астоматология": "Стоматология",
    "астоматологии": "стоматологии",
    "остоматолога": "у стоматолога",
    "и плантацию": "имплантацию",
    "плантация": "имплантация",
    "зубочерестные": "зубочелюстные",
    "рекомендация": "рекомендации",
    "вам были стоматологи": "давно были у стоматолога",
    "":"",



}   

def replace_words(text: str, replacements: dict) -> str:
    for wrong_word, correct_word in replacements.items():
        text = re.sub(r'\b' + re.escape(wrong_word) + r'\b', correct_word, text, flags=re.IGNORECASE)
    return text

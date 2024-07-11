import os
import subprocess
from datetime import datetime

# Жёстко заданные пути к директориям и модели
srcpath = "/home/kozlova/Music/test/calls_to_text/wav1/"
dstpath = "/home/kozlova/Music/test/calls_to_text/text/"
modelpath = "/usr/local/bin/vosk-transcriber"
# Проверка существования исходной директории
if not os.path.exists(srcpath):
    print(f"Ошибка: Исходная директория не найдена: {srcpath}")
    exit(2)

# Создание целевой директории, если её нет
os.makedirs(dstpath, exist_ok=True)

# Функция для транскрибации аудиофайлов
def transcribe_audio(srcfile, dstfile, model):
    cmd = [model, '-l', 'ru', '-i', srcfile, '-o', dstfile]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# Замена пробелов на подчеркивания в именах файлов
for root, _, files in os.walk(srcpath):
    for filename in files:
        if ' ' in filename:
            os.rename(os.path.join(root, filename), os.path.join(root, filename.replace(' ', '_')))

# Подсчёт количества файлов для транскрибации
file_count = sum(len(files) for _, _, files in os.walk(srcpath))
print(f"Найдено файлов: {file_count}")

# Транскрибация каждого файла
start_time = datetime.now()
processed_count = 0

for root, _, files in os.walk(srcpath):
    for filename in files:
        srcfile = os.path.join(root, filename)
        dstfile = os.path.join(dstpath, filename + '.txt')

        if os.path.isfile(srcfile):
            processed_count += 1
            print(f"Транскрибация {filename} ({processed_count}/{file_count})")
            transcribe_audio(srcfile, dstfile, modelpath)

# Подсчёт количества транскрибированных файлов
ready_count = len(os.listdir(dstpath))
print(f"ГОТОВО. Транскрибировано файлов: {ready_count} из {file_count}")

# Вывод времени начала и окончания выполнения
end_time = datetime.now()
print(f"НАЧАТО: {start_time}")
print(f"ЗАВЕРШЕНО: {end_time}")

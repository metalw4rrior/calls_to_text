import subprocess
import os

# Указываем пути к директориям
input_dir = '/home/kozlova/Music/test/calls_to_text/wav/'
output_dir = '/home/kozlova/Music/test/calls_to_text/wav1/'

# Создаем выходную директорию, если её нет
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Проходим по всем файлам в исходной директории
for filename in os.listdir(input_dir):
    if filename.endswith(".wav"):  # Проверяем, что файл имеет расширение .wav
        input_file = os.path.join(input_dir, filename)
        output_file = os.path.join(output_dir, filename)
        
        # Команда для конвертации файла с помощью ffmpeg
        command = [
            'ffmpeg', '-i', input_file,
            '-ac', '1', '-ar', '16000', '-acodec', 'pcm_s16le',
            output_file
        ]
        
        # Выполняем команду
        subprocess.run(command)

print("Конвертация завершена.")









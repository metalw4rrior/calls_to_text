#!/bin/bash

# Проверяем, установлен ли ffmpeg
if ! command -v ffmpeg &> /dev/null
then
    echo "ffmpeg не установлен. Установите ffmpeg и повторите попытку."
    exit
fi

# Проверяем, переданы ли аргументы
if [ $# -eq 0 ]; then
    echo "Необходимо указать хотя бы один файл или директорию."
    echo "Использование: $0 file1.wav file2.wav ... или $0 directory"
    exit 1
fi

# Функция для конвертации одного файла
convert_file() {
    local input_file="$1"
    local output_file="${input_file%.wav}.mp3"
    ffmpeg -i "$input_file" -q:a 0 "$output_file"
}

# Если аргумент - директория, обрабатываем все .wav файлы в ней
if [ -d "$1" ]; then
    for file in "$1"/*.wav; do
        [ -e "$file" ] || continue
        echo "Конвертация $file ..."
        convert_file "$file"
    done
else
    # Иначе, обрабатываем все переданные файлы
    for file in "$@"; do
        if [ -f "$file" ]; then
            echo "Конвертация $file ..."
            convert_file "$file"
        else
            echo "$file не является файлом."
        fi
    done
fi

echo "Конвертация завершена."

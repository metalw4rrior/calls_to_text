#!/bin/bash

# Переменные для путей и модели
srcpath="/home/kozlova/Music/test/calls_to_text/wav1/"
dstpath="/home/kozlova/Music/test/calls_to_text/text/"
modelpath="/usr/local/bin/vosk-transcriber"

errmsg="ИСПОЛЬЗОВАНИЕ: sh transcribe.sh"

# Проверка наличия исходной папки
if [ ! -d "$srcpath" ]; then
    echo "Ошибка: Исходная папка не найдена: $srcpath" >&2
    exit 2
fi

# Создание целевой папки, если она не существует
if [ ! -d "$dstpath" ]; then
    echo "Создание целевой папки: $dstpath"
    mkdir -p "$dstpath"
fi

# Замена пробелов на подчеркивания в именах файлов в исходной папке
find "$srcpath" -name "* *" -type f | while read file; do
    mv "$file" "$(dirname "$file")/$(basename "$file"|tr ' ' _)"
done

# Подсчет количества файлов для транскрибации
famount=$(find "$srcpath" -type f | wc -l)
echo "Найдено файлов: $famount"

i=0
# Цикл транскрибации файлов
for f in "$srcpath"/*; do
    if [ -f "$f" ]; then
        i=$((i + 1))
        echo "Транскрибация $(basename "$f") ($i/$famount)"
        
        # Получаем продолжительность файла в секундах
        duration=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$f")

        # Если длительность файла более 30 секунд, разбиваем на части
        if (( $(echo "$duration > 30" | bc -l) )); then
            echo "Файл длиннее 30 секунд, разбиваем на части..."

            # Создаем временную директорию для частей
            tmpdir=$(mktemp -d)
            echo "Временная директория: $tmpdir"

            # Разбиваем файл на части по 30 секунд
            ffmpeg -i "$f" -f segment -segment_time 30 -c copy "$tmpdir/%03d.wav"

            # Транскрибируем каждую часть и записываем результат в один временный файл
            tmptranscript="$tmpdir/transcript.txt"
            touch "$tmptranscript"
            for part in "$tmpdir"/*.wav; do
                vosk-transcriber -m "$modelpath" -i "$part" -o "$tmptranscript" >/dev/null 2>&1
            done

            # Перемещаем временный файл с текстом в целевую папку
            mv "$tmptranscript" "$dstpath/$(basename "$f").txt"

            # Удаляем временную директорию с частями
            rm -r "$tmpdir"

        else
            # Транскрибируем весь файл и записываем результат в целевую папку
            vosk-transcriber -m "$modelpath" -i "$f" -o "$dstpath/$(basename "$f").txt" >/dev/null 2>&1
        fi
    fi
done

# Подсчет количества транскрибированных файлов в целевой папке
fready=$(find "$dstpath" -type f | wc -l)
echo "ГОТОВО. Транскрибировано файлов: $fready из $famount"

startdate=$(date)
enddate=$(date)
echo "НАЧАТО: $startdate"
echo "ЗАВЕРШЕНО: $enddate"

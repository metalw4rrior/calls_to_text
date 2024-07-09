import os
from pydub import AudioSegment

def convert_ogg_to_wav(source_directory, destination_directory):
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)
    
    for filename in os.listdir(source_directory):
        if filename.endswith('.ogg'):
            ogg_path = os.path.join(source_directory, filename)
            wav_filename = os.path.splitext(filename)[0] + '.wav'
            wav_path = os.path.join(destination_directory, wav_filename)
            
            # Конвертация файла
            audio = AudioSegment.from_ogg(ogg_path)
            audio.export(wav_path, format='wav')
            print(f"Конвертирован: {filename} -> {wav_filename}")

if __name__ == "__main__":
    source_directory = '/home/Music/test/'  # Путь к папке с OGG файлами
    destination_directory = '/home/Music/test/wav/'  # Путь к папке для сохранения WAV файлов
    convert_ogg_to_wav(source_directory, destination_directory)

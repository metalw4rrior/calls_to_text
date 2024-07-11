from pydub import AudioSegment
import os

def convert_mp3_to_wav(mp3_path):
    sound = AudioSegment.from_mp3(mp3_path)
    wav_path = mp3_path.replace('.mp3', '.wav')
    sound.export(wav_path, format='wav')
    return wav_path

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.mp3'):
            mp3_path = os.path.join(directory, filename)
            wav_path = convert_mp3_to_wav(mp3_path)
            print(f"Конвертировано: {mp3_path} -> {wav_path}")

if __name__ == "__main__":
    directory = '/home/kozlova/Music/test/calls_to_text/mp3'  # Замените на нужный путь
    process_directory(directory)

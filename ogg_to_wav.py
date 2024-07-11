import os
import ffmpeg

def convert_ogg_to_wav(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.ogg'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.wav")
            
            try:
                ffmpeg.input(input_path).output(output_path, acodec='pcm_s16le', ar=16000).run(overwrite_output=True)
                print(f"Конвертация {filename} завершена.")
            except ffmpeg.Error as e:
                print(f"Ошибка конвертации файла {filename}: {e.stderr}")
            except Exception as e:
                print(f"Не удалось сконвертировать файл {filename}: {str(e)}")

if __name__ == "__main__":
    input_directory = '/home/kozlova/Music/test/calls_to_text/wav/'

    output_directory ='/home/kozlova/Music/test/calls_to_text/wav1/'

    
    convert_ogg_to_wav(input_directory, output_directory)








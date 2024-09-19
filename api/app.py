import redis
from dialogue_analyzer import analyze_dialogue
from text_corrections import replace_words, replacements

import logging
import uuid
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pydub import AudioSegment, effects
from faster_whisper import WhisperModel
import asyncpg
from datetime import datetime
import os
import re


redis_client = redis.StrictRedis(host='redis_host',password='password', port=6379, db=0)
# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Whisper model configuration
model_size = "large-v3"
model = WhisperModel(model_size, device="cpu", compute_type="int8")

class TranscriptionRequest(BaseModel):
    operatorName: str
    clientPhone: str
    duration: int
    callStartDate: str
    callType: str
    recordUrl: str

async def init_db():
    conn = await asyncpg.connect(
        user='user',
        password='password',
        database='db',
        host='host',
        port='6432',
        statement_cache_size=0
    )
    return conn

def split_stereo_to_mono(audio_path):
    audio = AudioSegment.from_mp3(audio_path)
    return audio.split_to_mono()

async def download_audio(record_url: str, file_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(record_url) as response:
            with open(file_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

def normalize_audio(audio_segment):
    return effects.normalize(audio_segment)

def remove_noise(audio_segment):
    return audio_segment.low_pass_filter(3000).high_pass_filter(200)

def transcribe_audio(audio_segment, language="ru"):
    # Save audio segment to a temporary file
    temp_file_path = f"temp_segment_{uuid.uuid4()}.mp3"
    audio_segment.export(temp_file_path, format="mp3")
    
    logger.info(f"Transcribing audio file: {temp_file_path}")
    segments, _ = model.transcribe(temp_file_path, beam_size=5, language=language, condition_on_previous_text=False)
    os.remove(temp_file_path)  # Clean up the temporary file
    logger.info(f"Transcription completed for file: {temp_file_path}")
    return list(segments)

def merge_transcriptions(left_segments, right_segments, call_type):
    logger.info("Merging transcriptions")

    if call_type == "incoming":
        client_segments = left_segments
        operator_segments = right_segments
    else:
        client_segments = right_segments
        operator_segments = left_segments

    all_segments = []
    for segment in client_segments:
        all_segments.append((segment.start, segment.end, "client", segment.text))
    for segment in operator_segments:
        all_segments.append((segment.start, segment.end, "operator", segment.text))

    all_segments.sort(key=lambda x: (x[0], x[1], x[2] != "operator"))

    merged_segments = []
    current_speaker = all_segments[0][2]
    current_text = [all_segments[0][3]]
    current_start = all_segments[0][0]
    current_end = all_segments[0][1]

    logger.info("Processing segments:")
    for start, end, speaker, text in all_segments:
        logger.info(f"Segment: Start={start}, End={end}, Speaker={speaker}, Text={text}")

    for start, end, speaker, text in all_segments[1:]:
        if speaker == current_speaker and current_end >= start:
            current_text.append(text)
            current_end = max(current_end, end)
        else:
            merged_segments.append((current_start, current_end, current_speaker, " ".join(current_text)))
            current_speaker = speaker
            current_text = [text]
            current_start = start
            current_end = end

    merged_segments.append((current_start, current_end, current_speaker, " ".join(current_text)))

    final_segments = []
    buffer_text = []
    buffer_speaker = None

    logger.info("Processing merged segments:")
    for start, end, speaker, text in merged_segments:
        logger.info(f"Segment: Start={start}, End={end}, Speaker={speaker}, Text={text}")

    for start, end, speaker, text in merged_segments:
        if speaker == buffer_speaker:
            buffer_text.append(text)
        else:
            if buffer_text:
                final_segments.append((None, None, buffer_speaker, " ".join(buffer_text)))
                buffer_text = []
            buffer_speaker = speaker
            buffer_text = [text]

    if buffer_text:
        final_segments.append((None, None, buffer_speaker, " ".join(buffer_text)))

    logger.info(f"Merged transcription: {final_segments}")

    return final_segments

def format_transcription_as_string(merged_transcription, phone_number, operator_number, call_date_str):
    # Обработка даты и времени
    call_date = datetime.strptime(call_date_str, "%Y-%m-%dT%H:%M:%S%z")
    formatted_transcription = "{\n"
    formatted_transcription += f'\tphone:{phone_number};\n'
    formatted_transcription += f'\toperator:{operator_number};\n'
    formatted_transcription += f'\tdate:{call_date.strftime("%Y-%m-%d")};\n'
    formatted_transcription += f'\ttime:{call_date.strftime("%H:%M:%S")};\n'
    formatted_transcription += '\ttext:{\n'

    for i, (_, _, speaker, text) in enumerate(merged_transcription):
        speaker_label = f"{speaker}{i+1}"
        formatted_transcription += f'\t\t{{{speaker_label}:"{text}";}}\n'

    formatted_transcription += '\t}\n'
    formatted_transcription += '}'
    return formatted_transcription

def extract_date_time(date_str_with_tz: str) -> (datetime, str):
    # Регулярное выражение для извлечения даты и времени из строки с временной зоной
    match = re.match(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})', date_str_with_tz)
    if match:
        date_part = match.group(1)
        time_part = match.group(2)
        return datetime.strptime(f"{date_part} {time_part}", '%Y-%m-%d %H:%M:%S')
    raise ValueError("Invalid date format")

async def process_audio(record_url: str, call_type: str, phone_number: str, operator_name: str, call_date_str: str):
    logger.info(f"Processing audio from URL: {record_url}")

    unique_id = str(uuid.uuid4())
    file_path = f"temp_audio_{unique_id}.mp3"  # Save as MP3 file

    conn = None
    try:
        await download_audio(record_url, file_path)

        mono_channels = split_stereo_to_mono(file_path)

        if len(mono_channels) != 2:
            logger.error(f"Invalid audio format: Expected stereo, got {len(mono_channels)} channels.")
            raise ValueError(f"Invalid audio format: Expected stereo, got {len(mono_channels)} channels.")

        mono_left, mono_right = normalize_audio(mono_channels[0]), normalize_audio(mono_channels[1])
        mono_left, mono_right = remove_noise(mono_left), remove_noise(mono_right)

        logger.info("Transcribing left audio channel")
        left_segments = transcribe_audio(mono_left)
        
        logger.info("Transcribing right audio channel")
        right_segments = transcribe_audio(mono_right)
        
        merged_transcription = merge_transcriptions(left_segments, right_segments, call_type)

        formatted_transcription = format_transcription_as_string(merged_transcription, phone_number, operator_name, call_date_str)
        corrected_transcription = replace_words(formatted_transcription, replacements)

        # Analyze the dialogue
        category_found, dialogue_count, is_corrected = await analyze_dialogue(corrected_transcription, operator_name)

        conn = await init_db()

        call_datetime = extract_date_time(call_date_str)
        call_date = call_datetime.date()
        call_time = call_datetime.time()

        if call_type == "in":
            await conn.execute('''
                INSERT INTO incoming_calls(filename, phone_number, operator_name, call_date, call_time, transcript, is_corrected, result, dialogue_count) 
                VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ''', file_path, phone_number, operator_name, call_date, call_time, corrected_transcription, is_corrected, category_found, dialogue_count)
        elif call_type == "out":
            await conn.execute('''
                INSERT INTO outgoing_calls(filename, phone_number, operator_name, call_date, call_time, transcript, is_corrected, result, dialogue_count) 
                VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ''', file_path, phone_number, operator_name, call_date, call_time, corrected_transcription, is_corrected, category_found, dialogue_count)

    except Exception as e:
        logger.error(f"Error processing audio: {e}")
        raise e

    finally:
        if conn:
            await conn.close()
        if os.path.exists(file_path):
            os.remove(file_path)


@app.post("/process/")
async def process_request(transcription_request: TranscriptionRequest):
    try:
        logger.info(f"Processing request: {transcription_request}")

        # Вызов функции для обработки аудио
        await process_audio(
            transcription_request.recordUrl,
            transcription_request.callType,
            transcription_request.clientPhone,
            transcription_request.operatorName,  # Передаём имя оператора вместо номера
            transcription_request.callStartDate
        )

        return {"message": "File processed successfully"}
    
    except Exception as e:
        logger.error(f"Error in /process/: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/uploadfile/")
async def upload_file(transcription_request: TranscriptionRequest):
    if transcription_request.duration < 15:
        raise HTTPException(status_code=400, detail="Audio duration must be at least 15 seconds.")
    
    try:
        logger.info(f"Adding request to queue: {transcription_request}")

        # Преобразуем запрос в JSON и добавляем его в очередь Redis
        redis_client.rpush('audio_requests', transcription_request.json())
        
        return {"message": "Request added to queue"}
    
    except Exception as e:
        logger.error(f"Error in /uploadfile/: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        workers=4
    )

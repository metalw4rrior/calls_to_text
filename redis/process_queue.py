import redis
import requests
import json
import time
import logging

# Настройка соединения с Redis
redis_client = redis.StrictRedis(host='host',password='pass', port=6379, db=0)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FASTAPI_SERVER_URL = "http://api_server/process"  # Убедитесь, что эндпоинт соответствует

def process_queue():
    while True:
        try:
            # Получаем запрос из очереди
            request_data = redis_client.lpop('audio_requests')
            if request_data:
                data = json.loads(request_data)
                logger.info(f"Processing request: {data}")
                
                # Отправляем запрос на ваш FastAPI сервер
                response = requests.post(FASTAPI_SERVER_URL, json=data)
                logger.info(f"Status code: {response.status_code}")
                
                try:
                    response_json = response.json()
                    logger.info(f"Response: {response_json}")
                except requests.exceptions.JSONDecodeError:
                    logger.error("Response is not valid JSON or is empty.")
                    logger.error(f"Response text: {response.text}")
            else:
                logger.info("Queue is empty, waiting for new requests.")
            
            time.sleep(1)  # Пауза между проверками очереди
        
        except Exception as e:
            logger.error(f"Error processing queue: {e}")

if __name__ == "__main__":
    process_queue()

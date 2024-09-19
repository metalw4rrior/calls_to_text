from flask import render_template, request
from db import get_db_connection
import re
from .text_corrections import replace_words,replacements  # Импорт функции для исправления текста

def process_transcript(text_data):
    # Удаляем внешние скобки и текст до ключа 'text'
    text_data = re.sub(r'^\{[^}]*text:\{', '', text_data).strip()
    text_data = re.sub(r'\}\s*\}$', '', text_data).strip()

    # Заменяем метки начала записи на новые строки с указанием спикеров
    text_data = re.sub(r'\{operator\d+:"', 'Оператор: ', text_data)
    text_data = re.sub(r'\{client\d+:"', 'Клиент: ', text_data)
    
    # Удаляем завершающие символы и лишние символы
    text_data = re.sub(r'";\}', '', text_data)
    text_data = re.sub(r'";', '', text_data)
    
    # Убираем оставшиеся кавычки и лишние пробелы
    text_data = re.sub(r'"', '', text_data)
    text_data = re.sub(r'\s+', ' ', text_data).strip()

    # Применяем исправления текста с помощью функции replace_words
    text_data = replace_words(text_data, replacements)

    # Разделяем реплики на отдельные абзацы
    text_data = re.sub(r'(Оператор:|Клиент:)', r'\n\n\1', text_data)

    # Убираем лишние пробелы и формируем итоговый текст
    text_data = text_data.strip()
    
    return text_data


def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Параметры постраничного вывода
    per_page = 20
    page = int(request.args.get('page', 1))

    # Запрос для получения общего количества записей
    count_query = """
        SELECT COUNT(*)
        FROM (
            SELECT phone_number FROM incoming_calls
            UNION ALL
            SELECT phone_number FROM outgoing_calls
        ) AS all_calls
    """
    cursor.execute(count_query)
    total_records = cursor.fetchone()[0]
    total_pages = (total_records + per_page - 1) // per_page

    # Запрос для получения записей на текущей странице
    query = """
        SELECT phone_number, operator_name, call_date, call_time, transcript, result,is_corrected, 'incoming' AS call_type
        FROM incoming_calls
        UNION ALL
        SELECT phone_number, operator_name, call_date, call_time, transcript, result, is_corrected, 'outgoing' AS call_type
        FROM outgoing_calls
        ORDER BY call_date DESC, call_time DESC
        LIMIT %s OFFSET %s
    """
    cursor.execute(query, (per_page, (page - 1) * per_page))
    records = cursor.fetchall()

    # Запрос для получения результатов для круговой диаграммы
    query_results = """
        SELECT result, COUNT(*) AS count
        FROM (
            SELECT result FROM incoming_calls
            UNION ALL
            SELECT result FROM outgoing_calls
        ) AS results
        GROUP BY result
    """
    cursor.execute(query_results)
    result_counts = cursor.fetchall()

    cursor.close()
    conn.close()

    calls = [{'phone_number': record[0],
              'operator_name': record[1] if record[1] else 'N/A',
              'call_date': record[2],
              'call_time': record[3],
              'transcript': process_transcript(record[4]),
              'result': record[5] if record[5] else 'N/A',
              'is_corrected': record[6] ,
              'call_type': record[7]} for record in records]

    result_data = [{'result': row[0], 'count': row[1]} for row in result_counts]

    return render_template(
        'index.html',
        calls=calls,
        result_data=result_data,
        current_page=page,
        total_pages=total_pages,
        current_year=2024
    )


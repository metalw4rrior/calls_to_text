from flask import render_template, request
from db import get_db_connection
import re
from .text_corrections import replace_words,replacements 
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

def operators():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получение параметров из запроса
    operator_name = request.args.get('operator_name')
    client_number = request.args.get('client_number')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    sort_by = request.args.get('sort_by', 'call_date')
    sort_order = request.args.get('sort_order', 'ASC')
    page = int(request.args.get('page', 1))  # Текущая страница
    per_page = 10  # Количество записей на странице

    # Проверка корректности параметров сортировки
    if sort_by not in ['call_date', 'call_time', 'operator_name', 'result']:
        sort_by = 'call_date'
    if sort_order not in ['ASC', 'DESC']:
        sort_order = 'ASC'

    # Базовый запрос
    base_query = """
        SELECT phone_number, operator_name, call_date, call_time, transcript, result, is_corrected, call_type
        FROM (
            SELECT phone_number, operator_name, call_date, call_time, transcript, result,is_corrected, 'incoming' AS call_type
            FROM incoming_calls
            UNION ALL
            SELECT phone_number, operator_name, call_date, call_time, transcript, result,is_corrected, 'outgoing' AS call_type
            FROM outgoing_calls
        ) AS all_calls
        WHERE 1=1
    """

    # Список параметров для фильтрации
    query_params = []

    if operator_name and operator_name.strip() != 'None':
        base_query += " AND operator_name = %s"
        query_params.append(operator_name)
    elif client_number and client_number.strip():
        base_query += " AND phone_number LIKE %s"
        query_params.append(f"%{client_number.strip()}%")

    if date_from:
        base_query += " AND call_date >= %s"
        query_params.append(date_from)
    if date_to:
        base_query += " AND call_date <= %s"
        query_params.append(date_to)

    # Добавление сортировки
    base_query += f" ORDER BY {sort_by} {sort_order}"

    # Добавление пагинации
    offset = (page - 1) * per_page
    base_query += f" LIMIT %s OFFSET %s"
    query_params.extend([per_page, offset])

    # Выполнение запроса с фильтрами и сортировкой
    cursor.execute(base_query, query_params)
    records = cursor.fetchall()

    # Получение общего количества записей
    count_query = """
        SELECT COUNT(*)
        FROM (
            SELECT phone_number, operator_name, call_date, call_time, transcript, result,is_corrected, 'incoming' AS call_type
            FROM incoming_calls
            UNION ALL
            SELECT phone_number, operator_name, call_date, call_time, transcript, result,is_corrected, 'outgoing' AS call_type
            FROM outgoing_calls
        ) AS all_calls
        WHERE 1=1
    """
    if operator_name and operator_name.strip() != 'None':
        count_query += " AND operator_name = %s"
    elif client_number and client_number.strip():
        count_query += " AND phone_number LIKE %s"
    if date_from:
        count_query += " AND call_date >= %s"
    if date_to:
        count_query += " AND call_date <= %s"
    cursor.execute(count_query, query_params[:-2])
    total_records = cursor.fetchone()[0]
    total_pages = (total_records + per_page - 1) // per_page

    # Получение списка операторов для фильтра
    query_operators = """
        SELECT DISTINCT operator_name
        FROM (
            SELECT operator_name FROM incoming_calls
            UNION ALL
            SELECT operator_name FROM outgoing_calls
        ) AS operators
        WHERE operator_name IS NOT NULL
        ORDER BY operator_name
    """
    cursor.execute(query_operators)
    operators = cursor.fetchall()

    cursor.close()
    conn.close()

    calls = [{
        'phone_number': record[0],
        'operator_name': record[1] if record[1] else 'N/A',
        'call_date': record[2],
        'call_time': record[3],
        'transcript': process_transcript(record[4]),  # Применение обработки транскрипта
        'result': record[5] if record[5] else 'N/A',
        'is_corrected': record[6] ,
        'call_type': record[7]
    } for record in records]

    return render_template(
        'operators.html',
        operators=[{'operator_name': op[0]} for op in operators],
        calls=calls,
        operator_name=operator_name,
        client_number=client_number,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        current_page=page,  # Добавлено для пагинации
        total_pages=total_pages  # Добавлено для пагинации
    )

from flask import Blueprint, render_template, request, jsonify
from db import get_db_connection
import psycopg2

app = Blueprint('app', __name__)

@app.route('/filtered-data')
def filtered_data():
    # Получение параметров фильтрации из запроса
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    operator_name = request.args.get('operator_name', '')  # Исправлено имя переменной

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Запрос для статистики по результатам звонков
        query_results = """
        SELECT result, COUNT(*)
        FROM outgoing_calls
        WHERE call_date BETWEEN %s AND %s
        AND (%s = '' OR operator_name = %s)
        GROUP BY result
        """
        cursor.execute(query_results, (start_date, end_date, operator_name, operator_name))  # Исправлен параметр
        result_data = cursor.fetchall()

        # Запрос для статистики по операторам
        query_operators = """
        SELECT operator_name, COUNT(*)
        FROM outgoing_calls
        WHERE call_date BETWEEN %s AND %s
        AND (%s = '' OR operator_name = %s)
        GROUP BY operator_name
        """
        cursor.execute(query_operators, (start_date, end_date, operator_name, operator_name))  # Исправлен параметр
        operator_data = cursor.fetchall()

        cursor.close()
        conn.close()

        # Формируем данные для графиков
        result_labels = [row[0] for row in result_data]
        result_values = [row[1] for row in result_data]
        operator_labels = [row[0] for row in operator_data]
        operator_values = [row[1] for row in operator_data]
        total_calls_count = sum(operator_values)  # Общее количество звонков

        return jsonify({
            'result_labels': result_labels,
            'result_values': result_values,
            'operator_labels': operator_labels,
            'operator_values': operator_values,
            'total_calls_count': total_calls_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

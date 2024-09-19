from flask import render_template, request, jsonify
from db import get_db_connection
import logging
from flask_jwt_extended import jwt_required
import traceback

logging.basicConfig(level=logging.DEBUG)

@jwt_required()
def chart():
    try:
        # Получаем параметры запроса
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        operator_name = request.args.get('operator_name', '')
        
        # Логируем полученные данные
        logging.debug(f"Received start_date: {start_date}, end_date: {end_date}, operator_name: {operator_name}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Получаем список всех операторов для выпадающего списка
        query_operators = """
            SELECT DISTINCT operator_name
            FROM (
                SELECT operator_name FROM incoming_calls
                UNION ALL
                SELECT operator_name FROM outgoing_calls
            ) AS combined
            ORDER BY operator_name
        """
        logging.debug("Executing query_operators")
        cursor.execute(query_operators)
        operators = cursor.fetchall()  # Получаем список имен операторов
        logging.debug(f"Operators: {operators}")

        if start_date and end_date:
            # Запрос для количества звонков по операторам
            query_operator = """
                SELECT operator_name, COUNT(*) AS count
                FROM (
                    SELECT operator_name, call_date FROM incoming_calls
                    UNION ALL
                    SELECT operator_name, call_date FROM outgoing_calls
                ) AS combined
                WHERE call_date BETWEEN %s AND %s
                AND (%s = '' OR operator_name = %s)
                GROUP BY operator_name
            """
            logging.debug("Executing query_operator")
            cursor.execute(query_operator, (start_date, end_date, operator_name, operator_name))
            operator_data = cursor.fetchall()
            logging.debug(f"Operator data: {operator_data}")

            # Запрос для распределения результатов звонков
            query_result = """
                SELECT result, COUNT(*) AS count
                FROM (
                    SELECT result, call_date FROM incoming_calls
                    UNION ALL
                    SELECT result, call_date FROM outgoing_calls
                ) AS combined
                WHERE call_date BETWEEN %s AND %s
                GROUP BY result
            """
            logging.debug("Executing query_result")
            cursor.execute(query_result, (start_date, end_date))
            result_data = cursor.fetchall()
            logging.debug(f"Result data: {result_data}")

            # Запрос для общего количества звонков
            total_calls_query = """
                SELECT COUNT(*) 
                FROM (
                    SELECT * FROM incoming_calls
                    UNION ALL
                    SELECT * FROM outgoing_calls
                ) AS combined
                WHERE call_date BETWEEN %s AND %s
            """
            logging.debug("Executing total_calls_query")
            cursor.execute(total_calls_query, (start_date, end_date))
            total_calls_count = cursor.fetchone()[0]
            logging.debug(f"Total calls count: {total_calls_count}")

            cursor.close()
            conn.close()

            # Возвращаем данные в формате JSON
            return jsonify({
                'result_labels': [row[0] for row in result_data],
                'result_values': [row[1] for row in result_data],
                'total_calls_count': total_calls_count
            })

        # Если нет фильтров, рендерим начальную страницу
        query_operator = """
            SELECT operator_name, COUNT(*) AS count
            FROM (
                SELECT operator_name, call_date FROM incoming_calls
                UNION ALL
                SELECT operator_name, call_date FROM outgoing_calls
            ) AS combined
            GROUP BY operator_name
        """
        logging.debug("Executing query_operator for initial render")
        cursor.execute(query_operator)
        operator_data = cursor.fetchall()

        query_result = """
            SELECT result, COUNT(*) AS count
            FROM (
                SELECT result, call_date FROM incoming_calls
                UNION ALL
                SELECT result, call_date FROM outgoing_calls
            ) AS combined
            GROUP BY result
        """
        logging.debug("Executing query_result for initial render")
        cursor.execute(query_result)
        result_data = cursor.fetchall()

        cursor.close()
        conn.close()

        overall_operator_labels = [row[0] for row in operator_data]
        overall_operator_values = [row[1] for row in operator_data]
        overall_result_labels = [row[0] for row in result_data]
        overall_result_values = [row[1] for row in result_data]

        # Рендерим шаблон
        return render_template('chart.html',
                               overall_operator_labels=overall_operator_labels,
                               overall_operator_values=overall_operator_values,
                               overall_result_labels=overall_result_labels,
                               overall_result_values=overall_result_values,
                               operators=[row[0] for row in operators])  # Передаем операторов в шаблон

    except Exception as e:
        # Логируем ошибку и возвращаем код 500
        logging.error(f"Error occurred: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred on the server.'}), 500


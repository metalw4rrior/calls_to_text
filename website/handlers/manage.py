from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required
import psycopg2
from db import get_db_connection

manage_bp = Blueprint('manage', __name__, url_prefix='/manage')

@manage_bp.route('/', methods=['GET', 'POST'])
@jwt_required()
def manage():
    conn = get_db_connection()
    
    try:
        if request.method == 'POST':
            # Добавление категории
            if 'category_name' in request.form:
                category_name = request.form.get('category_name')
                if category_exists(conn, category_name):
                    flash('Категория уже существует.', 'error')
                else:
                    add_category(conn, category_name)
                    flash('Категория успешно добавлена.', 'success')

            # Удаление категории
            elif 'delete_category' in request.form:
                category_id = request.form.get('category_id')
                delete_category(conn, category_id)
                flash('Категория успешно удалена.', 'success')

            # Добавление ключевого слова
            elif 'keyword_category' in request.form and 'keyword' in request.form:
                category_name = request.form.get('keyword_category')
                keyword = request.form.get('keyword')
                if keyword_exists(conn, category_name, keyword):
                    flash('Ключевая фраза уже существует в категории.', 'error')
                else:
                    add_keyword(conn, category_name, keyword)
                    flash('Ключевая фраза успешно добавлена.', 'success')

            # Удаление ключевого слова
            elif 'delete_keyword' in request.form:
                keyword_id = request.form.get('keyword_id')
                delete_keyword(conn, keyword_id)
                flash('Ключевая фраза успешно удалена.', 'success')

            # Назначение оператора
            elif 'assign_operator' in request.form:
                category_id = request.form.get('category_id')
                operator_id = request.form.get('operator_id')
                if not is_operator_assigned(conn, category_id, operator_id):
                    assign_operator(conn, category_id, operator_id)
                    flash('Оператор успешно назначен на категорию.', 'success')
                else:
                    flash('Оператор уже назначен на эту категорию.', 'error')

            # Удаление оператора из категории
            elif 'remove_operator' in request.form:
                category_id = request.form.get('category_id')
                operator_id = request.form.get('operator_id')
                if is_operator_assigned(conn, category_id, operator_id):
                    remove_operator(conn, category_id, operator_id)
                    flash('Оператор успешно удален из категории.', 'success')

        categories = get_categories_from_db(conn)
        keywords = get_keywords_from_db(conn)
        operators = get_operators_from_db(conn)
        assigned_operators = get_assigned_operators(conn)

        return render_template('manage.html', categories=categories, keywords=keywords, operators=operators, assigned_operators=assigned_operators)
    
    finally:
        conn.close()

# Функции работы с базой данных

def add_category(conn, category_name):
    with conn.cursor() as cursor:
        try:
            cursor.execute('INSERT INTO call_categories (name) VALUES (%s)', (category_name,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Произошла ошибка при добавлении категории: {e}", 'error')

def delete_category(conn, category_id):
    with conn.cursor() as cursor:
        try:
            cursor.execute('DELETE FROM call_categories WHERE id = %s', (category_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Произошла ошибка при удалении категории: {e}", 'error')

def add_keyword(conn, category_name, keyword):
    with conn.cursor() as cursor:
        try:
            cursor.execute('SELECT id FROM call_categories WHERE name = %s', (category_name,))
            category_id = cursor.fetchone()
            if category_id:
                cursor.execute('INSERT INTO category_phrases (category_id, text) VALUES (%s, %s)', (category_id[0], keyword))
                conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Произошла ошибка при добавлении ключевого слова: {e}", 'error')

def delete_keyword(conn, keyword_id):
    with conn.cursor() as cursor:
        try:
            cursor.execute('DELETE FROM category_phrases WHERE id = %s', (keyword_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Произошла ошибка при удалении ключевого слова: {e}", 'error')

def assign_operator(conn, category_id, operator_id):
    with conn.cursor() as cursor:
        try:
            cursor.execute('INSERT INTO call_category_operator (category_id, operator_id) VALUES (%s, %s)', (category_id, operator_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Произошла ошибка при назначении оператора: {e}", 'error')

def remove_operator(conn, category_id, operator_id):
    with conn.cursor() as cursor:
        try:
            cursor.execute('DELETE FROM call_category_operator WHERE category_id = %s AND operator_id = %s', (category_id, operator_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            flash(f"Произошла ошибка при удалении оператора: {e}", 'error')

# Вспомогательные функции для проверки существования записей

def category_exists(conn, category_name):
    with conn.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM call_categories WHERE name = %s', (category_name,))
        return cursor.fetchone()[0] > 0

def keyword_exists(conn, category_name, keyword):
    with conn.cursor() as cursor:
        cursor.execute('SELECT id FROM call_categories WHERE name = %s', (category_name,))
        category_id = cursor.fetchone()
        if category_id:
            cursor.execute('SELECT COUNT(*) FROM category_phrases WHERE category_id = %s AND text = %s', (category_id[0], keyword))
            return cursor.fetchone()[0] > 0
        return False

def is_operator_assigned(conn, category_id, operator_id):
    with conn.cursor() as cursor:
        cursor.execute('SELECT COUNT(*) FROM call_category_operator WHERE category_id = %s AND operator_id = %s', (category_id, operator_id))
        return cursor.fetchone()[0] > 0

# Функции для получения данных из базы данных

def get_categories_from_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, name FROM call_categories ORDER BY name;")
        return cursor.fetchall()

def get_keywords_from_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT cp.id, cc.name AS category_name, cp.text
            FROM category_phrases cp
            JOIN call_categories cc ON cp.category_id = cc.id
            ORDER BY cc.name, cp.text;
        """)
        return cursor.fetchall()

def get_operators_from_db(conn):
    with conn.cursor() as cursor:
        cursor.execute("SELECT id, operator_name FROM call_operators ORDER BY operator_name;")
        return cursor.fetchall()

def get_assigned_operators(conn):
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT cc.name AS category_name, co.operator_name AS operator_name
            FROM call_category_operator cco
            JOIN call_categories cc ON cco.category_id = cc.id
            JOIN call_operators co ON cco.operator_id = co.id
            ORDER BY cc.name, co.operator_name;
        """)
        return cursor.fetchall()


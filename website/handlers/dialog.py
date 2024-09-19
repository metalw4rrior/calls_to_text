# handlers/dialog.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required
from db import get_db_connection, get_keywords_from_db, get_categories_from_db

# Создаем Blueprint для маршрута dialog
dialog = Blueprint('dialog', __name__)

@dialog.route('/dialog', methods=['GET', 'POST'])
@jwt_required()
def manage_keywords():
    conn = get_db_connection()
    error_message = None
    success_message = None
    
    try:
        if request.method == 'POST':
            if 'category' in request.form and 'keyword' in request.form:
                category = request.form.get('category')
                keyword = request.form.get('keyword')

                if keyword_exists(conn, category, keyword):
                    error_message = 'Ключевая фраза уже существует в списке.'
                else:
                    add_keyword(conn, category, keyword)
                    success_message = 'Ключевая фраза успешно добавлена.'
            
            if 'keyword_id' in request.form:
                keyword_id = request.form.get('keyword_id')
                delete_keyword(conn, keyword_id)
                success_message = 'Ключевая фраза успешно удалена.'
            
            return render_template('dialog.html', keywords=get_keywords_from_db(conn), categories=get_categories_from_db(conn), error_message=error_message, success_message=success_message)

        keywords = get_keywords_from_db(conn)
        categories = get_categories_from_db(conn)
        
        return render_template('dialog.html', keywords=keywords, categories=categories, error_message=error_message, success_message=success_message)
    
    finally:
        conn.close()
def add_keyword(conn, category_name, keyword):
    with conn.cursor() as cursor:
        try:
            category_id_query = 'SELECT id FROM categories WHERE name = %s'
            cursor.execute(category_id_query, (category_name,))
            category_id = cursor.fetchone()
            if category_id:
                cursor.execute('INSERT INTO keywords (category_id, keyword) VALUES (%s, %s)', (category_id[0], keyword))
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"An error occurred: {e}")

def delete_keyword(conn, keyword_id):
    with conn.cursor() as cursor:
        try:
            cursor.execute('DELETE FROM keywords WHERE id = %s', (keyword_id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"An error occurred: {e}")

def keyword_exists(conn, category_name, keyword):
    with conn.cursor() as cursor:
        # Получаем ID категории
        category_id_query = 'SELECT id FROM categories WHERE name = %s'
        cursor.execute(category_id_query, (category_name,))
        category_id = cursor.fetchone()
        
        if category_id:
            # Проверяем наличие ключевого слова в категории
            keyword_query = 'SELECT COUNT(*) FROM keywords WHERE category_id = %s AND keyword = %s'
            cursor.execute(keyword_query, (category_id[0], keyword))
            count = cursor.fetchone()[0]
            return count > 0
        
        return False


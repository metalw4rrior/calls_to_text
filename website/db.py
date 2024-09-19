import psycopg2
from psycopg2 import sql
from typing import Dict, List, Tuple

def get_db_connection() -> psycopg2.extensions.connection:
    """Устанавливает соединение с базой данных и возвращает объект соединения."""
    conn = psycopg2.connect(
        dbname='',
        user='',
        password='',
        host='',
        port='6432'
    )
    return conn

def get_user(username: str) -> Tuple[str, str]:
    """Возвращает пользователя по имени пользователя."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("SELECT username, password_hash FROM users WHERE username = %s")
    cursor.execute(query, (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def add_user(username: str, password_hash: str):
    """Добавляет нового пользователя в базу данных."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("INSERT INTO users (username, password_hash) VALUES (%s, %s)")
    cursor.execute(query, (username, password_hash))
    conn.commit()
    cursor.close()
    conn.close()

def save_token(username: str, token: str, expires_at: str):
    """Сохраняет токен пользователя в базе данных."""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("INSERT INTO tokens (username, token, expires_at) VALUES (%s, %s, %s)")
    cursor.execute(query, (username, token, expires_at))
    conn.commit()
    cursor.close()
    conn.close()

def revoke_token(token: str):
    """Отзывает токен, устанавливая флаг is_revoked в TRUE."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = sql.SQL("UPDATE tokens SET is_revoked = TRUE WHERE token = %s")
        cursor.execute(query, (token,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Ошибка отзыва токена: {e}")
    finally:
        cursor.close()
        conn.close()

def is_token_revoked(token: str) -> bool:
    """Проверяет, отозван ли токен."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = sql.SQL("SELECT is_revoked FROM tokens WHERE token = %s")
        cursor.execute(query, (token,))
        result = cursor.fetchone()
        return result[0] if result else True
    finally:
        cursor.close()
        conn.close()
def get_keywords_from_db(conn) -> Dict[str, List[Dict[str, str]]]:
    cursor = conn.cursor()
    query = '''
    SELECT c.name AS category, k.id, k.keyword
    FROM keywords k
    JOIN categories c ON k.category_id = c.id
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    
    keyword_dict = {}
    for row in rows:
        category = row[0]
        keyword = row[2]
        keyword_id = row[1]
        if category not in keyword_dict:
            keyword_dict[category] = []
        keyword_dict[category].append({'id': keyword_id, 'keyword': keyword})
    
    return keyword_dict

def get_categories_from_db(conn) -> List[Dict[str, str]]:
    cursor = conn.cursor()
    query = 'SELECT id, name FROM categories'
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    
    return [{'id': row[0], 'name': row[1]} for row in rows]

def add_keyword(conn, category_name, keyword):
    cursor = conn.cursor()
    try:
        category_id_query = 'SELECT id FROM categories WHERE name = %s'
        cursor.execute(category_id_query, (category_name,))
        category_id = cursor.fetchone()
        if category_id:
            cursor.execute('INSERT INTO keywords (category_id, keyword) VALUES (%s, %s)', (category_id[0], keyword))
            conn.commit()
    finally:
        cursor.close()

def delete_keyword(conn, keyword_id):
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM keywords WHERE id = %s', (keyword_id,))
        conn.commit()
    finally:
        cursor.close()

# add_user.py

import psycopg2
from werkzeug.security import generate_password_hash
from db import get_db_connection

def add_user_to_db(username, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        cursor.execute(query, (username, password_hash))
        conn.commit()
        print(f"Пользователь '{username}' успешно добавлен.")
    except psycopg2.IntegrityError:
        conn.rollback()
        print(f"Пользователь '{username}' уже существует.")
    finally:
        cursor.close()
        conn.close()

def main():
    print("Добавление нового пользователя")
    username = input("Введите логин: ")
    password = input("Введите пароль: ")

    # Хэширование пароля
    password_hash = generate_password_hash(password)

    add_user_to_db(username, password_hash)

if __name__ == "__main__":
    main()


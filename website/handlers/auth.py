from flask import request, jsonify, render_template, redirect, url_for, make_response
from flask_jwt_extended import create_access_token, set_access_cookies, jwt_required, get_jwt_identity, unset_jwt_cookies
from psycopg2 import sql

from werkzeug.security import check_password_hash
import bcrypt
from db import get_user, add_user, save_token, revoke_token, get_db_connection
from datetime import datetime, timedelta
def login():
    if request.method == 'POST':
        username = request.form.get("username", None)
        password = request.form.get("password", None)

        user = get_user(username)
        if not user or not check_password_hash(user[1], password):
            return render_template("login.html", error="Неправильное имя пользователя или пароль")

        access_token = create_access_token(identity=username)
        expires_at = datetime.utcnow() + timedelta(hours=5)  # Установите время истечения

        save_token(username, access_token, expires_at)
        response = make_response(redirect(url_for('app.index')))
        set_access_cookies(response, access_token)
        return response

    return render_template("login.html")

def logout():
    response = redirect(url_for('app.login'))
    token = get_jwt_identity()  # Получите текущий токен
    conn = get_db_connection()
    cursor = conn.cursor()
    query = sql.SQL("UPDATE tokens SET is_revoked = TRUE WHERE token = %s")
    cursor.execute(query, (token,))
    conn.commit()
    cursor.close()
    conn.close()
    unset_jwt_cookies(response)  # Удаление JWT токенов из куки
    return response

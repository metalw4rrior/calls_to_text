from flask import Flask, redirect, url_for
from flask_jwt_extended import JWTManager
from routes import app as routes_blueprint

def create_app():
    app = Flask(__name__)

    # Настройка секрета для сессий и безопасности
    app.config['SECRET_KEY'] = 'a_secret_key_for_session_management'  # Установите свой секретный ключ здесь
    app.config['JWT_SECRET_KEY'] = 'secret key'
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = False
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    # Инициализация JWT Manager
    jwt = JWTManager(app)

    # Обработчик для перенаправления на страницу логина, если токен отсутствует
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return redirect(url_for('app.login'))

    # Обработчик для перенаправления на страницу логина, если токен истек
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return redirect(url_for('app.login'))

    # Регистрация Blueprint
    app.register_blueprint(routes_blueprint)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='host', port=8000, debug=True)

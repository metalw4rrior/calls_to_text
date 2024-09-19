from flask import Blueprint
from flask_jwt_extended import jwt_required
from handlers.index import index
from handlers.operators import operators
from handlers.chart import chart
from handlers.filtered_data import filtered_data
from handlers.auth import login, logout
from handlers.manage import manage
from handlers.dialog import manage_keywords

# Blueprint для всех маршрутов
app = Blueprint('app', __name__)

# Открытые маршруты
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])

# Защищенные маршруты
app.add_url_rule('/', 'index', jwt_required()(index))
app.add_url_rule('/logout', 'logout', jwt_required()(logout), methods=['POST'])
app.add_url_rule('/operators', 'operators', jwt_required()(operators), methods=['GET'])
app.add_url_rule('/chart', 'chart', jwt_required()(chart))
app.add_url_rule('/filtered-data', 'filtered_data', jwt_required()(filtered_data), methods=['GET'])
app.add_url_rule('/dialog', 'manage_keywords', jwt_required()(manage_keywords), methods=['GET', 'POST'])
app.add_url_rule('/manage', 'manage', jwt_required()(manage), methods=['GET', 'POST'])

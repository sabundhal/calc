from flask import Flask, jsonify, request
from flasgger import Swagger
from sqlalchemy import and_, between
import requests
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import sqlite3
import hashlib
from antipyretic_calculator import calculateAntipyreticDosage
import os
from creds import *
from data import *
import re
from contextlib import closing
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError

# Инициализация DatabaseManager
db_manager = DatabaseManager()

# Создание Flask-приложения
app = Flask(__name__)


# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('myapp.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Устанавливаем row_factory для доступа по именам колонок
    cursor = conn.cursor()
    return cursor




def validate_input(data):
    if not all(data.values()):
        return ERRORS['fields_required']

    username, email, password = data['username'], data['email'], data['password']

    if not 3 <= len(username) <= 30:
        return ERRORS['username_length']
    if not VALIDATORS['username'].match(username):
        return ERRORS['username_format']
    if not VALIDATORS['email'].match(email):
        return ERRORS['email_format']
    if not 8 <= len(password) <= 30:
        return ERRORS['password_length']
    if not VALIDATORS['password'].match(password):
        return ERRORS['password_strength']

    return None


# @app.route('/api/register', methods=['POST'])
# def register_user():
#     try:
#         data = {
#             'username': request.json.get('username', '').strip(),
#             'email': request.json.get('email', '').strip(),
#             'password': request.json.get('password', '')
#         }
#
#         if error := validate_input(data):
#             return jsonify({'message': error[0]}), error[1]
#
#         with closing(sqlite3.connect('myapp.db')) as conn:
#             with conn:  # Автокоммит
#                 cursor = conn.cursor()
#
#                 # Проверка уникальности
#                 if cursor.execute("SELECT 1 FROM users WHERE username = ?",
#                                   (data['username'],)).fetchone():
#                     return jsonify({'message': ERRORS['username_exists'][0]}), 409
#
#                 if cursor.execute("SELECT 1 FROM users WHERE email = ?",
#                                   (data['email'],)).fetchone():
#                     return jsonify({'message': ERRORS['email_exists'][0]}), 409
#
#                 # Создание пользователя
#                 cursor.execute(
#                     "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
#                     (data['username'], data['email'],
#                      hashlib.sha256(data['password'].encode()).hexdigest())
#                 )
#
#         return jsonify({'message': 'User registered successfully'}), 201
#
#     except sqlite3.Error as e:
#         return jsonify({'message': ERRORS['db_error'][0]}), 500



@app.route('/api/register', methods=['POST'])
def register_user():
    try:
        data = {
            'username': request.json.get('username', '').strip(),
            'email': request.json.get('email', '').strip(),
            'password': request.json.get('password', '')
        }

        # Валидация данных
        if error := validate_input(data):
            return jsonify({'message': error[0]}), error[1]

        # Создание сессии
        session = db_manager.Session()

        # Проверка уникальности username и email
        if session.query(User).filter_by(username=data['username']).first():
            session.close()
            return jsonify({'message': ERRORS['username_exists'][0]}), 409

        if session.query(User).filter_by(email=data['email']).first():
            session.close()
            return jsonify({'message': ERRORS['email_exists'][0]}), 409

        # Создание нового пользователя
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=hashlib.sha256(data['password'].encode()).hexdigest()
        )

        # Добавление пользователя в сессию и сохранение в БД
        session.add(new_user)
        session.commit()

        return jsonify({'message': 'User registered successfully'}), 201

    except IntegrityError as e:
        session.rollback()
        return jsonify({'message': ERRORS['db_error'][0]}), 500
    except Exception as e:
        session.rollback()
        return jsonify({'message': ERRORS['db_error'][0]}), 500
    finally:
        session.close()






@app.route('/api/login', methods=['POST'])
def login_user():
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("SELECT id FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = cursor.fetchone()

    if not user:
        return jsonify({'message': 'Неверные учетные данные'}), 401
        # Получаем user_id
    user_id = user[0]
    access_token = create_access_token(identity=username)
    # Возвращаем токен и user_id
    return jsonify(access_token=access_token, user_id=user_id), 200

###yandex


# @app.route('/api/auth/yandex', methods=['POST'])
# def handle_yandex_auth():
#     token = request.json.get('token')
#
#     if not token:
#         return jsonify({"error": "Токен отсутствует"}), 400
#
#     try:
#         # Получаем данные пользователя
#         user_info = get_user_info(token)
#         yandex_id = user_info["id"]  # Уникальный ID Яндекса
#         # Проверяем, есть ли пользователь в БД
#         conn = sqlite3.connect('myapp.db')
#         cursor = conn.cursor()
#         cursor.execute("SELECT * FROM users WHERE yandex_id = ?", (yandex_id,))
#         user = cursor.fetchone()
#
#         if not user:
#             # Пользователя нет, создаем его
#             username = user_info.get("login")
#             email = user_info.get("default_email", user_info.get("emails", [None])[0])
#             password = yandex_id  # Пароль = yandex_id (или можно оставить NULL)
#             hashed_password = hashlib.sha256(password.encode()).hexdigest()
#             cursor.execute(
#                 "INSERT INTO users (username, email, password, is_yandex, yandex_id) VALUES (?, ?, ?, ?, ?)",
#                 (username, email, hashed_password, 1, yandex_id)
#             )
#             conn.commit()  # Сохраняем изменения в БД
#
#             # Получаем только что созданного пользователя
#             cursor.execute("SELECT * FROM users WHERE yandex_id = ?", (yandex_id,))
#             user = cursor.fetchone()
#         return jsonify({"success": True, "user": user_info})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500



@app.route('/api/auth/yandex', methods=['POST'])
def handle_yandex_auth():
    token = request.json.get('token')

    if not token:
        return jsonify({"error": "Токен отсутствует"}), 400

    try:
        # Получаем данные пользователя
        user_info = get_user_info(token)
        yandex_id = user_info["id"]  # Уникальный ID Яндекса

        # Создание сессии
        session = db_manager.Session()

        # Проверяем, есть ли пользователь в БД
        user = session.query(User).filter_by(yandex_id=yandex_id).first()

        if not user:
            # Пользователя нет, создаем его
            username = user_info.get("login")
            email = user_info.get("default_email", user_info.get("emails", [None])[0])
            password = yandex_id  # Пароль = yandex_id (или можно оставить NULL)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                is_yandex=1,
                yandex_id=yandex_id
            )

            # Добавляем пользователя в сессию и сохраняем в БД
            session.add(new_user)
            session.commit()

            # Получаем только что созданного пользователя
            user = session.query(User).filter_by(yandex_id=yandex_id).first()

        return jsonify({"success": True, "user": user_info})

    except IntegrityError as e:
        session.rollback()
        return jsonify({"error": "Ошибка базы данных: пользователь уже существует"}), 500
    except Exception as e:
        session.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        session.close()



def get_user_info(token):
    url = "https://login.yandex.ru/info"
    headers = {"Authorization": f"OAuth {token}"}
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Ошибка: {response.status_code}, {response.text}")


# ###Calculator
# @app.route('/api/drugs', methods=['GET'])
# #@jwt_required()  # Защищаем маршрут JWT-токеном
# def get_drugs():
#     cursor = get_db_connection()
#     try:
#         # Выполняем SQL-запрос
#         cursor.execute('''
#             SELECT d.id, d.name, d.tablet_only, d.mls_var, d.instructions, dc.category_name
#             FROM drugs d
#             JOIN drugs_categories dc ON d.category_id = dc.category_id
#             ORDER BY dc.category_name, d.name
#         ''')
#         drugs = cursor.fetchall()
#
#         # Группируем препараты по категориям
#         drugs_by_categories = {}
#         for drug in drugs:
#             category_name = drug['category_name']
#             if category_name not in drugs_by_categories:
#                 drugs_by_categories[category_name] = []
#             drugs_by_categories[category_name].append({
#                 'id': drug['id'],
#                 'name': drug['name'],
#                 'tablet_only': drug['tablet_only'],
#                 'mls_var': drug['mls_var'],
#                 'instructions': drug['instructions']
#             })
#
#         return jsonify(drugs_by_categories)
#     except Exception as e:
#         print(f"Database error: {e}")
#         return jsonify({"error": "Failed to fetch drugs from the database."}), 500
#     finally:
#         cursor.connection.close()  # Закрываем соединение через курсор


@app.route('/api/drugs', methods=['GET'])
def get_drugs():
    try:
        # Создание сессии
        session = db_manager.Session()

        # Выполняем запрос с JOIN и сортировкой
        drugs = session.query(Drug, DrugsCategory.category_name) \
            .join(DrugsCategory, Drug.category_id == DrugsCategory.category_id) \
            .order_by(DrugsCategory.category_name, Drug.name) \
            .all()

        # Группируем препараты по категориям
        drugs_by_categories = {}
        for drug, category_name in drugs:
            if category_name not in drugs_by_categories:
                drugs_by_categories[category_name] = []
            drugs_by_categories[category_name].append({
                'id': drug.id,
                'name': drug.name,
                'tablet_only': drug.tablet_only,
                'mls_var': drug.mls_var,
                'instructions': drug.instructions
            })

        return jsonify(drugs_by_categories)

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"error": "Failed to fetch drugs from the database."}), 500
    finally:
        session.close()  # Закрываем сессию


##Расчет дозировки и сохранение в БД@app.route('/calculate', methods=['POST'])
@app.route('/api/calculate', methods=['POST'])
def calculate_dosage():
    data = request.json
    try:
        result = calculateAntipyreticDosage(data)
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400



# #############
# @app.route('/api/calculation-history/', methods=['GET'])
# def get_calculation_history():
#     user_id = request.args.get('user_id')
#     category_name = request.args.get('category_name', default=None, type=str)
#     date_from = request.args.get('date_from', default=None, type=str)
#     date_to = request.args.get('date_to', default=None, type=str)
#
#     # Проверяем наличие обязательного параметра
#     if not user_id:
#         return jsonify({'error': 'user_id is required'}), 400
#
#     try:
#         conn = sqlite3.connect('myapp.db')
#         cursor = conn.cursor()
#
#         # Формируем SQL-запрос с JOIN
#         query = '''SELECT ch.*
#                    FROM calculation_history ch
#                    JOIN drugs_categories dc ON ch.calculation_type = dc.category_id
#                    WHERE ch.user_id = ?'''
#         params = [user_id]
#
#         # Добавляем фильтры, если они переданы
#         if category_name:
#             query += ' AND dc.category_name = ?'
#             params.append(category_name)
#
#         if date_from and date_to:
#             query += ' AND ch.created_at BETWEEN ? AND ?'
#             params.extend([date_from, date_to])
#
#         # Выполняем запрос
#         cursor.execute(query, params)
#         history = cursor.fetchall()
#
#         # Преобразуем данные в формат JSON
#         result = []
#         for row in history:
#             result.append({
#                 'id': row[0],  # id
#         'user_id': row[2],  # user_id
#         'drug_name': row[4],  # drug_name
#         'calculation_type': row[18],
#         'weight': row[6],       # calculation_type
#         'standard_dose_ml': row[7],  # dosage_mls
#         'high_dose_ml': row[10],
#         'suppositories_high': row[16],
#         'suppositories_min': row[17],
#
#         'created_at': row[24]  # calculation_time
#     })
#         return jsonify(result), 200
#
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
#
#     finally:
#         conn.close()
#  ########


@app.route('/api/calculation-history/', methods=['GET'])
def get_calculation_history():
    user_id = request.args.get('user_id')
    category_name = request.args.get('category_name', default=None, type=str)
    date_from = request.args.get('date_from', default=None, type=str)
    date_to = request.args.get('date_to', default=None, type=str)

    # Проверяем наличие обязательного параметра
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400

    try:
        # Создание сессии
        session = db_manager.Session()

        # Формируем базовый запрос
        query = session.query(CalculationHistory).join(
            DrugsCategory, CalculationHistory.calculation_type == DrugsCategory.category_id
        ).filter(CalculationHistory.user_id == user_id)

        # Добавляем фильтры, если они переданы
        if category_name:
            query = query.filter(DrugsCategory.category_name == category_name)

        if date_from and date_to:
            # Преобразуем строки в объекты datetime
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(between(CalculationHistory.calculation_time, date_from, date_to))

        # Выполняем запрос
        history = query.all()

        # Преобразуем данные в формат JSON
        result = []
        for row in history:
            result.append({
                'id': row.id,
                'user_id': row.user_id,
                'drug_name': row.drug_name,
                'calculation_type': row.calculation_type,
                'weight': row.weight,
                'standard_dose_ml': row.dosage_mls,
                'high_dose_ml': row.highMgs,
                'suppositories_high': row.suppositories_high,
                'suppositories_min': row.suppositories_min,
                'created_at': row.calculation_time.strftime('%Y-%m-%d %H:%M:%S')  # Форматируем дату
            })

        return jsonify(result), 200

    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()  # Закрываем сессию




# Запуск приложения
if __name__ == '__main__':
    # Инициализация базы данных
    initialize_database()
    # populate_initial_data()
    app.config['SWAGGER'] = {
        'title': 'Calculator API',
        'host': 'localhost:8080',
        'uiversion': 3,
        'specs_route': '/apidocs/',
        'swagger_ui_bundle_js': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.3/swagger-ui-bundle.js',
        'swagger_ui_standalone_preset_js': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.3/swagger-ui-standalone-preset.js',
        'swagger_ui_css': 'https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.10.3/swagger-ui.css',
        'jquery_js': 'https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js'
    }
    Swagger(app, template_file='swagger.yaml')

    # Настройка JWT
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Замените 'your-secret-key' на ваш секретный ключ
    jwt = JWTManager(app)
    # Настройка CORS
    CORS(app)
    app.run()

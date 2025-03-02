from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import sqlite3
import hashlib

from data import DatabaseManager, Drug , CalculationHistory
db_manager = DatabaseManager()
##Расчет дозировки и сохранение в БД@app.route('/calculate', methods=['POST'])
# @app.route('/api/calculate', methods=['POST'])
# #@jwt_required()  # Защищаем маршрут JWT-токеном
# def calculate_dosage():
#     data = request.json
#     user_id = data.get('user_id')
#     drug_id = data.get('drug_id')
#     weight = data.get('weight')
#     weight = float(weight)
#
#     # Проверяем наличие обязательных параметров
#     if user_id is None or drug_id is None or weight is None:
#         return jsonify({'error': 'user_id, drug_id, and weight are required'}), 400
#     # Проверяем корректность веса
#     if weight <= 0:
#         return jsonify({'error': 'Weight must be greater than 0'}), 400
#     # Получаем данные о препарате из базы данных
#     try:
#         conn = sqlite3.connect('myapp.db')
#         cursor = conn.cursor()
#
#         # Запрос данных о препарате
#         #можно ли тут написать. select *?
#         cursor.execute('''SELECT name, category_id, mls_var, mgs_var
#                           FROM drugs
#                           WHERE id = ?''', (drug_id,))
#         drug = cursor.fetchone()
#
#         if not drug:
#             conn.close()
#             return jsonify({'error': 'Drug not found'}), 404
#
#         # Извлекаем данные из результата запроса
#         name, category_id, mls_var, mgs_var = drug
#
#         # Выполняем расчеты
#         mls_total = weight * mls_var
#         mgs_total = weight * mgs_var
#
#         # Сохраняем расчет в историю
#         # Установка значений для всех 23 полей
#         cursor.execute('''
#             INSERT INTO calculation_history (
#                 user_id, calculation_id, drug_id, drug_name, username, weight, dosage_mls, dosage_mgs,
#                 totalMgs, totalhigh, totalhighsachets, maximumMgsPerDay, highMgs,
#                 loading_dose, strep_drug, messageMgs, messageOther, calculation_type,
#                 calculation_status, calculation_version, patient_id, patient_name, error_message, age
#             ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)''',
#                        (
#                            user_id, None, drug_id, name, 'Username', weight, mls_total, mgs_total,
#                            0, 0, 0, 0, 0, 0, 0, 'Message', None, category_id,
#                            'Status', 'Version', 0, 'Patient Name', None , None
#                        ))
#         # Получаем автоматически сгенерированный id
#         calculation_id = cursor.lastrowid
#         # Обновляем запись, чтобы установить calculation_id равным id
#         cursor.execute('''
#             UPDATE calculation_history
#             SET calculation_id = ?
#             WHERE id = ?''',
#                        (calculation_id, calculation_id))
#         conn.commit()
#
#
#     except sqlite3.Error as e:
#         return jsonify({'error': f'Database error: {str(e)}'}), 500
#
#         # Возвращаем ответ с calculation_id
#     return jsonify({
#             'mlsTotal': mls_total,
#             'mgsTotal': mgs_total,
#             'calculation_id': calculation_id
#         })
#     conn.close()


def validateInput(data):
    """
    Проверяет корректность входных данных.
    :param data: Входные данные (user_id, drug_id, weight)
    :raises ValueError: Если данные некорректны
    """
    if not all(k in data for k in ['user_id', 'drug_id', 'weight']):
        raise ValueError("user_id, drug_id, and weight are required")
    try:
        weight = float(data['weight'])
        if weight <= 0:
            raise ValueError("Weight must be greater than 0")
    except ValueError:
        raise ValueError("Weight must be a valid number")

# def fetchDrugInfo(drug_id):
#     """
#     Получает данные о препарате из базы данных.
#     :param drug_id: ID препарата
#     :return: Словарь с данными о препарате
#     :raises ValueError: Если препарат не найден или произошла ошибка БД
#     """
#     try:
#         conn = sqlite3.connect('myapp.db')
#         cursor = conn.cursor()
#         cursor.execute('''SELECT name, category_id, mls_var, mgs_var, mls_max, mgs_max, high_range, high_modifier, mls_max_high, mgs_max_high, instructions, nzf_link, number_of_times_a_day, range1_dose,range2_dose
#                                  FROM drugs
#                                  WHERE id = ?''', (drug_id,))
#         drug = cursor.fetchone()
#         if not drug:
#             raise ValueError("Drug not found")
#         return {
#             'name': drug[0],                 # Название препарата
#             'category_id': drug[1],          # ID категории
#             'mls_var': drug[2],              # Объем на одну дозу (мл)
#             'mgs_var': drug[3],              # Доза на одну дозу (мг)
#             'mls_max': drug[4],              # Максимальный объем в сутки (мл)
#             'mgs_max': drug[5],              # Максимальная доза в сутки (мг)
#             'high_range': drug[6],           # Флаг для высокой дозировки
#             'high_modifier': drug[7],        # Модификатор для высокой дозировки
#             'mls_max_high': drug[8],         # Максимальный объем для высокой дозировки (мл)
#             'mgs_max_high': drug[9],
#             'instructions': drug[10],
#             'nzf_link': drug[11],
#             'number_of_times_a_day': drug[12],
#             'range1_dose': drug[13],
#             'range2_dose': drug[14]
#         }
#     except sqlite3.Error as e:
#         raise ValueError(f"Database error: {str(e)}")
#     finally:
#         conn.close()



def fetchDrugInfo(drug_id):
    """
    Получает данные о препарате из базы данных.
    :param drug_id: ID препарата
    :return: Словарь с данными о препарате
    :raises ValueError: Если препарат не найден или произошла ошибка БД
    """
    try:
        # Создание сессии
        session = db_manager.Session()

        # Выполняем запрос
        drug = session.query(Drug).filter_by(id=drug_id).first()
        if not drug:
            raise ValueError("Drug not found")

        # Возвращаем данные о препарате
        return {
            'name': drug.name,                 # Название препарата
            'category_id': drug.category_id,   # ID категории
            'mls_var': drug.mls_var,          # Объем на одну дозу (мл)
            'mgs_var': drug.mgs_var,          # Доза на одну дозу (мг)
            'mls_max': drug.mls_max,          # Максимальный объем в сутки (мл)
            'mgs_max': drug.mgs_max,          # Максимальная доза в сутки (мг)
            'high_range': drug.high_range,    # Флаг для высокой дозировки
            'high_modifier': drug.high_modifier,  # Модификатор для высокой дозировки
            'mls_max_high': drug.mls_max_high,  # Максимальный объем для высокой дозировки (мл)
            'mgs_max_high': drug.mgs_max_high,  # Максимальная доза для высокой дозировки (мг)
            'instructions': drug.instructions,  # Инструкции
            'nzf_link': drug.nzf_link,        # Ссылка на NZF
            'number_of_times_a_day': drug.number_of_times_a_day,  # Количество приемов в день
            'range1_dose': drug.range1_dose,  # Доза для диапазона 1
            'range2_dose': drug.range2_dose   # Доза для диапазона 2
        }

    except Exception as e:
        raise ValueError(f"Database error: {str(e)}")
    finally:
        session.close()  # Закрываем сессию

def calculateDosage(weight, drug_info):
    """
    Рассчитывает дозировку на основе веса пациента.
    :param weight: Вес пациента (кг)
    :param drug_info: Данные о препарате (mls_var, mgs_var, range1_dose, category_id)
    :return: Словарь с результатами расчета
    """
    result = {
        'standard_dose_ml': None,  # Стандартный объем на одну дозу (мл)
        'standard_dose_mg': None,  # Стандартная доза на одну дозу (мг)
        'high_dose_ml': None,  # Высокий объем на одну дозу (мл)
        'high_dose_mg': None,  # Высокая доза на одну дозу (мг)
        'max_dose_ml': None,  # Максимальный объем в сутки (мл)
        'max_dose_mg': None,  # Максимальная доза в сутки (мг)
        'suppositories_min': None,  # Минимальное количество свечей
        'suppositories_high': None  # Максимальное количество свечей
    }


    # Проверка на ректальные свечи (category_id = 6)
    if drug_info.get('category_id') == 6:
        # Разовая доза: 5-10 мг/кг
        mgs_var = drug_info.get('mgs_var', None)
        dose_min = mgs_var * weight  # Минимальная доза (мг)

        # Если включена высокая дозировка (high_range = 1), применяем high_modifier
        if drug_info.get('high_range') == 1:
            high_modifier = drug_info.get('high_modifier', 1)
            dose_high = dose_min*high_modifier

        # Получаем количество мг в одной свече
        dose_per_suppository = drug_info.get('range1_dose', None)
        if dose_per_suppository is None:
            return result

        # Рассчитываем количество свечей (дробное)
        suppositories_min = dose_min / dose_per_suppository
        suppositories_high = dose_high / dose_per_suppository

        result['suppositories_min'] = round(suppositories_min, 1)
        result['suppositories_high'] = round(suppositories_high, 1)


    else:

        # Рассчитываем максимальные суточные дозы НОВЫЙ РАСЧЕТ
        if drug_info.get('mgs_max') is not None:
            result['max_dose_ml'] = (weight * drug_info['mgs_max']) / drug_info['range2_dose']
        # Стандартный расчет для других категорий
        result['standard_dose_ml'] = weight * drug_info.get('mls_var', None) if drug_info.get('mls_var') is not None else None
        result['standard_dose_mg'] = weight * drug_info.get('mgs_var', None) if drug_info.get('mgs_var') is not None else None

        # Проверка на высокую дозировку
        if drug_info.get('high_range') == 1:  # Если высокая дозировка разрешена
            # Применяем high_modifier, если все данные доступны
            mls_var = drug_info.get('mls_var', None)
            high_modifier = drug_info.get('high_modifier', None)
            mls_max = drug_info.get('mls_max', None)


            # Рассчитываем высокую дозу (мл), если все данные есть
            if mls_var is not None and high_modifier is not None:
                mls_high = weight * mls_var * high_modifier
                if mls_max is not None:
                    mls_high = min(mls_high, mls_max)
                result['high_dose_ml'] = mls_high

            # Аналогично для высокой дозы (мг)
            mgs_var = drug_info.get('mgs_var', None)
            mgs_max = drug_info.get('mgs_max', None)
            if mgs_var is not None and high_modifier is not None:
                mgs_high = weight * mgs_var * high_modifier
                if mgs_max is not None:
                    mgs_high = min(mgs_high, mgs_max)
                result['high_dose_mg'] = mgs_high

    return result
#def saveCalculationToDB(data, mls_total, mgs_total, drug_info, category_id, mls_high):
# def saveCalculationToDB(data, standard_dose_ml, standard_dose_mg, drug_info, category_id, high_dose_ml,suppositories_min, suppositories_high ):
#     """
#     Сохраняет результат расчета в базу данных.
#     :param data: Входные данные (user_id, drug_id, weight)
#     :param mls_total: Рассчитанный объем (мл)
#     :param mgs_total: Рассчитанная доза (мг)
#     :param drug_info: Данные о препарате
#     :return: ID расчета
#     :raises ValueError: Если произошла ошибка БД
#     """
#     try:
#         conn = sqlite3.connect('myapp.db')
#         cursor = conn.cursor()
#         cursor.execute('''
#                     INSERT INTO calculation_history (
#                         user_id, calculation_id, drug_id, drug_name, username, weight, dosage_mls, dosage_mgs,
#                         totalMgs, totalhigh, totalhighsachets, maximumMgsPerDay, highMgs,
#                         loading_dose, strep_drug, suppositories_high, suppositories_min, calculation_type,
#                         calculation_status, calculation_version, patient_id, patient_name, error_message, age
#                     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)''',
#                                (
#                                    data['user_id'], None, data['drug_id'], drug_info['name'], 'Username', float(data['weight']), standard_dose_ml, standard_dose_mg,
#                                    0, high_dose_ml, 0, 0, 0, 0, 0, suppositories_high, suppositories_min, category_id,
#                                    'Status', 'Version', 0, 'Patient Name', None , None))
#         calculation_id = cursor.lastrowid
#         # Обновляем запись, чтобы установить calculation_id равным id
#         cursor.execute('''
#                     UPDATE calculation_history
#                     SET calculation_id = ?
#                     WHERE id = ?''',
#                                (calculation_id, calculation_id))
#         conn.commit()
#         return calculation_id
#     except sqlite3.Error as e:
#         raise ValueError(f"Database error: {str(e)}")
#     finally:
#         conn.close()




def saveCalculationToDB(data, standard_dose_ml, standard_dose_mg, drug_info, category_id, high_dose_ml, suppositories_min, suppositories_high):
    """
    Сохраняет результат расчета в базу данных.
    :param data: Входные данные (user_id, drug_id, weight)
    :param standard_dose_ml: Рассчитанный объем (мл)
    :param standard_dose_mg: Рассчитанная доза (мг)
    :param drug_info: Данные о препарате
    :param category_id: ID категории
    :param high_dose_ml: Высокая доза (мл)
    :param suppositories_min: Минимальная доза суппозиториев
    :param suppositories_high: Максимальная доза суппозиториев
    :return: ID расчета
    :raises ValueError: Если произошла ошибка БД
    """
    try:
        # Создание сессии
        session = db_manager.Session()

        # Создаем объект CalculationHistory
        calculation = CalculationHistory(
            user_id=data['user_id'],
            calculation_id=None,  # Пока оставляем None
            drug_id=data['drug_id'],
            drug_name=drug_info['name'],
            username='Username',  # Заглушка, можно заменить на реальное имя пользователя
            weight=float(data['weight']),
            dosage_mls=standard_dose_ml,
            dosage_mgs=standard_dose_mg,
            totalMgs=0,  # Заглушка
            totalhigh=high_dose_ml,
            totalhighsachets=0,  # Заглушка
            maximumMgsPerDay=0,  # Заглушка
            highMgs=0,  # Заглушка
            loading_dose=0,  # Заглушка
            strep_drug=0,  # Заглушка
            suppositories_high=suppositories_high,
            suppositories_min=suppositories_min,
            calculation_type=category_id,
            calculation_status='Status',  # Заглушка
            calculation_version='Version',  # Заглушка
            patient_id=0,  # Заглушка
            patient_name='Patient Name',  # Заглушка
            error_message=None,
            age=None
        )

        # Добавляем объект в сессию
        session.add(calculation)
        session.commit()

        # Обновляем calculation_id
        calculation.calculation_id = calculation.id
        session.commit()

        return calculation.id

    except Exception as e:
        session.rollback()
        raise ValueError(f"Database error: {str(e)}")
    finally:
        session.close()  # Закрываем сессию


def calculateAntipyreticDosage(data):
    """
    Основная функция для расчета дозировки жаропонижающего препарата.
    :param data: Входные данные (user_id, drug_id, weight)
    :return: Словарь с результатами расчета
    :raises ValueError: Если произошла ошибка
    """
    validateInput(data)
    drug_info = fetchDrugInfo(data['drug_id'])
    category_id = drug_info['category_id']
    instructions = drug_info['instructions']
    nzf_link = drug_info['nzf_link']
    # Вызов calculateDosage, который возвращает нужные значения
    result = calculateDosage(float(data['weight']), drug_info)
    # Вызов saveCalculationToDB с новыми параметрами
    calculation_id = saveCalculationToDB(
        data,
        result['standard_dose_ml'],  # standard_dose_ml
        result['standard_dose_mg'],  # standard_dose_mg
        drug_info,
        category_id,
        result['high_dose_ml'], # high_dose_ml
        result['suppositories_min'],
        result['suppositories_high']
    )

    # Возвращаем все необходимые поля
    return {
        'standard_dose_ml': result['standard_dose_ml'],  # Стандартный объем (мл)
        'standard_dose_mg': result['standard_dose_mg'],  # Стандартная доза (мг)
        'high_dose_ml': result['high_dose_ml'],  # Высокий объем (мл)
        'high_dose_mg': result['high_dose_mg'],  # Высокая доза (мг)
        'max_dose_ml': result['max_dose_ml'],  # Максимальный объем (мл)
        'max_dose_mg': drug_info['mgs_max'],  # Максимальная доза (мг)
        'calculation_id': calculation_id,  # ID расчета
        'instructions': drug_info['instructions'],
        'nzf_link': drug_info['nzf_link'],
        'number_of_times_a_day': drug_info['number_of_times_a_day'],
        'suppositories_min': result['suppositories_min'],
        'suppositories_high': result['suppositories_high']
    }
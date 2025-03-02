from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

# Класс для работы с базой данных
class DatabaseManager:
    def __init__(self, db_url='sqlite:///myapp2.db'):
        self.engine = create_engine(db_url, echo=True)
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)  # Создание таблиц, если их нет


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    is_yandex = Column(Integer, default=0)
    yandex_id = Column(Integer, unique=True)


class DrugsCategory(Base):
    __tablename__ = 'drugs_categories'
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    # Добавляем отношение к Drug
    drugs = relationship("Drug", back_populates="category")

class CalculationHistory(Base):
    __tablename__ = 'calculation_history'
    id = Column(Integer, primary_key=True)
    calculation_id = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    drug_id = Column(Integer, ForeignKey('drugs.id'), nullable=False)
    drug_name = Column(String)
    username = Column(String)
    weight = Column(Float, nullable=False)
    dosage_mls = Column(Float)
    dosage_mgs = Column(Float)
    totalMgs = Column(Float)
    totalhigh = Column(Float)
    totalhighsachets = Column(Float)
    maximumMgsPerDay = Column(Float)
    highMgs = Column(Float)
    loading_dose = Column(Integer)
    strep_drug = Column(Integer)
    suppositories_high = Column(String)
    suppositories_min = Column(String)
    calculation_type = Column(String)
    calculation_status = Column(String)
    calculation_version = Column(String)
    patient_id = Column(Integer)
    patient_name = Column(String)
    error_message = Column(String)
    calculation_time = Column(DateTime, default=datetime.now)
    age = Column(Float)

class Drug(Base):
    __tablename__ = 'drugs'
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('drugs_categories.category_id'))
    name = Column(String, unique=True)
    tablet_only = Column(Integer)
    mls_var = Column(Float)
    mgs_var = Column(Float)
    number_of_times_a_day = Column(String)
    mls_max = Column(Float)
    mgs_max = Column(Float)
    loading_dose = Column(Integer)
    mls_var_loading = Column(Float)
    mgs_var_loading = Column(Float)
    mls_max_loading = Column(Float)
    mgs_max_loading = Column(Float)
    instructions = Column(String)
    nzf_link = Column(String)
    high_range = Column(Integer)
    high_modifier = Column(Float)
    mls_max_high = Column(Float)
    mgs_max_high = Column(Float)
    strep_drug = Column(Integer)
    strep_frequency = Column(String)
    mls_var_strep = Column(Float)
    mgs_var_strep = Column(Float)
    mls_strep_max = Column(Float)
    mgs_strep_max = Column(Float)
    weight_cutoff_1 = Column(Float)
    weight_cutoff_2 = Column(Float)
    range1_dose = Column(Float)
    range2_dose = Column(Float)
    form = Column(String)
    age_range = Column(Float)
    category = relationship("DrugsCategory", back_populates="drugs")



# Инициализация базы данных
def initialize_database():
    engine = create_engine('sqlite:///myapp2.db')
    Base.metadata.create_all(engine)
    print("Database initialized successfully.")

def populate_initial_data():
    engine = create_engine('sqlite:///myapp2.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Заполнение таблицы drugs_categories
        categories_objects = []
        for category_tuple in categories_data:
            category_dict = dict(zip(category_fields, category_tuple))  # Сопоставляем поля с данными
            category = DrugsCategory(**category_dict)  # Создаем объект DrugsCategory
            categories_objects.append(category)

        session.add_all(categories_objects)

        # Заполнение таблицы drugs
        drugs_objects = []
        for drug_tuple in drugs_data:
            drug_dict = dict(zip(drug_fields, drug_tuple))  # Сопоставляем поля с данными
            drug = Drug(**drug_dict)  # Создаем объект Drug
            drugs_objects.append(drug)

        session.add_all(drugs_objects)

        session.commit()
        print("Initial data populated successfully.")
    except Exception as e:
        session.rollback()
        print(f"Error populating initial data: {e}")
    finally:
        session.close()

categories_data = [
            (1, 'Analgesics'),
            (2, 'Antibiotics'),
            (3, 'Anti-inflammatory'),
            (4, 'Antipyretic'),
            (5, 'Antiviral'),
               (6, 'Rectal antipyretic')
        ]
category_fields = ['category_id', 'category_name']

users_data = [
    ('user1', 'user1@example.com', 'b6ad34b0b6b7e38f878a513b3f7927ebeb4cffb01aeb6d9fd9f9ad67fbc76517', 0, None),
    ('yandex_user', 'yandex_user@example.com', 'b6ad34b0b6b7e38f878a513b3f7927ebeb4cffb01aeb6d9fd9f9ad67fbc76517', 1, '123456789')
]

user_fields = ['username', 'email', 'password', 'is_yandex', 'yandex_id']

drug_fields = [
    'name', 'category_id', 'tablet_only', 'mls_var', 'mgs_var', 'number_of_times_a_day',
    'mls_max', 'mgs_max', 'loading_dose', 'mls_var_loading', 'mgs_var_loading',
    'mls_max_loading', 'mgs_max_loading', 'instructions', 'nzf_link',
    'high_range', 'high_modifier', 'mls_max_high', 'mgs_max_high',
    'strep_drug', 'strep_frequency', 'mls_var_strep', 'mgs_var_strep',
    'mls_strep_max', 'mgs_strep_max', 'weight_cutoff_1', 'weight_cutoff_2',
    'range1_dose', 'range2_dose', 'form', 'age_range'
]

drugs_data = [
('Парацетамол суспензия 24мл/мг (120мл/5мг)', 1, False, 0.625, 15, '''Дозировка для детей зависит от возраста и массы тела ребенка.
        Для детей в возрасте от 3 до 12 месяцев 2,5-5 мл сиропа (60-120 мг парацетамола).
        Для детей от 1 года до 5 лет – 5-10 мл сиропа (120-240 мг парацетамола).
        Для детей в возрасте от 5 до 12 лет – 10-20 мл сиропа (240-480 мг парацетамола).
        Взрослые и дети массой тела выше 60 кг - 20-40 мл сиропа (480-960 мг парацетамола).
        Частота приема сиропа парацетамола составляет 3-4 раза в день.''', 42,
             60, True, 1.25, 30, 62.5, 1500,
             'Противопоказания: возраст до 1 месяца, детям в возрасте до 3-х месяцев применять с осторожностью.',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=343f01d1-bbda-436f-978c-d1a23dc670eb  https://www.eapteka.ru/volgograd/goods/id224735/', True, 1.5, None, None, False, '', None, None, None, None, None, None, None, 24, None, None),


        ('Парацетамол ФортеКидс суспензия для приема внутрь 250 мг/5 мл', 1, False, 0.3, 15, '''Дозировка для детей зависит от возраста и массы тела ребенка.
        Разовая доза у детей - 10-15 мг/кг массы тела.
        Максимальная суточная доза у детей - 60 мг/кг массы тела при приеме отдельными разовыми дозами по 10-15 мг/кг массы тела в течение 24 ч.''', 20,
             1000, True, 0.6, 30, 30, 1500,
             'Противопоказания: Не давайте ребенку более 4 доз в течение 24 часов! ПАРАЦЕТАМОЛ ФортеКидс ПОКАЗАН для симптоматической терапии у детей старше 6 лет и взрослых ',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=86c53657-c25d-4d2b-b0ad-92fa25ed74e4  https://www.eapteka.ru/volgograd/goods/id521602/', True, 1.5, None, None, False, '', None, None, None, None, None, None, None, 50, None, None),

            ('Ибупрофен суспензия 100мг/5мл', 1, False, 0.25, 5, '''Дозировка для детей зависит от возраста и массы тела ребенка.
        Максимальная суточная доза не должна превышать 30 мг/кг массы тела ребенка c интервалами между приемами препарата 6-8 часов.
        Дети в возрасте 3-6  месяцев (вес ребенка от 5 до 7,6 кг): по 2,5 мл (50 мг) до 3 раз в течение 24 часов, не более 7,5 мл (150 мг) в сутки.
        Дети в возрасте 6-12 месяцев (вес ребенка 7,7 - 9 кг): по 2,5 мл (50 мг) до 3-4 раз в течение 24 часов, не более 10 мл (200 мг) в сутки.
        Дети в возрасте 1-3 года (вес ребенка 10 - 16 кг): по 5,0 мл (100 мг) до 3 раз в течение 24 часов, не более 15 мл (300 мг) в сутки.
        Дети в возрасте 4-6 лет (вес ребенка 17 - 20 кг): по 7,5 мл (150 мг) до 3 раз в течение 24 часов, не более 22,5 мл (450 мг) в сутки.
        Дети в возрасте 7-9 лет (вес ребенка 21 - 30 кг): по 10 мл (200 мг) до 3 раз в течение 24 часов, не более 30 мл (600 мг) в сутки.
        Дети в возрасте 10-12 лет (вес ребенка 31 - 40 кг): по 15 мл (300 мг) до 3 раз в течение 24 часов, не более 45 мл (900 мг) в сутки.''', 10, 200, False, None, None, None, None,
             'Противопоказания: масса тела менее 5 кг, возраст менее 3 месяцев. Если при приеме препарата в течение 24 часов (у детей в возрасте 3-5 месяцев) или в течение 3 дней (у детей в возрасте 6 месяцев и старше) симптомы сохраняются или усиливаются, необходимо прекратить лечение и обратиться к врачу.',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=a1ab07d8-6779-4029-9b52-04aa390eb440  https://www.eapteka.ru/volgograd/goods/id250621/', True, 2, None, None, False, '', None, None, None, None, None, None, None, 20, None, None),

            ('Ибупрофен форте 40мг/мл (200мг/5мл)', 1, False, 0.125, 5, '''Дозировка для детей зависит от возраста и массы тела ребенка.
        Возраст (Масса тела) Разовая доза мл препарата/ мг ибупрофена Максимальная суточная доза мл препарата/ мг ибупрофена
        1-3 года (10-16 кг) 2,5 мл (100 мг) 7,5 мл (300 мг)
        4-6 лет (17-20 кг) 3,75 мл (150 мг) 11,25 мл (450 мг)
        7-9 лет (21-30 кг) 5 мл (200 мг) - 15 мл (600 мг)
        10-12 лет (31-40 кг) 7,5 мл (300 мг) 22,5 мл (900 мг)
        13 лет и старше (масса тела более 40кг) 7,5-10 мл (300-400 мг) 30 мл (1200 мг)''', 10, 400, False, None, None, None, None,
             'Противопоказания: масса тела ребенка менее 10 кг, возраст до 1 года. Если улучшение не наступило или Вы чувствуете ухудшение через 3 дня, необходимо обратиться к врачу.',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=a1ab07d8-6779-4029-9b52-04aa390eb440  https://www.eapteka.ru/volgograd/goods/id514767/', False, 2, None, None, False, '', None, None, None, None, None, None, None, 40, None, None),

            ('Ибупрофен суппозитории ректальные для детей 60 мг', 6, False, None, 5, '''Дозировка для детей зависит от возраста и массы тела ребенка.
        Максимальная суточная доза не должна превышать 30 мг/кг массы тела ребенка с интервалами между приемами препарата 6-8 часов.
        Дети в возрасте от 3 до 9 месяцев с массой тела от 6,0 кг до 8,0 кг - по 1 суппозиторию (60 мг) до 3 раз в течение 24 часов, не более 180 мг в сутки.
        Дети в возрасте от 9 месяцев до 2 лет с массой тела от 8,0 кг до 12,0 кг - по 1 суппозиторию (60 мг) до 4 раз в течение 24 часов, не более 240 мг в сутки.''', None, 180,
             False, None, None, None, None,
             'Противопоказания: масса тела ребенка менее 6 кг, возраст до 3 месяцев. Если при приеме препарата в течение 24 часов (у детей в возрасте 3-5 месяцев) или в течение 3 дней (у детей в возрасте 6 месяцев и старше) симптомы сохраняются или усиливаются, необходимо прекратить лечение и обратиться к врачу.',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=e9ee3f13-8126-4c0c-94f3-9e6069827956  https://www.eapteka.ru/volgograd/goods/id509733/', True, 2, None, None, False, '', None, None, None, None, None, None,
             60, None, 'суппозитории ректальные', None),

            ('Ибупрофен (Брудол) суппозитории ректальные для детей 125 мг,', 6, False, None, 5, '''Дозировка для детей зависит от возраста и массы тела ребенка.
            Максимальная суточная доза не должна превышать 30 мг/кг массы тела ребенка с интервалами между приемами препарата 6-8 часов.
            Дети в возрасте от 2 до 4 лет с массой тела от 12,5 до 17 кг - по 1 суппозиторию (125) до 3 раз в течение 24 часов, не более 375 мг в сутки. Дети в возрасте от 4 до 6 лет с массой 17 кг до 20,5 кг - по 1 суппозиторию (125мг) до 4 раз в сутки в течение 24 часов, не более 50 мг в сутки. ''', None, 375,
             False, None, None, None, None,
             'Противопоказания: масса тела ребенка менее 12 кг, возраст до 2х лет. Если при приеме препарата  в течение 3 дней (у детей в возрасте 6 месяцев и старше) симптомы сохраняются или усиливаются, необходимо прекратить лечение и обратиться к врачу.',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=420ddf02-9061-49a6-b652-67a0f16dbab8  https://aptekiplus.ru/moskva/product/brudol-dlya-detey-125-mg-10-sht-suppozitorii-rektalnie-dlya-detey/?utm_referrer=https://www.google.com/', True, 2, None, None, False, '', None, None, None, None, None, None,
             125, None, 'суппозитории ректальные', None),

            ('Цефекон Д (парацетамол) для детей суппозитории ректальные 50 мг', 6, False, None, 10, '''Дозировка препарата рассчитывается в зависимости от возраста и массы тела, в соответствии с таблицей. Разовая доза составляет 10-15 мг/кг массы тела ребенка, 2-3 раза в сутки, через 4-6 часов.
            Максимальная суточная доза парацетамола не должна превышать 60 мг/кг массы тела ребенка.
            Возраст	Вес	Разовая доза
            1–3 месяца	4–6 кг	1 суппозиторий по 50 мг
            3–12 месяцев	7–10 кг	1 суппозиторий по 100 мг
            1–3 года	11–16 кг	1–2 суппозитория по 100 мг
            3–10 лет	17–30 кг	1 суппозиторий по 250 мг
            10–12 лет	31–35 кг	2 суппозитория по 250 мг''', None, 180,
             False, None, None, None, None,
             'Противопоказания: период новорожденности (до 1 мес).Длительность курса лечения: 3 дня в качестве жаропонижающего и до 5 дней, как обезболивающего средства. Продление курса при необходимости после консультации с врачом.',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=320c8322-457d-4e3f-8418-13ab434a203b  https://www.eapteka.ru/volgograd/goods/id206253/', True, 1.5, None, None, False, '', None, None, None, None, None, None,
             50, None, 'суппозитории ректальные', None),

            ('Цефекон Д (парацетамол) для детей суппозитории ректальные 100 мг', 6, False, None, 10, '''Дозировка препарата рассчитывается в зависимости от возраста и массы тела, в соответствии с таблицей. Разовая доза составляет 10-15 мг/кг массы тела ребенка, 2-3 раза в сутки, через 4-6 часов.
            Максимальная суточная доза парацетамола не должна превышать 60 мг/кг массы тела ребенка.
            Возраст	Вес	Разовая доза
            3–12 месяцев	7–10 кг	1 суппозиторий по 100 мг
            1–3 года	11–16 кг	1–2 суппозитория по 100 мг
            3–10 лет	17–30 кг	1 суппозиторий по 250 мг
            10–12 лет	31–35 кг	2 суппозитория по 250 мг''', None, 180,
             False, None, None, None, None,
             'Противопоказания: период новорожденности (до 1 мес).Длительность курса лечения: 3 дня в качестве жаропонижающего и до 5 дней, как обезболивающего средства. Продление курса при необходимости после консультации с врачом.',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=320c8322-457d-4e3f-8418-13ab434a203b  https://www.eapteka.ru/volgograd/goods/id206254/', True, 1.5, None, None, False, '', None, None, None, None, None, None,
             100, None, 'суппозитории ректальные', None),

            ('Цефекон Д (парацетамол) для детей суппозитории ректальные 250 мг', 6, False, None, 10, '''Дозировка препарата рассчитывается в зависимости от возраста и массы тела, в соответствии с таблицей. Разовая доза составляет 10-15 мг/кг массы тела ребенка, 2-3 раза в сутки, через 4-6 часов.
            Максимальная суточная доза парацетамола не должна превышать 60 мг/кг массы тела ребенка.
            Возраст	Вес	Разовая доза
            3–10 лет	17–30 кг	1 суппозиторий по 250 мг
            10–12 лет	31–35 кг	2 суппозитория по 250 мг''', None, 180,
             False, None, None, None, None,
             'Противопоказания: период новорожденности (до 1 мес).Длительность курса лечения: 3 дня в качестве жаропонижающего и до 5 дней, как обезболивающего средства. Продление курса при необходимости после консультации с врачом.',
             'https://grls.rosminzdrav.ru/Grls_View_v2.aspx?routingGuid=320c8322-457d-4e3f-8418-13ab434a203b  https://www.eapteka.ru/volgograd/goods/id206255/', True, 1.5, None, None, False, '', None, None, None, None, None, None,
             250, None, 'суппозитории ректальные', None) ]





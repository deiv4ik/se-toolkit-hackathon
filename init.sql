-- Создаем таблицы (База данных innopolis_guide создается автоматически через POSTGRES_DB)

CREATE TABLE IF NOT EXISTS places (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(50) UNIQUE,
    name VARCHAR(200),
    latitude FLOAT,
    longitude FLOAT,
    radius_meters INT,
    type VARCHAR(50),
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS science_prompts (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(50) REFERENCES places(place_id),
    science_type VARCHAR(50),
    prompt_text TEXT
);

CREATE TABLE IF NOT EXISTS user_requests (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(50) REFERENCES places(place_id),
    latitude FLOAT,
    longitude FLOAT,
    requested_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS generated_facts (
    id SERIAL PRIMARY KEY,
    place_id VARCHAR(50) REFERENCES places(place_id),
    science_type VARCHAR(50),
    fact_text TEXT,
    audio_file VARCHAR(100),
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Заполняем места
INSERT INTO places (place_id, name, latitude, longitude, radius_meters, type, category, description) VALUES
('university', 'Университет Иннополис', 55.7517, 48.7446, 100, 'building', 'education', 'Первый российский университет, специализирующийся на IT и робототехнике'),
('technopark', 'Технопарк им. А.С. Попова', 55.7498, 48.7431, 80, 'building', 'business', 'Крупнейший IT-технопарк в России в форме кристалла'),
('sport_complex', 'Спортивный комплекс', 55.7532, 48.7459, 70, 'building', 'sport', 'Современный спортивный центр с бассейном олимпийского стандарта'),
('robotics_lab', 'Лаборатория робототехники', 55.7510, 48.7452, 50, 'facility', 'research', 'Научно-исследовательская лаборатория робототехники'),
('artspace', 'ArtSpace — культурный центр', 55.7519, 48.7521, 100, 'cultural_space', 'culture', 'Современное культурное пространство площадью 2000 кв.м с кинотеатром, театральной студией и выставочным залом')
ON CONFLICT (place_id) DO NOTHING;

-- Заполняем промпты
INSERT INTO science_prompts (place_id, science_type, prompt_text) VALUES
('university', 'physics', 'Расскажи об энергоэффективных технологиях в здании Университета Иннополис. Как работает умное освещение и система отопления?'),
('university', 'technology', 'Как устроена IT-инфраструктура современного университета? Расскажи про дата-центры и облачные вычисления.'),
('university', 'history', 'Расскажи историю создания Иннополиса как российского аналога Силиконовой долины.'),
('technopark', 'physics', 'Объясни физику работы умного стекла (smart glass) на фасаде технопарка. Как оно меняет прозрачность?'),
('technopark', 'technology', 'Почему технопарки важны для развития инноваций? Как устроена экосистема стартапов?'),
('technopark', 'biology', 'Расскажи, как вертикальное озеленение вокруг здания влияет на микроклимат и очистку воздуха.'),
('sport_complex', 'physics', 'Как устроена система фильтрации олимпийского бассейна? Объясни принципы работы насосов.'),
('sport_complex', 'biology', 'Расскажи о физиологии спорта: как тренировки влияют на сердечно-сосудистую систему.'),
('sport_complex', 'medicine', 'Какие медицинские исследования проводятся в области спортивной медицины?'),
('robotics_lab', 'physics', 'Объясни физические принципы работы датчиков и лидаров в беспилотных автомобилях.'),
('robotics_lab', 'technology', 'Как работают нейросети в компьютерном зрении роботов?'),
('robotics_lab', 'history', 'Кто изобрел первого робота и как эволюционировала робототехника?'),
('artspace', 'technology', 'Как цифровые технологии используются в современном искусстве? Расскажи про VR-выставки, цифровые инсталляции и мультимедийные проекты в культурных центрах.'),
('artspace', 'physics', 'Объясни физику света и цвета в выставочных пространствах. Как освещение и акустика влияют на восприятие произведений искусства в кинозалах и галереях?'),
('artspace', 'history', 'Расскажи историю создания культурного центра ArtSpace в Иннополисе. Как современное искусство и креативные пространства влияют на развитие IT-города?')
ON CONFLICT DO NOTHING;

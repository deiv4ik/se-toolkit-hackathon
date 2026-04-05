# geo_utils.py
from math import radians, cos, sin, asin, sqrt
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Рассчитывает расстояние между двумя точками на Земле в метрах
    (формула гаверсинуса)
    """
    # Конвертируем в радианы
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Разница координат
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Формула гаверсинуса
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))

    # Радиус Земли в метрах
    r = 6371000

    return c * r


def load_places(json_file='innopolis_places.json'):
    """Загружает базу мест из JSON"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        places = data.get('places', [])
        logger.info(f"✅ Загружено мест: {len(places)} из {json_file}")
        return places
    except FileNotFoundError:
        logger.error(f"❌ Файл {json_file} не найден!")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка в JSON: {e}")
        return []


def find_nearby_place(user_lat, user_lon, places):
    """
    Ищет место, рядом с которым находится пользователь
    Возвращает место или None
    """
    if not places:
        logger.warning("⚠️ База мест пуста")
        return None

    for place in places:
        try:
            place_lat = place['coordinates']['latitude']
            place_lon = place['coordinates']['longitude']
            radius = place['coordinates']['radius_meters']

            distance = haversine_distance(user_lat, user_lon, place_lat, place_lon)

            if distance <= radius:
                # Добавляем расстояние в результат
                place['distance'] = round(distance, 1)
                logger.info(f"✅ Найдено место: {place['name']} на расстоянии {round(distance, 1)}м")
                return place
        except KeyError as e:
            logger.error(f"❌ Ошибка в структуре места: {e}")
            continue

    logger.info("❌ Мест рядом не найдено")
    return None


def format_distance(distance_meters):
    """Форматирует расстояние в читаемый вид"""
    if distance_meters < 1000:
        return f"{distance_meters} м"
    else:
        return f"{distance_meters / 1000:.1f} км"


def find_all_nearby_places(user_lat, user_lon, places, exact_radius_only=False):
    """
    Находит ВСЕ места рядом

    Параметры:
        exact_radius_only: если True - только строго по радиусу
                          если False - показывает все в пределах 300м
    """
    if not places:
        return []

    nearby = []
    for place in places:
        try:
            place_lat = place['coordinates']['latitude']
            place_lon = place['coordinates']['longitude']
            radius = place['coordinates']['radius_meters']

            distance = haversine_distance(user_lat, user_lon, place_lat, place_lon)

            # Всегда добавляем, если расстояние меньше 300 метров
            if distance <= 300:  # Радиус обзора 300м
                place_copy = place.copy()
                place_copy['distance'] = round(distance, 1)

                # Добавляем статус: "точно рядом" или "нужно подойти"
                if distance <= radius:
                    place_copy['status'] = '✅ Точно рядом'
                else:
                    place_copy['status'] = '⚠️ Нужно подойти ближе'

                nearby.append(place_copy)

        except KeyError as e:
            logger.error(f"❌ Ошибка в структуре места: {e}")
            continue

    # Сортируем по расстоянию
    nearby.sort(key=lambda x: x['distance'])

    logger.info(f"✅ Найдено мест в радиусе 300м: {len(nearby)}")
    return nearby
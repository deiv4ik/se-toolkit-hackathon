# gigachat_api.py
import requests
import json
import os
import uuid
import logging
from typing import Optional, Dict
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Добавь ЭТО в самое начало gigachat_api.py, после импортов

import asyncio
import sys

# Для Windows исправляем проблему с event loop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# Отключаем предупреждения о SSL (для локальной разработки)
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



class GigaChatClient:
    """Клиент для работы с GigaChat API"""

    def __init__(self):
        load_dotenv()

        self.auth_key = os.getenv("GIGACHAT_AUTH_KEY")
        self.scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

        if not self.auth_key:
            raise ValueError("❌ GIGACHAT_AUTH_KEY не найден в .env файле!")

        # URL для GigaChat
        self.base_url = "https://gigachat.devices.sberbank.ru/api/v1"
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

        # Генерируем уникальный ID для запросов
        self.rquid = str(uuid.uuid4())

        # Токен и время его истечения
        self.access_token = None
        self.token_expires = None

        logger.info("✅ GigaChatClient инициализирован")

    def get_access_token(self) -> Optional[str]:
        """
        Получает новый Access Token для GigaChat
        Токен действует 30 минут
        """
        # Проверяем, может текущий токен еще действителен
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            logger.info("✅ Используем существующий токен")
            return self.access_token

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': self.rquid,
            'Authorization': f'Basic {self.auth_key}'
        }

        data = {
            'scope': self.scope
        }

        try:
            logger.info("🔄 Получаем новый Access Token от GigaChat...")
            response = requests.post(
                self.auth_url,
                headers=headers,
                data=data,
                verify=False,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get('access_token')
                expires_in = result.get('expires_in', 1800)  # 30 минут по умолчанию
                self.token_expires = datetime.now() + timedelta(seconds=expires_in)

                logger.info(f"✅ Токен получен, действует до {self.token_expires.strftime('%H:%M:%S')}")
                return self.access_token
            else:
                logger.error(f"❌ Ошибка получения токена: {response.status_code}")
                logger.error(f"Ответ: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error("❌ Таймаут при получении токена")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("❌ Ошибка соединения при получении токена")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка при получении токена: {e}")
            return None

    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """
        Внутренний метод для выполнения запросов к GigaChat API
        """
        token = self.get_access_token()
        if not token:
            logger.error("❌ Не удалось получить токен")
            return None

        url = f"{self.base_url}{endpoint}"

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        try:
            logger.info(f"📤 Отправляем {method} запрос к {endpoint}")

            if method == 'GET':
                response = requests.get(url, headers=headers, verify=False, timeout=30)
            elif method == 'POST':
                headers['Content-Type'] = 'application/json'
                response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
            else:
                logger.error(f"❌ Неподдерживаемый метод: {method}")
                return None

            if response.status_code == 200:
                logger.info(f"✅ Получен ответ от API")
                return response.json()
            else:
                logger.error(f"❌ Ошибка API: {response.status_code}")
                logger.error(f"Ответ: {response.text}")
                return None

        except requests.exceptions.Timeout:
            logger.error("❌ Таймаут при запросе к API")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("❌ Ошибка соединения с API")
            return None
        except Exception as e:
            logger.error(f"❌ Ошибка при запросе: {e}")
            return None

    def list_models(self) -> Optional[list]:
        """
        Получает список доступных моделей GigaChat
        """
        result = self._make_request('GET', '/models')
        if result and 'data' in result:
            models = result['data']
            logger.info(f"✅ Доступно моделей: {len(models)}")
            return models
        return None

    def chat_completion(self, messages: list, model: str = "GigaChat", temperature: float = 0.7,
                        max_tokens: int = 500) -> Optional[str]:
        """
        Отправляет запрос к GigaChat для получения ответа
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        result = self._make_request('POST', '/chat/completions', data)

        if result and 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            logger.info(f"✅ Получен ответ: {content[:50]}...")
            return content

        logger.error("❌ Не удалось получить ответ от модели")
        return None

    def generate_science_fact(self, place: Dict, science_type: str = None) -> Optional[str]:
        """
        Генерирует научный факт о месте с помощью GigaChat
        """
        # Формируем сообщения для GigaChat
        messages = [
            {
                "role": "system",
                "content": """Ты — научный гид по Иннополису (городу высоких технологий в России).
Твоя задача — рассказывать увлекательные и достоверные научные факты о местных достопримечательностях.
Отвечай кратко (3-5 предложений), но информативно. Используй научный, но понятный язык."""
            }
        ]

        # Формируем промпт
        if science_type and place.get('context_for_llm', {}).get('science_prompts', {}).get(science_type):
            user_content = place['context_for_llm']['science_prompts'][science_type]
        else:
            user_content = f"Расскажи интересные научные факты о {place['name']} в Иннополисе. Это {place.get('type', 'объект')}. {place.get('description_short', '')} Расскажи с точки зрения физики, биологии, технологии или истории."

        messages.append({
            "role": "user",
            "content": user_content
        })

        logger.info(f"🧪 Генерируем факт о: {place['name']}")
        return self.chat_completion(messages)

    def __call__(self, prompt: str, system_message: str = None) -> Optional[str]:
        """
        Удобный способ вызвать API напрямую
        """
        messages = []

        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        return self.chat_completion(messages)


# ===== ТЕСТИРОВАНИЕ =====
if __name__ == "__main__":
    print("🔬 ТЕСТИРОВАНИЕ GIGACHAT API")
    print("=" * 50)

    # Создаем клиент
    client = GigaChatClient()

    # Тест 1: Получение токена
    print("\n📋 Тест 1: Получение токена")
    token = client.get_access_token()
    if token:
        print(f"✅ Токен получен: {token[:20]}...")
    else:
        print("❌ Ошибка получения токена")
        exit()

    # Тест 2: Список моделей
    print("\n📋 Тест 2: Получение списка моделей")
    models = client.list_models()
    if models:
        print(f"✅ Доступные модели:")
        for model in models[:3]:  # Покажем первые 3
            print(f"  • {model.get('id')}")
    else:
        print("❌ Не удалось получить список моделей")

    # Тест 3: Простой запрос
    print("\n📋 Тест 3: Простой запрос")
    messages = [
        {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко."},
        {"role": "user", "content": "Скажи 'Привет, я GigaChat и я работаю!'"}
    ]
    result = client.chat_completion(messages)
    if result:
        print(f"✅ Ответ: {result}")
    else:
        print("❌ Ошибка запроса")

    # Тест 4: Научный факт
    print("\n📋 Тест 4: Генерация научного факта")
    test_place = {
        "name": "Университет Иннополис",
        "type": "building",
        "description_short": "Главный корпус Университета Иннополис",
        "context_for_llm": {
            "science_prompts": {
                "physics": "Расскажи об энергоэффективных технологиях в здании Университета Иннополис."
            }
        }
    }
    fact = client.generate_science_fact(test_place, "physics")
    if fact:
        print(f"✅ Факт: {fact}")
    else:
        print("❌ Ошибка генерации факта")
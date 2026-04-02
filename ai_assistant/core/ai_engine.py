"""
AI движок на базе Qwen (Alibaba Cloud DashScope)
Обеспечивает быстрые ответы через облачный API
"""
import json
import re
import logging
from typing import Optional, Dict, Any
import requests
from config.settings import QWEN_API_KEY, QWEN_MODEL

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AIEngine')


class AIEngine:
    """Движок для взаимодействия с Qwen AI"""
    
    def __init__(self):
        self.api_key = QWEN_API_KEY
        self.model = QWEN_MODEL
        self.base_url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
        
        # Проверка API ключа
        if not self.api_key or self.api_key == "your_api_key_here":
            logger.error("API ключ не настроен!")
            self.api_key_valid = False
        else:
            self.api_key_valid = True
            logger.info(f"AIEngine инициализирован с моделью: {self.model}")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.conversation_history = []
        
    def _build_prompt(self, user_message: str) -> list:
        """Формирует промпт с контекстом для понимания команд"""
        system_prompt = """Ты персональный ИИ-ассистент для Windows PC. 
Твои возможности:
1. Отвечать на вопросы текстом
2. Открывать приложения (команда: ОТКРЫТЬ_ПРИЛОЖЕНИЕ: название)
3. Открывать сайты в браузере (команда: ОТКРЫТЬ_САЙТ: url)
4. Анализировать содержимое экрана (команда: АНАЛИЗ_ЭКРАНА)
5. Работать с Office и Paint (команда: ДЕЙСТВИЕ_В_ПРИЛОЖЕНИИ: приложение|действие|параметры)
6. Управлять мышью (команда: МЫШЬ: действие|координаты)

Отвечай кратко и по делу. Если нужна команда - используй формат выше.
Пиши ответы на русском языке."""
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(self.conversation_history[-10:])  # Последние 10 сообщений
        messages.append({"role": "user", "content": user_message})
        return messages
    
    def ask(self, message: str, screenshot_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Отправляет запрос к Qwen и получает ответ
        
        Args:
            message: Текст запроса пользователя
            screenshot_data: Base64 скриншота (опционально)
            
        Returns:
            Dict с полями: response, command, params
        """
        logger.info(f"Запрос к AI: {message[:100]}...")
        
        # Проверка API ключа
        if not self.api_key_valid:
            error_msg = "API ключ не настроен! Получите ключ на https://dashscope.console.aliyun.com/ и установите переменную окружения QWEN_API_KEY"
            logger.error(error_msg)
            return {
                "response": error_msg,
                "command": None,
                "params": {}
            }
        
        messages = self._build_prompt(message)
        
        # Если есть скриншот, добавляем его как изображение
        if screenshot_data:
            logger.debug("Добавлен скриншот к запросу")
            messages[-1] = {
                "role": "user",
                "content": [
                    {"image": screenshot_data},
                    {"text": message}
                ]
            }
        
        payload = {
            "model": self.model,
            "input": {"messages": messages},
            "parameters": {
                "max_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        try:
            logger.debug(f"Отправка запроса к {self.base_url}")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            logger.debug(f"Статус ответа: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            logger.debug(f"Получен ответ: {result}")
            
            ai_response = result["output"]["choices"][0]["message"]["content"]
            logger.info(f"Ответ AI: {ai_response[:200]}...")
            
            # Сохраняем в историю
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Парсим команды из ответа
            command, params = self._parse_command(ai_response)
            if command:
                logger.info(f"Извлечена команда: {command}, параметры: {params}")
            
            return {
                "response": ai_response,
                "command": command,
                "params": params
            }
            
        except requests.exceptions.Timeout:
            error_msg = "Превышено время ожидания ответа от AI"
            logger.error(error_msg)
            return {
                "response": error_msg,
                "command": None,
                "params": {}
            }
        except requests.exceptions.RequestException as e:
            error_msg = f"Ошибка подключения к AI: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "response": error_msg,
                "command": None,
                "params": {}
            }
        except Exception as e:
            error_msg = f"Неизвестная ошибка AI: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "response": error_msg,
                "command": None,
                "params": {}
            }
    
    def _parse_command(self, text: str) -> tuple:
        """Извлекает команду из текста ответа"""
        patterns = {
            "ОТКРЫТЬ_ПРИЛОЖЕНИЕ": r"ОТКРЫТЬ_ПРИЛОЖЕНИЕ:\s*(\w+)",
            "ОТКРЫТЬ_САЙТ": r"ОТКРЫТЬ_САЙТ:\s*(https?://[^\s]+)",
            "АНАЛИЗ_ЭКРАНА": r"АНАЛИЗ_ЭКРАНА",
            "ДЕЙСТВИЕ_В_ПРИЛОЖЕНИИ": r"ДЕЙСТВИЕ_В_ПРИЛОЖЕНИИ:\s*(\w+)\|([^|]+)\|(.+)",
            "МЫШЬ": r"МЫШЬ:\s*(\w+)\|([\d,\s]+)"
        }
        
        for cmd_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                logger.debug(f"Найдена команда {cmd_name}: {groups}")
                return cmd_name, groups if len(groups) > 1 else groups[0]
        
        logger.debug("Команды не найдены")
        return None, {}
    
    def clear_history(self):
        """Очищает историю переписки"""
        self.conversation_history = []
        logger.info("История переписки очищена")

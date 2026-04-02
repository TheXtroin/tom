"""
AI движок на базе Qwen (Alibaba Cloud DashScope)
Обеспечивает быстрые ответы через облачный API
"""
import json
import re
from typing import Optional, Dict, Any
import requests
from config.settings import QWEN_API_KEY, QWEN_MODEL


class AIEngine:
    """Движок для взаимодействия с Qwen AI"""
    
    def __init__(self):
        self.api_key = QWEN_API_KEY
        self.model = QWEN_MODEL
        self.base_url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
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

Отвечай кратко и по делу. Если нужна команда - используй формат выше."""
        
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
        messages = self._build_prompt(message)
        
        # Если есть скриншот, добавляем его как изображение
        if screenshot_data:
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
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            ai_response = result["output"]["choices"][0]["message"]["content"]
            
            # Сохраняем в историю
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Парсим команды из ответа
            command, params = self._parse_command(ai_response)
            
            return {
                "response": ai_response,
                "command": command,
                "params": params
            }
            
        except Exception as e:
            return {
                "response": f"Ошибка подключения к AI: {str(e)}",
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
                return cmd_name, match.groups() if len(match.groups()) > 1 else match.group(1)
        
        return None, {}
    
    def clear_history(self):
        """Очищает историю переписки"""
        self.conversation_history = []

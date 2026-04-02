"""
Конфигурация приложения
"""
import os

# API ключ для Qwen (Alibaba Cloud DashScope)
# Получите ключ на: https://dashscope.console.aliyun.com/
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "your_api_key_here")
QWEN_MODEL = "qwen-max"  # Быстрая и мощная модель

# Пути к приложениям (если их нет в меню Пуск)
APPLICATIONS = {
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "paint": r"C:\Windows\System32\mspaint.exe",
    "notepad": r"C:\Windows\System32\notepad.exe",
    "calculator": r"C:\Windows\System32\calc.exe",
}

# Браузер по умолчанию
BROWSER = "msedge"  # Microsoft Edge

# Горячие клавиши для открытия/закрытия окна
HOTKEY = ("win", "shift", "enter")

# Настройки окна
WINDOW_TITLE = "AI Assistant"
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 600
WINDOW_X = None  # None = центр экрана
WINDOW_Y = None

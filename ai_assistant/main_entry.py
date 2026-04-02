"""
Точка входа приложения AI Assistant

Запуск:
    python main_entry.py

Предварительно установите зависимости:
    pip install -r requirements.txt

Настройте API ключ в config/settings.py или через переменную окружения:
    set QWEN_API_KEY=your_api_key_here
"""

import sys
import os

# Добавляем корень проекта в path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import AssistantController


def main():
    """Основная функция запуска"""
    print("=" * 50)
    print("🤖 AI Assistant для Windows")
    print("=" * 50)
    print()
    print("Инициализация...")
    print()
    
    # Проверка API ключа
    from config.settings import QWEN_API_KEY
    if QWEN_API_KEY == "your_api_key_here":
        print("⚠️  ВНИМАНИЕ: API ключ не настроен!")
        print("Получите ключ на: https://dashscope.console.aliyun.com/")
        print("И установите его:")
        print("  1) В файле config/settings.py")
        print("  2) Или через переменную окружения:")
        print("     set QWEN_API_KEY=your_actual_key")
        print()
        print("Приложение запустится, но не сможет работать с AI без ключа.")
        print()
    
    # Создание и запуск контроллера
    controller = AssistantController()
    
    print("✅ Готово!")
    print()
    print("Инструкция:")
    print("  • Нажмите Win+Shift+Enter чтобы открыть/закрыть окно")
    print("  • Введите вопрос или команду в поле ввода")
    print("  • Нажмите Enter или кнопку 'Отправить'")
    print()
    print("Примеры команд:")
    print("  • 'Открой браузер'")
    print("  • 'Покажи погоду в Москве'")
    print("  • 'Сделай скриншот и проанализируй'")
    print("  • 'Создай таблицу в Excel'")
    print()
    print("Нажмите Ctrl+C в этом окне для выхода")
    print("=" * 50)
    print()
    
    try:
        controller.start()
    except KeyboardInterrupt:
        print("\n\nОстановка приложения...")
        controller.stop()
        print("До свидания! 👋")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("Проверьте логи и настройки.")
        sys.exit(1)


if __name__ == "__main__":
    main()

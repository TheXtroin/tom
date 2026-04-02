"""
Главный контроллер приложения - координирует все компоненты
"""
import threading
from typing import Optional

from core.ai_engine import AIEngine
from core.system_controller import SystemController
from ui.controller import UIController
from ui.hotkey_manager import HotkeyManager
from config.settings import HOTKEY


class AssistantController:
    """Главный контроллер, объединяющий все компоненты"""
    
    def __init__(self):
        self.ai_engine = AIEngine()
        self.system_controller = SystemController()
        self.ui_controller = UIController()
        self.hotkey_manager = HotkeyManager()
        
        self.is_processing = False
        
        # Настройка callback'ов
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Настройка всех callback'ов"""
        # Горячие клавиши
        self.hotkey_manager.set_hotkey(HOTKEY)
        self.hotkey_manager.set_callback(self._on_hotkey_pressed)
        
        # UI callbacks
        self.ui_controller.on_message_callback = self._process_message
        self.ui_controller.on_screenshot_callback = self._handle_screenshot
    
    def _on_hotkey_pressed(self):
        """Обработчик горячей комбинации клавиш"""
        self.ui_controller.toggle()
    
    def _process_message(self, message: str, include_screenshot: bool = False):
        """
        Обработка сообщения пользователя
        
        Args:
            message: Текст сообщения
            include_screenshot: Включить ли скриншот
        """
        if self.is_processing:
            return
        
        self.is_processing = True
        self.ui_controller.set_status("Думаю...")
        
        # Запускаем в отдельном потоке чтобы не блокировать UI
        thread = threading.Thread(
            target=self._process_message_thread,
            args=(message, include_screenshot)
        )
        thread.daemon = True
        thread.start()
    
    def _process_message_thread(self, message: str, include_screenshot: bool):
        """Поток обработки сообщения"""
        try:
            screenshot_data = None
            
            # Если нужен скриншот для анализа
            if include_screenshot:
                screenshot_data = self.system_controller.take_screenshot()
            
            # Запрос к AI
            result = self.ai_engine.ask(message, screenshot_data)
            
            # Отображаем ответ
            self.ui_controller.add_message(result['response'], 'assistant')
            self.ui_controller.set_status("Готов")
            
            # Выполняем команду если есть
            if result['command']:
                self._execute_command(result['command'], result['params'])
                
        except Exception as e:
            self.ui_controller.add_message(f"Ошибка: {str(e)}", 'system')
            self.ui_controller.set_status("Ошибка")
        finally:
            self.is_processing = False
    
    def _execute_command(self, command: str, params):
        """Выполнение команды от AI"""
        try:
            if command == "ОТКРЫТЬ_ПРИЛОЖЕНИЕ":
                app_name = params if isinstance(params, str) else params[0]
                success = self.system_controller.open_application(app_name)
                status = f"Приложение {app_name} открыто" if success else f"Не удалось открыть {app_name}"
                self.ui_controller.set_status(status)
                
            elif command == "ОТКРЫТЬ_САЙТ":
                url = params if isinstance(params, str) else params[0]
                success = self.system_controller.open_website(url)
                status = f"Сайт открыт" if success else "Не удалось открыть сайт"
                self.ui_controller.set_status(status)
                
            elif command == "АНАЛИЗ_ЭКРАНА":
                screenshot = self.system_controller.take_screenshot()
                screen_info = self.system_controller.get_screen_info()
                self.ui_controller.set_status(f"Экран: {screen_info['width']}x{screen_info['height']}")
                
            elif command == "ДЕЙСТВИЕ_В_ПРИЛОЖЕНИИ":
                app, action, action_params = params
                success = self.system_controller.office_action(app, action, action_params)
                status = f"Действие выполнено" if success else "Не удалось выполнить действие"
                self.ui_controller.set_status(status)
                
            elif command == "МЫШЬ":
                action, coords = params
                if action == "click":
                    x, y = map(int, coords.replace(' ', '').split(','))
                    self.system_controller.mouse_click(x, y)
                elif action == "move":
                    x, y = map(int, coords.replace(' ', '').split(','))
                    self.system_controller.mouse_move(x, y)
                    
        except Exception as e:
            self.ui_controller.set_status(f"Ошибка команды: {e}")
    
    def _handle_screenshot(self):
        """Обработчик кнопки скриншота"""
        try:
            screenshot_data = self.system_controller.take_screenshot()
            self.ui_controller.add_message("📸 Скриншот сделан и готов к анализу", 'system')
            
            # Отправляем скриншот на анализ AI
            self._process_message("Что изображено на этом скриншоте?", include_screenshot=True)
            
        except Exception as e:
            self.ui_controller.add_message(f"Ошибка скриншота: {e}", 'system')
    
    def start(self):
        """Запуск приложения"""
        # Запускаем горячие клавиши
        self.hotkey_manager.start()
        
        # Инициализируем UI
        self.ui_controller.initialize()
        
        # Приветственное сообщение
        welcome_msg = (
            "Привет! Я ваш персональный AI ассистент.\n\n"
            "Я умею:\n"
            "• Отвечать на вопросы\n"
            "• Открывать приложения и сайты\n"
            "• Анализировать экран\n"
            "• Работать с Office и Paint\n"
            "• Управлять мышью\n\n"
            "Нажмите Win+Shift+Enter чтобы скрыть/показать это окно."
        )
        self.ui_controller.add_message(welcome_msg, 'system')
        
        # Запускаем главный цикл UI
        self.ui_controller.run()
    
    def stop(self):
        """Остановка приложения"""
        self.hotkey_manager.stop()
        self.ui_controller.quit()

"""
Главный контроллер приложения - координирует все компоненты
"""
import threading
import logging
from typing import Optional

# Настройка логирования в начале
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AssistantController')

from core.ai_engine import AIEngine
from core.system_controller import SystemController
from ui.controller import UIController
from ui.hotkey_manager import HotkeyManager
from config.settings import HOTKEY


class AssistantController:
    """Главный контроллер, объединяющий все компоненты"""
    
    def __init__(self):
        logger.info("Инициализация AssistantController...")
        
        self.ai_engine = AIEngine()
        self.system_controller = SystemController()
        self.ui_controller = UIController()
        self.hotkey_manager = HotkeyManager()
        
        self.is_processing = False
        
        # Настройка callback'ов
        self._setup_callbacks()
        
        logger.info("AssistantController инициализирован")
    
    def _setup_callbacks(self):
        """Настройка всех callback'ов"""
        logger.debug("Настройка callbacks...")
        
        # Горячие клавиши
        self.hotkey_manager.set_hotkey(HOTKEY)
        self.hotkey_manager.set_callback(self._on_hotkey_pressed)
        
        # UI callbacks
        self.ui_controller.on_message_callback = self._process_message
        self.ui_controller.on_screenshot_callback = self._handle_screenshot
        
        logger.debug("Callbacks настроены")
    
    def _on_hotkey_pressed(self):
        """Обработчик горячей комбинации клавиш"""
        logger.info("Горячая комбинация нажата! Переключение видимости окна...")
        try:
            self.ui_controller.toggle()
            logger.info("Окно переключено успешно")
        except Exception as e:
            logger.error(f"Ошибка при переключении окна: {e}", exc_info=True)
    
    def _process_message(self, message: str, include_screenshot: bool = False):
        """
        Обработка сообщения пользователя
        
        Args:
            message: Текст сообщения
            include_screenshot: Включить ли скриншот
        """
        if self.is_processing:
            logger.warning("Попытка обработки во время обработки другого сообщения")
            return
        
        logger.info(f"Начало обработки сообщения: {message[:50]}...")
        self.is_processing = True
        self.ui_controller.set_status("Думаю...")
        
        # Запускаем в отдельном потоке чтобы не блокировать UI
        thread = threading.Thread(
            target=self._process_message_thread,
            args=(message, include_screenshot),
            daemon=True
        )
        thread.start()
        logger.debug("Поток обработки запущен")
    
    def _process_message_thread(self, message: str, include_screenshot: bool):
        """Поток обработки сообщения"""
        try:
            screenshot_data = None
            
            # Если нужен скриншот для анализа
            if include_screenshot:
                logger.debug("Делаем скриншот...")
                screenshot_data = self.system_controller.take_screenshot()
                logger.debug(f"Скриншот сделан, размер: {len(screenshot_data)} байт")
            
            # Запрос к AI
            logger.info("Отправка запроса к AI...")
            result = self.ai_engine.ask(message, screenshot_data)
            logger.info(f"Получен ответ от AI: {result['response'][:100]}...")
            
            # Отображаем ответ
            self.ui_controller.add_message(result['response'], 'assistant')
            self.ui_controller.set_status("Готов")
            
            # Выполняем команду если есть
            if result['command']:
                logger.info(f"Выполнение команды: {result['command']}")
                self._execute_command(result['command'], result['params'])
                
        except Exception as e:
            error_msg = f"Ошибка обработки: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.ui_controller.add_message(error_msg, 'system')
            self.ui_controller.set_status("Ошибка")
        finally:
            self.is_processing = False
            logger.debug("Обработка завершена")
    
    def _execute_command(self, command: str, params):
        """Выполнение команды от AI"""
        try:
            logger.info(f"Выполнение команды {command} с параметрами {params}")
            
            if command == "ОТКРЫТЬ_ПРИЛОЖЕНИЕ":
                app_name = params if isinstance(params, str) else params[0]
                success = self.system_controller.open_application(app_name)
                status = f"Приложение {app_name} открыто" if success else f"Не удалось открыть {app_name}"
                self.ui_controller.set_status(status)
                logger.info(f"Результат открытия приложения: {success}")
                
            elif command == "ОТКРЫТЬ_САЙТ":
                url = params if isinstance(params, str) else params[0]
                success = self.system_controller.open_website(url)
                status = f"Сайт открыт" if success else "Не удалось открыть сайт"
                self.ui_controller.set_status(status)
                logger.info(f"Результат открытия сайта: {success}")
                
            elif command == "АНАЛИЗ_ЭКРАНА":
                screenshot = self.system_controller.take_screenshot()
                screen_info = self.system_controller.get_screen_info()
                self.ui_controller.set_status(f"Экран: {screen_info['width']}x{screen_info['height']}")
                logger.info(f"Информация об экране: {screen_info}")
                
            elif command == "ДЕЙСТВИЕ_В_ПРИЛОЖЕНИИ":
                app, action, action_params = params
                success = self.system_controller.office_action(app, action, action_params)
                status = f"Действие выполнено" if success else "Не удалось выполнить действие"
                self.ui_controller.set_status(status)
                logger.info(f"Результат действия в приложении: {success}")
                
            elif command == "МЫШЬ":
                action, coords = params
                if action == "click":
                    x, y = map(int, coords.replace(' ', '').split(','))
                    success = self.system_controller.mouse_click(x, y)
                elif action == "move":
                    x, y = map(int, coords.replace(' ', '').split(','))
                    success = self.system_controller.mouse_move(x, y)
                logger.info(f"Результат действия мыши: {success}")
                    
        except Exception as e:
            error_msg = f"Ошибка команды: {e}"
            logger.error(error_msg, exc_info=True)
            self.ui_controller.set_status(error_msg)
    
    def _handle_screenshot(self):
        """Обработчик кнопки скриншота"""
        try:
            logger.info("Обработка кнопки скриншота...")
            screenshot_data = self.system_controller.take_screenshot()
            self.ui_controller.add_message("📸 Скриншот сделан и готов к анализу", 'system')
            
            # Отправляем скриншот на анализ AI
            self._process_message("Что изображено на этом скриншоте?", include_screenshot=True)
            
        except Exception as e:
            error_msg = f"Ошибка скриншота: {e}"
            logger.error(error_msg, exc_info=True)
            self.ui_controller.add_message(error_msg, 'system')
    
    def start(self):
        """Запуск приложения"""
        logger.info("=" * 50)
        logger.info("Запуск AI Assistant...")
        logger.info("=" * 50)
        
        # Запускаем горячие клавиши
        logger.info("Запуск hotkey manager...")
        hk_success = self.hotkey_manager.start()
        if hk_success:
            logger.info("Hotkey manager запущен успешно")
        else:
            logger.error("Не удалось запустить hotkey manager")
        
        # Инициализируем UI
        logger.info("Инициализация UI...")
        self.ui_controller.initialize()
        logger.info("UI инициализирован")
        
        # Приветственное сообщение
        welcome_msg = (
            "Привет! Я ваш персональный AI ассистент.✨\n\n"
            "Я умею:\n"
            "• Отвечать на вопросы\n"
            "• Открывать приложения и сайты\n"
            "• Анализировать экран\n"
            "• Работать с Office и Paint\n"
            "• Управлять мышью\n\n"
            "Нажмите Win+Shift+Enter чтобы скрыть/показать это окно."
        )
        self.ui_controller.add_message(welcome_msg, 'system')
        
        logger.info("Запуск главного цикла UI...")
        # Запускаем главный цикл UI
        self.ui_controller.run()
    
    def stop(self):
        """Остановка приложения"""
        logger.info("Остановка приложения...")
        self.hotkey_manager.stop()
        self.ui_controller.quit()
        logger.info("Приложение остановлено")

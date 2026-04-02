"""
Менеджер горячих клавиш для глобального перехвата комбинаций
"""
import threading
import logging
from typing import Callable, Optional

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('HotkeyManager')

try:
    # Для Windows
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
    logger.info("pynput успешно импортирован")
except ImportError as e:
    PYNPUT_AVAILABLE = False
    logger.error(f"pynput не доступен: {e}")


class HotkeyManager:
    """Управление глобальными горячими клавишами"""
    
    def __init__(self):
        self.listener: Optional[keyboard.Listener] = None
        self.callback: Optional[Callable] = None
        self.hotkey = ('win', 'shift', 'enter')
        self.pressed_keys = set()
        self._callback_lock = threading.Lock()
        self._last_trigger_time = 0
        logger.debug("HotkeyManager инициализирован")
        
    def set_hotkey(self, keys: tuple):
        """Установить комбинацию горячих клавиш"""
        self.hotkey = tuple(k.lower() for k in keys)
        logger.info(f"Горячие клавиши установлены: {self.hotkey}")
    
    def set_callback(self, callback: Callable):
        """Установить callback для срабатывания горячей клавиши"""
        self.callback = callback
        logger.info(f"Callback установлен: {callback}")
    
    def _on_press(self, key):
        """Обработчик нажатия клавиш"""
        try:
            # Нормализация клавиш
            key_name = self._normalize_key(key)
            if key_name:
                self.pressed_keys.add(key_name)
                logger.debug(f"Нажата клавиша: {key_name}, текущие: {self.pressed_keys}")
            
            # Проверка комбинации
            if self._check_hotkey():
                import time
                current_time = time.time()
                # Защита от повторных срабатываний (debounce)
                if current_time - self._last_trigger_time > 0.5:
                    self._last_trigger_time = current_time
                    logger.info("Горячая комбинация обнаружена! Вызов callback...")
                    if self.callback:
                        with self._callback_lock:
                            try:
                                self.callback()
                                logger.info("Callback успешно выполнен")
                            except Exception as e:
                                logger.error(f"Ошибка в callback: {e}", exc_info=True)
                    # Сбрасываем нажатые клавиши после срабатывания
                    self.pressed_keys.clear()
                
        except Exception as e:
            logger.error(f"Ошибка в on_press: {e}", exc_info=True)
    
    def _on_release(self, key):
        """Обработчик отпускания клавиш"""
        try:
            key_name = self._normalize_key(key)
            if key_name:
                self.pressed_keys.discard(key_name)
                logger.debug(f"Отпущена клавиша: {key_name}, текущие: {self.pressed_keys}")
        except Exception as e:
            logger.error(f"Ошибка в on_release: {e}", exc_info=True)
    
    def _normalize_key(self, key) -> str:
        """Нормализует имя клавиши"""
        try:
            if hasattr(key, 'name') and key.name:
                name = key.name.lower()
                # Маппинг специальных клавиш
                key_map = {
                    'cmd': 'win',
                    'windows': 'win',
                    'lwin': 'win',
                    'rwin': 'win',
                    'lshift': 'shift',
                    'rshift': 'shift',
                    'lctrl': 'ctrl',
                    'rctrl': 'ctrl',
                    'lalt': 'alt',
                    'ralt': 'alt',
                    'return': 'enter',
                    'space': ' ',
                }
                return key_map.get(name, name)
            elif hasattr(key, 'char') and key.char:
                return key.char.lower()
            else:
                key_str = str(key).lower().replace('key.', '')
                # Дополнительные замены
                if 'win' in key_str or 'cmd' in key_str:
                    return 'win'
                return key_str
        except Exception as e:
            logger.warning(f"Не удалось нормализовать клавишу {key}: {e}")
            return ''
    
    def _check_hotkey(self) -> bool:
        """Проверяет, нажата ли вся комбинация"""
        hotkey_set = {k.lower() for k in self.hotkey}
        result = hotkey_set.issubset(self.pressed_keys)
        if result:
            logger.debug(f"Комбинация {hotkey_set} найдена в {self.pressed_keys}")
        return result
    
    def start(self):
        """Запустить прослушивание горячих клавиш"""
        if not PYNPUT_AVAILABLE:
            logger.error("pynput не установлен. Горячие клавиши не будут работать.")
            print("⚠️  pynput не доступен. Установите: pip install pynput")
            return False
        
        try:
            logger.info("Запуск listener горячих клавиш...")
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
            logger.info("Listener горячих клавиш запущен успешно")
            return True
        except Exception as e:
            logger.error(f"Ошибка запуска listener: {e}", exc_info=True)
            return False
    
    def stop(self):
        """Остановить прослушивание"""
        if self.listener:
            try:
                self.listener.stop()
                logger.info("Listener остановлен")
            except Exception as e:
                logger.error(f"Ошибка остановки listener: {e}")
            finally:
                self.listener = None

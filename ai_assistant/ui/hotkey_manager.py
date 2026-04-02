"""
Менеджер горячих клавиш для глобального перехвата комбинаций
"""
import threading
from typing import Callable, Optional

try:
    # Для Windows
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False


class HotkeyManager:
    """Управление глобальными горячими клавишами"""
    
    def __init__(self):
        self.listener: Optional[keyboard.Listener] = None
        self.callback: Optional[Callable] = None
        self.hotkey = ('win', 'shift', 'enter')
        self.pressed_keys = set()
        
    def set_hotkey(self, keys: tuple):
        """Установить комбинацию горячих клавиш"""
        self.hotkey = keys
    
    def set_callback(self, callback: Callable):
        """Установить callback для срабатывания горячей клавиши"""
        self.callback = callback
    
    def _on_press(self, key):
        """Обработчик нажатия клавиш"""
        try:
            # Нормализация клавиш
            key_name = self._normalize_key(key)
            self.pressed_keys.add(key_name)
            
            # Проверка комбинации
            if self._check_hotkey():
                if self.callback:
                    self.callback()
                # Сбрасываем нажатые клавиши после срабатывания
                self.pressed_keys.clear()
                
        except Exception as e:
            print(f"Ошибка в on_press: {e}")
    
    def _on_release(self, key):
        """Обработчик отпускания клавиш"""
        try:
            key_name = self._normalize_key(key)
            self.pressed_keys.discard(key_name)
        except Exception as e:
            print(f"Ошибка в on_release: {e}")
    
    def _normalize_key(self, key) -> str:
        """Нормализует имя клавиши"""
        try:
            if hasattr(key, 'name'):
                return key.name.lower()
            elif hasattr(key, 'char'):
                return key.char.lower() if key.char else ''
            else:
                return str(key).lower().replace('key.', '')
        except:
            return str(key).lower()
    
    def _check_hotkey(self) -> bool:
        """Проверяет, нажата ли вся комбинация"""
        hotkey_set = {k.lower() for k in self.hotkey}
        return hotkey_set.issubset(self.pressed_keys)
    
    def start(self):
        """Запустить прослушивание горячих клавиш"""
        if not PYNPUT_AVAILABLE:
            print("pynput не установлен. Горячие клавиши не будут работать.")
            print("Установите: pip install pynput")
            return
        
        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self.listener.start()
        except Exception as e:
            print(f"Ошибка запуска listener: {e}")
    
    def stop(self):
        """Остановить прослушивание"""
        if self.listener:
            self.listener.stop()
            self.listener = None

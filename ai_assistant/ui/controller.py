"""
UI Контроллер - управляет окном и взаимодействием с пользователем
"""
import tkinter as tk
from typing import Optional, Callable
import threading

from config.settings import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
from pages.assistant_window import AssistantWindow


class UIController:
    """Контроллер пользовательского интерфейса"""
    
    def __init__(self):
        self.root: Optional[tk.Tk] = None
        self.window: Optional[AssistantWindow] = None
        self.is_visible = False
        self.on_message_callback: Optional[Callable] = None
        self.on_screenshot_callback: Optional[Callable] = None
        
    def initialize(self):
        """Инициализация UI (должна вызываться в главном потоке)"""
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        
        # Размеры и позиция
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self.root.minsize(400, 500)
        
        # Создание окна
        self.window = AssistantWindow(self.root)
        
        # Привязка callbacks
        self.window.on_screenshot = self._handle_screenshot_button
        
        # Обработчик закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.hide)
        
    def _handle_screenshot_button(self):
        """Обработчик кнопки скриншота"""
        if self.on_screenshot_callback:
            self.window.set_status("Делаю скриншот...")
            self.on_screenshot_callback()
    
    def show(self):
        """Показать окно"""
        if not self.is_visible:
            if self.root is None:
                self.initialize()
            
            # Показываем окно поверх всех
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            self.root.deiconify()
            self.is_visible = True
            self.window.focus_input()
    
    def hide(self):
        """Скрыть окно (не закрывая приложение)"""
        if self.is_visible and self.root:
            self.root.withdraw()
            self.is_visible = False
    
    def toggle(self):
        """Переключить видимость окна"""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def add_message(self, text: str, sender: str = 'assistant'):
        """Добавить сообщение в чат"""
        if self.window:
            self.window.add_message(text, sender)
    
    def set_status(self, status: str):
        """Установить статус"""
        if self.window:
            self.window.set_status(status)
    
    def clear_chat(self):
        """Очистить чат"""
        if self.window:
            self.window.on_clear()
    
    def run(self):
        """Запустить главный цикл UI"""
        if self.root:
            self.root.mainloop()
    
    def quit(self):
        """Завершить работу UI"""
        if self.root:
            self.root.quit()
            self.root.destroy()

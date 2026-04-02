"""
Page Object для главного окна ассистента
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional


class AssistantWindow:
    """Page Object для основного окна диалога"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("AI Assistant")
        
        # Настройки стиля
        self._setup_styles()
        
        # Переменные
        self.input_text = tk.StringVar()
        self.is_resizable = True
        
        # Создание виджетов
        self._create_widgets()
        
        # Привязка событий
        self._bind_events()
    
    def _setup_styles(self):
        """Настройка стилей интерфейса"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Цветовая схема (темная тема)
        self.colors = {
            'bg': '#1e1e2e',
            'fg': '#cdd6f4',
            'accent': '#89b4fa',
            'input_bg': '#313244',
            'button_bg': '#89b4fa',
            'button_fg': '#1e1e2e',
            'chat_bg': '#181825'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Стили для кнопок
        style.configure('TButton',
                       background=self.colors['button_bg'],
                       foreground=self.colors['button_fg'],
                       padding=10,
                       font=('Segoe UI', 10))
        
        style.map('TButton',
                 background=[('active', '#b4befe')])
    
    def _create_widgets(self):
        """Создание всех виджетов окна"""
        # Основной фрейм
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        self.header_label = tk.Label(
            self.main_frame,
            text="🤖 AI Assistant",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['accent']
        )
        self.header_label.pack(pady=(0, 10))
        
        # Область чата
        self.chat_frame = tk.Frame(self.main_frame, bg=self.colors['chat_bg'])
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg=self.colors['chat_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            selectbackground=self.colors['accent'],
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Настройка тегов для сообщений
        self.chat_display.tag_configure('user', foreground='#a6e3a1', justify='right')
        self.chat_display.tag_configure('assistant', foreground='#89b4fa', justify='left')
        self.chat_display.tag_configure('system', foreground='#f9e2af', justify='center')
        
        # Фрейм ввода
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Поле ввода
        self.input_entry = tk.Entry(
            self.input_frame,
            textvariable=self.input_text,
            font=('Segoe UI', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=self.colors['accent']
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Кнопка отправки
        self.send_button = ttk.Button(
            self.input_frame,
            text="➤ Отправить",
            command=self.on_send
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Кнопки действий
        self.actions_frame = ttk.Frame(self.main_frame)
        self.actions_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.screenshot_btn = ttk.Button(
            self.actions_frame,
            text="📸 Скриншот",
            command=self.on_screenshot
        )
        self.screenshot_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(
            self.actions_frame,
            text="🗑 Очистить",
            command=self.on_clear
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_bar = tk.Label(
            self.main_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9),
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            anchor='w'
        )
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def _bind_events(self):
        """Привязка событий клавиатуры"""
        self.root.bind('<Return>', lambda e: self.on_send())
        self.root.bind('<Escape>', lambda e: self.on_close())
    
    def on_send(self):
        """Обработчик отправки сообщения"""
        message = self.input_text.get().strip()
        if message:
            self.add_message(message, 'user')
            self.input_text.set('')
            return message
        return None
    
    def on_screenshot(self):
        """Обработчик кнопки скриншота"""
        pass  # Будет переопределено контроллером
    
    def on_clear(self):
        """Очистка чата"""
        self.chat_display.delete('1.0', tk.END)
        self.status_var.set("Чат очищен")
    
    def on_close(self):
        """Закрытие окна"""
        self.root.destroy()
    
    def add_message(self, text: str, sender: str = 'assistant'):
        """Добавляет сообщение в чат"""
        tag = sender if sender in ['user', 'assistant', 'system'] else 'assistant'
        self.chat_display.insert(tk.END, f"\n{sender}: ", tag)
        self.chat_display.insert(tk.END, f"{text}\n", tag)
        self.chat_display.see(tk.END)
    
    def set_status(self, status: str):
        """Устанавливает статус в статус-баре"""
        self.status_var.set(status)
    
    def get_input(self) -> str:
        """Получает текст из поля ввода"""
        return self.input_text.get().strip()
    
    def clear_input(self):
        """Очищает поле ввода"""
        self.input_text.set('')
    
    def focus_input(self):
        """Фокусирует поле ввода"""
        self.input_entry.focus_set()

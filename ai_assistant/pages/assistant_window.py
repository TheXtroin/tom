"""
Page Object для главного окна ассистента
Современный дизайн в стиле "Матовое стекло" (Glassmorphism)
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Callable, Optional
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AssistantWindow')


class AssistantWindow:
    """Page Object для основного окна диалога в стиле Glassmorphism"""
    
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
        
        logger.info("AssistantWindow инициализирован")
    
    def _setup_styles(self):
        """Настройка стилей интерфейса в стиле Матовое стекло"""
        style = ttk.Style()
        
        # Пробуем использовать современные темы
        available_themes = style.theme_names()
        logger.debug(f"Доступные темы: {available_themes}")
        
        # Выбираем лучшую доступную тему
        if 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        else:
            style.theme_use('default')
        
        # Цветовая схема "Матовое стекло" (Glassmorphism)
        # Полупрозрачные цвета с размытием
        self.colors = {
            # Основной фон - темный полупрозрачный
            'bg': '#2d2d44',
            # Вторичный фон - более светлый полупрозрачный
            'bg_secondary': '#3a3a5c',
            # Текст - светлый
            'fg': '#e0e0ff',
            # Акцент - голубой неон
            'accent': '#7aa2f7',
            # Акцент при наведении
            'accent_hover': '#9dafff',
            # Фон input поля
            'input_bg': '#1a1a2e',
            # Фон чата
            'chat_bg': '#16162a',
            # Границы
            'border': '#4a4a6a',
            # Сообщение пользователя
            'user_msg': '#414868',
            # Сообщение ассистента
            'assistant_msg': '#2a3150',
            # Системное сообщение
            'system_msg': '#3d3d5c',
        }
        
        # Настройка прозрачности окна (работает только на Windows)
        try:
            # Устанавливаем атрибуты для эффекта стекла
            self.root.attributes('-alpha', 0.95)  # Легкая прозрачность
            logger.debug("Прозрачность окна установлена")
        except Exception as e:
            logger.warning(f"Не удалось установить прозрачность: {e}")
        
        self.root.configure(bg=self.colors['bg'])
        
        # Стили для кнопок
        style.configure(
            'TButton',
            background=self.colors['accent'],
            foreground='#ffffff',
            padding=(15, 8),
            font=('Segoe UI', 10, 'normal'),
            borderwidth=0,
            focusthickness=0
        )
        
        style.map(
            'TButton',
            background=[
                ('active', self.colors['accent_hover']),
                ('pressed', self.colors['accent']),
                ('disabled', '#5a5a7a')
            ],
            foreground=[
                ('disabled', '#8a8aaa')
            ]
        )
        
        # Стиль для фреймов
        style.configure(
            'TFrame',
            background=self.colors['bg_secondary']
        )
    
    def _create_widgets(self):
        """Создание всех виджетов окна"""
        # Главный контейнер с эффектом стекла
        self.main_frame = tk.Frame(
            self.root,
            bg=self.colors['bg_secondary'],
            highlightthickness=0
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Заголовок с градиентным эффектом
        self.header_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['bg_secondary'],
            height=60
        )
        self.header_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.header_label = tk.Label(
            self.header_frame,
            text="✨ AI Assistant",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colors['bg_secondary'],
            fg=self.colors['accent']
        )
        self.header_label.pack(side=tk.LEFT)
        
        # Индикатор статуса (светящаяся точка)
        self.status_indicator = tk.Canvas(
            self.header_frame,
            width=12,
            height=12,
            bg=self.colors['bg_secondary'],
            highlightthickness=0
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=(0, 10))
        self.status_indicator.create_oval(
            2, 2, 10, 10,
            fill='#4ade80',
            outline='#22c55e',
            width=2
        )
        
        # Область чата с эффектом стекла
        self.chat_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['chat_bg'],
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.chat_display = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg=self.colors['chat_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['accent'],
            selectbackground=self.colors['accent'],
            selectforeground='#ffffff',
            relief=tk.FLAT,
            padx=15,
            pady=15,
            borderwidth=0,
            highlightthickness=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Настройка тегов для сообщений
        self.chat_display.tag_configure(
            'user',
            foreground='#a6e3a1',
            justify='right',
            spacing1=5,
            spacing3=5
        )
        self.chat_display.tag_configure(
            'assistant',
            foreground=self.colors['accent'],
            justify='left',
            spacing1=5,
            spacing3=5
        )
        self.chat_display.tag_configure(
            'system',
            foreground='#f9e2af',
            justify='center',
            spacing1=5,
            spacing3=5
        )
        
        # Фрейм ввода с эффектом стекла
        self.input_container = tk.Frame(
            self.main_frame,
            bg=self.colors['bg_secondary'],
            highlightthickness=1,
            highlightbackground=self.colors['border']
        )
        self.input_container.pack(fill=tk.X, pady=(0, 10))
        
        # Поле ввода
        self.input_entry = tk.Entry(
            self.input_container,
            textvariable=self.input_text,
            font=('Segoe UI', 11),
            bg=self.colors['input_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['accent'],
            relief=tk.FLAT,
            highlightthickness=0,
            bd=0
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=10)
        
        # Кнопка отправки
        self.send_button = tk.Button(
            self.input_container,
            text="➤ Отправить",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colors['accent'],
            fg='#ffffff',
            activebackground=self.colors['accent_hover'],
            activeforeground='#ffffff',
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=8,
            command=self.on_send,
            borderwidth=0
        )
        self.send_button.pack(side=tk.RIGHT, padx=(0, 15), pady=5)
        
        # Кнопки действий
        self.actions_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['bg_secondary']
        )
        self.actions_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Кнопка скриншота
        self.screenshot_btn = tk.Button(
            self.actions_frame,
            text="📸 Скриншот",
            font=('Segoe UI', 9),
            bg=self.colors['user_msg'],
            fg=self.colors['fg'],
            activebackground=self.colors['accent'],
            activeforeground='#ffffff',
            relief=tk.FLAT,
            cursor='hand2',
            padx=12,
            pady=6,
            command=self.on_screenshot,
            borderwidth=0
        )
        self.screenshot_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка очистки
        self.clear_btn = tk.Button(
            self.actions_frame,
            text="🗑 Очистить",
            font=('Segoe UI', 9),
            bg=self.colors['user_msg'],
            fg=self.colors['fg'],
            activebackground='#ef4444',
            activeforeground='#ffffff',
            relief=tk.FLAT,
            cursor='hand2',
            padx=12,
            pady=6,
            command=self.on_clear,
            borderwidth=0
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Статус бар с эффектом свечения
        self.status_frame = tk.Frame(
            self.main_frame,
            bg=self.colors['bg_secondary']
        )
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_var = tk.StringVar(value="● Готов к работе")
        self.status_bar = tk.Label(
            self.status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 9, 'italic'),
            bg=self.colors['bg_secondary'],
            fg='#94a3b8',
            anchor='w'
        )
        self.status_bar.pack(fill=tk.X)
    
    def _bind_events(self):
        """Привязка событий клавиатуры"""
        self.root.bind('<Return>', lambda e: self.on_send())
        self.root.bind('<Escape>', lambda e: self.on_close())
        
        # Привязка изменения размера для адаптивности
        self.root.bind('<Configure>', self._on_resize)
        
        logger.debug("События клавиатуры привязаны")
    
    def _on_resize(self, event):
        """Обработчик изменения размера окна"""
        # Можно добавить дополнительную логику адаптации
        pass
    
    def on_send(self):
        """Обработчик отправки сообщения"""
        message = self.input_text.get().strip()
        if message:
            logger.info(f"Отправлено сообщение: {message[:50]}...")
            self.add_message(message, 'user')
            self.input_text.set('')
            return message
        return None
    
    def on_screenshot(self):
        """Обработчик кнопки скриншота"""
        logger.info("Кнопка скриншота нажата")
        pass  # Будет переопределено контроллером
    
    def on_clear(self):
        """Очистка чата"""
        logger.info("Чат очищен")
        self.chat_display.delete('1.0', tk.END)
        self.set_status("● Чат очищен")
    
    def on_close(self):
        """Закрытие окна"""
        logger.info("Окно закрыто")
        self.root.destroy()
    
    def add_message(self, text: str, sender: str = 'assistant'):
        """Добавляет сообщение в чат"""
        tag = sender if sender in ['user', 'assistant', 'system'] else 'assistant'
        
        # Форматирование сообщения
        timestamp = ""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M")
        except:
            pass
        
        formatted_text = f"[{timestamp}] {sender}: {text}\n"
        self.chat_display.insert(tk.END, formatted_text, tag)
        self.chat_display.see(tk.END)
        logger.debug(f"Добавлено сообщение от {sender}")
    
    def set_status(self, status: str):
        """Устанавливает статус в статус-баре"""
        self.status_var.set(f"● {status}")
        logger.debug(f"Статус установлен: {status}")
        
        # Изменение цвета индикатора в зависимости от статуса
        try:
            color = '#4ade80'  # Зеленый - готов
            if 'думаю' in status.lower() or 'загрузка' in status.lower():
                color = '#fbbf24'  # Желтый - обработка
            elif 'ошибка' in status.lower():
                color = '#ef4444'  # Красный - ошибка
            
            self.status_indicator.itemconfig(1, fill=color)
        except:
            pass
    
    def get_input(self) -> str:
        """Получает текст из поля ввода"""
        return self.input_text.get().strip()
    
    def clear_input(self):
        """Очищает поле ввода"""
        self.input_text.set('')
    
    def focus_input(self):
        """Фокусирует поле ввода"""
        self.input_entry.focus_set()
        logger.debug("Поле ввода сфокусировано")

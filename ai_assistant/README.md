# AI Assistant для Windows

Персональный ИИ-ассистент с голосовым управлением, интеграцией с Office и возможностью анализа экрана.

## Возможности

1. **Ответы на вопросы** - Общение с ИИ на естественном языке
2. **Открытие приложений** - Быстрый поиск через меню Пуск или по заданным путям
3. **Открытие сайтов** - Запуск сайтов в Microsoft Edge
4. **Анализ экрана** - Просмотр и анализ содержимого экрана
5. **Работа с Office**:
   - Word: написание текста, создание таблиц, рисование
   - Excel: ввод данных, создание таблиц
   - PowerPoint: создание слайдов, добавление текста
   - Paint: рисование линий, выбор цветов
6. **Управление мышью** - Клик, перемещение, перетаскивание

## Требования

- Windows 10/11
- Python 3.8+
- Microsoft Edge (браузер по умолчанию)

## Установка

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

### 2. Настройте API ключ

Получите API ключ Qwen на [Alibaba Cloud DashScope](https://dashscope.console.aliyun.com/)

Установите ключ одним из способов:

**Способ 1:** В файле `config/settings.py`
```python
QWEN_API_KEY = "your_actual_api_key"
```

**Способ 2:** Через переменную окружения
```bash
set QWEN_API_KEY=your_actual_api_key
```

## Запуск

```bash
python main_entry.py
```

## Использование

### Горячие клавиши

- **Win + Shift + Enter** - Открыть/закрыть окно ассистента

### Примеры команд

```
Открой браузер
Запусти калькулятор
Покажи погоду в Москве
Открой сайт youtube.com
Сделай скриншот и проанализируй
Создай документ Word и напиши привет
Создай таблицу в Excel
Нарисуй линию в Paint
```

## Структура проекта

```
ai_assistant/
├── config/
│   └── settings.py          # Конфигурация и пути к приложениям
├── core/
│   ├── ai_engine.py         # Движок ИИ (Qwen API)
│   └── system_controller.py # Управление системой
├── pages/
│   └── assistant_window.py  # Page Object окна
├── ui/
│   ├── controller.py        # UI контроллер
│   └── hotkey_manager.py    # Менеджер горячих клавиш
├── main.py                  # Главный контроллер
├── main_entry.py            # Точка входа
└── requirements.txt         # Зависимости
```

## Архитектура

Проект использует паттерн **Page Object Model** для разделения логики:

- **AI Engine** - Взаимодействие с облачным ИИ (Qwen)
- **System Controller** - Управление приложениями, мышью, экраном
- **UI Controller** - Управление интерфейсом
- **Hotkey Manager** - Глобальный перехват горячих клавиш
- **Assistant Window** - Page Object основного окна

## Настройка путей к приложениям

Если приложения не находятся в стандартных путях, отредактируйте `config/settings.py`:

```python
APPLICATIONS = {
    "word": r"C:\Your\Path\to\WINWORD.EXE",
    "excel": r"C:\Your\Path\to\EXCEL.EXE",
    "powerpoint": r"C:\Your\Path\to\POWERPNT.EXE",
    "paint": r"C:\Windows\System32\mspaint.exe",
}
```

## Особенности ИИ

- **Модель**: Qwen-max (Alibaba Cloud)
- **Преимущества**:
  - Быстрые ответы (облачный API)
  - Доступен в России
  - Поддержка мультимодальных запросов (текст + изображения)
  - Понимание контекста диалога

## Troubleshooting

### Горячие клавиши не работают
```bash
pip install pynput
```

### Ошибка импорта win32com
```bash
pip install pywin32
```

### Ошибка с меню Пуск
```bash
pip install winshell
```

## Лицензия

MIT License

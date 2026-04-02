"""
Контроллер системы для управления приложениями, мышью и экраном
"""
import subprocess
import time
import base64
from pathlib import Path
from typing import Optional, List
import pyautogui
import pygetwindow as gw
from PIL import Image
import io

# Для работы с меню Пуск в Windows
try:
    import winshell
    from win32com.shell import shell
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False

from config.settings import APPLICATIONS, BROWSER


class SystemController:
    """Управление системой: приложения, мышь, экран"""
    
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        
    def open_application(self, app_name: str) -> bool:
        """
        Открывает приложение по имени
        
        Args:
            app_name: Название приложения (word, excel, paint и т.д.)
            
        Returns:
            True если успешно, иначе False
        """
        app_name = app_name.lower()
        
        # Проверяем в словаре приложений
        if app_name in APPLICATIONS:
            try:
                subprocess.Popen([APPLICATIONS[app_name]])
                return True
            except Exception as e:
                print(f"Ошибка открытия {app_name}: {e}")
                return False
        
        # Если нет в словаре - ищем через поиск Windows
        if WINDOWS_AVAILABLE:
            try:
                # Поиск в меню Пуск
                start_menu = shell.SHGetFolderPath(0, 11, None, 0)
                for root, dirs, files in Path(start_menu).rglob("*"):
                    if files and app_name in files.name.lower():
                        subprocess.Popen([str(files)])
                        return True
            except Exception as e:
                print(f"Ошибка поиска в меню Пуск: {e}")
        
        # Пробуем запустить как команду
        try:
            subprocess.Popen([app_name])
            return True
        except Exception:
            pass
        
        return False
    
    def open_website(self, url: str) -> bool:
        """Открывает сайт в браузере Edge"""
        try:
            if not url.startswith("http"):
                url = "https://" + url
            
            # Открываем в Microsoft Edge
            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            subprocess.Popen([edge_path, url])
            return True
        except Exception as e:
            print(f"Ошибка открытия сайта: {e}")
            # Фоллбэк на браузер по умолчанию
            try:
                import webbrowser
                webbrowser.open(url)
                return True
            except Exception:
                return False
    
    def take_screenshot(self) -> str:
        """
        Делает скриншот экрана и возвращает в base64
        
        Returns:
            Base64 строка изображения
        """
        screenshot = pyautogui.screenshot()
        buffered = io.BytesIO()
        screenshot.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    
    def get_screen_info(self) -> dict:
        """Получает информацию о текущем экране"""
        return {
            "width": self.screen_width,
            "height": self.screen_height,
            "active_window": gw.getActiveWindowTitle() if gw.getActiveWindowTitle() else "None"
        }
    
    def mouse_click(self, x: Optional[int] = None, y: Optional[int] = None, 
                   button: str = "left", clicks: int = 1) -> bool:
        """
        Кликает мышью в указанных координатах
        
        Args:
            x: Координата X (None = текущая позиция)
            y: Координата Y (None = текущая позиция)
            button: 'left', 'right' или 'middle'
            clicks: Количество кликов
        """
        try:
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.3)
            pyautogui.click(clicks=clicks, button=button)
            return True
        except Exception as e:
            print(f"Ошибка клика мышью: {e}")
            return False
    
    def mouse_move(self, x: int, y: int, duration: float = 0.3) -> bool:
        """Перемещает мышь в указанные координаты"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            return True
        except Exception as e:
            print(f"Ошибка перемещения мыши: {e}")
            return False
    
    def mouse_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, 
                  duration: float = 0.5) -> bool:
        """Перетаскивает мышь от одной точки к другой"""
        try:
            pyautogui.moveTo(start_x, start_y)
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
            return True
        except Exception as e:
            print(f"Ошибка перетаскивания: {e}")
            return False
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """Вводит текст с клавиатуры"""
        try:
            pyautogui.write(text, interval=interval)
            return True
        except Exception as e:
            print(f"Ошибка ввода текста: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """Нажимает клавишу"""
        try:
            pyautogui.press(key)
            return True
        except Exception as e:
            print(f"Ошибка нажатия клавиши: {e}")
            return False
    
    def press_keys(self, keys: List[str]) -> bool:
        """Нажимает комбинацию клавиш"""
        try:
            pyautogui.hotkey(*keys)
            return True
        except Exception as e:
            print(f"Ошибка комбинации клавиш: {e}")
            return False
    
    def office_action(self, app: str, action: str, params: str) -> bool:
        """
        Выполняет действия в Office приложениях
        
        Args:
            app: word, excel, powerpoint
            action: write, create_table, draw и т.д.
            params: Параметры действия
        """
        try:
            if app == "word":
                return self._word_action(action, params)
            elif app == "excel":
                return self._excel_action(action, params)
            elif app == "powerpoint":
                return self._ppt_action(action, params)
            elif app == "paint":
                return self._paint_action(action, params)
            return False
        except Exception as e:
            print(f"Ошибка действия в {app}: {e}")
            return False
    
    def _word_action(self, action: str, params: str) -> bool:
        """Действия в Word"""
        try:
            import win32com.client as win32
            
            word = win32.Dispatch("Word.Application")
            word.Visible = True
            
            if not word.Documents.Count:
                word.Documents.Add()
            
            doc = word.ActiveDocument
            
            if action == "write":
                selection = word.Selection
                selection.TypeText(params)
            elif action == "create_table":
                rows, cols, text = params.split("|")
                table = doc.Tables.Add(word.Selection.Range, int(rows), int(cols))
                table.Cell(1, 1).Range.Text = text
            elif action == "draw":
                # Добавляем фигуру
                shape = doc.Shapes.AddLine(
                    Left=100, Top=100, 
                    EndX=200, EndY=200
                )
            
            return True
        except Exception as e:
            print(f"Ошибка Word: {e}")
            return False
    
    def _excel_action(self, action: str, params: str) -> bool:
        """Действия в Excel"""
        try:
            import win32com.client as win32
            
            excel = win32.Dispatch("Excel.Application")
            excel.Visible = True
            
            if not excel.Workbooks.Count:
                excel.Workbooks.Add()
            
            wb = excel.ActiveWorkbook
            ws = wb.ActiveSheet
            
            if action == "write":
                cell, value = params.split("|")
                ws.Range(cell).Value = value
            elif action == "create_table":
                # Пример: A1:C3|data
                range_str, data = params.split("|")
                rows = data.split(";")
                for i, row in enumerate(rows):
                    cells = row.split(",")
                    for j, cell in enumerate(cells):
                        ws.Cells(i+1, j+1).Value = cell.strip()
            
            return True
        except Exception as e:
            print(f"Ошибка Excel: {e}")
            return False
    
    def _ppt_action(self, action: str, params: str) -> bool:
        """Действия в PowerPoint"""
        try:
            import win32com.client as win32
            
            ppt = win32.Dispatch("PowerPoint.Application")
            ppt.Visible = True
            
            if not ppt.Presentations.Count:
                ppt.Presentations.Add()
            
            pres = ppt.ActivePresentation
            
            if action == "add_slide":
                slide = pres.Slides.Add(pres.Slides.Count + 1, 1)  # ppLayoutText
            elif action == "write":
                slide = pres.Slides(1)
                slide.Shapes(1).TextFrame.TextRange.Text = params
            
            return True
        except Exception as e:
            print(f"Ошибка PowerPoint: {e}")
            return False
    
    def _paint_action(self, action: str, params: str) -> bool:
        """Действия в Paint"""
        try:
            if action == "draw_line":
                coords = list(map(int, params.split(",")))
                return self.mouse_drag(coords[0], coords[1], coords[2], coords[3])
            elif action == "click_color":
                coords = list(map(int, params.split(",")))
                return self.mouse_click(coords[0], coords[1])
            return False
        except Exception as e:
            print(f"Ошибка Paint: {e}")
            return False

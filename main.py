import tkinter as tk
from tkinter import ttk, messagebox, font, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
from PIL import Image as PILImage
import mss
import pytesseract
import os
import json
import subprocess
import requests
from spylls.hunspell import Dictionary
import sys
import keyboard
import threading
import socket
import re
import io
import win32clipboard
import win32api
import win32con
import cv2
import numpy as np
from fontTools.ttLib import TTFont
import pystray
import webbrowser
from plyer import notification
import shutil
import collections
import ctypes
import time
from packaging import version
import ctypes
import colorsys

APP_NAME = "Suki Translate"
VERSION = "1.8.0"
GITHUB_REPO_URL = "https://api.github.com/repos/Suki8898/SukiTranslate/releases/latest"

class CustomTitleBar:
    def __init__(self, parent_window, title="Suki Translate", app_ref=None, show_minimize=True, show_maximize=True, show_close=True, use_system_titlebar=False, allow_resize=True):
        self.parent_window = parent_window
        self.title = title
        self.app_ref = app_ref
        self.show_minimize = show_minimize
        self.show_maximize = show_maximize
        self.show_close = show_close
        self.use_system_titlebar = use_system_titlebar
        self.allow_resize = allow_resize
        
        self.start_x = None
        self.start_y = None
        
        self.resize_mode = None
        self.resize_start_x = None
        self.resize_start_y = None
        self.resize_start_geometry = None
        
        if use_system_titlebar:
            parent_window.title(title)
            self.title_bar = None
            self.left_frame = None
            self.right_frame = None
            return
        
        parent_window.overrideredirect(True)
        
        self.title_bar = tk.Frame(parent_window, height=35, relief="flat")
        self.title_bar.pack(fill="x", side="top")
        self.title_bar.pack_propagate(False)
        
        self.left_frame = tk.Frame(self.title_bar)
        self.left_frame.pack(side="left", fill="y", padx=5)
        
        try:
            icon_img = Image.open(ICON_DIR)
            icon_img = icon_img.resize((20, 20), Image.LANCZOS)
            self.icon_photo = ImageTk.PhotoImage(icon_img)
            self.icon_label = tk.Label(self.left_frame, image=self.icon_photo)
            self.icon_label.pack(side="left", padx=(0, 5), pady=7)
        except:
            self.icon_label = tk.Label(self.left_frame, text="S", font=("Arial", 12, "bold"))
            self.icon_label.pack(side="left", padx=(0, 5), pady=7)
        
        self.title_label = tk.Label(self.left_frame, text=title, font=("Arial", 9))
        self.title_label.pack(side="left", pady=10)
        
        self.right_frame = tk.Frame(self.title_bar)
        self.right_frame.pack(side="right", fill="y")
        
        button_width = 45
        button_height = 35
        
        if show_close:
            self.close_button = tk.Button(
                self.right_frame, 
                text="×", 
                font=("Arial", 14, "bold"), 
                width=3, 
                height=1, 
                relief="flat", 
                bd=0, 
                command=self.close_window)
            self.close_button.pack(side="right", fill="y")
            self.setup_button_hover(self.close_button, "#ff4444")
        
        if show_maximize:
            self.maximize_button = tk.Button(
                self.right_frame, 
                text="□", 
                font=("Arial", 12), 
                width=3, 
                height=1, 
                relief="flat", 
                bd=0, 
                command=self.maximize_window)
            self.maximize_button.pack(side="right", fill="y")
            self.setup_button_hover(self.maximize_button)
        
        if show_minimize:
            self.minimize_button = tk.Button(
                self.right_frame,
                text="─", 
                font=("Arial", 12, "bold"), 
                width=3, 
                height=1, 
                relief="flat", 
                bd=0, 
                command=self.minimize_window)
            self.minimize_button.pack(side="right", fill="y")
            self.setup_button_hover(self.minimize_button)
        
        self.bind_drag_events()
        
        if self.allow_resize:
            self.bind_resize_events()
        
        if app_ref:
            self.apply_theme(app_ref.theme_values if hasattr(app_ref, 'theme_values') else self.get_default_theme())
    
    def get_default_theme(self):
        return {
            'bg_color': '#f0f0f0',
            'fg_color': '#000000',
            'active_bg': '#e0e0e0'
        }
    
    def setup_button_hover(self, button, hover_color=None):
        if not hover_color:
            if self.app_ref and hasattr(self.app_ref, 'theme_values'):
                hover_color = self.app_ref.theme_values.get('active_bg', '#e0e0e0')
            else:
                hover_color = '#e0e0e0'
        
        original_color = button.cget('bg')
        
        def on_enter(event):
            button.configure(bg=hover_color)
        
        def on_leave(event):
            if self.app_ref and hasattr(self.app_ref, 'theme_values'):
                button.configure(bg=self.app_ref.theme_values.get('bg_color', original_color))
            else:
                button.configure(bg=original_color)
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    def bind_drag_events(self):
        widgets_to_bind = [self.title_bar, self.left_frame, self.icon_label, self.title_label]
        
        for widget in widgets_to_bind:
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.drag_window)
    
    def bind_resize_events(self):
        self.parent_window.bind("<Motion>", self.on_mouse_motion)
        self.parent_window.bind("<Button-1>", self.on_mouse_click)
        self.parent_window.bind("<B1-Motion>", self.on_mouse_drag)
        self.parent_window.bind("<ButtonRelease-1>", self.on_mouse_release)
    
    def on_mouse_motion(self, event):
        if self.use_system_titlebar:
            return
            
        x, y = event.x_root - self.parent_window.winfo_rootx(), event.y_root - self.parent_window.winfo_rooty()
        width, height = self.parent_window.winfo_width(), self.parent_window.winfo_height()
        
        resize_border = 10
        
        if x <= resize_border and y <= resize_border:
            self.parent_window.config(cursor="top_left_corner")
            self.resize_mode = "nw"
        elif x >= width - resize_border and y <= resize_border:
            self.parent_window.config(cursor="top_right_corner")
            self.resize_mode = "ne"
        elif x <= resize_border and y >= height - resize_border:
            self.parent_window.config(cursor="bottom_left_corner")
            self.resize_mode = "sw"
        elif x >= width - resize_border and y >= height - resize_border:
            self.parent_window.config(cursor="bottom_right_corner")
            self.resize_mode = "se"
        elif x <= resize_border:
            self.parent_window.config(cursor="left_side")
            self.resize_mode = "w"
        elif x >= width - resize_border:
            self.parent_window.config(cursor="right_side")
            self.resize_mode = "e"
        elif y <= resize_border:
            self.parent_window.config(cursor="top_side")
            self.resize_mode = "n"
        elif y >= height - resize_border:
            self.parent_window.config(cursor="bottom_side")
            self.resize_mode = "s"
        else:
            self.parent_window.config(cursor="")
            self.resize_mode = None
    
    def on_mouse_click(self, event):
        if self.resize_mode:
            self.resize_start_x = event.x_root
            self.resize_start_y = event.y_root
            self.resize_start_geometry = self.parent_window.geometry()
            return "break"
        return None
    
    def on_mouse_drag(self, event):
        if self.resize_mode and self.resize_start_x is not None:
            dx = event.x_root - self.resize_start_x
            dy = event.y_root - self.resize_start_y
            
            geometry = self.resize_start_geometry
            parts = geometry.split('+')
            if len(parts) == 3:
                size_part = parts[0]
                x_pos = int(parts[1])
                y_pos = int(parts[2])
            else:
                parts = geometry.split('-')
                size_part = parts[0]
                x_pos = -int(parts[1]) if len(parts) > 1 else 0
                y_pos = -int(parts[2]) if len(parts) > 2 else 0
            
            width, height = map(int, size_part.split('x'))
            
            new_width = width
            new_height = height
            new_x = x_pos
            new_y = y_pos
            
            if 'e' in self.resize_mode:
                new_width = max(200, width + dx)
            if 'w' in self.resize_mode:
                new_width = max(200, width - dx)
                new_x = x_pos + dx
            if 's' in self.resize_mode:
                new_height = max(100, height + dy)
            if 'n' in self.resize_mode:
                new_height = max(100, height - dy)
                new_y = y_pos + dy
            
            self.parent_window.geometry(f"{new_width}x{new_height}+{new_x}+{new_y}")
            return "break"
        return None
    
    def on_mouse_release(self, event):
        if self.resize_mode:
            self.resize_mode = None
            self.resize_start_x = None
            self.resize_start_y = None
            self.resize_start_geometry = None
            self.parent_window.config(cursor="")
            return "break"
        return None
    
    def start_drag(self, event):
        if not self.resize_mode:
            self.start_x = event.x_root
            self.start_y = event.y_root
    
    def drag_window(self, event):
        if not self.resize_mode and self.start_x is not None and self.start_y is not None:
            delta_x = event.x_root - self.start_x
            delta_y = event.y_root - self.start_y
            
            new_x = self.parent_window.winfo_x() + delta_x
            new_y = self.parent_window.winfo_y() + delta_y
            
            self.parent_window.geometry(f"+{new_x}+{new_y}")
            
            self.start_x = event.x_root
            self.start_y = event.y_root
    
    def maximize_window(self):
        if hasattr(self.parent_window, '_is_maximized') and self.parent_window._is_maximized:
            if hasattr(self.parent_window, '_normal_geometry'):
                self.parent_window.geometry(self.parent_window._normal_geometry)
            self.parent_window._is_maximized = False
            self.maximize_button.configure(text="□")
        else:
            self.parent_window._normal_geometry = self.parent_window.geometry()
            screen_width = self.parent_window.winfo_screenwidth()
            screen_height = self.parent_window.winfo_screenheight()
            self.parent_window.geometry(f"{screen_width}x{screen_height}+0+0")
            self.parent_window._is_maximized = True
            self.maximize_button.configure(text="❐")
    
    def close_window(self):
        if self.app_ref and hasattr(self.app_ref, 'root') and self.parent_window == self.app_ref.root:
            if self.app_ref.settings.get("minimize_to_tray", False):
                self.parent_window.withdraw()
                if not self.app_ref.tray_icon or not getattr(self.app_ref, '_tray_thread_started', False):
                    self.app_ref.system_tray_icon()
            else:
                self.app_ref.quit_application()
        else:
            if hasattr(self.parent_window, '_window_close_handler'):
                self.parent_window._window_close_handler()
            else:
                self.cleanup()
                self.parent_window.destroy()
    
    def show_mini_bar(self):
        if hasattr(self, "mini_bar") and self.mini_bar.winfo_exists():
            self.mini_bar.lift()
            return

        self.mini_bar = tk.Toplevel(self.parent_window)
        self.mini_bar.overrideredirect(True)
        self.mini_bar.attributes("-topmost", True)
        self.mini_bar.configure(bg="#2b2b2b")

        self.parent_window.update_idletasks()
        x = self.parent_window.winfo_rootx()
        y = self.parent_window.winfo_rooty()
        main_width = self.parent_window.winfo_width()
        main_height = self.parent_window.winfo_height()

        width, height = 165, 40

        self.mini_bar.geometry(f"{width}x{height}+{x}+{y}")

        try:
            self.mini_bar.wm_attributes("-alpha", 0.92)
        except:
            pass

        def create_rainbow_canvas(parent, text="S u k i T r a n s la t e", font=("ZFVCutiegirl", 11, "bold"), bg="#2b2b2b", speed=50):
            canvas = tk.Canvas(parent, bg=bg, highlightthickness=0)
            canvas.pack(expand=True, fill="both")

            hue = 0.0

            def draw_text():
                nonlocal hue
                canvas.delete("all")

                for i, ch in enumerate(reversed(text)):
                    offset = (hue + i * 0.01) % 1.0
                    r, g, b = [int(255 * v) for v in colorsys.hsv_to_rgb(offset, 1, 1)]
                    color = f'#{r:02x}{g:02x}{b:02x}'
                    canvas.create_text(20 + (len(text) - i - 1) * 5, 20, text=ch, fill=color, font=font, anchor="w")

                hue = (hue + 0.02) % 1.0
                canvas.after(speed, draw_text)

            draw_text()
            return canvas

        canvas = create_rainbow_canvas(self.mini_bar, text="S u k i T r a n s la t e")

        canvas.bind("<Button-1>", self.start_move)
        canvas.bind("<B1-Motion>", self.do_move)
        canvas.bind("<Double-Button-1>", lambda e: self.restore_main_window())
        canvas.bind("<Enter>", lambda e: canvas.configure(bg="#3c3c3c"))
        canvas.bind("<Leave>", lambda e: canvas.configure(bg="#2b2b2b"))

    def start_move(self, event):
        self._x = event.x
        self._y = event.y

    def do_move(self, event):
        x = event.x_root - self._x
        y = event.y_root - self._y
        self.mini_bar.geometry(f"+{x}+{y}")

    def restore_main_window(self):
        if hasattr(self, "mini_bar") and self.mini_bar.winfo_exists():
            self.mini_bar.update_idletasks()
            x = self.mini_bar.winfo_x()
            y = self.mini_bar.winfo_y()
            self.mini_bar.destroy()

            self.parent_window.geometry(f"+{x}+{y}")

        self.parent_window.deiconify()
        self.parent_window.lift()
        self.parent_window.attributes("-topmost", True)
        self.parent_window.after(100, lambda: self.parent_window.attributes("-topmost", False))

    def minimize_window(self):
        if self.app_ref and hasattr(self.app_ref, 'root') and self.parent_window == self.app_ref.root:
            self.parent_window.withdraw()
            self.show_mini_bar()
            if not self.app_ref.tray_icon or not getattr(self.app_ref, '_tray_thread_started', False):
                self.app_ref.system_tray_icon()
        else:
            self.parent_window.withdraw()

    def apply_theme(self, theme_values):

        try:
            if self.use_system_titlebar:
                return
                
            if self.is_destroyed():
                return
                
            bg_color = theme_values.get('bg_color', '#f0f0f0')
            fg_color = theme_values.get('fg_color', '#000000')
            active_bg = theme_values.get('active_bg', '#e0e0e0')
            
            if self.title_bar.winfo_exists():
                self.title_bar.configure(bg=bg_color)
            if self.left_frame.winfo_exists():
                self.left_frame.configure(bg=bg_color)
            if self.right_frame.winfo_exists():
                self.right_frame.configure(bg=bg_color)
            
            if self.icon_label.winfo_exists():
                self.icon_label.configure(bg=bg_color, fg=fg_color)
            if self.title_label.winfo_exists():
                self.title_label.configure(bg=bg_color, fg=fg_color)
            
            if hasattr(self, 'minimize_button') and self.minimize_button.winfo_exists():
                self.minimize_button.configure(bg=bg_color, fg=fg_color, activebackground=active_bg)
            if hasattr(self, 'maximize_button') and self.maximize_button.winfo_exists():
                self.maximize_button.configure(bg=bg_color, fg=fg_color, activebackground=active_bg)
            if hasattr(self, 'close_button') and self.close_button.winfo_exists():
                self.close_button.configure(bg=bg_color, fg=fg_color, activebackground="#ff4444")
        except tk.TclError:
            pass
    
    def cleanup(self):

        self._destroyed = True
        
        if self.use_system_titlebar:
            return
            
        self.title_bar = None
        self.left_frame = None
        self.right_frame = None
        self.icon_label = None
        self.title_label = None
        if hasattr(self, 'minimize_button'):
            self.minimize_button = None
        if hasattr(self, 'maximize_button'):
            self.maximize_button = None
        if hasattr(self, 'close_button'):
            self.close_button = None
    
    def is_destroyed(self):

        if getattr(self, '_destroyed', False):
            return True
            
        if self.use_system_titlebar:
            try:
                return self.parent_window is None or not self.parent_window.winfo_exists()
            except (tk.TclError, AttributeError):
                return True
                
        try:
            return self.parent_window is None or not self.parent_window.winfo_exists()
        except (tk.TclError, AttributeError):
            return True


APPDATA_DIR = os.path.join(os.getenv('APPDATA'), 'Suki8898', 'SukiTranslate')
os.makedirs(APPDATA_DIR, exist_ok=True)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

HUNSPELL_DIR = os.path.join(APPDATA_DIR, 'hunspell')
os.makedirs(HUNSPELL_DIR, exist_ok=True)

TESSDATA_DIR = os.path.join(APPDATA_DIR, 'tessdata')
os.makedirs(TESSDATA_DIR, exist_ok=True)

TRANSLATORS_DIR = os.path.join(APPDATA_DIR, 'translators')
os.makedirs(TRANSLATORS_DIR, exist_ok=True)

TESSERACT_DIR = os.path.join(PROJECT_DIR, "Tesseract-OCR", "tesseract.exe")
if not os.path.exists(TESSERACT_DIR):
    messagebox.showerror("Error", f"Tesseract.exe not found at: {TESSERACT_DIR}. Please check the path.")
    exit()
pytesseract.pytesseract.tesseract_cmd = TESSERACT_DIR

NODE_MODULES_DIR = os.path.join(APPDATA_DIR, 'node_modules')            

if getattr(sys, 'frozen', False):
    _base_bundle_dir = os.path.dirname(sys.executable)
    NODE_DIR = os.path.join(_base_bundle_dir, 'Node', 'node.exe')
    NPM_DIR = os.path.join(_base_bundle_dir, 'Node', 'npm.cmd')
else:
    NODE_DIR = os.path.join(PROJECT_DIR, 'Node', 'node.exe')
    NPM_DIR = os.path.join(PROJECT_DIR, 'Node', 'npm.cmd')

if getattr(sys, 'frozen', False):
    _base_bundle_dir = sys._MEIPASS
    ICON_DIR = os.path.join(_base_bundle_dir, 'icons', 'icon.ico')
else:
    ICON_DIR = os.path.join(PROJECT_DIR, 'icons', 'icon.ico')

LOCK_FILE = os.path.join(APPDATA_DIR, 'app.lock')


GLOBAL_LOG_BUFFER = collections.deque(maxlen=2000) 
ACTIVE_LOG_WIDGET = None 

settings_path = os.path.join(os.getenv('APPDATA'), 'Suki8898', 'SukiTranslate', 'settings.json')
run_as_admin = False
if os.path.exists(settings_path):
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings_data = json.load(f)
            run_as_admin = settings_data.get("run_as_admin", False)
    except:
        pass

if run_as_admin and not ctypes.windll.shell32.IsUserAnAdmin():
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        os._exit(0)
    except Exception as e:
        print(f"Failed to restart as admin: {e}")
        os._exit(1)


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    ctypes.windll.user32.SetProcessDPIAware()

class GlobalTextRedirector:
    def write(self, string):
        GLOBAL_LOG_BUFFER.append(string)
        if ACTIVE_LOG_WIDGET and ACTIVE_LOG_WIDGET.winfo_exists():
            try:
                ACTIVE_LOG_WIDGET.configure(state='normal')
                ACTIVE_LOG_WIDGET.insert(tk.END, string)
                ACTIVE_LOG_WIDGET.see(tk.END)
                ACTIVE_LOG_WIDGET.configure(state='disabled')
            except tk.TclError: 
                pass

    def flush(self):
        pass

LANGUAGE_MAPPING = {
    "Afrikaans": {"code": "af", "tess_code": "afr"},
    "Amharic": {"code": "am", "tess_code": "amh"},
    "Arabic": {"code": "ar", "tess_code": "ara"},
    "Assamese": {"code": "as", "tess_code": "asm"},
    "Azerbaijani": {"code": "az", "tess_code": "aze"},
    "Belarusian": {"code": "be", "tess_code": "bel"},
    "Bengali": {"code": "bn", "tess_code": "ben"},
    "Tibetan": {"code": "bo", "tess_code": "bod"},
    "Bosnian": {"code": "bs", "tess_code": "bos"},
    "Bulgarian": {"code": "bg", "tess_code": "bul"},
    "Catalan": {"code": "ca", "tess_code": "cat"},
    "Cebuano": {"code": "ceb", "tess_code": "ceb"},
    "Czech": {"code": "cs", "tess_code": "ces"},
    "Chinese (Simplified)": {"code": "zh", "tess_code": "chi_sim"},
    "Chinese (Traditional)": {"code": "zh", "tess_code": "chi_tra"},
    "Cherokee": {"code": "chr", "tess_code": "chr"},
    "Welsh": {"code": "cy", "tess_code": "cym"},
    "Danish": {"code": "da", "tess_code": "dan"},
    "German": {"code": "de", "tess_code": "deu"},
    "Dzongkha": {"code": "dz", "tess_code": "dzo"},
    "Greek": {"code": "el", "tess_code": "ell"},
    "English": {"code": "en", "tess_code": "eng"},
    "Esperanto": {"code": "eo", "tess_code": "epo"},
    "Estonian": {"code": "et", "tess_code": "est"},
    "Basque": {"code": "eu", "tess_code": "eus"},
    "Persian": {"code": "fa", "tess_code": "fas"},
    "Finnish": {"code": "fi", "tess_code": "fin"},
    "French": {"code": "fr", "tess_code": "fra"},
    "Irish": {"code": "ga", "tess_code": "gle"},
    "Galician": {"code": "gl", "tess_code": "glg"},
    "Gujarati": {"code": "gu", "tess_code": "guj"},
    "Haitian Creole": {"code": "ht", "tess_code": "hat"},
    "Hebrew": {"code": "he", "tess_code": "heb"},
    "Hindi": {"code": "hi", "tess_code": "hin"},
    "Croatian": {"code": "hr", "tess_code": "hrv"},
    "Hungarian": {"code": "hu", "tess_code": "hun"},
    "Armenian": {"code": "hy", "tess_code": "hye"},
    "Indonesian": {"code": "id", "tess_code": "ind"},
    "Icelandic": {"code": "is", "tess_code": "isl"},
    "Italian": {"code": "it", "tess_code": "ita"},
    "Javanese": {"code": "jv", "tess_code": "jav"},
    "Japanese": {"code": "ja", "tess_code": "jpn"},
    "Kannada": {"code": "kn", "tess_code": "kan"},
    "Georgian": {"code": "ka", "tess_code": "kat"},
    "Kazakh": {"code": "kk", "tess_code": "kaz"},
    "Khmer": {"code": "km", "tess_code": "khm"},
    "Korean": {"code": "ko", "tess_code": "kor"},
    "Kurdish": {"code": "ku", "tess_code": "kur"},
    "Kyrgyz": {"code": "ky", "tess_code": "kir"},
    "Lao": {"code": "lo", "tess_code": "lao"},
    "Latin": {"code": "la", "tess_code": "lat"},
    "Latvian": {"code": "lv", "tess_code": "lav"},
    "Lithuanian": {"code": "lt", "tess_code": "lit"},
    "Luxembourgish": {"code": "lb", "tess_code": "ltz"},
    "Macedonian": {"code": "mk", "tess_code": "mkd"},
    "Malayalam": {"code": "ml", "tess_code": "mal"},
    "Marathi": {"code": "mr", "tess_code": "mar"},
    "Malay": {"code": "ms", "tess_code": "msa"},
    "Burmese": {"code": "my", "tess_code": "mya"},
    "Nepali": {"code": "ne", "tess_code": "nep"},
    "Dutch": {"code": "nl", "tess_code": "nld"},
    "Norwegian": {"code": "no", "tess_code": "nor"},
    "Occitan": {"code": "oc", "tess_code": "oci"},
    "Oriya": {"code": "or", "tess_code": "ori"},
    "Punjabi": {"code": "pa", "tess_code": "pan"},
    "Polish": {"code": "pl", "tess_code": "pol"},
    "Portuguese": {"code": "pt", "tess_code": "por"},
    "Romanian": {"code": "ro", "tess_code": "ron"},
    "Russian": {"code": "ru", "tess_code": "rus"},
    "Sanskrit": {"code": "sa", "tess_code": "san"},
    "Sinhala": {"code": "si", "tess_code": "sin"},
    "Slovak": {"code": "sk", "tess_code": "slk"},
    "Slovenian": {"code": "sl", "tess_code": "slv"},
    "Spanish": {"code": "es", "tess_code": "spa"},
    "Albanian": {"code": "sq", "tess_code": "sqi"},
    "Serbian": {"code": "sr", "tess_code": "srp"},
    "Swedish": {"code": "sv", "tess_code": "swe"},
    "Swahili": {"code": "sw", "tess_code": "swa"},
    "Tamil": {"code": "ta", "tess_code": "tam"},
    "Telugu": {"code": "te", "tess_code": "tel"},
    "Tajik": {"code": "tg", "tess_code": "tgk"},
    "Tagalog": {"code": "tl", "tess_code": "tgl"},
    "Thai": {"code": "th", "tess_code": "tha"},
    "Turkish": {"code": "tr", "tess_code": "tur"},
    "Uyghur": {"code": "ug", "tess_code": "uig"},
    "Ukrainian": {"code": "uk", "tess_code": "ukr"},
    "Urdu": {"code": "ur", "tess_code": "urd"},
    "Uzbek": {"code": "uz", "tess_code": "uzb"},
    "Vietnamese": {"code": "vi", "tess_code": "vie"},
    "Yiddish": {"code": "yi", "tess_code": "yid"},
    "Yoruba": {"code": "yo", "tess_code": "yor"}
}

def is_already_running():
    try:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read())
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("localhost", 8898))
                s.send(b"EXIT")
                s.close()
                # Wait for the old instance to close
                time.sleep(1.0)
                # Check if the old instance has actually closed
                max_wait = 5  # Maximum wait time in seconds
                wait_count = 0
                while os.path.exists(LOCK_FILE) and wait_count < max_wait:
                    time.sleep(0.5)
                    wait_count += 0.5
                # Continue with new instance setup
                if os.path.exists(LOCK_FILE):
                    os.remove(LOCK_FILE)
                # Don't return True here - let the new instance continue
            except (OSError, socket.error):
                if os.path.exists(LOCK_FILE):
                    os.remove(LOCK_FILE)
    except Exception:
        pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("localhost", 8898))
        s.listen(1)
        threading.Thread(target=exit, args=(s,), daemon=True).start()
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
        return False
    except socket.error:
        return True

def exit(server_socket):
    while True:
        try:
            client_socket, _ = server_socket.accept()
            data = client_socket.recv(1024)
            if data == b"EXIT":
                client_socket.close()
                server_socket.close()
                if 'app' in globals():
                    app.quit_application()
                break
        except:
            break
        
def download_traineddata(lang_code):
    tessdata_url = f"https://github.com/tesseract-ocr/tessdata/raw/main/{lang_code}.traineddata"
    local_path = os.path.join(TESSDATA_DIR, f"{lang_code}.traineddata")
    
    try:
        print(f"Downloading {lang_code}.traineddata...")
        response = requests.get(tessdata_url, stream=True)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded {lang_code}.traineddata")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {lang_code}.traineddata: {e}")
        return False
    except Exception as e:
        print(f"Error downloading {lang_code}.traineddata: {e}")
        return False

def get_available_dictionaries():
    try:
        response = requests.get("https://api.github.com/repos/wooorm/dictionaries/contents/dictionaries")
        response.raise_for_status()
        return [item['name'] for item in response.json() if item['type'] == 'dir']
    except Exception as e:
        print(f"Error fetching available dictionaries: {e}")
        return ['en', 'vi'] 

def download_hunspell_dict(lang_code):
    short_lang_code = lang_code.split('_')[0].lower()
    aff_path = os.path.join(HUNSPELL_DIR, f"{lang_code}.aff")
    dic_path = os.path.join(HUNSPELL_DIR, f"{lang_code}.dic")
    if os.path.exists(aff_path) and os.path.exists(dic_path):
        return (aff_path, dic_path)
    base_url = "https://raw.githubusercontent.com/wooorm/dictionaries/main/dictionaries"
    aff_url = f"{base_url}/{short_lang_code}/index.aff"
    dic_url = f"{base_url}/{short_lang_code}/index.dic"
    try:
        print(f"Downloading Hunspell {lang_code}...")
        response = requests.get(aff_url)
        response.raise_for_status()
        with open(aff_path, 'wb') as f:
            f.write(response.content)
        response = requests.get(dic_url)
        response.raise_for_status()
        with open(dic_path, 'wb') as f:
            f.write(response.content)
            
        print(f"Successfully downloaded Hunspell {lang_code}")
        return (aff_path, dic_path)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Dictionary {lang_code} does not exist in the repository")
        else:
            print(f"Error downloading Hunspell dictionary {lang_code}: {e}")
        return None
    except Exception as e:
        print(f"Error downloading Hunspell dictionary {lang_code}: {e}")
        return None

def check_spelling(text, lang_code='en'):
    short_lang_code = lang_code.split('_')[0] if '_' in lang_code else lang_code
    dict_paths = download_hunspell_dict(short_lang_code)
    if not dict_paths:
        print(f"No dictionary found for language {lang_code}, skipping spell check")
        return True, [] 
    aff_path, dic_path = dict_paths
    try:
        dict_name = dic_path.replace('.dic', '')
        hobj = Dictionary.from_files(dict_name)
    except Exception as e:
        print(f"Error loading dictionary {lang_code}: {e}")
        return True, []
    
    words = text.split()
    misspelled = []
    for word in words:
        clean_word = word.strip('.,!?()[]{}"\'').lower()
        if clean_word and not hobj.lookup(clean_word):
            misspelled.append(word)
    
    return len(misspelled) == 0, misspelled

def copy_original_text(text):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    finally:
        win32clipboard.CloseClipboard()

def copy_translated_text(text):
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, text)
    finally:
        win32clipboard.CloseClipboard()

def copy_image(image):
    try:
        output = io.BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    finally:
        win32clipboard.CloseClipboard()

def find_font_path(font_name):
    font_directories = [
        "C:/Windows/Fonts",
        os.path.join(os.getenv('LOCALAPPDATA'), "Microsoft", "Windows", "Fonts")
    ]
    for directory in font_directories:
        if not os.path.exists(directory):
            continue
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".ttf") or file.endswith(".otf"):
                    try:
                        font_path = os.path.join(root, file)
                        ttfont = TTFont(font_path)
                        for record in ttfont['name'].names:
                             if record.nameID == 4 and record.platformID == 3 and record.platEncID == 1 and record.langID == 0x409:
                                if record.string.decode('utf-16be', 'ignore').strip() == font_name:
                                    return font_path
                    except:
                        pass
    return None

def wrap_text(text, font, max_width):
    lines = []
    words = text.split()
    current_line = ""
    for word in words:
        bbox = font.getbbox(current_line + word)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            current_line += word + " "
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines

def set_startup(enabled):
    import winreg
    app_path = os.path.abspath(sys.argv[0])
    key = winreg.HKEY_CURRENT_USER
    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
    try:
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE) as regkey:
            if enabled:
                winreg.SetValueEx(regkey, APP_NAME, 0, winreg.REG_SZ, app_path)
            else:
                try:
                    winreg.DeleteValue(regkey, APP_NAME)
                except WindowsError:
                    pass
        return True
    except Exception as e:
        print(f"Error modifying startup: {e}")
        return False

def prepare_image(image):
    img_array = np.array(image)
    return Image.fromarray(img_array)

class SpellChecker:
    def __init__(self):
        self.current_dict = None
        self.current_lang = None

    def get_dict_for_language(self, lang_name):
        if lang_name in LANGUAGE_MAPPING:
            return LANGUAGE_MAPPING[lang_name]["code"]
        return None

    def download_dictionary(self, lang_code):
        short_lang_code = lang_code.split('_')[0]
        base_url = "https://raw.githubusercontent.com/wooorm/dictionaries/main/dictionaries"
        aff_url = f"{base_url}/{short_lang_code}/index.aff"
        dic_url = f"{base_url}/{short_lang_code}/index.dic"
        try:
            os.makedirs(os.path.join(HUNSPELL_DIR, lang_code), exist_ok=True)
            aff_path = os.path.join(HUNSPELL_DIR, lang_code, f"{lang_code}.aff")
            if not os.path.exists(aff_path):
                response = requests.get(aff_url)
                response.raise_for_status()
                with open(aff_path, 'wb') as f:
                    f.write(response.content)
            dic_path = os.path.join(HUNSPELL_DIR, lang_code, f"{lang_code}.dic")
            if not os.path.exists(dic_path):
                response = requests.get(dic_url)
                response.raise_for_status()
                with open(dic_path, 'wb') as f:
                    f.write(response.content)
            return True
        except Exception as e:
            print(f"Error downloading dictionary {lang_code}: {e}")
            return False

    def load_dictionary_for_language(self, lang_name):
        lang_code = self.get_dict_for_language(lang_name)
        if not lang_code:
            self.current_dict = None
            self.current_lang = None
            return False
        dict_code = f"{lang_code}_US" if lang_code == "en" else lang_code      
        dict_path = os.path.join(HUNSPELL_DIR, dict_code, dict_code)     
        if not os.path.exists(f"{dict_path}.aff") or not os.path.exists(f"{dict_path}.dic"):
            if not self.download_dictionary(dict_code):
                return False
        
        try:
            self.current_dict = Dictionary.from_files(dict_path)
            self.current_lang = dict_code
            return True
        except Exception as e:
            print(f"Error loading dictionary {dict_code}: {e}")
            return False
    
    def check_spelling(self, text):
        if not self.current_dict:
            return True, []
        words = text.split()
        misspelled = []
        for word in words:
            clean_word = ''.join(c for c in word if c.isalpha())
            if clean_word and not self.current_dict.lookup(clean_word):
                misspelled.append(clean_word)
        
        return len(misspelled) == 0, misspelled

class UpdateChecker:
    def __init__(self, app_ref):
        self.app_ref = app_ref
        self.github_api_url = GITHUB_REPO_URL
        
    def check_for_updates(self, show_no_update_message=False):
        try:
            headers = {
                'User-Agent': f'{APP_NAME}/{VERSION}'
            }
            
            response = requests.get(self.github_api_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            
            if not latest_version:
                if show_no_update_message:
                    self.show_update_info_dialog("Update Check", "Unable to determine latest version.")
                return False
                
            try:
                if version.parse(latest_version) > version.parse(VERSION):
                    self.show_update_dialog(latest_version, release_data)
                    return True
                else:
                    if show_no_update_message:
                        self.show_update_info_dialog("Update Check", f"You have the latest version ({VERSION}).")
                    return False
            except Exception as e:
                print(f"Version comparison error: {e}")
                if show_no_update_message:
                    self.show_update_info_dialog("Update Check", "Unable to compare versions.")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Network error checking for updates: {e}")
            if show_no_update_message:
                self.show_update_error_dialog("Update Check", "Unable to check for updates. Please check your internet connection.")
            return False
        except Exception as e:
            print(f"Error checking for updates: {e}")
            if show_no_update_message:
                self.show_update_error_dialog("Update Check", f"Error checking for updates: {e}")
            return False
    
    def show_update_message_dialog(self, title, message, message_type="info"):
        msg_window = tk.Toplevel(self.app_ref.root)
        msg_window.title(title)
        msg_window.geometry("400x150")
        msg_window.resizable(False, False)
        msg_window.grab_set()
        
        msg_window.update_idletasks()
        x = (msg_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (msg_window.winfo_screenheight() // 2) - (150 // 2)
        msg_window.geometry(f"400x150+{x}+{y}")
        
        try:
            msg_window.iconbitmap(ICON_DIR)
        except:
            pass
        
        custom_title_bar = CustomTitleBar(msg_window, title, app_ref=self.app_ref, show_maximize=False, use_system_titlebar=False)
        
        if hasattr(self.app_ref, 'custom_title_bars'):
            self.app_ref.custom_title_bars.append(custom_title_bar)
        
        def on_msg_close():
            if hasattr(self.app_ref, 'custom_title_bars') and custom_title_bar in self.app_ref.custom_title_bars:
                self.app_ref.custom_title_bars.remove(custom_title_bar)
            custom_title_bar.cleanup()
            msg_window.destroy()
        
        msg_window.protocol("WM_DELETE_WINDOW", on_msg_close)
        
        main_frame = ttk.Frame(msg_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        icon_text = "ℹ️" if message_type == "info" else "❌"
        icon_label = ttk.Label(content_frame, text=icon_text, font=("Arial", 16))
        icon_label.pack(side="left", padx=(0, 10))
        
        msg_label = ttk.Label(content_frame, text=message, wraplength=300, font=("Arial", 10))
        msg_label.pack(side="left", fill="both", expand=True)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        ok_button = ttk.Button(button_frame, text="OK", command=on_msg_close)
        ok_button.pack(side="right")
        
        ok_button.focus()
        
        msg_window.bind('<Return>', lambda e: on_msg_close())
    
    def show_update_info_dialog(self, title, message):
        self.show_update_message_dialog(title, message, "info")
    
    def show_update_error_dialog(self, title, message):
        self.show_update_message_dialog(title, message, "error")

    def show_update_dialog(self, latest_version, release_data):
        release_notes = release_data.get('body', 'No release notes available.')
        download_url = release_data.get('html_url', 'https://github.com/Suki8898/SukiTranslate/releases/latest')
        
        update_window = tk.Toplevel(self.app_ref.root)
        update_window.title("Update Available")
        update_window.geometry("500x400")
        update_window.resizable(False, False)
        update_window.grab_set()
        
        update_window.update_idletasks()
        x = (update_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (update_window.winfo_screenheight() // 2) - (400 // 2)
        update_window.geometry(f"500x400+{x}+{y}")
        
        try:
            update_window.iconbitmap(ICON_DIR)
        except:
            pass
        
        custom_title_bar = CustomTitleBar(update_window, "Update Available", app_ref=self.app_ref, show_maximize=True, use_system_titlebar=False)
        
        if hasattr(self.app_ref, 'custom_title_bars'):
            self.app_ref.custom_title_bars.append(custom_title_bar)
        
        def on_update_close():
            if hasattr(self.app_ref, 'custom_title_bars') and custom_title_bar in self.app_ref.custom_title_bars:
                self.app_ref.custom_title_bars.remove(custom_title_bar)
            custom_title_bar.cleanup()
            update_window.destroy()
        
        update_window.protocol("WM_DELETE_WINDOW", on_update_close)
            
        main_frame = ttk.Frame(update_window, padding="20")
        main_frame.pack(fill="both", expand=True)

        title_label = ttk.Label(main_frame, text="Update Available!", font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(version_frame, text=f"Current version: {VERSION}", font=("Arial", 10)).pack(anchor="w")
        ttk.Label(version_frame, text=f"Latest version: {latest_version}", font=("Arial", 10, "bold")).pack(anchor="w")
        
        notes_label = ttk.Label(main_frame, text="Release Notes:", font=("Arial", 10, "bold"))
        notes_label.pack(anchor="w", pady=(10, 5))
        
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        theme = self.app_ref.theme_values
        text_bg = theme.get('bg_color', '#ffffff')
        text_fg = theme.get('fg_color', '#000000')
        
        notes_text = tk.Text(text_frame, wrap="word", height=10, font=("Arial", 9),
                            bg=text_bg, fg=text_fg, insertbackground=text_fg,
                            selectbackground="#0078d4", selectforeground="white")
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=notes_text.yview)
        notes_text.configure(yscrollcommand=scrollbar.set)
        
        notes_text.insert("1.0", release_notes)
        notes_text.config(state="disabled")
        
        notes_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        def open_download_page():
            webbrowser.open(download_url)
            on_update_close()
        
        ttk.Button(button_frame, text="Download Update", command=open_download_page).pack(side="left")
        
    def check_for_updates_on_startup(self):
        if not self.app_ref.settings.get("auto_check_updates", True):
            return
            
        last_check = self.app_ref.settings.get("last_update_check", 0)
        current_time = time.time()
        
        if current_time - last_check > 86400:
            settings = self.app_ref.settings.copy()
            settings["last_update_check"] = current_time
            self.app_ref.settings_manager.save_settings(settings)
            self.app_ref.settings = settings
            
            threading.Thread(target=self.check_for_updates, daemon=True).start()
    
    def show_update_info_dialog(self, title, message):
        info_window = tk.Toplevel(self.app_ref.root)
        info_window.geometry("400x200")
        info_window.resizable(False, False)
        info_window.grab_set()
        
        info_window.update_idletasks()
        x = (info_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (info_window.winfo_screenheight() // 2) - (200 // 2)
        info_window.geometry(f"400x200+{x}+{y}")
        
        try:
            info_window.iconbitmap(ICON_DIR)
        except:
            pass
        
        custom_title_bar = CustomTitleBar(info_window, title, app_ref=self.app_ref, show_maximize=False, use_system_titlebar=False)
        
        if hasattr(self.app_ref, 'custom_title_bars'):
            self.app_ref.custom_title_bars.append(custom_title_bar)
        
        def on_info_close():
            if hasattr(self.app_ref, 'custom_title_bars') and custom_title_bar in self.app_ref.custom_title_bars:
                self.app_ref.custom_title_bars.remove(custom_title_bar)
            custom_title_bar.cleanup()
            info_window.destroy()
        
        info_window.protocol("WM_DELETE_WINDOW", on_info_close)
            
        main_frame = ttk.Frame(info_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        message_label = ttk.Label(main_frame, text=message, wraplength=350, justify="center", font=("Arial", 10))
        message_label.pack(pady=(20, 30), expand=True)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="OK", command=on_info_close).pack(anchor="center")
        
    def show_update_error_dialog(self, title, message):
        error_window = tk.Toplevel(self.app_ref.root)
        error_window.geometry("400x200")
        error_window.resizable(False, False)
        error_window.grab_set()
        
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (error_window.winfo_screenheight() // 2) - (200 // 2)
        error_window.geometry(f"400x200+{x}+{y}")
        
        try:
            error_window.iconbitmap(ICON_DIR)
        except:
            pass
        
        custom_title_bar = CustomTitleBar(error_window, title, app_ref=self.app_ref, show_maximize=False, use_system_titlebar=False)
        
        if hasattr(self.app_ref, 'custom_title_bars'):
            self.app_ref.custom_title_bars.append(custom_title_bar)
        
        def on_error_close():
            if hasattr(self.app_ref, 'custom_title_bars') and custom_title_bar in self.app_ref.custom_title_bars:
                self.app_ref.custom_title_bars.remove(custom_title_bar)
            custom_title_bar.cleanup()
            error_window.destroy()
        
        error_window.protocol("WM_DELETE_WINDOW", on_error_close)
            
        main_frame = ttk.Frame(error_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill="both")
        
        message_label = ttk.Label(content_frame, text=message, wraplength=350, justify="center", font=("Arial", 10), foreground="red")
        message_label.pack(pady=(20, 30), expand=True)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="OK", command=on_error_close).pack(anchor="center")

    def show_custom_info_dialog(self, title, message):
        info_window = tk.Toplevel(self.window)
        info_window.geometry("400x200")
        info_window.resizable(False, False)
        info_window.grab_set()
        
        info_window.update_idletasks()
        x = (info_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (info_window.winfo_screenheight() // 2) - (200 // 2)
        info_window.geometry(f"400x200+{x}+{y}")
        
        try:
            info_window.iconbitmap(ICON_DIR)
        except:
            pass
        
        custom_title_bar = CustomTitleBar(info_window, title, app_ref=self.app, show_maximize=False, use_system_titlebar=False)
        
        if hasattr(self.app, 'custom_title_bars'):
            self.app.custom_title_bars.append(custom_title_bar)
        
        def on_info_close():
            if hasattr(self.app, 'custom_title_bars') and custom_title_bar in self.app.custom_title_bars:
                self.app.custom_title_bars.remove(custom_title_bar)
            custom_title_bar.cleanup()
            info_window.destroy()
        
        info_window.protocol("WM_DELETE_WINDOW", on_info_close)
            
        main_frame = ttk.Frame(info_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        message_label = ttk.Label(main_frame, text=message, wraplength=350, justify="center", font=("Arial", 10))
        message_label.pack(pady=(20, 30), expand=True)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="OK", command=on_info_close).pack(anchor="center")
        
    def show_custom_error_dialog(self, title, message):
        error_window = tk.Toplevel(self.window)
        error_window.geometry("400x200")
        error_window.resizable(False, False)
        error_window.grab_set()
        
        error_window.update_idletasks()
        x = (error_window.winfo_screenwidth() // 2) - (400 // 2)
        y = (error_window.winfo_screenheight() // 2) - (200 // 2)
        error_window.geometry(f"400x200+{x}+{y}")
        
        try:
            error_window.iconbitmap(ICON_DIR)
        except:
            pass
        
        custom_title_bar = CustomTitleBar(error_window, title, app_ref=self.app, show_maximize=False, use_system_titlebar=False)
        
        if hasattr(self.app, 'custom_title_bars'):
            self.app.custom_title_bars.append(custom_title_bar)
        
        def on_error_close():
            if hasattr(self.app, 'custom_title_bars') and custom_title_bar in self.app.custom_title_bars:
                self.app.custom_title_bars.remove(custom_title_bar)
            custom_title_bar.cleanup()
            error_window.destroy()
        
        error_window.protocol("WM_DELETE_WINDOW", on_error_close)
            
        main_frame = ttk.Frame(error_window, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(expand=True, fill="both")
        
        message_label = ttk.Label(content_frame, text=message, wraplength=350, justify="center", font=("Arial", 10), foreground="red")
        message_label.pack(pady=(20, 30), expand=True)
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        ttk.Button(button_frame, text="OK", command=on_error_close).pack(anchor="center")

class SettingsManager:
    def __init__(self):

        self.settings_path = os.path.join(APPDATA_DIR, "settings.json")
        
        self.default_settings = {
            "source_lang": "eng",
            "target_lang": "vie",
            "active_translator": None,
            "dark_mode": False,
            "result_font": "Arial",
            "result_font_size": 12,
            "display_mode": "manual",
            "custom_font_color": "#db9aaa",
            "custom_stroke_color": "#000000", 
            "custom_bg_color": "#000000",
            "hotkey": "Ctrl+Q",
            "always_on_top": False,
            "run_at_startup": False,
            "sample_text": "Suki loves boba, naps, and head scratches UwU",
            "minimize_to_tray": False,
            "ocr_mode": "AI",
            "auto_copy_original_clipboard": False,
            "auto_copy_clipboard": False,
            "auto_check_updates": True,
            "run_as_admin": True,
            "last_update_check": 0
        }
        self.settings = self.default_settings.copy()
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_path):
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
                    for key in self.default_settings:
                        if key not in self.settings:
                            self.settings[key] = self.default_settings[key]
            return self.settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings):
        try:
            self.settings = settings
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get_setting(self, key):
        return self.settings.get(key, self.default_settings.get(key))
        
class TranslatorManager:
    def __init__(self):
        self.translators = {}
        self.active_translator = None
        self.load_translators()
        
    def load_translators(self):
        self.translators = {}
        for file in os.listdir(TRANSLATORS_DIR):
            if file.endswith(".js"):
                name = file[:-3]
                self.translators[name] = {
                    'path': os.path.join(TRANSLATORS_DIR, file),
                    'enabled': False
                }
    
    def set_active_translator(self, translator_name):
        if translator_name not in self.translators:
            return False
        for name in self.translators:
            self.translators[name]['enabled'] = (name == translator_name)
        self.active_translator = translator_name if self.translators[translator_name]['enabled'] else None
        return True
    
    def get_active_translator(self):
        if not self.active_translator:
            return None
        return self.translators[self.active_translator]
    
    def get_translator_list(self):
        return list(self.translators.keys())

class SettingsWindow:
    def __init__(self, app, translator_manager, spell_checker):
        self.app = app
        self.translator_manager = translator_manager
        self.window = tk.Toplevel(app.root)
        self.window.update_idletasks()
        dpi_scale = self.window.winfo_fpixels('1i') / 96
        self.window.geometry(f"{int(500 * dpi_scale * 96 / 100)}x{int(435 * dpi_scale * 96 / 100)}")
        self.window.resizable(True, True)
        
        self.custom_title_bar = CustomTitleBar(self.window, "Settings - Suki Translate", app_ref=app, show_maximize=True, use_system_titlebar=False)
        try:
            self.window.iconbitmap(ICON_DIR)
        except:
            pass
        
        if hasattr(app, 'custom_title_bars'):
            app.custom_title_bars.append(self.custom_title_bar)
        
        def on_settings_close():
            if hasattr(app, 'custom_title_bars') and self.custom_title_bar in app.custom_title_bars:
                app.custom_title_bars.remove(self.custom_title_bar)
            
            self.custom_title_bar.cleanup()
            
            if hasattr(app, 'on_settings_window_close'):
                app.on_settings_window_close()
            else:
                self.window.destroy()
        self.window._window_close_handler = on_settings_close

        self.notebook = ttk.Notebook(self.window)
        
        self.general_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.general_frame, text="General")
        self.setup_general_tab()
        
        self.prompt_var = tk.StringVar(value="")
        self.model_var = tk.StringVar(value="")
        self.temperature_var = tk.DoubleVar(value=0.5)
        self.max_tokens_var = tk.IntVar(value=2000)

        self.translator_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.translator_frame, text="Translators")
        self.setup_translator_tab()
        
        self.display_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.display_tab, text="Display")
        self.setup_display_tab()

        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="About")
        self.setup_about_tab()

        self.notebook.pack(expand=True, fill="both")

        active_trans = self.translator_manager.active_translator
        if active_trans:
            self.load_and_set_translator_params(active_trans)

    def setup_general_tab(self):
        hotkey_row = ttk.Frame(self.general_frame)
        hotkey_row.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        
        ttk.Label(hotkey_row, text="Hotkey:").grid(row=0, column=0, sticky="w")

        self.hotkey_display = ttk.Label(hotkey_row, text=self.app.settings.get("hotkey", "Ctrl+Q"))
        self.hotkey_display.grid(row=0, column=1, sticky="w", padx=(5, 20))

        self.record_button = ttk.Button(hotkey_row, text="🎙 Record", command=self.start_hotkey_recording)
        self.record_button.grid(row=0, column=2, sticky="e")

        self.recording = False
        self.current_keys = set()
        self.hotkey_var = tk.StringVar(value=self.app.settings.get("hotkey", "Ctrl+Q"))

        self.always_on_top_var = tk.BooleanVar(value=self.app.settings.get("always_on_top", False))
        always_on_top_chk = ttk.Checkbutton(
            self.general_frame,
            text="Always on top",
            variable=self.always_on_top_var,
            command=self.toggle_always_on_top
        )
        always_on_top_chk.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.run_at_startup_var = tk.BooleanVar(value=self.app.settings.get("run_at_startup", False))
        run_at_startup_chk = ttk.Checkbutton(
            self.general_frame,
            text="Run at startup",
            variable=self.run_at_startup_var,
            command=self.toggle_run_at_startup
        )
        run_at_startup_chk.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.run_as_admin_var = tk.BooleanVar(value=self.app.settings.get("run_as_admin", False))
        run_as_admin_chk = ttk.Checkbutton(
            self.general_frame,
            text="Run as administrator",
            variable=self.run_as_admin_var,
            command=self.toggle_run_as_admin
        )
        run_as_admin_chk.grid(row=3, column=0, sticky="w", padx=10, pady=5)


        self.minimize_to_tray_var = tk.BooleanVar(value=self.app.settings.get("minimize_to_tray", False))
        minimize_to_tray_chk = ttk.Checkbutton(
            self.general_frame,
            text="Minimize to system tray on close",
            variable=self.minimize_to_tray_var,
            command=self.update_general_settings
        )

        minimize_to_tray_chk.grid(row=4, column=0, sticky="w", padx=10, pady=5)

        self.auto_copy_original_clipboard_var = tk.BooleanVar(value=self.app.settings.get("auto_copy_original_clipboard", False))
        self.auto_copy_original_clipboard_chk = ttk.Checkbutton(
            self.general_frame,
            text="Auto save Original Text to clipboard (Tesseract)",
            variable=self.auto_copy_original_clipboard_var,
            command=self.update_general_settings
        )
        self.auto_copy_original_clipboard_chk.grid(row=5, column=0, sticky="w", padx=10, pady=5)

        self.auto_copy_clipboard_var = tk.BooleanVar(value=self.app.settings.get("auto_copy_clipboard", False))
        auto_copy_clipboard_chk = ttk.Checkbutton(
            self.general_frame,
            text="Auto save Result Text to clipboard",
            variable=self.auto_copy_clipboard_var,
            command=self.update_general_settings
        )
        auto_copy_clipboard_chk.grid(row=6, column=0, sticky="w", padx=10, pady=5)

        self.auto_check_updates_var = tk.BooleanVar(value=self.app.settings.get("auto_check_updates", True))
        auto_check_updates_chk = ttk.Checkbutton(
            self.general_frame,
            text="Automatically check for updates",
            variable=self.auto_check_updates_var,
            command=self.update_general_settings
        )
        auto_check_updates_chk.grid(row=7, column=0, sticky="w", padx=10, pady=5)
        
        update_button_frame = ttk.Frame(self.general_frame)
        update_button_frame.grid(row=8, column=0, sticky="w", padx=10, pady=5)
        
        ttk.Button(
            update_button_frame,
            text="Check for Updates Now",
            command=self.manual_update_check
        ).pack(side="left")
        
        version_label = ttk.Label(
            update_button_frame,
            text=f"Current version: {VERSION}",
            font=("Arial", 8)
        )
        version_label.pack(side="left", padx=(10, 0))

        self.hotkey_var.trace("w", lambda *args: self.update_general_settings())
        self.always_on_top_var.trace("w", lambda *args: self.update_general_settings())
        self.run_at_startup_var.trace("w", lambda *args: self.update_general_settings())
        self.minimize_to_tray_var.trace("w", lambda *args: self.update_general_settings())
        self.auto_copy_original_clipboard_var.trace("w", lambda *args: self.update_general_settings())
        self.auto_copy_clipboard_var.trace("w", lambda *args: self.update_general_settings())
        self.auto_check_updates_var.trace("w", lambda *args: self.update_general_settings())


        ocr_frame = ttk.Frame(self.general_frame)
        ocr_frame.grid(row=9, column=0, sticky="w", padx=10, pady=5)
        ttk.Label(ocr_frame, text="OCR Mode:").grid(row=0, column=0, sticky="w")
        
        self.ocr_mode_var = tk.StringVar(value=self.app.settings.get("ocr_mode", "tesseract"))
        ttk.Radiobutton(ocr_frame, text="Tesseract", variable=self.ocr_mode_var, value="Tesseract").grid(row=0, column=1, sticky="w", padx=5)
        ttk.Radiobutton(ocr_frame, text="AI Recognition", variable=self.ocr_mode_var, value="AI").grid(row=0, column=2, sticky="w", padx=5)
        
        self.ocr_mode_var.trace("w", lambda *args: self.update_ocr_mode_dependent_settings())
        
        self.update_ocr_mode_dependent_settings()
        
    def manual_update_check(self):
        threading.Thread(target=lambda: self.app.update_checker.check_for_updates(show_no_update_message=True), daemon=True).start()

    def start_hotkey_recording(self):
        if not self.recording:
            self.recording = True
            self.current_keys = set()
            self.hotkey_display.config(text="Press keys now...")
            self.record_button.config(text="Recording...")
            
            self.window.bind("<KeyPress>", self.on_key_press)
            self.window.bind("<KeyRelease>", self.on_key_release)
            self.window.focus_set()
        else:
            self.stop_hotkey_recording()

    def stop_hotkey_recording(self):
        self.recording = False
        self.window.unbind("<KeyPress>")
        self.window.unbind("<KeyRelease>")
        self.record_button.config(text="Record Hotkey")
        
        if self.current_keys:
            formatted_hotkey = "+".join(sorted(self.current_keys, key=lambda x: (len(x), x)))
            self.hotkey_display.config(text=formatted_hotkey)
            self.hotkey_var.set(formatted_hotkey)
            self.update_general_settings()
            self.app.bind_global_hotkey()
        else:
            self.hotkey_display.config(text=self.hotkey_var.get())

    def on_key_press(self, event):
        if not self.recording:
            return
            
        key = self.get_key_name(event)
        if key:
            self.current_keys.add(key)
            
            self.hotkey_display.config(text="+".join(sorted(self.current_keys, key=lambda x: (len(x), x))))

    def on_key_release(self, event):
        if not self.recording:
            return
            
        if len(self.current_keys) > 0:
            self.stop_hotkey_recording()

    def get_key_name(self, event):
        key = event.keysym
        if key in ("Control_L", "Control_R"):
            return "Ctrl"
        elif key in ("Shift_L", "Shift_R"):
            return "Shift"
        elif key in ("Alt_L", "Alt_R"):
            return "Alt"
        elif key in ("Super_L", "Super_R"):
            return "Win"
        else:
            return key.capitalize()

    def toggle_always_on_top(self):
        new_value = self.always_on_top_var.get()
        self.app.root.attributes('-topmost', new_value)
        self.update_general_settings()

    def toggle_run_at_startup(self):
        new_value = self.run_at_startup_var.get()
        if set_startup(new_value):
            self.update_general_settings()
        else:
            self.run_at_startup_var.set(not new_value)
            messagebox.showerror("Error", "Could not modify startup settings")

    def toggle_run_as_admin(self):
        new_value = self.run_as_admin_var.get()
        new_settings = self.app.settings.copy()
        new_settings["run_as_admin"] = new_value
        self.app.settings_manager.save_settings(new_settings)
        self.app.settings = new_settings

        if new_value:
            messagebox.showinfo("Run as Admin", "The app will now restart with administrator rights.")
            self.restart_as_admin()

    def restart_as_admin(self):
        import sys, ctypes, subprocess
        if not ctypes.windll.shell32.IsUserAnAdmin():
            params = " ".join(sys.argv)
            try:
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
                os._exit(0)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to restart as admin: {e}")


    def update_ocr_mode_dependent_settings(self):
        self.update_general_settings()
        
        ocr_mode = self.ocr_mode_var.get()
        if ocr_mode == "Tesseract":
            self.auto_copy_original_clipboard_chk.config(state="normal")
        else:
            self.auto_copy_original_clipboard_chk.config(state="disabled")
            self.auto_copy_original_clipboard_var.set(False)

    def update_general_settings(self):
        new_settings = self.app.settings.copy()
        new_settings["hotkey"] = self.hotkey_var.get()
        new_settings["always_on_top"] = self.always_on_top_var.get()
        new_settings["run_at_startup"] = self.run_at_startup_var.get()
        new_settings["minimize_to_tray"] = self.minimize_to_tray_var.get()
        new_settings["ocr_mode"] = self.ocr_mode_var.get()
        new_settings["auto_copy_original_clipboard"] = self.auto_copy_original_clipboard_var.get()
        new_settings["auto_copy_clipboard"] = self.auto_copy_clipboard_var.get()
        new_settings["auto_check_updates"] = self.auto_check_updates_var.get()
        
        self.app.settings_manager.save_settings(new_settings)
        self.app.settings = new_settings

        if hasattr(self.app, 'root'):
            self.app.root.attributes('-topmost', new_settings["always_on_top"])


    def update_settings_immediately(self):
        new_settings = self.app.settings.copy()
        new_settings["dark_mode"] = self.dark_mode_var.get()
        new_settings["result_font"] = self.font_var.get()
        new_settings["result_font_size"] = self.font_size_var.get()
        new_settings["display_mode"] = self.display_mode.get()
        new_settings["custom_font_color"] = self.font_color.get()
        new_settings["custom_stroke_color"] = self.stroke_color.get()
        new_settings["custom_bg_color"] = self.bg_color.get()
        new_settings["sample_text"] = self.sample_text.get()

        self.app.settings_manager.save_settings(new_settings)
        self.app.settings = new_settings
        self.app.apply_theme()

    def choose_font_color(self):
        color = colorchooser.askcolor(color=self.font_color.get())[1]
        if color:
            self.font_color.set(color)
            self.font_color_box.config(bg=color)
            self.update_settings_immediately()

    def choose_stroke_color(self):
        color = colorchooser.askcolor(color=self.stroke_color.get())[1]
        if color:
            self.stroke_color.set(color)
            self.stroke_color_box.config(bg=color)
            self.update_settings_immediately()


    def choose_bg_color(self):
        color = colorchooser.askcolor(color=self.bg_color.get())[1]
        if color:
            self.bg_color.set(color)
            self.bg_color_box.config(bg=color)
            self.update_settings_immediately()

    def update_display_mode(self):
        if self.display_mode.get() == "manual":
            self.manual_frame.pack(anchor="w", fill="x", padx=5, pady=5)
        else:
            self.manual_frame.forget()
    
    def toggle_dark_mode_immediate(self):
        new_value = self.dark_mode_var.get()
        self.app.settings["dark_mode"] = new_value
        self.app.apply_theme()
        if hasattr(self.app, 'edit_window') and self.app.edit_window and self.app.edit_window.winfo_exists():
            self.app.update_edit_window_theme()
        
        self.apply_translator_canvas_theme()

    def open_translators_folder(self):
        try:
            os.startfile(TRANSLATORS_DIR)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open translators folder: {e}")

    def load_params_from_translator_file(self, translator_name):
        defaults = {"prompt": "", "model": "", "temperature": 0.5, "max_tokens": 2000}
        if not translator_name:
            return defaults

        path = os.path.join(TRANSLATORS_DIR, f"{translator_name}.js")
        if not os.path.exists(path):
            print(f"Translator file not found for {translator_name}, using defaults.")
            return defaults

        params = defaults.copy()
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            prompt_match = re.search(r"const\s+PROMPT\s*=\s*['\"](.*?)['\"]\s*;", content, re.MULTILINE)
            if prompt_match:
                params["prompt"] = prompt_match.group(1)

            model_match = re.search(r"const\s+MODEL\s*=\s*['\"](.*?)['\"]\s*;", content, re.MULTILINE)
            if model_match:
                params["model"] = model_match.group(1)

            temp_match = re.search(r"const\s+TEMPERATURE\s*=\s*([\d.]+)\s*;", content, re.MULTILINE)
            if temp_match:
                try:
                    params["temperature"] = float(temp_match.group(1))
                except ValueError:
                    print(f"Warning: Could not parse TEMPERATURE from {translator_name}.js")

            max_tokens_match = re.search(r"const\s+MAX_TOKENS\s*=\s*(\d+)\s*;", content, re.MULTILINE)
            if max_tokens_match:
                try:
                    params["max_tokens"] = int(max_tokens_match.group(1))
                except ValueError:
                    print(f"Warning: Could not parse MAX_TOKENS from {translator_name}.js")
        except Exception as e:
            print(f"Error loading params from {translator_name}.js: {e}")
            return defaults 
        return params

    def save_prompt_temp_tokens_to_file(self, translator_name, prompt, temperature, max_tokens):
        path = os.path.join(TRANSLATORS_DIR, f"{translator_name}.js")
        if not os.path.exists(path):
            print(f"Cannot save params: Translator file not found for {translator_name}")
            return

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated_lines = []
        prompt_found, temperature_found, max_tokens_found = False, False, False

        for line in lines:
            if re.match(r"^\s*const\s+PROMPT\s*=", line):
                updated_lines.append(f"const PROMPT = '{prompt}';\n")
                prompt_found = True
            elif re.match(r"^\s*const\s+TEMPERATURE\s*=", line):
                updated_lines.append(f"const TEMPERATURE = {temperature};\n")
                temperature_found = True
            elif re.match(r"^\s*const\s+MAX_TOKENS\s*=", line):
                updated_lines.append(f"const MAX_TOKENS = {max_tokens};\n")
                max_tokens_found = True
            else:
                updated_lines.append(line)
        
        insert_pos = 0
        for i, line_content in enumerate(lines):
            stripped_line = line_content.strip()
            if not stripped_line.startswith("//") and stripped_line != "":
                insert_pos = i
                break
        else:
            insert_pos = len(updated_lines)


        if not max_tokens_found:
            updated_lines.insert(insert_pos, f"const MAX_TOKENS = {max_tokens};\n")
        if not temperature_found:
            updated_lines.insert(insert_pos, f"const TEMPERATURE = {temperature};\n")
        if not prompt_found:
            updated_lines.insert(insert_pos, f"const PROMPT = '{prompt}';\n")

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

    def load_and_set_translator_params(self, translator_name):
        params = self.load_params_from_translator_file(translator_name)
        self.prompt_var.set(params.get("prompt", ""))
        self.model_var.set(params.get("model", ""))
        self.temperature_var.set(params.get("temperature", 0.5))
        self.max_tokens_var.set(params.get("max_tokens", 2000))

    def reset_translator_params_ui(self):
        self.prompt_var.set("")
        self.model_var.set("")
        self.temperature_var.set(0.5)
        self.max_tokens_var.set(2000)

    def setup_translator_tab(self):
        list_frame = ttk.Frame(self.translator_frame)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        update_btn = ttk.Button(list_frame, text="🔄 Update translators from GitHub", command=self.update_translators_from_github)
        update_btn.grid(row=0, column=0, columnspan=2, sticky="w", pady=5)

        open_folder_btn = ttk.Button(list_frame, text="📂 Open folder", command=self.open_translators_folder)
        open_folder_btn.grid(row=0, column=2, sticky="e", pady=5, padx=(0, 100))

        save_btn = ttk.Button(list_frame, text="💾 Save", command=self.save_active_translator_specific_params)
        save_btn.grid(row=0, column=2, sticky="e", pady=5, padx=(0, 10))

        ttk.Label(list_frame, text="Prompt:").grid(row=1, column=0, sticky="w", pady=5)
        prompt_entry = ttk.Entry(list_frame, textvariable=self.prompt_var, width=50)
        prompt_entry.grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 10))

        ttk.Label(list_frame, text="Model:").grid(row=2, column=0, sticky="w", pady=5)
        self.model_var = tk.StringVar(value="")
        model_entry = ttk.Entry(list_frame, textvariable=self.model_var, width=50)
        model_entry.grid(row=2, column=1, columnspan=2, sticky="ew", padx=(0, 10))

        ttk.Label(list_frame, text="Temperature:").grid(row=3, column=0, sticky="w", pady=5)
        temperature_entry = ttk.Entry(list_frame, textvariable=self.temperature_var, width=10)
        temperature_entry.grid(row=3, column=1, sticky="w", padx=(0, 5))

        ttk.Label(list_frame, text="Max Tokens:").grid(row=4, column=0, sticky="w", pady=5)
        max_tokens_entry = ttk.Entry(list_frame, textvariable=self.max_tokens_var, width=10)
        max_tokens_entry.grid(row=4, column=1, sticky="w", padx=(0, 5))

        ttk.Label(list_frame, text="Translator").grid(row=5, column=0, sticky="w", pady=5)
        ttk.Label(list_frame, text="API Key").grid(row=5, column=2, sticky="w", pady=5)

        scrollable_frame = ttk.Frame(list_frame)
        scrollable_frame.grid(row=6, column=0, columnspan=3, sticky="nsew", pady=5)
        
        list_frame.rowconfigure(6, weight=1)
        list_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(2, weight=1)

        translators_count = len(self.translator_manager.get_translator_list())
        max_visible_rows = 8
        row_height = 25
        canvas_height = min(translators_count * row_height, max_visible_rows * row_height)
        
        self.translator_canvas = tk.Canvas(scrollable_frame, highlightthickness=0, height=canvas_height)
        self.translator_scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=self.translator_canvas.yview)
        self.scrollable_inner_frame = ttk.Frame(self.translator_canvas)
        
        self.scrollable_inner_frame.bind(
            "<Configure>",
            lambda e: self.translator_canvas.configure(scrollregion=self.translator_canvas.bbox("all"))
        )
        
        self.canvas_frame_id = self.translator_canvas.create_window((0, 0), window=self.scrollable_inner_frame, anchor="nw")
        self.translator_canvas.configure(yscrollcommand=self.translator_scrollbar.set)
        
        self.translator_canvas.pack(side="left", fill="both", expand=True)
        self.translator_scrollbar.pack(side="right", fill="y")
        
        def configure_canvas_width(event):
            canvas_width = event.width
            self.translator_canvas.itemconfig(self.canvas_frame_id, width=canvas_width)
        scrollable_frame.bind("<Configure>", configure_canvas_width)
        
        def on_mousewheel(event):
            self.translator_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            self.translator_canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_mousewheel(event):
            self.translator_canvas.unbind_all("<MouseWheel>")
        
        self.translator_canvas.bind("<Enter>", bind_mousewheel)
        self.translator_canvas.bind("<Leave>", unbind_mousewheel)
        
        self.scrollable_inner_frame.columnconfigure(1, weight=1)
        self.scrollable_inner_frame.columnconfigure(2, weight=1)

        self.translator_vars = {}
        self.api_key_entries = {}
        self.model_entries = {}
        
        translators = self.translator_manager.get_translator_list()
        active_trans_from_settings = self.app.settings.get("active_translator")
        
        for row_idx, t_name in enumerate(translators, start=0):
            var = tk.BooleanVar(value=(t_name == active_trans_from_settings))
            chk = ttk.Checkbutton(
                self.scrollable_inner_frame,
                text=f"{t_name}.js",
                variable=var,
                command=lambda n=t_name, v=var: self.on_translator_check(n, v)
            )
            chk.grid(row=row_idx, column=0, sticky="w", padx=(5, 10), pady=2)
            
            api_key_var = tk.StringVar()
            api_key_entry = ttk.Entry(
                self.scrollable_inner_frame,
                textvariable=api_key_var,
                show="•",
                width=20
            )
            api_key_entry.grid(row=row_idx, column=1, columnspan=2, sticky="ew", padx=(0, 10), pady=2)
            
            key_path = os.path.join(TRANSLATORS_DIR, f"{t_name}.js")
            if os.path.exists(key_path):
                with open(key_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    api_key_match = re.search(r"const\s+API_KEY\s*=\s*['\"](.*?)['\"]\s*;", file_content)
                    if api_key_match:
                        api_key = api_key_match.group(1)
                        api_key_var.set(api_key)
                        if api_key == "YOUR_API_KEY_HERE":
                            api_key_entry.config(show="")
                    
                    model_match = re.search(r"const\s+MODEL\s*=\s*['\"](.*?)['\"]\s*;", file_content)
                    if model_match and t_name == active_trans_from_settings:
                        self.model_var.set(model_match.group(1))
                     
            def update_api_key_visibility_factory(entry_widget, key_string_var):
                def update_visibility(*args):
                    if key_string_var.get() == "YOUR_API_KEY_HERE":
                        entry_widget.config(show="")
                    else:
                        entry_widget.config(show="•")
                return update_visibility
            
            api_key_var.trace_add("write", update_api_key_visibility_factory(api_key_entry, api_key_var))
            
            self.translator_vars[t_name] = var
            self.api_key_entries[t_name] = api_key_var
            self.model_entries[t_name] = tk.StringVar(value="")

        if active_trans_from_settings:
            if active_trans_from_settings in self.translator_vars:
                self.translator_vars[active_trans_from_settings].set(True)
            self.load_and_set_translator_params(active_trans_from_settings)
        else:
            self.reset_translator_params_ui()
        
        self.apply_translator_canvas_theme()

    def apply_translator_canvas_theme(self):

        if hasattr(self, 'translator_canvas'):
            dark_mode = self.app.settings.get("dark_mode", False)
            
            style = ttk.Style()
            
            if dark_mode:
                bg_color = "#2e2e2e"
                scrollbar_bg = "#3c3c3c"
                scrollbar_trough = "#2e2e2e"
                scrollbar_arrow = "#ffffff"
                
                self.translator_canvas.configure(bg=bg_color)
                
                style.configure(
                    "Translator.Vertical.TScrollbar",
                    background=scrollbar_bg,
                    troughcolor=scrollbar_trough,
                    arrowcolor=scrollbar_arrow,
                    bordercolor=scrollbar_bg,
                    lightcolor=scrollbar_bg,
                    darkcolor=scrollbar_bg
                )
                style.map(
                    "Translator.Vertical.TScrollbar",
                    background=[("active", "#444444"), ("pressed", "#555555")]
                )
                
                if hasattr(self, 'translator_scrollbar'):
                    self.translator_scrollbar.configure(style="Translator.Vertical.TScrollbar")
            else:
                bg_color = "#ffffff"
                self.translator_canvas.configure(bg=bg_color)
                
                if hasattr(self, 'translator_scrollbar'):
                    self.translator_scrollbar.configure(style="Vertical.TScrollbar")

    def save_active_translator_specific_params(self):
        active_translator = self.translator_manager.active_translator
        if not active_translator:
            return

        prompt = self.prompt_var.get()
        model = self.model_var.get()
        try:
            temperature = float(self.temperature_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Temperature must be a valid number.")
            params = self.load_params_from_translator_file(active_translator)
            self.temperature_var.set(params.get("temperature", 0.5))
            return 
        try:
            max_tokens = int(self.max_tokens_var.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Max Tokens must be a valid integer.")
            params = self.load_params_from_translator_file(active_translator)
            self.max_tokens_var.set(params.get("max_tokens", 2000))
            return


        api_key = ""
        if active_translator in self.api_key_entries:
            api_key = self.api_key_entries[active_translator].get()

        self.save_translator_params_to_file(
            active_translator,
            prompt,
            model,
            temperature,
            max_tokens,
            api_key
        )

        for t_name, api_key_var in self.api_key_entries.items():
            if t_name == active_translator:
                continue

            api_key_val = api_key_var.get().strip()
            if api_key_val:
                path = os.path.join(TRANSLATORS_DIR, f"{t_name}.js")
                if not os.path.exists(path):
                    continue

                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                updated_lines = []
                key_found = False
                for line in lines:
                    if re.match(r"^\s*const\s+API_KEY\s*=", line):
                        updated_lines.append(f"const API_KEY = '{api_key_val}';\n")
                        key_found = True
                    else:
                        updated_lines.append(line)

                if not key_found:
                    updated_lines.append(f"const API_KEY = '{api_key_val}';\n")

                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(updated_lines)

    def save_translator_params_to_file(self, translator_name, prompt, model, temperature=0.5, max_tokens=2000, api_key=""):
        path = os.path.join(TRANSLATORS_DIR, f"{translator_name}.js")
        if not os.path.exists(path):
            print(f"Cannot save params: Translator file not found for {translator_name}")
            return

        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated_lines = []
        key_found, prompt_found, model_found, temperature_found, max_tokens_found = False, False, False, False, False

        for line in lines:
            if re.match(r"^\s*const\s+API_KEY\s*=", line):
                updated_lines.append(f"const API_KEY = '{api_key}';\n")
                key_found = True
            elif re.match(r"^\s*const\s+PROMPT\s*=", line):
                updated_lines.append(f"const PROMPT = '{prompt}';\n")
                prompt_found = True
            elif re.match(r"^\s*const\s+MODEL\s*=", line):
                updated_lines.append(f"const MODEL = '{model}';\n")
                model_found = True
            elif re.match(r"^\s*const\s+TEMPERATURE\s*=", line):
                updated_lines.append(f"const TEMPERATURE = {temperature};\n")
                temperature_found = True
            elif re.match(r"^\s*const\s+MAX_TOKENS\s*=", line):
                updated_lines.append(f"const MAX_TOKENS = {max_tokens};\n")
                max_tokens_found = True
            else:
                updated_lines.append(line)

        if not key_found:
            updated_lines.append(f"const API_KEY = '{api_key}';\n")
        if not prompt_found:
            updated_lines.append(f"const PROMPT = '{prompt}';\n")
        if not model_found:
            updated_lines.append(f"const MODEL = '{model}';\n")
        if not temperature_found:
            updated_lines.append(f"const TEMPERATURE = {temperature};\n")
        if not max_tokens_found:
            updated_lines.append(f"const MAX_TOKENS = {max_tokens};\n")

        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)



    def update_translator_files(self):
        try:
            repo_url = "https://raw.githubusercontent.com/Suki8898/SukiTranslate/main/translators/"
            response = requests.get("https://api.github.com/repos/Suki8898/SukiTranslate/contents/translators")
            response.raise_for_status()
            files = response.json()
            
            for file_info in files:
                if not file_info["name"].endswith(".js"):
                    continue

                filename = file_info["name"]
                raw_url = file_info["download_url"]
                local_path = os.path.join(TRANSLATORS_DIR, filename)

                response = requests.get(raw_url)
                response.raise_for_status()
                new_code = response.text.replace('\r\n', '\n')

                with open(local_path, "w", encoding="utf-8", newline='\n') as f:
                    f.write(new_code)

                print(f"✅ Updated {filename}")

            return True
        except Exception as e:
            self.show_custom_error_dialog("Update Failed", f"Error downloading translators from GitHub:\n{e}")
            return False


    def setup_display_tab(self):
        self.dark_mode_var = tk.BooleanVar(value=self.app.settings.get("dark_mode", False))
        dark_mode_chk = ttk.Checkbutton(
            self.display_tab,
            text="Enable Dark Mode",
            variable=self.dark_mode_var,
            command=self.toggle_dark_mode_immediate
        )
        dark_mode_chk.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        font_frame = ttk.Frame(self.display_tab)
        font_frame.grid(row=1, column=0, sticky="ew", padx=(10, 10), pady=10)
        self.display_tab.columnconfigure(0, weight=1)  

        ttk.Label(font_frame, text="Font Name", width=20).grid(row=0, column=0, sticky="e")
        self.font_var = tk.StringVar(value=self.app.settings.get("result_font", "Arial"))
        font_options = sorted(font.families())
        font_combo = ttk.Combobox(font_frame, textvariable=self.font_var, values=font_options, width=20)
        font_combo.grid(row=0, column=1, sticky="ew")
        font_frame.columnconfigure(1, weight=1)

        size_frame = ttk.Frame(self.display_tab)
        size_frame.grid(row=2, column=0, sticky="ew", padx=(10, 10), pady=10)

        ttk.Label(size_frame, text="Font Size", width=20).grid(row=0, column=0, sticky="e")
        self.font_size_var = tk.IntVar(value=self.app.settings.get("result_font_size", 12))
        self.font_size_spinbox = ttk.Spinbox(size_frame, from_=8, to=72, textvariable=self.font_size_var, width=5)
        self.font_size_spinbox.grid(row=0, column=1, sticky="w")
        size_frame.columnconfigure(1, weight=1)

        font_color_frame = ttk.Frame(self.display_tab)
        font_color_frame.grid(row=3, column=0, sticky="w", padx=(10, 10), pady=10)

        ttk.Label(font_color_frame, text="Font Color", width=20).grid(row=0, column=0, sticky="e")
        self.font_color = tk.StringVar(value=self.app.settings.get("custom_font_color", "#000000")) 
        self.font_color_box = tk.Canvas(font_color_frame, width=30, height=15, bg=self.font_color.get(),
                                        highlightthickness=1, highlightbackground="black", cursor="hand2")
        self.font_color_box.grid(row=0, column=1, sticky="w")
        self.font_color_box.bind("<Button-1>", lambda e: self.choose_font_color())
        font_color_frame.columnconfigure(1, weight=1)


        stroke_color_frame = ttk.Frame(self.display_tab)
        stroke_color_frame.grid(row=3, column=1, sticky="w", padx=(10, 10), pady=10)

        ttk.Label(stroke_color_frame, text="Stroke Color:", width=20).grid(row=0, column=0, sticky="w")
        self.stroke_color = tk.StringVar(value=self.app.settings.get("custom_stroke_color", "#000000"))
        self.stroke_color_box = tk.Canvas(stroke_color_frame, width=30, height=15, bg=self.stroke_color.get(),
                                        highlightthickness=1, highlightbackground="black", cursor="hand2")
        self.stroke_color_box.grid(row=0, column=1, sticky="w")
        self.stroke_color_box.bind("<Button-1>", lambda e: self.choose_stroke_color())
        stroke_color_frame.columnconfigure(1, weight=1)


        bg_color_frame = ttk.Frame(self.display_tab)

        ttk.Label(bg_color_frame, text="Background Color", width=20).grid(row=0, column=0, sticky="e")
        self.bg_color = tk.StringVar(value=self.app.settings.get("custom_bg_color", "#ffffff"))
        self.bg_color_box = tk.Canvas(bg_color_frame, width=30, height=15, bg=self.bg_color.get(),
                                        highlightthickness=1, highlightbackground="black", cursor="hand2")
        self.bg_color_box.grid(row=0, column=1, sticky="w")
        self.bg_color_box.bind("<Button-1>", lambda e: self.choose_bg_color())
        bg_color_frame.columnconfigure(1, weight=1)

        ttk.Label(self.display_tab, text="Background Color Mode:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.display_mode = tk.StringVar(value=self.app.settings.get("display_mode", "manual"))

        empty_row4_frame = ttk.Frame(self.display_tab)

        def update_display_mode():
            if self.display_mode.get() == "manual":
                bg_color_frame.grid(row=4, column=0, sticky="w", padx=(10, 10), pady=10)
            else:
                bg_color_frame.grid_forget()
                empty_row4_frame.grid(row=4, column=0, pady=18)
            self.update_settings_immediately()

        modes = [("Manual", "manual"), ("Auto", "auto"), ("Blur", "blur")]
        for i, (text, value) in enumerate(modes):
            radio = ttk.Radiobutton(
                self.display_tab, text=text,
                variable=self.display_mode, value=value,
                command=update_display_mode
            )
            radio.grid(row=6 + i, column=0, sticky="w", padx=10, pady=2)

        self.sample_text = tk.StringVar(value=self.app.settings.get("sample_text", "Suki loves boba, naps, and head scratches UwU"))

        self.sample_entry = tk.Entry(
            self.display_tab, 
            textvariable=self.sample_text, 
            font=(self.font_var.get(), 
            self.font_size_var.get()), 
            fg=self.font_color.get(), 
            bg=self.bg_color.get(), 
            justify="center"
            )
        self.sample_entry.grid(row=6 + len(modes), column=0, columnspan=2, sticky="ew", padx=10, pady=(20, 10))

        def update_sample_text(*args):
            self.sample_entry.config(
                font=(self.font_var.get(), self.font_size_var.get()),
                fg=self.font_color.get(),
                bg=self.bg_color.get()
            )

        self.font_var.trace_add("write", update_sample_text)
        self.font_size_var.trace_add("write", update_sample_text)
        self.font_color.trace_add("write", update_sample_text)
        self.stroke_color.trace_add("write", update_sample_text)
        self.bg_color.trace_add("write", update_sample_text)

        self.dark_mode_var.trace("w", lambda *args: self.update_settings_immediately())
        self.font_var.trace("w", lambda *args: self.update_settings_immediately())
        self.font_size_var.trace("w", lambda *args: self.update_settings_immediately())
        self.display_mode.trace("w", lambda *args: self.update_settings_immediately())
        self.font_color.trace("w", lambda *args: self.update_settings_immediately())
        self.stroke_color.trace("w", lambda *args: self.update_settings_immediately())
        self.bg_color.trace("w", lambda *args: self.update_settings_immediately())
        self.sample_text.trace("w", lambda *args: self.update_settings_immediately())

        update_display_mode()

    def validate_fontsize(self, new_value):
        if new_value == "":
            return True
        try:
            value = int(new_value)
            return 8 <= value <= 72
        except ValueError:
            return False

    def on_translator_check(self, translator_name, var):
        current_active = self.translator_manager.active_translator
        new_active_translator = None

        if var.get():
            self.translator_manager.set_active_translator(translator_name)
            new_active_translator = translator_name
            for other_name, other_var in self.translator_vars.items():
                if other_name != translator_name:
                    other_var.set(False)
            
            self.load_and_set_translator_params(translator_name)
            
        else:
            if current_active == translator_name:
                self.translator_manager.set_active_translator(None)
                new_active_translator = None
                self.reset_translator_params_ui()

        self.app.settings["active_translator"] = self.translator_manager.active_translator
        self.app.settings_manager.save_settings(self.app.settings)

    def update_translators_from_github(self):
        if self.update_translator_files():
            self.show_custom_info_dialog("Done", "Translators updated successfully!")
            self.translator_manager.load_translators()
            self.translator_frame.destroy()
            self.translator_frame = ttk.Frame(self.notebook)
            self.notebook.insert(1, self.translator_frame, text="Translators")
            self.setup_translator_tab()

    def setup_about_tab(self):
        about_frame = ttk.Frame(self.about_frame)
        about_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ttk.Label(about_frame, text=APP_NAME, font=("Arial", 16, "bold")).pack(anchor="center", pady=5)

        description = "OCR Tesseract character recognition tool and AI-powered translation"
        ttk.Label(about_frame, text=description, wraplength=400, justify="center").pack(anchor="center", pady=10)

        ttk.Label(about_frame, text=f"Version: {VERSION}").pack(anchor="center", pady=5)

        author_frame = ttk.Frame(about_frame)
        author_frame.pack(anchor="center", pady=5)
        ttk.Label(author_frame, text="Author: ").pack(side="left")
        author_link = ttk.Label(author_frame, text="Suki", foreground="#db9aaa", cursor="hand2")
        author_link.pack(side="left")
        author_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Suki8898"))

        support_frame = ttk.Frame(about_frame)
        support_frame.pack(anchor="center", pady=5)
        ttk.Label(support_frame, text="Support: ").pack(side="left")
        support_link = ttk.Label(support_frame, text="Buymeacoffee", foreground="#db9aaa", cursor="hand2")
        support_link.pack(side="left")
        support_link.bind("<Button-1>", lambda e: webbrowser.open("https://buymeacoffee.com/suki8898"))

        license_frame = ttk.Frame(about_frame)
        license_frame.pack(anchor="center", pady=5)
        ttk.Label(license_frame, text="License: ").pack(side="left")
        license_link = ttk.Label(license_frame, text="MIT", foreground="#db9aaa", cursor="hand2")
        license_link.pack(side="left")
        license_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Suki8898/SukiTranslate/blob/main/LICENSE"))

        wiki_frame = ttk.Frame(about_frame)
        wiki_frame.pack(anchor="center", pady=5)

        wiki_link = ttk.Label(wiki_frame, text="Wiki", foreground="#db9aaa", cursor="hand2")
        wiki_link.pack(side="left")
        wiki_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Suki8898/SukiTranslate/wiki"))

        issue_frame = ttk.Frame(about_frame)
        issue_frame.pack(anchor="center", pady=5)

        issue_link = ttk.Label(issue_frame, text="Report issue", foreground="#db9aaa", cursor="hand2")
        issue_link.pack(side="left")
        issue_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/Suki8898/SukiTranslate/issues"))

class SukiTranslateApp:
    def __init__(self, root):
        self.root = root
        
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        sys.stdout = GlobalTextRedirector()
        sys.stderr = GlobalTextRedirector()

        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        self.spell_checker = SpellChecker()
        self.apply_theme()
        
        self.custom_title_bar = CustomTitleBar(self.root, APP_NAME, app_ref=self, show_maximize=False, allow_resize=False)
        
        self.custom_title_bars = [self.custom_title_bar]

        self.translator_manager = TranslatorManager()
        
        self.x1 = self.y1 = self.x2 = self.y2 = None
        self.full_screen_img = None
        self.rect = None
        
        self.console_visible = False
        self.console_window = None
        self.console_log_text_widget = None
        self.tray_icon = None

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        self.top_frame = ttk.Frame(self.main_frame)
        self.top_frame.pack(fill="x", pady=5, padx=10)

        self.bottom_frame = ttk.Frame(self.main_frame)
        self.bottom_frame.pack(fill="x", pady=5, padx=10)
        
        self.left_frame = ttk.Frame(self.top_frame)
        self.left_frame.pack(side="left", fill="y")
        
        style = ttk.Style()


        self.capture_button = ttk.Button(self.left_frame, text="📸", command=self.start_capture, width=3, style='Custom.TButton')
        self.capture_button.pack(side="left", padx=5 , pady=(10, 0))
        
        style = ttk.Style()
        style.configure('Custom.TButton', font=("Arial", 15), width=3, height=1, padding=18)

        self.middle_frame = ttk.Frame(self.top_frame)
        self.middle_frame.pack(side="left", fill="both", expand=True)
        
        self.source_lang_label = ttk.Label(self.middle_frame, text="Source Language:")
        self.source_lang_label.pack(anchor="center")

        sorted_languages = sorted(LANGUAGE_MAPPING.keys())
        self.source_lang_combo = ttk.Combobox(self.middle_frame, values=sorted_languages, width=25)  
        self.source_lang_combo.pack(anchor="center")

        default_lang = self.settings.get("source_lang", "eng")
        default_display = next((name for name, data in LANGUAGE_MAPPING.items() 
                            if data["tess_code"] == default_lang), "English")
        self.source_lang_combo.set(default_display)

        self.target_lang_label = ttk.Label(self.middle_frame, text="Target Language:")
        self.target_lang_label.pack(anchor="center")

        common_targets = [
            "Afrikaans", "Amharic", "Arabic", "Assamese", "Azerbaijani", "Belarusian",
            "Bengali", "Tibetan", "Bosnian", "Bulgarian", "Catalan", "Cebuano",
            "Czech", "Chinese (Simplified)", "Chinese (Traditional)", "Cherokee",
            "Welsh", "Danish", "German", "Dzongkha", "Greek", "English",
            "Esperanto", "Estonian", "Basque", "Persian", "Finnish", "French",
            "Irish", "Galician", "Gujarati", "Haitian Creole", "Hebrew", "Hindi",
            "Croatian", "Hungarian", "Armenian", "Indonesian", "Icelandic", "Italian",
            "Javanese", "Japanese", "Kannada", "Georgian", "Kazakh", "Khmer",
            "Korean", "Kurdish", "Kyrgyz", "Lao", "Latin", "Latvian",
            "Lithuanian", "Luxembourgish", "Macedonian", "Malayalam", "Marathi",
            "Malay", "Burmese", "Nepali", "Dutch", "Norwegian", "Occitan",
            "Oriya", "Punjabi", "Polish", "Portuguese", "Romanian", "Russian",
            "Sanskrit", "Sinhala", "Slovak", "Slovenian", "Spanish", "Albanian",
            "Serbian", "Swedish", "Swahili", "Tamil", "Telugu", "Tajik",
            "Tagalog", "Thai", "Turkish", "Uyghur", "Ukrainian", "Urdu",
            "Uzbek", "Vietnamese", "Yiddish", "Yoruba", "UwU",
        ]
        self.target_lang_combo = ttk.Combobox(self.middle_frame, values=common_targets, width=25)
        self.target_lang_combo.pack(anchor="center")

        default_target = self.settings.get("target_lang", "vie")
        default_target_display = next((name for name, data in LANGUAGE_MAPPING.items() 
                                    if data["tess_code"] == default_target), "Vietnamese")
        self.target_lang_combo.set(default_target_display)
        
        self.right_frame = ttk.Frame(self.top_frame)
        self.right_frame.pack(side="right", fill="y")
        
        self.settings_button = ttk.Button(self.right_frame, text="⚙", width=3, command=self.open_settings)
        
        self.settings_button.pack(side="top", padx=5, pady=(12, 5))
        
        self.log_button = ttk.Button(self.right_frame, text="📜", width=3, command=self.toggle_console)
        self.log_button.pack(side="top", padx=5, pady=(5, 0))

        self.canvas = tk.Canvas(self.main_frame, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        self.apply_theme()
        
        if self.settings["active_translator"]:
            self.translator_manager.set_active_translator(self.settings["active_translator"])

        self.source_lang_combo.bind("<<ComboboxSelected>>", self.update_language_setting)
        self.target_lang_combo.bind("<<ComboboxSelected>>", self.update_language_setting)

        self.hotkey_thread = None
        self.hotkey_running = False
        self.bind_global_hotkey()

        self.last_extracted_text = None 
        self.captured_image = None
        self.current_overlay = None
        
        self.update_checker = UpdateChecker(self)
        
        self.system_tray_icon()
        
    def system_tray_icon(self):
        if self.tray_icon and hasattr(self, '_tray_thread_started') and self._tray_thread_started:
            return
        
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
            self.tray_icon = None
        
        if not hasattr(self, '_cached_tray_icon_image'):
            try:
                self._cached_tray_icon_image = PILImage.open(ICON_DIR)
            except:
                self._cached_tray_icon_image = PILImage.new('RGB', (64, 64), color='blue')
        
        image = self._cached_tray_icon_image

        menu = (
            pystray.MenuItem("Show", self.show_window_from_tray),
            pystray.MenuItem("Settings", self.open_settings_from_tray),
            pystray.MenuItem("Exit", self.quit_application_from_tray)
        )
        self.tray_icon = pystray.Icon("SukiTranslate", image, APP_NAME, menu)
        
        if not hasattr(self, '_tray_thread_started') or not self._tray_thread_started:
            def run_tray():
                try:
                    self.tray_icon.run()
                except Exception as e:
                    print(f"Tray icon error: {e}")
                finally:
                    self._tray_thread_started = False
            
            threading.Thread(target=run_tray, daemon=True).start()
            self._tray_thread_started = True

    def show_window_from_tray(self):
        tb = None
        if hasattr(self, 'custom_title_bars'):
            for t in self.custom_title_bars:
                try:
                    if t and not t.is_destroyed() and getattr(t, 'parent_window', None) == self.root:
                        tb = t
                        break
                except Exception:
                    continue

        # Nếu tìm được title bar và nó có method restore_main_window -> dùng luôn
        if tb and hasattr(tb, 'restore_main_window'):
            try:
                tb.restore_main_window()
                return
            except Exception as e:
                print(f"[show_window_from_tray] restore_main_window failed: {e}")

        # Fallback: hành vi mặc định
        try:
            self.root.after(1, self.show_window)
        except Exception as e:
            # nếu show_window cũng có vấn đề thì cố gắng trực tiếp restore như restore_main_window
            try:
                self.root.deiconify()
                self.root.lift()
                self.root.attributes("-topmost", True)
                self.root.after(100, lambda: self.root.attributes("-topmost", False))
                self.root.focus_force()
            except Exception as e2:
                print(f"[show_window_from_tray] fallback failed: {e2}")

    def open_settings_from_tray(self):
        self.root.after(1, self.open_settings)

    def quit_application_from_tray(self):
        self.root.after(1, self.quit_application)

    def quit_application(self):
        if hasattr(self, 'original_stdout') and self.original_stdout:
            sys.stdout = self.original_stdout
        if hasattr(self, 'original_stderr') and self.original_stderr:
            sys.stderr = self.original_stderr
        
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
            self.tray_icon = None
        
        if hasattr(self, '_tray_thread_started'):
            self._tray_thread_started = False
        
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except:
                pass
        self.root.destroy()

    def bind_global_hotkey(self):
        self.unbind_global_hotkey()
        hotkey = self.settings.get("hotkey", "Ctrl+Q")
        try:        
            keyboard.add_hotkey(hotkey.lower(), self.start_capture)
            self.current_hotkey = hotkey

        except Exception as e:
            print(f"Error setting global hotkey: {e}")

    def unbind_global_hotkey(self):
        try:
            if hasattr(keyboard, '_hotkeys'):
                for hotkey in list(keyboard._hotkeys):
                    keyboard.remove_hotkey(hotkey)
        except Exception as e:
            print(f"Error unbinding hotkey: {e}")


    def _global_hotkey_listener(self, hotkey):
        try:
            keyboard.add_hotkey(hotkey.lower(), self.start_capture)
            
            while self.hotkey_running:
                keyboard.wait()
        except Exception as e:
            print(f"Global hotkey error: {e}")
        finally:
            keyboard.unhook_all()

    def update_general_settings(self, event=None):
        self.bind_global_hotkey()

    def toggle_console(self):
        if self.console_visible and self.console_window and self.console_window.winfo_exists():
            try:
                window_state = self.console_window.state()
                if window_state == 'withdrawn':
                    self.console_window.deiconify()
                    self.console_window.lift()
                    self.console_window.focus_force()
                    return
                else:
                    self.on_console_close()
            except tk.TclError:
                self.on_console_close()
                self.show_console()
        else:
            self.show_console()
    
    def show_console(self):
        self.console_window = tk.Toplevel(self.root)
        self.console_window.geometry("600x400")
        self.console_window.resizable(True, True)
        
        self.console_title_bar = CustomTitleBar(self.console_window, "Console Log - Suki Translate", app_ref=self, show_maximize=True, use_system_titlebar=False)
        try:
            self.console_window.iconbitmap(ICON_DIR)
        except:
            pass
        
        if hasattr(self, 'custom_title_bars'):
            self.custom_title_bars.append(self.console_title_bar)
        
        def on_console_close():
            if hasattr(self, 'custom_title_bars') and hasattr(self, 'console_title_bar') and self.console_title_bar in self.custom_title_bars:
                self.custom_title_bars.remove(self.console_title_bar)
            
            if hasattr(self, 'console_title_bar'):
                self.console_title_bar.cleanup()
            
            self.on_console_close()
        self.console_window._window_close_handler = on_console_close
        
        self.console_window.configure(bg=self.theme_values.get('bg_color', '#1E1E1E'))

        console_style = ttk.Style()
        console_style.configure(
            "DarkConsole.TFrame",
            background="#1E1E1E"
        )
        console_style.configure(
            "DarkConsole.TButton",
            foreground="white",
            background="#3C3C3C",
            font=('Arial', 9)
        )
        console_style.map(
            "DarkConsole.TButton",
            background=[('active', '#555555'), ('pressed', '#666666')],
            foreground=[('active', 'white')]
        )
        console_style.configure(
            "DarkConsole.Vertical.TScrollbar",
            background="#3C3C3C",
            troughcolor="#2E2E2E",
            arrowcolor="#DCDCDC",
            gripcount=0
        )
        console_style.map(
            "DarkConsole.Vertical.TScrollbar",
            background=[('active', '#555555')],
            troughcolor=[('active', '#2E2E2E')]
        )
        
        text_frame = ttk.Frame(self.console_window, style="DarkConsole.TFrame")
        text_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(text_frame, style="DarkConsole.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        
        self.console_log_text_widget = tk.Text(
            text_frame, 
            wrap="word", 
            yscrollcommand=scrollbar.set,
            bg="#1E1E1E",
            fg="#DCDCDC",
            insertbackground="white",
            borderwidth=0, 
            highlightthickness=0,
            state='disabled'
        )
        self.console_log_text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.console_log_text_widget.yview)
        
        button_frame = ttk.Frame(self.console_window, style="DarkConsole.TFrame")
        button_frame.pack(fill="x", pady=(0,5))

        clear_button = ttk.Button(button_frame, text="Clear Log", 
                                 command=self.clear_console_log_and_buffer,
                                 style="DarkConsole.TButton")
        clear_button.pack(pady=5)
        
        global ACTIVE_LOG_WIDGET
        ACTIVE_LOG_WIDGET = self.console_log_text_widget
        
        self.console_log_text_widget.configure(state='normal')
        current_logs = "".join(list(GLOBAL_LOG_BUFFER))
        self.console_log_text_widget.insert(tk.END, current_logs)
        self.console_log_text_widget.see(tk.END)
        self.console_log_text_widget.configure(state='disabled')
            
        self.console_window.protocol("WM_DELETE_WINDOW", self.on_console_close)
        self.console_visible = True

    def clear_console_log_and_buffer(self):
        if self.console_log_text_widget and self.console_log_text_widget.winfo_exists():
            self.console_log_text_widget.configure(state='normal')
            self.console_log_text_widget.delete(1.0, tk.END)
            self.console_log_text_widget.configure(state='disabled')
        GLOBAL_LOG_BUFFER.clear()
        print("Console log cleared.")

    def on_console_close(self):
        global ACTIVE_LOG_WIDGET
        ACTIVE_LOG_WIDGET = None
        self.console_log_text_widget = None 
        self.console_visible = False
        if self.console_window and self.console_window.winfo_exists():
            self.console_window.destroy()
            self.console_window = None

    def update_language_setting(self, event=None):
        source_display = self.source_lang_combo.get()
        target_display = self.target_lang_combo.get()
        source_lang = LANGUAGE_MAPPING.get(source_display, {}).get("tess_code", "eng")
        target_lang = LANGUAGE_MAPPING.get(target_display, {}).get("tess_code", "vie")
        
        self.settings["source_lang"] = source_lang
        self.settings["target_lang"] = target_lang
        self.settings_manager.save_settings(self.settings)


    
    def apply_theme(self):
        dark_mode = self.settings.get("dark_mode", False)
        always_on_top = self.settings.get("always_on_top", False)
        self.root.attributes('-topmost', always_on_top)

        style = ttk.Style()
        style.theme_use('default')

        if dark_mode:
            bg_color = "#2e2e2e"
            active_bg = "#444444"
            entry_bg = "#3c3c3c"
            fg_color = "#ffffff"
            text_bg = self.settings.get("custom_bg_color", "#000000")
            text_fg = self.settings.get("custom_font_color", "#ffffff")

            style.map("TCheckbutton",
                background=[("active", active_bg)],
                foreground=[("active", fg_color)])
            style.map("TRadiobutton",
                background=[("active", active_bg)],
                foreground=[("active", fg_color)])
            style.map("TButton",
                background=[("active", active_bg)],
                foreground=[("active", fg_color)])
            style.map("TNotebook.Tab",
                background=[("selected", active_bg)])
            style.map('TCombobox',
                fieldbackground=[('readonly', entry_bg)],
                background=[('readonly', entry_bg)],
                foreground=[('readonly', fg_color)],
                selectbackground=[('readonly', active_bg)],
                selectforeground=[('readonly', fg_color)],
                arrowcolor=[('active', fg_color)]
            )
            self.root.option_add('*TCombobox*Listbox.background', entry_bg)
            self.root.option_add('*TCombobox*Listbox.foreground', fg_color)
            self.root.option_add('*TCombobox*Listbox.selectBackground', active_bg)
            self.root.option_add('*TCombobox*Listbox.selectForeground', fg_color)
            self.root.option_add('*TCombobox*Listbox*Scrollbar.background', '#3c3c3c')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.troughColor', '#2e2e2e')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.activeBackground', '#444444')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.highlightBackground', '#2e2e2e')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.borderWidth', '0')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.selectBackground', '#444444')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.foreground', '#ffffff')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.activeForeground', '#ffffff')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.relief', 'flat')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.highlightThickness', '0')
            self.root.option_add('*Scrollbar.background', '#3c3c3c')
            self.root.option_add('*Scrollbar.troughColor', '#2e2e2e')
            self.root.option_add('*Scrollbar.activeBackground', '#444444')
            self.root.option_add('*Scrollbar.foreground', '#ffffff')
            self.root.option_add('*Scrollbar.activeForeground', '#ffffff')
            self.root.option_add('*Scrollbar.relief', 'flat')
            self.root.option_add('*Scrollbar.borderWidth', '0')
            style.map('TSpinbox',
                fieldbackground=[('readonly', entry_bg), ('active', active_bg)],
                background=[('readonly', entry_bg), ('active', active_bg)],
                foreground=[('readonly', fg_color), ('active', fg_color)],
                arrowcolor=[('active', fg_color)]
            )


        else:
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            entry_bg = "#ffffff"
            active_bg = "#d9d9d9"
            text_bg = "#ffffff"
            text_fg = "#000000"

            style.map("TCheckbutton",
                background=[("active", active_bg)],
                foreground=[("active", fg_color)])
            style.map("TRadiobutton",
                background=[("active", active_bg)],
                foreground=[("active", fg_color)])
            style.map("TButton",
                background=[("active", active_bg)],
                foreground=[("active", fg_color)])
            style.map("TNotebook.Tab",
                background=[("selected", active_bg)])
            style.map('TCombobox',
                fieldbackground=[('readonly', entry_bg)],
                background=[('readonly', entry_bg)],
                foreground=[('readonly', fg_color)],
                selectbackground=[('readonly', active_bg)],
                selectforeground=[('readonly', fg_color)],
                arrowcolor=[('active', fg_color)]
            )
            self.root.option_add('*TCombobox*Listbox.background', entry_bg)
            self.root.option_add('*TCombobox*Listbox.foreground', fg_color)
            self.root.option_add('*TCombobox*Listbox.selectBackground', active_bg)
            self.root.option_add('*TCombobox*Listbox.selectForeground', fg_color)
            self.root.option_add('*TCombobox*Listbox*Scrollbar.background', '#e1e1e1')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.troughColor', '#f0f0f0')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.activeBackground', '#d0d0d0')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.highlightBackground', '#f0f0f0')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.borderWidth', '0')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.selectBackground', '#d0d0d0')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.foreground', '#000000')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.activeForeground', '#000000')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.relief', 'flat')
            self.root.option_add('*TCombobox*Listbox*Scrollbar.highlightThickness', '0')
            style.map('TSpinbox',
                fieldbackground=[('readonly', '#3c3c3c'), ('active', '#444444')],
                background=[('readonly', '#3c3c3c'), ('active', '#444444')],
                foreground=[('readonly', '#ffffff'), ('active', '#ffffff')],
                arrowcolor=[('active', '#ffffff')]
            )

        self.theme_values = {
            'bg_color': bg_color,
            'fg_color': fg_color,
            'entry_bg': entry_bg,
            'active_bg': active_bg,
            'text_bg': text_bg,
            'text_fg': text_fg
        }

        self.root.configure(bg=bg_color)
        
        if hasattr(self, "result_text"):
            self.result_text.configure(
                bg=text_bg,
                fg=text_fg,
                insertbackground=fg_color,
                highlightbackground=bg_color
            )



        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=bg_color, foreground=fg_color)
        style.map("TNotebook.Tab", background=[("selected", active_bg)])

        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color)
        style.configure("TCheckbutton", background=bg_color, foreground=fg_color)
        

        style.configure("TRadiobutton", background=bg_color, foreground=fg_color)
        

        style.configure("TEntry", fieldbackground=entry_bg, background=entry_bg, foreground=fg_color)
        style.configure("TCombobox", fieldbackground=entry_bg, background=entry_bg, foreground=fg_color)
        style.configure("TButton", background=entry_bg, foreground=fg_color)
        style.configure('TSpinbox',
                background=entry_bg,
                foreground=fg_color,
                fieldbackground=entry_bg,
                insertcolor=fg_color,
                bordercolor=active_bg,
                arrowcolor=fg_color,
                lightcolor=entry_bg,
                darkcolor=entry_bg
            )
        style.configure('Popdown',
                background=entry_bg,
                foreground=fg_color,
                fieldbackground=entry_bg,
                insertcolor=fg_color,
                bordercolor=active_bg,
                arrowcolor=fg_color,
                lightcolor=entry_bg,
                darkcolor=entry_bg
            )
        
        if hasattr(self, "widgets_to_theme"):
            for widget in self.widgets_to_theme:
                try:
                    if not str(widget).startswith('.!ttk'):
                        widget.configure(bg=bg_color, fg=fg_color)
                except:
                    pass
        
        if hasattr(self, 'canvas'):
            self.canvas.configure(bg=bg_color)
        
        if hasattr(self, 'custom_title_bars'):
            self.custom_title_bars = [tb for tb in self.custom_title_bars if tb is not None and not tb.is_destroyed()]
            for title_bar in self.custom_title_bars.copy():
                try:
                    if title_bar and not title_bar.is_destroyed():
                        title_bar.apply_theme(self.theme_values)
                    else:
                        if title_bar in self.custom_title_bars:
                            self.custom_title_bars.remove(title_bar)
                except (tk.TclError, AttributeError):
                    if title_bar in self.custom_title_bars:
                        self.custom_title_bars.remove(title_bar)

    def open_settings(self):
        if hasattr(self, "settings_window"):
            if self.settings_window and self.settings_window.window.winfo_exists():
                try:
                    window_state = self.settings_window.window.state()
                    if window_state == 'withdrawn':
                        self.settings_window.window.deiconify()
                    self.settings_window.window.lift()
                    self.settings_window.window.focus_force()
                    return
                except tk.TclError:
                    del self.settings_window
            else:
                del self.settings_window

        self.settings_window = SettingsWindow(self, self.translator_manager, self.spell_checker)
        self.settings_window.window.protocol("WM_DELETE_WINDOW", self.on_settings_window_close)

    def on_settings_window_close(self):
        if hasattr(self, "settings_window"):
            self.settings_window.window.destroy()
            if self.root.winfo_exists():
                self.settings = self.settings_manager.load_settings()
                try:
                    self.apply_theme()
                except tk.TclError:
                    pass

    def start_capture(self):
        if hasattr(self, 'overlay') and self.overlay:
            self.cancel_capture()

        self.rect = None

        self.root.after(100, self.create_overlay)
        
    def create_overlay(self):
        try:
            if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
                self.overlay.destroy()

            try:
                with mss.mss() as sct:
                    monitor = sct.monitors[0]
                    mon_w, mon_h = monitor["width"], monitor["height"]                   
                    self.full_screen_img = Image.frombytes("RGB", (mon_w, mon_h), sct.grab(monitor).bgra, "raw", "BGRX")
            except Exception as e:
                print(f"Error capturing screen: {e}")
                self.cancel_capture()
                return
      
            try:
                self.overlay = tk.Toplevel(self.root)
                self.overlay.overrideredirect(True)
                self.overlay.withdraw()
                self.overlay.geometry(f"{mon_w}x{mon_h}+0+0")
                self.overlay.attributes('-topmost', True)
                self.overlay.config(cursor='crosshair')
            except Exception as e:
                print(f"Error creating overlay window: {e}")
                self.cancel_capture()
                return

            
            try:
                scr_w = self.root.winfo_screenwidth()
                scr_h = self.root.winfo_screenheight()
                self.scale_x = mon_w / scr_w
                self.scale_y = mon_h / scr_h
            except Exception as e:
                print(f"Error calculating scaling: {e}")
                
                self.scale_x = self.scale_y = 1.0

            
            try:
                self.tk_img = ImageTk.PhotoImage(self.full_screen_img)
                self.overlay_canvas = tk.Canvas(self.overlay, width=mon_w, height=mon_h, highlightthickness=0)
                self.overlay_canvas.place(x=0, y=0, width=mon_w, height=mon_h)
                self.overlay_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
            except Exception as e:
                print(f"Error creating canvas/image: {e}")
                self.cancel_capture()
                return

            
            try:
                border_thickness = 3
                self.overlay_canvas.create_rectangle(0, 0, mon_w, border_thickness, fill="white", width=0)
                self.overlay_canvas.create_rectangle(0, mon_h - border_thickness, mon_w, mon_h, fill="white", width=0)
                self.overlay_canvas.create_rectangle(0, 0, border_thickness, mon_h, fill="white", width=0)
                self.overlay_canvas.create_rectangle(mon_w - border_thickness, 0, mon_w, mon_h, fill="white", width=0)
            except Exception as e:
                print(f"Error creating borders: {e}")
                

            
            try:
                self.overlay_canvas.bind("<ButtonPress-1>", self.on_mouse_down)
                self.overlay_canvas.bind("<B1-Motion>", self.on_mouse_move)
                self.overlay_canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
                
                
                self.overlay_canvas.bind("<Button-3>", self.cancel_capture)
                
                
                self.overlay.bind("<Escape>", self.cancel_capture)
                self.overlay_canvas.bind("<Key>", self.on_key_press)
                
                
                self.overlay.bind("<FocusOut>", self.on_focus_lost)
                self.overlay.bind("<Alt-F4>", self.cancel_capture)
                self.overlay.bind("<Control-c>", self.cancel_capture)
                self.overlay.bind("<Double-Button-3>", self.cancel_capture)
                
                
                self.overlay_canvas.bind("<MouseWheel>", self.on_mouse_wheel)
                self.overlay_canvas.bind("<Button-4>", self.on_mouse_wheel)
                self.overlay_canvas.bind("<Button-5>", self.on_mouse_wheel)
            except Exception as e:
                print(f"Error setting up event bindings: {e}")
                self.cancel_capture()
                return

            try:
                self.overlay.focus_force()
                self.overlay_canvas.focus_set()
                self.overlay_canvas.config(takefocus=True)
            except Exception as e:
                print(f"Error setting focus: {e}")
            
            self.overlay.after(100, self._set_focus_with_delay)
            self.overlay.after(60000, self._emergency_timeout)
            
            try:
                self.overlay.deiconify()
                self.overlay.lift()
                self.overlay.focus_force()
            except Exception as e:
                print(f"Error showing overlay window: {e}")
        except Exception as e:
            print(f"Critical error in create_overlay: {e}")
            
            self.cancel_capture()

    def _set_focus_with_delay(self):

        try:
            if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():

                self.overlay.focus_force()
                self.overlay_canvas.focus_force()

                try:
                    self.overlay.grab_set()
                except tk.TclError as e:
                    print(f"Warning: Could not set grab: {e}")
                    try:
                        self.overlay.grab_set_global()
                    except tk.TclError as e2:
                        print(f"Warning: Could not set global grab either: {e2}")
            else:
                print("Overlay no longer exists - skipping focus setup")
        except Exception as e:
            print(f"Critical error in _set_focus_with_delay: {e}")

            try:
                self.cancel_capture()
            except:
                pass

    def cancel_capture(self, event=None):
        try:
            if win32api.GetAsyncKeyState(win32con.VK_LBUTTON) & 0x8000:
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        except Exception as e:
            print(f"Error checking/releasing mouse button state: {e}")

        if hasattr(self, 'overlay') and self.overlay:
            try:

                if self.overlay.winfo_exists():
                    try:
                        self.overlay.grab_release()
                    except tk.TclError as e:
                        print(f"Error releasing grab: {e}")
                    
                    try:
                        self.overlay.destroy()
                    except tk.TclError as e:
                        print(f"Error destroying overlay: {e}")
                        
            except Exception as e:
                print(f"Critical error in cancel_capture: {e}")

                try:
                    if hasattr(self.overlay, 'destroy'):
                        self.overlay.destroy()
                except:
                    pass
            
        self.overlay = None
        self.rect = None
        
        try:
            if hasattr(self, 'root') and self.root and self.root.winfo_exists():
                self.root.focus_force()
                self.root.lift()
        except (tk.TclError, AttributeError) as e:
            print(f"Error returning focus to main window: {e}")
        

    def on_key_press(self, event):

        if event.keysym in ["Escape", "q", "Q"]:
            print(f"Key pressed: {event.keysym} - exiting crop mode only (application stays running)")
            self.cancel_capture(event)
        return "break"
    
    def on_focus_lost(self, event=None):
        if hasattr(self, 'overlay') and self.overlay:
            self.overlay.after(1000, self._check_focus_and_cancel)
    
    def _check_focus_and_cancel(self):

        try:
            if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
                current_focus = self.overlay.focus_get()
                if not current_focus or not str(current_focus).startswith(str(self.overlay)):
                    self.cancel_capture()
        except Exception as e:
            print(f"Error in focus check: {e}")
    
    def on_mouse_wheel(self, event=None):
        self.cancel_capture(event)
        return "break"
    
    def _emergency_timeout(self):

        if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
            print("EMERGENCY TIMEOUT: Force closing overlay after 60 seconds")
            try:
                print("WARNING: Crop mode has been active for too long. Force closing for safety.")
            except:
                pass
            self.cancel_capture()

    def on_mouse_down(self, event):
        self.x1 = event.x
        self.y1 = event.y
        self.x2 = None
        self.y2 = None
        self.rect = None

    def on_mouse_move(self, event):
        if  self.x1 is not None and self.y1 is not None:
            self.x2 = event.x
            self.y2 = event.y
            if self.rect:
                self.overlay_canvas.delete(self.rect)
            self.rect = self.overlay_canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2, outline="red", width=1)

    def on_mouse_up(self, event):
        x1l, y1l = self.x1, self.y1
        x2l, y2l = event.x, event.y
        x1l, x2l = min(x1l, x2l), max(x1l, x2l)
        y1l, y2l = min(y1l, y2l), max(y1l, y2l)

        cw = max(1, self.overlay_canvas.winfo_width())
        ch = max(1, self.overlay_canvas.winfo_height())

        if hasattr(self, 'overlay') and self.overlay and self.overlay.winfo_exists():
            try:
                self.overlay.destroy()
            except tk.TclError:
                pass
        self.overlay = None

        iw, ih = self.full_screen_img.size

        sx = iw / cw
        sy = ih / ch

        x1p = int(round(x1l * sx))
        y1p = int(round(y1l * sy))
        x2p = int(round(x2l * sx))
        y2p = int(round(y2l * sy))

        x1p = max(0, min(x1p, iw))
        x2p = max(0, min(x2p, iw))
        y1p = max(0, min(y1p, ih))
        y2p = max(0, min(y2p, ih))

        self.x1 = x1p
        self.y1 = y1p
        self.x2 = x2p
        self.y2 = y2p

        self.captured_image = self.full_screen_img.crop((x1p, y1p, x2p, y2p))

        threading.Thread(target=self.perform_translation).start()

    def perform_translation(self):
        try:
            if self.captured_image is None:
                messagebox.showerror("Error", "Please capture an area first.")
                return

            captured_image = self.captured_image

            

            ocr_mode = self.settings.get("ocr_mode", "tesseract")
            if ocr_mode == "Tesseract":
                extracted_text = self.extract_text_from_image(captured_image)
                self.last_extracted_text = extracted_text

                if not extracted_text.strip():
                    messagebox.showinfo("Info", "No text detected in selected area.")
                    return

                selected_lang = self.source_lang_combo.get()
                if selected_lang in LANGUAGE_MAPPING:
                    self.spell_checker.load_dictionary_for_language(selected_lang)

                if self.spell_checker.current_dict:
                    is_correct, misspelled = self.spell_checker.check_spelling(extracted_text)

                active_translator = self.translator_manager.get_active_translator()
                if not active_translator:
                    messagebox.showerror("Error", "No translator is enabled. Please enable one in Settings.")
                    return

                self.translated_input_text = extracted_text
                print(f"--- Extracted OCR Text -----------------------------------------------\n{extracted_text}")

                if self.settings.get("auto_copy_original_clipboard", False):
                    try:
                        copy_original_text(extracted_text)
                    except Exception as clipboard_error:
                        print(f"Error auto-copying original text to clipboard: {clipboard_error}")

                translated_text = self.translate_with_api(
                    extracted_text,
                    self.source_lang_combo.get(),
                    self.target_lang_combo.get(),
                    active_translator['path']
                )
            elif ocr_mode == "AI":
                translated_text = self.extract_text_with_ai(captured_image)
                self.last_extracted_text = translated_text

            if not translated_text.strip():
                messagebox.showinfo("Info", "No text detected or translated in selected area.")
                return

            self.translated_input_text = translated_text
            print(f"--- Result Text ------------------------------------------------------\n{translated_text}")

            if self.settings.get("auto_copy_clipboard", False):
                try:
                    copy_translated_text(translated_text)
                except Exception as clipboard_error:
                    print(f"Error auto-copying to clipboard: {clipboard_error}")

            self.display_translation_overlay(translated_text)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def extract_text_from_image(self, image):
        lang_name = self.source_lang_combo.get()
        if lang_name in LANGUAGE_MAPPING:
            self.spell_checker.load_dictionary_for_language(lang_name)
        lang_data = LANGUAGE_MAPPING.get(lang_name, LANGUAGE_MAPPING["English"])
        tess_code = lang_data["tess_code"]

        traineddata_path = os.path.join(TESSDATA_DIR, f"{tess_code}.traineddata")
        if not os.path.exists(traineddata_path):
            if not download_traineddata(tess_code):
                messagebox.showerror("Error", f"Could not download language file for {lang_name}")
                return ""

        try:
            processed_image = prepare_image(image)

            os.environ['TESSDATA_PREFIX'] = TESSDATA_DIR
            text = pytesseract.image_to_string(
                processed_image,
                lang=tess_code,
                config=f'--tessdata-dir {os.path.normpath(TESSDATA_DIR)} --psm 6'
            )
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
        
    def extract_text_with_ai(self, image):
        try:
            active_translator = self.translator_manager.get_active_translator()
            if not active_translator:
                raise Exception("No translator is enabled. Please enable one in Settings.")

            temp_image_path = os.path.join(PROJECT_DIR, "temp_image.png")
            image.save(temp_image_path, format="PNG")

            import base64
            with open(temp_image_path, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            source_lang = self.source_lang_combo.get()
            target_lang = self.target_lang_combo.get()
            source_lang_code = LANGUAGE_MAPPING.get(source_lang, {}).get("code", "en")
            target_lang_code = LANGUAGE_MAPPING.get(target_lang, {}).get("code", "vi")

            translator_path = active_translator['path']
            temp_input = os.path.join(PROJECT_DIR, "temp_input.json")
            with open(temp_input, "w", encoding="utf-8") as f:
                json.dump({
                    "image": image_base64,
                    "sourceLang": source_lang_code,
                    "targetLang": target_lang_code
                }, f)

            temp_output = os.path.join(PROJECT_DIR, "temp_output.txt")

            node_command = (
                f'"{NODE_DIR}" -e "'
                f'const translator = require(\'{translator_path.replace(os.sep, "/")}\'); '
                f'translator.translateImage('
                f'require(\'fs\').readFileSync(\'{temp_input.replace(os.sep, "/")}\', \'utf-8\')'
                f').then(result => require(\'fs\').writeFileSync(\'{temp_output.replace(os.sep, "/")}\', result));"'
            )

            result = subprocess.run(node_command, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                raise Exception(f"Node.js error: {result.stderr}")

            with open(temp_output, "r", encoding="utf-8") as f:
                translated_text = f.read()

            os.remove(temp_image_path)
            os.remove(temp_input)
            os.remove(temp_output)

            return translated_text.strip()

        except Exception as e:
            print(f"AI Translation Error: {e}")
            return ""
        
    def translate_with_api(self, text, source_lang, target_lang, translator_path):
        try:
            temp_input = os.path.join(PROJECT_DIR, "temp_input.txt")
            with open(temp_input, "w", encoding="utf-8") as f:
                f.write(text)
            
            temp_output = os.path.join(PROJECT_DIR, "temp_output.txt")
            
            node_command = (
                f'"{NODE_DIR}" -e "'
                f'const translator = require(\'{translator_path.replace(os.sep, "/")}\'); '
                f'translator.getTranslatedText('
                f'require(\'fs\').readFileSync(\'{temp_input.replace(os.sep, "/")}\', \'utf-8\'), '
                f'\'{source_lang}\', \'{target_lang}\''
                f').then(result => require(\'fs\').writeFileSync(\'{temp_output.replace(os.sep, "/")}\', result));"'
            )
            
            result = subprocess.run(node_command, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Node.js error: {result.stderr}")
            
            with open(temp_output, "r", encoding="utf-8") as f:
                translated_text = f.read()
            
            os.remove(temp_input)
            os.remove(temp_output)
            
            return translated_text
            
        except Exception as e:
            print(f"Translation API Error: {e}")
            return None



    def display_translation_overlay(self, text):
        try:
            if self.current_overlay is not None and self.current_overlay.winfo_exists():
                self.current_overlay.destroy()

            capture_width = abs(self.x2 - self.x1)
            capture_height = abs(self.y2 - self.y1)
                        
            capture_width = max(100, capture_width)
            capture_height = max(50, capture_height)
            
            overlay_x = min(self.x1, self.x2)
            overlay_y = min(self.y1, self.y2)

            font_name = self.settings.get("result_font", "Arial")
            font_size = self.settings.get("result_font_size", 12)
            font_color = self.settings.get("custom_font_color", "#db9aaa")
            stroke_color = self.settings.get("custom_stroke_color", "#000000")
            bg_color = self.settings.get("custom_bg_color", "#000000")

            overlay = tk.Toplevel(self.root)
            overlay.overrideredirect(True)
            overlay.withdraw()
            overlay.attributes('-topmost', True)
            overlay.configure(bg=bg_color)
            
            overlay.geometry("1x1-10000-10000")

            display_mode = self.settings.get("display_mode")
            font_path = find_font_path(font_name)
            if font_path is None:
                font_path = "arial.ttf"
                print(f"Font {font_name} not found, using arial.ttf")
            
            final_width = capture_width
            final_height = capture_height            
           
            if display_mode == "blur":
                img_pil = self.captured_image.convert("RGB")
                img_pil = img_pil.resize((capture_width, capture_height), Image.LANCZOS)
                img_cv2 = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                img_cv2 = cv2.GaussianBlur(img_cv2, (55, 55), 0)

                mask = np.zeros(img_cv2.shape[:2], dtype=np.uint8)
                cv2.rectangle(mask, (0, 0), (capture_width, capture_height), 255, -1)

                inpainted_img = cv2.inpaint(img_cv2, mask, inpaintRadius=1, flags=cv2.INPAINT_TELEA)
                inpainted_img_pil = Image.fromarray(cv2.cvtColor(inpainted_img, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(inpainted_img_pil)
                
                current_font_size = font_size * 1.3
                while True:
                    try:
                        font = ImageFont.truetype(font_path, current_font_size)
                    except:
                        font = ImageFont.load_default()
                    lines = wrap_text(text, font, capture_width - 20)
                    total_text_height = len(lines) * font.size

                    if total_text_height <= capture_height:
                        break  
                    else:
                        current_font_size -= 1
                        if current_font_size < 8:
                            break

                total_text_height = len(lines) * font.size
                y = (capture_height - total_text_height) / 2

                for line in lines:
                    bbox = draw.textbbox((0,0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (capture_width - text_width) / 2
                    draw.text((x, y), line, font=font, fill=font_color, stroke_width=2, stroke_fill=stroke_color)
                    y += font.size

                self.tk_img = ImageTk.PhotoImage(inpainted_img_pil)
                label = tk.Label(overlay, image=self.tk_img, bd=0, highlightthickness=0)
                label.image = self.tk_img
                final_width = capture_width
                final_height = capture_height
                print(f"Blur mode: final dimensions {final_width}x{final_height} match crop area")


            elif display_mode == "auto":
                img_pil = self.captured_image.convert("RGB")
                img_pil = img_pil.resize((capture_width, capture_height), Image.LANCZOS)
                img_cv2 = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                height, width, _ = img_cv2.shape

                top_color = img_cv2[0, width // 2]
                bottom_color = img_cv2[-1, width // 2]
                left_color = img_cv2[height // 2, 0]
                right_color = img_cv2[height // 2, -1]
                avg_color = tuple(map(int, np.mean([top_color, bottom_color, left_color, right_color], axis=0)))

                bg_img = np.full_like(img_cv2, avg_color, dtype=np.uint8)
                bg_pil = Image.fromarray(cv2.cvtColor(bg_img, cv2.COLOR_BGR2RGB))
                draw = ImageDraw.Draw(bg_pil)

                current_font_size = font_size * 1.3
                while True:
                    try:
                        font = ImageFont.truetype(font_path, current_font_size)
                    except:
                        font = ImageFont.load_default()
                    lines = wrap_text(text, font, capture_width - 20)
                    total_text_height = len(lines) * font.size

                    if total_text_height <= capture_height:
                        break
                    else:
                        current_font_size -= 1
                        if current_font_size < 8:
                            break

                total_text_height = len(lines) * font.size
                y = (capture_height - total_text_height) / 2

                for line in lines:
                    bbox = draw.textbbox((0,0), line, font=font)
                    text_width = bbox[2] - bbox[0]
                    x = (capture_width - text_width) / 2
                    draw.text((x, y), line, font=font, fill=font_color, stroke_width=2, stroke_fill=stroke_color)
                    y += font.size

                self.tk_img = ImageTk.PhotoImage(bg_pil)
                label = tk.Label(overlay, image=self.tk_img, bd=0, highlightthickness=0)
                label.image = self.tk_img
                final_width = capture_width
                final_height = capture_height
                print(f"Auto mode: final dimensions {final_width}x{final_height} match crop area")

            else:
                label = tk.Label(
                    overlay,
                    text=text,
                    font=(font_name, font_size),
                    fg=font_color,
                    bg=bg_color,
                    wraplength=capture_width - 20,
                    justify="left",
                    padx=10,
                    pady=10
                )
                label.pack()
                overlay.update_idletasks()
                final_height = label.winfo_reqheight()
                final_width = capture_width
                label.pack_forget()
            label.pack(fill="both", expand=True)
            overlay.update_idletasks()
            
            display_mode = self.settings.get("display_mode")
            if display_mode not in ["blur", "auto"]:
                final_width = max(100, final_width)
                final_height = max(50, final_height)
            else:
                final_width = max(1, final_width)
                final_height = max(1, final_height)
            
            try:
                import mss
                with mss.mss() as sct:
                    crop_center_x = overlay_x + final_width // 2
                    crop_center_y = overlay_y + final_height // 2
                    
                    target_monitor = sct.monitors[0]
                    for monitor in sct.monitors[1:]:
                        if (monitor["left"] <= crop_center_x < monitor["left"] + monitor["width"] and
                            monitor["top"] <= crop_center_y < monitor["top"] + monitor["height"]):
                            target_monitor = monitor
                            break
                    
                    screen_left = target_monitor["left"]
                    screen_top = target_monitor["top"] 
                    screen_width = target_monitor["width"]
                    screen_height = target_monitor["height"]
                    
                    overlay_x = max(screen_left, min(overlay_x, screen_left + screen_width - final_width))
                    overlay_y = max(screen_top, min(overlay_y, screen_top + screen_height - final_height))
                    
            except Exception as e:
                print(f"Error detecting monitor for result window: {e}")
                screen_width = overlay.winfo_screenwidth()
                screen_height = overlay.winfo_screenheight()
                overlay_x = max(0, min(overlay_x, screen_width - final_width))
                overlay_y = max(0, min(overlay_y, screen_height - final_height))
            
            overlay.geometry(f"{final_width}x{final_height}+{overlay_x}+{overlay_y}")

            context_menu = tk.Menu(overlay, tearoff=0)
            is_ai_mode = self.settings.get("ocr_mode", "tesseract") == "AI"
            context_menu.add_command(
                label="Copy Original Text",
                command=lambda: copy_original_text(self.last_extracted_text),
                state="disabled" if is_ai_mode else "normal"
            )
            context_menu.add_command(
                label="Copy Result Text",
                command=lambda: copy_translated_text(text)
            )
            context_menu.add_command(
                label="Copy Image",
                command=lambda: copy_image(self.captured_image)
            )
            context_menu.add_command(
                label="Edit",
                command=lambda: self.open_edit_window(),
                state="disabled" if is_ai_mode else "normal"
            )

            def show_context_menu(event): 
                context_menu.post(event.x_root, event.y_root)
                return "break"
            overlay.bind("<Button-3>", show_context_menu)

            def close_overlay(event=None): 
                if hasattr(self, '_mouse_hook_id') and self._mouse_hook_id:
                    try:
                        import win32gui
                        win32api.UnhookWindowsHookEx(self._mouse_hook_id)
                        self._mouse_hook_id = None
                    except Exception as e:
                        print(f"Error removing mouse hook: {e}")
                overlay.destroy()
                
            overlay.bind("<Escape>", close_overlay)
            overlay.bind("<Button-1>", close_overlay)
            label.bind("<Button-1>", close_overlay)
            overlay.bind("<FocusOut>", close_overlay)

            overlay.deiconify()
            
            overlay.focus_force()
            overlay.lift()
            overlay.attributes('-topmost', True)
            
            self.current_overlay = overlay

        except Exception as e:
            print(f"Error displaying translation overlay: {e}")
            messagebox.showerror("Error", f"Could not display translation: {e}")

    def open_edit_window(self):
        edit_window = tk.Toplevel(self.root)
        edit_window.update_idletasks()
        dpi_scale = edit_window.winfo_fpixels('1i') / 96.0
        edit_window.geometry(f"{int(600 * dpi_scale * 96 / 100)}x{int(600 * dpi_scale * 96 / 100)}")
        edit_window.resizable(True, True)
        
        self.edit_custom_title_bar = CustomTitleBar(edit_window, "Edit and Translate - Suki Translate", app_ref=self, show_maximize=True, use_system_titlebar=False)
        try:
            edit_window.iconbitmap(ICON_DIR)
        except:
            pass
        
        if hasattr(self, 'custom_title_bars'):
            self.custom_title_bars.append(self.edit_custom_title_bar)
        
        self.edit_custom_title_bar.apply_theme(self.theme_values)

        self.apply_theme()
        theme = self.theme_values
        edit_window.configure(bg=theme['bg_color'])

        image_label = None
        if self.captured_image:
            max_img_size = (500, 300)
            img = self.captured_image.copy()
            img.thumbnail(max_img_size, Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            image_label = tk.Label(edit_window, image=tk_img, bg=theme['bg_color'])
            image_label.image = tk_img
            image_label.pack(pady=5)

        lang_frame = ttk.Frame(edit_window)
        lang_frame.pack(fill="x", padx=10, pady=5)
        lang_label = ttk.Label(lang_frame, text="Source Language:")
        lang_label.pack(side="left")
        sorted_languages = sorted(LANGUAGE_MAPPING.keys())
        source_lang_combo = ttk.Combobox(lang_frame, values=sorted_languages, width=25)
        source_lang_combo.set(self.source_lang_combo.get())
        source_lang_combo.pack(side="left", padx=5)

        target_lang_label = ttk.Label(lang_frame, text="Target Language:")
        target_lang_label.pack(side="left", padx=5)
        common_targets = sorted(LANGUAGE_MAPPING.keys())
        target_lang_combo = ttk.Combobox(lang_frame, values=common_targets, width=25)
        target_lang_combo.set(self.target_lang_combo.get())
        target_lang_combo.pack(side="left", padx=5)

        text_frame = ttk.Frame(edit_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        text_widget = tk.Text(
            text_frame,
            height=10,
            wrap="word",
            bg=theme['entry_bg'],
            fg=theme['fg_color'],
            insertbackground=theme['fg_color'],
            highlightbackground=theme['bg_color']
        )
        text_widget.insert("1.0", self.last_extracted_text or "")
        text_widget.pack(fill="both", expand=True, padx=5)

        def translate_edited_text():
            edited_text = text_widget.get("1.0", tk.END).strip()
            source_lang = source_lang_combo.get()
            target_lang = target_lang_combo.get()
            active_translator = self.translator_manager.get_active_translator()
            
            if not edited_text:
                messagebox.showwarning("Warning", "Please enter text to translate.")
                return
            if not active_translator:
                messagebox.showerror("Error", "No translator is enabled. Please enable one in Settings.")
                return

            translated_text = self.translate_with_api(
                edited_text,
                source_lang,
                target_lang,
                active_translator['path']
            )
            if translated_text:
                self.last_extracted_text = edited_text
                self.display_translation_overlay(translated_text)
                edit_window.destroy()
            else:
                messagebox.showerror("Error", "Translation failed.")

        translate_button = ttk.Button(edit_window, text="Translate", command=translate_edited_text)
        translate_button.pack(pady=10)

        self.edit_window = edit_window
        self.edit_window_widgets = {
            'image_label': image_label,
            'text_widget': text_widget,
            'lang_frame': lang_frame,
        }

        edit_window.attributes('-topmost', True)
        edit_window.focus_force()

        def on_edit_window_close():
            if hasattr(self, 'custom_title_bars') and hasattr(self, 'edit_custom_title_bar') and self.edit_custom_title_bar in self.custom_title_bars:
                self.custom_title_bars.remove(self.edit_custom_title_bar)
            
            if hasattr(self, 'edit_custom_title_bar'):
                self.edit_custom_title_bar.cleanup()
            
            self.edit_window = None
            self.edit_window_widgets = None
            edit_window.destroy()

        edit_window.protocol("WM_DELETE_WINDOW", on_edit_window_close)
        edit_window._window_close_handler = on_edit_window_close

    def update_edit_window_theme(self):
        if not hasattr(self, 'edit_window') or not self.edit_window or not self.edit_window.winfo_exists():
            return

        self.apply_theme()
        theme = self.theme_values

        self.edit_window.configure(bg=theme['bg_color'])

        widgets = self.edit_window_widgets
        if widgets['image_label']:
            widgets['image_label'].configure(bg=theme['bg_color'])
        widgets['text_widget'].configure(
            bg=theme['entry_bg'],
            fg=theme['fg_color'],
            insertbackground=theme['fg_color'],
            highlightbackground=theme['bg_color']
        )

if __name__ == "__main__":
    if not os.path.exists(NODE_MODULES_DIR):
        print("Node modules directory not found in AppData. Creating directory...")
        os.makedirs(NODE_MODULES_DIR, exist_ok=True)

    node_fetch_path = os.path.join(NODE_MODULES_DIR, 'node-fetch')
    if not os.path.exists(node_fetch_path):
        print("node-fetch not found. Attempting to install node-fetch...")
        try:
            npm_command = (
                f'"{NPM_DIR}" install node-fetch@2.7.0 '
                f'--prefix "{APPDATA_DIR}"'
            )          
            
            result = subprocess.run(
                npm_command,
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            
            print("node-fetch installed successfully into AppData.")
            if result.stdout:
                print("NPM Output:\n", result.stdout)
            if result.stderr:
                print("NPM Errors:\n", result.stderr)

        except subprocess.CalledProcessError as e:
            msg = f"Error running NPM install: {e}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            print(msg)
            messagebox.showerror("NPM Installation Error", msg)
            sys.exit(1)
        except Exception as e:
            msg = f"An unexpected error occurred during node-fetch installation: {e}"
            print(msg)
            messagebox.showerror("Installation Error", msg)
            sys.exit(1)
            
    if is_already_running():
        sys.exit(0)

    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except:
        ctypes.windll.user32.SetProcessDPIAware()

    try:
        root = tk.Tk()
        app = SukiTranslateApp(root)
        root.update_idletasks()
        dpi = root.winfo_fpixels('1i') 
        root.geometry(f"{int(315 * dpi / 96)}x{int(125 * dpi / 100)}")
        root.resizable(False, False)

        settings_manager = SettingsManager()
        settings = settings_manager.load_settings()
        if settings.get("run_at_startup", False) and settings.get("minimize_to_tray", False):
            root.withdraw()
            app.system_tray_icon()
            
        def on_closing():
            if app.settings.get("minimize_to_tray", False):
                app.root.withdraw()
                if not app.tray_icon or not getattr(app, '_tray_thread_started', False):
                    app.system_tray_icon()
            else:
                app.quit_application()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        def delayed_update_check():
            try:
                app.update_checker.check_for_updates_on_startup()
            except Exception as e:
                print(f"Error checking for updates on startup: {e}")
        
        root.after(5000, delayed_update_check)
        
        root.mainloop()

    except Exception as e:
        if 'app' in locals() and hasattr(app, 'original_stdout') and app.original_stdout:
            sys.stdout = app.original_stdout
        if 'app' in locals() and hasattr(app, 'original_stderr') and app.original_stderr:
            sys.stderr = app.original_stderr
        
        import traceback
        traceback.print_exc()

        try:
            if GLOBAL_LOG_BUFFER is not None:
                 GLOBAL_LOG_BUFFER.append(f"FATAL ERROR: {e}\n{traceback.format_exc()}")
        except:
            pass

        sys.exit(1)
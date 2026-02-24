import sys, os, json, subprocess, requests, keyboard, threading, socket, re, io, cv2, mss, time, collections, ctypes, webbrowser, base64
import numpy as np
import win32clipboard, win32api, win32con, win32gui
from PIL import Image, ImageDraw, ImageFont
from packaging import version
import colorsys
from fontTools.ttLib import TTFont
from plyer import notification


from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QComboBox, QTextEdit, QSystemTrayIcon, QMenu, QFormLayout, QLineEdit, QFileDialog, QCheckBox, QStackedWidget, QScrollArea, QSizePolicy, QSlider, QListWidget, QListWidgetItem, QDoubleSpinBox, QSpinBox, QColorDialog, QFontComboBox, QRadioButton, QButtonGroup, QFrame, QMessageBox)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QRect, QRectF, QThread, QPoint, QEvent
from PySide6.QtGui import QIcon, QPixmap, QPainter, QPainterPath, QAction, QColor, QFont, QMouseEvent, QKeySequence
APP_NAME = "Suki Translate"
VERSION = "2.0.0"
GITHUB_REPO_URL = "https://api.github.com/repos/Suki8898/SukiTranslate/releases/latest"

THEME_BG_COLOR = "#2e2e2e"
THEME_FG_COLOR = "#ffffff"
THEME_ENTRY_BG = "#3c3c3c"
THEME_ACTIVE_BG = "#444444"
THEME_SCROLLBAR_BG = "#3c3c3c"
THEME_SCROLLBAR_TROUGH = "#2e2e2e"
THEME_SCROLLBAR_ACTIVE = "#555555"
THEME_SCROLLBAR_ARROW = "#ffffff"

def enable_windows_dark_context_menus():
    """Best-effort: ask Windows to render native context menus in dark mode."""
    if sys.platform != "win32":
        return False

    try:
        uxtheme = ctypes.WinDLL("uxtheme")
        set_preferred_app_mode = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int)(135, uxtheme)
        flush_menu_themes = ctypes.WINFUNCTYPE(None)(136, uxtheme)

        set_preferred_app_mode(2)
        flush_menu_themes()
        return True
    except Exception:
        return False


WINDOWS_DARK_MENU_ENABLED = enable_windows_dark_context_menus()

APPDATA_DIR = os.path.join(os.getenv('APPDATA'), 'Suki8898', 'SukiTranslate')
os.makedirs(APPDATA_DIR, exist_ok=True)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

if getattr(sys, 'frozen', False):
    _base_bundle_dir = sys._MEIPASS
    ICON_DIR = os.path.join(_base_bundle_dir, 'icons', 'icon.ico')
else:
    ICON_DIR = os.path.join(PROJECT_DIR, 'icons', 'icon.ico')

LOCK_FILE = os.path.join(APPDATA_DIR, 'app.lock')
LOG_FILE = os.path.join(APPDATA_DIR, 'app.log')


class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "a", encoding="utf-8")
    def write(self, message):
        if self.terminal:
            try:
                self.terminal.write(message)
            except UnicodeEncodeError:
                self.terminal.write(message.encode('ascii', 'replace').decode('ascii'))
        try:
            self.log.write(message)
            self.log.flush()
        except:
            pass
    def flush(self):
        if self.terminal:
            self.terminal.flush()
        try:
            self.log.flush()
        except:
            pass

class HotkeyLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setPlaceholderText("Press hotkey...")
        self.setStyleSheet("background-color: #3c3c3c; color: #ffffff; border: 1px solid #555;")

    def keyPressEvent(self, event):
        key = event.key()
        modifiers = event.modifiers()
        
        if key == Qt.Key_Escape:
            self.clear()
            return
            
        if key in [Qt.Key_Control, Qt.Key_Shift, Qt.Key_Alt, Qt.Key_Meta]:
            return

        parts = []
        if modifiers & Qt.ControlModifier: parts.append("ctrl")
        if modifiers & Qt.AltModifier:     parts.append("alt")
        if modifiers & Qt.ShiftModifier:   parts.append("shift")
        if modifiers & Qt.MetaModifier:    parts.append("windows")

        key_str = QKeySequence(key).toString().lower()
        
        
        special_keys = {
            "return": "enter",
            "enter": "enter",
            "backspace": "backspace",
            "tab": "tab",
            "space": "space",
            "del": "delete",
            "ins": "insert",
            "left": "left",
            "right": "right",
            "up": "up",
            "down": "down",
            "pgup": "page up",
            "pgdown": "page down",
            "home": "home",
            "end": "end",
            "esc": "esc"
        }
        key_str = special_keys.get(key_str, key_str)
        
        if key_str:
            parts.append(key_str)
            self.setText("+".join(parts))

if not getattr(sys, 'frozen', False): 
    sys.stdout = Logger(LOG_FILE)
    sys.stderr = Logger(LOG_FILE)
else:
    sys.stdout = Logger(LOG_FILE)
    sys.stderr = Logger(LOG_FILE)

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
        script_path = os.path.abspath(sys.argv[0])
        args = [f'"{script_path}"'] + sys.argv[1:]
        cwd = os.path.dirname(script_path)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(args), cwd, 1)
        os._exit(0)
    except Exception as e:
        print(f"Failed to restart as admin: {e}")
        os._exit(1)


try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    ctypes.windll.user32.SetProcessDPIAware()

LANGUAGES = ['Afrikaans', 'Amharic', 'Arabic', 'Assamese', 'Azerbaijani', 'Belarusian', 'Bengali', 'Tibetan', 'Bosnian', 'Bulgarian', 'Catalan', 'Cebuano', 'Czech', 'Chinese (Simplified)', 'Chinese (Traditional)', 'Cherokee', 'Welsh', 'Danish', 'German', 'Dzongkha', 'Greek', 'English', 'Esperanto', 'Estonian', 'Basque', 'Persian', 'Finnish', 'French', 'Irish', 'Galician', 'Gujarati', 'Haitian Creole', 'Hebrew', 'Hindi', 'Croatian', 'Hungarian', 'Armenian', 'Indonesian', 'Icelandic', 'Italian', 'Javanese', 'Japanese', 'Kannada', 'Georgian', 'Kazakh', 'Khmer', 'Korean', 'Kurdish', 'Kyrgyz', 'Lao', 'Latin', 'Latvian', 'Lithuanian', 'Luxembourgish', 'Macedonian', 'Malayalam', 'Marathi', 'Malay', 'Burmese', 'Nepali', 'Dutch', 'Norwegian', 'Occitan', 'Oriya', 'Punjabi', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Sanskrit', 'Sinhala', 'Slovak', 'Slovenian', 'Spanish', 'Albanian', 'Serbian', 'Swedish', 'Swahili', 'Tamil', 'Telugu', 'Tajik', 'Tagalog', 'Thai', 'Turkish', 'Uyghur', 'Ukrainian', 'Urdu', 'Uzbek', 'Vietnamese', 'Yiddish', 'Yoruba']

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
                time.sleep(1.0)
                max_wait = 5
                wait_count = 0
                while os.path.exists(LOCK_FILE) and wait_count < max_wait:
                    time.sleep(0.5)
                    wait_count += 0.5
                if os.path.exists(LOCK_FILE):
                    os.remove(LOCK_FILE)
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
        
def copy_translated_text(text):
    QApplication.clipboard().setText(text)

def copy_image(image):
    output = io.BytesIO()
    image.convert("RGB").save(output, "PNG")
    pixmap = QPixmap()
    pixmap.loadFromData(output.getvalue(), "PNG")
    QApplication.clipboard().setPixmap(pixmap)

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
    if text is None:
        return [""]

    lines = []
    for raw_line in text.splitlines():
        if raw_line == "":
            lines.append("")
            continue

        words = raw_line.split()
        if not words:
            lines.append("")
            continue

        current_line = words[0]
        for word in words[1:]:
            candidate = f"{current_line} {word}"
            bbox = font.getbbox(candidate)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line = candidate
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)

    if not lines:
        lines.append(text.strip() if isinstance(text, str) else "")

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

class UpdateChecker:
    def __init__(self, app_ref=None):
        self.app_ref = app_ref
        self.github_api_url = GITHUB_REPO_URL
        
    def check_for_updates(self, show_no_update_message=False):
        try:
            response = requests.get(self.github_api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get('tag_name', '').lstrip('v')
                if latest_version and version.parse(latest_version) > version.parse(VERSION):
                    self.show_update_dialog(latest_version, data)
                elif show_no_update_message:
                    self.show_update_info_dialog("No Updates", f"You are on the latest version ({VERSION}).")
            elif show_no_update_message:
                self.show_update_error_dialog("Error", "Failed to check for updates.")
        except Exception as e:
            if show_no_update_message:
                self.show_update_error_dialog("Error", f"Could not connect to GitHub API:\n{str(e)}")

    def check_for_updates_on_startup(self):
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    def show_update_message_dialog(self, title, message, message_type='info'):
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QIcon
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        if message_type == 'info':
            msg.setIcon(QMessageBox.Information)
        else:
            msg.setIcon(QMessageBox.Critical)
        try:
            msg.setWindowIcon(QIcon(ICON_DIR))
        except:
            pass
        msg.exec()
    def show_update_info_dialog(self, title, message):
        self.show_update_message_dialog(title, message, 'info')
    def show_update_error_dialog(self, title, message):
        self.show_update_message_dialog(title, message, 'error')
    def show_update_dialog(self, latest_version, release_data):
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QIcon
        msg = QMessageBox()
        msg.setWindowTitle('Update Available')
        msg.setText(f'A new version ({latest_version}) is available!\n\nCurrent version: {VERSION}')
        
        body = release_data.get('body', 'No release notes provided.')
        msg.setInformativeText("Release Notes:\n\n" + body)
        msg.setStandardButtons(QMessageBox.Ok)
        
        try:
            msg.setWindowIcon(QIcon(ICON_DIR))
            msg.setIconPixmap(QIcon(ICON_DIR).pixmap(64, 64))
        except:
            msg.setIcon(QMessageBox.Information)
            
        msg.exec()
    def show_custom_info_dialog(self, title, message):
        self.show_update_info_dialog(title, message)
    def show_custom_error_dialog(self, title, message):
        self.show_update_error_dialog(title, message)

class SettingsManager:
    def __init__(self):

        self.settings_path = os.path.join(APPDATA_DIR, "settings.json")
        
        self.default_settings = {
            "source_language": "Japanese",
            "target_language": "Vietnamese",
            "active_translator": "google",
            "api_providers": {
                "google": {"api_key": "", "model": "gemini-2.5-flash", "temperature": 0.5, "max_tokens": 2000, "prompt": "Translate the {SOURCE_LANGUAGE} text to {TARGET_LANGUAGE}. Only return the translation."},
                "groq": {"api_key": "", "model": "meta-llama/llama-4-scout-17b-16e-instruct", "temperature": 0.5, "max_tokens": 2000, "prompt": "Translate the {SOURCE_LANGUAGE} text to {TARGET_LANGUAGE}. Only return the translation."},
                "openai": {"api_key": "", "model": "gpt-4o-mini", "temperature": 0.5, "max_tokens": 2000, "prompt": "Translate the {SOURCE_LANGUAGE} text to {TARGET_LANGUAGE}. Only return the translation."},
                "openrouter": {"api_key": "", "model": "nvidia/nemotron-nano-12b-v2-vl:free", "temperature": 0.5, "max_tokens": 2000, "prompt": "Translate the {SOURCE_LANGUAGE} text to {TARGET_LANGUAGE}. Only return the translation."},
                "togetherai": {"api_key": "", "model": "Qwen/Qwen3-VL-32B-Instruct", "temperature": 0.5, "max_tokens": 2000, "prompt": "Translate the {SOURCE_LANGUAGE} text to {TARGET_LANGUAGE}. Only return the translation."},
                "xai": {"api_key": "", "model": "grok-2-vision-1212", "temperature": 0.5, "max_tokens": 2000, "prompt": "Translate the {SOURCE_LANGUAGE} text to {TARGET_LANGUAGE}. Only return the translation."}
            },
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
            "auto_copy_clipboard": False,
            "auto_check_updates": True,
            "run_as_admin": True,
            "last_update_check": 0
        }
        self.settings = self.default_settings.copy()
        self.history = []
        self.load_settings()
        
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
            
    def save(self):
        return self.save_settings(self.settings)
        
    def get(self, key, default=None):
        val = self.get_setting(key)
        return val if val is not None else default
        
    def set(self, key, value):
        self.settings[key] = value

    def get_setting(self, key):
        return self.settings.get(key, self.default_settings.get(key))
        

class SettingsWindow(QWidget):
    def __init__(self, settings_manager, update_checker, apply_theme_callback=None):
        super().__init__()
        self.settings = settings_manager
        self.update_checker = update_checker
        self.apply_theme_callback = apply_theme_callback
        self.setWindowTitle("Settings")
        self.resize(800, 600)
        self.layout = QVBoxLayout(self)
        
        
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)
        
        self.tab_general = QWidget()
        self.tab_translators = QWidget()
        self.tab_display = QWidget()
        self.tab_history = QWidget()
        self.tab_about = QWidget()
        
        self.tabs.addTab(self.tab_general, "General")
        self.tabs.addTab(self.tab_translators, "Translators")
        self.tabs.addTab(self.tab_history, "History")
        self.tabs.addTab(self.tab_display, "Display")
        self.tabs.addTab(self.tab_about, "Suki :3")
        
        self.setup_general()
        self.setup_translators()
        self.setup_history()
        self.setup_display()
        self.setup_about()
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_settings)
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        self.layout.addLayout(btn_layout)
        
    def setup_general(self):
        lyt = QFormLayout(self.tab_general)
        
        hk_lyt = QHBoxLayout()
        self.capture_hk = HotkeyLineEdit(self.settings.get("capture_hotkey", "alt+q"))
        hk_lyt.addWidget(self.capture_hk)
        lyt.addRow("Hotkey:", hk_lyt)
        
        
        lang_lyt = QHBoxLayout()
        self.source_cb = QComboBox()
        self.source_cb.addItems(LANGUAGES)
        self.source_cb.setCurrentText(self.settings.get("source_language", "Japanese"))
        
        self.swap_btn = QPushButton("⮀")
        self.swap_btn.setFixedWidth(35)
        self.swap_btn.clicked.connect(self.swap_lang)
        
        self.target_cb = QComboBox()
        self.target_cb.addItems(LANGUAGES)
        self.target_cb.setCurrentText(self.settings.get("target_language", "Vietnamese"))
        
        lang_lyt.addWidget(self.source_cb)
        lang_lyt.addWidget(self.swap_btn)
        lang_lyt.addWidget(self.target_cb)
        
        lyt.addRow("Languages:", lang_lyt)
        
        self.admin_chk = QCheckBox("Run as Admin")
        self.admin_chk.setChecked(self.settings.get("run_as_admin", False))
        lyt.addRow("", self.admin_chk)
        
        self.startup_chk = QCheckBox("Run at startup")
        self.startup_chk.setChecked(self.settings.get("run_at_startup", False))
        lyt.addRow("", self.startup_chk)

        self.minimize_tray_chk = QCheckBox("Start minimized to system tray")
        self.minimize_tray_chk.setChecked(self.settings.get("minimize_to_tray", True))
        lyt.addRow("", self.minimize_tray_chk)

        self.auto_copy_chk = QCheckBox("Auto save Result Text to clipboard")
        self.auto_copy_chk.setChecked(self.settings.get("auto_copy_clipboard", False))
        lyt.addRow("", self.auto_copy_chk)

        self.auto_copy_img_chk = QCheckBox("Auto save Image to clipboard")
        self.auto_copy_img_chk.setChecked(self.settings.get("auto_copy_image", False))
        lyt.addRow("", self.auto_copy_img_chk)

        self.auto_update_chk = QCheckBox("Automatically check for updates")
        self.auto_update_chk.setChecked(self.settings.get("auto_check_updates", True))
        lyt.addRow("", self.auto_update_chk)

        update_lyt = QHBoxLayout()
        self.check_update_btn = QPushButton("Check for Updates Now")
        self.check_update_btn.clicked.connect(lambda: self.update_checker.check_for_updates(True))
        version_label = QLabel(f"Current version: {VERSION}")
        update_lyt.addWidget(self.check_update_btn)
        update_lyt.addWidget(version_label)
        update_lyt.addStretch()
        lyt.addRow("", update_lyt)
        
    def swap_lang(self):
        src = self.source_cb.currentText()
        tgt = self.target_cb.currentText()
        self.source_cb.setCurrentText(tgt)
        self.target_cb.setCurrentText(src)
        
    def setup_translators(self):
        lyt = QHBoxLayout(self.tab_translators)
        
        self.provider_list = QListWidget()
        self.providers = ["google", "groq", "openai", "openrouter", "togetherai", "xai"]
        self.provider_list.setMinimumWidth(120)
        self.provider_list.setMaximumWidth(150)
        
        active = self.settings.get("active_translator", "google")
        for p in self.providers:
            item = QListWidgetItem(p)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if p == active else Qt.Unchecked)
            self.provider_list.addItem(item)
        
        lyt.addWidget(self.provider_list)
        
        right_lyt = QVBoxLayout()
        form_lyt = QFormLayout()
        
        right_lyt.addSpacing(10)
        right_lyt.addWidget(QLabel("<b>Provider Settings</b>"))
        
        self.provider_prompt = QTextEdit()
        self.provider_prompt.setMinimumHeight(200)
        
        self.provider_api_key = QComboBox()
        self.provider_api_key.setEditable(True)
        self.provider_api_key.lineEdit().setEchoMode(QLineEdit.Password)
        
        self.btn_del_key = QPushButton("❌")
        self.btn_del_key.setToolTip("Delete selected API Key")
        self.btn_del_key.setFixedWidth(25)
        self.btn_del_key.clicked.connect(self.on_del_key_clicked)
        
        apiKey_lyt = QHBoxLayout()
        apiKey_lyt.setContentsMargins(0, 0, 0, 0)
        apiKey_lyt.addWidget(self.provider_api_key)
        apiKey_lyt.addWidget(self.btn_del_key)
        
        self.provider_model = QComboBox()
        self.provider_model.setEditable(True)
        
        self.btn_link_models = QPushButton("Models List")
        self.btn_link_models.setToolTip("Open provider's website to find available models")
        self.btn_link_models.setFixedWidth(75)
        self.btn_link_models.clicked.connect(self.on_link_models_clicked)
        
        model_lyt = QHBoxLayout()
        model_lyt.setContentsMargins(0, 0, 0, 0)
        model_lyt.addWidget(self.provider_model)
        model_lyt.addWidget(self.btn_link_models)
        
        self.provider_temp = QDoubleSpinBox()
        self.provider_temp.setRange(0.0, 2.0)
        self.provider_temp.setSingleStep(0.1)
        self.provider_tokens = QSpinBox()
        self.provider_tokens.setRange(1, 128000)
        self.provider_tokens.setSingleStep(100)
        
        form_lyt.addRow("API Key:", apiKey_lyt)
        form_lyt.addRow("Model:", model_lyt)
        
        vision_note = QLabel("<i>Note: Ensure the custom model supports Vision (Image) input!</i>")
        vision_note.setStyleSheet("color: #aaa; font-size: 11px;")
        form_lyt.addRow("", vision_note)
        
        form_lyt.addRow("Temperature:", self.provider_temp)
        form_lyt.addRow("Max Tokens:", self.provider_tokens)
        form_lyt.addRow("Prompt:", self.provider_prompt)
        
        right_lyt.addLayout(form_lyt)
        right_lyt.addStretch()
        
        lyt.addLayout(right_lyt)
        
        self.provider_list.currentItemChanged.connect(self.on_provider_selected)
        self.provider_list.itemChanged.connect(self.on_provider_checked)
        
        self.current_provider_editing = None
        idx = self.providers.index(active) if active in self.providers else 0
        self.provider_list.setCurrentRow(idx)

    def on_link_models_clicked(self):
        provider_name = self.providers[self.provider_list.currentRow()]
        links = {
            "google": "https://ai.google.dev/gemini-api/docs/models",
            "groq": "https://console.groq.com/settings/limits",
            "openai": "https://developers.openai.com/api/docs/pricing",
            "openrouter": "https://openrouter.ai/models",
            "togetherai": "https://api.together.ai/models",
            "xai": "https://console.x.ai/"
        }
        url = links.get(provider_name)
        if url:
            webbrowser.open(url)
        else:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", f"No link available for {provider_name}.")

    def on_provider_selected(self, current, previous):
        if previous:
            prev_name = previous.text()
            self.save_current_provider_to_memory(prev_name)
            
        if current:
            curr_name = current.text()
            self.load_provider_to_ui(curr_name)
            self.current_provider_editing = curr_name
            
    def on_provider_checked(self, item):
        if item.checkState() == Qt.Checked:
            
            self.provider_list.blockSignals(True)
            for i in range(self.provider_list.count()):
                other = self.provider_list.item(i)
                if other != item:
                    other.setCheckState(Qt.Unchecked)
            self.provider_list.blockSignals(False)
            self.settings.set("active_translator", item.text())
        else:
            
            self.provider_list.blockSignals(True)
            item.setCheckState(Qt.Checked)
            self.provider_list.blockSignals(False)

    def on_del_key_clicked(self):
        idx = self.provider_api_key.currentIndex()
        if idx >= 0:
            provider_name = self.providers[self.provider_list.currentRow()]
            real_key = self.provider_api_key.itemData(idx)
            
            history_key = f"{provider_name}_api_keys"
            keys_history = self.settings.get(history_key, [])
            if real_key in keys_history:
                keys_history.remove(real_key)
                self.settings.set(history_key, keys_history)
                
            self.provider_api_key.removeItem(idx)

    def save_current_provider_to_memory(self, provider_name):
        api_providers = self.settings.get("api_providers", {}).copy()
        
        current_text = self.provider_api_key.currentText().strip()
        real_key = current_text
        for i in range(self.provider_api_key.count()):
            if self.provider_api_key.itemText(i) == current_text:
                if self.provider_api_key.itemData(i):
                    real_key = self.provider_api_key.itemData(i)
                break

        current_model = self.provider_model.currentText().strip()
        
        if provider_name in api_providers:
            api_providers[provider_name]["prompt"] = self.provider_prompt.toPlainText()
            api_providers[provider_name]["api_key"] = real_key
            api_providers[provider_name]["model"] = current_model
            api_providers[provider_name]["temperature"] = self.provider_temp.value()
            api_providers[provider_name]["max_tokens"] = self.provider_tokens.value()
        self.settings.set("api_providers", api_providers)
        
        if real_key:
            history_key = f"{provider_name}_api_keys"
            keys_history = self.settings.get(history_key, [])
            if real_key in keys_history:
                keys_history.remove(real_key)
            keys_history.insert(0, real_key)
            self.settings.set(history_key, keys_history[:10])

    def load_provider_to_ui(self, provider_name):
        self.provider_model.clear()
            
        
        self.provider_api_key.clear()
        history_key = f"{provider_name}_api_keys"
        keys_history = self.settings.get(history_key, [])
        for k in keys_history:
            if not k: continue
            masked = k[:10] + "•" * min(15, max(3, len(k)-10)) if len(k) > 10 else "•••"
            self.provider_api_key.addItem(masked, k)
            
        api_providers = self.settings.get("api_providers", {})
        if provider_name in api_providers:
            p_conf = api_providers[provider_name]
            self.provider_prompt.setPlainText(p_conf.get("prompt", ""))
            
            saved_key = p_conf.get("api_key", "")
            if saved_key:
                masked_saved = saved_key[:10] + "•" * min(15, max(3, len(saved_key)-10)) if len(saved_key) > 10 else "•••"
                self.provider_api_key.setCurrentText(masked_saved)
            else:
                self.provider_api_key.setCurrentIndex(-1)
                
            saved_model = p_conf.get("model", "")
            if saved_model:
                self.provider_model.setCurrentText(saved_model)
            else:
                self.provider_model.setCurrentIndex(0 if self.provider_model.count() > 0 else -1)
                
            self.provider_temp.setValue(p_conf.get("temperature", 0.5))
            self.provider_tokens.setValue(p_conf.get("max_tokens", 2000))
        else:
            self.provider_prompt.clear()
            self.provider_api_key.setCurrentIndex(-1)
            self.provider_model.setCurrentIndex(0 if self.provider_model.count() > 0 else -1)
            self.provider_temp.setValue(0.5)
            self.provider_tokens.setValue(2000)

    def setup_display(self):
        lyt = QFormLayout(self.tab_display)
        
        self.font_cb = QFontComboBox()
        self.font_cb.setCurrentFont(QFont(self.settings.get("result_font", "Arial")))
        lyt.addRow("Font Name:", self.font_cb)
        
        self.font_size_sp = QSpinBox()
        self.font_size_sp.setRange(8, 72)
        self.font_size_sp.setValue(self.settings.get("result_font_size", 12))
        lyt.addRow("Font Size:", self.font_size_sp)
        
        self.font_cb.currentFontChanged.connect(self.update_sample_font)
        self.font_size_sp.valueChanged.connect(self.update_sample_font)
        
        color_lyt = QHBoxLayout()
        self.font_color_btn = QPushButton()
        self.font_color_btn.setFixedSize(30, 15)
        self.font_color_btn.setStyleSheet(f"background-color: {self.settings.get('custom_font_color', '#db9aaa')}; border: 1px solid black;")
        self.font_color_btn.clicked.connect(lambda: self.pick_color('custom_font_color', self.font_color_btn))
        color_lyt.addWidget(self.font_color_btn)
        
        self.stroke_chk = QCheckBox("Stroke:")
        self.stroke_chk.setChecked(self.settings.get("use_stroke", True))
        self.stroke_chk.stateChanged.connect(self.toggle_stroke)
        color_lyt.addWidget(self.stroke_chk)
        
        self.stroke_color_btn = QPushButton()
        self.stroke_color_btn.setFixedSize(30, 15)
        self.stroke_color_btn.setStyleSheet(f"background-color: {self.settings.get('custom_stroke_color', '#000000')}; border: 1px solid black;")
        self.stroke_color_btn.clicked.connect(lambda: self.pick_color('custom_stroke_color', self.stroke_color_btn))
        color_lyt.addWidget(self.stroke_color_btn)
        color_lyt.addStretch()
        lyt.addRow("Font Color:", color_lyt)
        self.bg_color_widget = QWidget()
        bg_lyt = QHBoxLayout(self.bg_color_widget)
        bg_lyt.setContentsMargins(0,0,0,0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedSize(30, 15)
        self.bg_color_btn.setStyleSheet(f"background-color: {self.settings.get('custom_bg_color', '#000000')}; border: 1px solid black;")
        self.bg_color_btn.clicked.connect(lambda: self.pick_color('custom_bg_color', self.bg_color_btn))
        bg_lyt.addWidget(self.bg_color_btn)
        bg_lyt.addStretch()
        lyt.addRow("Background Color:", self.bg_color_widget)
        
        lyt.addRow(QLabel("Background Color Mode:"))
        self.bg_mode_grp = QButtonGroup(self)
        self.mode_manual = QRadioButton("Manual")
        self.mode_auto = QRadioButton("Auto")
        self.mode_blur = QRadioButton("Blur")
        self.bg_mode_grp.addButton(self.mode_manual, 1)
        self.bg_mode_grp.addButton(self.mode_auto, 2)
        self.bg_mode_grp.addButton(self.mode_blur, 3)
        
        mode_lyt = QHBoxLayout()
        mode_lyt.addWidget(self.mode_manual)
        mode_lyt.addWidget(self.mode_auto)
        mode_lyt.addWidget(self.mode_blur)
        lyt.addRow("", mode_lyt)
        
        self.sample_input = QLineEdit(self.settings.get("sample_text", "Suki loves boba, naps, and head scratches UwU"))
        self.sample_input.textChanged.connect(self.update_sample_text)
        lyt.addRow("Preview Text:", self.sample_input)
        
        self.preview_container = PreviewContainer()
        self.preview_container.mock_text = self.sample_input.text()
        self.preview_container.setMinimumHeight(60)
        p_lyt = QVBoxLayout(self.preview_container)
        p_lyt.setContentsMargins(5, 5, 5, 5)
        self.sample_text = StrokeLabel(self.sample_input.text())
        self.sample_text.setAlignment(Qt.AlignCenter)
        p_lyt.addWidget(self.sample_text)
        lyt.addRow(self.preview_container)
        
        font = QFont(self.settings.get("result_font", "Arial"), self.settings.get("result_font_size", 12))
        self.sample_text.setFont(font)
        self.preview_container.mock_font = font
        self.preview_container.font_color = self.settings.get('custom_font_color', '#db9aaa')
        self.preview_container.stroke_color = self.settings.get('custom_stroke_color', '#000000')
        self.preview_container.use_stroke = self.settings.get('use_stroke', True)
        
        
        self.mode_manual.toggled.connect(self.update_preview_bg)
        self.mode_auto.toggled.connect(self.update_preview_bg)
        self.mode_blur.toggled.connect(self.update_preview_bg)
        
        
        mode = self.settings.get("display_mode", "manual")
        if mode == "auto": self.mode_auto.setChecked(True)
        elif mode == "blur": self.mode_blur.setChecked(True)
        else:
            self.mode_manual.setChecked(True)
            self.update_preview_bg()  
        
    def update_sample_font(self):
        font = self.font_cb.currentFont()
        font.setPointSize(self.font_size_sp.value())
        self.sample_text.setFont(font)
        self.preview_container.mock_font = font
        self.preview_container.update()
        
    def update_sample_text(self, text):
        self.sample_text.setText(text)
        self.preview_container.mock_text = text
        self.preview_container.update()
        
    def update_preview_bg(self):
        if not hasattr(self, 'sample_text'):
            return
        use_stroke = self.settings.get("use_stroke", True)
        self.sample_text.setStrokeWidth(1 if use_stroke else 0)
        
        fc = self.settings.get('custom_font_color', '#db9aaa')
        sc = self.settings.get('custom_stroke_color', '#000000')
        
        if self.mode_manual.isChecked():
            self.bg_color_widget.show()
            self.preview_container.mode = "manual"
            self.preview_container.manual_bg = self.settings.get('custom_bg_color', '#000000')
        else:
            self.bg_color_widget.hide()
            if self.mode_auto.isChecked():
                self.preview_container.mode = "auto"
            else:
                self.preview_container.mode = "blur"
        
        self.preview_container.font_color = fc
        self.preview_container.stroke_color = sc
        self.preview_container.use_stroke = use_stroke
        self.preview_container.update()
        self.sample_text.setStyleSheet(f"color: {fc}; background: transparent;")
        self.sample_text.setStrokeColor(sc)

    def setup_history(self):
        lyt = QVBoxLayout(self.tab_history)
        
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_content = QWidget()
        self.history_layout = QVBoxLayout(self.history_content)
        self.history_layout.setAlignment(Qt.AlignTop)
        
        self.history_scroll.setWidget(self.history_content)
        lyt.addWidget(self.history_scroll)
        
        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.clicked.connect(self.clear_history)
        lyt.addWidget(self.clear_history_btn)
        
    def clear_history(self):
        self.settings.history = []
        self.update_history()
        
    def update_history(self):
        while self.history_layout.count():
            child = self.history_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        for item in reversed(self.settings.history):
            card = QFrame()
            card.setFrameShape(QFrame.StyledPanel)
            c_lyt = QHBoxLayout(card)
            
            img_lbl = QLabel()
            import io
            output = io.BytesIO()
            item["image"].convert("RGB").save(output, "PNG")
            pixmap = QPixmap()
            pixmap.loadFromData(output.getvalue(), "PNG")
            img_lbl.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            img_lbl.setFixedSize(160, 160)
            img_lbl.setAlignment(Qt.AlignCenter)
            
            text_edit = QTextEdit()
            text_edit.setPlainText(item["text"])
            text_edit.setReadOnly(True)
            text_edit.setMaximumHeight(150)
            
            btn_lyt = QVBoxLayout()
            copy_txt_btn = QPushButton("Copy Text")
            copy_txt_btn.clicked.connect(lambda _, t=item["text"]: copy_translated_text(t))
            copy_img_btn = QPushButton("Copy Image")
            copy_img_btn.clicked.connect(lambda _, i=item["image"]: copy_image(i))
            
            btn_lyt.addWidget(copy_txt_btn)
            btn_lyt.addWidget(copy_img_btn)
            btn_lyt.addStretch()
            
            c_lyt.addWidget(img_lbl)
            c_lyt.addWidget(text_edit)
            c_lyt.addLayout(btn_lyt)
            
            self.history_layout.addWidget(card)

    def pick_color(self, setting_name, btn):
        current = self.settings.get(setting_name, "#ffffff")
        color = QColorDialog.getColor(QColor(current), self, "Select Color")
        if color.isValid():
            hex_color = color.name()
            self.settings.set(setting_name, hex_color)
            btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid black;")
            self.update_preview_bg()
            
    def toggle_stroke(self):
        self.settings.set("use_stroke", self.stroke_chk.isChecked())
        self.update_preview_bg()

    def setup_about(self):
        layout = QVBoxLayout(self.tab_about)
        
        lbl_title = QLabel(APP_NAME)
        lbl_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel("Translate anything on your screen.")
        lbl_desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_desc)
        
        lbl_version = QLabel(f"Version: {VERSION}")
        lbl_version.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_version)
        
        def create_link_row(label_text, link_text, url):
            row = QHBoxLayout()
            row.addStretch()
            if label_text:
                lbl = QLabel(label_text)
                row.addWidget(lbl)
            
            link = QLabel(f'<a href="{url}" style="color: #db9aaa; text-decoration: none;">{link_text}</a>')
            link.setOpenExternalLinks(True)
            row.addWidget(link)
            row.addStretch()
            layout.addLayout(row)
            
        create_link_row("Author: ", "Suki", "https://github.com/Suki8898")
        create_link_row("Support: ", "Buymeacoffee", "https://buymeacoffee.com/suki8898")
        create_link_row("License: ", "MIT", "https://github.com/Suki8898/SukiTranslate/blob/main/LICENSE")

        
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignCenter)
        
        links = [
            ("github.png", "https://github.com/Suki8898"),
            ("discord.png", "https://discord.com/users/494332657098817557"),
            ("facebook.png", "https://www.facebook.com/suki8898/"),
            ("tiktok.png", "https://www.tiktok.com/@suki8898"),
            ("youtube.png", "https://www.youtube.com/suki8898")
        ]
        
        for icon_file, url in links:
            icon_path = os.path.join(PROJECT_DIR, "icons", icon_file).replace("\\", "/")
            if os.path.exists(icon_path):
                lbl_icon = QLabel()
                
                lbl_icon.setText(f'<a href="{url}"><img src="{icon_path}" width="24" height="24"></a>')
                lbl_icon.setOpenExternalLinks(True)
                icon_layout.addWidget(lbl_icon)
                
        layout.addLayout(icon_layout)
        
        
        image_path = os.path.join(PROJECT_DIR, "Suki UwU", "Suki.png")
        if os.path.exists(image_path):
            lbl_img = QLabel()
            original_pixmap = QPixmap(image_path)
            if not original_pixmap.isNull():
                
                scaled_pixmap = original_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                rounded = QPixmap(scaled_pixmap.size())
                rounded.fill(Qt.transparent)
                
                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                
                path.addRoundedRect(QRectF(0, 0, scaled_pixmap.width(), scaled_pixmap.height()), 20, 20)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, scaled_pixmap)
                painter.end()
                
                lbl_img.setPixmap(rounded)
                lbl_img.setAlignment(Qt.AlignCenter)
                layout.addWidget(lbl_img)
                
        layout.addStretch()
        
    def save_settings(self):
        self.settings.set("source_language", self.source_cb.currentText())
        self.settings.set("target_language", self.target_cb.currentText())
        self.settings.set("run_as_admin", self.admin_chk.isChecked())
        
        self.settings.set("run_at_startup", self.startup_chk.isChecked())
        set_startup(self.startup_chk.isChecked())
        
        self.settings.set("auto_copy_clipboard", self.auto_copy_chk.isChecked())
        self.settings.set("auto_copy_image", self.auto_copy_img_chk.isChecked())
        self.settings.set("auto_check_updates", self.auto_update_chk.isChecked())
        self.settings.set("minimize_to_tray", self.minimize_tray_chk.isChecked())
        
        if self.current_provider_editing:
            self.save_current_provider_to_memory(self.current_provider_editing)
            
        self.settings.set("capture_hotkey", self.capture_hk.text())
        
        self.settings.set("result_font", self.font_cb.currentFont().family())
        self.settings.set("result_font_size", self.font_size_sp.value())
        if self.mode_auto.isChecked(): self.settings.set("display_mode", "auto")
        elif self.mode_blur.isChecked(): self.settings.set("display_mode", "blur")
        else: self.settings.set("display_mode", "manual")
        self.settings.set("sample_text", self.sample_input.text())
        self.settings.set("use_stroke", self.stroke_chk.isChecked())
        
        self.settings.save()
        if self.apply_theme_callback:
            self.apply_theme_callback()
        
        main_window = self.window()
        if hasattr(main_window, 'bind_hotkeys'):
            main_window.bind_hotkeys()
        
        font = QFont(self.settings.get("result_font", "Arial"), self.settings.get("result_font_size", 12))
        self.sample_text.setFont(font)
        self.window().hide()

class StrokeLabel(QLabel):
    def __init__(self, text=""):
        super().__init__(text)
        self.stroke_color = QColor(0, 0, 0)
        self.stroke_width = 1

    def setStrokeColor(self, color_hex):
        self.stroke_color = QColor(color_hex)
        self.update()
        
    def setStrokeWidth(self, width):
        self.stroke_width = width
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        
        pen = painter.pen()
        flags = int(self.alignment() | Qt.TextWordWrap)
        
        crect = self.contentsRect()
        
        if self.stroke_width > 0:
            painter.setPen(self.stroke_color)
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)]:
                painter.drawText(crect.translated(dx * self.stroke_width, dy * self.stroke_width), flags, self.text())
            
        painter.setPen(pen)
        painter.drawText(crect, flags, self.text())
        
class PreviewContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.mode = "manual"
        self.manual_bg = "#000000"
        self.mock_text = ""
        self.mock_font = None
        self.font_color = "#db9aaa"
        self.stroke_color = "#000000"
        self.use_stroke = True
        
    def paintEvent(self, event):
        from PySide6.QtGui import QPainter, QColor, QFont, QImage
        from PySide6.QtCore import Qt
        painter = QPainter(self)
        painter.setRenderHint(QPainter.TextAntialiasing)
        flags = int(Qt.AlignCenter | Qt.TextWordWrap)
        
        if self.mode == "blur":
            
            img = QImage(self.size(), QImage.Format_ARGB32)
            img.fill(QColor("#2E2E2E"))
            p = QPainter(img)
            p.setRenderHint(QPainter.TextAntialiasing)
            if self.mock_font:
                p.setFont(self.mock_font)
            sc = QColor(self.stroke_color)
            if self.use_stroke:
                p.setPen(sc)
                for dx, dy in [(-1,-1),(1,-1),(-1,1),(1,1)]:
                    p.drawText(self.rect().translated(dx, dy), flags, self.mock_text)
            p.setPen(QColor(self.font_color))
            p.drawText(self.rect(), flags, self.mock_text)
            p.end()
            
            w, h = max(1, img.width() // 8), max(1, img.height() // 8)
            small = img.scaled(w, h, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            blurred = small.scaled(img.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            painter.drawImage(0, 0, blurred)
        elif self.mode == "auto":
            painter.fillRect(self.rect(), QColor("#2E2E2E"))
        else:
            painter.fillRect(self.rect(), QColor(self.manual_bg))
        
        super().paintEvent(event)
        
class ResultWindow(QWidget):
    def __init__(self, settings, auto_bg_color=None, img=None):
        super().__init__()
        self.settings = settings
        self.img = img
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.NoDropShadowWindowHint)
        
        mode = settings.get("display_mode", "manual")
        bg_color = settings.get("custom_bg_color", "#000000")
        if mode == "auto" and auto_bg_color:
            bg_color = auto_bg_color
            
        if mode == "blur" and sys.platform == "win32":
            self.setAttribute(Qt.WA_TranslucentBackground, True)
            self.setStyleSheet("background: rgba(0, 0, 0, 1); border: none;")
            self._blur_bg = True
        else:
            self._blur_bg = False
            self.setStyleSheet(f"background-color: {bg_color}; border: none;")
                
        self.layout = QVBoxLayout(self)
        self.label = StrokeLabel("")
        font = QFont(settings.get("result_font", "Arial"), settings.get("result_font_size", 12))
        self.label.setFont(font)
        self.label.setStyleSheet(f"color: {settings.get('custom_font_color', '#db9aaa')}; padding: 3px 3px 0px 3px; background: transparent;")
        self.label.setStrokeColor(settings.get("custom_stroke_color", "#000000"))
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.label.setWordWrap(True)
        
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.label)
        
        
        
    def update_text(self, text):
        use_stroke = self.settings.get("use_stroke", True)
        self.label.setStrokeWidth(1 if use_stroke else 0)
        self.label.setText(text)
        
        fm = self.label.fontMetrics()
        min_w = self.minimumWidth()
        min_h = self.minimumHeight()
        
        
        screen = QApplication.screenAt(self.pos()) or QApplication.primaryScreen()
        screen_geo = screen.geometry() if screen else QRect(0,0,1920,1080)
        max_allowed_w = int(screen_geo.width() * 0.6)
        
        
        final_w = min_w
        
        
        
        words = text.split()
        max_word_w = 0
        for word in words:
            word_w = fm.boundingRect(0, 0, 10000, 10000, Qt.TextSingleLine, word).width() + 40
            if word_w > max_word_w:
                max_word_w = word_w
        
        
        if max_word_w > final_w:
            final_w = min(max_word_w, max_allowed_w)
        
        
        wrapped_rect = fm.boundingRect(0, 0, final_w - 40, 10000, Qt.TextWordWrap, text)
        text_h = wrapped_rect.height() + 10
        
        final_h = max(min_h, text_h)
        
        self.setFixedSize(max(final_w, 10), max(final_h, 0))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pass

    def contextMenuEvent(self, event):
        self._menu_open = True
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { 
                background-color: #2b2b2b; color: #ffffff; border: 1px solid #555; 
                min-width: 125px; padding: 4px; 
            }
            QMenu::item { padding: 6px 20px 6px 20px; }
            QMenu::item:selected { background-color: #555555; }
        """)
        copy_action = menu.addAction("Copy Result Text")
        copy_action.triggered.connect(lambda: copy_translated_text(self.label.text()))
        if self.img:
            copy_img_action = menu.addAction("Copy Image")
            copy_img_action.triggered.connect(lambda: copy_image(self.img))
        
        menu.aboutToHide.connect(lambda: setattr(self, '_menu_open', False))
        menu.exec(event.globalPos())

    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.ActivationChange:
            if not getattr(self, '_menu_open', False):
                if QApplication.activeWindow() is not self:
                    self.hide()

    def showEvent(self, ev):
        super().showEvent(ev)
        if self._blur_bg:
            try:
                from ctypes import windll, c_int, byref, Structure, sizeof
                class ACCENTPOLICY(Structure):
                    _fields_ = [
                        ("AccentState", c_int),
                        ("AccentFlags", c_int),
                        ("GradientColor", c_int),
                        ("AnimationId", c_int)
                    ]
                class WINDOWCOMPOSITIONATTRIBDATA(Structure):
                    _fields_ = [
                        ("Attribute", c_int),
                        ("Data", ctypes.POINTER(c_int)),
                        ("SizeOfData", c_int)
                    ]
                accent = ACCENTPOLICY()
                accent.AccentState = 3  
                accent.AccentFlags = 0   
                accent.GradientColor = 0  
                
                data = WINDOWCOMPOSITIONATTRIBDATA()
                data.Attribute = 19     
                data.SizeOfData = sizeof(accent)
                data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(c_int))
                
                windll.user32.SetWindowCompositionAttribute(int(self.winId()), byref(data))
            except Exception as e:
                print(f"Blur error: {e}")
        self.activateWindow()
        self.setFocus()

    def paintEvent(self, event):
        if getattr(self, '_blur_bg', False):
            painter = QPainter(self)
            painter.setBrush(QColor(1, 1, 1, 1))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())
        super().paintEvent(event)

class ScreenCaptureOverlay(QWidget):
    capture_finished = Signal(int, int, int, int)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setCursor(Qt.CrossCursor)
        
        self.start_pos = None
        self.current_pos = None
        
    def showEvent(self, event):
        self.start_pos = None
        self.current_pos = None
        super().showEvent(event)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))
        
        pen = painter.pen()
        pen.setColor(QColor(255, 255, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawRect(self.rect())
        
        if self.start_pos and self.current_pos:
            rect = QRectF(self.start_pos, self.current_pos).normalized()
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QColor(255, 255, 255))
            painter.drawRect(rect)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.position()
            self.current_pos = self.start_pos
        elif event.button() == Qt.RightButton:
            self.start_pos = None
            self.current_pos = None
            self.hide()
            
    def mouseMoveEvent(self, event):
        if self.start_pos:
            self.current_pos = event.position()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.start_pos:
            rect = QRectF(self.start_pos, self.current_pos).normalized()
            self.hide()
            QApplication.processEvents()
            
            x, y, w, h = int(self.geometry().x() + rect.x()), int(self.geometry().y() + rect.y()), int(rect.width()), int(rect.height())
            QTimer.singleShot(20, lambda: self.capture_finished.emit(x, y, w, h))
            
class TranslationThread(QThread):
    finished = Signal(str)
    error_signal = Signal(str)
    
    def __init__(self, image, settings):
        super().__init__()
        self.image = image
        self.settings = settings
        
    def run(self):
        try:
            active_provider = self.settings.get("active_translator")
            if not active_provider:
                raise Exception("No provider enabled.")
            
            providers_config = self.settings.get("api_providers", {}).get(active_provider)
            if not providers_config:
                raise Exception("Provider config missing.")
                
            api_key = providers_config.get("api_key", "")
            if not api_key:
                raise Exception(f"API Key missing for {active_provider}")
                
            model = providers_config.get("model", "")
            prompt_template = providers_config.get("prompt", "")
            temp = float(providers_config.get("temperature", 0.5))
            max_tokens = int(providers_config.get("max_tokens", 2000))
            
            source_lang = self.settings.get("source_language", "Japanese")
            target_lang = self.settings.get("target_language", "Vietnamese")
            
            prompt = prompt_template.replace("{TARGET_LANGUAGE}", target_lang).replace("{SOURCE_LANGUAGE}", source_lang)
            prompt = prompt.replace("SourceLang", source_lang).replace("TargetLang", target_lang)
            
            output = io.BytesIO()
            self.image.save(output, format="PNG")
            image_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
            
            if active_provider == "google":
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                payload = {
                    "system_instruction": {"parts": [{"text": prompt}]},
                    "contents": {"parts": [{"inlineData": {"mimeType": "image/png", "data": image_base64}}]},
                    "generationConfig": {"temperature": temp, "maxOutputTokens": max_tokens},
                    "safetySettings": [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                }
                
                print(f"[LOG] Sending request to {active_provider}...")
                print(f"[LOG] Model: {model}")
                print(f"[LOG] Payload (partial): system_instruction={prompt}")
                
                res = requests.post(url, json=payload)
                res.raise_for_status()
                data = res.json()
                
                resp_str = json.dumps(data, ensure_ascii=False)
                print(f"[LOG] Received response from {active_provider}: {resp_str[:500]}...")
                text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
                if not text:
                    raise Exception("No translated text returned.")
                self.finished.emit(text)
                
            else:
                urls = {
                    "groq": "https://api.groq.com/openai/v1/chat/completions",
                    "openai": "https://api.openai.com/v1/chat/completions",
                    "openrouter": "https://openrouter.ai/api/v1/chat/completions",
                    "togetherai": "https://api.together.xyz/v1/chat/completions",
                    "xai": "https://api.x.ai/v1/chat/completions"
                }
                url = urls.get(active_provider)
                payload = {
                    "model": model,
                    "temperature": temp,
                    "max_tokens": max_tokens,
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}]}
                    ]
                }
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                if active_provider == "openrouter":
                    headers["HTTP-Referer"] = "https://github.com/Suki8898/SukiTranslate"
                    headers["X-Title"] = "Suki Translate"
                
                print(f"[LOG] Sending request to {active_provider}...")
                print(f"[LOG] Model: {model}")
                msg_str = json.dumps(payload['messages'], ensure_ascii=False)
                print(f"[LOG] Payload (messages): {msg_str[:300]}...")
                    
                res = requests.post(url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                
                resp_str = json.dumps(data, ensure_ascii=False)
                print(f"[LOG] Received response from {active_provider}: {resp_str[:500]}...")
                text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                self.finished.emit(text)
                
        except Exception as e:
            self.error_signal.emit(str(e))

class SukiTranslateApp(QMainWindow):
    capture_signal = Signal()
    
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.update_checker = UpdateChecker()
        self.settings_window = SettingsWindow(self.settings, self.update_checker)
        
        self.setWindowTitle("Suki Translate")
        if os.path.exists(ICON_DIR):
            self.setWindowIcon(QIcon(ICON_DIR))
            
        self.setCentralWidget(self.settings_window)
        
        self.capture_signal.connect(self.start_capture)
        self.setup_tray()
        self.bind_hotkeys()
        
        self.capture_overlay = ScreenCaptureOverlay()
        self.capture_overlay.capture_finished.connect(self.on_capture_finished)
        
        self.result_window = None
        
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        
    def fetch_models_in_background(self):
        def _fetch():
            try:
                url = "https://raw.githubusercontent.com/Suki8898/SukiTranslate/main/models.json"
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    data = resp.json()
                    self.settings.set("cached_vision_models", data)
                    self.settings.save()
            except Exception as e:
                print("Failed to fetch dynamic models list:", e)
        threading.Thread(target=_fetch, daemon=True).start()

    def setup_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        icon_path = ICON_DIR if os.path.exists(ICON_DIR) else ""
        if icon_path:
            self.tray_icon.setIcon(QIcon(icon_path))
            
        tray_menu = QMenu()
        
        
        settings_action = tray_menu.addAction("Settings")
        settings_action.triggered.connect(self.showNormal)
        
        
        log_action = tray_menu.addAction("Open Log")
        log_action.triggered.connect(lambda: os.startfile(LOG_FILE) if os.path.exists(LOG_FILE) else None)
        
        
        quit_action = tray_menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def bind_hotkeys(self):
        try:
            keyboard.remove_all_hotkeys()
        except AttributeError:
            pass
        hk = self.settings.get("capture_hotkey", "alt+q")
        try:
            keyboard.add_hotkey(hk, lambda: self.capture_signal.emit())
            print(f"[LOG] Hotkey bound: {hk}")
        except Exception as e:
            print("Hotkey error:", e)
            
    def start_capture(self):
        
        if self.result_window:
            self.result_window.hide()
            self.result_window.deleteLater()
            self.result_window = None
            
        if self.capture_overlay:
            self.capture_overlay.hide()
            self.capture_overlay.deleteLater()
        
        self.capture_overlay = ScreenCaptureOverlay()
        self.capture_overlay.capture_finished.connect(self.on_capture_finished)
        
        desktop_rect = QRect()
        for screen in QApplication.screens():
            desktop_rect = desktop_rect.united(screen.geometry())
            
        self.capture_overlay.setGeometry(desktop_rect)
        self.capture_overlay.show()
        self.capture_overlay.activateWindow()
        
    def on_capture_finished(self, x, y, w, h):
        if w <= 10 or h <= 10: 
            print(f"Capture area too small: {w}x{h}")
            return
        
        try:
            with mss.mss() as sct:
                monitor = {"left": int(x), "top": int(y), "width": int(w), "height": int(h)}
                grabbed = sct.grab(monitor)
                img = Image.frombytes("RGB", (grabbed.width, grabbed.height), grabbed.bgra, "raw", "BGRX")
                
            
            small_img = img.resize((64, 64), Image.Resampling.NEAREST)
            colors = small_img.getcolors(64 * 64)
            if colors:
                colors.sort(key=lambda c: c[0], reverse=True)
                dominant = colors[0][1]
            else:
                dominant = (0, 0, 0)
            auto_bg_color = f"#{dominant[0]:02x}{dominant[1]:02x}{dominant[2]:02x}"
                
            print(f"Captured area at {x}, {y} size {w}x{h}")
        
            if self.settings.get("auto_copy_image", False):
                try:
                    copy_image(img)
                    print("[LOG] Image auto-copied to clipboard.")
                except Exception as e:
                    print(f"[LOG] Failed to auto-copy image: {e}")
        
            if self.result_window:
                try:
                    self.result_window.hide()
                    self.result_window.deleteLater()
                except:
                    pass
                self.result_window = None
            
            self.last_capture_x = int(x)
            self.last_capture_y = int(y)
            self.last_capture_w = int(w)
            self.last_capture_h = int(h)
            self.last_capture_bg = auto_bg_color
            
            self.translation_thread = TranslationThread(img, self.settings)
            self.translation_thread.finished.connect(self.on_translation_success)
            self.translation_thread.error_signal.connect(self.on_translation_error)
            self.translation_thread.start()
            
        except Exception as e:
            print(f"Capture process error: {e}")
            import traceback
            traceback.print_exc()
            
    def show_result_window(self, text):
        if self.result_window:
            try:
                self.result_window.hide()
                self.result_window.deleteLater()
            except:
                pass
        self.result_window = ResultWindow(self.settings, self.last_capture_bg, self.translation_thread.image)
        self.result_window.setMinimumWidth(self.last_capture_w)
        self.result_window.setMinimumHeight(self.last_capture_h)
        self.result_window.update_text(text)
        
        w = max(1, self.result_window.width())
        h = max(1, self.result_window.height())
        screen = QApplication.screenAt(QPoint(self.last_capture_x, self.last_capture_y))
        
        if screen:
            rect = screen.geometry()
            x = max(rect.left(), min(self.last_capture_x, rect.right() - w))
            y = max(rect.top(), min(self.last_capture_y, rect.bottom() - h))
        else:
            x, y = self.last_capture_x, self.last_capture_y
            
        self.result_window.move(x, y)
        self.result_window.show()
        
    def on_translation_success(self, text):
        self.settings.history.append({"image": self.translation_thread.image, "text": text})
        if len(self.settings.history) > 50:
            self.settings.history.pop(0)
        self.settings_window.update_history()
        
        if self.settings.get("auto_copy_clipboard", False):
            try:
                copy_translated_text(text)
                print("[LOG] Text auto-copied to clipboard.")
            except Exception as e:
                print(f"[LOG] Failed to auto-copy text: {e}")
                
        self.show_result_window(text)
        
    def on_translation_error(self, error):
        self.show_result_window(f"Error: {error}")
        
    def quit_app(self):
        QApplication.quit()

if __name__ == "__main__":
    print("Starting app...")
    try:
        if is_already_running():
            print("Already running, exiting.")
            sys.exit(0)
    except Exception as e:
        print("Error in is_already_running:", e)
        
    print("Creating QApplication...")
    app = QApplication(sys.argv)
    print("Creating main window...")
    try:
        window = SukiTranslateApp()
        print("Main window created.")
    except Exception as e:
        print("Error creating SukiTranslateApp:")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    print("Checking minimize_to_tray...")
    try:
        if not window.settings.get("minimize_to_tray", True):
            print("Showing window...")
            window.show()
        else:
            print("Minimized to tray.")
    except Exception as e:
        print("Error getting setting:", e)
        
    print("Executing app...")
    sys.exit(app.exec())

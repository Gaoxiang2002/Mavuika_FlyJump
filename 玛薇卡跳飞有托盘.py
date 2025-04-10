import ctypes
import sys
import time
import threading
from tkinter import simpledialog, Tk
import keyboard
import win32gui
from pystray import Icon as TrayIcon, Menu as TrayMenu, MenuItem as TrayMenuItem
from PIL import Image
import os
import json

# 封装命令
# pyinstaller --onefile --noconsole --icon="玛薇卡跳飞.ico" --add-data "玛薇卡跳飞.ico;." "玛薇卡跳飞有托盘.py"

# 请求管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
    sys.exit()

# 获取当前焦点窗口标题
def get_foreground_title():
    window = win32gui.GetForegroundWindow()
    title = win32gui.GetWindowText(window)
    return title

# 定义配置文件路径
def get_config_path():
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件，则使用可执行文件所在目录
        application_path = os.path.dirname(sys.executable)
    else:
        # 开发环境下，配置文件放在脚本同目录
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, "config.json")

# 加载和保存配置
def load_config():
    try:
        with open(get_config_path(), 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {'trigger_key': 'v', 'enable_key': '3'}
    return config

def save_config(config):
    with open(get_config_path(), 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# 全局状态管理
class AppState:
    def __init__(self):
        self.lock = threading.Lock()
        self.is_handling = False
        self.function_enabled = False
        self.config = load_config()
        self.enable_key = self.config.get('enable_key', '3')
        self.trigger_key = self.config.get('trigger_key', 'v')

    def update_trigger_key(self, new_key):
        global trigger_key
        self.trigger_key = new_key
        self.config['trigger_key'] = new_key
        save_config(self.config)

    def update_enable_key(self, new_enable_key):
        self.enable_key = new_enable_key
        self.config['enable_key'] = new_enable_key
        save_config(self.config)

app_state = AppState()

# 更改触发键函数
def change_trigger_key():
    def ask_for_key():
        root = Tk()
        root.withdraw()
        new_key = simpledialog.askstring(" ", "请输入新的触发键:")
        if new_key:
            app_state.update_trigger_key(new_key)
        root.destroy()
    threading.Thread(target=ask_for_key).start()

# 更改角色编号函数
def change_enable_key():
    def ask_for_enable_key():
        root = Tk()
        root.withdraw()
        new_enable_key = simpledialog.askstring(" ", "请输入新的角色编号(1-5):")
        if new_enable_key in ['1', '2', '3', '4', '5']:
            app_state.update_enable_key(new_enable_key)
        root.destroy()
    threading.Thread(target=ask_for_enable_key).start()

# 处理按键事件
def on_key_event(event):
    if event.event_type == keyboard.KEY_DOWN:
        handle_number_key(event.name)
        
        if event.name == app_state.trigger_key:
            current_title = get_foreground_title()  # 新增：获取当前窗口标题
            with app_state.lock:
                if app_state.is_handling or not app_state.function_enabled or ("原神" not in current_title and "云·原神" not in current_title):  # 修改判断条件
                    return
                
                app_state.is_handling = True

            try:
                for _ in range(3):
                    keyboard.press('space')
                    time.sleep(0.02)
                    keyboard.release('space')
                    time.sleep(0.08)
            finally:
                with app_state.lock:
                    app_state.is_handling = False

def handle_number_key(key):
    current_title = get_foreground_title()  # 新增：获取当前窗口标题
    if "原神" not in current_title and "云·原神" not in current_title:  # 修改判断条件
        return
    
    with app_state.lock:
        if key == app_state.enable_key:
            app_state.function_enabled = True
        elif key in {'1','2','3','4','5'} - {app_state.enable_key}:
            app_state.function_enabled = False

# 创建系统托盘图标
keyboard.hook(on_key_event)

icon_path = os.path.join(getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__))), "玛薇卡跳飞.ico")
image = Image.open(icon_path)
menu = TrayMenu(
    TrayMenuItem('更改触发键', change_trigger_key),
    TrayMenuItem('更改角色编号', change_enable_key),
    TrayMenuItem('退出', lambda icon, item: (icon.stop(), keyboard.unhook_all(), sys.exit()))
)
tray_icon = TrayIcon("Genshin Automation", image, "玛薇卡跳飞", menu)

try:
    tray_icon.run()
except KeyboardInterrupt:
    pass
finally:
    keyboard.unhook_all()
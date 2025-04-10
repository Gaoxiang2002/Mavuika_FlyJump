import ctypes
import sys
import time
import threading
import win32gui
import keyboard

# 封装命令
# pyinstaller --onefile --noconsole --icon="玛薇卡跳飞.ico" "玛薇卡跳飞无托盘.py"

# 配置区
trigger_key = 'v'
enable_key = '3'

# 请求管理员权限
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, None, 1)
    sys.exit()

def get_foreground_title():
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)

class AppState:
    def __init__(self):
        self.lock = threading.Lock()
        self.is_handling = False
        self.function_enabled = False
        self.enable_key = enable_key

app_state = AppState()

def handle_number_key(key):
    current_title = get_foreground_title()
    if "原神" not in current_title and "云·原神" not in current_title:
        return
    
    with app_state.lock:
        if key == app_state.enable_key:
            app_state.function_enabled = True
        elif key in {'1','2','3','4','5'} - {app_state.enable_key}:
            app_state.function_enabled = False

def on_key_event(event):
    if event.event_type == keyboard.KEY_DOWN:
        if event.name in ['1','2','3','4','5']:
            handle_number_key(event.name)
        
        if event.name == trigger_key:
            current_title = get_foreground_title()
            with app_state.lock:
                if app_state.is_handling:
                    return
                
                if not app_state.function_enabled:
                    return
                
                if "原神" not in current_title and "云·原神" not in current_title:
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

keyboard.hook(on_key_event)

try:
    keyboard.wait()
except KeyboardInterrupt:
    pass
finally:
    keyboard.unhook_all()
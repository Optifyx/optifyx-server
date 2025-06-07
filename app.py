import platform
import os
import sys
import gzip
import time
import shutil
import threading
import socket
import webbrowser
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from src.internal import run_server, SERVER_PORT
import qrcode

# OS Detection
current_os = platform.system()
IS_WINDOWS = current_os == "Windows"
IS_LINUX = current_os == "Linux"
IS_MAC = current_os == "Darwin"

try:
    import pystray
    from pystray import MenuItem as item
except ImportError:
    print("pystray not available. Tray icon will be disabled.")

try:
    if IS_WINDOWS:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
    else:
        from plyer import notification
except ImportError:
    print("Native notification unavailable.")

# Logger
threads = []
hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)
SERVER_URL = f"http://{IP}:{SERVER_PORT}"

debug_enabled = True
log_window = None
log_text_widget = None
log_file_path = os.path.join("temp", "logs.gz")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

if os.path.exists(log_file_path):
    os.remove(log_file_path)
with gzip.open(log_file_path, 'wb') as f:
    f.write(b'')

class LoggerWriter:
    def __init__(self, stream):
        self.stream = stream or open(os.devnull, 'w')

    def write(self, message):
        if message.strip() == "":
            return
        if not message.endswith('\n'):
            message += '\n'
        timestamped = f"[{time.strftime('%H:%M:%S')}] {message}"
        try:
            self.stream.write(timestamped)
            self.stream.flush()
        except:
            with open(os.devnull, 'w') as devnull:
                devnull.write(timestamped)
        with gzip.open(log_file_path, 'ab') as f:
            f.write(timestamped.encode('utf-8'))

    def flush(self): pass
    def isatty(self): return False

sys.stdout = LoggerWriter(sys.__stdout__)
sys.stderr = LoggerWriter(sys.__stderr__)

def update_log_window():
    last_size = 0
    while True:
        try:
            if not debug_enabled or log_text_widget is None or not log_text_widget.winfo_exists():
                time.sleep(1)
                continue
            with gzip.open(log_file_path, 'rb') as f:
                f.seek(last_size)
                new_data = f.read()
                last_size = f.tell()
            if new_data:
                text = new_data.decode('utf-8')
                log_text_widget.after(0, lambda t=text: log_text_widget.insert(tk.END, t))
                log_text_widget.after(0, lambda: log_text_widget.see(tk.END))
        except Exception as e:
            print(f"[DEBUG LOG ERROR] {e}")
        time.sleep(1)

def open_log_window():
    global log_window, log_text_widget
    if log_window is not None and log_window.winfo_exists():
        log_window.lift()
        log_window.focus_force()
        return
    log_window = tk.Toplevel()
    log_window.title("Optifyx Debug Log")
    log_window.geometry("600x400")
    log_window.configure(bg="black")
    log_window.attributes('-topmost', True)
    log_text_widget = tk.Text(log_window, wrap="word", bg="black", fg="lime", font=("Courier", 10))
    log_text_widget.pack(expand=True, fill="both")

    def on_close():
        global log_window, log_text_widget
        log_window.destroy()
        log_window = None
        log_text_widget = None
    log_window.protocol("WM_DELETE_WINDOW", on_close)

def toggle_debug(icon=None, item=None):
    global debug_enabled
    debug_enabled = not debug_enabled
    print(f"Debug mode {'ON' if debug_enabled else 'OFF'}")

def add_to_startup():
    if IS_WINDOWS:
        startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
        script_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__)
        destination_path = os.path.join(startup_folder, os.path.basename(script_path))
        if not os.path.exists(destination_path):
            shutil.copy(script_path, destination_path)
            print(f"Added to startup: {destination_path}")

def notify(title, message):
    try:
        if IS_WINDOWS:
            toaster.show_toast(title, message, duration=5, threaded=True)
        else:
            notification.notify(title=title, message=message, app_name="Optifyx", timeout=5)
    except:
        print(f"{title}: {message}")

def exit_action(icon, item):
    print("Shutting down...")
    notify("Optifyx", "Shutting down server...")
    def shutdown():
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=1)
        if icon: icon.stop()
        os._exit(0)
    threading.Thread(target=shutdown, daemon=True).start()

def show_qr_code():
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    qr_path = os.path.join(temp_dir, "server_qr.png")
    qrcode.make(SERVER_URL).save(qr_path)

    def open_qr_window():
        qr_win = tk.Toplevel()
        qr_win.title("Server QR Code")
        qr_win.geometry("400x450")
        qr_win.configure(bg='white')
        qr_win.attributes('-topmost', True)
        img = Image.open(qr_path)
        img_tk = ImageTk.PhotoImage(img)
        tk.Label(qr_win, image=img_tk, bg='white').pack(pady=20)
        tk.Label(qr_win, text=SERVER_URL, wraplength=380, fg="black", bg="white").pack(pady=10)
        qr_win.mainloop()
    if 'root' in globals():
        root.after(0, open_qr_window)

def get_menu(icon):
    return pystray.Menu(
        item("Show QR Code", show_qr_code),
        item("Show Debug Log", open_log_window),
        item(lambda item: f"Toggle Debug Mode ({'ON' if debug_enabled else 'OFF'})", toggle_debug),
        item("Website", lambda: webbrowser.open("https://optifyx.theushen.me")),
        item("Exit", exit_action)
    )

def setup_tray_icon():
    try:
        icon_image = Image.open(os.path.abspath("Assets/image.ico"))
        icon = pystray.Icon("Optifyx", icon_image, "Optifyx Server")
        icon.menu = get_menu(icon)
        icon.run()
    except Exception as e:
        print(f"Tray icon failed: {e}")

def create_window():
    global root
    if os.environ.get('DISPLAY', None):
        root = tk.Tk()
        root.title("Optifyx")
        root.geometry("650x650")
        root.configure(bg='black')
        img = tk.PhotoImage(file="Assets/image.png")
        tk.Label(root, image=img, bg='black').pack(pady=20)
        tk.Label(root, text="You can close this tab now", fg="white", font=("Arial", 20), bg='black').pack()
        tk.Button(root, text="Show Debug Log", command=open_log_window, bg="gray", fg="lime").pack(pady=8)
        threading.Timer(0.4, lambda: root.withdraw()).start()
        root.mainloop()
    else:
        print("Warning: No display environment. GUI will not start.")

def has_display():
    # Para Linux/macOS: verifica DISPLAY
    if IS_LINUX or IS_MAC:
        return bool(os.environ.get('DISPLAY'))
    # Para Windows, normalmente tem GUI, então retorna True
    if IS_WINDOWS:
        return True
    return False

if __name__ == "__main__":
    add_to_startup()
    server_thread = threading.Thread(target=run_server, name="ServerThread", daemon=True)
    log_thread = threading.Thread(target=update_log_window, name="LogThread", daemon=True)
    threads.extend([server_thread, log_thread])
    for t in [server_thread, log_thread]:
        t.start()

    if has_display():
        if IS_MAC:
            create_window()
            setup_tray_icon()
        else:
            window_thread = threading.Thread(target=create_window, name="WindowThread", daemon=True)
            tray_thread = threading.Thread(target=setup_tray_icon, name="TrayThread", daemon=True)
            threads.extend([window_thread, tray_thread])
            window_thread.start()
            tray_thread.start()
    else:
        print("Warning: No display environment. Tray Icon will not start.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Program terminated.")
        sys.exit(0)
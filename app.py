import pystray
from pystray import MenuItem as item
from PIL import Image, ImageTk
import tkinter as tk
import threading
from src.internal import run_server
import os
import time
import shutil
import sys
from plyer import notification
import socket
import qrcode
from src.internal import SERVER_PORT
import webbrowser
import gzip

threads = []
hostname = socket.gethostname()
IP = socket.gethostbyname(hostname)
SERVER_URL = f"http://{IP}:{SERVER_PORT}"

debug_enabled = True
log_window = None
log_text_widget = None
log_file_path = os.path.join("temp", "logs.gz")

# Limpa o arquivo de logs ao iniciar
if os.path.exists(log_file_path):
    os.remove(log_file_path)
with gzip.open(log_file_path, 'wb') as f:
    f.write(b'')

class LoggerWriter:
    def __init__(self, stream):
        self.stream = stream
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        if not os.path.exists(log_file_path):
            with gzip.open(log_file_path, 'wb') as f:
                f.write(b'')

    def write(self, message):
        if message.strip() == "":
            return
        # Garante quebra de linha no final
        if not message.endswith('\n'):
            message += '\n'
        timestamped = f"[{time.strftime('%H:%M:%S')}] {message}"
        self.stream.write(timestamped)
        self.stream.flush()
        with gzip.open(log_file_path, 'ab') as f:
            f.write(timestamped.encode('utf-8'))

    def flush(self):
        pass

    def isatty(self):
        return False

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
        log_window.destroy()  # Permite fechar normalmente
        log_window = None
        log_text_widget = None

    log_window.protocol("WM_DELETE_WINDOW", on_close)

def toggle_debug(icon=None, item=None):
    global debug_enabled
    debug_enabled = not debug_enabled
    print(f"Debug mode {'ON' if debug_enabled else 'OFF'}")
    # Não precisa atualizar o menu, pois o texto do item é dinâmico

def add_to_startup():
    startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
    script_path = os.path.abspath(__file__)
    destination_path = os.path.join(startup_folder, os.path.basename(script_path))

    if not os.path.exists(destination_path):
        shutil.copy(script_path, destination_path)
        print(f"Logs: Adicionado à inicialização em {startup_folder}")

def exit_action(icon, item):
    print("Logs: Encerrando o programa...")
    notification.notify(title="Optifyx", message="Closing the server...", app_name="Optifyx", timeout=5)

    def shutdown():
        for thread in threads:
            if thread.is_alive():
                print(f"Logs: Encerrando thread {thread.name}...")
                thread.join(timeout=1)
        icon.stop()
        os._exit(0)

    threading.Thread(target=shutdown, daemon=True).start()

def show_qr_code():
    temp_dir = os.path.join(os.getcwd(), "temp")
    os.makedirs(temp_dir, exist_ok=True)
    qr_img_path = os.path.join(temp_dir, "server_qr.png")
    qr = qrcode.make(SERVER_URL)
    qr.save(qr_img_path)

    def open_qr_window():
        qr_win = tk.Toplevel()
        qr_win.title("Server QR Code")
        qr_win.geometry("400x450")
        qr_win.configure(bg='white')
        qr_win.attributes('-topmost', True)
        qr_win.lift()
        qr_win.focus_force()

        qr_img = Image.open(qr_img_path)
        qr_img_tk = ImageTk.PhotoImage(qr_img)

        label = tk.Label(qr_win, image=qr_img_tk, bg='white')
        label.image = qr_img_tk
        label.pack(pady=20)

        text_label = tk.Label(qr_win, text=SERVER_URL, wraplength=380, fg="black", bg="white")
        text_label.pack(pady=10)

    if 'root' in globals():
        root.after(0, open_qr_window)

def get_menu(icon):
    return pystray.Menu(
        item("Show QR Code", lambda: show_qr_code()),
        item("Show Debug Log", lambda: open_log_window()),
        item(lambda item: f"Toggle Debug Mode ({'ON' if debug_enabled else 'OFF'})",
             lambda icon, item: toggle_debug(icon, item)),
        item("Website", lambda: webbrowser.open("https://optifyx.theushen.me")),
        item("Exit", lambda icon, item: exit_action(icon, item))
    )

def setup_tray_icon():
    icon_image = Image.open(os.path.abspath("Assets/image.ico"))
    icon = pystray.Icon("Optifyx", icon_image, "Optifyx Server")
    icon.menu = get_menu(icon)
    icon.run()

def create_window():
    global root
    root = tk.Tk()
    root.title("Optifyx")
    root.geometry("650x650")
    root.configure(bg='black')

    img = tk.PhotoImage(file="Assets/image.png")
    image_label = tk.Label(root, image=img, bg='black')
    image_label.image = img
    image_label.pack(pady=20)

    text_label = tk.Label(root, text="You can close this tab now", fg="white", font=("Arial", 20), bg='black')
    text_label.pack()

    debug_btn = tk.Button(root, text="Show Debug Log", command=open_log_window, bg="gray", fg="lime")
    debug_btn.pack(pady=8)

    threading.Timer(0.4, lambda: root.withdraw()).start()
    root.mainloop()

if __name__ == "__main__":
    add_to_startup()

    window_thread = threading.Thread(target=create_window, name="WindowThread", daemon=True)
    tray_thread = threading.Thread(target=setup_tray_icon, name="TrayThread", daemon=True)
    server_thread = threading.Thread(target=run_server, name="ServerThread", daemon=True)
    log_thread = threading.Thread(target=update_log_window, name="LogThread", daemon=True)

    threads.extend([window_thread, tray_thread, server_thread, log_thread])

    for t in threads:
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Finish Program.")
        sys.exit(0)
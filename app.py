import pystray
from pystray import MenuItem as item
from PIL import Image
import tkinter as tk
import threading
from utils.endpoints import run_server
import os
import time
import shutil
import sys
from plyer import notification

threads = []

def add_to_startup():
    startup_folder = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
    script_path = os.path.abspath(__file__)
    script_name = os.path.basename(script_path)
    destination_path = os.path.join(startup_folder, script_name)

    if not os.path.exists(destination_path):
        shutil.copy(script_path, destination_path)
        print(f"Logs: Arquivo {script_name} adicionado à inicialização em {startup_folder}")

def exit_action(icon, item):
    print("Logs: Encerrando o programa...")

    notification.notify(
        title="Optifyx",
        message="Closing the server...",
        app_name="Optifyx",
        timeout=5
    )

    def shutdown():
        for thread in threads:
            if thread.is_alive():
                print(f"Logs: Encerrando thread {thread.name}...")
                thread.join(timeout=1)

        icon.stop()
        os._exit(0)

    threading.Thread(target=shutdown, daemon=True).start()

def setup_tray_icon():
    icon_image = Image.open(os.path.abspath("Assets/image.ico"))
    icon = pystray.Icon("Optifyx", icon_image, "Optifyx Server", menu=pystray.Menu(
        item("Exit", lambda: exit_action(icon, None))
    ))

    icon.run()

def create_window():
    root = tk.Tk()
    root.title("Optifyx")
    root.geometry("650x650")
    root.configure(bg='black')

    img = tk.PhotoImage(file="Assets/image.png")
    image_label = tk.Label(root, image=img, bg='black')
    image_label.pack(pady=20)

    text_label = tk.Label(root, text="You can close this tab now", fg="white", font=("Arial", 20), bg='black')
    text_label.pack()

    threading.Timer(0.4, lambda: root.withdraw()).start()
    root.mainloop()

if __name__ == "__main__":
    add_to_startup()

    window_thread = threading.Thread(target=create_window, name="WindowThread", daemon=True)
    tray_thread = threading.Thread(target=setup_tray_icon, name="TrayThread", daemon=True)
    server_thread = threading.Thread(target=run_server, name="ServerThread", daemon=True)

    threads.extend([window_thread, tray_thread, server_thread])

    window_thread.start()
    tray_thread.start()
    server_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Programa encerrado.")
        sys.exit(0)

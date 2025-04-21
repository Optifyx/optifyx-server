import random
import string
import pyperclip
import tkinter as tk

generated_code = ""

def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def copy_to_clipboard(code):
    pyperclip.copy(code)

def display_code_window(code):
    root = tk.Tk()
    root.title("Connection Code")
    root.geometry("600x250")
    root.attributes('-topmost', True)
    root.lift()
    root.focus_force()
    label = tk.Label(root, text=f"Connection Code: {code}", font=("Arial", 20))
    label.pack(pady=20)
    copy_button = tk.Button(root, text="Copy Code", command=lambda: copy_to_clipboard(code))
    copy_button.pack(pady=10)
    root.mainloop()
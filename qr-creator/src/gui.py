import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

def draw_simple_window()-> None:
    # Draw user window
    root = tk.Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    tk.Label(frm, text="Hello, World!").grid(column=0, row=2)
    tk.Button(frm, text="Select File")
    tk.Button(frm, text="Quit", command=root.destroy).grid(column=0, row=0)
    root.mainloop()

def draw_interactive_window()-> None:
# create special TkinterDnD Window
    root = TkinterDnD.Tk()
    root.geometry("500x300")
    root.title("File Drag and Drop")

    label = tk.Label(root, text="Drag & Drop a file here", bg="lightgray", width=50, height=10)
    label.pack(pady=50)

# enable drop events
    label.drop_target_register(DND_FILES)
    label.dnd_bind("<<Drop>>", drop_file)

    root.mainloop()

def drop_file(event):
    # Handles the dropped file path
    file_path = event.data
    label.config(text=f"Dropped file:\n{file_path}")

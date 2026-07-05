import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

def draw_window() -> None:
    # create special TkinterDnD Window
    root = TkinterDnD.Tk()
    root.geometry("500x300")
    lb = tk.Listbox(root)
    lb.insert(1, "Drag & Drop a file here")
    root.title("File Drag and Drop")

    def on_drop(event) -> None:
        # Handles the dropped file path
        for path in root.tk.splitlist(event.data):
            lb.insert(tk.END, path)

    # register listbox as a drop target
    lb.drop_target_register(DND_FILES)
    lb.dnd_bind("<<Drop>>", on_drop)

    lb.pack()
    root.mainloop()

import tkinter as tk
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

def draw_window()-> None:
    # Draw user window
    root = tk.Tk()
    frm = ttk.Frame(root, padding=10)
    frm.grid()
    tk.Label(frm, text="Hello, World!").grid(column=0, row=0)
    tk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
    root.mainloop()

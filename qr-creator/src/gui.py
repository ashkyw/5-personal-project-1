import qrcode
import openpyxl
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

class TopLevelWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = ctk.CTkLabel(self, text="TopLevelWindow")
        self.label.pack(padx=20, pady=20)

class DragAndDropFrame(ctk.CTkFrame):
    def __init__(self, master, title):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1)
        self.title = title

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")



class ButtonFrame(ctk.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.buttons = []

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            button = ctk.CTkButton(self, text=value)
            button.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="ew")

class CheckBoxFrame(ctk.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.checkboxes = []

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            checkbox = ctk.CTkCheckBox(self, text=value)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self) -> str:
        checked_checkboxes = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes

class RadiobuttonFrame(ctk.CTkFrame):
    def __init__(self, master, title, values):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values = values
        self.title = title
        self.radiobuttons = []
        self.variable = ctk.StringVar(value="")

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self) -> str:
        return self.variable.get()

    def set(self, value) -> None:
        self.variable.set(value)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("App title goes here")
        self.geometry("400x380")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.toplevel_window = None

        self.button = ctk.CTkButton(self, text="New window", command=self.create_toplevel_window)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

        self.button_frame = ButtonFrame(self, "Functions", values=["QR Code", "Something else"])
        self.button_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nsw")

        self.drop_frame = DragAndDropFrame(self, "File")
        self.drop_frame.grid(row=0, column=1, padx=(0,10), pady=(10,0), sticky="nsew")
        self.drop_frame.configure(fg_color="transparent")

    # Figure out how to inject this to the frame to capture data.
        def on_drop(event) -> str:
            files = self.drop_frame.tk.splitlist(event.data)
            entry.delete(0, "end")
            entry.insert(0, files[0])

        TkinterDnD.require(self.drop_frame)
        entry = ctk.CTkEntry(
            self.drop_frame, width=200, placeholder_text="Drag file here..."
        )

        entry.drop_target_register(DND_FILES)
        entry.dnd_bind("<<Drop>>", on_drop)

    def button_callback(self) -> None:
        print("checked checkboxes", self.checkbox_frame.get())
        print("radiobutton_frame", self.radiobutton_frame.get())

    def create_toplevel_window(self) -> None:
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = TopLevelWindow(self)
        else:
            self.toplevel_window.focus()

    def create_qrcodes(workbook):
        data_book = openpyxl.load_workbook(workbook)
        data_tab = data_book.active
        i = 0

        for row in data_tab.iter_rows(values_only=True):
            if row != (None,):
                cleaned_row = "".join(map(str, row))
                img = qrcode.make(cleaned_row)
                img.save(f"{i}.png")
                i += 1

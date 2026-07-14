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

class LabelText(ctk.CTkFrame):
    def __init__(self, master, values):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=10)
        self.values = values

        for i, value in enumerate(self.values):
            self.label = ctk.CTkLabel(self, text=value, fg_color="transparent", justify="center")
            self.label.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="ew")

class DragAndDropFrame(ctk.CTkFrame):
    def __init__(self, master, title, on_files=None):
        super().__init__(master)
        self.title = title
        self.on_files = on_files

        self.grid_columnconfigure(0, weight=10)

        self.title = ctk.CTkLabel(self, text=self.title, font=ctk.CTkFont(size=16, weight="bold"))
        self.title.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)

    # ID and filter unwanted captured data
    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        valid = self.validate_files(files)

        if self.on_files:
            self.on_files(valid)

    # Validate files before displaying
    def validate_files(self, files):
        valid_list = []
        for file in files:
            if file.endswith(".png"):
                if file not in valid_list:
                    valid_list.append(file)

        return valid_list

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

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        # Set App window settings
        self.title("App title goes here")
        self.geometry("800x640")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(bg="black")

        self.files = []

        self.toplevel_window = None

        self.button = ctk.CTkButton(self, text="New window", command=self.create_toplevel_window)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

        # Set ButtonFrame names & settings
        self.button_frame = ButtonFrame(self, "Functions", values=["QR Code", "Something else"])
        self.button_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nsew")

        # Set DragAndDropFrame labels & settings
        self.drop_frame = DragAndDropFrame(self, "Drag files here...", on_files=self.files_dropped)
        self.drop_frame.grid(row=0, column=1, padx=(0,10), pady=(10,0), sticky="nsew", columnspan=2)
        self.drop_frame.configure(fg_color="transparent")

    # Hands files off to other functions
    def files_dropped(self, files):
        self.files = files

        # Display and update dropped files
        # If frame exists, clear it
        if hasattr(self, "text_frame"):
            self.text_frame.destroy()

        # Set LabelText labels & values
        self.text_frame = LabelText(self.drop_frame, self.files)
        self.text_frame.grid(row=1, column=0, padx=10, pady=(10,0), sticky="ew")

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

    def button_callback(self) -> None:
        print("checked checkboxes", self.checkbox_frame.get())
        print("radiobutton_frame", self.radiobutton_frame.get())

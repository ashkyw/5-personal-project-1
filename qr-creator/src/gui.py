import qrcode
import openpyxl
import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from pathlib import Path

class TopLevelWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x300")

        self.label = ctk.CTkLabel(self, text="TopLevelWindow")
        self.label.pack(padx=20, pady=20)

class DragAndDropFrame(ctk.CTkFrame):
    def __init__(self, master, title, label):
        super().__init__(master)

        self.title = title
        self.files = []
        self.drop_label = label

        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.drop_label = ctk.CTkLabel(self, text=self.drop_label, font=ctk.CTkFont(size=16, weight="bold"))
        self.drop_label.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)

        #TODO
        # Add a textbox that posts the individual file names for user display in this frame
    # Define captured event data
    def on_drop(self, event):
        raw = event.data.strip()
        self.files = self.parse_dnd_files(raw)
        self.title.configure(text=f"{self.title} ({len(self.files)})")

    def parse_dnd_files(self, raw: str):
        raw = raw.strip()

        if not raw:
            return []

        if raw.startswith("{") is False and raw.count(" ") == 0 and raw.count("\n") == 0:
            print([raw])
            return [raw]

        out = []
        cur = ""
        in_braces = False

        for ch in raw:
            if ch == "{":
                in_braces = True
                continue
            if ch == "}":
                in_braces = False
                out.append(cur)
                cur = ""
                continue
            if ch == " " and not in_braces:
                if cur:
                    out.append(cur)
                    cur = ""
                continue
            cur += ch

        if cur:
            out.append(cur)

        print(out)
        return out

    def get_files(self):
        return list(self.files)

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
        self.geometry("400x380")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(bg="black")

        self.toplevel_window = None

        self.button = ctk.CTkButton(self, text="New window", command=self.create_toplevel_window)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=2)
        # Set ButtonFrame names & settings
        self.button_frame = ButtonFrame(self, "Functions", values=["QR Code", "Something else"])
        self.button_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nsw")
        # Set DragAndDropFrame labels & settings
        self.drop_frame = DragAndDropFrame(self, "File", "Drag files here...")
        self.drop_frame.grid(row=0, column=1, padx=(0,10), pady=(10,0), sticky="nsew")
        self.drop_frame.configure(fg_color="gray30")

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

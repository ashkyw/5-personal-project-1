import qrcode
import openpyxl
import customtkinter as ctk
from io import BytesIO
from tkinterdnd2 import DND_FILES, TkinterDnD
from openpyxl.drawing.image import Image

class TopLevelWindow(ctk.CTkToplevel):
    def __init__(self, master, text: str):
        super().__init__(master)
        self.geometry("400x300")

        self.text: str = text

        self.label = ctk.CTkLabel(self, text=text)
        self.label.pack(padx=20, pady=20)

class LabelText(ctk.CTkFrame):
    def __init__(self, master, values: list[str]):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=10)
        self.values: list[str] = values

        if len(self.values) == 1:
            for i, value in enumerate(self.values):
                self.label = ctk.CTkLabel(self, text=value, fg_color="transparent", justify="center")
                self.label.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="ew")
        else:
            self.label = ctk.CTkLabel(self, text=self.values, fg_color="transparent", justify="center")
            self.label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")

class DragAndDropFrame(ctk.CTkFrame):
    def __init__(self, master, title: str, on_files: list[str]=None, valid_extensions: tuple[str]=None):
        super().__init__(master)
        self.title: str = title
        self.on_files: list[str] = on_files
        self.valid_extensions: tuple[str] = valid_extensions

        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(self, text=self.title, font=ctk.CTkFont(size=16, weight="bold"))
        self.title.grid(row=0, column=0, padx=10, pady=(10,0), sticky="ew")

        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)

    # ID and filter unwanted captured data
    def on_drop(self, event: list[str]) -> None:
        files = self.tk.splitlist(event.data)
        valid = self.validate_files(files, self.valid_extensions)

        if self.on_files:
            self.on_files(valid)

    # Validate files before displaying
    def validate_files(self, files: list[str], valid_extensions: tuple[str]):
        valid_files: list[str] = []
        for file in files:
            if file.endswith(self.valid_extensions):
                if file not in valid_files:
                    valid_files.append(file)

        return valid_files

class ButtonFrame(ctk.CTkFrame):
    # Takes text and commands as lists
    def __init__(self, master, title: str, text: list[str]=None, commands: list[str]=None):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.title: str = title
        self.button_text: str = text
        self.buttons: list[str] = []
        self.commands: list[str] = commands

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        if self.button_text is not None and self.commands is not None:
            for i, text in enumerate(self.button_text):
                button = ctk.CTkButton(self, text=text, command=self.commands[i])
                button.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="ew")

class CheckBoxFrame(ctk.CTkFrame):
    def __init__(self, master, title: str, values: list[str]):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values: list[str] = values
        self.title: str = title
        self.checkboxes: list[str, int] = []

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            checkbox = ctk.CTkCheckBox(self, text=value)
            checkbox.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.checkboxes.append(checkbox)

    def get(self) -> list[str, int]:
        checked_checkboxes: list[str, int] = []
        for checkbox in self.checkboxes:
            if checkbox.get() == 1:
                checked_checkboxes.append(checkbox.cget("text"))
        return checked_checkboxes

class RadiobuttonFrame(ctk.CTkFrame):
    def __init__(self, master, title: str, values: list[str]):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values: list[str] = values
        self.title: str = title
        self.radiobuttons: list[str] = []
        self.variable = ctk.StringVar(value="")

        self.title = ctk.CTkLabel(self, text=self.title, fg_color="gray30", corner_radius=6)
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(self, text=value, value=value, variable=self.variable)
            radiobutton.grid(row=i+1, column=0, padx=10, pady=(10, 0), sticky="w")
            self.radiobuttons.append(radiobutton)

    def get(self) -> str:
        return self.variable.get()

    def set(self, value: str) -> None:
        self.variable.set(value)

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        # Set App window settings
        self.title("Excel File Formatter")
        self.geometry("800x640")
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.configure(bg="gray10")

        self.files: list[str] = []

        self.toplevel_window = None
        valid_extensions: tuple[str] = (".xlsx", ".xlsm")
        dnd_title_message: str = f"Drag files here...\n\n Files must be saved in {valid_extensions} format."

        # Set DragAndDropFrame labels & settings
        self.drop_frame = DragAndDropFrame(
            self, title=dnd_title_message, on_files=self.files_dropped,
            valid_extensions=valid_extensions
        )
        self.drop_frame.grid(row=0, column=1, padx=(0,10), pady=(10,0), sticky="nsew")
        self.drop_frame.configure(fg_color="gray30", border_width=1, border_color="black")

        # Set ButtonFrame buttons & settings
        self.button_frame = ButtonFrame(
            self, "Functions", text=["Create QR Codes"],
            commands=[self.create_qrcodes]
        )
        self.button_frame.grid(row=0, column=0, padx=10, pady=(10,0), sticky="nsew")

        self.button = ctk.CTkButton(self, text="Clear List", command=self.clear_files_list)
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

    # Hands files off to other functions, displays files in list
    def files_dropped(self, files: list[str]) -> None:
        self.files: list[str] = files

        # Display and update dropped files
        # If frame exists, clear it
        self.clear_drop_frame_text

        # Set child labels & values
        self.drop_frame_text = LabelText(self.drop_frame, self.files)
        self.drop_frame_text.grid(row=1, column=0, padx=10, pady=(10,0), sticky="ew")

    # Button functions
    # Create new toplevel window
    def create_toplevel_window(self, text: str) -> None:

        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = TopLevelWindow(self, text=text)
        else:
            self.toplevel_window.focus()

    # Clear current active list, update display frame
    def clear_files_list(self) -> None:
        self.files = []
        self.clear_drop_frame_text

    # Fun button to test things
    def test_adding_commands_to_buttons(self) -> str:
        print("Every thing works")

    # Creates QR Codes and stores them in excel file
    def create_qrcodes(self) -> None:
        if self.files == []:
            self.create_toplevel_window("No files found")
        else:
            try:
                for file in self.files:
                    # set workbook and sheet
                    workbook = openpyxl.load_workbook(file)
                    ws = workbook.active
                    # split file for saving
                    file_path, extension = file.split(".")
                    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
                        if row != (None,):
                            self.format_excel_sheet(ws, i)
                            cleaned_row = "".join(map(str, row))
                            qr_img = qrcode.make(cleaned_row)
                            qr_img = self.format_qrcode_images(qr_img, i)
                            ws.add_image(qr_img)
                    workbook.save(f"{file_path}_qrcodes.{extension}")
                    # Provide user feedback
                    self.create_toplevel_window("Operation Success!")
            except KeyError:
                    self.create_toplevel_window(
                        "Operation Failed.\n File(s) may be corrupted. Try again."
                    )
                    self.files=[]
                    self.clear_drop_frame_text

    # Helper function to format Excel sheet
    def format_excel_sheet(self, ws, row: int) -> None:
        ws.row_dimensions[row].height = 185
        ws.column_dimensions["B"].width = 2
        ws.column_dimensions["C"].width = 28

    # Helper function to format and temp store QR Codes
    def format_qrcode_images(self, img, num: int) -> Image:
        # Create temp buffer to store image
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        # Set img to be temp stored image, set parameters
        img = Image(buffer)
        img.width = 225
        img.height = 225
        img.anchor = f"C{num}"
        return img

    def button_callback(self) -> None:
        print("checked checkboxes", self.checkbox_frame.get())
        print("radiobutton_frame", self.radiobutton_frame.get())

    # Clear Active Frames
    def clear_drop_frame_text(self) -> None:
        if hasattr(self, "drop_frame_text"):
            self.drop_frame_text.destroy()

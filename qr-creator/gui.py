import os
from io import BytesIO

import customtkinter as ctk
import openpyxl
import qrcode
from openpyxl.drawing.image import Image
from pypdf import PdfReader, PdfWriter
from pypdf.errors import FileNotDecryptedError
from tkinterdnd2 import DND_FILES, TkinterDnD


class TopLevelWindow(ctk.CTkToplevel):
    def __init__(self, master, text: str):
        super().__init__(master)
        self.geometry("400x300")

        self.text: str = text

        self.label = ctk.CTkLabel(
            self,
            text=self.text,
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="center",
        )
        self.label.pack(padx=20, pady=20)


class LabelText(ctk.CTkFrame):
    def __init__(self, master, values: list[str]):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=10)
        self.values: list[str] = values
        if len(self.values) != 1:
            for i, value in enumerate(self.values):
                self.label = ctk.CTkLabel(
                    self, text=value, fg_color="transparent", justify="center"
                )
                self.label.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="ew")
        else:
            self.label = ctk.CTkLabel(
                self, text=self.values, fg_color="transparent", justify="center"
            )
            self.label.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="ew")


class DragAndDropFrame(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        on_files: list[str] = [],
        valid_extensions: tuple[str] = None,
    ):
        super().__init__(master)
        self.title: str = title
        self.on_files: list[str] = on_files
        self.valid_extensions: tuple[str] = valid_extensions

        self.grid_columnconfigure(0, weight=1)

        self.title = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold"),
            justify="center",
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

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
    def __init__(
        self, master, title: str, text: list[str] = None, commands: list[str] = None
    ):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.title: str = title
        self.button_text: str = text
        self.buttons: list[str] = []
        self.commands: list[str] = commands

        self.title = ctk.CTkLabel(
            self, text=self.title, fg_color="gray30", corner_radius=6
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")
        if self.button_text is not None and self.commands is not None:
            for i, text in enumerate(self.button_text):
                button = ctk.CTkButton(self, text=text, command=self.commands[i])
                button.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="nsew")


class CheckBoxFrame(ctk.CTkFrame):
    def __init__(self, master, title: str, values: list[str]):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.values: list[str] = values
        self.title: str = title
        self.checkboxes: list[str, int] = []

        self.title = ctk.CTkLabel(
            self, text=self.title, fg_color="gray30", corner_radius=6
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            checkbox = ctk.CTkCheckBox(self, text=value)
            checkbox.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
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

        self.title = ctk.CTkLabel(
            self, text=self.title, fg_color="gray30", corner_radius=6
        )
        self.title.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        for i, value in enumerate(self.values):
            radiobutton = ctk.CTkRadioButton(
                self, text=value, value=value, variable=self.variable
            )
            radiobutton.grid(row=i + 1, column=0, padx=10, pady=(10, 0), sticky="w")
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

        # valid_extensions: tuple[str] = (".xlsx", ".pdf")
        valid_extensions: str = ".pdf"
        # first_type, second_type = valid_extensions
        # dnd_title_message: str = f'Files must be saved in "{first_type}" or "{second_type}" format. \n\n Drag files onto this text... '
        dnd_title_message: str = f'Files must be saved in "{valid_extensions}" format. \n\n Drag files onto this text... '

        self.reset_drop_frame_related_frames()

        # Set DragAndDropFrame labels & settings
        self.drop_frame = DragAndDropFrame(
            self,
            title=dnd_title_message,
            on_files=self.files_dropped,
            valid_extensions=valid_extensions,
        )
        self.drop_frame.grid(row=0, column=1, padx=(0, 10), pady=(10, 0), sticky="nsew")
        self.drop_frame.configure(
            fg_color="gray30", border_width=1, border_color="black"
        )

        self.button = ctk.CTkButton(
            self, text="Clear List", command=self.clear_files_list
        )
        self.button.grid(row=3, column=0, padx=10, pady=10, sticky="ew", columnspan=2)

    # Button functions
    # Create new toplevel window
    def create_toplevel_window(self, title: str, text: str) -> None:
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = TopLevelWindow(self, text=text)
            self.toplevel_window.title(title)
        else:
            self.toplevel_window.focus()

    # Fun button to test things
    def test_buttons(self) -> None:
        print("Every thing works")

    # Exists in case it's ever needed
    def button_callback(self) -> None:
        print("checked checkboxes", self.checkbox_frame.get())
        print("radiobutton_frame", self.radiobutton_frame.get())

    # Clear current active list, update display frame
    def clear_files_list(self) -> None:
        self.files = []
        self.reset_drop_frame_related_frames()

    # Creates QR Codes and stores them in excel file
    def create_qrcodes(self) -> None:
        if self.files == []:
            self.create_toplevel_window("Error", text="No files found")
        else:
            try:
                for file in self.files:
                    # set workbook and sheet
                    workbook = openpyxl.load_workbook(file)
                    ws = workbook.active
                    new_path = self.create_and_validate_new_file_path(file, "/qrcoded/")
                    for i, row in enumerate(ws.iter_rows(values_only=True), start=1):
                        if row != (None,):
                            self.format_excel_sheet(ws, i)
                            cleaned_row = "".join(map(str, row))
                            qr_img = qrcode.make(cleaned_row)
                            qr_img = self.format_qrcode_images(qr_img, i)
                            ws.add_image(qr_img)
                    workbook.save(new_path)
                    # Provide user feedback
                    self.create_toplevel_window("Success", text="Operation Success!")
            except Exception:
                self.create_toplevel_window(
                    "Error",
                    text="Operation Failed.\n\n File(s) may be corrupted. Try again.",
                )
                self.files = []
                self.reset_drop_frame_related_frames()

    # Removes PDF password, reformats file name
    def remove_pdf_password(self, pdf_password="111111") -> None:
        for file in self.files:
            reader = PdfReader(file)
            try:
                new_path = self.create_and_validate_new_file_path(file, "/cleaned/")
                reader.decrypt(pdf_password)
                writer = PdfWriter(clone_from=reader)
                writer.write(new_path)
            except FileNotDecryptedError:
                self.remove_pdf_password(
                    self.get_user_input("Missing Password", "Enter password")
                )

    # Create a dialog box to return user input
    def get_user_input(self, title: str, text: str) -> str:
        dialog = ctk.CTkInputDialog(text=text, title=title)
        return dialog.get_input()

    # Helper Functions
    # Create new file path, send it to validate
    def create_and_validate_new_file_path(self, file: str, new_folder: str) -> str:
        path = os.path.dirname(file)
        current_file = os.path.splitext(os.path.basename(file))
        extension = current_file[-1]
        if extension == ".pdf":
            file_name = current_file[0].split(" _")
            file_name = file_name[0]
            if len(file_name) >= 12 and len(file_name) < 13:
                file_name = file_name[:-1]

            new_path = f"{path}{new_folder}{file_name}{extension}"
        else:
            new_path = f"{path}{new_folder}{current_file[0]}{extension}"

        self.validate_file_path(f"{path}{new_folder}")
        return new_path

    # Check if file path exists & make it if not
    def validate_file_path(self, file_path: str) -> None:
        try:
            if not os.path.exists(file_path):
                os.makedirs(file_path)
        except Exception:
            self.create_toplevel_window(
                title="Error",
                text="Something happened.",
            )

    # Hands files off to other functions, displays files in list
    def files_dropped(self, files: list[str]) -> None:
        self.files: list[str] = files

        # If frame exists, reset it
        self.reset_drop_frame_related_frames()

        # Set self.files to filtered list
        self.files = self.count_and_filter_file_types()

        # Set child labels & values
        try:
            self.drop_frame_text = LabelText(self.drop_frame, values=self.files)
            self.drop_frame_text.grid(
                row=1, column=0, padx=10, pady=(10, 0), sticky="ew"
            )
        except Exception:
            self.create_toplevel_window(
                title="Error",
                text="Cannot filter file types.",
            )
            self.files = []
            self.reset_drop_frame_related_frames()

    # Format Excel sheet
    def format_excel_sheet(self, ws, row: int) -> None:
        ws.row_dimensions[row].height = 185
        ws.column_dimensions["B"].width = 2
        ws.column_dimensions["C"].width = 28

    # Format and temp store QR Codes
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

    # Reset Active Frames
    def reset_drop_frame_related_frames(self) -> None:
        self.button_frame = ButtonFrame(self, title="Functions")
        self.button_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.button_frame.configure(border_width=1, border_color="black")

        if hasattr(self, "drop_frame_text"):
            self.drop_frame_text.destroy()

    # Filters file types based on count
    def count_and_filter_file_types(self) -> list[str]:
        excel_file_count = 0
        pdf_file_count = 0
        excel_files = []
        pdf_files = []
        # Count file type

        for file in self.files:
            if file.endswith(".xlsx"):
                excel_files.append(file)
                excel_file_count += 1
            elif file.endswith(".pdf"):
                pdf_files.append(file)
                pdf_file_count += 1

        # Set state based on file type count, return filtered list
        if excel_file_count == len(self.files) or excel_file_count > pdf_file_count:
            self.set_button_frame_functions("Excel")
            return excel_files
        elif pdf_file_count == len(self.files) or pdf_file_count > excel_file_count:
            self.set_button_frame_functions("PDF")
            return pdf_files

    # Set button frame functionality
    def set_button_frame_functions(self, button_type: str) -> ButtonFrame:
        # Set ButtonFrame buttons & settings
        match button_type:
            case "Excel":
                self.button_frame = ButtonFrame(
                    self,
                    title="Excel Functions",
                    text=["Create QR Codes"],
                    commands=[self.create_qrcodes],
                )
            case "PDF":
                self.button_frame = ButtonFrame(
                    self,
                    title="PDF Functions",
                    text=["Remove PDF Password"],
                    commands=[self.remove_pdf_password],
                )

        self.button_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="nsew")
        self.button_frame.configure(border_width=1, border_color="black")

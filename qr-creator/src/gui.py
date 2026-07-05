import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("File Drag and Drop")
        self.geometry("800x640")
        self.grid_columnconfigure((0, 1), weight=1)

        self.appearance = ctk.set_appearance_mode("system")

        self.button = ctk.CTkButton(self, text="my button", command=self.button_callback)
        self.button.grid(row=1, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
        self.checkbox_1 = ctk.CTkCheckBox(self, text="checkbox 1")
        self.checkbox_1.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")
        self.checkbox_2 = ctk.CTkCheckBox(self, text="checkbox 2")
        self.checkbox_2.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="w")

    def button_callback(self) -> None:
        print("button pressed")

# Consider adding this function to the App class, and only called on button click.
# see https://customtkinter.tomschimansky.com/documentation/windows/toplevel
def draw_window() -> None:
    def on_drop(event) -> str:
        files = app.tk.splitlist(event.data)
        entry.delete(0, "end")
        entry.insert(0, files[0])

    app = App()

    # Inject DnD into app root
    TkinterDnD.require(app)

    entry = ctk.CTkEntry(
        app, width=400, placeholder_text="Drag a file here..."
    )
    # below doesn't work with class grid setup
    # entry.pack(padx=20, pady=20)

    entry.drop_target_register(DND_FILES)
    entry.dnd_bind("<<Drop>>", on_drop)

    app.mainloop()

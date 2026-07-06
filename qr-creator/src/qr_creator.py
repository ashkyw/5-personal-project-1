import qrcode
import openpyxl
from gui import draw_window

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

def main():
    draw_window()

if __name__ == "__main__":
    main()

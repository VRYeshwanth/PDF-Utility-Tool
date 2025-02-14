import tkinter as tk
from utils import clear_window, FONT
import pdf_merger
import pdf_splitter
import pdf_rotater
import image_to_pdf

def show_main_menu():
    clear_window(root)

    # Title Label
    tk.Label(root, text="PDF Utilities", font=("Cascadia Code", 20, "bold")).grid(row=0, columnspan=2, padx=20, pady=20)
    # Buttons for each utility
    tk.Button(root, text="PDF Merger", font=FONT, width=25,
              command=lambda: pdf_merger.show_pdf_merger(root, show_main_menu)).grid(row=1, column=0, padx=20, pady=20)
    tk.Button(root, text="PDF Splitter", font=FONT, width=25,
              command=lambda: pdf_splitter.show_pdf_splitter(root, show_main_menu)).grid(row=1, column=1, padx=20, pady=20)
    tk.Button(root, text="PDF Rotater", font=FONT, width=25,
              command=lambda: pdf_rotater.show_pdf_rotater(root, show_main_menu)).grid(row=2, column=0, padx=20, pady=20)
    tk.Button(root, text="Image to PDF", font=FONT, width=25,
              command=lambda: image_to_pdf.show_image_to_pdf_converter(root, show_main_menu)).grid(row=2, column=1, padx=20, pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("PDF Utilities")
    root.resizable(0, 0)
    show_main_menu()
    root.mainloop()

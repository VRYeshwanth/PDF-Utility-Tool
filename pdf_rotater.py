import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter  # type: ignore
from utils import clear_window, FONT

def show_pdf_rotater(root, show_main_menu):
    clear_window(root)

    rotater_frame = tk.Frame(root)
    rotater_frame.pack(fill="both", expand=True, padx=25)
    tk.Label(rotater_frame, text="PDF Rotater", font=("Cascadia Code", 24, "bold")).pack(pady=10)

    inp_frame = tk.Frame(rotater_frame)
    inp_frame.pack(padx=20)
    tk.Label(inp_frame, text="Choose PDF :- ", font=("Cascadia Code", 14)).grid(row=0, column=0, sticky="W", pady=8)
    pdf_path = tk.StringVar()
    tk.Entry(inp_frame, textvariable=pdf_path, width=50, font=("Cascadia Code", 14)).grid(row=1, column=0, ipadx=2, ipady=5, pady=5)
    tk.Button(inp_frame, text="Browse", font=("Cascadia Code", 14), command=lambda: browse_file(pdf_path)).grid(row=1, column=1, padx=(5,10), ipadx=2, ipady=2)

    tk.Label(inp_frame, text="Pages (Comma Separated) :- ", font=("Cascadia Code", 14)).grid(row=2, column=0, sticky="W", pady=(5, 10))
    pages_val = tk.StringVar()
    tk.Entry(inp_frame, textvariable=pages_val, width=50, font=("Cascadia Code", 14)).grid(row=3, column=0, ipadx=2, ipady=5)

    tk.Label(inp_frame, text="Rotation Angle :- ", font=("Cascadia Code", 14)).grid(row=4, column=0, sticky="W", pady=(5, 2))
    options = ["90°", "180°", "270°"]
    menu_var = tk.StringVar(value="90°")
    option_menu = tk.OptionMenu(inp_frame, menu_var, *options)
    option_menu.grid(row=5, column=0, sticky="W", padx=(45, 0), pady=2)
    option_menu.config(font=("Cascadia Code", 14))
    option_menu["menu"].config(font=("Cascadia Code", 14))

    radio_frame = tk.Frame(inp_frame)
    radio_frame.grid(row=4, column=1, rowspan=2, padx=(50, 0))
    mode = tk.StringVar(value="Clockwise")
    tk.Radiobutton(radio_frame, text="Clockwise", variable=mode, value="Clockwise", font=("Cascadia Code", 14)).grid(row=0, column=0, sticky="W")
    tk.Radiobutton(radio_frame, text="Anticlockwise", variable=mode, value="Anticlockwise", font=("Cascadia Code", 14)).grid(row=1, column=0, sticky="W")

    tk.Button(rotater_frame, text="Rotate", font=("Cascadia Code", 14),
              command=lambda: rotate_pdf(pdf_path, pages_val, menu_var, mode)).pack(pady=(20, 10))
    tk.Button(rotater_frame, text="Back to Menu", font=FONT, command=show_main_menu).pack(pady=10)

    # Helper functions
    def browse_file(pdf_path):
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")], title="Select PDF")
        if file_path and file_path.endswith(".pdf"):
            pdf_path.set(file_path)
        else:
            messagebox.showerror("Error", "Please select a PDF file")

    def rotate_pdf(pdf_path, pages_val, menu_var, mode):
        file_path = pdf_path.get()
        pages = pages_val.get()
        angle_str = menu_var.get()
        rotation_mode = mode.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a PDF file.")
            return
        if not pages:
            messagebox.showerror("Error", "Please specify the pages to rotate.")
            return
        try:
            page_numbers = [int(page.strip()) - 1 for page in pages.split(",")]
        except ValueError:
            messagebox.showerror("Error", "Invalid page numbers format. Use comma-separated numbers.")
            return
        try:
            pdf_reader = PdfReader(file_path)
            total_pages = len(pdf_reader.pages)
            invalid_pages = [str(p + 1) for p in page_numbers if p < 0 or p >= total_pages]
            if invalid_pages:
                messagebox.showerror("Error", f"Invalid Page Numbers: {', '.join(invalid_pages)}")
                return
            pdf_writer = PdfWriter()
            angle = int(angle_str.replace("°", ""))
            for i in range(total_pages):
                page = pdf_reader.pages[i]
                if i in page_numbers:
                    if rotation_mode == "Anticlockwise":
                        page.rotate(-angle)
                    else:
                        page.rotate(angle)
                pdf_writer.add_page(page)
            output_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                       filetypes=[("PDF files", "*.pdf")],
                                                       title="Save Rotated PDF As")
            if output_path:
                with open(output_path, "wb") as output_pdf:
                    pdf_writer.write(output_pdf)
                messagebox.showinfo("Success", "PDF rotated successfully!")
            else:
                messagebox.showinfo("Cancelled", "Save operation cancelled.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate PDF.\n{e}")

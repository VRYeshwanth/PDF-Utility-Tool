import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter  # type: ignore
from utils import clear_window, FONT

def show_pdf_splitter(root, show_main_menu):
    clear_window(root)

    # Main Frame
    splitter_frame = tk.Frame(root)
    splitter_frame.pack(fill="both", expand=True, padx=25)

    # Header
    heading = tk.Label(splitter_frame, text="PDF Splitter", font=("Cascadia Code", 24, "bold"))
    heading.pack(pady=10)

    # Body for PDF file and directory selection
    body = tk.Frame(splitter_frame)
    body.pack(pady=10)
    tk.Label(body, text="Choose PDF :- ", font=("Cascadia Code", 15)).grid(row=0, column=0, sticky="W", pady=5)
    pdf_path = tk.StringVar()
    tk.Entry(body, textvariable=pdf_path, width=60, font=("Cascadia Code", 14)).grid(row=1, column=0, ipadx=2, ipady=5, pady=5)
    tk.Button(body, text="Browse", font=("Cascadia Code", 14), command=lambda: choose_pdf(pdf_path, page_count)).grid(row=1, column=1, padx=(5,10), ipadx=2, ipady=2)

    tk.Label(body, text="Choose Directory :- ", font=("Cascadia Code", 15)).grid(row=2, column=0, sticky="W", pady=5)
    dir_path = tk.StringVar()
    tk.Entry(body, textvariable=dir_path, width=60, font=("Cascadia Code", 14)).grid(row=3, column=0, ipadx=2, ipady=5, pady=5)
    tk.Button(body, text="Browse", font=("Cascadia Code", 14), command=lambda: choose_directory(dir_path)).grid(row=3, column=1, padx=(5,10), ipadx=2, ipady=2)

    tk.Label(body, text="Output File Name :- ", font=("Cascadia Code", 15)).grid(row=4, column=0, sticky="W", pady=5)
    output_fname = tk.StringVar()
    tk.Entry(body, textvariable=output_fname, width=60, font=("Cascadia Code", 14)).grid(row=5, column=0, ipadx=2, ipady=5, pady=5)

    # Page Range and Total Pages
    page_frame = tk.Frame(splitter_frame)
    page_frame.pack(pady=10)
    tk.Label(page_frame, text="Page Range :- ", font=("Cascadia Code", 15)).grid(row=0, column=0, sticky="W")
    range_var = tk.StringVar()
    tk.Entry(page_frame, textvariable=range_var, width=15, font=("Cascadia Code", 14)).grid(row=1, column=0, ipadx=2, ipady=5, sticky="W", pady=5)

    tk.Label(page_frame, text="Total Pages :- ", font=("Cascadia Code", 15)).grid(row=0, column=1, sticky="W", padx=(50,0))
    page_count = tk.IntVar()
    count_entry = tk.Entry(page_frame, width=10, font=("Cascadia Code", 14, "bold"), textvariable=page_count)
    count_entry.grid(row=1, column=1, ipadx=2, ipady=5, sticky="W", padx=(50,0))
    count_entry.config(state=tk.DISABLED)

    # Split and Back Buttons
    tk.Button(splitter_frame, text="Split", font=("Cascadia Code", 14), command=lambda: split_pdf(pdf_path, dir_path, output_fname, range_var)).pack(pady=(5,10), ipadx=2, ipady=2)
    tk.Button(splitter_frame, text="Back to Menu", font=FONT, command=show_main_menu).pack(pady=10)

    # Helper functions
    def choose_pdf(pdf_path, page_count):
        pdf_file = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF Files", "*.pdf")])
        if pdf_file and pdf_file.endswith(".pdf"):
            pdf_path.set(pdf_file)
            with open(pdf_file, "rb") as f:
                reader = PdfReader(f)
                page_count.set(len(reader.pages))
        else:
            messagebox.showerror("Error", "Please select a PDF file")

    def choose_directory(dir_path):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            dir_path.set(directory)

    def split_pdf(pdf_path, dir_path, output_fname, range_var):
        fpath = pdf_path.get()
        dpath = dir_path.get()
        filename = output_fname.get()
        p_range = range_var.get().strip()

        if not fpath or not dpath or not filename or not p_range:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            start_index, end_index = map(int, p_range.split('-'))
        except ValueError:
            messagebox.showerror("Error", "Invalid range format. Use format like '1-5'.")
            return

        try:
            with open(fpath, "rb") as f:
                reader = PdfReader(f)
                max_pages = len(reader.pages)
                if end_index > max_pages or start_index < 1:
                    messagebox.showerror("Error", f"Invalid range. The PDF contains {max_pages} pages.")
                    return

                writer = PdfWriter()
                for page_num in range(start_index - 1, end_index):
                    writer.add_page(reader.pages[page_num])

                output_path = f"{dpath}/{filename}.pdf"
                with open(output_path, "wb") as output_file:
                    writer.write(output_file)

                messagebox.showinfo("Success", f"PDF successfully split and saved as:\n{output_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred: {e}")

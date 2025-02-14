import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfWriter  # type: ignore
from utils import clear_window, FONT

def show_pdf_merger(root, show_main_menu):
    clear_window(root)

    # Title Label
    title = tk.Label(root, text="PDF Merger", font=("Cascadia Code", 24, "bold"))
    title.grid(row=0, columnspan=3, pady=10)

    # Instructions
    instructions = tk.Label(root, text="Add PDF files to merge by clicking 'Add PDF'.\nArrange the order and click 'Merge'.", font=FONT)
    instructions.grid(row=1, columnspan=3, pady=5)

    # Listbox
    list_frame = tk.Frame(root)
    list_frame.grid(row=2, columnspan=3, pady=10)
    box = tk.Listbox(list_frame, selectmode="multiple", font=FONT, height=10, width=70)
    box.pack(side="left", fill="both")

    # Scrollbar
    scrollbar = tk.Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")
    box.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=box.yview)

    # Buttons Frame
    buttons_frame = tk.Frame(root)
    buttons_frame.grid(row=3, columnspan=3, pady=10)
    tk.Button(buttons_frame, text="Add PDF", font=FONT, width=12, command=lambda: add_pdf(box)).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(buttons_frame, text="Merge", font=FONT, width=12, command=lambda: merge_pdf(box)).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(buttons_frame, text="Remove PDF", font=FONT, width=12, command=lambda: remove_pdf(box)).grid(row=0, column=2, padx=5, pady=5)
    tk.Button(buttons_frame, text="Move Up", font=FONT, width=12, command=lambda: move_up(box)).grid(row=1, column=0, padx=5, pady=5)
    tk.Button(buttons_frame, text="Move Down", font=FONT, width=12, command=lambda: move_down(box)).grid(row=1, column=2, padx=5, pady=5)

    # Back Button
    tk.Button(root, text="Back to Menu", font=FONT, width=15, command=show_main_menu).grid(row=4, columnspan=3, pady=20)

    # Helper functions
    def add_pdf(box):
        files = filedialog.askopenfilenames(title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")])
        for file in files:
            if file.endswith(".pdf"):
                box.insert(tk.END, file)

    def remove_pdf(box):
        selected_indices = box.curselection()
        for index in reversed(selected_indices):
            box.delete(index)

    def move_up(box):
        selected_indices = box.curselection()
        for i in selected_indices:
            if i == 0:
                continue
            text = box.get(i)
            box.delete(i)
            box.insert(i - 1, text)
            box.selection_set(i - 1)

    def move_down(box):
        selected_indices = box.curselection()
        for i in reversed(selected_indices):
            if i == box.size() - 1:
                continue
            text = box.get(i)
            box.delete(i)
            box.insert(i + 1, text)
            box.selection_set(i + 1)

    def merge_pdf(box):
        files = box.get(0, tk.END)
        if len(files) < 2:
            messagebox.showwarning("Warning", "Please add at least 2 files to merge")
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")],title="Save Merged PDF As")
        if not save_path:
            return
        try:
            with PdfWriter() as merger:
                for file in files:
                    with open(file, "rb") as f:
                        merger.append(f)
                with open(save_path, "wb") as f:
                    merger.write(f)
            messagebox.showinfo("Success", f"PDFs successfully merged and saved as:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during merging:\n{e}")

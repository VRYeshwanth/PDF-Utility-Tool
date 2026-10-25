import os
import sys
import subprocess
import tempfile
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from PyPDF2 import PdfReader, PdfWriter #type: ignore
from utils import FONT

# --------------------------------------------------
# Theme
# --------------------------------------------------

COLORS = {
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "text": "#172033",
    "secondary_text": "#64748B",
    "border": "#E2E8F0",
    "accent_background": "#EFF6FF",
    "success": "#15803D",
    "error": "#DC2626",
}


FONT_FAMILY = "Segoe UI"

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def format_file_size(size_bytes):
    """Convert bytes into a human-readable file size."""

    if size_bytes < 1024:
        return f"{size_bytes} B"

    if size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"

    if size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.2f} MB"

    return f"{size_bytes / (1024 ** 3):.2f} GB"


def parse_page_ranges(range_text, total_pages):
    """
    Parse page selections such as:
        1-3
        1, 4, 7
        1-3, 5, 8-10

    Returns zero-based page indexes in the specified order.
    """

    if not range_text.strip():
        raise ValueError("Enter at least one page number or page range.")

    selected_pages = []
    seen_pages = set()

    parts = range_text.split(",")

    for part in parts:
        part = part.strip()

        if not part:
            raise ValueError(
                "The page range contains an empty entry. "
                "Check the commas and try again."
            )

        if "-" in part:
            if part.count("-") != 1:
                raise ValueError(
                    f"Invalid range '{part}'. Use a format such as 2-5."
                )

            start_text, end_text = part.split("-", 1)

            if not start_text.strip().isdigit() or not end_text.strip().isdigit():
                raise ValueError(
                    f"Invalid range '{part}'. Use a format such as 2-5."
                )

            start_page = int(start_text.strip())
            end_page = int(end_text.strip())

            if start_page > end_page:
                raise ValueError(
                    f"In '{part}', the starting page exceeds the ending page."
                )

            pages = range(start_page, end_page + 1)

        else:
            if not part.isdigit():
                raise ValueError(
                    f"Invalid page number '{part}'. "
                    "Enter a page number such as 5."
                )

            pages = [int(part)]

        for page in pages:
            if page < 1 or page > total_pages:
                raise ValueError(
                    f"Page {page} is outside the valid range of "
                    f"1-{total_pages}."
                )

            if page in seen_pages:
                raise ValueError(
                    f"Page {page} is selected more than once. "
                    "Remove the duplicate page or range."
                )

            seen_pages.add(page)
            selected_pages.append(page - 1)

    return selected_pages


def open_pdf_file(path):
    """Open the resulting PDF using the system's default PDF viewer."""

    try:
        if sys.platform.startswith("win"):
            os.startfile(path)

        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])

        else:
            subprocess.Popen(["xdg-open", path])

    except Exception as error:
        messagebox.showwarning(
            "Unable to Open PDF",
            "The PDF was created successfully, but it could not be opened "
            f"automatically.\n\n{error}",
        )


# --------------------------------------------------
# PDF Splitter Interface
# --------------------------------------------------

def show_pdf_splitter(root, show_main_menu):

    # Clear the existing screen.
    for widget in root.winfo_children():
        widget.destroy()

    root.configure(bg=COLORS["background"])
    root.geometry("900x790")
    root.resizable(True, True)

    # Main container.
    main_frame = tk.Frame(
        root,
        bg=COLORS["background"],
        padx=35,
        pady=20,
    )
    main_frame.pack(fill="both", expand=True)

    # --------------------------------------------------
    # Heading
    # --------------------------------------------------

    tk.Label(
        main_frame,
        text="PDF Splitter",
        font=(FONT_FAMILY, 25, "bold"),
        bg=COLORS["background"],
        fg=COLORS["text"],
    ).pack(anchor="w")

    tk.Label(
        main_frame,
        text="Extract specific pages from a PDF into a new document.",
        font=(FONT_FAMILY, 11),
        bg=COLORS["background"],
        fg=COLORS["secondary_text"],
    ).pack(anchor="w", pady=(3, 20))

    # --------------------------------------------------
    # PDF Selection Section
    # --------------------------------------------------

    file_card = tk.Frame(
        main_frame,
        bg=COLORS["surface"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
        padx=20,
        pady=18,
    )
    file_card.pack(fill="x", pady=(0, 15))

    tk.Label(
        file_card,
        text="1. Select PDF",
        font=(FONT_FAMILY, 14, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
    ).pack(anchor="w", pady=(0, 10))

    pdf_path = tk.StringVar()

    file_row = tk.Frame(file_card, bg=COLORS["surface"])
    file_row.pack(fill="x")

    pdf_entry = tk.Entry(
        file_row,
        textvariable=pdf_path,
        font=(FONT_FAMILY, 10),
        bg="#F8FAFC",
        fg=COLORS["text"],
        relief="solid",
        bd=1,
        state="readonly",
        readonlybackground="#F8FAFC",
    )
    pdf_entry.pack(side="left", fill="x", expand=True, ipady=9)

    # --------------------------------------------------
    # PDF Information Panel
    # --------------------------------------------------

    info_card = tk.Frame(
        main_frame,
        bg=COLORS["accent_background"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
        padx=20,
        pady=15,
    )
    info_card.pack(fill="x", pady=(0, 15))

    tk.Label(
        info_card,
        text="PDF Information",
        font=(FONT_FAMILY, 13, "bold"),
        bg=COLORS["accent_background"],
        fg=COLORS["text"],
    ).pack(anchor="w", pady=(0, 10))

    info_grid = tk.Frame(info_card, bg=COLORS["accent_background"])
    info_grid.pack(fill="x")

    filename_value = tk.StringVar(value="No PDF selected")
    page_count_value = tk.StringVar(value="—")
    file_size_value = tk.StringVar(value="—")

    def create_info_item(parent, title, variable, column):
        item = tk.Frame(parent, bg=COLORS["accent_background"])
        item.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=(0 if column == 0 else 20, 10),
        )

        tk.Label(
            item,
            text=title,
            font=(FONT_FAMILY, 9),
            bg=COLORS["accent_background"],
            fg=COLORS["secondary_text"],
        ).pack(anchor="w")

        tk.Label(
            item,
            textvariable=variable,
            font=(FONT_FAMILY, 11, "bold"),
            bg=COLORS["accent_background"],
            fg=COLORS["text"],
            wraplength=240,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

    create_info_item(
        info_grid,
        "FILE NAME",
        filename_value,
        0,
    )

    create_info_item(
        info_grid,
        "TOTAL PAGES",
        page_count_value,
        1,
    )

    create_info_item(
        info_grid,
        "FILE SIZE",
        file_size_value,
        2,
    )

    info_grid.grid_columnconfigure(0, weight=2)
    info_grid.grid_columnconfigure(1, weight=1)
    info_grid.grid_columnconfigure(2, weight=1)

    # --------------------------------------------------
    # Output Settings
    # --------------------------------------------------

    output_card = tk.Frame(
        main_frame,
        bg=COLORS["surface"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
        padx=20,
        pady=18,
    )
    output_card.pack(fill="x", pady=(0, 15))

    tk.Label(
        output_card,
        text="2. Output Settings",
        font=(FONT_FAMILY, 14, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
    ).pack(anchor="w", pady=(0, 12))

    # Output directory.
    tk.Label(
        output_card,
        text="Output Directory",
        font=(FONT_FAMILY, 10, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
    ).pack(anchor="w")

    dir_path = tk.StringVar()

    directory_row = tk.Frame(output_card, bg=COLORS["surface"])
    directory_row.pack(fill="x", pady=(5, 12))

    tk.Entry(
        directory_row,
        textvariable=dir_path,
        font=(FONT_FAMILY, 10),
        bg="#F8FAFC",
        fg=COLORS["text"],
        relief="solid",
        bd=1,
    ).pack(side="left", fill="x", expand=True, ipady=8)

    def choose_directory():
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            parent=root,
        )

        if directory:
            dir_path.set(directory)

    tk.Button(
        directory_row,
        text="Browse",
        command=choose_directory,
        font=(FONT_FAMILY, 10, "bold"),
        bg=COLORS["accent_background"],
        fg=COLORS["primary"],
        activebackground="#DBEAFE",
        relief="flat",
        cursor="hand2",
        padx=14,
        pady=7,
    ).pack(side="left", padx=(8, 0))

    # Output filename.
    tk.Label(
        output_card,
        text="Output File Name",
        font=(FONT_FAMILY, 10, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
    ).pack(anchor="w")

    output_fname = tk.StringVar()

    tk.Entry(
        output_card,
        textvariable=output_fname,
        font=(FONT_FAMILY, 10),
        bg="#F8FAFC",
        fg=COLORS["text"],
        relief="solid",
        bd=1,
    ).pack(fill="x", ipady=8, pady=(5, 0))

    tk.Label(
        output_card,
        text="The .pdf extension will be added automatically.",
        font=(FONT_FAMILY, 9),
        bg=COLORS["surface"],
        fg=COLORS["secondary_text"],
    ).pack(anchor="w", pady=(4, 0))

    # --------------------------------------------------
    # Page Range Selection
    # --------------------------------------------------

    range_card = tk.Frame(
        main_frame,
        bg=COLORS["surface"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
        padx=20,
        pady=18,
    )
    range_card.pack(fill="x", pady=(0, 15))

    tk.Label(
        range_card,
        text="3. Select Pages",
        font=(FONT_FAMILY, 14, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
    ).pack(anchor="w", pady=(0, 5))

    tk.Label(
        range_card,
        text="Enter page numbers, ranges, or a combination of both.",
        font=(FONT_FAMILY, 10),
        bg=COLORS["surface"],
        fg=COLORS["secondary_text"],
    ).pack(anchor="w", pady=(0, 10))

    range_var = tk.StringVar()

    range_entry = tk.Entry(
        range_card,
        textvariable=range_var,
        font=(FONT_FAMILY, 12),
        bg="#F8FAFC",
        fg=COLORS["text"],
        relief="solid",
        bd=1,
    )
    range_entry.pack(fill="x", ipady=9)

    tk.Label(
        range_card,
        text="Examples: 1-5     |     2, 5, 8     |     1-3, 5, 8-10",
        font=(FONT_FAMILY, 10),
        bg=COLORS["surface"],
        fg=COLORS["primary"],
    ).pack(anchor="w", pady=(8, 3))

    tk.Label(
        range_card,
        text="Pages are extracted in the order you specify.",
        font=(FONT_FAMILY, 9),
        bg=COLORS["surface"],
        fg=COLORS["secondary_text"],
    ).pack(anchor="w")

    validation_message = tk.StringVar(
        value="Select a PDF to see its valid page range."
    )

    validation_label = tk.Label(
        range_card,
        textvariable=validation_message,
        font=(FONT_FAMILY, 9),
        bg=COLORS["surface"],
        fg=COLORS["secondary_text"],
        wraplength=750,
        justify="left",
    )
    validation_label.pack(anchor="w", pady=(8, 0))

    # --------------------------------------------------
    # Validation
    # --------------------------------------------------

    def validate_range(*_):
        total_pages_text = page_count_value.get()

        if total_pages_text == "—":
            validation_message.set(
                "Select a PDF to see its valid page range."
            )
            validation_label.config(fg=COLORS["secondary_text"])
            return

        text = range_var.get().strip()

        if not text:
            validation_message.set(
                f"Enter a page number or range between 1 and {total_pages_text}."
            )
            validation_label.config(fg=COLORS["secondary_text"])
            return

        try:
            pages = parse_page_ranges(text, int(total_pages_text))

            validation_message.set(
                f"Valid selection: {len(pages)} page(s) will be extracted."
            )
            validation_label.config(fg=COLORS["success"])

        except ValueError as error:
            validation_message.set(str(error))
            validation_label.config(fg=COLORS["error"])

    range_var.trace_add("write", validate_range)

    # --------------------------------------------------
    # File Selection
    # --------------------------------------------------

    def choose_pdf():
        selected_file = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF Files", "*.pdf")],
            parent=root,
        )

        if not selected_file:
            return

        try:
            reader = PdfReader(selected_file)

            if reader.is_encrypted:
                try:
                    result = reader.decrypt("")
                except Exception:
                    result = 0

                if not result:
                    messagebox.showerror(
                        "Encrypted PDF",
                        "This PDF is password-protected. "
                        "Please use an unencrypted PDF.",
                        parent=root,
                    )
                    return

            total_pages = len(reader.pages)

            if total_pages == 0:
                messagebox.showerror(
                    "Invalid PDF",
                    "The selected PDF does not contain any pages.",
                    parent=root,
                )
                return

            file_size = os.path.getsize(selected_file)

            pdf_path.set(selected_file)
            filename_value.set(Path(selected_file).name)
            page_count_value.set(str(total_pages))
            file_size_value.set(format_file_size(file_size))

            # Choose sensible defaults.
            dir_path.set(str(Path(selected_file).parent))
            output_fname.set(f"{Path(selected_file).stem}_split")

            # Reset the page range when a different PDF is selected.
            range_var.set("")

        except Exception as error:
            messagebox.showerror(
                "Unable to Read PDF",
                f"Could not read the selected PDF.\n\n{error}",
                parent=root,
            )

    tk.Button(
        file_row,
        text="Browse PDF",
        command=choose_pdf,
        font=(FONT_FAMILY, 10, "bold"),
        bg=COLORS["primary"],
        fg="#FFFFFF",
        activebackground=COLORS["primary_hover"],
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        padx=14,
        pady=8,
    ).pack(side="left", padx=(8, 0))

    # --------------------------------------------------
    # Split Operation
    # --------------------------------------------------

    def split_pdf():
        input_path = pdf_path.get().strip()
        output_directory = dir_path.get().strip()
        output_name = output_fname.get().strip()
        page_range = range_var.get().strip()

        # Required fields.
        if not input_path:
            messagebox.showerror(
                "Missing PDF",
                "Please select a PDF file.",
                parent=root,
            )
            return

        if not output_directory:
            messagebox.showerror(
                "Missing Output Directory",
                "Please select an output directory.",
                parent=root,
            )
            return

        if not output_name:
            messagebox.showerror(
                "Missing Filename",
                "Please enter a name for the output PDF.",
                parent=root,
            )
            return

        if not page_range:
            messagebox.showerror(
                "Missing Page Range",
                "Please enter the pages you want to extract.",
                parent=root,
            )
            return

        # Prevent invalid filename characters.
        if output_name in {".", ".."} or any(
            character in output_name for character in '<>:"/\\|?*'
        ):
            messagebox.showerror(
                "Invalid Filename",
                "The output filename contains invalid characters.",
                parent=root,
            )
            return

        if output_name.lower().endswith(".pdf"):
            output_name = output_name[:-4]

        if not output_name:
            messagebox.showerror(
                "Invalid Filename",
                "Please enter a valid output filename.",
                parent=root,
            )
            return

        if not os.path.isfile(input_path):
            messagebox.showerror(
                "File Not Found",
                "The selected PDF could not be found. Please select it again.",
                parent=root,
            )
            return

        if not os.path.isdir(output_directory):
            messagebox.showerror(
                "Invalid Directory",
                "The selected output directory does not exist.",
                parent=root,
            )
            return

        output_path = os.path.abspath(
            os.path.join(output_directory, f"{output_name}.pdf")
        )

        if os.path.abspath(input_path) == output_path:
            messagebox.showerror(
                "Invalid Output",
                "The output path cannot be the same as the input PDF. "
                "Choose a different filename.",
                parent=root,
            )
            return

        if os.path.exists(output_path):
            overwrite = messagebox.askyesno(
                "File Already Exists",
                f"A file named '{os.path.basename(output_path)}' already exists.\n\n"
                "Do you want to replace it?",
                parent=root,
            )

            if not overwrite:
                return

        temporary_path = None

        try:
            with open(input_path, "rb") as input_file:
                reader = PdfReader(input_file)

                if reader.is_encrypted:
                    try:
                        result = reader.decrypt("")
                    except Exception:
                        result = 0

                    if not result:
                        messagebox.showerror(
                            "Encrypted PDF",
                            "This PDF requires a password and cannot be "
                            "processed without it.",
                            parent=root,
                        )
                        return

                total_pages = len(reader.pages)

                # Validate the selection against the actual PDF.
                selected_pages = parse_page_ranges(
                    page_range,
                    total_pages,
                )

                writer = PdfWriter()

                for page_index in selected_pages:
                    writer.add_page(reader.pages[page_index])

                # Write to a temporary file first to avoid leaving a
                # partially written output if the operation fails.
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    suffix=".pdf",
                    prefix="pdf_split_",
                    dir=output_directory,
                    delete=False,
                ) as temporary_file:
                    temporary_path = temporary_file.name
                    writer.write(temporary_file)

            # Replace the destination only after the PDF is written.
            os.replace(temporary_path, output_path)
            temporary_path = None

            messagebox.showinfo(
                "Split Complete",
                f"Successfully extracted {len(selected_pages)} page(s).\n\n"
                f"Saved to:\n{output_path}\n\n"
                "Opening the resulting PDF...",
                parent=root,
            )

            open_pdf_file(output_path)

        except ValueError as error:
            messagebox.showerror(
                "Invalid Page Range",
                str(error),
                parent=root,
            )

        except Exception as error:
            messagebox.showerror(
                "Split Failed",
                f"An error occurred while splitting the PDF.\n\n{error}",
                parent=root,
            )

        finally:
            if temporary_path and os.path.exists(temporary_path):
                try:
                    os.remove(temporary_path)
                except OSError:
                    pass

    # --------------------------------------------------
    # Bottom Buttons
    # --------------------------------------------------

    button_frame = tk.Frame(
        main_frame,
        bg=COLORS["background"],
    )
    button_frame.pack(fill="x", pady=(0, 5))

    tk.Button(
        button_frame,
        text="← Back to Menu",
        command=show_main_menu,
        font=(FONT_FAMILY, 10, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
        activebackground="#E2E8F0",
        relief="flat",
        cursor="hand2",
        padx=18,
        pady=11,
    ).pack(side="left")

    tk.Button(
        button_frame,
        text="Extract Pages",
        command=split_pdf,
        font=(FONT_FAMILY, 11, "bold"),
        bg=COLORS["primary"],
        fg="#FFFFFF",
        activebackground=COLORS["primary_hover"],
        activeforeground="#FFFFFF",
        relief="flat",
        cursor="hand2",
        padx=24,
        pady=11,
    ).pack(side="right")

    # Initial focus.
    range_entry.focus_set()
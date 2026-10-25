import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

from PyPDF2 import PdfReader, PdfWriter  # type: ignore
from utils import (COLORS, BG_COLOR, CARD_COLOR, PRIMARY_COLOR, PRIMARY_HOVER, LIGHT_BLUE, TEXT_COLOR, MUTED_COLOR, BORDER_COLOR, SUCCESS_COLOR, ERROR_COLOR, FONT_FAMILY, FONT, TITLE_FONT, SECTION_FONT, SUBSECTION_FONT, BODY_FONT, SMALL_FONT, BOLD_BUTTON_FONT, clear_window, create_card as shared_create_card, create_label as shared_create_label, create_button as shared_create_button, configure_ttk_styles)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def format_file_size(size_bytes):
    """Convert a file size in bytes into a readable string."""
    size = float(size_bytes)

    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} TB"


def parse_page_ranges(page_text, total_pages):
    """
    Parse page selections such as:
        1,3,5
        1-5
        1-3, 5, 8-10

    Page numbers are 1-indexed.
    Duplicate selections are ignored.
    The returned list contains zero-indexed page numbers.
    """
    page_text = page_text.strip()

    if not page_text:
        raise ValueError("Enter the pages you want to rotate.")

    selected_pages = []
    seen_pages = set()

    parts = page_text.split(",")

    for part in parts:
        part = part.strip()

        if not part:
            raise ValueError(
                "The page selection contains an empty entry. "
                "Use a format such as 1-3, 5, 8-10."
            )

        if "-" in part:
            if part.count("-") != 1:
                raise ValueError(
                    f"Invalid page range '{part}'. "
                    "Use a format such as 1-5."
                )

            start_text, end_text = part.split("-", 1)
            start_text = start_text.strip()
            end_text = end_text.strip()

            if not start_text.isdigit() or not end_text.isdigit():
                raise ValueError(
                    f"Invalid page range '{part}'. "
                    "Use positive page numbers."
                )

            start_page = int(start_text)
            end_page = int(end_text)

            if start_page < 1 or end_page < 1:
                raise ValueError("Page numbers must be greater than zero.")

            if start_page > end_page:
                raise ValueError(
                    f"Invalid range '{part}'. "
                    "The starting page must not exceed the ending page."
                )

            pages_in_part = range(start_page, end_page + 1)

        else:
            if not part.isdigit():
                raise ValueError(
                    f"Invalid page number '{part}'. "
                    "Use a format such as 1, 3, 5."
                )

            page_number = int(part)

            if page_number < 1:
                raise ValueError("Page numbers must be greater than zero.")

            pages_in_part = [page_number]

        for page_number in pages_in_part:
            if page_number > total_pages:
                raise ValueError(
                    f"Page {page_number} does not exist. "
                    f"This PDF contains {total_pages} pages."
                )

            zero_indexed_page = page_number - 1

            # Avoid rotating the same page more than once.
            if zero_indexed_page not in seen_pages:
                seen_pages.add(zero_indexed_page)
                selected_pages.append(zero_indexed_page)

    if not selected_pages:
        raise ValueError("Select at least one page to rotate.")

    return selected_pages


def open_pdf_file(file_path):
    """Open a PDF using the operating system's default PDF viewer."""
    if sys.platform.startswith("win"):
        os.startfile(file_path)  # type: ignore[attr-defined]

    elif sys.platform == "darwin":
        subprocess.Popen(["open", file_path])

    else:
        subprocess.Popen(["xdg-open", file_path])


# --------------------------------------------------
# MAIN PDF ROTATER INTERFACE
# --------------------------------------------------

def show_pdf_rotater(root, show_main_menu):
    clear_window(root)
    configure_ttk_styles(root)

    root.configure(bg=BG_COLOR)

    # Stores the currently loaded PDF information.
    pdf_state = {
        "path": None,
        "reader": None,
        "total_pages": 0,
        "size": 0,
    }

    pdf_path = tk.StringVar()
    pages_val = tk.StringVar()

    angle_var = tk.StringVar(value="90°")
    direction_var = tk.StringVar(value="Clockwise")

    validation_var = tk.StringVar(
        value="Select a PDF to begin."
    )

    validation_color = MUTED_COLOR

    # --------------------------------------------------
    # GENERAL WIDGET HELPERS
    # --------------------------------------------------

    def create_card(parent, **kwargs):
        return shared_create_card(parent, **kwargs)

    def create_label(
        parent, text, font=BODY_FONT, fg=TEXT_COLOR, bg=CARD_COLOR, **kwargs
    ):
        return shared_create_label(parent, text, font=font, fg=fg, bg=bg, **kwargs)

    def create_button(parent, text, command, primary=False, **kwargs):
        return shared_create_button(
            parent, text, command,
            variant="primary" if primary else "secondary",
            padx=16, pady=9, **kwargs
        )

    def set_validation(message, color=MUTED_COLOR):
        validation_var.set(message)
        validation_label.config(fg=color)

    # --------------------------------------------------
    # PAGE VALIDATION
    # --------------------------------------------------

    def validate_page_selection(*_):
        """
        Validate the page selection whenever its text changes.
        The Rotate button is enabled only when the selection is valid.
        """
        current_path = pdf_path.get().strip()
        page_text = pages_val.get()

        if not current_path:
            rotate_button.config(state="disabled")
            set_validation("Select a PDF to begin.")
            return

        total_pages = pdf_state["total_pages"]

        if not total_pages:
            rotate_button.config(state="disabled")
            set_validation("Load a valid PDF before selecting pages.")
            return

        if not page_text.strip():
            rotate_button.config(state="disabled")
            set_validation(
                f"Enter pages to rotate. Total pages: {total_pages}."
            )
            return

        try:
            selected_pages = parse_page_ranges(
                page_text,
                total_pages,
            )

            rotate_button.config(state="normal")

            set_validation(
                f"✓ {len(selected_pages)} page(s) selected.",
                SUCCESS_COLOR,
            )

        except ValueError as error:
            rotate_button.config(state="disabled")
            set_validation(str(error), ERROR_COLOR)

    # --------------------------------------------------
    # PDF INFORMATION PANEL
    # --------------------------------------------------

    def reset_pdf_information():
        pdf_state["path"] = None
        pdf_state["reader"] = None
        pdf_state["total_pages"] = 0
        pdf_state["size"] = 0

        filename_value.config(text="No PDF selected")
        page_count_value.config(text="—")
        file_size_value.config(text="—")

        rotate_button.config(state="disabled")

        set_validation("Select a PDF to begin.")

    def load_pdf(file_path):
        """
        Load the selected PDF and update the information panel.
        Return True if the document can be read.
        """
        if not file_path:
            return False

        if not os.path.isfile(file_path):
            messagebox.showerror(
                "File Not Found",
                "The selected PDF file could not be found.",
                parent=root,
            )
            return False

        if not file_path.lower().endswith(".pdf"):
            messagebox.showerror(
                "Invalid File",
                "Please select a file with a .pdf extension.",
                parent=root,
            )
            return False

        try:
            reader = PdfReader(file_path)

            if reader.is_encrypted:
                raise ValueError(
                    "This PDF is encrypted or password-protected. "
                    "Please select an unprotected PDF."
                )

            total_pages = len(reader.pages)

            if total_pages == 0:
                raise ValueError(
                    "The selected PDF does not contain any pages."
                )

            file_size = os.path.getsize(file_path)

            pdf_state["path"] = os.path.abspath(file_path)
            pdf_state["reader"] = reader
            pdf_state["total_pages"] = total_pages
            pdf_state["size"] = file_size

            filename_value.config(
                text=os.path.basename(file_path)
            )

            page_count_value.config(
                text=str(total_pages)
            )

            file_size_value.config(
                text=format_file_size(file_size)
            )

            validate_page_selection()

            return True

        except Exception as error:
            reset_pdf_information()

            messagebox.showerror(
                "Unable to Read PDF",
                f"The selected PDF could not be opened.\n\n{error}",
                parent=root,
            )

            return False

    # --------------------------------------------------
    # FILE BROWSING
    # --------------------------------------------------

    def browse_file():
        file_path = filedialog.askopenfilename(
            parent=root,
            title="Select PDF to Rotate",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("All files", "*.*"),
            ],
        )

        if not file_path:
            return

        pdf_path.set(file_path)

        # Clear the old selection when switching documents.
        pages_val.set("")

        if not load_pdf(file_path):
            pdf_path.set("")
            reset_pdf_information()
            return

        # Load the new PDF before validating the page selection.
        validate_page_selection()

    # --------------------------------------------------
    # ROTATION PROCESSING
    # --------------------------------------------------

    def rotate_pdf():
        file_path = pdf_path.get().strip()
        page_text = pages_val.get().strip()

        if not file_path:
            messagebox.showerror(
                "Missing PDF",
                "Please select a PDF file first.",
                parent=root,
            )
            return

        # Reload the document if the path changed.
        if (
            pdf_state["path"] != os.path.abspath(file_path)
            or pdf_state["reader"] is None
        ):
            if not load_pdf(file_path):
                return

        reader = pdf_state["reader"]
        total_pages = pdf_state["total_pages"]

        try:
            selected_pages = set(
                parse_page_ranges(page_text, total_pages)
            )

        except ValueError as error:
            messagebox.showerror(
                "Invalid Page Selection",
                str(error),
                parent=root,
            )
            return

        # A positive PyPDF2 rotation angle is clockwise.
        angle = int(angle_var.get().replace("°", ""))

        if direction_var.get() == "Anticlockwise":
            angle = -angle

        # Generate a useful default filename.
        input_directory = os.path.dirname(file_path)
        input_filename = os.path.splitext(
            os.path.basename(file_path)
        )[0]

        default_filename = f"{input_filename}_rotated.pdf"

        # Ask the user where to save the output.
        output_path = filedialog.asksaveasfilename(
            parent=root,
            title="Save Rotated PDF",
            initialdir=input_directory,
            initialfile=default_filename,
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
            ],
        )

        # Cancelling the dialog should not be treated as an error.
        if not output_path:
            return

        output_path = os.path.abspath(output_path)

        # Prevent accidental replacement of the original document.
        if os.path.normcase(output_path) == os.path.normcase(
            os.path.abspath(file_path)
        ):
            messagebox.showerror(
                "Invalid Output Location",
                "The output file cannot be the same as the original PDF.\n\n"
                "Choose a different filename to preserve the source document.",
                parent=root,
            )
            return

        # Confirm overwriting an existing output file.
        if os.path.exists(output_path):
            overwrite = messagebox.askyesno(
                "Confirm Overwrite",
                f"The following file already exists:\n\n"
                f"{output_path}\n\n"
                "Do you want to replace it?",
                icon="warning",
                parent=root,
            )

            if not overwrite:
                return

        try:
            writer = PdfWriter()

            # Process the input pages in their original order.
            # Only the selected pages are rotated.
            for index in range(total_pages):
                page = reader.pages[index]

                if index in selected_pages:
                    page.rotate(angle)

                writer.add_page(page)

            # Write the output only after the PDF is fully prepared.
            with open(output_path, "wb") as output_pdf:
                writer.write(output_pdf)

            messagebox.showinfo(
                "Rotation Complete",
                f"PDF rotated successfully!\n\n"
                f"Pages rotated: {len(selected_pages)}\n"
                f"Rotation: {angle_var.get()} "
                f"{direction_var.get().lower()}\n\n"
                f"Saved to:\n{output_path}",
                parent=root,
            )

            # Automatically open the resulting PDF.
            try:
                open_pdf_file(output_path)

            except Exception as error:
                messagebox.showwarning(
                    "PDF Saved",
                    "The PDF was saved successfully, but it could not "
                    f"be opened automatically.\n\n{error}\n\n"
                    "You can open it manually from:\n"
                    f"{output_path}",
                    parent=root,
                )

        except Exception as error:
            messagebox.showerror(
                "Rotation Failed",
                "The PDF could not be rotated or saved.\n\n"
                f"Details: {error}",
                parent=root,
            )

    # --------------------------------------------------
    # MAIN LAYOUT
    # --------------------------------------------------

    main_frame = tk.Frame(
        root,
        bg=BG_COLOR,
    )

    main_frame.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=20,
    )

    # Header
    header_frame = tk.Frame(
        main_frame,
        bg=BG_COLOR,
    )

    header_frame.pack(
        fill="x",
        pady=(0, 18),
    )

    create_label(
        header_frame,
        "PDF Rotater",
        font=TITLE_FONT,
        bg=BG_COLOR,
    ).pack(anchor="w")

    create_label(
        header_frame,
        "Rotate selected pages in your PDF document.",
        font=BODY_FONT,
        fg=MUTED_COLOR,
        bg=BG_COLOR,
    ).pack(anchor="w", pady=(4, 0))

    # --------------------------------------------------
    # SECTION 1: PDF SELECTION
    # --------------------------------------------------

    file_card = create_card(main_frame)
    file_card.pack(fill="x", pady=(0, 14))

    file_content = tk.Frame(
        file_card,
        bg=CARD_COLOR,
    )

    file_content.pack(
        fill="x",
        padx=20,
        pady=18,
    )

    create_label(
        file_content,
        "1. Select PDF",
        font=SECTION_FONT,
    ).pack(anchor="w", pady=(0, 12))

    browse_row = tk.Frame(
        file_content,
        bg=CARD_COLOR,
    )

    browse_row.pack(fill="x")

    pdf_entry = tk.Entry(
        browse_row,
        textvariable=pdf_path,
        font=BODY_FONT,
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        highlightcolor=PRIMARY_COLOR,
        bg="#FFFFFF",
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
    )

    pdf_entry.pack(
        side="left",
        fill="x",
        expand=True,
        ipady=8,
        padx=(0, 10),
    )

    # Prevent manual path edits from leaving stale document metadata.
    pdf_entry.config(state="readonly")

    create_button(
        browse_row,
        "Browse PDF",
        browse_file,
    ).pack(side="right")

    # --------------------------------------------------
    # SECTION 2: PDF INFORMATION
    # --------------------------------------------------

    info_card = create_card(main_frame)
    info_card.pack(fill="x", pady=(0, 14))

    info_content = tk.Frame(
        info_card,
        bg=CARD_COLOR,
    )

    info_content.pack(
        fill="x",
        padx=20,
        pady=16,
    )

    create_label(
        info_content,
        "PDF Information",
        font=SECTION_FONT,
    ).pack(anchor="w", pady=(0, 12))

    info_grid = tk.Frame(
        info_content,
        bg=CARD_COLOR,
    )

    info_grid.pack(fill="x")

    info_grid.columnconfigure(0, weight=3)
    info_grid.columnconfigure(1, weight=1)
    info_grid.columnconfigure(2, weight=1)

    # Filename
    filename_frame = tk.Frame(
        info_grid,
        bg=LIGHT_BLUE,
    )

    filename_frame.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(0, 8),
    )

    create_label(
        filename_frame,
        "FILENAME",
        font=SMALL_FONT,
        fg=MUTED_COLOR,
        bg=LIGHT_BLUE,
    ).pack(anchor="w", padx=12, pady=(10, 3))

    filename_value = create_label(
        filename_frame,
        "No PDF selected",
        font=BOLD_BUTTON_FONT,
        bg=LIGHT_BLUE,
        wraplength=300,
        justify="left",
        anchor="w",
    )

    filename_value.pack(
        anchor="w",
        padx=12,
        pady=(0, 10),
        fill="x",
    )

    # Page count
    page_count_frame = tk.Frame(
        info_grid,
        bg=LIGHT_BLUE,
    )

    page_count_frame.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=4,
    )

    create_label(
        page_count_frame,
        "TOTAL PAGES",
        font=SMALL_FONT,
        fg=MUTED_COLOR,
        bg=LIGHT_BLUE,
    ).pack(anchor="w", padx=12, pady=(10, 3))

    page_count_value = create_label(
        page_count_frame,
        "—",
        font=SUBSECTION_FONT,
        bg=LIGHT_BLUE,
    )

    page_count_value.pack(
        anchor="w",
        padx=12,
        pady=(0, 10),
    )

    # File size
    file_size_frame = tk.Frame(
        info_grid,
        bg=LIGHT_BLUE,
    )

    file_size_frame.grid(
        row=0,
        column=2,
        sticky="nsew",
        padx=(8, 0),
    )

    create_label(
        file_size_frame,
        "FILE SIZE",
        font=SMALL_FONT,
        fg=MUTED_COLOR,
        bg=LIGHT_BLUE,
    ).pack(anchor="w", padx=12, pady=(10, 3))

    file_size_value = create_label(
        file_size_frame,
        "—",
        font=BOLD_BUTTON_FONT,
        bg=LIGHT_BLUE,
    )

    file_size_value.pack(
        anchor="w",
        padx=12,
        pady=(0, 10),
    )

    # --------------------------------------------------
    # SECTION 3: ROTATION SETTINGS
    # --------------------------------------------------

    settings_card = create_card(main_frame)
    settings_card.pack(fill="x", pady=(0, 14))

    settings_content = tk.Frame(
        settings_card,
        bg=CARD_COLOR,
    )

    settings_content.pack(
        fill="x",
        padx=20,
        pady=18,
    )

    create_label(
        settings_content,
        "2. Rotation Settings",
        font=SECTION_FONT,
    ).pack(anchor="w", pady=(0, 12))

    # Page selection
    create_label(
        settings_content,
        "Pages to rotate",
        font=BOLD_BUTTON_FONT,
    ).pack(anchor="w")

    create_label(
        settings_content,
        "Enter individual pages or ranges. Example: 1-3, 5, 8-10",
        font=SMALL_FONT,
        fg=MUTED_COLOR,
    ).pack(anchor="w", pady=(3, 8))

    pages_entry = tk.Entry(
        settings_content,
        textvariable=pages_val,
        font=BODY_FONT,
        relief="solid",
        bd=1,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        highlightcolor=PRIMARY_COLOR,
        bg="#FFFFFF",
        fg=TEXT_COLOR,
        insertbackground=TEXT_COLOR,
    )

    pages_entry.pack(
        fill="x",
        ipady=8,
    )

    validation_label = tk.Label(
        settings_content,
        textvariable=validation_var,
        font=SMALL_FONT,
        fg=MUTED_COLOR,
        bg=CARD_COLOR,
        anchor="w",
        justify="left",
        wraplength=650,
    )

    validation_label.pack(
        anchor="w",
        fill="x",
        pady=(7, 14),
    )

    # Angle and direction controls
    options_frame = tk.Frame(
        settings_content,
        bg=CARD_COLOR,
    )

    options_frame.pack(fill="x")

    options_frame.columnconfigure(0, weight=1)
    options_frame.columnconfigure(1, weight=1)

    # Rotation angle
    angle_frame = tk.Frame(
        options_frame,
        bg=CARD_COLOR,
    )

    angle_frame.grid(
        row=0,
        column=0,
        sticky="nw",
        padx=(0, 20),
    )

    create_label(
        angle_frame,
        "Rotation angle",
        font=BOLD_BUTTON_FONT,
    ).pack(anchor="w", pady=(0, 8))

    angle_options = tk.Frame(
        angle_frame,
        bg=CARD_COLOR,
    )

    angle_options.pack(anchor="w")

    for angle_option in ("90°", "180°", "270°"):
        tk.Radiobutton(
            angle_options,
            text=angle_option,
            variable=angle_var,
            value=angle_option,
            font=BODY_FONT,
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            activebackground=CARD_COLOR,
            selectcolor=LIGHT_BLUE,
            cursor="hand2",
        ).pack(
            side="left",
            padx=(0, 12),
        )

    # Rotation direction
    direction_frame = tk.Frame(
        options_frame,
        bg=CARD_COLOR,
    )

    direction_frame.grid(
        row=0,
        column=1,
        sticky="nw",
    )

    create_label(
        direction_frame,
        "Direction",
        font=BOLD_BUTTON_FONT,
    ).pack(anchor="w", pady=(0, 8))

    tk.Radiobutton(
        direction_frame,
        text="Clockwise",
        variable=direction_var,
        value="Clockwise",
        font=BODY_FONT,
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        activebackground=CARD_COLOR,
        selectcolor=LIGHT_BLUE,
        cursor="hand2",
    ).pack(anchor="w")

    tk.Radiobutton(
        direction_frame,
        text="Anticlockwise",
        variable=direction_var,
        value="Anticlockwise",
        font=BODY_FONT,
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        activebackground=CARD_COLOR,
        selectcolor=LIGHT_BLUE,
        cursor="hand2",
    ).pack(anchor="w")

    # --------------------------------------------------
    # ACTION BUTTONS
    # --------------------------------------------------

    action_frame = tk.Frame(
        main_frame,
        bg=BG_COLOR,
    )

    action_frame.pack(
        fill="x",
        pady=(4, 0),
    )

    back_button = create_button(
        action_frame,
        "← Back to Menu",
        show_main_menu,
    )

    back_button.pack(side="left")

    rotate_button = create_button(
        action_frame,
        "Rotate PDF",
        rotate_pdf,
        primary=True,
        state="disabled",
    )

    rotate_button.pack(side="right")

    # --------------------------------------------------
    # EVENT BINDINGS
    # --------------------------------------------------

    pages_val.trace_add(
        "write",
        validate_page_selection,
    )

    # Initial state
    reset_pdf_information()
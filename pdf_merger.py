import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PyPDF2 import PdfReader, PdfWriter #type: ignore

from utils import clear_window


# =========================
# Configuration
# =========================

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
}

FONT_FAMILY = "Segoe UI"


def show_pdf_merger(root, show_main_menu):
    clear_window(root)
    root.configure(bg=COLORS["background"])

    # =========================
    # Main Layout
    # =========================

    main_frame = tk.Frame(root, bg=COLORS["background"])
    main_frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=22)

    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_rowconfigure(3, weight=1)

    # =========================
    # Header
    # =========================

    tk.Label(
        main_frame,
        text="Merge PDFs",
        font=(FONT_FAMILY, 23, "bold"),
        bg=COLORS["background"],
        fg=COLORS["text"],
    ).grid(row=0, column=0, sticky="w", pady=(0, 5))

    tk.Label(
        main_frame,
        text="Combine multiple PDF documents into one file.",
        font=(FONT_FAMILY, 10),
        bg=COLORS["background"],
        fg=COLORS["secondary_text"],
    ).grid(row=1, column=0, sticky="w", pady=(0, 20))

    # =========================
    # File List Section
    # =========================

    list_section = tk.Frame(
        main_frame,
        bg=COLORS["surface"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
    )

    list_section.grid(row=2, column=0, sticky="nsew")
    list_section.grid_columnconfigure(0, weight=1)
    list_section.grid_rowconfigure(1, weight=1)

    list_header = tk.Frame(list_section, bg=COLORS["surface"])
    list_header.grid(
        row=0, column=0, columnspan=2,
        sticky="ew", padx=18, pady=(16, 10)
    )
    list_header.grid_columnconfigure(0, weight=1)

    count_label = tk.Label(
        list_header,
        text="Selected files (0)",
        font=(FONT_FAMILY, 12, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
    )
    count_label.grid(row=0, column=0, sticky="w")

    tk.Label(
        list_header,
        text="Files will be merged in the order shown.",
        font=(FONT_FAMILY, 9),
        bg=COLORS["surface"],
        fg=COLORS["secondary_text"],
    ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    # Treeview displaying filename, pages, and size.
    columns = ("filename", "pages", "size")

    style = ttk.Style(root)
    style.configure(
        "Merger.Treeview",
        font=(FONT_FAMILY, 10),
        rowheight=32,
    )
    style.configure(
        "Merger.Treeview.Heading",
        font=(FONT_FAMILY, 10, "bold"),
    )

    table_frame = tk.Frame(list_section, bg=COLORS["surface"])
    table_frame.grid(
        row=1, column=0, columnspan=2,
        sticky="nsew", padx=18
    )
    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_rowconfigure(0, weight=1)

    box = ttk.Treeview(
        table_frame,
        columns=columns,
        show="headings",
        selectmode="extended",
        style="Merger.Treeview",
    )

    box.heading("filename", text="File Name")
    box.heading("pages", text="Pages")
    box.heading("size", text="Size")

    box.column("filename", width=380, minwidth=180, anchor="w")
    box.column("pages", width=80, minwidth=60, anchor="center")
    box.column("size", width=100, minwidth=80, anchor="center")

    scrollbar = ttk.Scrollbar(
        table_frame,
        orient="vertical",
        command=box.yview,
    )
    box.configure(yscrollcommand=scrollbar.set)

    box.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    # Store the full path separately from the displayed filename.
    file_paths = {}

    # =========================
    # Status
    # =========================

    status_label = tk.Label(
        list_section,
        text="Add at least two PDF files to get started.",
        font=(FONT_FAMILY, 9),
        bg=COLORS["surface"],
        fg=COLORS["secondary_text"],
        anchor="w",
    )

    status_label.grid(
        row=2, column=0, columnspan=2,
        sticky="ew", padx=18, pady=(10, 16)
    )

    # =========================
    # Helper Functions
    # =========================

    def update_file_count():
        count = len(box.get_children())
        count_label.configure(text=f"Selected files ({count})")

    def get_selected_indices():
        items = list(box.get_children())
        selected = set(box.selection())

        return [
            index
            for index, item in enumerate(items)
            if item in selected
        ]

    def add_pdf():
        files = filedialog.askopenfilenames(
            parent=root,
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf")],
        )

        if not files:
            return

        existing_paths = {
            os.path.normcase(os.path.abspath(path))
            for path in file_paths.values()
        }

        added = 0
        skipped = 0

        for path in files:
            if not os.path.isfile(path):
                skipped += 1
                continue

            if not path.lower().endswith(".pdf"):
                skipped += 1
                continue

            normalized_path = os.path.normcase(os.path.abspath(path))

            if normalized_path in existing_paths:
                skipped += 1
                continue

            try:
                with open(path, "rb") as pdf_file:
                    reader = PdfReader(pdf_file, strict=False)

                    if reader.is_encrypted:
                        # Attempt to open PDFs that use an empty password.
                        if reader.decrypt(""):
                            page_count = len(reader.pages)
                        else:
                            skipped += 1
                            continue
                    else:
                        page_count = len(reader.pages)

                size_bytes = os.path.getsize(path)
                size_mb = size_bytes / (1024 * 1024)

                item_id = box.insert(
                    "",
                    tk.END,
                    values=(
                        os.path.basename(path),
                        page_count,
                        f"{size_mb:.2f} MB",
                    ),
                )

                file_paths[item_id] = path
                existing_paths.add(normalized_path)
                added += 1

            except Exception:
                skipped += 1

        update_file_count()

        if added:
            status_label.configure(
                text=f"Added {added} PDF file(s).",
                fg=COLORS["success"],
            )

        if skipped:
            messagebox.showwarning(
                "Some files were skipped",
                f"{skipped} file(s) were skipped because they were "
                "duplicates, unreadable, encrypted with an unsupported "
                "password, or not valid PDFs.",
                parent=root,
            )

    def remove_selected():
        selected_items = box.selection()

        if not selected_items:
            messagebox.showinfo(
                "No selection",
                "Select one or more files to remove.",
                parent=root,
            )
            return

        for item in selected_items:
            box.delete(item)
            file_paths.pop(item, None)

        update_file_count()

        status_label.configure(
            text="Selected files removed.",
            fg=COLORS["secondary_text"],
        )

    def clear_all():
        if not box.get_children():
            return

        if not messagebox.askyesno(
            "Clear all files",
            "Remove all selected PDFs?",
            parent=root,
        ):
            return

        for item in box.get_children():
            box.delete(item)

        file_paths.clear()
        update_file_count()

        status_label.configure(
            text="All files cleared.",
            fg=COLORS["secondary_text"],
        )

    def select_all():
        items = box.get_children()

        if items:
            box.selection_set(items)

    def move_up():
        items = list(box.get_children())
        selected_indices = get_selected_indices()

        if not selected_indices:
            return

        # Process from top to bottom so consecutive selections
        # retain their relative order.
        for index in selected_indices:
            if index == 0:
                continue

            current_item = items[index]
            previous_item = items[index - 1]

            box.move(current_item, "", index - 1)
            items[index - 1], items[index] = current_item, previous_item

        box.selection_set(
            [items[index - 1] if index > 0 else items[index]
             for index in selected_indices]
        )

    def move_down():
        items = list(box.get_children())
        selected_indices = get_selected_indices()

        if not selected_indices:
            return

        # Process from bottom to top to preserve the order of
        # consecutive selections.
        for index in reversed(selected_indices):
            if index >= len(items) - 1:
                continue

            current_item = items[index]
            next_item = items[index + 1]

            box.move(current_item, "", index + 1)
            items[index], items[index + 1] = next_item, current_item

        box.selection_set(
            [items[index + 1] if index < len(items) - 1 else items[index]
             for index in selected_indices]
        )

    def open_pdf_file(path):
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

        except Exception as error:
            messagebox.showerror(
                "Unable to Open PDF",
                f"The PDF was merged successfully, but could not be opened.\n\n{error}",
                parent=root,
            )

    def merge_pdf():
        items = list(box.get_children())

        if len(items) < 2:
            messagebox.showwarning(
                "Not enough files",
                "Please add at least two PDF files to merge.",
                parent=root,
            )
            return

        files = [file_paths[item] for item in items]

        save_path = filedialog.asksaveasfilename(
            parent=root,
            title="Save Merged PDF As",
            defaultextension=".pdf",
            initialfile="Merged_Document.pdf",
            filetypes=[("PDF Files", "*.pdf")],
        )

        if not save_path:
            return

        save_path = os.path.abspath(save_path)

        input_paths = {
            os.path.normcase(os.path.abspath(path))
            for path in files
        }

        if os.path.normcase(save_path) in input_paths:
            messagebox.showerror(
                "Invalid output path",
                "The output file cannot overwrite one of the input PDFs. "
                "Choose a different filename.",
                parent=root,
            )
            return

        # Validate all inputs before creating the output.
        try:
            for path in files:
                if not os.path.isfile(path):
                    raise FileNotFoundError(
                        f"The file no longer exists:\n{path}"
                    )

                with open(path, "rb") as pdf_file:
                    reader = PdfReader(pdf_file, strict=False)

                    if reader.is_encrypted:
                        if not reader.decrypt(""):
                            raise ValueError(
                                f"The PDF is password-protected:\n{path}"
                            )

                    # Force page-tree access before starting the merge.
                    len(reader.pages)

        except Exception as error:
            messagebox.showerror(
                "Unable to process PDF",
                f"Please check the selected files.\n\n{error}",
                parent=root,
            )
            return

        try:
            with PdfWriter() as merger:
                for path in files:
                    merger.append(path)

                with open(save_path, "wb") as output_file:
                    merger.write(output_file)

            status_label.configure(
                text="PDFs merged successfully.",
                fg=COLORS["success"],
            )

            messagebox.showinfo(
                "Merge Complete",
                f"Successfully merged {len(files)} PDF files.\n\n"
                f"Saved to:\n{save_path}\n\n"
                "Opening the merged PDF...",
                parent=root,
            )

            open_pdf_file(save_path)

        except Exception as error:
            # Remove an incomplete output file where possible.
            try:
                if os.path.exists(save_path):
                    os.remove(save_path)
            except OSError:
                pass

            messagebox.showerror(
                "Merge failed",
                f"An error occurred while merging the PDFs:\n\n{error}",
                parent=root,
            )

    # =========================
    # File Actions
    # =========================

    actions_frame = tk.Frame(
        list_section,
        bg=COLORS["surface"],
    )

    actions_frame.grid(
        row=3, column=0, columnspan=2,
        sticky="ew", padx=18, pady=(0, 16)
    )

    def create_button(parent, text, command, primary=False):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT_FAMILY, 9, "bold"),
            bg=COLORS["primary"] if primary else COLORS["accent_background"],
            fg="#FFFFFF" if primary else COLORS["primary"],
            activebackground=COLORS["primary_hover"],
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=12,
            pady=9,
        )

    create_button(
        actions_frame, "+ Add PDFs", add_pdf, primary=True
    ).pack(side="left", padx=(0, 8))

    create_button(
        actions_frame, "Select All", select_all
    ).pack(side="left", padx=(0, 8))

    create_button(
        actions_frame, "Remove Selected", remove_selected
    ).pack(side="left", padx=(0, 8))

    create_button(
        actions_frame, "Clear All", clear_all
    ).pack(side="left")

    # =========================
    # Bottom Controls
    # =========================

    bottom_frame = tk.Frame(
        main_frame,
        bg=COLORS["background"],
    )

    bottom_frame.grid(
        row=3, column=0, sticky="ew", pady=(18, 0)
    )

    create_button(
        bottom_frame, "↑ Move Up", move_up
    ).pack(side="left", padx=(0, 8))

    create_button(
        bottom_frame, "↓ Move Down", move_down
    ).pack(side="left")

    create_button(
        bottom_frame, "Back to Menu", show_main_menu
    ).pack(side="left", padx=(18, 0))

    create_button(
        bottom_frame, "Merge PDFs", merge_pdf, primary=True
    ).pack(side="right")
import tkinter as tk
from tkinter import ttk

from utils import clear_window, FONT
import pdf_merger
import pdf_splitter
import pdf_rotater
import image_to_pdf


# =========================
# Application Configuration
# =========================

APP_TITLE = "PDF Utilities"

COLORS = {
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "text": "#172033",
    "secondary_text": "#64748B",
    "border": "#E2E8F0",
    "accent_background": "#EFF6FF",
}

WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 800


def create_utility_card(parent, title, description, icon, command):
    """
    Create a reusable card for a PDF utility.
    """

    card = tk.Frame(
        parent,
        bg=COLORS["surface"],
        highlightbackground=COLORS["border"],
        highlightthickness=1,
        bd=0,
    )

    card.grid_columnconfigure(0, weight=1)

    # Icon
    tk.Label(
        card,
        text=icon,
        font=("Segoe UI Emoji", 24),
        bg=COLORS["surface"],
        fg=COLORS["primary"],
    ).grid(
        row=0,
        column=0,
        sticky="w",
        padx=22,
        pady=(20, 8),
    )

    # Title
    tk.Label(
        card,
        text=title,
        font=("Segoe UI", 15, "bold"),
        bg=COLORS["surface"],
        fg=COLORS["text"],
        anchor="w",
    ).grid(
        row=1,
        column=0,
        sticky="ew",
        padx=22,
        pady=(0, 6),
    )

    # Description
    tk.Label(
        card,
        text=description,
        font=("Segoe UI", 10),
        bg=COLORS["surface"],
        fg=COLORS["secondary_text"],
        anchor="nw",
        justify="left",
        wraplength=290,
        height=2,
    ).grid(
        row=2,
        column=0,
        sticky="ew",
        padx=22,
        pady=(0, 18),
    )

    # Action button
    button = tk.Button(
        card,
        text="Open Utility  →",
        font=("Segoe UI", 10, "bold"),
        bg=COLORS["accent_background"],
        fg=COLORS["primary"],
        activebackground=COLORS["primary"],
        activeforeground="#FFFFFF",
        relief="flat",
        bd=0,
        cursor="hand2",
        padx=12,
        pady=10,
        command=command,
    )

    button.grid(
        row=3,
        column=0,
        sticky="ew",
        padx=22,
        pady=(0, 22),
    )

    def on_enter(event):
        button.configure(
            bg=COLORS["primary"],
            fg="#FFFFFF",
        )

    def on_leave(event):
        button.configure(
            bg=COLORS["accent_background"],
            fg=COLORS["primary"],
        )

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

    return card


def show_main_menu():
    clear_window(root)

    root.configure(bg=COLORS["background"])

    # Allow the main content to expand when the window is resized.
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)

    # Main container
    main_frame = tk.Frame(
        root,
        bg=COLORS["background"],
    )

    main_frame.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=30,
        pady=24,
    )

    main_frame.grid_columnconfigure(0, weight=1)

    # =========================
    # Header
    # =========================

    header = tk.Frame(
        main_frame,
        bg=COLORS["background"],
    )

    header.grid(
        row=0,
        column=0,
        sticky="ew",
        pady=(0, 32),
    )

    header.grid_columnconfigure(1, weight=1)

    tk.Label(
        header,
        text="PDF",
        font=("Segoe UI", 20, "bold"),
        bg=COLORS["primary"],
        fg="#FFFFFF",
        padx=12,
        pady=7,
    ).grid(
        row=0,
        column=0,
        rowspan=2,
        sticky="w",
        padx=(0, 14),
    )

    tk.Label(
        header,
        text="PDF Utilities",
        font=("Segoe UI", 20, "bold"),
        bg=COLORS["background"],
        fg=COLORS["text"],
    ).grid(
        row=0,
        column=1,
        sticky="w",
    )

    tk.Label(
        header,
        text="Simple tools for everyday document tasks",
        font=("Segoe UI", 10),
        bg=COLORS["background"],
        fg=COLORS["secondary_text"],
    ).grid(
        row=1,
        column=1,
        sticky="w",
        pady=(3, 0),
    )

    # =========================
    # Welcome Section
    # =========================

    tk.Label(
        main_frame,
        text="Choose a tool to get started.",
        font=("Segoe UI", 17, "bold"),
        bg=COLORS["background"],
        fg=COLORS["text"],
        anchor="w",
    ).grid(
        row=1,
        column=0,
        sticky="ew",
        pady=(0, 6),
    )

    # =========================
    # Utility Cards
    # =========================

    utilities_frame = tk.Frame(
        main_frame,
        bg=COLORS["background"],
    )

    utilities_frame.grid(
        row=3,
        column=0,
        sticky="nsew",
    )

    utilities_frame.grid_columnconfigure(
        0,
        weight=1,
        uniform="utility_cards",
    )

    utilities_frame.grid_columnconfigure(
        1,
        weight=1,
        uniform="utility_cards",
    )

    utilities_frame.grid_rowconfigure(
        0,
        weight=1,
        uniform="utility_rows",
    )

    utilities_frame.grid_rowconfigure(
        1,
        weight=1,
        uniform="utility_rows",
    )

    utility_cards = [
        {
            "title": "Merge PDFs",
            "description": (
                "Combine multiple PDF documents "
                "into a single file."
            ),
            "icon": "📑",
            "command": lambda: pdf_merger.show_pdf_merger(
                root, show_main_menu
            ),
        },
        {
            "title": "Split PDF",
            "description": (
                "Extract pages or divide a PDF "
                "into smaller documents."
            ),
            "icon": "✂",
            "command": lambda: pdf_splitter.show_pdf_splitter(
                root, show_main_menu
            ),
        },
        {
            "title": "Rotate PDF",
            "description": (
                "Rotate PDF pages to the "
                "correct orientation."
            ),
            "icon": "🔄",
            "command": lambda: pdf_rotater.show_pdf_rotater(
                root, show_main_menu
            ),
        },
        {
            "title": "Images to PDF",
            "description": (
                "Convert multiple images "
                "into a single PDF document."
            ),
            "icon": "🖼",
            "command": lambda: image_to_pdf.show_image_to_pdf_converter(
                root, show_main_menu
            ),
        },
    ]

    for index, utility in enumerate(utility_cards):
        row = index // 2
        column = index % 2

        card = create_utility_card(
            utilities_frame,
            title=utility["title"],
            description=utility["description"],
            icon=utility["icon"],
            command=utility["command"],
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=(0, 10) if column == 0 else (10, 0),
            pady=(0, 12) if row == 0 else (12, 0),
        )

    # =========================
    # Footer
    # =========================

    footer = tk.Frame(
        main_frame,
        bg=COLORS["background"],
    )

    footer.grid(
        row=4,
        column=0,
        sticky="ew",
        pady=(22, 0),
    )

    tk.Label(
        footer,
        text="PDF Utilities  •  All your essential tools in one place",
        font=("Segoe UI", 9),
        bg=COLORS["background"],
        fg=COLORS["secondary_text"],
    ).pack(anchor="center")


if __name__ == "__main__":
    root = tk.Tk()

    root.title(APP_TITLE)
    root.geometry("850x700")
    root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
    root.configure(bg=COLORS["background"])

    show_main_menu()

    root.mainloop()
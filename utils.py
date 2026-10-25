"""Shared theme and widget helpers for PDF Utility Tool."""
import tkinter as tk
from tkinter import ttk

# Centralized color palette
COLORS = {
    "background": "#F4F7FB",
    "surface": "#FFFFFF",
    "primary": "#2563EB",
    "primary_hover": "#1D4ED8",
    "accent_background": "#EFF6FF",
    "text": "#172033",
    "secondary_text": "#64748B",
    "border": "#E2E8F0",
    "success": "#15803D",
    "error": "#DC2626",
}

# Backwards-friendly semantic aliases used by utility modules.
BG_COLOR = COLORS["background"]
CARD_COLOR = COLORS["surface"]
PRIMARY_COLOR = COLORS["primary"]
PRIMARY_HOVER = COLORS["primary_hover"]
LIGHT_BLUE = COLORS["accent_background"]
TEXT_COLOR = COLORS["text"]
MUTED_COLOR = COLORS["secondary_text"]
BORDER_COLOR = COLORS["border"]
SUCCESS_COLOR = COLORS["success"]
ERROR_COLOR = COLORS["error"]
DANGER_COLOR = ERROR_COLOR
ACCENT_COLOR = PRIMARY_COLOR
ACCENT_HOVER = PRIMARY_HOVER
FONT_FAMILY = "Segoe UI"
FONT = FONT_FAMILY

TITLE_FONT = (FONT_FAMILY, 24, "bold")
SECTION_FONT = (FONT_FAMILY, 14, "bold")
SUBSECTION_FONT = (FONT_FAMILY, 12, "bold")
BODY_FONT = (FONT_FAMILY, 10)
BUTTON_FONT = (FONT_FAMILY, 10)
BOLD_BUTTON_FONT = (FONT_FAMILY, 10, "bold")
SMALL_FONT = (FONT_FAMILY, 9)


def clear_window(root):
    """Destroy the current view's widgets before rendering another view."""
    for widget in root.winfo_children():
        widget.destroy()


def create_card(parent, **kwargs):
    """Create a standard white card; explicit kwargs can override defaults."""
    options = {
        "bg": COLORS["surface"],
        "highlightbackground": COLORS["border"],
        "highlightthickness": 1,
        "bd": 0,
    }
    options.update(kwargs)
    return tk.Frame(parent, **options)


def create_label(parent, text=None, *, font=BODY_FONT, fg=None, bg=None, **kwargs):
    """Create a label using shared typography and semantic colors."""
    options = {
        "font": font,
        "fg": fg or COLORS["text"],
        "bg": bg or COLORS["surface"],
    }
    options.update(kwargs)
    return tk.Label(parent, text=text, **options)


def create_button(parent, text, command=None, *, variant="secondary",
                  bold=None, padx=12, pady=8, **kwargs):
    """Create a consistent Tk button. Variants: primary, secondary, subtle."""
    if variant == "primary":
        bg, fg, active_bg = COLORS["primary"], "#FFFFFF", COLORS["primary_hover"]
    elif variant == "subtle":
        bg, fg, active_bg = COLORS["accent_background"], COLORS["primary"], "#DBEAFE"
    else:
        bg, fg, active_bg = COLORS["surface"], COLORS["text"], COLORS["accent_background"]
    if bold is None:
        bold = variant == "primary"
    options = {
        "font": BOLD_BUTTON_FONT if bold else BUTTON_FONT,
        "bg": bg, "fg": fg,
        "activebackground": active_bg, "activeforeground": fg,
        "relief": "flat", "bd": 0, "borderwidth": 0,
        "cursor": "hand2", "padx": padx, "pady": pady,
    }
    options.update(kwargs)
    active_bg = options.get("activebackground", active_bg)
    button = tk.Button(parent, text=text, command=command, **options)
    # Hover colors are handled here so modules don't implement their own behavior.
    if kwargs.get("state") != "disabled":
        normal_bg = options.get("bg", bg)
        normal_fg = options.get("fg", fg)
        def on_enter(_event):
            if str(button["state"]) != "disabled":
                button.configure(bg=active_bg)
        def on_leave(_event):
            button.configure(bg=normal_bg, fg=normal_fg)
        button.bind("<Enter>", on_enter, add="+")
        button.bind("<Leave>", on_leave, add="+")
    return button


def create_entry(parent, *, font=BODY_FONT, **kwargs):
    """Create a consistently styled classic Tk entry."""
    options = {
        "font": font,
        "bg": "#F8FAFC",
        "fg": COLORS["text"],
        "insertbackground": COLORS["text"],
        "relief": "solid",
        "bd": 1,
        "highlightthickness": 1,
        "highlightbackground": COLORS["border"],
        "highlightcolor": COLORS["primary"],
    }
    options.update(kwargs)
    return tk.Entry(parent, **options)


def configure_ttk_styles(root):
    """Apply shared ttk styling, including tables and scrollbars."""
    style = ttk.Style(root)
    try:
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure(".", font=BODY_FONT)
    style.configure("Treeview", font=BODY_FONT, rowheight=30,
                    background=COLORS["surface"], foreground=COLORS["text"],
                    fieldbackground=COLORS["surface"], bordercolor=COLORS["border"])
    style.configure("Treeview.Heading", font=BOLD_BUTTON_FONT,
                    background=COLORS["accent_background"], foreground=COLORS["text"])
    style.map("Treeview", background=[("selected", COLORS["primary"])],
              foreground=[("selected", "#FFFFFF")])
    style.configure("Vertical.TScrollbar", background=COLORS["accent_background"],
                    troughcolor=COLORS["background"], bordercolor=COLORS["border"],
                    arrowcolor=COLORS["secondary_text"])
    style.configure("Horizontal.TScrollbar", background=COLORS["accent_background"],
                    troughcolor=COLORS["background"], bordercolor=COLORS["border"],
                    arrowcolor=COLORS["secondary_text"])
    return style

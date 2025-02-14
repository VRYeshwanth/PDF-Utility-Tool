import tkinter as tk

# Define a common font to use across modules
FONT = ("Cascadia Code", 14)

def clear_window(root):
    # Removes all widgets from the root window.
    for widget in root.winfo_children():
        widget.destroy()

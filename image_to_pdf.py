import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import os
from utils import clear_window, FONT

def show_image_to_pdf_converter(root, show_main_menu):
    clear_window(root)

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True, padx=25)
    tk.Label(frame, text="Image to PDF Converter", font=("Cascadia Code", 24, "bold")).pack(pady=10)

    inp_frame = tk.Frame(frame)
    inp_frame.pack(pady=10)
    image_listbox = tk.Listbox(inp_frame, width=50, height=10, font=("Cascadia Code", 12))
    image_listbox.grid(row=0, column=0, columnspan=3, padx=10, pady=5)
    image_paths = []

    def browse_images():
        files = filedialog.askopenfilenames(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")],
            title="Select Images"
        )
        for file in files:
            filename = os.path.basename(file)
            image_listbox.insert(tk.END, filename)
            image_paths.append(file)

    def move_up():
        selected_idx = image_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            if idx > 0:
                filename = image_listbox.get(idx)
                image_listbox.delete(idx)
                image_listbox.insert(idx - 1, filename)
                image_listbox.select_set(idx - 1)
                image_paths[idx], image_paths[idx - 1] = image_paths[idx - 1], image_paths[idx]

    def move_down():
        selected_idx = image_listbox.curselection()
        if selected_idx:
            idx = selected_idx[0]
            if idx < image_listbox.size() - 1:
                filename = image_listbox.get(idx)
                image_listbox.delete(idx)
                image_listbox.insert(idx + 1, filename)
                image_listbox.select_set(idx + 1)
                image_paths[idx], image_paths[idx + 1] = image_paths[idx + 1], image_paths[idx]

    def convert_to_pdf():
        if not image_paths:
            messagebox.showerror("Error", "No images selected.")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                   filetypes=[("PDF files", "*.pdf")],
                                                   title="Save PDF As")
        if not output_path:
            return
        try:
            images = [Image.open(img).convert("RGB") for img in image_paths]
            images[0].save(output_path, save_all=True, append_images=images[1:])
            messagebox.showinfo("Success", "Images successfully converted to PDF!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert images to PDF.\n{e}")

    tk.Button(inp_frame, text="Add Images", font=("Cascadia Code", 14), command=browse_images).grid(row=1, column=0, padx=5, pady=10)
    tk.Button(inp_frame, text="Move Up", font=("Cascadia Code", 14), command=move_up).grid(row=1, column=1, padx=5, pady=10)
    tk.Button(inp_frame, text="Move Down", font=("Cascadia Code", 14), command=move_down).grid(row=1, column=2, padx=5, pady=10)
    tk.Button(frame, text="Convert to PDF", font=("Cascadia Code", 14), command=convert_to_pdf).pack(pady=10)
    tk.Button(frame, text="Back to Menu", font=("Cascadia Code", 14), command=show_main_menu).pack(pady=10)

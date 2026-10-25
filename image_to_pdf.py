import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageOps #type: ignore

from utils import clear_window, FONT

# --------------------------------------------------
# UI THEME
# --------------------------------------------------

BG_COLOR = "#F4F6FA"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#1F2937"
MUTED_COLOR = "#6B7280"
ACCENT_COLOR = "#2563EB"
ACCENT_HOVER = "#1D4ED8"
BORDER_COLOR = "#E5E7EB"
SUCCESS_COLOR = "#15803D"
DANGER_COLOR = "#DC2626"

SUPPORTED_IMAGE_TYPES = (
    ("Image files", "*.png *.jpg *.jpeg *.bmp"),
    ("PNG files", "*.png"),
    ("JPEG files", "*.jpg *.jpeg"),
    ("BMP files", "*.bmp"),
    ("All files", "*.*"),
)

# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def format_file_size(size_bytes):
    """Convert a file size in bytes into a readable string."""
    size = float(size_bytes)

    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.2f} {unit}"

        size /= 1024

    return f"{size:.2f} GB"


def open_file(path):
    """Open a file using the operating system's default application."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    except Exception as exc:
        messagebox.showwarning(
            "Open File",
            f"The PDF was created successfully, but it could not "
            f"be opened automatically.\n\n{exc}",
        )


def get_image_information(image_path):
    """Return useful information about an image."""
    try:
        with Image.open(image_path) as image:
            width, height = image.size
            image_format = image.format or "Unknown"

        file_size = os.path.getsize(image_path)

        return {
            "width": width,
            "height": height,
            "format": image_format,
            "size": file_size,
        }

    except Exception as exc:
        raise ValueError(f"Unable to read image information:\n{exc}") from exc


def prepare_image(image_path):
    """
    Open an image, correct its EXIF orientation, and convert it to RGB.

    Transparent pixels are composited onto a white background.
    The returned image is independent of the source file.
    """
    with Image.open(image_path) as source:
        # Correct orientation for images taken with phones and cameras.
        oriented = ImageOps.exif_transpose(source)

        try:
            # Preserve transparency by placing transparent areas on white.
            if oriented.mode in ("RGBA", "LA") or (
                oriented.mode == "P" and "transparency" in oriented.info
            ):
                rgba_image = oriented.convert("RGBA")

                try:
                    background = Image.new(
                        "RGB",
                        rgba_image.size,
                        "white",
                    )

                    try:
                        background.paste(
                            rgba_image,
                            mask=rgba_image.getchannel("A"),
                        )
                        return background.copy()
                    finally:
                        background.close()

                finally:
                    rgba_image.close()

            return oriented.convert("RGB")

        finally:
            # ImageOps.exif_transpose may return the original image.
            if oriented is not source:
                oriented.close()


# --------------------------------------------------
# MAIN CONVERTER
# --------------------------------------------------

def show_image_to_pdf_converter(root, show_main_menu):
    clear_window(root)

    image_paths = []

    # --------------------------------------------------
    # ROOT LAYOUT
    # --------------------------------------------------

    root.configure(bg=BG_COLOR)

    main_frame = tk.Frame(root, bg=BG_COLOR)
    main_frame.pack(fill="both", expand=True, padx=28, pady=20)

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    header_frame = tk.Frame(main_frame, bg=BG_COLOR)
    header_frame.pack(fill="x", pady=(0, 18))

    tk.Label(
        header_frame,
        text="Image to PDF Converter",
        font=(FONT, 24, "bold"),
        bg=BG_COLOR,
        fg=TEXT_COLOR,
    ).pack(anchor="w")

    tk.Label(
        header_frame,
        text=(
            "Combine multiple images into a single PDF. "
            "Arrange the images in the order you want."
        ),
        font=(FONT, 10),
        bg=BG_COLOR,
        fg=MUTED_COLOR,
        wraplength=800,
        justify="left",
    ).pack(anchor="w", pady=(5, 0))

    # --------------------------------------------------
    # IMAGE SELECTION CARD
    # --------------------------------------------------

    selection_card = tk.Frame(
        main_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
    )
    selection_card.pack(fill="both", expand=True)

    selection_header = tk.Frame(selection_card, bg=CARD_COLOR)
    selection_header.pack(fill="x", padx=18, pady=(16, 8))

    tk.Label(
        selection_header,
        text="Selected Images",
        font=(FONT, 14, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
    ).pack(side="left")

    image_count_label = tk.Label(
        selection_header,
        text="0 images",
        font=(FONT, 10),
        bg=CARD_COLOR,
        fg=MUTED_COLOR,
    )
    image_count_label.pack(side="right")

    # --------------------------------------------------
    # IMAGE LIST AND SCROLLBAR
    # --------------------------------------------------

    list_frame = tk.Frame(selection_card, bg=CARD_COLOR)
    list_frame.pack(fill="both", expand=True, padx=18, pady=(0, 10))

    image_listbox = tk.Listbox(
        list_frame,
        font=(FONT, 11),
        bg="#FFFFFF",
        fg=TEXT_COLOR,
        selectbackground=ACCENT_COLOR,
        selectforeground="#FFFFFF",
        activestyle="none",
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=BORDER_COLOR,
        highlightcolor=ACCENT_COLOR,
        height=8,
        exportselection=False,
        selectmode=tk.SINGLE,
    )
    image_listbox.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(
        list_frame,
        orient="vertical",
        command=image_listbox.yview,
    )
    scrollbar.pack(side="right", fill="y")

    image_listbox.configure(yscrollcommand=scrollbar.set)

    # --------------------------------------------------
    # BUTTON HELPER
    # --------------------------------------------------

    def create_button(
        parent,
        text,
        command,
        bg="#FFFFFF",
        fg=TEXT_COLOR,
        active_bg="#F3F4F6",
        padx=12,
        pady=7,
        bold=False,
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            font=(FONT, 10, "bold" if bold else "normal"),
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=fg,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            padx=padx,
            pady=pady,
        )

    # --------------------------------------------------
    # IMAGE LIST MANAGEMENT
    # --------------------------------------------------

    def update_image_count():
        count = len(image_paths)

        image_count_label.config(
            text=f"{count} image{'s' if count != 1 else ''}"
        )

    def refresh_listbox(selected_index=None):
        image_listbox.delete(0, tk.END)

        for index, path in enumerate(image_paths, start=1):
            filename = os.path.basename(path)

            # Number the images to make the final PDF page order clear.
            image_listbox.insert(
                tk.END,
                f"{index:02d}.  {filename}",
            )

        update_image_count()

        if selected_index is not None and image_paths:
            selected_index = max(
                0,
                min(selected_index, len(image_paths) - 1),
            )

            image_listbox.selection_set(selected_index)
            image_listbox.activate(selected_index)
            image_listbox.see(selected_index)

        update_image_information()

    def get_selected_index():
        selection = image_listbox.curselection()

        if not selection:
            return None

        return selection[0]

    def browse_images():
        files = filedialog.askopenfilenames(
            parent=root,
            title="Select Images",
            filetypes=SUPPORTED_IMAGE_TYPES,
        )

        if not files:
            return

        existing_paths = {
            os.path.normcase(os.path.realpath(path))
            for path in image_paths
        }

        added_count = 0

        for path in files:
            normalized_path = os.path.normcase(os.path.realpath(path))

            # Avoid adding the same file more than once.
            if normalized_path in existing_paths:
                continue

            # Validate that the selected file can be opened as an image.
            try:
                with Image.open(path) as image:
                    image.verify()

            except Exception:
                messagebox.showwarning(
                    "Invalid Image",
                    f"This file could not be read as an image:\n\n"
                    f"{os.path.basename(path)}",
                    parent=root,
                )
                continue

            image_paths.append(path)
            existing_paths.add(normalized_path)
            added_count += 1

        if image_paths:
            refresh_listbox(len(image_paths) - 1)

        if added_count == 0 and files:
            return

    def remove_selected():
        index = get_selected_index()

        if index is None:
            messagebox.showwarning(
                "No Selection",
                "Select an image to remove.",
                parent=root,
            )
            return

        del image_paths[index]

        if image_paths:
            refresh_listbox(min(index, len(image_paths) - 1))
        else:
            refresh_listbox()

    def clear_all():
        if not image_paths:
            return

        confirm = messagebox.askyesno(
            "Clear Images",
            "Remove all selected images?",
            parent=root,
        )

        if confirm:
            image_paths.clear()
            refresh_listbox()

    def move_up():
        index = get_selected_index()

        if index is None or index == 0:
            return

        image_paths[index - 1], image_paths[index] = (
            image_paths[index],
            image_paths[index - 1],
        )

        refresh_listbox(index - 1)

    def move_down():
        index = get_selected_index()

        if index is None or index >= len(image_paths) - 1:
            return

        image_paths[index + 1], image_paths[index] = (
            image_paths[index],
            image_paths[index + 1],
        )

        refresh_listbox(index + 1)

    # --------------------------------------------------
    # IMAGE MANAGEMENT BUTTONS
    # --------------------------------------------------

    management_frame = tk.Frame(selection_card, bg=CARD_COLOR)
    management_frame.pack(fill="x", padx=18, pady=(0, 14))

    create_button(
        management_frame,
        "＋ Add Images",
        browse_images,
        bg=ACCENT_COLOR,
        fg="#FFFFFF",
        active_bg=ACCENT_HOVER,
        bold=True,
    ).pack(side="left", padx=(0, 7))

    create_button(
        management_frame,
        "↑ Move Up",
        move_up,
    ).pack(side="left", padx=3)

    create_button(
        management_frame,
        "↓ Move Down",
        move_down,
    ).pack(side="left", padx=3)

    create_button(
        management_frame,
        "Remove",
        remove_selected,
        fg=DANGER_COLOR,
    ).pack(side="left", padx=3)

    create_button(
        management_frame,
        "Clear All",
        clear_all,
        fg=DANGER_COLOR,
    ).pack(side="right")

    # --------------------------------------------------
    # IMAGE INFORMATION CARD
    # --------------------------------------------------

    info_card = tk.Frame(
        main_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
    )
    info_card.pack(fill="x", pady=(14, 0))

    tk.Label(
        info_card,
        text="Image Information",
        font=(FONT, 12, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
    ).pack(anchor="w", padx=16, pady=(12, 6))

    info_content = tk.Frame(info_card, bg=CARD_COLOR)
    info_content.pack(fill="x", padx=16, pady=(0, 12))

    info_filename = tk.Label(
        info_content,
        text="Select an image to view its details.",
        font=(FONT, 10),
        bg=CARD_COLOR,
        fg=MUTED_COLOR,
        anchor="w",
        justify="left",
        wraplength=800,
    )
    info_filename.pack(fill="x", pady=2)

    info_dimensions = tk.Label(
        info_content,
        text="Dimensions: —",
        font=(FONT, 10),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        anchor="w",
    )
    info_dimensions.pack(fill="x", pady=2)

    info_format = tk.Label(
        info_content,
        text="Format: —",
        font=(FONT, 10),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        anchor="w",
    )
    info_format.pack(fill="x", pady=2)

    info_size = tk.Label(
        info_content,
        text="File size: —",
        font=(FONT, 10),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
        anchor="w",
    )
    info_size.pack(fill="x", pady=2)

    def update_image_information(event=None):
        index = get_selected_index()

        if index is None:
            info_filename.config(
                text="Select an image to view its details.",
                fg=MUTED_COLOR,
            )
            info_dimensions.config(text="Dimensions: —")
            info_format.config(text="Format: —")
            info_size.config(text="File size: —")
            return

        path = image_paths[index]

        try:
            details = get_image_information(path)

            info_filename.config(
                text=f"File: {os.path.basename(path)}",
                fg=TEXT_COLOR,
            )

            info_dimensions.config(
                text=(
                    f"Dimensions: {details['width']} × "
                    f"{details['height']} pixels"
                )
            )

            info_format.config(
                text=f"Format: {details['format']}"
            )

            info_size.config(
                text=f"File size: {format_file_size(details['size'])}"
            )

        except Exception as exc:
            info_filename.config(
                text=f"File: {os.path.basename(path)}",
                fg=DANGER_COLOR,
            )
            info_dimensions.config(text="Dimensions: Unavailable")
            info_format.config(text="Format: Unavailable")
            info_size.config(text=f"Error: {exc}")

    image_listbox.bind(
        "<<ListboxSelect>>",
        update_image_information,
    )

    # --------------------------------------------------
    # CONVERSION SETTINGS
    # --------------------------------------------------

    settings_card = tk.Frame(
        main_frame,
        bg=CARD_COLOR,
        highlightbackground=BORDER_COLOR,
        highlightthickness=1,
    )
    settings_card.pack(fill="x", pady=(14, 0))

    tk.Label(
        settings_card,
        text="Conversion Settings",
        font=(FONT, 12, "bold"),
        bg=CARD_COLOR,
        fg=TEXT_COLOR,
    ).pack(anchor="w", padx=16, pady=(12, 4))

    tk.Label(
        settings_card,
        text=(
            "Page size: Original Image Size\n"
            "Each image becomes one PDF page. "
            "Image dimensions are preserved, and transparent areas "
            "are filled with white."
        ),
        font=(FONT, 10),
        bg=CARD_COLOR,
        fg=MUTED_COLOR,
        justify="left",
        wraplength=850,
    ).pack(anchor="w", padx=16, pady=(0, 12))

    # --------------------------------------------------
    # CONVERSION
    # --------------------------------------------------

    def convert_to_pdf():
        if not image_paths:
            messagebox.showerror(
                "No Images",
                "Add at least one image before converting.",
                parent=root,
            )
            return

        # Use the first image's directory and filename as the defaults.
        first_image = image_paths[0]
        default_directory = os.path.dirname(first_image)
        base_name = os.path.splitext(os.path.basename(first_image))[0]
        default_filename = f"{base_name}_converted.pdf"

        output_path = filedialog.asksaveasfilename(
            parent=root,
            title="Save PDF As",
            initialdir=default_directory,
            initialfile=default_filename,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )

        if not output_path:
            return

        output_path = os.path.abspath(output_path)

        # Prevent accidentally replacing an input image.
        input_paths = {
            os.path.normcase(os.path.realpath(path))
            for path in image_paths
        }

        output_normalized = os.path.normcase(
            os.path.realpath(output_path)
        )

        if output_normalized in input_paths:
            messagebox.showerror(
                "Invalid Output Path",
                "The output PDF cannot overwrite one of the input images.",
                parent=root,
            )
            return

        # Explicitly confirm overwriting an existing output file.
        if os.path.exists(output_path):
            overwrite = messagebox.askyesno(
                "Confirm Overwrite",
                f"The following file already exists:\n\n"
                f"{output_path}\n\n"
                "Do you want to replace it?",
                parent=root,
            )

            if not overwrite:
                return

        prepared_images = []

        try:
            # Prepare every image before writing the output.
            for path in image_paths:
                if not os.path.isfile(path):
                    raise FileNotFoundError(
                        f"The image no longer exists:\n{path}"
                    )

                prepared_images.append(prepare_image(path))

            if not prepared_images:
                raise ValueError("No valid images are available.")

            # Save all images as pages in a single PDF.
            first_image_to_save = prepared_images[0]

            first_image_to_save.save(
                output_path,
                format="PDF",
                save_all=True,
                append_images=prepared_images[1:],
                resolution=100.0,
            )

        except Exception as exc:
            messagebox.showerror(
                "Conversion Failed",
                f"Unable to create the PDF.\n\n{exc}",
                parent=root,
            )
            return

        finally:
            # Release image resources even if conversion fails.
            for image in prepared_images:
                try:
                    image.close()
                except Exception:
                    pass

        messagebox.showinfo(
            "Conversion Successful",
            f"Successfully converted {len(image_paths)} image(s) "
            f"into a PDF.\n\nSaved to:\n{output_path}",
            parent=root,
        )

        # Open the resulting PDF with the default PDF viewer.
        if messagebox.askyesno(
            "Open PDF",
            "Would you like to open the generated PDF now?",
            parent=root,
        ):
            open_file(output_path)

    # --------------------------------------------------
    # FOOTER
    # --------------------------------------------------

    footer_frame = tk.Frame(main_frame, bg=BG_COLOR)
    footer_frame.pack(fill="x", pady=(16, 0))

    create_button(
        footer_frame,
        "← Back to Menu",
        show_main_menu,
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        active_bg="#E5E7EB",
    ).pack(side="left")

    create_button(
        footer_frame,
        "Convert to PDF",
        convert_to_pdf,
        bg=ACCENT_COLOR,
        fg="#FFFFFF",
        active_bg=ACCENT_HOVER,
        padx=22,
        pady=10,
        bold=True,
    ).pack(side="right")
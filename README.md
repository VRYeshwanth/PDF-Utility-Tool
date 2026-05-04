# 📄 PDF Utility Tool

A clean, powerful, and user-friendly **Python desktop application** for handling everyday PDF tasks with ease. Designed with simplicity in mind, this tool eliminates the need for complex command-line operations or paid software.

---

## ✨ Features

### 🔗 PDF Merger

Combine multiple PDF files into a single document effortlessly.

- Add and remove files
- Reorder using **Move Up / Move Down**
- Clean and intuitive workflow

---

### ✂️ PDF Splitter

Extract specific pages from a PDF with precision.

- Define ranges like `1-5`
- Save output to any directory
- Fast and accurate extraction

---

### 🔄 PDF Rotater

Rotate selected pages exactly how you want.

- Input pages (e.g., `1,3,5`)
- Choose rotation: `90°`, `180°`, `270°`
- Direction control: Clockwise / Anticlockwise

---

### 🖼️ Image to PDF Converter

Convert images into a single PDF file.

- Supports `.png`, `.jpg`, `.jpeg`, `.bmp`
- Reorder images before conversion
- High-quality output

---

## 🛠️ Tech Stack

- **🐍 Python** – Core programming language
- **🪟 Tkinter** – GUI development
- **📚 PyPDF2** – PDF processing engine
- **🖼️ Pillow (PIL)** – Image handling and conversion

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/VRYeshwanth/PDF-Utility-Tool.git
cd PDF-Utility-Tool
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the Application

```bash
python main.py
```

---

## 📁 Project Structure

```
PDF-Utility-Tool/
│
├── image_to_pdf.py     # Image → PDF conversion logic
├── main.py             # Entry point (main menu UI)
├── pdf_merger.py       # PDF merging functionality
├── pdf_rotater.py      # Page rotation logic
├── pdf_splitter.py     # Page extraction logic
├── utils.py            # Shared utilities and UI helpers
├── README.md           # Project documentation
└── requirements.txt    # Dependencies
```

---

## 🤝 Contributing

Contributions are welcome and appreciated.

### Steps to Contribute:

1. Fork the repository
2. Create a new branch

    ```bash
    git checkout -b feature/AmazingFeature
    ```

3. Commit your changes

    ```bash
    git commit -m "Add AmazingFeature"
    ```

4. Push to your branch

    ```bash
    git push origin feature/AmazingFeature
    ```

5. Open a Pull Request

---

## 🌟 Final Note

This project is built to simplify PDF workflows while maintaining a clean and beginner-friendly structure. Perfect for learning, extending, and practical usage.

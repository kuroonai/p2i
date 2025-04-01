# PDF to Image GUI Converter - Installation Guide

This guide explains how to install and use the PDF to Image GUI Converter application.

## Prerequisites

The application requires Python 3.9 or higher and several dependencies.

## Installation

### Step 1: Install Required OS Dependencies

#### On Windows

No additional OS dependencies are required.

#### On macOS

```bash
brew install poppler
```

#### On Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y poppler-utils
```

### Step 2: Create a Virtual Environment (Optional but Recommended)

```bash
# Create a virtual environment
python -m venv pdf2image-env

# Activate the virtual environment
# On Windows:
pdf2image-env\Scripts\activate
# On macOS/Linux:
source pdf2image-env/bin/activate
```

### Step 3: Install Python Requirements

```bash
pip install -r requirements.txt
```

## Running the Application

After installation, you can run the application:

```bash
python pdf2image_gui.py
```

## Features

The PDF to Image GUI Converter includes the following features:

1. **User-Friendly Interface**: Easy-to-use GUI for converting PDF files to images
2. **Batch Processing**: Convert multiple PDF files at once
3. **Page Range Selection**: Convert specific pages or page ranges
4. **Preview**: Preview pages before conversion
5. **Multiple Output Formats**: Save as JPG, PNG, TIFF, or BMP
6. **Quality Control**: Adjust DPI and image quality
7. **Multi-threading**: Utilize multiple CPU cores for faster conversion
8. **Progress Tracking**: Monitor conversion progress
9. **Error Handling**: Robust error handling with informative messages

## Usage Examples

### Converting a Single PDF

1. Click "Browse..." to select your PDF file
2. Set the output directory
3. Choose your desired settings (DPI, format, quality)
4. Click "Convert"

### Batch Processing

1. Check the "Batch Mode" checkbox
2. Click "Browse..." to select a folder containing multiple PDFs
3. Set the output directory
4. Adjust settings as needed
5. Click "Convert"

### Previewing Pages

1. Select your PDF file
2. Click "Get Page Count" to detect all pages
3. Enter the page number you want to preview
4. Click "Preview Page"

## Troubleshooting

### Common Issues

1. **PDF Conversion Fails**

   - Ensure you have installed poppler (on macOS/Linux)
   - Check if the PDF is password-protected
   - Try with a lower DPI setting for very large PDFs
2. **Missing Output Images**

   - Verify you have write permissions for the output directory
   - Check if the output folder exists
3. **Application Freezes**

   - For very large PDFs, the application may appear to freeze during page counting
   - Be patient or try processing fewer pages at once

### Error Messages

If you encounter error messages, they will appear in dialog boxes with details about the issue. Most common errors are related to:

- Invalid file paths
- File permission issues
- Memory limitations with very large files

## Advanced Usage

### Command Line Arguments (Optional)

The GUI application also supports command line arguments for advanced users:

```bash
python pdf2image_gui.py [pdf_path] [output_dir]
```

- `pdf_path`: Path to PDF file or directory (optional)
- `output_dir`: Path to output directory (optional)

## License

This software is distributed under the MIT License. See the LICENSE file for more information.

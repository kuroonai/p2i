# p2i - Advanced PDF & Image Processing Tool

p2i (PDF & Image) is a comprehensive GUI application for PDF and image operations, including:

**PDF Tools:**

- PDF merging, splitting, and page organizing
- PDF compression (Ghostscript, PyPDF2, image-based with presets)
- PDF to image conversion
- PDF security (passwords, permissions) & watermarking

**Image Tools:**

- Image format conversion (PNG, JPG, BMP, WEBP, TIFF, GIF, ICO)
- Image resizing/scaling with aspect ratio control
- Batch image processing (resize, convert, adjust, optimize)
- Image watermarking (text or image overlay)
- Image metadata (EXIF) viewer and stripper
- Image to PDF conversion

## Prerequisites

The application requires Python 3.9 or higher and several dependencies.

## Installation

### Step 1: Install Required OS Dependencies

#### On Windows
1. For basic functionality, no additional OS dependencies are required.
2. For enhanced PDF compression, install Ghostscript:
   - Download from the [official website](https://www.ghostscript.com/releases/gsdnld.html)
   - Choose the appropriate version (32-bit or 64-bit)
   - Run the installer and follow the wizard

#### On macOS
```bash
brew install poppler
brew install ghostscript  # For enhanced PDF compression
```

#### On Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils
sudo apt-get install -y ghostscript  # For enhanced PDF compression
sudo apt-get install python3-tk
```

### Step 2: Create a Virtual Environment (Optional but Recommended)

#### Using venv

```bash
# Create a virtual environment
python -m venv p2i-env

# Activate the virtual environment
# On Windows:
p2i-env\Scripts\activate
# On macOS/Linux:
source p2i-env/bin/activate
```

#### Using Conda

```bash
# Create a new conda environment
conda create -n p2i python=3.9

# Activate the environment
conda activate p2i

# Install conda packages (when available)
conda install -c conda-forge pillow pypdf2 reportlab tk

# Some packages might need pip
pip install pdf2image pypdfium2 tqdm
```

### Step 3: Install Python Requirements

```bash
pip install -r requirements.txt
```

## Running the Application

After installation, you can run the application:

```bash
python main.py
```

For convenience, you can also create a launcher script:

**Windows (launch.bat)**:
```bat
@echo off
start pythonw main.py
```

**macOS/Linux (launch.sh)**:
```bash
#!/bin/bash
python main.py &
```
Make it executable: `chmod +x launch.sh`

## Features

### PDF Tools

- **Merge PDFs** — Combine multiple PDFs into a single document with drag-and-drop reordering
- **Split PDF** — Extract page ranges, specific pages, or every Nth page
- **Compress PDF** — Multiple methods (Ghostscript, PyPDF2, image-based) with Low/Medium/High/Custom presets, DPI and quality controls, before/after size comparison
- **PDF to Image** — Convert pages to JPG, PNG, TIFF, BMP with adjustable DPI and batch mode
- **PDF Security** — Password protection, permission controls, text/image watermarks
- **PDF Organizer** — Visual page management: reorder, delete, insert blank, rotate, extract, duplicate

### Image Tools

- **Image to PDF** — Create PDFs from multiple images with page size, orientation, and margin options
- **Convert Image** — Format conversion between PNG, JPG, BMP, WEBP, TIFF, GIF, ICO with quality controls
- **Resize Image** — Scale by percentage, exact dimensions, or max dimension with aspect ratio lock
- **Batch Process** — Bulk resize, convert, adjust (brightness/contrast/sharpness/filters), optimize
- **Watermark** — Text or image overlay with opacity, position, rotation, and tile mode
- **Metadata** — View EXIF data, copy to clipboard, strip metadata from single or batch images

## Troubleshooting

### Common Issues

1. **PDF Conversion Fails**
   - Ensure you have installed all required dependencies
   - Check if the PDF is password-protected
   - Try with a lower DPI setting for very large PDFs

2. **Missing Output Files**
   - Verify you have write permissions for the output directory
   - Check if the output folder exists

3. **Application Freezes**
   - For very large PDFs, the application may appear to freeze during processing
   - Be patient or try processing fewer pages at once

4. **Poor Compression Results**
   - Install Ghostscript for best compression results
   - Try different compression methods for different types of PDFs
   - Some PDFs may already be highly optimized and won't compress further

5. **Security Tab Issues**
   - If experiencing issues with password protection, ensure you've entered at least one password
   - Some PDFs may have restrictions that prevent modifications

### Error Messages

If you encounter error messages, they will appear in dialog boxes with details about the issue. Most common errors are related to:
- Invalid file paths
- File permission issues
- Memory limitations with very large files
- Missing dependencies

## Pre-built Installers

### Windows

1. Download the installer from [GitHub Releases](https://github.com/kuroonai/p2i/releases)
2. Run `p2i-1.1.0-setup.exe` and follow the wizard
3. Launch p2i from the Start menu or desktop shortcut

### Building from source (Nuitka)

```bash
python -m nuitka --standalone --mingw64 --windows-console-mode=disable \
  --windows-icon-from-ico=resources/icon/app_icon.ico \
  --enable-plugin=tk-inter --include-data-dir=resources=resources \
  --output-filename=p2i.exe --output-dir=dist \
  --assume-yes-for-downloads main.py
```

Then use the included `installer.iss` with [Inno Setup](https://jrsoftware.org/isinfo.php) to create the installer.

## Dependencies

### Python packages

- Pillow >= 9.0.0
- pypdfium2 >= 3.3.0
- PyPDF2 >= 2.0.0
- reportlab >= 3.6.0
- tkinterdnd2 >= 0.3.0

### Optional

- **Ghostscript** — Required for optimal PDF compression. Download from [ghostscript.com](https://www.ghostscript.com/releases/gsdnld.html) and ensure `gswin64c` is on your PATH. p2i auto-detects Ghostscript and shows its status in the Compress PDF tab and status bar.

## License

This software is distributed under the MIT License. See the [LICENSE](LICENSE) file for more information.

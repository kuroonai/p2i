# p2i - Advanced PDF & Image Processing Tool

p2i (PDF & Image) is a comprehensive GUI application for PDF and image operations, including:
- PDF to Image conversion
- Image to PDF conversion
- PDF merging
- PDF splitting
- PDF compression (with multiple methods)
- PDF security & watermarking
- Image batch processing

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

### PDF to Image Conversion
- Convert entire PDFs or specific page ranges to images
- Support for various image formats (JPG, PNG, TIFF, BMP)
- Adjustable DPI and quality settings
- Batch processing mode for multiple PDFs

### Image to PDF Conversion
- Create PDFs from multiple image files
- Rearrange images before conversion
- Set page size, orientation, and margins
- Adjust image quality in the resulting PDF

### PDF Merging
- Combine multiple PDFs into a single document
- Rearrange PDFs before merging
- Automatic page counting and information display

### PDF Splitting
- Extract specific page ranges
- Extract individual pages by number
- Extract every Nth page
- Create new PDFs with selected content

### PDF Compression
- Multiple compression methods:
  - Ghostscript-based compression (best quality and results)
  - Direct compression with PyPDF2 (best for text-heavy PDFs)
  - Image-based compression (good for graphics-heavy PDFs)
- Three compression levels (low, medium, high)
- Automatic PDF content analysis for optimal compression method selection
- Size reduction information display

### PDF Security & Watermarking
- Password protection with owner/user passwords
- Permission controls (printing, copying, modification)
- Text and image watermarks with customizable position, opacity, and rotation
- Password removal functionality

### Image Batch Processing
- Resize images with various options (percentage, dimensions, maximum dimension)
- Convert between different image formats
- Adjust brightness, contrast, and sharpness
- Apply image filters
- Optimize images for web/storage

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

## License

This software is distributed under the MIT License. See the LICENSE file for more information.
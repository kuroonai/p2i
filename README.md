# PDF Utils - Advanced PDF Processing GUI

This application provides a comprehensive GUI for PDF and image operations, including:
- PDF to Image conversion
- Image to PDF conversion
- PDF merging
- PDF splitting
- PDF compression (with multiple compression methods)

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
```

### Step 2: Create a Virtual Environment (Optional but Recommended)

```bash
# Create a virtual environment
python -m venv pdfutils-env

# Activate the virtual environment
# On Windows:
pdfutils-env\Scripts\activate
# On macOS/Linux:
source pdfutils-env/bin/activate
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

## Compression Methods Explained

The application offers several compression strategies:

1. **Ghostscript Compression**: Uses the industry-standard Ghostscript tool with optimized presets. This usually provides the best compression while maintaining quality. Requires Ghostscript to be installed on your system.

2. **Direct Compression**: Preserves text quality while compressing embedded images and content streams. Best for text-heavy documents like reports or articles.

3. **Image-based Compression**: Converts PDF pages to compressed images before creating a new PDF. This can achieve high compression ratios but may reduce text quality. Best for PDFs with many graphics.

The application automatically analyzes your PDF and suggests the best method, but you can override this choice if needed.

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

### Error Messages

If you encounter error messages, they will appear in dialog boxes with details about the issue. Most common errors are related to:
- Invalid file paths
- File permission issues
- Memory limitations with very large files
- Missing dependencies

## License

This software is distributed under the MIT License. See the LICENSE file for more information.
# p2i Documentation

Welcome to the official documentation for p2i (PDF & Image Tool), a free and open-source desktop application for PDF and image processing.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Features](#features)
   - [PDF Merge](#pdf-merge)
   - [PDF Split](#pdf-split)
   - [PDF Compress](#pdf-compress)
   - [PDF to Image](#pdf-to-image)
   - [PDF Security](#pdf-security)
   - [PDF Organizer](#pdf-organizer)
   - [Image to PDF](#image-to-pdf)
   - [Image Batch Processing](#image-batch-processing)
4. [Advanced Usage](#advanced-usage)
5. [Troubleshooting](#troubleshooting)
6. [Contributing](#contributing)
7. [License](#license)

## Introduction

p2i is a comprehensive toolkit for handling PDF and image files, designed with simplicity and efficiency in mind. Whether you need to merge PDFs, extract specific pages, convert between formats, or process images in bulk, p2i provides these capabilities through an intuitive user interface.

The application is built with Python and uses industry-standard libraries like PyPDF2 and Pypdfium2 for reliable PDF processing, and Pillow (PIL) for image manipulation.

## Installation

### System Requirements

- **Operating System**: Windows 7/10/11, macOS 10.13+, or most Linux distributions
- **Disk Space**: Approximately 100MB
- **RAM**: 2GB minimum (4GB recommended)
- **Python**: Bundled with the application (no separate installation required)

### Installation Methods

#### Windows
1. Download the installer (.exe) from the [GitHub Releases](https://github.com/kuroonai/p2i/releases) page
2. Run the installer and follow the on-screen instructions
3. Launch p2i from the Start menu or desktop shortcut

#### macOS
1. Download the .dmg file from the [GitHub Releases](https://github.com/kuroonai/p2i/releases) page
2. Open the .dmg file and drag the p2i application to your Applications folder
3. Launch p2i from your Applications folder
   
   Note: You may need to right-click the app and select "Open" the first time to bypass macOS security warnings.

#### Linux
1. Download the AppImage from the [GitHub Releases](https://github.com/kuroonai/p2i/releases) page
2. Make it executable: `chmod +x p2i-x86_64.AppImage`
3. Run the AppImage: `./p2i-x86_64.AppImage`

#### From Source
For developers or advanced users who want to run from source:

1. Clone the repository: `git clone https://github.com/kuroonai/p2i.git`
2. Navigate to the project directory: `cd p2i`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Run the application: `python main.py`

## Features

### PDF Merge

Combine multiple PDF files into a single document.

#### Usage

1. Navigate to the "Merge PDFs" tab
2. Click "Add PDFs" to select the PDF files you want to merge
3. Use the "Move Up" and "Move Down" buttons to arrange the files in the desired order
4. Set the output directory and filename
5. Click "Merge PDFs" to create the merged document

#### Options

- **Reordering**: Arrange PDFs in any order before merging
- **Output Selection**: Choose where to save the merged file
- **Drag and Drop**: Directly drag PDF files into the application

#### Tips

- The order of PDFs in the list determines their order in the final document
- You can remove a PDF from the list by selecting it and clicking "Remove Selected"
- To clear all PDFs from the list, click "Clear All"

### PDF Split

Extract specific pages or page ranges from a PDF document.

#### Usage

1. Navigate to the "Split PDF" tab
2. Click "Browse..." to select the PDF file you want to split
3. Click "Get Page Count" to see the total number of pages
4. Choose a split mode (Page Range, Single Pages, or Extract Every N Pages)
5. Set the output directory
6. Click "Split PDF" to extract the specified pages

#### Split Modes

- **Page Range**: Extract a continuous range of pages (e.g., pages 5-10)
- **Single Pages**: Extract specific pages by number (e.g., 1,3,5-7)
- **Extract Every N Pages**: Extract pages at regular intervals (e.g., every 2nd page)

#### Tips

- You can preview the PDF structure before splitting by checking the page count
- For complex extractions, use the "Single Pages" mode with comma-separated values and ranges
- The output will be saved with a filename indicating the extracted pages

### PDF Compress

Reduce the file size of PDF documents while maintaining reasonable quality.

#### Usage

1. Navigate to the "Compress PDF" tab
2. Click "Browse..." to select the PDF file you want to compress
3. Choose the compression level (Low, Medium, or High)
4. Select the compression method (Auto, Image-based, or Direct)
5. Set the output directory and filename
6. Click "Compress PDF" to create the optimized document

#### Compression Levels

- **Low**: Better quality, larger file size
- **Medium**: Balanced quality and size
- **High**: Lower quality, smaller file size

#### Compression Methods

- **Auto**: Analyzes content and selects the best method
- **Image-based**: Best for PDFs with many images or graphics
- **Direct**: Best for text-heavy documents

#### Tips

- If your PDF contains both text and images, the "Auto" method usually produces the best results
- Check the original and compressed file sizes to see the reduction
- For very large PDFs, compression may take several minutes

### PDF to Image

Convert PDF pages to image files in various formats.

#### Usage

1. Navigate to the "PDF to Image" tab
2. Click "Browse..." to select the PDF file you want to convert
3. Click "Get Page Count" to see the total number of pages
4. Set the page range, DPI, and output format
5. Set the output directory
6. Click "Convert PDF to Images" to start the conversion

#### Options

- **Page Range**: Choose which pages to convert
- **DPI**: Set the resolution of the output images (72-600 DPI)
- **Format**: Choose the image format (JPG, PNG, TIFF, BMP)
- **Quality**: Adjust the quality setting for JPG output (10-100%)
- **Threads**: Utilize multiple CPU cores for faster conversion

#### Batch Mode

For converting multiple PDFs:

1. Check "Batch Mode"
2. Select a folder containing PDF files
3. Set output options
4. Click "Convert PDF to Images" to process all PDFs

#### Tips

- Higher DPI values result in larger, more detailed images
- Preview a single page before converting all pages to check quality
- For web use, 72-150 DPI is usually sufficient
- For printing, consider 300 DPI or higher

### PDF Security

Add or remove password protection and watermarks from PDF documents.

#### Usage

1. Navigate to the "PDF Security" tab
2. Click "Browse..." to select the PDF file you want to modify
3. Choose a security operation (No Password Changes, Add Password Protection, or Remove Password Protection)
4. Configure security settings or watermark options
5. Set the output directory and filename
6. Click "Process PDF" to create the secured or watermarked document

#### Security Operations

- **Add Password Protection**: Set owner and/or user passwords with customizable permissions
- **Remove Password Protection**: Remove existing password protection (requires the current password)
- **Watermarking**: Add text or image watermarks with adjustable position, opacity, and rotation

#### Permission Options

When adding password protection, you can control:
- Printing permissions
- Content copying permissions
- Modification permissions

#### Watermark Options

- **Type**: Text or image watermark
- **Position**: Center, top-left, top-right, bottom-left, or bottom-right
- **Opacity**: Control watermark transparency (10-100%)
- **Rotation**: Adjust watermark angle (0-360°)

#### Tips

- The owner password allows full access to the PDF, while the user password restricts actions based on permissions
- For watermarks to be visible but not intrusive, use 20-40% opacity
- Diagonal watermarks (45° rotation) are harder to remove
- Store secure passwords safely, as they cannot be recovered if lost

### PDF Organizer

Visually organize pages from one or more PDF documents, add blank pages, and create a new arranged PDF.

#### Usage

1. Navigate to the "PDF Organizer" tab
2. Click "Add PDFs" to select the PDF files you want to organize
3. Use the page thumbnails or preview to navigate through pages
4. Rearrange, delete, or add pages as needed
5. Set the output directory and filename
6. Click "Save Organized PDF" to create the new document

#### Page Operations

- **Delete Page**: Remove the current page
- **Insert Blank Page**: Add a blank page before the current page
- **Insert Blank After**: Add a blank page after the current page
- **Rotate Page**: Rotate pages left or right (90° increments)
- **Extract Page**: Save the current page as a separate PDF
- **Duplicate Page**: Create a copy of the current page
- **Move to Position**: Move the current page to a specific position

#### Navigation and View

- **Previous/Next**: Navigate between pages
- **Zoom Controls**: Adjust the page preview size
- **Thumbnails View**: See all pages at once in the "Pages" tab
- **Drag and Drop**: Reorder pages by dragging thumbnails

#### Tips

- Use the "PDF Files" tab to manage source documents
- Use the "Pages" tab to see and rearrange individual pages
- For complex documents, add blank pages where needed for printing considerations
- Preview each page to ensure proper orientation before saving

### Image to PDF

Convert one or more image files to a PDF document.

#### Usage

1. Navigate to the "Image to PDF" tab
2. Click "Add Images" to select the image files you want to convert
3. Use the "Move Up" and "Move Down" buttons to arrange the images in the desired order
4. Set page size, orientation, and margin options
5. Set the output directory and filename
6. Click "Create PDF from Images" to generate the PDF

#### Options

- **Page Size**: Choose from standard sizes (A4, Letter, Legal, etc.)
- **Orientation**: Portrait or landscape
- **Margin**: Set margins in millimeters
- **Image Quality**: Adjust quality for the embedded images (10-100%)

#### Preview

- Click "Preview Selected Image" to see how an image will appear in the PDF
- The preview shows the image with the current page settings

#### Tips

- Images are resized to fit the page while maintaining their aspect ratio
- For best results, use high-resolution images
- To create multi-page PDFs, add all images in the desired order
- For consistent page layout, use images with similar dimensions

### Image Batch Processing

Process multiple images with the same operations at once.

#### Usage

1. Navigate to the "Image Processing" tab
2. Click "Browse..." to select the directory containing images
3. Choose the operation type (resize, convert, adjust, or optimize)
4. Configure the operation-specific settings
5. Set the output directory
6. Click "Process Images" to start batch processing

#### Operation Types

- **Resize**: Change image dimensions using various methods
- **Convert**: Change image format with quality options
- **Adjust**: Modify brightness, contrast, and apply filters
- **Optimize**: Reduce file size for web/sharing

#### Resize Options

- **Percentage**: Resize to a percentage of original size
- **Dimensions**: Set specific width and height
- **Max Dimension**: Set maximum width or height while maintaining aspect ratio

#### Format Conversion

- Convert images to JPG, PNG, TIFF, BMP, or WebP
- Adjust quality and compression settings for each format

#### Image Adjustments

- **Brightness**: Lighten or darken images (0.1-2.0)
- **Contrast**: Increase or decrease contrast (0.1-2.0)
- **Sharpness**: Adjust image sharpness (0.1-2.0)
- **Filters**: Apply effects like blur, sharpen, or edge enhancement

#### Tips

- Use "Select Image for Preview" to test settings on a single image before processing all files
- For web images, the "Optimize" operation with 70-80% quality is usually a good balance
- Batch processing can handle hundreds of images at once
- Use meaningful filenames in the output to identify processed images

## Advanced Usage

### Command Line Interface

p2i includes a command-line interface for automation and scripting:

```bash
# Merge PDFs
python -m p2i merge -o output.pdf input1.pdf input2.pdf input3.pdf

# Split PDF pages 1-5
python -m p2i split -i input.pdf -o output_dir -r 1-5

# Convert PDF to images
python -m p2i pdf2img -i input.pdf -o output_dir -f jpg -d 300

# Create PDF from images
python -m p2i img2pdf -o output.pdf -s A4 input1.jpg input2.jpg
```

Run `python -m p2i --help` for a complete list of commands and options.

### Drag and Drop Support

All tabs in the application support drag and drop:

1. Simply drag files from your file explorer
2. Drop them onto the appropriate tab
3. The application will automatically add the files to the current operation

### Configuration Options

p2i stores user preferences in a configuration file located at:

- Windows: `%APPDATA%\.p2i\settings.json`
- macOS: `~/Library/Application Support/.p2i/settings.json`
- Linux: `~/.p2i/settings.json`

You can manually edit this file to change default settings.

## Troubleshooting

### Common Issues

#### "File not found" error when opening a PDF
- Ensure the file path doesn't contain special characters
- Check if you have read permissions for the file
- Try moving the file to a different location

#### Application doesn't start
- Verify you have the correct version for your operating system
- Check if your antivirus isn't blocking the application
- Try running as administrator (Windows) or with sudo (Linux)

#### Slow performance with large files
- For PDFs larger than 50MB, operations may take longer
- Try closing other applications to free up memory
- For batch operations, process fewer files at once

#### PDF is password-protected
- You'll need the correct password to modify protected PDFs
- Use the "PDF Security" tab to remove the password (if you know it)

#### "Missing dependencies" warning
- Some operations require additional software like Ghostscript
- Follow the instructions in the warning message to install them

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/kuroonai/p2i/issues) page for similar problems
2. Use the "Report Bugs" section in the "Contribute" dialog to submit a detailed report
3. Include error messages and steps to reproduce the issue

## Contributing

We welcome contributions from everyone! To get started:

1. From the Help menu, select "Contribute to p2i"
2. Choose how you'd like to contribute (code, documentation, translations, bug reports)
3. Follow the instructions in the contribution dialog

For code contributions:

1. Fork the repository on GitHub
2. Create a branch for your feature or fix
3. Make your changes and test them
4. Submit a pull request with a clear description of the changes

See the [CONTRIBUTING.md](https://github.com/kuroonai/p2i/blob/main/CONTRIBUTING.md) file for detailed guidelines.

## License

p2i is released under the MIT License. This means you are free to use, modify, and distribute the software, even for commercial purposes, as long as you include the original copyright notice.

See the [LICENSE](https://github.com/kuroonai/p2i/blob/main/LICENSE) file for the full text of the license.

---

© 2025 p2i Team | [GitHub Repository](https://github.com/kuroonai/p2i)

import os
import threading
import tempfile
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pypdfium2 as pdfium
from PIL import Image
import utils

# Import PyPDF2 for direct PDF manipulation
try:
    from PyPDF2 import PdfReader, PdfWriter
    HAVE_PYPDF2 = True
except ImportError:
    HAVE_PYPDF2 = False

class PDFCompressTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_name = tk.StringVar(value="compressed.pdf")
        self.compress_level = tk.StringVar(value="medium")  # low, medium, high
        self.compress_method = tk.StringVar(value="auto")  # auto, image, direct
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.conversion_canceled = False
        
        # Create UI elements
        self.create_file_frame()
        self.create_options_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame, 
            self.start_compression, 
            self.cancel_compression, 
            self.open_output_folder,
            "Compress PDF"
        )
        
        # Set default output directory to user's Documents folder
        default_output = os.path.join(str(Path.home()), "Documents")
        self.output_dir.set(default_output)
        
        # Show warning if PyPDF2 is not available
        if not HAVE_PYPDF2:
            self.status_var.set("Warning: PyPDF2 not found. Direct compression unavailable.")
    
    def create_file_frame(self):
        file_frame = ttk.LabelFrame(self.frame, text="PDF Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # PDF File selection
        ttk.Label(file_frame, text="PDF File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_pdf).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Output directory selection
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        
        # Output filename
        ttk.Label(file_frame, text="Output Filename:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_name, width=50).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # File size info
        self.file_size_label = ttk.Label(file_frame, text="Original Size: -")
        self.file_size_label.grid(row=3, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Make column 1 expand
        file_frame.columnconfigure(1, weight=1)
    
    def create_options_frame(self):
        options_frame = ttk.LabelFrame(self.frame, text="Compression Options", padding=10)
        options_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Compression level selection
        ttk.Label(options_frame, text="Compression Level:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        level_frame = ttk.Frame(options_frame)
        level_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(level_frame, text="Low (Better Quality, Larger Size)", 
                      variable=self.compress_level, value="low").pack(anchor="w")
        ttk.Radiobutton(level_frame, text="Medium (Balanced Quality and Size)", 
                      variable=self.compress_level, value="medium").pack(anchor="w")
        ttk.Radiobutton(level_frame, text="High (Lower Quality, Smaller Size)", 
                      variable=self.compress_level, value="high").pack(anchor="w")
        
        # Compression method selection (only if PyPDF2 is available)
        if HAVE_PYPDF2:
            ttk.Label(options_frame, text="Compression Method:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
            
            method_frame = ttk.Frame(options_frame)
            method_frame.grid(row=1, column=1, sticky="w", padx=5, pady=5)
            
            ttk.Radiobutton(method_frame, text="Auto (Best for mixed content)", 
                          variable=self.compress_method, value="auto").pack(anchor="w")
            ttk.Radiobutton(method_frame, text="Image-based (Best for graphics/photos)", 
                          variable=self.compress_method, value="image").pack(anchor="w")
            ttk.Radiobutton(method_frame, text="Direct (Best for text documents)", 
                          variable=self.compress_method, value="direct").pack(anchor="w")
        
        # Explanation
        explanation = """Compression works by optimizing the PDF content.
Auto mode analyzes your PDF and selects the best method.
Image-based compresses by converting pages to images (good for graphics).
Direct compression preserves text quality (best for text-heavy documents).
Note: Results may vary depending on the PDF content."""
        
        explanation_label = ttk.Label(options_frame, text=explanation, wraplength=500, justify="left")
        explanation_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    def browse_pdf(self):
        selected_file = filedialog.askopenfilename(
            title="Select PDF File to Compress",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if selected_file:
            self.pdf_path.set(selected_file)
            self.status_var.set(f"Selected file: {os.path.basename(selected_file)}")
            self.update_file_size_info()
            
            # Set default output filename based on input filename
            pdf_basename = os.path.splitext(os.path.basename(selected_file))[0]
            self.output_name.set(f"{pdf_basename}_compressed.pdf")
            
            # Analyze PDF to suggest the best compression method
            if HAVE_PYPDF2:
                threading.Thread(target=self._analyze_pdf).start()
    
    def _analyze_pdf(self):
        """Analyze PDF to determine if it's more text or image heavy"""
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Analyzing PDF content..."))
            
            reader = PdfReader(self.pdf_path.get())
            total_size = os.path.getsize(self.pdf_path.get())
            image_size = 0
            
            # Count images and their size
            for page in reader.pages:
                if "/Resources" in page and "/XObject" in page["/Resources"]:
                    x_objects = page["/Resources"]["/XObject"].get_object()
                    for obj in x_objects:
                        if x_objects[obj]["/Subtype"] == "/Image":
                            if "/Length" in x_objects[obj]:
                                image_size += x_objects[obj]["/Length"]
            
            # Calculate image percentage
            image_ratio = image_size / total_size if total_size > 0 else 0
            
            # Suggest best method
            if image_ratio > 0.5:
                self.compress_method.set("image")
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Analysis complete: Image-heavy PDF detected"))
            else:
                self.compress_method.set("direct")
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Analysis complete: Text-heavy PDF detected"))
        except Exception as e:
            error_msg = str(e)
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"PDF analysis error: {error_msg}"))
    
    def browse_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)
    
    def update_file_size_info(self):
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            return
            
        file_size = os.path.getsize(self.pdf_path.get())
        file_size_formatted = utils.format_file_size(file_size)
        self.file_size_label.config(text=f"Original Size: {file_size_formatted}")
    
    def start_compression(self):
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return
        
        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory.")
            return
            
        if not self.output_name.get():
            messagebox.showerror("Error", "Please enter a name for the output PDF file.")
            return
            
        # Add .pdf extension if not present
        pdf_filename = self.output_name.get()
        if not pdf_filename.lower().endswith('.pdf'):
            pdf_filename += ".pdf"
            
        output_path = os.path.join(self.output_dir.get(), pdf_filename)
        
        # Confirm if file exists
        if os.path.exists(output_path):
            result = messagebox.askyesno("Confirm", f"File {pdf_filename} already exists. Overwrite?")
            if not result:
                return
                
        # Disable controls during compression
        utils.set_controls_state(self.frame, tk.DISABLED)
        
        # Determine compression method to use
        method = self.compress_method.get()
        if method == "auto":
            # Auto-determine based on file analysis
            if hasattr(self, "_image_ratio") and self._image_ratio > 0.5:
                method = "image"
            else:
                method = "direct" if HAVE_PYPDF2 else "image"
        
        # Start compression in a separate thread
        self.conversion_canceled = False
        threading.Thread(target=self._compression_thread, args=(output_path, method)).start()
    
    def _compression_thread(self, output_path, method):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Compressing PDF using {method} method..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
            # Try Ghostscript first for best compression (if method supports it)
            if method in ["auto", "image"]:
                try:
                    self._gs_compress_pdf(output_path)
                    # If successful, skip to the end
                except Exception as e:
                    # If Ghostscript fails, fall back to other methods
                    if method == "direct" and HAVE_PYPDF2:
                        self._direct_compress_pdf(output_path)
                    else:
                        self._image_compress_pdf(output_path)
            else:
                # Use chosen method directly
                if method == "direct" and HAVE_PYPDF2:
                    self._direct_compress_pdf(output_path)
                else:
                    self._image_compress_pdf(output_path)
                
                # Get and display file size reduction
                original_size = os.path.getsize(self.pdf_path.get())
                compressed_size = os.path.getsize(output_path)
                original_formatted = utils.format_file_size(original_size)
                compressed_formatted = utils.format_file_size(compressed_size)
                reduction_percent = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
                
                result_message = (
                    f"Compression complete!\n"
                    f"Original size: {original_formatted}\n"
                    f"Compressed size: {compressed_formatted}\n"
                    f"Reduction: {reduction_percent:.1f}%\n"
                    f"Saved to: {output_path}"
                )
                
                # Complete
                self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Compression complete: {os.path.basename(output_path)}"))
                self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", result_message))
                
        except Exception as e:
            error_msg = str(e)
            
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to compress PDF: {error_msg}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {error_msg}"))
            # Delete partial output
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
        finally:
            # Re-enable controls
            self.frame.winfo_toplevel().after(0, lambda: utils.set_controls_state(self.frame, tk.NORMAL))
    
    def _direct_compress_pdf(self, output_path):
        """Compress PDF directly using PyPDF2 (preserves text quality)"""
        reader = PdfReader(self.pdf_path.get())
        writer = PdfWriter()
        
        # Get compression parameters based on level
        level = self.compress_level.get()
        if level == "low":
            compress_images = True
            image_quality = 90
        elif level == "medium":
            compress_images = True
            image_quality = 75
        else:  # high
            compress_images = True
            image_quality = 60
        
        # Process each page
        total_pages = len(reader.pages)
        for i, page in enumerate(reader.pages):
            if self.conversion_canceled:
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Compression canceled"))
                return
            
            # Update progress
            progress_pct = ((i + 1) / total_pages) * 100
            current_page = i+1
            self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
            self.frame.winfo_toplevel().after(0, lambda p=current_page, t=total_pages: 
                self.status_var.set(f"Processing page {p}/{t}..."))
            
            # Add page to the writer
            writer.add_page(page)
            
            # Attempt to compress images within the page if present
            if compress_images and "/Resources" in page and "/XObject" in page["/Resources"]:
                x_objects = page["/Resources"]["/XObject"].get_object()
                for obj_id in x_objects:
                    obj = x_objects[obj_id]
                    if obj["/Subtype"] == "/Image":
                        writer.compress_content_streams = True  # This compresses text and other content
        
        # Save the compressed file
        with open(output_path, "wb") as f:
            writer.write(f)
    
    def _image_compress_pdf(self, output_path):
        """Compress PDF by converting to images with aggressive compression settings"""
        # Open the PDF
        pdf = pdfium.PdfDocument(self.pdf_path.get())
        page_count = len(pdf)
        
        # Get compression parameters based on level - more aggressive settings
        level = self.compress_level.get()
        if level == "low":
            dpi = 100  # Reduced from 120
            quality = 70  # Reduced from 80
            optimize = True
        elif level == "medium":
            dpi = 75   # Reduced from 100 
            quality = 50  # Reduced from 60
            optimize = True
        else:  # high
            dpi = 60   # Reduced from 80
            quality = 30  # Reduced from 45
            optimize = True
        
        # Create a temporary directory for the images
        with tempfile.TemporaryDirectory() as temp_dir:
            # Convert each page to an image and save in temporary directory
            for page_idx in range(page_count):
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Compression canceled"))
                    return
                
                # Update progress
                progress_pct = ((page_idx + 1) / (page_count * 2)) * 100  # First half for rendering
                current_page = page_idx+1
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=current_page: 
                    self.status_var.set(f"Rendering page {p}/{page_count}..."))
                
                # Render page to image
                page = pdf[page_idx]
                pil_image = page.render(
                    scale=dpi/72,  # Convert DPI to scale factor
                    rotation=0
                ).to_pil()
                
                # Additional pre-processing to reduce size
                # Convert to grayscale for further reduction if high compression
                if level == "high" and not self._is_color_critical(pil_image):
                    pil_image = pil_image.convert('L')
                
                # Resize if the image is very large
                if max(pil_image.size) > 2000 and level in ["medium", "high"]:
                    factor = 2000 / max(pil_image.size)
                    new_size = (int(pil_image.size[0] * factor), int(pil_image.size[1] * factor))
                    pil_image = pil_image.resize(new_size, Image.LANCZOS)
                
                # Save as JPEG with compression
                img_path = os.path.join(temp_dir, f"page_{page_idx}.jpg")
                pil_image.save(img_path, format="JPEG", quality=quality, optimize=optimize)
            
            # Create a new PDF from the compressed images with minimal metadata
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            
            c = canvas.Canvas(output_path)
            
            # Add each image as a page
            for page_idx in range(page_count):
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Compression canceled"))
                    # Delete partial output
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
                    return
                
                # Update progress
                progress_pct = (((page_idx + 1) / page_count) * 50) + 50  # Second half for creating PDF
                current_page = page_idx+1
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=current_page: 
                    self.status_var.set(f"Creating page {p}/{page_count}..."))
                
                # Open the image
                img_path = os.path.join(temp_dir, f"page_{page_idx}.jpg")
                img = Image.open(img_path)
                
                # Get the PDF page dimensions from the original PDF
                orig_page = pdf[page_idx]
                width, height = orig_page.get_size()
                
                # Set the page size to match the original
                c.setPageSize((width, height))
                
                # Create a new page
                if page_idx > 0:
                    c.showPage()
                
                # Draw the image to fill the page
                c.drawImage(ImageReader(img), 0, 0, width=width, height=height)
            
            # Save the PDF with minimal metadata
            c.setAuthor("")
            c.setCreator("")
            c.setTitle("")
            c.setSubject("")
            c.save()

    def _is_color_critical(self, img):
        """
        Detect if an image relies heavily on color
        Returns True if converting to grayscale would lose important info
        """
        # Simple heuristic: sample pixels and check if color variation is significant
        try:
            pixels = img.getdata()
            sample_size = min(1000, len(pixels))
            stride = max(1, len(pixels) // sample_size)
            
            sampled_pixels = [pixels[i] for i in range(0, len(pixels), stride)]
            
            # Check if RGB values differ significantly
            color_variance = sum(
                abs(p[0] - p[1]) + abs(p[1] - p[2]) + abs(p[0] - p[2])
                for p in sampled_pixels if len(p) >= 3
            ) / len(sampled_pixels)
            
            # If average variance between channels is > 30, consider color important
            return color_variance > 30
        except:
            # If any issues, default to keeping color
            return True
    
    def cancel_compression(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling compression...")
    
    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())

    def _gs_compress_pdf(self, output_path):
        """Use Ghostscript for compression if available (usually most effective)"""
        import subprocess
        import platform
        
        # Check if ghostscript is available
        gs_command = "gswin64c" if platform.system() == "Windows" else "gs"
        try:
            subprocess.run([gs_command, "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except (subprocess.SubprocessError, FileNotFoundError):
            # Ghostscript not found, fall back to image compression
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Ghostscript not found, using fallback method..."))
            self._image_compress_pdf(output_path)
            return
        
        level = self.compress_level.get()
        if level == "low":
            preset = "printer"
            dpi = "150"
        elif level == "medium":
            preset = "ebook"
            dpi = "120"
        else:  # high
            preset = "screen"
            dpi = "72"
        
        self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Compressing with Ghostscript ({preset} preset)..."))
        
        # Ghostscript command for PDF compression
        gs_cmd = [
            gs_command,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/" + preset,
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-r{dpi}",
            "-sOutputFile=" + output_path,
            self.pdf_path.get()
        ]
        
        # Run Ghostscript
        try:
            subprocess.run(gs_cmd, check=True)
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
        except subprocess.SubprocessError as e:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Ghostscript error: {e}"))
            # Fall back to image compression
            self._image_compress_pdf(output_path)
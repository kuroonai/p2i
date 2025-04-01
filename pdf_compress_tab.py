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
        
        # Explanation
        explanation = """Compression works by reducing image quality and optimizing content.
Low compression preserves most quality but with minimal size reduction.
Medium compression offers a good balance between quality and file size.
High compression reduces quality more but creates smaller files.
Note: Results may vary depending on the PDF content."""
        
        explanation_label = ttk.Label(options_frame, text=explanation, wraplength=500, justify="left")
        explanation_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
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
        
        # Start compression in a separate thread
        self.conversion_canceled = False
        threading.Thread(target=self._compression_thread, args=(output_path,)).start()
    
    def _compression_thread(self, output_path):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Compressing PDF..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
            # Open the PDF
            pdf = pdfium.PdfDocument(self.pdf_path.get())
            page_count = len(pdf)
            
            # Get compression parameters based on level
            level = self.compress_level.get()
            if level == "low":
                dpi = 150
                quality = 85
                optimize = True
            elif level == "medium":
                dpi = 120
                quality = 75
                optimize = True
            else:  # high
                dpi = 100
                quality = 60
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
                    self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                    self.frame.winfo_toplevel().after(0, lambda p=page_idx+1: 
                        self.status_var.set(f"Rendering page {p}/{page_count}..."))
                    
                    # Render page to image
                    page = pdf[page_idx]
                    pil_image = page.render(
                        scale=dpi/72,  # Convert DPI to scale factor
                        rotation=0
                    ).to_pil()
                    
                    # Save as JPEG with compression
                    img_path = os.path.join(temp_dir, f"page_{page_idx}.jpg")
                    pil_image.save(img_path, format="JPEG", quality=quality, optimize=optimize)
                
                # Create a new PDF from the compressed images
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                from reportlab.lib.utils import ImageReader
                
                c = canvas.Canvas(output_path, pagesize=letter)
                
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
                    self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                    self.frame.winfo_toplevel().after(0, lambda p=page_idx+1: 
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
                
                # Save the PDF
                c.save()
            
            # Get and display file size reduction
            original_size = os.path.getsize(self.pdf_path.get())
            compressed_size = os.path.getsize(output_path)
            original_formatted = utils.format_file_size(original_size)
            compressed_formatted = utils.format_file_size(compressed_size)
            reduction_percent = ((original_size - compressed_size) / original_size) * 100
            
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
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to compress PDF: {str(e)}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            # Delete partial output
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
        finally:
            # Re-enable controls
            self.frame.winfo_toplevel().after(0, lambda: utils.set_controls_state(self.frame, tk.NORMAL))
    
    def cancel_compression(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling compression...")
    
    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())
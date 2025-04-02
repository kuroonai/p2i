# pdf_security_tab.py
import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pypdfium2 as pdfium
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageDraw, ImageFont
import utils

class PDFSecurityTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_name = tk.StringVar(value="secured.pdf")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        
        # Security options
        self.use_encryption = tk.BooleanVar(value=False)
        self.owner_password = tk.StringVar()
        self.user_password = tk.StringVar()
        
        # Permission options
        self.allow_printing = tk.BooleanVar(value=True)
        self.allow_copying = tk.BooleanVar(value=True)
        self.allow_modification = tk.BooleanVar(value=True)
        
        # Watermark options
        self.add_watermark = tk.BooleanVar(value=False)
        self.watermark_text = tk.StringVar(value="CONFIDENTIAL")
        self.watermark_type = tk.StringVar(value="text")  # text or image
        self.watermark_image_path = tk.StringVar()
        self.watermark_opacity = tk.IntVar(value=30)
        self.watermark_position = tk.StringVar(value="center")
        self.watermark_rotation = tk.IntVar(value=45)
        
        # Create UI elements
        self.create_file_frame()
        self.create_security_frame()
        self.create_watermark_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame, 
            self.start_process, 
            self.cancel_process, 
            self.open_output_folder,
            "Process PDF"
        )
        
        # Set default output directory
        default_output = os.path.join(str(Path.home()), "Documents")
        self.output_dir.set(default_output)
        
        # Process canceled flag
        self.process_canceled = False
    
    def create_file_frame(self):
        file_frame = ttk.LabelFrame(self.frame, text="File Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # PDF File selection
        ttk.Label(file_frame, text="PDF File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_pdf).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Output settings
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        
        ttk.Label(file_frame, text="Output Filename:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_name, width=50).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # Make column 1 expand
        file_frame.columnconfigure(1, weight=1)
    
    def create_security_frame(self):
        security_frame = ttk.LabelFrame(self.frame, text="Security Settings", padding=10)
        security_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Enable encryption checkbox
        ttk.Checkbutton(
            security_frame, 
            text="Enable Password Protection", 
            variable=self.use_encryption,
            command=self.toggle_encryption
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Password entry fields
        self.password_frame = ttk.Frame(security_frame)
        self.password_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.password_frame, text="Owner Password:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.owner_pw_entry = ttk.Entry(self.password_frame, textvariable=self.owner_password, width=20, show="*")
        self.owner_pw_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.password_frame, text="User Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.user_pw_entry = ttk.Entry(self.password_frame, textvariable=self.user_password, width=20, show="*")
        self.user_pw_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Permissions frame
        self.permissions_frame = ttk.LabelFrame(security_frame, text="Permissions", padding=5)
        self.permissions_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Checkbutton(self.permissions_frame, text="Allow Printing", variable=self.allow_printing).grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(self.permissions_frame, text="Allow Copying", variable=self.allow_copying).grid(
            row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(self.permissions_frame, text="Allow Modification", variable=self.allow_modification).grid(
            row=1, column=0, sticky="w", padx=5, pady=2)
        
        # Initially disable password fields
        self.toggle_encryption()
    
    def create_watermark_frame(self):
        watermark_frame = ttk.LabelFrame(self.frame, text="Watermark Settings", padding=10)
        watermark_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Enable watermark checkbox
        ttk.Checkbutton(
            watermark_frame, 
            text="Add Watermark", 
            variable=self.add_watermark,
            command=self.toggle_watermark
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Watermark options frame
        self.watermark_options = ttk.Frame(watermark_frame)
        self.watermark_options.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Watermark type
        ttk.Label(self.watermark_options, text="Type:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        type_frame = ttk.Frame(self.watermark_options)
        type_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(type_frame, text="Text", variable=self.watermark_type, value="text", 
                      command=self.toggle_watermark_type).pack(side="left", padx=5)
        ttk.Radiobutton(type_frame, text="Image", variable=self.watermark_type, value="image", 
                      command=self.toggle_watermark_type).pack(side="left", padx=5)
        
        # Text watermark options
        self.text_options = ttk.Frame(self.watermark_options)
        self.text_options.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.text_options, text="Text:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.text_options, textvariable=self.watermark_text, width=30).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)
        
        # Image watermark options
        self.image_options = ttk.Frame(self.watermark_options)
        self.image_options.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.image_options, text="Image:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.image_options, textvariable=self.watermark_image_path, width=30).grid(
            row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.image_options, text="Browse...", command=self.browse_watermark_image).grid(
            row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Common watermark options
        ttk.Label(self.watermark_options, text="Position:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        position_combo = ttk.Combobox(self.watermark_options, textvariable=self.watermark_position, 
                                    values=["center", "top-left", "top-right", "bottom-left", "bottom-right"], width=15)
        position_combo.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.watermark_options, text="Opacity (%):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        ttk.Scale(self.watermark_options, from_=10, to=100, variable=self.watermark_opacity, orient="horizontal").grid(
            row=4, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.watermark_options, text="Rotation (°):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        ttk.Scale(self.watermark_options, from_=0, to=360, variable=self.watermark_rotation, orient="horizontal").grid(
            row=5, column=1, sticky="ew", padx=5, pady=5)
        
        # Initially hide watermark options
        self.toggle_watermark()
        self.toggle_watermark_type()
    
    def toggle_encryption(self):
        if self.use_encryption.get():
            for child in self.password_frame.winfo_children():
                child.configure(state="normal")
            for child in self.permissions_frame.winfo_children():
                child.configure(state="normal")
        else:
            for child in self.password_frame.winfo_children():
                child.configure(state="disabled")
            for child in self.permissions_frame.winfo_children():
                child.configure(state="disabled")
    
    def toggle_watermark(self):
        if self.add_watermark.get():
            self.watermark_options.grid()
        else:
            self.watermark_options.grid_remove()
    
    def toggle_watermark_type(self):
        if self.watermark_type.get() == "text":
            self.text_options.grid()
            self.image_options.grid_remove()
        else:
            self.text_options.grid_remove()
            self.image_options.grid()
    
    def browse_pdf(self):
        selected_file = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if selected_file:
            self.pdf_path.set(selected_file)
            
            # Set default output name based on input filename
            pdf_basename = os.path.splitext(os.path.basename(selected_file))[0]
            if self.use_encryption.get() and self.add_watermark.get():
                output_name = f"{pdf_basename}_secured_watermarked.pdf"
            elif self.use_encryption.get():
                output_name = f"{pdf_basename}_secured.pdf"
            elif self.add_watermark.get():
                output_name = f"{pdf_basename}_watermarked.pdf"
            else:
                output_name = f"{pdf_basename}_processed.pdf"
            
            self.output_name.set(output_name)
            self.status_var.set(f"Selected file: {os.path.basename(selected_file)}")
    
    def browse_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)
    
    def browse_watermark_image(self):
        selected_file = filedialog.askopenfilename(
            title="Select Watermark Image",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("All Files", "*.*")
            ]
        )
        if selected_file:
            self.watermark_image_path.set(selected_file)
    
    def start_process(self):
        # Validate inputs
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return
        
        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory.")
            return
        
        if not self.output_name.get():
            messagebox.showerror("Error", "Please enter a name for the output PDF file.")
            return
        
        # Validate watermark image if selected
        if self.add_watermark.get() and self.watermark_type.get() == "image":
            if not self.watermark_image_path.get() or not os.path.isfile(self.watermark_image_path.get()):
                messagebox.showerror("Error", "Please select a valid watermark image.")
                return
        
        # Validate passwords if encryption is enabled
        if self.use_encryption.get():
            if not self.owner_password.get() and not self.user_password.get():
                messagebox.showerror("Error", "Please enter at least one password for encryption.")
                return
        
        # Prepare output path
        output_filename = self.output_name.get()
        if not output_filename.lower().endswith('.pdf'):
            output_filename += ".pdf"
        
        output_path = os.path.join(self.output_dir.get(), output_filename)
        
        # Confirm if file exists
        if os.path.exists(output_path):
            result = messagebox.askyesno("Confirm", f"File {output_filename} already exists. Overwrite?")
            if not result:
                return
        
        # Disable controls during processing
        utils.set_controls_state(self.frame, tk.DISABLED)
        
        # Start processing in a separate thread
        self.process_canceled = False
        threading.Thread(target=self._processing_thread, args=(output_path,)).start()
    
    def _processing_thread(self, output_path):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Processing PDF..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
            # Load the PDF
            reader = PdfReader(self.pdf_path.get())
            writer = PdfWriter()
            
            # Copy all pages from input to output
            total_pages = len(reader.pages)
            
            # Process each page
            for i in range(total_pages):
                if self.process_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Processing canceled"))
                    return
                
                # Update progress - we allocate 80% of progress to page processing
                progress_pct = ((i + 1) / total_pages) * 80
                current_page = i + 1
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=current_page, t=total_pages: 
                    self.status_var.set(f"Processing page {p}/{t}..."))
                
                # Get the page
                page = reader.pages[i]
                
                # Add watermark if enabled
                if self.add_watermark.get():
                    page = self._add_watermark_to_page(page, i)
                
                # Add page to writer
                writer.add_page(page)
            
            # Apply security if enabled - this is the last 20% of progress
            if self.use_encryption.get():
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Applying security settings..."))
                self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(80))
                
                # Set up encryption parameters
                writer.encrypt(
                    user_password=self.user_password.get() if self.user_password.get() else None,
                    owner_password=self.owner_password.get() if self.owner_password.get() else None,
                    use_128bit=True
                )
                
                # Set permissions
                if not self.allow_printing.get():
                    writer.add_metadata({"/CanPrint": False})
                if not self.allow_copying.get():
                    writer.add_metadata({"/CanCopy": False})
                if not self.allow_modification.get():
                    writer.add_metadata({"/CanModify": False})
            
            # Save the output file
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Saving output file..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(90))
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Processing complete: {os.path.basename(output_path)}"))
            
            success_message = "PDF processed successfully.\n"
            if self.use_encryption.get():
                success_message += "Security settings applied.\n"
            if self.add_watermark.get():
                success_message += "Watermark added.\n"
            success_message += f"Saved to: {output_path}"
            
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", success_message))
            
        except Exception as e:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to process PDF: {str(e)}"))
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
    
    def _add_watermark_to_page(self, page, page_index):
        """Add watermark to a PDF page"""
        # Get page dimensions
        page_width = page.mediabox.width
        page_height = page.mediabox.height
        
        # Create watermark based on type
        if self.watermark_type.get() == "text":
            # Create a text watermark
            watermark = self._create_text_watermark(page_width, page_height)
        else:
            # Create an image watermark
            watermark = self._create_image_watermark(page_width, page_height)
        
        # Add watermark to page (using PyPDF2's merge_page)
        page.merge_page(watermark)
        return page
    
    def _create_text_watermark(self, width, height):
        """Create a text watermark PDF page"""
        # Create a blank PDF page
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from io import BytesIO
        
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        
        # Set watermark properties
        text = self.watermark_text.get()
        opacity = self.watermark_opacity.get() / 100
        rotation = self.watermark_rotation.get()
        
        # Calculate position based on selection
        position = self.watermark_position.get()
        if position == "center":
            x, y = width / 2, height / 2
        elif position == "top-left":
            x, y = width * 0.1, height * 0.9
        elif position == "top-right":
            x, y = width * 0.9, height * 0.9
        elif position == "bottom-left":
            x, y = width * 0.1, height * 0.1
        elif position == "bottom-right":
            x, y = width * 0.9, height * 0.1
        
        # Set text properties
        c.setFont("Helvetica", 72)
        c.setFillColorRGB(0, 0, 0, opacity)
        
        # Draw rotated text
        c.saveState()
        c.translate(x, y)
        c.rotate(rotation)
        c.drawCentredString(0, 0, text)
        c.restoreState()
        
        c.save()
        
        # Create PDF page from the canvas
        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        return watermark_pdf.pages[0]
    
    def _create_image_watermark(self, width, height):
        """Create an image watermark PDF page"""
        # Load and resize watermark image
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch
        from io import BytesIO
        
        packet = BytesIO()
        c = canvas.Canvas(packet, pagesize=(width, height))
        
        # Set watermark properties
        image_path = self.watermark_image_path.get()
        opacity = self.watermark_opacity.get() / 100
        rotation = self.watermark_rotation.get()
        
        # Load image
        img = Image.open(image_path)
        
        # Calculate image dimensions (resize to fit but maintain aspect ratio)
        img_width, img_height = img.size
        max_dimension = min(width, height) * 0.5  # Use 50% of page size
        
        ratio = min(max_dimension / img_width, max_dimension / img_height)
        new_width = img_width * ratio
        new_height = img_height * ratio
        
        # Calculate position based on selection
        position = self.watermark_position.get()
        if position == "center":
            x, y = width / 2 - new_width / 2, height / 2 - new_height / 2
        elif position == "top-left":
            x, y = width * 0.05, height * 0.95 - new_height
        elif position == "top-right":
            x, y = width * 0.95 - new_width, height * 0.95 - new_height
        elif position == "bottom-left":
            x, y = width * 0.05, height * 0.05
        elif position == "bottom-right":
            x, y = width * 0.95 - new_width, height * 0.05
        
        # Create temporary image for watermark
        temp_img_path = os.path.join(os.path.dirname(image_path), "temp_watermark.png")
        img.save(temp_img_path, format="PNG")
        
        # Draw rotated image
        c.saveState()
        c.translate(x + new_width/2, y + new_height/2)
        c.rotate(rotation)
        c.setFillAlpha(opacity)
        c.drawImage(temp_img_path, -new_width/2, -new_height/2, width=new_width, height=new_height)
        c.restoreState()
        
        c.save()
        
        # Delete temporary image
        try:
            os.remove(temp_img_path)
        except:
            pass
        
        # Create PDF page from the canvas
        packet.seek(0)
        watermark_pdf = PdfReader(packet)
        return watermark_pdf.pages[0]
    
    def cancel_process(self):
        self.process_canceled = True
        self.status_var.set("Canceling process...")
    
    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())
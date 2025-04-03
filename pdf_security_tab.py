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
        self.operation_mode = tk.StringVar(value="none")  # none, add_password, remove_password
        self.owner_password = tk.StringVar()
        self.user_password = tk.StringVar()
        self.current_password = tk.StringVar()  # For password removal
        
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
    
    @staticmethod
    def to_float(value):
        """Convert any numeric value to float, including Decimal types."""
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0
    
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
        
        # Security operation mode radio buttons
        ttk.Label(security_frame, text="Security Operation:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        modes_frame = ttk.Frame(security_frame)
        modes_frame.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Radiobutton(modes_frame, text="No Password Changes", variable=self.operation_mode, 
                      value="none", command=self.update_security_ui).pack(side="left", padx=5)
        ttk.Radiobutton(modes_frame, text="Add Password Protection", variable=self.operation_mode, 
                      value="add_password", command=self.update_security_ui).pack(side="left", padx=5)
        ttk.Radiobutton(modes_frame, text="Remove Password Protection", variable=self.operation_mode, 
                      value="remove_password", command=self.update_security_ui).pack(side="left", padx=5)
        
        # Container for password setting frames
        self.security_container = ttk.Frame(security_frame)
        self.security_container.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Create frames for different operations
        self.create_add_password_frame()
        self.create_remove_password_frame()
        
        # Initially hide all operation-specific frames
        self.update_security_ui()
    
    def create_add_password_frame(self):
        self.add_password_frame = ttk.Frame(self.security_container)
        
        # Password entry fields
        ttk.Label(self.add_password_frame, text="Owner Password:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.owner_pw_entry = ttk.Entry(self.add_password_frame, textvariable=self.owner_password, width=20, show="*")
        self.owner_pw_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.add_password_frame, text="User Password:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.user_pw_entry = ttk.Entry(self.add_password_frame, textvariable=self.user_password, width=20, show="*")
        self.user_pw_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Permissions frame
        permissions_frame = ttk.LabelFrame(self.add_password_frame, text="Permissions", padding=5)
        permissions_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Checkbutton(permissions_frame, text="Allow Printing", variable=self.allow_printing).grid(
            row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(permissions_frame, text="Allow Copying", variable=self.allow_copying).grid(
            row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Checkbutton(permissions_frame, text="Allow Modification", variable=self.allow_modification).grid(
            row=1, column=0, sticky="w", padx=5, pady=2)
    
    def create_remove_password_frame(self):
        self.remove_password_frame = ttk.Frame(self.security_container)
        
        ttk.Label(self.remove_password_frame, text="Current PDF Password:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.current_pw_entry = ttk.Entry(self.remove_password_frame, textvariable=self.current_password, width=20, show="*")
        self.current_pw_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.remove_password_frame, text="Leave blank if PDF has no password").grid(
            row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
    
    def update_security_ui(self):
        """Update the security UI based on the selected operation mode"""
        # Hide all frames first
        self.add_password_frame.grid_forget()
        self.remove_password_frame.grid_forget()
        
        # Show the appropriate frame based on the selected mode
        if self.operation_mode.get() == "add_password":
            self.add_password_frame.grid(row=0, column=0, sticky="ew")
        elif self.operation_mode.get() == "remove_password":
            self.remove_password_frame.grid(row=0, column=0, sticky="ew")
    
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
            output_name = f"{pdf_basename}_processed.pdf"
            
            if self.operation_mode.get() == "add_password":
                output_name = f"{pdf_basename}_secured.pdf"
            elif self.operation_mode.get() == "remove_password":
                output_name = f"{pdf_basename}_unlocked.pdf"
                
            if self.add_watermark.get():
                output_name = f"{pdf_basename}_watermarked.pdf"
                
            if self.operation_mode.get() != "none" and self.add_watermark.get():
                output_name = f"{pdf_basename}_secured_watermarked.pdf"
            
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
        
        # Validate password if adding password protection
        if self.operation_mode.get() == "add_password":
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
            
            # Handle based on operation mode
            if self.operation_mode.get() == "remove_password":
                self._remove_password(output_path)
            else:
                # For "none" or "add_password" modes
                self._process_pdf(output_path)
            
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
    
    def _remove_password(self, output_path):
        """Process for removing password protection"""
        self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Removing password protection..."))
        self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(20))
        
        # Try to open with provided password
        try:
            # Try with or without password based on what user provided
            password = self.current_password.get() if self.current_password.get() else None
            reader = PdfReader(self.pdf_path.get(), password=password)
            writer = PdfWriter()
            
            # Copy all pages from input to output
            total_pages = len(reader.pages)
            
            # Process each page
            for i in range(total_pages):
                if self.process_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Processing canceled"))
                    return
                
                # Update progress
                progress_pct = ((i + 1) / total_pages) * 80 + 20
                current_page = i + 1
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=current_page, t=total_pages: 
                    self.status_var.set(f"Processing page {p}/{t}..."))
                
                # Get the page and add it to the writer without any encryption
                page = reader.pages[i]
                
                # Add watermark if enabled
                if self.add_watermark.get():
                    page = self._add_watermark_to_page(page, i)
                
                writer.add_page(page)
            
            # Save the output file without any encryption
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Saving unprotected PDF..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(90))
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Password protection removed: {os.path.basename(output_path)}"))
            success_message = "Password protection removed.\n"
            if self.add_watermark.get():
                success_message += "Watermark added.\n"
            success_message += f"Saved to: {output_path}"
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", success_message))
                
        except Exception as e:
            error_msg = str(e)
            # Check if it's a password-related error
            if "password" in error_msg.lower() or "decrypt" in error_msg.lower():
                self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", 
                    "Failed to remove password protection: Incorrect password or no password provided."))
            else:
                self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", 
                    f"Failed to process PDF: {error_msg}"))
            raise  # Re-raise the exception to be caught by the outer try-except block
    
    def _process_pdf(self, output_path):
        """Process the PDF (add password and/or watermark)"""
        # Load the PDF
        try:
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
            
            # Apply security if requested
            if self.operation_mode.get() == "add_password":
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Applying security settings..."))
                self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(80))
                
                try:
                    # Get permission flags
                    permissions = 0
                    if self.allow_printing.get():
                        permissions |= 4  # Print document
                    if self.allow_copying.get():
                        permissions |= 16  # Copy content
                    if self.allow_modification.get():
                        permissions |= 8  # Modify contents
                    
                    # Try newer PyPDF2 API first
                    try:
                        writer.encrypt(
                            user_password=self.user_password.get() if self.user_password.get() else "",
                            owner_password=self.owner_password.get() if self.owner_password.get() else "",
                            use_128bit=True,
                            permissions_flag=permissions
                        )
                    except TypeError:
                        # Fall back to older PyPDF2 API
                        writer.encrypt(
                            user_pwd=self.user_password.get() if self.user_password.get() else "",
                            owner_pwd=self.owner_password.get() if self.owner_password.get() else "",
                            use_128bit=True
                        )
                except Exception as e:
                    self.frame.winfo_toplevel().after(0, lambda err=str(e): 
                        messagebox.showwarning("Warning", f"Failed to apply password protection: {err}"))
            
            # Save the output file
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Saving output file..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(90))
            
            with open(output_path, "wb") as output_file:
                writer.write(output_file)
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Processing complete: {os.path.basename(output_path)}"))
            
            success_message = "PDF processed successfully.\n"
            if self.operation_mode.get() == "add_password":
                success_message += "Security settings applied.\n"
            if self.add_watermark.get():
                success_message += "Watermark added.\n"
            success_message += f"Saved to: {output_path}"
            
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", success_message))
            
        except Exception as e:
            error_msg = str(e)
            raise Exception(f"Failed to process PDF: {error_msg}")
    
    def _add_watermark_to_page(self, page, page_index):
        """Add watermark to a PDF page"""
        # Get page dimensions
        page_width = PDFSecurityTab.to_float(page.mediabox.width)
        page_height = PDFSecurityTab.to_float(page.mediabox.height)
        
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
        # Convert to float to avoid decimal.Decimal issues
        width = PDFSecurityTab.to_float(width)
        height = PDFSecurityTab.to_float(height)
        
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
        # Convert to float to avoid decimal.Decimal issues
        width = PDFSecurityTab.to_float(width)
        height = PDFSecurityTab.to_float(height)
    
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
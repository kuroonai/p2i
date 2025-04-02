# image_batch_tab.py
import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import utils

class ImageBatchTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Variables
        self.images_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.operation = tk.StringVar(value="resize")  # resize, convert, adjust, optimize
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        
        # Resize options
        self.resize_mode = tk.StringVar(value="percentage")  # percentage, dimensions, max_dimension
        self.resize_percentage = tk.IntVar(value=50)
        self.resize_width = tk.IntVar(value=800)
        self.resize_height = tk.IntVar(value=600)
        self.resize_max_dimension = tk.IntVar(value=1024)
        self.maintain_aspect = tk.BooleanVar(value=True)
        
        # Convert options
        self.output_format = tk.StringVar(value="jpg")
        self.jpg_quality = tk.IntVar(value=85)
        self.png_compression = tk.IntVar(value=6)
        
        # Adjustment options
        self.brightness = tk.DoubleVar(value=1.0)
        self.contrast = tk.DoubleVar(value=1.0)
        self.sharpness = tk.DoubleVar(value=1.0)
        self.apply_filter = tk.BooleanVar(value=False)
        self.filter_type = tk.StringVar(value="BLUR")
        
        # Optimization options
        self.optimize_quality = tk.IntVar(value=80)
        self.strip_metadata = tk.BooleanVar(value=True)
        
        # File selection
        self.recursive_search = tk.BooleanVar(value=False)
        self.file_pattern = tk.StringVar(value="*.jpg,*.jpeg,*.png")
        
        # Preview
        self.preview_image = None
        self.selected_image_path = tk.StringVar()
        
        # Process canceled flag
        self.process_canceled = False
        
        # Create UI elements
        self.create_file_frame()
        self.create_operation_frame()
        self.create_preview_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame, 
            self.start_process, 
            self.cancel_process, 
            self.open_output_folder,
            "Process Images"
        )
        
        # Set default output directory
        default_output = os.path.join(str(Path.home()), "Pictures", "Processed")
        self.output_dir.set(default_output)
    
    def create_file_frame(self):
        file_frame = ttk.LabelFrame(self.frame, text="File Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Input directory
        ttk.Label(file_frame, text="Images Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.images_dir, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_input_dir).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Output directory
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        
        # File pattern and recursive search
        ttk.Label(file_frame, text="File Pattern:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.file_pattern, width=30).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        ttk.Checkbutton(file_frame, text="Include Subdirectories", variable=self.recursive_search).grid(
            row=2, column=2, sticky="w", padx=5, pady=5)
        
        # Make column 1 expand
        file_frame.columnconfigure(1, weight=1)
    
    def create_operation_frame(self):
        operation_frame = ttk.LabelFrame(self.frame, text="Batch Operation", padding=10)
        operation_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Operation type
        ttk.Label(operation_frame, text="Operation:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        operations = ttk.Combobox(operation_frame, textvariable=self.operation, 
                               values=["resize", "convert", "adjust", "optimize"])
        operations.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        operations.bind("<<ComboboxSelected>>", self.on_operation_change)
        
        # Create frames for each operation type
        self.create_resize_frame(operation_frame)
        self.create_convert_frame(operation_frame)
        self.create_adjust_frame(operation_frame)
        self.create_optimize_frame(operation_frame)
        
        # Show initial frame
        self.on_operation_change(None)
    
    def create_resize_frame(self, parent):
        self.resize_frame = ttk.Frame(parent)
        self.resize_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Resize mode
        ttk.Label(self.resize_frame, text="Resize Mode:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        modes = ttk.Combobox(self.resize_frame, textvariable=self.resize_mode, 
                          values=["percentage", "dimensions", "max_dimension"])
        modes.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        modes.bind("<<ComboboxSelected>>", self.on_resize_mode_change)
        
        # Percentage mode
        self.percentage_frame = ttk.Frame(self.resize_frame)
        self.percentage_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.percentage_frame, text="Resize to:").pack(side="left", padx=5)
        ttk.Scale(self.percentage_frame, from_=10, to=100, variable=self.resize_percentage, 
                orient="horizontal", length=200).pack(side="left", padx=5)
        ttk.Label(self.percentage_frame, textvariable=self.resize_percentage, 
                width=3).pack(side="left", padx=0)
        ttk.Label(self.percentage_frame, text="%").pack(side="left", padx=0)
        
        # Dimensions mode
        self.dimensions_frame = ttk.Frame(self.resize_frame)
        self.dimensions_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.dimensions_frame, text="Width:").pack(side="left", padx=5)
        ttk.Spinbox(self.dimensions_frame, from_=1, to=10000, textvariable=self.resize_width, 
                  width=6).pack(side="left", padx=5)
        ttk.Label(self.dimensions_frame, text="Height:").pack(side="left", padx=5)
        ttk.Spinbox(self.dimensions_frame, from_=1, to=10000, textvariable=self.resize_height, 
                  width=6).pack(side="left", padx=5)
        ttk.Checkbutton(self.dimensions_frame, text="Maintain Aspect Ratio", 
                      variable=self.maintain_aspect).pack(side="left", padx=5)
        
        # Max dimension mode
        self.max_dim_frame = ttk.Frame(self.resize_frame)
        self.max_dim_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.max_dim_frame, text="Maximum Dimension:").pack(side="left", padx=5)
        ttk.Spinbox(self.max_dim_frame, from_=1, to=10000, textvariable=self.resize_max_dimension, 
                  width=6).pack(side="left", padx=5)
        ttk.Label(self.max_dim_frame, text="pixels").pack(side="left", padx=5)
        
        # Initially show percentage frame
        self.on_resize_mode_change(None)
    
    def create_convert_frame(self, parent):
        self.convert_frame = ttk.Frame(parent)
        self.convert_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Format selection
        ttk.Label(self.convert_frame, text="Convert to:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        formats = ttk.Combobox(self.convert_frame, textvariable=self.output_format, 
                            values=["jpg", "png", "tiff", "bmp", "webp"])
        formats.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        formats.bind("<<ComboboxSelected>>", self.on_format_change)
        
        # JPEG quality
        self.jpg_frame = ttk.Frame(self.convert_frame)
        self.jpg_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.jpg_frame, text="JPEG Quality:").pack(side="left", padx=5)
        ttk.Scale(self.jpg_frame, from_=10, to=100, variable=self.jpg_quality, 
                orient="horizontal", length=200).pack(side="left", padx=5)
        ttk.Label(self.jpg_frame, textvariable=self.jpg_quality, width=3).pack(side="left", padx=0)
        
        # PNG compression
        self.png_frame = ttk.Frame(self.convert_frame)
        self.png_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        ttk.Label(self.png_frame, text="PNG Compression:").pack(side="left", padx=5)
        ttk.Scale(self.png_frame, from_=0, to=9, variable=self.png_compression, 
                orient="horizontal", length=200).pack(side="left", padx=5)
        ttk.Label(self.png_frame, textvariable=self.png_compression, width=1).pack(side="left", padx=0)
        ttk.Label(self.png_frame, text="(0=none, 9=max)").pack(side="left", padx=5)
        
        # Initially configure format options
        self.on_format_change(None)
    
    def create_adjust_frame(self, parent):
        self.adjust_frame = ttk.Frame(parent)
        self.adjust_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Brightness
        ttk.Label(self.adjust_frame, text="Brightness:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        brightness_scale = ttk.Scale(self.adjust_frame, from_=0.1, to=2.0, variable=self.brightness, 
                                   orient="horizontal", length=200)
        brightness_scale.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        def format_brightness(*args):
            return f"{self.brightness.get():.1f}"
        
        self.brightness_label = ttk.Label(self.adjust_frame, text=format_brightness())
        self.brightness_label.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Update label when slider changes
        def update_brightness(*args):
            self.brightness_label.configure(text=format_brightness())
        
        self.brightness.trace_add("write", update_brightness)
        
        # Contrast
        ttk.Label(self.adjust_frame, text="Contrast:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        contrast_scale = ttk.Scale(self.adjust_frame, from_=0.1, to=2.0, variable=self.contrast, 
                                 orient="horizontal", length=200)
        contrast_scale.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        def format_contrast(*args):
            return f"{self.contrast.get():.1f}"
        
        self.contrast_label = ttk.Label(self.adjust_frame, text=format_contrast())
        self.contrast_label.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        
        # Update label when slider changes
        def update_contrast(*args):
            self.contrast_label.configure(text=format_contrast())
        
        self.contrast.trace_add("write", update_contrast)
        
        # Sharpness
        ttk.Label(self.adjust_frame, text="Sharpness:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        sharpness_scale = ttk.Scale(self.adjust_frame, from_=0.1, to=2.0, variable=self.sharpness, 
                                  orient="horizontal", length=200)
        sharpness_scale.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        def format_sharpness(*args):
            return f"{self.sharpness.get():.1f}"
        
        self.sharpness_label = ttk.Label(self.adjust_frame, text=format_sharpness())
        self.sharpness_label.grid(row=2, column=2, sticky="w", padx=5, pady=5)
        
        # Update label when slider changes
        def update_sharpness(*args):
            self.sharpness_label.configure(text=format_sharpness())
        
        self.sharpness.trace_add("write", update_sharpness)
        
        # Filter options
        ttk.Checkbutton(self.adjust_frame, text="Apply Filter", 
                      variable=self.apply_filter).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        
        filter_combo = ttk.Combobox(self.adjust_frame, textvariable=self.filter_type, 
                                  values=["BLUR", "SHARPEN", "CONTOUR", "DETAIL", "EDGE_ENHANCE", "SMOOTH"])
        filter_combo.grid(row=3, column=1, sticky="w", padx=5, pady=5)
    
    def create_optimize_frame(self, parent):
        self.optimize_frame = ttk.Frame(parent)
        self.optimize_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Quality setting
        ttk.Label(self.optimize_frame, text="Output Quality:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Scale(self.optimize_frame, from_=10, to=100, variable=self.optimize_quality, 
                orient="horizontal", length=200).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        ttk.Label(self.optimize_frame, textvariable=self.optimize_quality, 
                width=3).grid(row=0, column=2, sticky="w", padx=0, pady=5)
        ttk.Label(self.optimize_frame, text="%").grid(row=0, column=3, sticky="w", padx=0, pady=5)
        
        # Strip metadata
        ttk.Checkbutton(self.optimize_frame, text="Strip Image Metadata", 
                      variable=self.strip_metadata).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Explanation
        explanation = """Image optimization reduces file size while maintaining acceptable visual quality.
This is useful for web images, email attachments, or saving disk space.
Stripping metadata removes information like camera details and GPS coordinates."""
        
        explanation_label = ttk.Label(self.optimize_frame, text=explanation, wraplength=500, justify="left")
        explanation_label.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=5)
    
    def create_preview_frame(self):
        preview_frame = ttk.LabelFrame(self.frame, text="Preview", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Preview canvas
        self.canvas = tk.Canvas(preview_frame, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Select Image for Preview", 
                 command=self.select_preview_image).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Preview Processing", 
                 command=self.preview_processing).pack(side="left", padx=5)
        
        self.preview_label = ttk.Label(controls_frame, text="No image selected")
        self.preview_label.pack(side="left", padx=5)
    
    def on_operation_change(self, event):
        """Show/hide operation-specific frames based on selected operation"""
        operation = self.operation.get()
        
        self.resize_frame.grid_remove()
        self.convert_frame.grid_remove()
        self.adjust_frame.grid_remove()
        self.optimize_frame.grid_remove()
        
        if operation == "resize":
            self.resize_frame.grid()
        elif operation == "convert":
            self.convert_frame.grid()
        elif operation == "adjust":
            self.adjust_frame.grid()
        elif operation == "optimize":
            self.optimize_frame.grid()
    
    def on_resize_mode_change(self, event):
        """Show/hide resize mode specific frames"""
        mode = self.resize_mode.get()
        
        self.percentage_frame.grid_remove()
        self.dimensions_frame.grid_remove()
        self.max_dim_frame.grid_remove()
        
        if mode == "percentage":
            self.percentage_frame.grid()
        elif mode == "dimensions":
            self.dimensions_frame.grid()
        elif mode == "max_dimension":
            self.max_dim_frame.grid()
    
    def on_format_change(self, event):
        """Show/hide format-specific options"""
        format = self.output_format.get()
        
        self.jpg_frame.grid_remove()
        self.png_frame.grid_remove()
        
        if format == "jpg" or format == "jpeg":
            self.jpg_frame.grid()
        elif format == "png":
            self.png_frame.grid()
    
    def browse_input_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Directory Containing Images",
            initialdir=self.images_dir.get() if self.images_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.images_dir.set(selected_dir)
            self.status_var.set(f"Selected input directory: {selected_dir}")
    
    def browse_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)
    
    def select_preview_image(self):
        if not self.images_dir.get() or not os.path.isdir(self.images_dir.get()):
            messagebox.showerror("Error", "Please select a valid input directory first.")
            return
        
        # Get image file extensions from pattern
        patterns = self.file_pattern.get().split(',')
        extensions = []
        for pattern in patterns:
            if pattern.startswith('*.'):
                extensions.append(pattern[1:])  # Remove the *
        
        if not extensions:
            extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        # Create filetypes for dialog
        filetypes = [("Image Files", ' '.join(extensions))]
        for ext in extensions:
            desc = ext.upper()[1:] + " Files"  # Convert .jpg to JPG Files
            filetypes.append((desc, f"*{ext}"))
        filetypes.append(("All Files", "*.*"))
        
        selected_file = filedialog.askopenfilename(
            title="Select Image for Preview",
            initialdir=self.images_dir.get(),
            filetypes=filetypes
        )
        
        if selected_file:
            self.selected_image_path.set(selected_file)
            self.preview_label.config(text=os.path.basename(selected_file))
            
            # Load and display the image
            self.show_preview_image(selected_file)
    
    def show_preview_image(self, image_path):
        """Load and display an image in the preview canvas"""
        try:
            # Open the image
            img = Image.open(image_path)
            
            # Display in canvas
            self._display_preview(img)
            self.status_var.set(f"Preview image loaded: {os.path.basename(image_path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def _display_preview(self, img):
        """Display image in canvas with proper scaling"""
        # Calculate the ratio to fit the image within the canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # If canvas hasn't been realized yet, use a default size
        if canvas_width <= 1:
            canvas_width = 600
        if canvas_height <= 1:
            canvas_height = 400
        
        img_width, img_height = img.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        
        # Resize the image
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Save reference to prevent garbage collection
        self.preview_image = photo
        
        # Update canvas
        self.canvas.delete("all")
        
        # Calculate center position
        x_pos = (canvas_width - new_width) // 2
        y_pos = (canvas_height - new_height) // 2
        
        # Create image on canvas
        self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=photo)
    
    def preview_processing(self):
        """Process the selected preview image with current settings and display result"""
        if not self.selected_image_path.get() or not os.path.isfile(self.selected_image_path.get()):
            messagebox.showinfo("Info", "Please select an image for preview first.")
            return
        
        try:
            # Load original image
            img = Image.open(self.selected_image_path.get())
            original_format = img.format
            
            # Process image based on selected operation
            operation = self.operation.get()
            
            if operation == "resize":
                img = self._resize_image(img)
            elif operation == "convert":
                # For convert, we just change the save format later
                pass
            elif operation == "adjust":
                img = self._adjust_image(img)
            elif operation == "optimize":
                # For optimize, mostly affects save options
                pass
            
            # Display the processed image
            self._display_preview(img)
            self.status_var.set("Preview of processed image")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process image: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def _resize_image(self, img):
        """Resize an image based on current settings"""
        width, height = img.size
        mode = self.resize_mode.get()
        
        if mode == "percentage":
            percentage = self.resize_percentage.get() / 100
            new_width = int(width * percentage)
            new_height = int(height * percentage)
            
        elif mode == "dimensions":
            new_width = self.resize_width.get()
            new_height = self.resize_height.get()
            
            if self.maintain_aspect.get():
                # Calculate aspect ratio
                aspect = width / height
                
                # Adjust dimensions to maintain aspect ratio
                if new_width / new_height > aspect:
                    new_width = int(new_height * aspect)
                else:
                    new_height = int(new_width / aspect)
                    
        elif mode == "max_dimension":
            max_dim = self.resize_max_dimension.get()
            
            if width > height:
                new_width = max_dim
                new_height = int(height * (max_dim / width))
            else:
                new_height = max_dim
                new_width = int(width * (max_dim / height))
        
        # Perform resize
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def _adjust_image(self, img):
        """Apply image adjustments based on current settings"""
        # Apply brightness adjustment
        if self.brightness.get() != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(self.brightness.get())
        
        # Apply contrast adjustment
        if self.contrast.get() != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(self.contrast.get())
        
        # Apply sharpness adjustment
        if self.sharpness.get() != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(self.sharpness.get())
        
        # Apply filter if enabled
        if self.apply_filter.get():
            filter_type = self.filter_type.get()
            
            if filter_type == "BLUR":
                img = img.filter(ImageFilter.BLUR)
            elif filter_type == "SHARPEN":
                img = img.filter(ImageFilter.SHARPEN)
            elif filter_type == "CONTOUR":
                img = img.filter(ImageFilter.CONTOUR)
            elif filter_type == "DETAIL":
                img = img.filter(ImageFilter.DETAIL)
            elif filter_type == "EDGE_ENHANCE":
                img = img.filter(ImageFilter.EDGE_ENHANCE)
            elif filter_type == "SMOOTH":
                img = img.filter(ImageFilter.SMOOTH)
        
        return img
    
    def start_process(self):
        # Validate inputs
        if not self.images_dir.get() or not os.path.isdir(self.images_dir.get()):
            messagebox.showerror("Error", "Please select a valid input directory.")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please specify an output directory.")
            return
        
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir.get()):
            try:
                os.makedirs(self.output_dir.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
                return
        
        # Disable controls during processing
        utils.set_controls_state(self.frame, tk.DISABLED)
        
        # Start processing in a separate thread
        self.process_canceled = False
        threading.Thread(target=self._processing_thread).start()
    
    def _processing_thread(self):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Finding images..."))
            
            # Find all matching image files
            image_files = self._find_image_files()
            
            if not image_files:
                self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Info", "No matching image files found."))
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("No matching files found"))
                return
            
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Found {len(image_files)} images to process"))
            
            # Process each image
            operation = self.operation.get()
            total_files = len(image_files)
            
            for i, img_path in enumerate(image_files):
                if self.process_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Processing canceled"))
                    return
                
                # Update progress
                progress_pct = ((i + 1) / total_files) * 100
                current_file = os.path.basename(img_path)
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda f=current_file, p=i+1, t=total_files: 
                    self.status_var.set(f"Processing {p}/{t}: {f}"))
                
                try:
                    # Process image based on operation
                    if operation == "resize":
                        self._process_resize(img_path)
                    elif operation == "convert":
                        self._process_convert(img_path)
                    elif operation == "adjust":
                        self._process_adjust(img_path)
                    elif operation == "optimize":
                        self._process_optimize(img_path)
                except Exception as e:
                    self.frame.winfo_toplevel().after(0, lambda f=current_file, err=str(e): 
                        messagebox.showwarning("Warning", f"Failed to process {f}: {err}"))
                    continue
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Batch processing complete"))
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", 
                f"Batch processing complete.\n{total_files} images processed.\nOutput saved to: {self.output_dir.get()}"))
            
        except Exception as e:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Batch processing failed: {str(e)}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        finally:
            # Re-enable controls
            self.frame.winfo_toplevel().after(0, lambda: utils.set_controls_state(self.frame, tk.NORMAL))
    
    def _find_image_files(self):
        """Find all matching image files in the input directory"""
        import fnmatch
        
        patterns = self.file_pattern.get().split(',')
        image_files = []
        
        if self.recursive_search.get():
            for root, dirs, files in os.walk(self.images_dir.get()):
                for pattern in patterns:
                    for filename in fnmatch.filter(files, pattern.strip()):
                        image_files.append(os.path.join(root, filename))
        else:
            for pattern in patterns:
                matches = fnmatch.filter(os.listdir(self.images_dir.get()), pattern.strip())
                for match in matches:
                    image_files.append(os.path.join(self.images_dir.get(), match))
        
        # Return only files that actually exist and are readable
        return [f for f in image_files if os.path.isfile(f) and os.access(f, os.R_OK)]
    
    def _process_resize(self, img_path):
        """Process a single image for resizing"""
        # Open image
        img = Image.open(img_path)
        
        # Resize image
        resized_img = self._resize_image(img)
        
        # Create output filename
        filename = os.path.basename(img_path)
        output_path = os.path.join(self.output_dir.get(), f"resized_{filename}")
        
        # Save processed image
        resized_img.save(output_path, quality=95)
    
    def _process_convert(self, img_path):
        """Process a single image for format conversion"""
        # Open image
        img = Image.open(img_path)
        
        # Get file basename without extension
        basename = os.path.splitext(os.path.basename(img_path))[0]
        
        # Get target format and options
        format = self.output_format.get().upper()
        if format == "JPG":
            format = "JPEG"  # PIL uses JPEG, not JPG
        
        # Create output filename with new extension
        output_path = os.path.join(self.output_dir.get(), f"{basename}.{self.output_format.get().lower()}")
        
        # Save with format-specific options
        if format == "JPEG":
            img.save(output_path, format=format, quality=self.jpg_quality.get())
        elif format == "PNG":
            img.save(output_path, format=format, compress_level=self.png_compression.get())
        else:
            img.save(output_path, format=format)
    
    def _process_adjust(self, img_path):
        """Process a single image for adjustments"""
        # Open image
        img = Image.open(img_path)
        
        # Apply adjustments
        adjusted_img = self._adjust_image(img)
        
        # Create output filename
        filename = os.path.basename(img_path)
        output_path = os.path.join(self.output_dir.get(), f"adjusted_{filename}")
        
        # Save processed image
        adjusted_img.save(output_path, quality=95)
    
    def _process_optimize(self, img_path):
        """Process a single image for optimization"""
        # Open image
        img = Image.open(img_path)
        original_format = img.format
        
        # Create output filename
        filename = os.path.basename(img_path)
        output_path = os.path.join(self.output_dir.get(), f"optimized_{filename}")
        
        # Optimize settings
        save_opts = {
            'optimize': True,
            'quality': self.optimize_quality.get()
        }
        
        # Strip metadata if requested
        if self.strip_metadata.get():
            # Create a new image without metadata
            new_img = Image.new(img.mode, img.size)
            new_img.paste(img)
            img = new_img
        
        # Save optimized image
        if original_format == 'PNG':
            save_opts['compress_level'] = 9  # Maximum compression for PNG
            del save_opts['quality']  # Not used for PNG
        
        img.save(output_path, format=original_format, **save_opts)
    
    def cancel_process(self):
        self.process_canceled = True
        self.status_var.set("Canceling batch processing...")
    
    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())
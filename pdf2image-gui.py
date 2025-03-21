#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF and Image Converter GUI
- PDF to Image conversion
- Image to PDF conversion
Based on original work by Naveen Kumar Vasudevan and the package pdf2image
Enhanced with GUI and additional features
"""

import os
import sys
import threading
import multiprocessing
from pathlib import Path
from pdf2image import convert_from_path
from tqdm import tqdm
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from PIL import Image as PILImage

class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF & Image Converter")
        self.root.iconbitmap("p2i.ico")
        
        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window dimensions
        window_width = int(screen_width * 0.8)  # 80% of screen width
        window_height = int(screen_height * 0.8)  # 80% of screen height
        
        # Calculate position to center window
        position_top = int((screen_height - window_height)/2)
        position_left = int((screen_width - window_width)/2)
        
        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")        
        self.root.configure(bg="#f0f0f0")
        
        # Create tab control
        self.tab_control = ttk.Notebook(self.root)
        
        # PDF to Image tab
        self.pdf_to_image_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.pdf_to_image_tab, text="PDF to Image")
        
        # Image to PDF tab
        self.image_to_pdf_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.image_to_pdf_tab, text="Image to PDF")
        
        self.tab_control.pack(expand=1, fill="both")
        
        # Setup PDF to Image tab
        self.setup_pdf_to_image_tab()
        
        # Setup Image to PDF tab
        self.setup_image_to_pdf_tab()
    
    def setup_pdf_to_image_tab(self):
        # PDF to Image Variables
        self.pdf_path = tk.StringVar()
        self.pdf_output_dir = tk.StringVar()
        self.start_page = tk.IntVar(value=1)
        self.end_page = tk.IntVar(value=1)
        self.dpi = tk.IntVar(value=300)
        self.format = tk.StringVar(value="jpg")
        self.batch_mode = tk.BooleanVar(value=False)
        self.n_cpu = multiprocessing.cpu_count()
        self.threads = tk.IntVar(value=self.n_cpu)
        self.total_pages = 0
        self.preview_image = None
        self.progress = None
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        
        # Create UI elements
        self.create_file_frame(self.pdf_to_image_tab, "pdf")
        self.create_options_frame(self.pdf_to_image_tab)
        self.create_preview_frame(self.pdf_to_image_tab)
        self.create_progress_frame(self.pdf_to_image_tab, "pdf")
        self.create_buttons_frame(self.pdf_to_image_tab, "pdf")
        
        # Set default output directory to user's Pictures folder
        default_output = os.path.join(str(Path.home()), "Pictures")
        self.pdf_output_dir.set(default_output)
    
    def setup_image_to_pdf_tab(self):
        # Image to PDF Variables
        self.images_paths = []
        self.img_output_dir = tk.StringVar()
        self.pdf_name = tk.StringVar(value="output.pdf")
        self.page_size = tk.StringVar(value="A4")
        self.orientation = tk.StringVar(value="portrait")
        self.margin = tk.IntVar(value=10)
        self.img_quality = tk.IntVar(value=90)
        self.img_preview_image = None
        self.img_progress_var = tk.DoubleVar(value=0.0)
        self.img_status_var = tk.StringVar(value="Ready")
        self.selected_image_index = 0
        
        # Create UI elements for Image to PDF
        self.create_img_file_frame()
        self.create_img_options_frame()
        self.create_img_preview_frame()
        self.create_progress_frame(self.image_to_pdf_tab, "img")
        self.create_buttons_frame(self.image_to_pdf_tab, "img")
        
        # Set default output directory to user's Documents folder
        default_output = os.path.join(str(Path.home()), "Documents")
        self.img_output_dir.set(default_output)
    
    def create_file_frame(self, parent, mode):
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # PDF File selection
        ttk.Label(file_frame, text="PDF File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_pdf).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Output directory selection
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        
        # Batch mode checkbox
        ttk.Checkbutton(
            file_frame, 
            text="Batch Mode (Convert all PDFs in a folder)", 
            variable=self.batch_mode,
            command=self.toggle_batch_mode
        ).grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        # Make column 1 expand
        file_frame.columnconfigure(1, weight=1)
    
    def create_img_file_frame(self):
        file_frame = ttk.LabelFrame(self.image_to_pdf_tab, text="Image Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add Images", command=self.add_images).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected_image).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_images).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Move Up", command=self.move_image_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Move Down", command=self.move_image_down).pack(side="left", padx=5)
        
        # List of images
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox with images
        self.img_listbox = tk.Listbox(list_frame, height=6, width=60, yscrollcommand=scrollbar.set)
        self.img_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.img_listbox.yview)
        
        # Bind selection event
        self.img_listbox.bind('<<ListboxSelect>>', self.on_image_select)
        
        # Output settings
        ttk.Label(file_frame, text="Output Directory:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.img_output_dir, width=50).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_img_output_dir).grid(row=2, column=2, sticky="e", padx=5, pady=5)
        
        ttk.Label(file_frame, text="PDF Filename:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_name, width=50).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Make rows and columns expand
        file_frame.rowconfigure(1, weight=1)
        file_frame.columnconfigure(1, weight=1)
    
    def create_options_frame(self, parent):
        options_frame = ttk.LabelFrame(parent, text="Conversion Options", padding=10)
        options_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Page range
        ttk.Label(options_frame, text="Start Page:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(options_frame, from_=1, to=9999, textvariable=self.start_page, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(options_frame, text="End Page:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ttk.Spinbox(options_frame, from_=1, to=9999, textvariable=self.end_page, width=10).grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Button(options_frame, text="Get Page Count", command=self.get_page_count).grid(row=0, column=4, sticky="w", padx=5, pady=5)
        
        # DPI selection
        ttk.Label(options_frame, text="DPI:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(options_frame, from_=72, to=600, textvariable=self.dpi, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Format selection
        ttk.Label(options_frame, text="Format:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        format_combo = ttk.Combobox(options_frame, textvariable=self.format, values=["jpg", "png", "tiff", "bmp"], width=8)
        format_combo.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        # Thread selection
        ttk.Label(options_frame, text="Threads:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(options_frame, from_=1, to=self.n_cpu, textvariable=self.threads, width=10).grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Maximum compression quality slider
        ttk.Label(options_frame, text="Quality:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.quality = tk.IntVar(value=90)
        quality_scale = ttk.Scale(options_frame, from_=10, to=100, variable=self.quality, orient="horizontal")
        quality_scale.grid(row=2, column=3, sticky="ew", padx=5, pady=5)
        ttk.Label(options_frame, textvariable=tk.StringVar(value=self.quality)).grid(row=2, column=4, sticky="w", padx=5, pady=5)
        
        # Update the quality label when the slider changes
        def update_quality_label(*args):
            quality_scale.master.children["!label5"].configure(text=f"{self.quality.get()}%")
        
        self.quality.trace_add("write", update_quality_label)
        update_quality_label()
    
    def create_img_options_frame(self):
        options_frame = ttk.LabelFrame(self.image_to_pdf_tab, text="PDF Options", padding=10)
        options_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Page size
        ttk.Label(options_frame, text="Page Size:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        size_combo = ttk.Combobox(options_frame, textvariable=self.page_size, 
                                 values=["A4", "Letter", "Legal", "Tabloid", "A3", "A5"], width=10)
        size_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # Orientation
        ttk.Label(options_frame, text="Orientation:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        orientation_combo = ttk.Combobox(options_frame, textvariable=self.orientation, 
                                        values=["portrait", "landscape"], width=10)
        orientation_combo.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        # Margin
        ttk.Label(options_frame, text="Margin (mm):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Spinbox(options_frame, from_=0, to=50, textvariable=self.margin, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        # Image quality in PDF
        ttk.Label(options_frame, text="Image Quality:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        quality_scale = ttk.Scale(options_frame, from_=10, to=100, variable=self.img_quality, orient="horizontal")
        quality_scale.grid(row=1, column=3, sticky="ew", padx=5, pady=5)
        
        quality_label = ttk.Label(options_frame, text=f"{self.img_quality.get()}%")
        quality_label.grid(row=1, column=4, sticky="w", padx=5, pady=5)
        
        # Update the quality label when the slider changes
        def update_img_quality_label(*args):
            quality_label.configure(text=f"{self.img_quality.get()}%")
        
        self.img_quality.trace_add("write", update_img_quality_label)
    
    def create_preview_frame(self, parent):
        preview_frame = ttk.LabelFrame(parent, text="Preview", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Preview canvas
        self.canvas = tk.Canvas(preview_frame, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Preview Page", command=self.preview_page).pack(side="left", padx=5)
        ttk.Label(controls_frame, text="Page:").pack(side="left", padx=5)
        self.preview_page_var = tk.IntVar(value=1)
        ttk.Spinbox(controls_frame, from_=1, to=1, textvariable=self.preview_page_var, width=10).pack(side="left", padx=5)
    
    def create_img_preview_frame(self):
        preview_frame = ttk.LabelFrame(self.image_to_pdf_tab, text="Preview", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Preview canvas
        self.img_canvas = tk.Canvas(preview_frame, bg="#ffffff", highlightthickness=0)
        self.img_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Preview Selected Image", command=self.preview_selected_image).pack(side="left", padx=5)
        ttk.Label(controls_frame, text="Image:").pack(side="left", padx=5)
        
        self.selected_image_label = ttk.Label(controls_frame, text="None selected")
        self.selected_image_label.pack(side="left", padx=5)
    
    def create_progress_frame(self, parent, mode):
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=10)
        progress_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Progress bar
        if mode == "pdf":
            self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
            self.progress.pack(fill="x", expand=True, padx=5, pady=5)
            
            # Status label
            ttk.Label(progress_frame, textvariable=self.status_var).pack(fill="x", expand=True, padx=5, pady=5)
        else:
            self.img_progress = ttk.Progressbar(progress_frame, variable=self.img_progress_var, maximum=100)
            self.img_progress.pack(fill="x", expand=True, padx=5, pady=5)
            
            # Status label
            ttk.Label(progress_frame, textvariable=self.img_status_var).pack(fill="x", expand=True, padx=5, pady=5)
    
    def create_buttons_frame(self, parent, mode):
        buttons_frame = ttk.Frame(parent, padding=10)
        buttons_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        if mode == "pdf":
            ttk.Button(buttons_frame, text="Convert PDF to Images", command=self.start_pdf_conversion).pack(side="left", padx=5)
            ttk.Button(buttons_frame, text="Cancel", command=self.cancel_conversion).pack(side="left", padx=5)
            ttk.Button(buttons_frame, text="Open Output Folder", command=lambda: self.open_output_folder(mode)).pack(side="left", padx=5)
        else:
            ttk.Button(buttons_frame, text="Create PDF from Images", command=self.start_img_conversion).pack(side="left", padx=5)
            ttk.Button(buttons_frame, text="Cancel", command=self.cancel_img_conversion).pack(side="left", padx=5)
            ttk.Button(buttons_frame, text="Open Output Folder", command=lambda: self.open_output_folder(mode)).pack(side="left", padx=5)
        
        ttk.Button(buttons_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)
    
    # PDF to Image methods
    
    def browse_pdf(self):
        if self.batch_mode.get():
            selected_dir = filedialog.askdirectory(
                title="Select Folder Containing PDFs",
                initialdir=os.path.dirname(self.pdf_path.get()) if self.pdf_path.get() else os.getcwd()
            )
            if selected_dir:
                self.pdf_path.set(selected_dir)
                self.status_var.set(f"Selected folder: {selected_dir}")
        else:
            selected_file = filedialog.askopenfilename(
                title="Select PDF File",
                filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
                initialdir=os.path.dirname(self.pdf_path.get()) if self.pdf_path.get() else os.getcwd()
            )
            if selected_file:
                self.pdf_path.set(selected_file)
                self.status_var.set(f"Selected file: {os.path.basename(selected_file)}")
                self.get_page_count()
    
    def browse_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.pdf_output_dir.get() if self.pdf_output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.pdf_output_dir.set(selected_dir)
    
    def toggle_batch_mode(self):
        if self.batch_mode.get():
            # Switch to folder selection mode
            if self.pdf_path.get() and os.path.isfile(self.pdf_path.get()):
                # If a file was selected, change to its parent directory
                self.pdf_path.set(os.path.dirname(self.pdf_path.get()))
        else:
            # Switch to file selection mode
            if self.pdf_path.get() and os.path.isdir(self.pdf_path.get()):
                # If a directory was selected, clear the path
                self.pdf_path.set("")
    
    def get_page_count(self):
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            messagebox.showerror("Error", "Please select a valid PDF file first.")
            return
            
        try:
            # Use first page only to get total count (more efficient)
            self.status_var.set("Counting pages...")
            # Put this in a thread to avoid freezing the UI
            threading.Thread(target=self._get_page_count_thread).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get page count: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def _get_page_count_thread(self):
        try:
            # Import here to avoid circular import
            from pdf2image.pdf2image import pdfinfo_from_path
            
            info = pdfinfo_from_path(self.pdf_path.get())
            self.total_pages = info["Pages"]
            
            # Update UI in the main thread
            self.root.after(0, self._update_page_count_ui)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get page count: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def _update_page_count_ui(self):
        self.end_page.set(self.total_pages)
        # Update the preview page spinbox's range
        for child in self.pdf_to_image_tab.winfo_children():
            if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Preview":
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Frame):
                        for widget in subchild.winfo_children():
                            if isinstance(widget, ttk.Spinbox):
                                widget.config(to=self.total_pages)
                                break
        
        self.status_var.set(f"PDF has {self.total_pages} pages")
    
    def preview_page(self):
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            messagebox.showerror("Error", "Please select a valid PDF file first.")
            return
            
        page_num = self.preview_page_var.get()
        
        try:
            self.status_var.set(f"Generating preview for page {page_num}...")
            # Use a thread to prevent UI freezing
            threading.Thread(target=self._preview_page_thread, args=(page_num,)).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate preview: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def _preview_page_thread(self, page_num):
        try:
            # Convert the page
            images = convert_from_path(
                self.pdf_path.get(), 
                dpi=self.dpi.get(), 
                first_page=page_num, 
                last_page=page_num
            )
            
            if images:
                # Get the image and resize it to fit the canvas
                img = images[0]
                self.display_preview(img, "pdf")
            else:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "No pages were converted."))
                
            self.root.after(0, lambda: self.status_var.set("Preview generated"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate preview: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def display_preview(self, img, mode):
        # Calculate the ratio to fit the image within the canvas
        if mode == "pdf":
            canvas = self.canvas
        else:
            canvas = self.img_canvas
            
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
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
        img = img.resize((new_width, new_height), PILImage.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Save reference to prevent garbage collection
        if mode == "pdf":
            self.preview_image = photo
            # Update the canvas in the main thread
            self.root.after(0, lambda: self._update_canvas(photo, new_width, new_height, "pdf"))
        else:
            self.img_preview_image = photo
            # Update the canvas in the main thread
            self.root.after(0, lambda: self._update_canvas(photo, new_width, new_height, "img"))
    
    def _update_canvas(self, photo, width, height, mode):
        # Clear previous content
        if mode == "pdf":
            canvas = self.canvas
        else:
            canvas = self.img_canvas
            
        canvas.delete("all")
        
        # Calculate center position
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        x_pos = (canvas_width - width) // 2
        y_pos = (canvas_height - height) // 2
        
        # Create image on canvas
        canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=photo)
    
    def start_pdf_conversion(self):
        if self.batch_mode.get():
            if not self.pdf_path.get() or not os.path.isdir(self.pdf_path.get()):
                messagebox.showerror("Error", "Please select a valid folder containing PDFs.")
                return
        else:
            if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
                messagebox.showerror("Error", "Please select a valid PDF file.")
                return
        
        if not self.pdf_output_dir.get() or not os.path.isdir(self.pdf_output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory.")
            return
        
        # Validate page range
        if self.start_page.get() < 1:
            messagebox.showerror("Error", "Start page must be at least 1.")
            return
            
        if self.end_page.get() < self.start_page.get():
            messagebox.showerror("Error", "End page cannot be less than start page.")
            return
        
        # Disable controls during conversion
        self._set_controls_state(tk.DISABLED, "pdf")
        
        # Start conversion in a separate thread
        self.conversion_canceled = False
        threading.Thread(target=self._conversion_thread).start()
    
    def _conversion_thread(self):
        try:
            if self.batch_mode.get():
                self._batch_convert()
            else:
                self._single_convert()
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Conversion failed: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
        finally:
            # Re-enable controls
            self.root.after(0, lambda: self._set_controls_state(tk.NORMAL, "pdf"))
    
    def _single_convert(self):
        self.root.after(0, lambda: self.status_var.set("Converting PDF to images..."))
        
        # Create folder with same name as PDF if it doesn't exist
        pdf_basename = os.path.splitext(os.path.basename(self.pdf_path.get()))[0]
        output_folder = os.path.join(self.pdf_output_dir.get(), pdf_basename)
        
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        # Convert the pages
        try:
            total_pages = self.end_page.get() - self.start_page.get() + 1
            
            # Update progress in main thread
            for i in range(total_pages):
                if self.conversion_canceled:
                    self.root.after(0, lambda: self.status_var.set("Conversion canceled"))
                    return
                
                # Calculate current page
                current_page = self.start_page.get() + i
                
                # Update progress
                progress_pct = (i / total_pages) * 100
                self.root.after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.root.after(0, lambda p=current_page: self.status_var.set(f"Converting page {p}..."))
                
                # Convert single page
                images = convert_from_path(
                    self.pdf_path.get(),
                    dpi=self.dpi.get(),
                    first_page=current_page,
                    last_page=current_page
                )
                
                if images:
                    # Save the image
                    img = images[0]
                    if current_page == self.start_page.get() and total_pages == 1:
                        # If only one page, don't add page number
                        output_filename = f"{pdf_basename}.{self.format.get()}"
                    else:
                        # Add page number for multiple pages
                        output_filename = f"{pdf_basename}_{current_page}.{self.format.get()}"
                    
                    output_path = os.path.join(output_folder, output_filename)
                    
                    # Save with quality setting if JPEG
                    if self.format.get().lower() in ['jpg', 'jpeg']:
                        img.save(output_path, quality=self.quality.get())
                    else:
                        img.save(output_path)
            
            # Complete
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_var.set(f"Conversion complete. Images saved to {output_folder}"))
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Conversion complete.\n{total_pages} pages converted and saved to:\n{output_folder}"))
            
        except Exception as e:
            raise Exception(f"Conversion failed: {str(e)}")
    
    def _batch_convert(self):
        # Get all PDF files in the selected directory
        pdf_files = [f for f in os.listdir(self.pdf_path.get()) if f.lower().endswith('.pdf')]
        
        if not pdf_files:
            self.root.after(0, lambda: messagebox.showwarning("Warning", "No PDF files found in the selected directory."))
            self.root.after(0, lambda: self.status_var.set("No PDF files found"))
            return
        
        total_files = len(pdf_files)
        self.root.after(0, lambda: self.status_var.set(f"Found {total_files} PDF files to convert"))
        
        # Process each PDF file
        for i, pdf_file in enumerate(pdf_files):
            if self.conversion_canceled:
                self.root.after(0, lambda: self.status_var.set("Batch conversion canceled"))
                return
                
            pdf_path = os.path.join(self.pdf_path.get(), pdf_file)
            pdf_basename = os.path.splitext(pdf_file)[0]
            
            # Create output folder for this PDF
            output_folder = os.path.join(self.pdf_output_dir.get(), pdf_basename)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Update progress
            file_progress = (i / total_files) * 100
            self.root.after(0, lambda p=file_progress: self.progress_var.set(p))
            self.root.after(0, lambda f=pdf_file: self.status_var.set(f"Converting {f} ({i+1}/{total_files})..."))
            
            try:
                # Get the total pages for this PDF
                from pdf2image.pdf2image import pdfinfo_from_path
                info = pdfinfo_from_path(pdf_path)
                total_pages = info["Pages"]
                
                # Determine page range
                start_page = self.start_page.get()
                end_page = min(self.end_page.get(), total_pages)
                
                # Convert pages in batches to save memory
                batch_size = 10  # Process 10 pages at a time
                for page_start in range(start_page, end_page + 1, batch_size):
                    if self.conversion_canceled:
                        break
                        
                    page_end = min(page_start + batch_size - 1, end_page)
                    
                    # Convert batch of pages
                    images = convert_from_path(
                        pdf_path,
                        dpi=self.dpi.get(),
                        first_page=page_start,
                        last_page=page_end
                    )
                    
                    # Save each image
                    for idx, img in enumerate(images):
                        page_num = page_start + idx
                        output_filename = f"{pdf_basename}_{page_num}.{self.format.get()}"
                        output_path = os.path.join(output_folder, output_filename)
                        
                        # Save with quality setting if JPEG
                        if self.format.get().lower() in ['jpg', 'jpeg']:
                            img.save(output_path, quality=self.quality.get())
                        else:
                            img.save(output_path)
                
            except Exception as e:
                self.root.after(0, lambda f=pdf_file, err=str(e): 
                    messagebox.showwarning("Warning", f"Failed to convert {f}: {err}"))
                continue
        
        # Complete
        if not self.conversion_canceled:
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.status_var.set("Batch conversion complete"))
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                f"Batch conversion complete.\n{total_files} PDF files processed.\nOutput saved to: {self.pdf_output_dir.get()}"))
    
    def cancel_conversion(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling conversion...")
        
    # Image to PDF methods
    
    def add_images(self):
        file_paths = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("JPEG", "*.jpg *.jpeg"),
                ("PNG", "*.png"),
                ("All Files", "*.*")
            ]
        )
        
        if file_paths:
            for path in file_paths:
                self.images_paths.append(path)
                self.img_listbox.insert(tk.END, os.path.basename(path))
            
            self.img_status_var.set(f"Added {len(file_paths)} images. Total: {len(self.images_paths)}")
            
            # Select the first image if none selected
            if len(self.images_paths) == len(file_paths):
                self.img_listbox.selection_set(0)
                self.on_image_select(None)
    
    def remove_selected_image(self):
        selected_indices = self.img_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select an image to remove")
            return
            
        # Remove in reverse order to avoid index shifting
        for index in sorted(selected_indices, reverse=True):
            self.img_listbox.delete(index)
            del self.images_paths[index]
        
        self.img_status_var.set(f"Removed {len(selected_indices)} images. Total: {len(self.images_paths)}")
        
        # Update preview if needed
        if self.images_paths and self.selected_image_index >= len(self.images_paths):
            self.selected_image_index = len(self.images_paths) - 1
            self.img_listbox.selection_set(self.selected_image_index)
            self.preview_selected_image()
        elif not self.images_paths:
            self.selected_image_index = 0
            self.img_canvas.delete("all")
            self.selected_image_label.config(text="None selected")
    
    def clear_images(self):
        if not self.images_paths:
            return
            
        result = messagebox.askyesno("Confirm", "Are you sure you want to clear all images?")
        if result:
            self.img_listbox.delete(0, tk.END)
            self.images_paths.clear()
            self.img_canvas.delete("all")
            self.selected_image_index = 0
            self.selected_image_label.config(text="None selected")
            self.img_status_var.set("All images cleared")
    
    def move_image_up(self):
        selected_indices = self.img_listbox.curselection()
        if not selected_indices or selected_indices[0] == 0:
            return
            
        index = selected_indices[0]
        # Swap in paths list
        self.images_paths[index], self.images_paths[index-1] = self.images_paths[index-1], self.images_paths[index]
        
        # Update listbox
        self.img_listbox.delete(index-1, index)
        self.img_listbox.insert(index-1, os.path.basename(self.images_paths[index-1]))
        self.img_listbox.insert(index, os.path.basename(self.images_paths[index]))
        
        # Reselect the moved item
        self.img_listbox.selection_clear(0, tk.END)
        self.img_listbox.selection_set(index-1)
        self.selected_image_index = index-1
        
        self.img_status_var.set(f"Moved image up: {os.path.basename(self.images_paths[index-1])}")
    
    def move_image_down(self):
        selected_indices = self.img_listbox.curselection()
        if not selected_indices or selected_indices[0] == len(self.images_paths) - 1:
            return
            
        index = selected_indices[0]
        # Swap in paths list
        self.images_paths[index], self.images_paths[index+1] = self.images_paths[index+1], self.images_paths[index]
        
        # Update listbox
        self.img_listbox.delete(index, index+1)
        self.img_listbox.insert(index, os.path.basename(self.images_paths[index]))
        self.img_listbox.insert(index+1, os.path.basename(self.images_paths[index+1]))
        
        # Reselect the moved item
        self.img_listbox.selection_clear(0, tk.END)
        self.img_listbox.selection_set(index+1)
        self.selected_image_index = index+1
        
        self.img_status_var.set(f"Moved image down: {os.path.basename(self.images_paths[index+1])}")
    
    def on_image_select(self, event):
        selected_indices = self.img_listbox.curselection()
        if selected_indices:
            self.selected_image_index = selected_indices[0]
            filename = os.path.basename(self.images_paths[self.selected_image_index])
            self.selected_image_label.config(text=filename)
            self.preview_selected_image()
    
    def preview_selected_image(self):
        if not self.images_paths:
            messagebox.showinfo("Info", "No images available to preview")
            return
            
        if not self.img_listbox.curselection():
            messagebox.showinfo("Info", "Please select an image to preview")
            return
            
        try:
            image_path = self.images_paths[self.selected_image_index]
            self.img_status_var.set(f"Loading preview for {os.path.basename(image_path)}...")
            
            # Load image in a separate thread
            threading.Thread(target=self._load_image_preview, args=(image_path,)).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.img_status_var.set(f"Error: {str(e)}")
    
    def _load_image_preview(self, image_path):
        try:
            img = PILImage.open(image_path)
            self.display_preview(img, "img")
            self.root.after(0, lambda: self.img_status_var.set(f"Preview loaded: {os.path.basename(image_path)}"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load image: {str(e)}"))
            self.root.after(0, lambda: self.img_status_var.set(f"Error: {str(e)}"))
    
    def browse_img_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.img_output_dir.get() if self.img_output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.img_output_dir.set(selected_dir)
    
    def start_img_conversion(self):
        if not self.images_paths:
            messagebox.showerror("Error", "Please add at least one image to convert")
            return
            
        if not self.img_output_dir.get() or not os.path.isdir(self.img_output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory")
            return
            
        if not self.pdf_name.get():
            messagebox.showerror("Error", "Please enter a name for the output PDF file")
            return
            
        # Add .pdf extension if not present
        pdf_filename = self.pdf_name.get()
        if not pdf_filename.lower().endswith('.pdf'):
            pdf_filename += ".pdf"
            
        output_path = os.path.join(self.img_output_dir.get(), pdf_filename)
        
        # Confirm if file exists
        if os.path.exists(output_path):
            result = messagebox.askyesno("Confirm", f"File {pdf_filename} already exists. Overwrite?")
            if not result:
                return
                
        # Disable controls during conversion
        self._set_controls_state(tk.DISABLED, "img")
        
        # Start conversion in a separate thread
        self.img_conversion_canceled = False
        threading.Thread(target=self._img_conversion_thread, args=(output_path,)).start()
    
    def _img_conversion_thread(self, output_path):
        try:
            self.root.after(0, lambda: self.img_status_var.set("Creating PDF from images..."))
            self.root.after(0, lambda: self.img_progress_var.set(0))
            
            # Get page size dimensions in points (1/72 inch)
            page_sizes = {
                "A4": (595, 842),  # 210 × 297 mm
                "Letter": (612, 792),  # 8.5 × 11 inches
                "Legal": (612, 1008),  # 8.5 × 14 inches
                "Tabloid": (792, 1224),  # 11 × 17 inches
                "A3": (842, 1191),  # 297 × 420 mm
                "A5": (420, 595),  # 148 × 210 mm
            }
            
            # Get selected page size
            page_width, page_height = page_sizes.get(self.page_size.get(), page_sizes["A4"])
            
            # Adjust for orientation
            if self.orientation.get() == "landscape":
                page_width, page_height = page_height, page_width
            
            # Convert margin from mm to points (1 mm = 2.83 points)
            margin = self.margin.get() * 2.83
            
            # Create PDF
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            
            c = canvas.Canvas(output_path, pagesize=(page_width, page_height))
            
            total_images = len(self.images_paths)
            for i, img_path in enumerate(self.images_paths):
                if self.img_conversion_canceled:
                    self.root.after(0, lambda: self.img_status_var.set("Conversion canceled"))
                    # Delete partial PDF
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
                    return
                
                # Update progress
                progress_pct = ((i + 1) / total_images) * 100
                self.root.after(0, lambda p=progress_pct: self.img_progress_var.set(p))
                self.root.after(0, lambda p=i+1, t=total_images: 
                    self.img_status_var.set(f"Processing image {p}/{t}: {os.path.basename(self.images_paths[i])}"))
                
                # Open image and get dimensions
                img = PILImage.open(img_path)
                img_width, img_height = img.size
                
                # Calculate maximum dimensions preserving aspect ratio
                max_width = page_width - 2 * margin
                max_height = page_height - 2 * margin
                
                # Calculate scaling factor
                scale = min(max_width / img_width, max_height / img_height)
                new_width = img_width * scale
                new_height = img_height * scale
                
                # Calculate centered position
                x_pos = (page_width - new_width) / 2
                y_pos = (page_height - new_height) / 2
                
                # Draw image
                c.drawImage(ImageReader(img), x_pos, y_pos, width=new_width, height=new_height)
                
                # Go to next page
                c.showPage()
            
            # Save PDF
            c.save()
            
            # Complete
            self.root.after(0, lambda: self.img_progress_var.set(100))
            self.root.after(0, lambda: self.img_status_var.set(f"PDF created successfully: {os.path.basename(output_path)}"))
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                f"PDF created successfully.\n{total_images} images included.\nSaved to: {output_path}"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to create PDF: {str(e)}"))
            self.root.after(0, lambda: self.img_status_var.set(f"Error: {str(e)}"))
            # Delete partial PDF
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
        finally:
            # Re-enable controls
            self.root.after(0, lambda: self._set_controls_state(tk.NORMAL, "img"))
    
    def cancel_img_conversion(self):
        self.img_conversion_canceled = True
        self.img_status_var.set("Canceling conversion...")
    
    def open_output_folder(self, mode):
        # Determine output directory based on mode
        output_dir = self.pdf_output_dir.get() if mode == "pdf" else self.img_output_dir.get()
        
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Output directory does not exist")
            return
            
        # Open the folder in file explorer
        if os.name == 'nt':  # Windows
            os.startfile(output_dir)
        elif os.name == 'posix':  # macOS or Linux
            if sys.platform == 'darwin':  # macOS
                os.system(f'open "{output_dir}"')
            else:  # Linux
                os.system(f'xdg-open "{output_dir}"')
    
    def _set_controls_state(self, state, mode):
        # Determine which tab to modify based on mode
        tab = self.pdf_to_image_tab if mode == "pdf" else self.image_to_pdf_tab
        
        # Disable/enable all interactive controls during conversion
        for widget in tab.winfo_children():
            if isinstance(widget, (ttk.LabelFrame, ttk.Frame)):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Button, ttk.Entry, ttk.Spinbox, ttk.Combobox, 
                                        ttk.Checkbutton, ttk.Scale, tk.Listbox)):
                        # Don't disable Cancel button
                        if isinstance(child, ttk.Button) and child["text"] == "Cancel":
                            continue
                        
                        # Check for nested widgets
                        if isinstance(child, ttk.Frame):
                            for subchild in child.winfo_children():
                                if isinstance(subchild, (ttk.Button, ttk.Entry, ttk.Spinbox)):
                                    subchild.configure(state=state)
                        else:
                            child.configure(state=state)

def main():
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

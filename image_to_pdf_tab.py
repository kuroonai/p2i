import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import utils

class ImageToPDFTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Variables
        self.images_paths = []
        self.output_dir = tk.StringVar()
        self.pdf_name = tk.StringVar(value="output.pdf")
        self.page_size = tk.StringVar(value="A4")
        self.orientation = tk.StringVar(value="portrait")
        self.margin = tk.IntVar(value=10)
        self.img_quality = tk.IntVar(value=90)
        self.preview_image = None
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.selected_image_index = 0
        self.conversion_canceled = False
        
        # Create UI elements
        self.create_file_frame()
        self.create_options_frame()
        self.create_preview_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame, 
            self.start_conversion, 
            self.cancel_conversion, 
            self.open_output_folder,
            "Create PDF from Images"
        )
        
        # Set default output directory to user's Documents folder
        default_output = os.path.join(str(Path.home()), "Documents")
        self.output_dir.set(default_output)
    
    def create_file_frame(self):
        file_frame = ttk.LabelFrame(self.frame, text="Image Selection", padding=10)
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
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=2, column=2, sticky="e", padx=5, pady=5)
        
        ttk.Label(file_frame, text="PDF Filename:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_name, width=50).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Make rows and columns expand
        file_frame.rowconfigure(1, weight=1)
        file_frame.columnconfigure(1, weight=1)
    
    def create_options_frame(self):
        options_frame = ttk.LabelFrame(self.frame, text="PDF Options", padding=10)
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
        
        self.quality_label = ttk.Label(options_frame, text=f"{self.img_quality.get()}%")
        self.quality_label.grid(row=1, column=4, sticky="w", padx=5, pady=5)
        
        # Update the quality label when the slider changes
        def update_quality_label(*args):
            self.quality_label.configure(text=f"{self.img_quality.get()}%")
        
        self.img_quality.trace_add("write", update_quality_label)
    
    def create_preview_frame(self):
        preview_frame = ttk.LabelFrame(self.frame, text="Preview", padding=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Preview canvas
        self.canvas = tk.Canvas(preview_frame, bg="#ffffff", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Preview Selected Image", command=self.preview_selected_image).pack(side="left", padx=5)
        ttk.Label(controls_frame, text="Image:").pack(side="left", padx=5)
        
        self.selected_image_label = ttk.Label(controls_frame, text="None selected")
        self.selected_image_label.pack(side="left", padx=5)
    
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
            
            self.status_var.set(f"Added {len(file_paths)} images. Total: {len(self.images_paths)}")
            
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
        
        self.status_var.set(f"Removed {len(selected_indices)} images. Total: {len(self.images_paths)}")
        
        # Update preview if needed
        if self.images_paths and self.selected_image_index >= len(self.images_paths):
            self.selected_image_index = len(self.images_paths) - 1
            self.img_listbox.selection_set(self.selected_image_index)
            self.preview_selected_image()
        elif not self.images_paths:
            self.selected_image_index = 0
            self.canvas.delete("all")
            self.selected_image_label.config(text="None selected")
    
    def clear_images(self):
        if not self.images_paths:
            return
            
        result = messagebox.askyesno("Confirm", "Are you sure you want to clear all images?")
        if result:
            self.img_listbox.delete(0, tk.END)
            self.images_paths.clear()
            self.canvas.delete("all")
            self.selected_image_index = 0
            self.selected_image_label.config(text="None selected")
            self.status_var.set("All images cleared")
    
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
        
        self.status_var.set(f"Moved image up: {os.path.basename(self.images_paths[index-1])}")
    
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
        
        self.status_var.set(f"Moved image down: {os.path.basename(self.images_paths[index+1])}")
    
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
            self.status_var.set(f"Loading preview for {os.path.basename(image_path)}...")
            
            # Load image in a separate thread
            threading.Thread(target=self._load_image_preview, args=(image_path,)).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def _load_image_preview(self, image_path):
        try:
            img = Image.open(image_path)
            self._display_preview(img)
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Preview loaded: {os.path.basename(image_path)}"))
        except Exception as e:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to load image: {str(e)}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def _display_preview(self, img):
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
        
        # Update the canvas in the main thread
        self.frame.winfo_toplevel().after(0, lambda: self._update_canvas(photo, new_width, new_height))
    
    def _update_canvas(self, photo, width, height):
        # Clear previous content
        self.canvas.delete("all")
        
        # Calculate center position
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        x_pos = (canvas_width - width) // 2
        y_pos = (canvas_height - height) // 2
        
        # Create image on canvas
        self.canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=photo)
    
    def browse_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)
    
    def start_conversion(self):
        if not self.images_paths:
            messagebox.showerror("Error", "Please add at least one image to convert")
            return
            
        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory")
            return
            
        if not self.pdf_name.get():
            messagebox.showerror("Error", "Please enter a name for the output PDF file")
            return
            
        # Add .pdf extension if not present
        pdf_filename = self.pdf_name.get()
        if not pdf_filename.lower().endswith('.pdf'):
            pdf_filename += ".pdf"
            
        output_path = os.path.join(self.output_dir.get(), pdf_filename)
        
        # Confirm if file exists
        if os.path.exists(output_path):
            result = messagebox.askyesno("Confirm", f"File {pdf_filename} already exists. Overwrite?")
            if not result:
                return
                
        # Disable controls during conversion
        utils.set_controls_state(self.frame, tk.DISABLED)
        
        # Start conversion in a separate thread
        self.conversion_canceled = False
        threading.Thread(target=self._conversion_thread, args=(output_path,)).start()
    
    def _conversion_thread(self, output_path):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Creating PDF from images..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
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
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Conversion canceled"))
                    # Delete partial PDF
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
                    return
                
                # Update progress
                progress_pct = ((i + 1) / total_images) * 100
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=i+1, t=total_images: 
                    self.status_var.set(f"Processing image {p}/{t}: {os.path.basename(self.images_paths[i])}"))
                
                # Open image and get dimensions
                img = Image.open(img_path)
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
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"PDF created successfully: {os.path.basename(output_path)}"))
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", 
                f"PDF created successfully.\n{total_images} images included.\nSaved to: {output_path}"))
            
        except Exception as e:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to create PDF: {str(e)}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
            # Delete partial PDF
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
        finally:
            # Re-enable controls
            self.frame.winfo_toplevel().after(0, lambda: utils.set_controls_state(self.frame, tk.NORMAL))
    
    def cancel_conversion(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling conversion...")
    
    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())
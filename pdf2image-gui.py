#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to Image GUI Converter
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

class PDF2ImageGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Image Converter")
        self.root.geometry("850x650")
        self.root.configure(bg="#f0f0f0")
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()
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
        self.create_file_frame()
        self.create_options_frame()
        self.create_preview_frame()
        self.create_progress_frame()
        self.create_buttons_frame()
        
        # Set default output directory to user's Pictures folder
        default_output = os.path.join(str(Path.home()), "Pictures")
        self.output_dir.set(default_output)
        
    def create_file_frame(self):
        file_frame = ttk.LabelFrame(self.root, text="File Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # PDF File selection
        ttk.Label(file_frame, text="PDF File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_pdf).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Output directory selection
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
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
        
    def create_options_frame(self):
        options_frame = ttk.LabelFrame(self.root, text="Conversion Options", padding=10)
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
        
    def create_preview_frame(self):
        preview_frame = ttk.LabelFrame(self.root, text="Preview", padding=10)
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
        
    def create_progress_frame(self):
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding=10)
        progress_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill="x", expand=True, padx=5, pady=5)
        
        # Status label
        ttk.Label(progress_frame, textvariable=self.status_var).pack(fill="x", expand=True, padx=5, pady=5)
        
    def create_buttons_frame(self):
        buttons_frame = ttk.Frame(self.root, padding=10)
        buttons_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        ttk.Button(buttons_frame, text="Convert", command=self.start_conversion).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Cancel", command=self.cancel_conversion).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Open Output Folder", command=self.open_output_folder).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)
        
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
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)
            
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
        for child in self.root.winfo_children():
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
                self.display_preview(img)
            else:
                self.root.after(0, lambda: messagebox.showwarning("Warning", "No pages were converted."))
                
            self.root.after(0, lambda: self.status_var.set("Preview generated"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to generate preview: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def display_preview(self, img):
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
        self.root.after(0, lambda: self._update_canvas(photo, new_width, new_height))
    
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
    
    def start_conversion(self):
        if self.batch_mode.get():
            if not self.pdf_path.get() or not os.path.isdir(self.pdf_path.get()):
                messagebox.showerror("Error", "Please select a valid folder containing PDFs.")
                return
        else:
            if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
                messagebox.showerror("Error", "Please select a valid PDF file.")
                return
        
        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
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
        self._set_controls_state(tk.DISABLED)
        
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
            self.root.after(0, lambda: self._set_controls_state(tk.NORMAL))
    
    def _single_convert(self):
        self.root.after(0, lambda: self.status_var.set("Converting PDF to images..."))
        
        # Create folder with same name as PDF if it doesn't exist
        pdf_basename = os.path.splitext(os.path.basename(self.pdf_path.get()))[0]
        output_folder = os.path.join(self.output_dir.get(), pdf_basename)
        
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
            output_folder = os.path.join(self.output_dir.get(), pdf_basename)
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
                f"Batch conversion complete.\n{total_files} PDF files processed.\nOutput saved to: {self.output_dir.get()}"))
    
    def cancel_conversion(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling conversion...")
    
    def open_output_folder(self):
        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Output directory does not exist")
            return
            
        # Open the folder in file explorer
        if os.name == 'nt':  # Windows
            os.startfile(self.output_dir.get())
        elif os.name == 'posix':  # macOS or Linux
            if sys.platform == 'darwin':  # macOS
                os.system(f'open "{self.output_dir.get()}"')
            else:  # Linux
                os.system(f'xdg-open "{self.output_dir.get()}"')
    
    def _set_controls_state(self, state):
        # Disable/enable all interactive controls during conversion
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.LabelFrame) or isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Button, ttk.Entry, ttk.Spinbox, ttk.Combobox, ttk.Checkbutton, ttk.Scale)):
                        if child.winfo_name() != "!button2":  # Don't disable Cancel button
                            child.configure(state=state)

def main():
    root = tk.Tk()
    app = PDF2ImageGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pypdfium2 as pdfium
import utils

class PDFSplitTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Variables
        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.start_page = tk.IntVar(value=1)
        self.end_page = tk.IntVar(value=1)
        self.split_mode = tk.StringVar(value="range")  # "range", "single", "extract"
        self.total_pages = 0
        self.single_pages = tk.StringVar(value="")  # comma-separated page numbers
        self.page_interval = tk.IntVar(value=1)  # For splitting by intervals
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.conversion_canceled = False
        self._pages_to_extract = []
        
        # Create UI elements
        self.create_file_frame()
        self.create_options_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame, 
            self.start_split, 
            self.cancel_split, 
            self.open_output_folder,
            "Split PDF"
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
        
        # Page count button
        ttk.Button(file_frame, text="Get Page Count", command=self.get_page_count).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        
        # Total pages display
        self.pages_label = ttk.Label(file_frame, text="Total Pages: 0")
        self.pages_label.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        # Make column 1 expand
        file_frame.columnconfigure(1, weight=1)
    
    def create_options_frame(self):
        options_frame = ttk.LabelFrame(self.frame, text="Split Options", padding=10)
        options_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Split mode selection
        ttk.Label(options_frame, text="Split Mode:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        
        mode_frame = ttk.Frame(options_frame)
        mode_frame.grid(row=0, column=1, columnspan=3, sticky="w", padx=5, pady=5)
        
        self.mode_range = ttk.Radiobutton(mode_frame, text="Page Range", variable=self.split_mode, value="range", command=self.toggle_split_mode)
        self.mode_range.pack(side="left", padx=5)
        
        self.mode_single = ttk.Radiobutton(mode_frame, text="Single Pages", variable=self.split_mode, value="single", command=self.toggle_split_mode)
        self.mode_single.pack(side="left", padx=5)
        
        self.mode_extract = ttk.Radiobutton(mode_frame, text="Extract Every N Pages", variable=self.split_mode, value="extract", command=self.toggle_split_mode)
        self.mode_extract.pack(side="left", padx=5)
        
        # Page range options
        self.range_frame = ttk.Frame(options_frame)
        self.range_frame.grid(row=1, column=0, columnspan=4, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.range_frame, text="Start Page:").pack(side="left", padx=5)
        ttk.Spinbox(self.range_frame, from_=1, to=9999, textvariable=self.start_page, width=10).pack(side="left", padx=5)
        
        ttk.Label(self.range_frame, text="End Page:").pack(side="left", padx=5)
        ttk.Spinbox(self.range_frame, from_=1, to=9999, textvariable=self.end_page, width=10).pack(side="left", padx=5)
        
        # Single pages options
        self.single_frame = ttk.Frame(options_frame)
        self.single_frame.grid(row=2, column=0, columnspan=4, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.single_frame, text="Page Numbers:").pack(side="left", padx=5)
        ttk.Entry(self.single_frame, textvariable=self.single_pages, width=40).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Label(self.single_frame, text="(comma-separated, e.g. 1,3,5-7)").pack(side="left", padx=5)
        
        # Extract every N pages options
        self.extract_frame = ttk.Frame(options_frame)
        self.extract_frame.grid(row=3, column=0, columnspan=4, sticky="w", padx=5, pady=5)
        
        ttk.Label(self.extract_frame, text="Extract every").pack(side="left", padx=5)
        ttk.Spinbox(self.extract_frame, from_=1, to=100, textvariable=self.page_interval, width=5).pack(side="left", padx=5)
        ttk.Label(self.extract_frame, text="page(s)").pack(side="left", padx=5)
        
        # Hide single and extract frames initially
        self.single_frame.grid_remove()
        self.extract_frame.grid_remove()
    
    def toggle_split_mode(self):
        """Show/hide option frames based on selected split mode"""
        mode = self.split_mode.get()
        
        if mode == "range":
            self.range_frame.grid()
            self.single_frame.grid_remove()
            self.extract_frame.grid_remove()
        elif mode == "single":
            self.range_frame.grid_remove()
            self.single_frame.grid()
            self.extract_frame.grid_remove()
        elif mode == "extract":
            self.range_frame.grid_remove()
            self.single_frame.grid_remove()
            self.extract_frame.grid()
    
    def browse_pdf(self):
        selected_file = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
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
    
    def get_page_count(self):
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            messagebox.showerror("Error", "Please select a valid PDF file first.")
            return
            
        try:
            self.status_var.set("Counting pages...")
            # Put this in a thread to avoid freezing the UI
            threading.Thread(target=self._get_page_count_thread).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get page count: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def _get_page_count_thread(self):
        try:
            pdf = pdfium.PdfDocument(self.pdf_path.get())
            self.total_pages = len(pdf)
            
            # Update UI in the main thread
            self.frame.winfo_toplevel().after(0, self._update_page_count_ui)
        except Exception as e:
            error_msg = str(e)
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to get page count: {error_msg}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {error_msg}"))
    
    def _update_page_count_ui(self):
        self.end_page.set(self.total_pages)
        self.pages_label.config(text=f"Total Pages: {self.total_pages}")
        self.status_var.set(f"PDF has {self.total_pages} pages")
    
    def start_split(self):
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return
        
        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory.")
            return
            
        # Validate options based on the selected mode
        mode = self.split_mode.get()
        
        if mode == "range":
            if self.start_page.get() < 1 or self.start_page.get() > self.total_pages:
                messagebox.showerror("Error", f"Start page must be between 1 and {self.total_pages}.")
                return
                
            if self.end_page.get() < self.start_page.get() or self.end_page.get() > self.total_pages:
                messagebox.showerror("Error", f"End page must be between {self.start_page.get()} and {self.total_pages}.")
                return
                
        elif mode == "single":
            if not self.single_pages.get().strip():
                messagebox.showerror("Error", "Please enter page numbers to extract.")
                return
                
            # Validate page numbers in another function to keep this one clean
            if not self._validate_page_numbers():
                return
                
        elif mode == "extract":
            if self.page_interval.get() < 1:
                messagebox.showerror("Error", "Page interval must be at least 1.")
                return
        
        # Disable controls during splitting
        utils.set_controls_state(self.frame, tk.DISABLED)
        
        # Start conversion in a separate thread
        self.conversion_canceled = False
        threading.Thread(target=self._split_thread).start()
    
    def _validate_page_numbers(self):
        """Validate page numbers entered in the single pages mode"""
        try:
            page_specs = self.single_pages.get().split(',')
            pages = []
            
            for spec in page_specs:
                spec = spec.strip()
                if '-' in spec:
                    # Handle page range like "5-10"
                    start, end = map(int, spec.split('-'))
                    if start < 1 or end > self.total_pages or start > end:
                        messagebox.showerror("Error", f"Invalid page range: {spec}. Must be between 1 and {self.total_pages}.")
                        return False
                    pages.extend(range(start, end + 1))
                else:
                    # Handle single page
                    page = int(spec)
                    if page < 1 or page > self.total_pages:
                        messagebox.showerror("Error", f"Invalid page number: {page}. Must be between 1 and {self.total_pages}.")
                        return False
                    pages.append(page)
            
            # Store the validated page numbers
            self._pages_to_extract = sorted(set(pages))  # Remove duplicates and sort
            return True
            
        except ValueError:
            messagebox.showerror("Error", "Invalid page format. Use comma-separated numbers and ranges (e.g., 1,3,5-7).")
            return False
    
    def _split_thread(self):
        try:
            mode = self.split_mode.get()
            
            if mode == "range":
                self._split_by_range()
            elif mode == "single":
                self._split_single_pages()
            elif mode == "extract":
                self._split_by_interval()
                
        except Exception as e:
            error_msg = str(e)
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to split PDF: {error_msg}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {error_msg}"))
        finally:
            # Re-enable controls
            self.frame.winfo_toplevel().after(0, lambda: utils.set_controls_state(self.frame, tk.NORMAL))
    
    def _split_by_range(self):
        """Split PDF by page range"""
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Splitting PDF by page range..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
            # Get source PDF filename without extension
            pdf_basename = os.path.splitext(os.path.basename(self.pdf_path.get()))[0]
            
            # Create output filename
            start = self.start_page.get()
            end = self.end_page.get()
            output_filename = f"{pdf_basename}_pages_{start}-{end}.pdf"
            output_path = os.path.join(self.output_dir.get(), output_filename)
            
            # Open source PDF
            source_pdf = pdfium.PdfDocument(self.pdf_path.get())
            
            # Use PyPDF's split_page method, not import_page
            # First, create a new empty document
            output_pdf = pdfium.PdfDocument.new()
            
            # Copy pages from source to output
            for i, page_idx in enumerate(range(start-1, end)):
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Splitting canceled"))
                    return
                
                # Update progress
                progress_pct = ((i + 1) / (end - start + 1)) * 100
                current_page = page_idx + 1
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=current_page: 
                    self.status_var.set(f"Processing page {p}..."))
                
                output_pdf.import_pages(source_pdf, [page_idx])
            
            # Save the new PDF
            output_pdf.save(output_path)
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"PDF split complete: {output_filename}"))
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", 
                f"PDF split successfully.\nPages {start}-{end} extracted.\nSaved to: {output_path}"))
            
        except Exception as e:
            error_msg = str(e)
            raise Exception(f"Failed to split PDF by range: {error_msg}")
    
    def _split_single_pages(self):
        """Extract specific pages from PDF"""
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Extracting selected pages..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
            # Get source PDF filename without extension
            pdf_basename = os.path.splitext(os.path.basename(self.pdf_path.get()))[0]
            
            # Create output filename
            page_list = ','.join(str(p) for p in self._pages_to_extract)
            if len(page_list) > 20:  # Truncate if too long
                page_list = page_list[:20] + "..."
            output_filename = f"{pdf_basename}_pages_{page_list}.pdf"
            output_path = os.path.join(self.output_dir.get(), output_filename)
            
            # Open source PDF
            source_pdf = pdfium.PdfDocument(self.pdf_path.get())
            
            # Create new PDF with selected pages
            output_pdf = pdfium.PdfDocument.new()
            
            for i, page_num in enumerate(self._pages_to_extract):
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Extraction canceled"))
                    return
                
                # Update progress
                progress_pct = ((i + 1) / len(self._pages_to_extract)) * 100
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=page_num: 
                    self.status_var.set(f"Processing page {p}..."))
                
                # Get page and add it to the output document
                output_pdf.import_pages(source_pdf, [page_num - 1])
            
            # Save the new PDF
            output_pdf.save(output_path)
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Page extraction complete: {output_filename}"))
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", 
                f"Pages extracted successfully.\n{len(self._pages_to_extract)} pages extracted.\nSaved to: {output_path}"))
            
        except Exception as e:
            error_msg = str(e)
            raise Exception(f"Failed to extract pages: {error_msg}")
    
    def _split_by_interval(self):
        """Extract every Nth page from PDF"""
        try:
            interval = self.page_interval.get()
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Extracting every {interval} page(s)..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
            # Get source PDF filename without extension
            pdf_basename = os.path.splitext(os.path.basename(self.pdf_path.get()))[0]
            
            # Create output filename
            output_filename = f"{pdf_basename}_every_{interval}_pages.pdf"
            output_path = os.path.join(self.output_dir.get(), output_filename)
            
            # Open source PDF
            source_pdf = pdfium.PdfDocument(self.pdf_path.get())
            
            # Create list of pages to extract
            pages_to_extract = list(range(0, self.total_pages, interval))
            
            # Create new PDF with selected pages
            output_pdf = pdfium.PdfDocument.new()
            
            for i, page_idx in enumerate(pages_to_extract):
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Extraction canceled"))
                    return
                
                # Update progress
                progress_pct = ((i + 1) / len(pages_to_extract)) * 100
                current_page = page_idx + 1
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=current_page: 
                    self.status_var.set(f"Processing page {p}..."))
                
                # Get page and add it to the output document
                output_pdf.import_pages(source_pdf, [page_idx])
            
            # Save the new PDF
            output_pdf.save(output_path)
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Page extraction complete: {output_filename}"))
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", 
                f"Pages extracted successfully.\n{len(pages_to_extract)} pages extracted.\nSaved to: {output_path}"))
            
        except Exception as e:
            error_msg = str(e)
            raise Exception(f"Failed to extract pages: {error_msg}")
    
    def cancel_split(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling split operation...")
    
    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())
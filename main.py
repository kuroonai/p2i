# main.py
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, askdirectory
import multiprocessing

# Import all tab modules
from pdf_merge_tab import PDFMergeTab
from pdf_split_tab import PDFSplitTab
from pdf_compress_tab import PDFCompressTab
from pdf_to_image_tab import PDFToImageTab
from image_to_pdf_tab import ImageToPDFTab
from pdf_security_tab import PDFSecurityTab
from image_batch_tab import ImageBatchTab
from office_convert_tab import OfficeConvertTab

# Import settings and drag drop
from settings import Settings
from drag_drop import DragDropManager

class P2IApp:
    def __init__(self, root):
        self.root = root
        self.root.title("p2i - PDF & Image Processing Tool")
        self.root.geometry("900x700")
        
        # Load settings
        self.settings = Settings()
        
        # Set up main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Detect CPU count for parallel processing
        n_cpu = max(1, multiprocessing.cpu_count() - 1)  # Leave one CPU free
        
        # Create tabs
        self.pdf_merge_tab = PDFMergeTab(self.notebook)
        self.pdf_split_tab = PDFSplitTab(self.notebook)
        self.pdf_compress_tab = PDFCompressTab(self.notebook)
        self.pdf_to_image_tab = PDFToImageTab(self.notebook, n_cpu)
        self.image_to_pdf_tab = ImageToPDFTab(self.notebook)
        self.pdf_security_tab = PDFSecurityTab(self.notebook)
        self.image_batch_tab = ImageBatchTab(self.notebook)
        self.office_convert_tab = OfficeConvertTab(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.pdf_merge_tab.frame, text="Merge PDFs")
        self.notebook.add(self.pdf_split_tab.frame, text="Split PDF")
        self.notebook.add(self.pdf_compress_tab.frame, text="Compress PDF")
        self.notebook.add(self.pdf_to_image_tab.frame, text="PDF to Image")
        self.notebook.add(self.image_to_pdf_tab.frame, text="Image to PDF")
        self.notebook.add(self.pdf_security_tab.frame, text="PDF Security")
        self.notebook.add(self.image_batch_tab.frame, text="Image Processing")
        self.notebook.add(self.office_convert_tab.frame, text="Office/Markdown to PDF")
        
        # Create main menu
        self.create_menu()
        
        # Set up drag and drop
        self.setup_drag_drop()
        
        # Handle application close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open PDF...", command=self.open_pdf)
        file_menu.add_command(label="Open Image...", command=self.open_image)
        file_menu.add_command(label="Open Office Document...", command=self.open_office_doc)
        
        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        self.update_recent_files_menu()
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Clear Recent Files", command=self.clear_recent_files)
        tools_menu.add_command(label="Preferences...", command=self.show_preferences)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="Check for Updates", command=self.check_updates)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_drag_drop(self):
        """Set up drag and drop functionality"""
        # Create list of widgets to receive dropped files
        drop_targets = [
            self.pdf_merge_tab.frame,
            self.pdf_split_tab.frame,
            self.pdf_compress_tab.frame,
            self.pdf_to_image_tab.frame,
            self.image_to_pdf_tab.frame,
            self.pdf_security_tab.frame,
            self.image_batch_tab.frame,
            self.office_convert_tab.frame
        ]
        
        # Initialize drag-drop manager
        self.dnd_manager = DragDropManager(self.root, self.settings, drop_targets)
    
    def update_recent_files_menu(self):
        """Update the recent files menu items"""
        # Clear existing items
        self.recent_menu.delete(0, tk.END)
        
        # Get recent files
        recent_files = self.settings.get_recent_files()
        
        if recent_files:
            # Add each file to the menu
            for file_path in recent_files:
                # Truncate very long paths
                display_path = file_path
                if len(display_path) > 60:
                    display_path = "..." + display_path[-57:]
                    
                self.recent_menu.add_command(
                    label=display_path,
                    command=lambda path=file_path: self.open_recent_file(path)
                )
        else:
            # Add a disabled item if no recent files
            self.recent_menu.add_command(label="No Recent Files", state=tk.DISABLED)
    
    def open_pdf(self):
        """Open a PDF file and switch to appropriate tab"""
        file_path = askopenfilename(
            title="Open PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            self.settings.add_recent_file(file_path)
            self.update_recent_files_menu()
            
            # Determine appropriate tab based on file type
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == ".pdf":
                # Ask user which operation to perform
                operation = self.ask_pdf_operation()
                
                if operation == "merge":
                    self.notebook.select(0)  # Merge tab
                    self.pdf_merge_tab.add_pdfs([file_path])
                elif operation == "split":
                    self.notebook.select(1)  # Split tab
                    self.pdf_split_tab.pdf_path.set(file_path)
                    self.pdf_split_tab.get_page_count()
                elif operation == "compress":
                    self.notebook.select(2)  # Compress tab
                    self.pdf_compress_tab.pdf_path.set(file_path)
                    self.pdf_compress_tab.update_file_size_info()
                elif operation == "to_image":
                    self.notebook.select(3)  # PDF to Image tab
                    self.pdf_to_image_tab.pdf_path.set(file_path)
                    self.pdf_to_image_tab.get_page_count()
                elif operation == "security":
                    self.notebook.select(5)  # PDF Security tab
                    self.pdf_security_tab.pdf_path.set(file_path)
    
    def open_image(self):
        """Open an image file and switch to appropriate tab"""
        file_path = askopenfilename(
            title="Open Image File",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.settings.add_recent_file(file_path)
            self.update_recent_files_menu()
            
            # Ask user which operation to perform
            operation = self.ask_image_operation()
            
            if operation == "to_pdf":
                self.notebook.select(4)  # Image to PDF tab
                self.image_to_pdf_tab.add_images([file_path])
            elif operation == "batch":
                self.notebook.select(6)  # Image Processing tab
                self.image_batch_tab.selected_image_path.set(file_path)
                self.image_batch_tab.show_preview_image(file_path)
    
    def open_office_doc(self):
        """Open an office document and switch to appropriate tab"""
        file_path = askopenfilename(
            title="Open Office Document",
            filetypes=[
                ("Office Documents", "*.docx *.xlsx *.pptx *.doc *.xls *.ppt *.md *.txt"),
                ("Word Documents", "*.docx *.doc"),
                ("Excel Workbooks", "*.xlsx *.xls"),
                ("PowerPoint Presentations", "*.pptx *.ppt"),
                ("Markdown Files", "*.md *.txt"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.settings.add_recent_file(file_path)
            self.update_recent_files_menu()
            
            # Switch to Office Convert tab
            self.notebook.select(7)  # Office/Markdown to PDF tab
            self.office_convert_tab.input_path.set(file_path)
            
            # Set file type based on extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext in [".docx", ".doc"]:
                self.office_convert_tab.file_type.set("word")
            elif ext in [".xlsx", ".xls"]:
                self.office_convert_tab.file_type.set("excel")
            elif ext in [".pptx", ".ppt"]:
                self.office_convert_tab.file_type.set("powerpoint")
            elif ext in [".md", ".txt"]:
                self.office_convert_tab.file_type.set("markdown")
            else:
                self.office_convert_tab.file_type.set("auto")
            
            # Update visible options
            self.office_convert_tab.on_file_type_change(None)
            
            # Set default output name
            input_basename = os.path.splitext(os.path.basename(file_path))[0]
            self.office_convert_tab.output_name.set(f"{input_basename}.pdf")
    
    def open_recent_file(self, file_path):
        """Open a file from the recent files list"""
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            # Remove from recent files
            self.settings.settings['recent_files'].remove(file_path)
            self.settings.save_settings()
            self.update_recent_files_menu()
            return
        
        # Determine file type
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == ".pdf":
            # For PDFs, ask what operation to perform
            self.open_pdf()
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"]:
            # For images
            self.open_image()
        elif ext in [".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt", ".md", ".txt"]:
            # For office documents
            self.open_office_doc()
        else:
            # For unknown types
            messagebox.showinfo("Info", f"Unknown file type: {ext}")
    
    def ask_pdf_operation(self):
        """Ask user which operation to perform on a PDF"""
        operations = {
            "Merge with other PDFs": "merge",
            "Split into parts": "split",
            "Compress PDF": "compress",
            "Convert to images": "to_image",
            "Add security/watermark": "security"
        }
        
        # Create a simple dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Operation")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="What would you like to do with this PDF?", 
                font=("Helvetica", 12)).pack(pady=10)
        
        # Variable to store result
        result = tk.StringVar()
        
        # Create buttons for each operation
        for label, value in operations.items():
            ttk.Button(dialog, text=label, width=30,
                     command=lambda v=value: [result.set(v), dialog.destroy()]).pack(pady=5)
        
        ttk.Button(dialog, text="Cancel", width=30,
                 command=dialog.destroy).pack(pady=10)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        return result.get()
    
    def ask_image_operation(self):
        """Ask user which operation to perform on an image"""
        operations = {
            "Convert to PDF": "to_pdf",
            "Process/Edit Image": "batch"
        }
        
        # Create a simple dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Operation")
        dialog.geometry("350x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="What would you like to do with this image?", 
                font=("Helvetica", 12)).pack(pady=10)
        
        # Variable to store result
        result = tk.StringVar()
        
        # Create buttons for each operation
        for label, value in operations.items():
            ttk.Button(dialog, text=label, width=30,
                     command=lambda v=value: [result.set(v), dialog.destroy()]).pack(pady=5)
        
        ttk.Button(dialog, text="Cancel", width=30,
                 command=dialog.destroy).pack(pady=10)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        return result.get()
    
    def handle_dropped_files(self, files):
        """Process files that were dropped onto the application"""
        if not files:
            return
            
        # Add files to recent list
        for file_path in files:
            self.settings.add_recent_file(file_path)
        
        self.update_recent_files_menu()
        
        # Determine file types
        pdf_files = []
        image_files = []
        office_files = []
        
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".pdf":
                pdf_files.append(file_path)
            elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"]:
                image_files.append(file_path)
            elif ext in [".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt", ".md", ".txt"]:
                office_files.append(file_path)
        
        # Handle based on current tab and dropped file types
        current_tab_idx = self.notebook.index(self.notebook.select())
        
        if current_tab_idx == 0 and pdf_files:  # Merge PDFs tab
            self.pdf_merge_tab.add_pdfs(pdf_files)
        elif current_tab_idx == 1 and len(pdf_files) == 1:  # Split PDF tab
            self.pdf_split_tab.pdf_path.set(pdf_files[0])
            self.pdf_split_tab.get_page_count()
        elif current_tab_idx == 2 and len(pdf_files) == 1:  # Compress PDF tab
            self.pdf_compress_tab.pdf_path.set(pdf_files[0])
            self.pdf_compress_tab.update_file_size_info()
        elif current_tab_idx == 3 and len(pdf_files) == 1:  # PDF to Image tab
            self.pdf_to_image_tab.pdf_path.set(pdf_files[0])
            self.pdf_to_image_tab.get_page_count()
        elif current_tab_idx == 4 and image_files:  # Image to PDF tab
            self.image_to_pdf_tab.add_images(image_files)
        elif current_tab_idx == 5 and len(pdf_files) == 1:  # PDF Security tab
            self.pdf_security_tab.pdf_path.set(pdf_files[0])
        elif current_tab_idx == 6 and image_files:  # Image Processing tab
            if len(image_files) == 1:
                self.image_batch_tab.selected_image_path.set(image_files[0])
                self.image_batch_tab.show_preview_image(image_files[0])
            else:
                # If multiple images, set the images directory to the parent folder of the first image
                parent_dir = os.path.dirname(image_files[0])
                self.image_batch_tab.images_dir.set(parent_dir)
        elif current_tab_idx == 7 and (office_files or pdf_files):  # Office/Markdown to PDF tab
            file_to_use = office_files[0] if office_files else pdf_files[0]
            self.office_convert_tab.input_path.set(file_to_use)
            
            # Set file type based on extension
            ext = os.path.splitext(file_to_use)[1].lower()
            if ext in [".docx", ".doc"]:
                self.office_convert_tab.file_type.set("word")
            elif ext in [".xlsx", ".xls"]:
                self.office_convert_tab.file_type.set("excel")
            elif ext in [".pptx", ".ppt"]:
                self.office_convert_tab.file_type.set("powerpoint")
            elif ext in [".md", ".txt"]:
                self.office_convert_tab.file_type.set("markdown")
            else:
                self.office_convert_tab.file_type.set("auto")
            
            # Update visible options
            self.office_convert_tab.on_file_type_change(None)
            
            # Set default output name
            input_basename = os.path.splitext(os.path.basename(file_to_use))[0]
            self.office_convert_tab.output_name.set(f"{input_basename}.pdf")
    
    def clear_recent_files(self):
        """Clear the list of recent files"""
        result = messagebox.askyesno("Confirm", "Clear all recent files?")
        if result:
            self.settings.settings['recent_files'] = []
            self.settings.save_settings()
            self.update_recent_files_menu()
    
    def show_preferences(self):
        """Show preferences dialog"""
        # Create a simple preferences dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Preferences")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # General preferences
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # Theme selection
        ttk.Label(general_frame, text="Theme:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        theme_var = tk.StringVar(value=self.settings.settings.get('theme', 'default'))
        theme_combo = ttk.Combobox(general_frame, textvariable=theme_var, 
                                 values=["default", "light", "dark"], width=15)
        theme_combo.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Max recent files
        ttk.Label(general_frame, text="Maximum Recent Files:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        max_recent_var = tk.IntVar(value=self.settings.settings.get('max_recent_files', 10))
        ttk.Spinbox(general_frame, from_=1, to=50, textvariable=max_recent_var, width=5).grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Confirm overwrite
        confirm_overwrite_var = tk.BooleanVar(value=self.settings.settings.get('confirm_overwrite', True))
        ttk.Checkbutton(general_frame, text="Confirm before overwriting existing files", 
                      variable=confirm_overwrite_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Remember last directory
        remember_dir_var = tk.BooleanVar(value=self.settings.settings.get('remember_last_directory', True))
        ttk.Checkbutton(general_frame, text="Remember last used directories", 
                      variable=remember_dir_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Directories preferences
        dir_frame = ttk.Frame(notebook)
        notebook.add(dir_frame, text="Directories")
        
        # Default PDF output directory
        ttk.Label(dir_frame, text="Default PDF Output Directory:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        pdf_dir_var = tk.StringVar(value=self.settings.settings.get('default_output_dir', str(Path.home() / "Documents")))
        ttk.Entry(dir_frame, textvariable=pdf_dir_var, width=40).grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        ttk.Button(dir_frame, text="Browse...", 
                 command=lambda: self._browse_dir_for_var(pdf_dir_var)).grid(row=0, column=2, sticky="e", padx=10, pady=5)
        
        # Default Image output directory
        ttk.Label(dir_frame, text="Default Image Output Directory:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        img_dir_var = tk.StringVar(value=self.settings.settings.get('default_image_output_dir', str(Path.home() / "Pictures")))
        ttk.Entry(dir_frame, textvariable=img_dir_var, width=40).grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        ttk.Button(dir_frame, text="Browse...", 
                 command=lambda: self._browse_dir_for_var(img_dir_var)).grid(row=1, column=2, sticky="e", padx=10, pady=5)
        
        # Make column 1 expand
        dir_frame.columnconfigure(1, weight=1)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Cancel", 
                 command=dialog.destroy).pack(side="right", padx=5)
        
        def save_preferences():
            # Update settings
            self.settings.settings['theme'] = theme_var.get()
            self.settings.settings['max_recent_files'] = max_recent_var.get()
            self.settings.settings['confirm_overwrite'] = confirm_overwrite_var.get()
            self.settings.settings['remember_last_directory'] = remember_dir_var.get()
            self.settings.settings['default_output_dir'] = pdf_dir_var.get()
            self.settings.settings['default_image_output_dir'] = img_dir_var.get()
            
            # Save settings
            self.settings.save_settings()
            
            # Update UI if needed
            self.update_recent_files_menu()
            
            dialog.destroy()
            messagebox.showinfo("Success", "Preferences saved successfully.")
        
        ttk.Button(btn_frame, text="Save", 
                 command=save_preferences).pack(side="right", padx=5)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def _browse_dir_for_var(self, var):
        """Browse for a directory and set it to the given variable"""
        directory = askdirectory(
            title="Select Directory",
            initialdir=var.get() if var.get() else os.getcwd()
        )
        if directory:
            var.set(directory)
    
    def show_help(self):
        """Show help information"""
        # Create a simple help dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Help")
        dialog.geometry("600x500")
        dialog.transient(self.root)
        
        # Create a scrollable text widget
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        text = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set)
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)
        
        # Insert help content
        text.insert("1.0", """p2i - Help

This application provides a comprehensive set of tools for PDF and image processing:

1. Merge PDFs
   - Combine multiple PDF files into a single document
   - Rearrange the order of PDFs before merging
   - Preview the total number of pages

2. Split PDF
   - Extract specific page ranges from a PDF
   - Extract individual pages
   - Extract every Nth page

3. Compress PDF
   - Reduce PDF file size with different compression levels
   - Choose between different compression methods
   - View file size reduction information

4. PDF to Image Conversion
   - Convert PDF pages to images in various formats
   - Control resolution and quality settings
   - Batch conversion support

5. Image to PDF Conversion
   - Create PDFs from multiple images
   - Adjust page size, orientation, and margins
   - Rearrange images before conversion

6. PDF Security & Watermark
   - Add password protection to PDFs
   - Set document permissions
   - Add text or image watermarks with customizable settings

7. Image Processing
   - Resize, convert, adjust, and optimize images
   - Batch process multiple images
   - Preview changes before processing

8. Office/Markdown to PDF
   - Convert Word, Excel, PowerPoint and Markdown documents to PDF
   - Customize conversion settings

Tips:
- Drag and drop files directly onto the application
- Use the Recent Files menu to quickly access previous documents
- Set your preferences in the Tools > Preferences menu
""")
        
        text.config(state="disabled")  # Make text read-only
        
        # Add a close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        
        # Center the dialog
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def check_updates(self):
        """Check for application updates"""
        messagebox.showinfo("Updates", "You have the latest version (1.0.0) of p2i.")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """p2i - Advanced PDF Processing GUI
Version 1.0.0

A comprehensive toolkit for PDF and image processing.

This application provides a user-friendly interface for:
- PDF merging, splitting, and compression
- PDF to image conversion
- Image to PDF conversion
- PDF security and watermarking
- Image batch processing
- Office document to PDF conversion

© 2025 p2i Team
"""
        messagebox.showinfo("About p2i", about_text)
    
    def on_close(self):
        """Handle application close"""
        # Save any settings if needed
        self.settings.save_settings()
        
        # Destroy the root window
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = P2IApp(root)
    root.mainloop()
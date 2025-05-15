# main.py
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, askdirectory
import multiprocessing
from pathlib import Path 

# Import all tab modules
from pdf_merge_tab import PDFMergeTab
from pdf_split_tab import PDFSplitTab
from pdf_compress_tab import PDFCompressTab
from pdf_to_image_tab import PDFToImageTab
from image_to_pdf_tab import ImageToPDFTab
from pdf_security_tab import PDFSecurityTab
from image_batch_tab import ImageBatchTab
from pdf_organizer_tab import PDFOrganizerTab
from contribute_dialog import show_contribute_dialog
from support_tab import SupportTab
#from office_convert_tab import OfficeConvertTab

# Import settings and drag drop
from settings import Settings
from drag_drop import DragDropManager

class P2IApp:
    def __init__(self, root):
        self.root = root
        self.root.title("p2i - PDF & Image Processing Tool")
        self.root.geometry("900x700")

        # Handle resource paths differently when running as script vs executable
        if getattr(sys, 'frozen', False):
            # Running as executable
            application_path = sys._MEIPASS
        else:
            # Running as script
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        # Platform-specific icon handling
        if os.name == 'nt':  # Windows
            # Try both locations for the icon
            icon_path = os.path.join(application_path, "resources", "icon", "app_icon.ico")
            if not os.path.exists(icon_path):
                # Try the root ico file as fallback
                icon_path = os.path.join(application_path, "p2i.ico")
            
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                except Exception as e:
                    print(f"Could not load icon: {e}")
            else:
                print(f"Icon not found at: {icon_path}")
        else:  # Linux/Mac
            try:
                # For Linux/Mac, try PNG format
                icon_path = os.path.join(application_path, "resources", "icon", "app_icon.png")
                if os.path.exists(icon_path):
                    img = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, img)
                else:
                    print(f"Icon not found at: {icon_path}")
            except Exception as e:
                print(f"Could not load icon: {e}")
        
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
        self.pdf_organizer_tab = PDFOrganizerTab(self.notebook)
        self.support_tab = SupportTab(self.notebook)
        #self.office_convert_tab = OfficeConvertTab(self.notebook)
        
        # Add tabs to notebook
        self.notebook.add(self.pdf_merge_tab.frame, text="Merge PDFs")
        self.notebook.add(self.pdf_split_tab.frame, text="Split PDF")
        self.notebook.add(self.pdf_compress_tab.frame, text="Compress PDF")
        self.notebook.add(self.pdf_to_image_tab.frame, text="PDF to Image")
        self.notebook.add(self.image_to_pdf_tab.frame, text="Image to PDF")
        self.notebook.add(self.pdf_security_tab.frame, text="PDF Security")
        self.notebook.add(self.image_batch_tab.frame, text="Image Processing")
        self.notebook.add(self.pdf_organizer_tab.frame, text="PDF Organizer")
        self.notebook.add(self.support_tab.frame, text="Support p2i")
        #self.notebook.add(self.office_convert_tab.frame, text="Office/Markdown to PDF")
        
        # Create main menu
        self.create_menu()

        self.apply_settings()
        
        # Set up drag and drop
        self.setup_drag_drop()
        
        # Handle application close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def set_app_icon(self):
        # Try to set the icon based on the platform
        if os.name == 'nt':  # Windows
            icon_path = os.path.join("resources", "icon", "app_icon.ico")
            if os.path.exists(icon_path):
                try:
                    self.root.iconbitmap(icon_path)
                except Exception as e:
                    print(f"Could not load Windows icon: {e}")
                    # Try to use ico file from root as fallback
                    if os.path.exists("p2i.ico"):
                        try:
                            self.root.iconbitmap("p2i.ico")
                        except Exception as e:
                            print(f"Could not load fallback icon: {e}")
        else:  # Linux/Mac
            # For Linux we need to use PhotoImage instead of iconbitmap
            try:
                # Try PNG first (commonly used in Linux)
                icon_path = os.path.join("resources", "icon", "app_icon.png")
                if not os.path.exists(icon_path):
                    # If PNG doesn't exist, try to find other formats
                    for ext in ['.png']:#, '.gif', '.ppm', '.xbm']:
                        alt_path = os.path.join("resources", "icon", f"app_icon{ext}")
                        if os.path.exists(alt_path):
                            icon_path = alt_path
                            break
                
                if os.path.exists(icon_path):
                    icon_img = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, icon_img)
                else:
                    print("No suitable icon found for this platform")
            except Exception as e:
                print(f"Could not load icon for Linux/Mac: {e}")
                
    def setup_drag_drop(self):
        """Set up drag and drop functionality"""
        # Create list of widgets to receive dropped files
        drop_targets = [
            self.pdf_merge_tab.frame,
            self.pdf_split_tab.frame,
            self.pdf_organizer_tab.frame,
            self.pdf_compress_tab.frame,
            self.pdf_security_tab.frame,
            self.pdf_to_image_tab.frame,
            self.image_to_pdf_tab.frame,
            self.image_batch_tab.frame,
            self.support_tab.frame
            #self.office_convert_tab.frame
        ]
        
        # Initialize drag-drop manager
        self.dnd_manager = DragDropManager(self.root, self.settings, drop_targets)
        
        # Show a status message about drag and drop availability
        if not self.dnd_manager.is_available():
            print("TkinterDnD not available. Drag and drop disabled.")
            # You could also show this in the UI
            self.status_bar = ttk.Label(self.root, text="Drag and Drop disabled. Install tkinterdnd2 to enable this feature.")
            self.status_bar.pack(side="bottom", fill="x", padx=5, pady=2)
        else:
            print("Drag and Drop enabled")
            # Optional: show enabled status
            self.status_bar = ttk.Label(self.root, text="Drag and Drop enabled")
            self.status_bar.pack(side="bottom", fill="x", padx=5, pady=2)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open PDF...", command=self.open_pdf)
        file_menu.add_command(label="Open Image...", command=self.open_image)
        # file_menu.add_command(label="Open Office Document...", command=self.open_office_doc)
        
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
        
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Help", command=self.show_help)
        help_menu.add_command(label="Check for Updates", command=self.check_updates)
        help_menu.add_separator()
        help_menu.add_command(label="Contribute to p2i", command=lambda: show_contribute_dialog(self.root))
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
            #self.office_convert_tab.frame
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
    '''
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
    '''
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
        # elif ext in [".docx", ".xlsx", ".pptx", ".doc", ".xls", ".ppt", ".md", ".txt"]:
        #     # For office documents
        #     self.open_office_doc()
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
        # elif current_tab_idx == 7 and (office_files or pdf_files):  # Office/Markdown to PDF tab
        #     file_to_use = office_files[0] if office_files else pdf_files[0]
        #     self.office_convert_tab.input_path.set(file_to_use)
            
        #     # Set file type based on extension
        #     ext = os.path.splitext(file_to_use)[1].lower()
        #     if ext in [".docx", ".doc"]:
        #         self.office_convert_tab.file_type.set("word")
        #     elif ext in [".xlsx", ".xls"]:
        #         self.office_convert_tab.file_type.set("excel")
        #     elif ext in [".pptx", ".ppt"]:
        #         self.office_convert_tab.file_type.set("powerpoint")
        #     elif ext in [".md", ".txt"]:
        #         self.office_convert_tab.file_type.set("markdown")
        #     else:
        #         self.office_convert_tab.file_type.set("auto")
            
        #     # Update visible options
        #     self.office_convert_tab.on_file_type_change(None)
            
        #     # Set default output name
        #     input_basename = os.path.splitext(os.path.basename(file_to_use))[0]
        #     self.office_convert_tab.output_name.set(f"{input_basename}.pdf")
    
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
        
        def save_preferences(self):
            # Update settings
            self.settings.settings['theme'] = theme_var.get()
            self.settings.settings['max_recent_files'] = max_recent_var.get()
            self.settings.settings['confirm_overwrite'] = confirm_overwrite_var.get()
            self.settings.settings['remember_last_directory'] = remember_dir_var.get()
            self.settings.settings['default_output_dir'] = pdf_dir_var.get()
            self.settings.settings['default_image_output_dir'] = img_dir_var.get()
            
            # Save settings
            self.settings.save_settings()
            
            # Apply settings to current application state
            self.apply_settings()
            
            # Update UI if needed
            self.update_recent_files_menu()
            
            dialog.destroy()
            messagebox.showinfo("Success", "Preferences saved successfully.")

    def apply_settings(self):
        """Apply current settings to the application"""
        # Apply theme if changed
        theme = self.settings.settings.get('theme', 'default')
        self._apply_theme(theme)
        
        # Update recent files max limit
        # Already handled by self.update_recent_files_menu()
        
        # Update default directories in each tab that uses them
        default_output_dir = self.settings.settings.get('default_output_dir')
        default_image_dir = self.settings.settings.get('default_image_output_dir')
        
        # Only update if the directory exists
        if default_output_dir and os.path.isdir(default_output_dir):
            # Update output directory in PDF-related tabs
            tabs_with_pdf_output = [
                self.pdf_merge_tab,
                self.pdf_split_tab,
                self.pdf_compress_tab,
                self.pdf_security_tab,
                #self.office_convert_tab
            ]
            for tab in tabs_with_pdf_output:
                if hasattr(tab, 'output_dir') and not tab.output_dir.get():
                    tab.output_dir.set(default_output_dir)
        
        if default_image_dir and os.path.isdir(default_image_dir):
            # Update output directory in image-related tabs
            tabs_with_image_output = [
                self.pdf_to_image_tab,
                self.image_batch_tab
            ]
            for tab in tabs_with_image_output:
                if hasattr(tab, 'output_dir') and not tab.output_dir.get():
                    tab.output_dir.set(default_image_dir)

    def _apply_theme(self, theme_name):
        """Apply the selected theme to the application"""
        if theme_name == 'default':
            style = ttk.Style()
            style.theme_use('default')
        elif theme_name == 'light':
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('.', background='#f0f0f0')
            style.configure('TFrame', background='#f0f0f0')
            style.configure('TLabel', background='#f0f0f0')
            style.configure('TLabelframe', background='#f0f0f0')
            style.configure('TLabelframe.Label', background='#f0f0f0')
        elif theme_name == 'dark':
            style = ttk.Style()
            style.theme_use('clam')
            style.configure('.', background='#2d2d2d', foreground='#ffffff')
            style.configure('TFrame', background='#2d2d2d')
            style.configure('TLabel', background='#2d2d2d', foreground='#ffffff')
            style.configure('TLabelframe', background='#2d2d2d')
            style.configure('TLabelframe.Label', background='#2d2d2d', foreground='#ffffff')
            style.configure('TButton', background='#444444', foreground='#ffffff')
            style.map('TButton', background=[('active', '#555555')])
            style.configure('TEntry', fieldbackground='#444444', foreground='#ffffff')
            style.configure('TCombobox', fieldbackground='#444444', foreground='#ffffff')
            style.configure('Horizontal.TProgressbar', background='#0088cc')
    
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

        help_text = """p2i - PDF & Image Processing Tool - User Guide

                    QUICK START
                    - Use the tabs at the top to select different tools
                    - For most operations: select input file(s), set options, choose output location, click Process/Convert button
                    - Drag and drop files directly onto any tab for quicker workflow

                    PDF TOOLS

                    1. Merge PDFs
                    • Click "Add PDFs" to select multiple PDF files
                    • Reorder them using Move Up/Down buttons
                    • Set output location and filename
                    • Click "Merge PDFs" to combine them into a single document

                    2. Split PDF
                    • Select a PDF file to split
                    • Choose split mode:
                        - Page Range: Extract a specific range of pages
                        - Single Pages: Extract specific page numbers (e.g., 1,3,5-7)
                        - Extract Every N Pages: Take every Nth page
                    • Set output location
                    • Click "Split PDF" to create new PDF(s)

                    3. Compress PDF
                    • Select a PDF to compress
                    • Choose compression level (low, medium, high)
                    • Select compression method:
                        - Auto: Analyzes content and chooses best method
                        - Image-based: Best for documents with many images
                        - Direct: Best for text-heavy documents
                    • Click "Compress PDF" to reduce file size

                    4. PDF to Image
                    • Select a PDF to convert to images
                    • Set page range, DPI, and image format
                    • Use "Preview" to see how the output will look
                    • For multiple PDFs, check "Batch Mode"
                    • Click "Convert PDF to Images" to process

                    5. Image to PDF
                    • Click "Add Images" to select images to combine
                    • Reorder them using Move Up/Down buttons
                    • Set page size, orientation, and margins
                    • Click "Create PDF from Images" to convert

                    6. PDF Security
                    • Select a PDF file
                    • For password protection:
                        - Check "Enable Password Protection"
                        - Set owner and/or user passwords
                        - Configure permissions (printing, copying, etc.)
                    • For watermarking:
                        - Check "Add Watermark"
                        - Choose text or image watermark
                        - Set position, opacity, and rotation
                    • Click "Process PDF" to apply changes

                    IMAGE TOOLS

                    7. Image Processing
                    • Select input directory containing images
                    • Choose operation type:
                        - Resize: Change dimensions using various methods
                        - Convert: Change image format with quality options
                        - Adjust: Modify brightness, contrast, filters
                        - Optimize: Reduce file size for web/sharing
                    • Preview changes on sample image
                    • Click "Process Images" to batch process all images

                    8. Office/Markdown to PDF
                    • Select Office document (Word, Excel, PowerPoint) or Markdown file
                    • Set conversion options specific to the file type
                    • Choose output location and filename
                    • Click "Convert to PDF" to transform document

                    TIPS
                    - Use the "Preview" feature where available to check results before processing
                    - For batch operations, check file pattern settings to ensure all files are included
                    - Right-click lists to access context menus for additional options
                    - Check the status bar at the bottom for operation progress
                    - If conversion fails, try different settings or check file permissions
                    """

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
        text.insert("1.0", help_text)
        
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

def main():
    root = tk.Tk()
    app = P2IApp(root)
    root.mainloop()
    
if __name__ == "__main__":
    main()

# office_convert_tab.py
import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import utils

class OfficeConvertTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Variables
        self.input_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_name = tk.StringVar(value="converted.pdf")
        self.file_type = tk.StringVar(value="auto")  # auto, word, excel, powerpoint, markdown
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.conversion_canceled = False
        
        # Markdown specific options
        self.markdown_css = tk.StringVar()
        self.markdown_toc = tk.BooleanVar(value=True)
        self.markdown_numbered_headings = tk.BooleanVar(value=False)
        
        # Word specific options
        self.word_include_bookmarks = tk.BooleanVar(value=True)
        self.word_embed_fonts = tk.BooleanVar(value=True)
        
        # Create UI elements
        self.create_file_frame()
        self.create_options_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame, 
            self.start_conversion, 
            self.cancel_conversion, 
            self.open_output_folder,
            "Convert to PDF"
        )
        
        # Set default output directory to user's Documents folder
        default_output = os.path.join(str(Path.home()), "Documents")
        self.output_dir.set(default_output)
        
        # Check for required dependencies
        self.check_dependencies()
    
    def create_file_frame(self):
        file_frame = ttk.LabelFrame(self.frame, text="File Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Input file selection
        ttk.Label(file_frame, text="Input File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_input).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Output directory selection
        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=2, sticky="e", padx=5, pady=5)
        
        # Output filename
        ttk.Label(file_frame, text="Output Filename:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_name, width=50).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        
        # File type selection
        ttk.Label(file_frame, text="File Type:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        file_types = ttk.Combobox(file_frame, textvariable=self.file_type, 
                               values=["auto", "word", "excel", "powerpoint", "markdown"])
        file_types.grid(row=3, column=1, sticky="w", padx=5, pady=5)
        file_types.bind("<<ComboboxSelected>>", self.on_file_type_change)
        
        # Make column 1 expand
        file_frame.columnconfigure(1, weight=1)
    
    def create_options_frame(self):
        self.options_frame = ttk.LabelFrame(self.frame, text="Conversion Options", padding=10)
        self.options_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Create options frames for each file type
        self.create_markdown_options()
        self.create_word_options()
        self.create_excel_options()
        self.create_powerpoint_options()
        
        # Initially hide all option frames
        self.markdown_options.pack_forget()
        self.word_options.pack_forget()
        self.excel_options.pack_forget()
        self.powerpoint_options.pack_forget()
    
    def create_markdown_options(self):
        self.markdown_options = ttk.Frame(self.options_frame)
        
        # CSS stylesheet
        ttk.Label(self.markdown_options, text="CSS Stylesheet (optional):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(self.markdown_options, textvariable=self.markdown_css, width=40).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(self.markdown_options, text="Browse...", command=self.browse_css).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Table of contents
        ttk.Checkbutton(self.markdown_options, text="Generate Table of Contents", 
                      variable=self.markdown_toc).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Numbered headings
        ttk.Checkbutton(self.markdown_options, text="Numbered Headings", 
                      variable=self.markdown_numbered_headings).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        
        # Make column 1 expand
        self.markdown_options.columnconfigure(1, weight=1)
    
    def create_word_options(self):
        self.word_options = ttk.Frame(self.options_frame)
        
        # Bookmarks
        ttk.Checkbutton(self.word_options, text="Include Bookmarks", 
                      variable=self.word_include_bookmarks).pack(anchor="w", padx=5, pady=5)
        
        # Embed fonts
        ttk.Checkbutton(self.word_options, text="Embed Fonts", 
                      variable=self.word_embed_fonts).pack(anchor="w", padx=5, pady=5)
    
    def create_excel_options(self):
        self.excel_options = ttk.Frame(self.options_frame)
        
        # For now, no special Excel options
        ttk.Label(self.excel_options, text="Excel to PDF conversion uses default settings").pack(padx=5, pady=10)
    
    def create_powerpoint_options(self):
        self.powerpoint_options = ttk.Frame(self.options_frame)
        
        # For now, no special PowerPoint options
        ttk.Label(self.powerpoint_options, text="PowerPoint to PDF conversion uses default settings").pack(padx=5, pady=10)
    
    def check_dependencies(self):
        """Check if required conversion tools are installed"""
        self.have_libreoffice = self._check_command(["libreoffice", "--version"])
        self.have_pandoc = self._check_command(["pandoc", "--version"])
        
        # Show warnings if dependencies are missing
        warning_text = ""
        
        if not self.have_libreoffice:
            warning_text += "LibreOffice not found. Office document conversion may not work.\n"
        
        if not self.have_pandoc:
            warning_text += "Pandoc not found. Markdown conversion may not work.\n"
        
        if warning_text:
            warning_text += "\nPlease install missing dependencies for full functionality."
            self.status_var.set("Warning: Some dependencies missing")
            messagebox.showwarning("Missing Dependencies", warning_text)
    
    def _check_command(self, command):
        """Check if a command is available"""
        try:
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def on_file_type_change(self, event):
        """Show appropriate options frame based on selected file type"""
        file_type = self.file_type.get()
        
        # Hide all option frames
        self.markdown_options.pack_forget()
        self.word_options.pack_forget()
        self.excel_options.pack_forget()
        self.powerpoint_options.pack_forget()
        
        # Show appropriate frame
        if file_type == "markdown":
            self.markdown_options.pack(fill="x", expand=True, padx=5, pady=5)
        elif file_type == "word":
            self.word_options.pack(fill="x", expand=True, padx=5, pady=5)
        elif file_type == "excel":
            self.excel_options.pack(fill="x", expand=True, padx=5, pady=5)
        elif file_type == "powerpoint":
            self.powerpoint_options.pack(fill="x", expand=True, padx=5, pady=5)
    
    def browse_input(self):
        file_type = self.file_type.get()
        filetypes = [("All Files", "*.*")]
        
        if file_type == "auto":
            filetypes = [
                ("Office & Markdown Files", "*.docx *.xlsx *.pptx *.doc *.xls *.ppt *.md *.markdown *.txt"),
                ("Word Documents", "*.docx *.doc"),
                ("Excel Workbooks", "*.xlsx *.xls"),
                ("PowerPoint Presentations", "*.pptx *.ppt"),
                ("Markdown Files", "*.md *.markdown *.txt"),
                ("All Files", "*.*")
            ]
        elif file_type == "word":
            filetypes = [
                ("Word Documents", "*.docx *.doc"),
                ("All Files", "*.*")
            ]
        elif file_type == "excel":
            filetypes = [
                ("Excel Workbooks", "*.xlsx *.xls"),
                ("All Files", "*.*")
            ]
        elif file_type == "powerpoint":
            filetypes = [
                ("PowerPoint Presentations", "*.pptx *.ppt"),
                ("All Files", "*.*")
            ]
        elif file_type == "markdown":
            filetypes = [
                ("Markdown Files", "*.md *.markdown *.txt"),
                ("All Files", "*.*")
            ]
        
        selected_file = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=filetypes
        )
        
        if selected_file:
            self.input_path.set(selected_file)
            
            # Set file type based on extension if on auto
            if self.file_type.get() == "auto":
                ext = os.path.splitext(selected_file)[1].lower()
                if ext in [".docx", ".doc"]:
                    self.file_type.set("word")
                elif ext in [".xlsx", ".xls"]:
                    self.file_type.set("excel")
                elif ext in [".pptx", ".ppt"]:
                    self.file_type.set("powerpoint")
                elif ext in [".md", ".markdown", ".txt"]:
                    self.file_type.set("markdown")
                
                # Update visible options
                self.on_file_type_change(None)
            
            # Set default output name based on input filename
            input_basename = os.path.splitext(os.path.basename(selected_file))[0]
            self.output_name.set(f"{input_basename}.pdf")
            
            self.status_var.set(f"Selected file: {os.path.basename(selected_file)}")
    
    def browse_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)
    
    def browse_css(self):
        selected_file = filedialog.askopenfilename(
            title="Select CSS Stylesheet",
            filetypes=[("CSS Files", "*.css"), ("All Files", "*.*")]
        )
        if selected_file:
            self.markdown_css.set(selected_file)
    
    def start_conversion(self):
        if not self.input_path.get() or not os.path.isfile(self.input_path.get()):
            messagebox.showerror("Error", "Please select a valid input file.")
            return
        
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please specify an output directory.")
            return
        
        if not self.output_name.get():
            messagebox.showerror("Error", "Please enter a name for the output PDF file.")
            return
            
        # Create output directory if it doesn't exist
        if not os.path.exists(self.output_dir.get()):
            try:
                os.makedirs(self.output_dir.get())
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create output directory: {str(e)}")
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
        
        # Disable controls during conversion
        utils.set_controls_state(self.frame, tk.DISABLED)
        
        # Start conversion in a separate thread
        self.conversion_canceled = False
        threading.Thread(target=self._conversion_thread, args=(output_path,)).start()
    
    def _conversion_thread(self, output_path):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Converting to PDF..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(10))
            
            file_type = self.file_type.get()
            input_path = self.input_path.get()
            
            # Determine file type if auto
            if file_type == "auto":
                ext = os.path.splitext(input_path)[1].lower()
                if ext in [".docx", ".doc"]:
                    file_type = "word"
                elif ext in [".xlsx", ".xls"]:
                    file_type = "excel"
                elif ext in [".pptx", ".ppt"]:
                    file_type = "powerpoint"
                elif ext in [".md", ".markdown", ".txt"]:
                    file_type = "markdown"
                else:
                    self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror(
                        "Error", "Could not determine file type. Please specify manually."))
                    return
            
            # Convert based on file type
            if file_type == "markdown":
                success = self._convert_markdown(input_path, output_path)
            else:  # Office formats
                success = self._convert_office(input_path, output_path, file_type)
            
            if self.conversion_canceled:
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Conversion canceled"))
                # Delete partial output
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except:
                        pass
                return
            
            if success:
                # Complete
                self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Conversion complete: {os.path.basename(output_path)}"))
                self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", 
                    f"File converted successfully.\nSaved to: {output_path}"))
            else:
                self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", 
                    "Conversion failed. Please check that appropriate conversion tools are installed."))
            
        except Exception as e:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Conversion failed: {str(e)}"))
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
    
    def _convert_markdown(self, input_path, output_path):
        """Convert Markdown to PDF using Pandoc"""
        if not self.have_pandoc:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", 
                "Pandoc is required for Markdown conversion but was not found."))
            return False
        
        self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Converting Markdown to PDF..."))
        self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(30))
        
        # Build Pandoc command
        cmd = ["pandoc", input_path, "-o", output_path]
        
        # Add options
        if self.markdown_toc.get():
            cmd.extend(["--toc"])
        
        if self.markdown_numbered_headings.get():
            cmd.extend(["--number-sections"])
        
        if self.markdown_css.get() and os.path.isfile(self.markdown_css.get()):
            cmd.extend(["--css", self.markdown_css.get()])
        
        # Run Pandoc
        # Continuing office_convert_tab.py from where we left off

        # Run Pandoc
        self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Running Pandoc..."))
        self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(50))
        
        try:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(90))
            return True
        except subprocess.CalledProcessError as e:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Pandoc error: {e.stderr.decode('utf-8')}"))
            return False
    
    def _convert_office(self, input_path, output_path, file_type):
        """Convert Office formats to PDF using LibreOffice"""
        if not self.have_libreoffice:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", 
                "LibreOffice is required for Office conversion but was not found."))
            return False
        
        file_type_name = {
            "word": "Word document",
            "excel": "Excel spreadsheet",
            "powerpoint": "PowerPoint presentation"
        }.get(file_type, "Office document")
        
        self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Converting {file_type_name} to PDF..."))
        self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(30))
        
        # Get output directory
        output_dir = os.path.dirname(output_path)
        
        # Build LibreOffice command
        # Use --convert-to to output to same directory, then move the file
        cmd = [
            "libreoffice", "--headless", "--convert-to", "pdf",
            "--outdir", output_dir, input_path
        ]
        
        # Run LibreOffice
        self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Running LibreOffice..."))
        self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(50))
        
        try:
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            
            # LibreOffice creates the PDF with the same base name as input
            # We need to rename it to our target filename
            input_basename = os.path.splitext(os.path.basename(input_path))[0]
            temp_pdf_path = os.path.join(output_dir, f"{input_basename}.pdf")
            
            if os.path.exists(temp_pdf_path) and temp_pdf_path != output_path:
                os.replace(temp_pdf_path, output_path)
            
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(90))
            return True
        except subprocess.CalledProcessError as e:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"LibreOffice error: {e.stderr.decode('utf-8')}"))
            return False
    
    def cancel_conversion(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling conversion...")
    
    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())
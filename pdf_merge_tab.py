import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pypdfium2 as pdfium
import utils

class PDFMergeTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Variables
        self.pdf_paths = []
        self.output_dir = tk.StringVar()
        self.output_name = tk.StringVar(value="merged.pdf")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.selected_index = 0
        self.conversion_canceled = False
        
        # Create UI elements
        self.create_file_frame()
        self.create_info_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame, 
            self.start_merge, 
            self.cancel_merge, 
            self.open_output_folder,
            "Merge PDFs"
        )
        
        # Set default output directory to user's Documents folder
        default_output = os.path.join(str(Path.home()), "Documents")
        self.output_dir.set(default_output)
    
    def create_file_frame(self):
        file_frame = ttk.LabelFrame(self.frame, text="PDF Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(file_frame)
        btn_frame.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add PDFs", command=self.add_pdfs).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_selected_pdf).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_pdfs).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Move Up", command=self.move_pdf_up).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Move Down", command=self.move_pdf_down).pack(side="left", padx=5)
        
        # List of PDFs
        list_frame = ttk.Frame(file_frame)
        list_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # Listbox with PDFs
        self.pdf_listbox = tk.Listbox(list_frame, height=10, width=60, yscrollcommand=scrollbar.set)
        self.pdf_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.pdf_listbox.yview)
        
        # Bind selection event
        self.pdf_listbox.bind('<<ListboxSelect>>', self.on_pdf_select)
        
        # Output settings
        ttk.Label(file_frame, text="Output Directory:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=2, column=2, sticky="e", padx=5, pady=5)
        
        ttk.Label(file_frame, text="Output Filename:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_name, width=50).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        
        # Make rows and columns expand
        file_frame.rowconfigure(1, weight=1)
        file_frame.columnconfigure(1, weight=1)
    
    def create_info_frame(self):
        info_frame = ttk.LabelFrame(self.frame, text="Merge Information", padding=10)
        info_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        # Display selected PDF count and total pages
        self.info_label = ttk.Label(info_frame, text="Selected PDFs: 0 | Total Pages: 0")
        self.info_label.pack(fill="x", expand=True, padx=5, pady=5)
    
    def add_pdfs(self):
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if file_paths:
            for path in file_paths:
                self.pdf_paths.append(path)
                self.pdf_listbox.insert(tk.END, os.path.basename(path))
            
            self.status_var.set(f"Added {len(file_paths)} PDFs. Total: {len(self.pdf_paths)}")
            self.update_info_label()
            
            # Select the first PDF if none selected
            if len(self.pdf_paths) == len(file_paths):
                self.pdf_listbox.selection_set(0)
                self.on_pdf_select(None)
    
    def remove_selected_pdf(self):
        selected_indices = self.pdf_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a PDF to remove")
            return
            
        # Remove in reverse order to avoid index shifting
        for index in sorted(selected_indices, reverse=True):
            self.pdf_listbox.delete(index)
            del self.pdf_paths[index]
        
        self.status_var.set(f"Removed {len(selected_indices)} PDFs. Total: {len(self.pdf_paths)}")
        self.update_info_label()
        
        # Update preview if needed
        if self.pdf_paths and self.selected_index >= len(self.pdf_paths):
            self.selected_index = len(self.pdf_paths) - 1
            self.pdf_listbox.selection_set(self.selected_index)
    
    def clear_pdfs(self):
        if not self.pdf_paths:
            return
            
        result = messagebox.askyesno("Confirm", "Are you sure you want to clear all PDFs?")
        if result:
            self.pdf_listbox.delete(0, tk.END)
            self.pdf_paths.clear()
            self.selected_index = 0
            self.status_var.set("All PDFs cleared")
            self.update_info_label()
    
    def move_pdf_up(self):
        selected_indices = self.pdf_listbox.curselection()
        if not selected_indices or selected_indices[0] == 0:
            return
            
        index = selected_indices[0]
        # Swap in paths list
        self.pdf_paths[index], self.pdf_paths[index-1] = self.pdf_paths[index-1], self.pdf_paths[index]
        
        # Update listbox
        self.pdf_listbox.delete(index-1, index)
        self.pdf_listbox.insert(index-1, os.path.basename(self.pdf_paths[index-1]))
        self.pdf_listbox.insert(index, os.path.basename(self.pdf_paths[index]))
        
        # Reselect the moved item
        self.pdf_listbox.selection_clear(0, tk.END)
        self.pdf_listbox.selection_set(index-1)
        self.selected_index = index-1
        
        self.status_var.set(f"Moved PDF up: {os.path.basename(self.pdf_paths[index-1])}")
    
    def move_pdf_down(self):
        selected_indices = self.pdf_listbox.curselection()
        if not selected_indices or selected_indices[0] == len(self.pdf_paths) - 1:
            return
            
        index = selected_indices[0]
        # Swap in paths list
        self.pdf_paths[index], self.pdf_paths[index+1] = self.pdf_paths[index+1], self.pdf_paths[index]
        
        # Update listbox
        self.pdf_listbox.delete(index, index+1)
        self.pdf_listbox.insert(index, os.path.basename(self.pdf_paths[index]))
        self.pdf_listbox.insert(index+1, os.path.basename(self.pdf_paths[index+1]))
        
        # Reselect the moved item
        self.pdf_listbox.selection_clear(0, tk.END)
        self.pdf_listbox.selection_set(index+1)
        self.selected_index = index+1
        
        self.status_var.set(f"Moved PDF down: {os.path.basename(self.pdf_paths[index+1])}")
    
    def on_pdf_select(self, event):
        selected_indices = self.pdf_listbox.curselection()
        if selected_indices:
            self.selected_index = selected_indices[0]
    
    def browse_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)
    
    def update_info_label(self):
        """Update the information label with PDF count and total pages"""
        if not self.pdf_paths:
            self.info_label.config(text="Selected PDFs: 0 | Total Pages: 0")
            return
            
        # Count pages in all PDFs
        threading.Thread(target=self._count_pages_thread).start()
    
    def _count_pages_thread(self):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Counting pages..."))
            
            total_pages = 0
            for pdf_path in self.pdf_paths:
                try:
                    pdf = pdfium.PdfDocument(pdf_path)
                    total_pages += len(pdf)
                except Exception as e:
                    # If we can't open a PDF, just skip it in the count
                    continue
            
            self.frame.winfo_toplevel().after(0, lambda: self.info_label.config(
                text=f"Selected PDFs: {len(self.pdf_paths)} | Total Pages: {total_pages}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Page count complete"))
        except Exception as e:
            error_msg = str(e)
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error counting pages: {error_msg}"))
    
    def start_merge(self):
        if not self.pdf_paths:
            messagebox.showerror("Error", "Please add at least one PDF to merge")
            return
            
        if len(self.pdf_paths) < 2:
            messagebox.showerror("Error", "Please add at least two PDFs to merge")
            return
            
        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory")
            return
            
        if not self.output_name.get():
            messagebox.showerror("Error", "Please enter a name for the output PDF file")
            return
            
        # Add .pdf extension if not present
        pdf_filename = self.output_name.get()
        if not pdf_filename.lower().endswith('.pdf'):
            pdf_filename += ".pdf"
            
        output_path = os.path.join(self.output_dir.get(), pdf_filename)
        
        # Confirm if file exists
        if os.path.exists(output_path):
            result = messagebox.askyesno("Confirm", f"File {pdf_filename} already exists. Overwrite?")
            if not result:
                return
                
        # Disable controls during merging
        utils.set_controls_state(self.frame, tk.DISABLED)
        
        # Start merging in a separate thread
        self.conversion_canceled = False
        threading.Thread(target=self._merge_thread, args=(output_path,)).start()
    
    def _merge_thread(self, output_path):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Merging PDFs..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
            # Create a new PDF document to contain the merged result
            merger = pdfium.PdfDocument.new()
            
            # Process each PDF
            total_pdfs = len(self.pdf_paths)
            for i, pdf_path in enumerate(self.pdf_paths):
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Merging canceled"))
                    # Delete partial output
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
                    return
                
                # Update progress
                progress_pct = ((i + 1) / total_pdfs) * 100
                current_file = os.path.basename(pdf_path)
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=i+1, t=total_pdfs, f=current_file: 
                    self.status_var.set(f"Processing {p}/{t}: {f}"))
                
                # Open source PDF
                try:
                    pdf = pdfium.PdfDocument(pdf_path)
                    
                    # Import all pages from this PDF
                    # Use the correct method for importing pages
                    pages = [pdf[page_idx] for page_idx in range(len(pdf))]
                    merger.import_pages(pages)
                except Exception as e:
                    error_msg = str(e)
                    self.frame.winfo_toplevel().after(0, lambda f=current_file, err=error_msg: 
                        messagebox.showwarning("Warning", f"Failed to process {f}: {err}"))
                    continue
            
            # Save the merged PDF
            merger.save(output_path)
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Merge complete: {os.path.basename(output_path)}"))
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", 
                f"PDFs merged successfully.\n{total_pdfs} PDFs combined.\nSaved to: {output_path}"))
            
        except Exception as e:
            error_msg = str(e)
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to merge PDFs: {error_msg}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {error_msg}"))
            # Delete partial output
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
        finally:
            # Re-enable controls
            self.frame.winfo_toplevel().after(0, lambda: utils.set_controls_state(self.frame, tk.NORMAL))
    
    def cancel_merge(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling merge operation...")
    
    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())
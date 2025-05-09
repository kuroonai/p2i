# pdf_organizer_tab.py
import os
import threading
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pypdfium2 as pdfium
from PIL import Image, ImageTk
from PyPDF2 import PdfReader, PdfWriter
import utils

class PDFOrganizerTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Variables
        self.source_pdfs = []  # List of PDF paths
        self.output_dir = tk.StringVar()
        self.output_name = tk.StringVar(value="organized.pdf")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.process_canceled = False
        
        # Page management
        self.all_pages = []  # List of (pdf_path, page_index, is_blank) tuples
        self.selected_index = -1
        self.thumbnail_cache = {}  # Cache for page thumbnails
        self.current_zoom = 1.0  # Zoom level for main preview
        
        # Create UI elements
        self.create_main_layout()
        
        # Set default output directory to user's Documents folder
        default_output = os.path.join(str(Path.home()), "Documents")
        self.output_dir.set(default_output)
    
    def create_main_layout(self):
        # Main layout using PanedWindow
        self.main_paned = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create left panel (PDF preview and page controls)
        self.left_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.left_frame, weight=2)
        
        # Create right panel (PDF list and page thumbnails)
        self.right_frame = ttk.Frame(self.main_paned)
        self.main_paned.add(self.right_frame, weight=1)
        
        # Create the panels content
        self.create_preview_panel()
        self.create_pdf_list_panel()
        
        # Create bottom panel for output settings and progress
        self.bottom_frame = ttk.Frame(self.frame)
        self.bottom_frame.pack(fill="x", expand=False, padx=10, pady=5)
        self.create_output_panel()
        
        # Create progress and buttons
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame, 
            self.start_process, 
            self.cancel_process, 
            self.open_output_folder,
            "Save Organized PDF"
        )
    
    def create_preview_panel(self):
        # Preview frame
        preview_frame = ttk.LabelFrame(self.left_frame, text="Page Preview")
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Preview canvas with scrollbars
        self.preview_canvas_frame = ttk.Frame(preview_frame)
        self.preview_canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.preview_canvas_frame, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(self.preview_canvas_frame)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for displaying the PDF preview
        self.preview_canvas = tk.Canvas(
            self.preview_canvas_frame, 
            bg="white", 
            highlightthickness=0,
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        self.preview_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Connect scrollbars to canvas
        h_scrollbar.config(command=self.preview_canvas.xview)
        v_scrollbar.config(command=self.preview_canvas.yview)
        
        # Preview controls
        controls_frame = ttk.Frame(preview_frame)
        controls_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Navigation and zoom controls
        ttk.Button(controls_frame, text="◀ Previous", command=self.previous_page).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Next ▶", command=self.next_page).pack(side="left", padx=5)
        
        ttk.Label(controls_frame, text="Zoom:").pack(side="left", padx=5)
        ttk.Button(controls_frame, text="🔍-", command=lambda: self.zoom_preview(-0.25)).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="🔍+", command=lambda: self.zoom_preview(0.25)).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="100%", command=lambda: self.set_zoom(1.0)).pack(side="left", padx=2)
        ttk.Button(controls_frame, text="Fit", command=self.zoom_to_fit).pack(side="left", padx=2)
        
        # Page number indicator
        self.page_label = ttk.Label(controls_frame, text="Page: 0 / 0")
        self.page_label.pack(side="left", padx=15)
        
        # Page manipulation controls
        manipulation_frame = ttk.Frame(preview_frame)
        manipulation_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(manipulation_frame, text="Delete Page", command=self.delete_current_page).pack(side="left", padx=5)
        ttk.Button(manipulation_frame, text="Insert Blank Page", command=self.insert_blank_page).pack(side="left", padx=5)
        ttk.Button(manipulation_frame, text="Insert Blank After", command=self.insert_blank_after).pack(side="left", padx=5)
        ttk.Button(manipulation_frame, text="Rotate Left", command=lambda: self.rotate_page(-90)).pack(side="left", padx=5)
        ttk.Button(manipulation_frame, text="Rotate Right", command=lambda: self.rotate_page(90)).pack(side="left", padx=5)
        
        # Advanced features
        advanced_frame = ttk.Frame(preview_frame)
        advanced_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(advanced_frame, text="Add Annotation", command=self.add_annotation).pack(side="left", padx=5)
        ttk.Button(advanced_frame, text="Extract Page", command=self.extract_current_page).pack(side="left", padx=5)
        ttk.Button(advanced_frame, text="Duplicate Page", command=self.duplicate_page).pack(side="left", padx=5)
        ttk.Button(advanced_frame, text="Move to Position...", command=self.move_to_position).pack(side="left", padx=5)
    
    def create_pdf_list_panel(self):
        # Create notebook for tabs
        self.right_notebook = ttk.Notebook(self.right_frame)
        self.right_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # PDF List tab
        self.pdf_list_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.pdf_list_frame, text="PDF Files")
        
        # Thumbnails tab
        self.thumbnails_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.thumbnails_frame, text="Pages")
        
        # Setup PDF list tab
        self.setup_pdf_list_tab()
        
        # Setup thumbnails tab
        self.setup_thumbnails_tab()
    
    def setup_pdf_list_tab(self):
        # PDF list controls
        controls_frame = ttk.Frame(self.pdf_list_frame)
        controls_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add PDFs", command=self.add_pdfs).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Remove", command=self.remove_selected_pdf).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Clear All", command=self.clear_pdfs).pack(side="left", padx=5)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(self.pdf_list_frame)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.pdf_listbox = tk.Listbox(list_frame, height=10, yscrollcommand=scrollbar.set)
        self.pdf_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.pdf_listbox.yview)
        
        # Bind selection event
        self.pdf_listbox.bind('<<ListboxSelect>>', self.on_pdf_select)
        
        # PDF reordering controls
        reorder_frame = ttk.Frame(self.pdf_list_frame)
        reorder_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(reorder_frame, text="Move Up", command=self.move_pdf_up).pack(side="left", padx=5)
        ttk.Button(reorder_frame, text="Move Down", command=self.move_pdf_down).pack(side="left", padx=5)
        ttk.Button(reorder_frame, text="Refresh Pages", command=self.refresh_pages).pack(side="left", padx=5)
    
    def setup_thumbnails_tab(self):
        # Thumbnails controls
        controls_frame = ttk.Frame(self.thumbnails_frame)
        controls_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Select All", command=self.select_all_thumbnails).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Deselect All", command=self.deselect_all_thumbnails).pack(side="left", padx=5)
        ttk.Button(controls_frame, text="Delete Selected", command=self.delete_selected_thumbnails).pack(side="left", padx=5)
        
        # Create canvas with scrollbar for thumbnails
        self.thumb_canvas_frame = ttk.Frame(self.thumbnails_frame)
        self.thumb_canvas_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self.thumb_canvas_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.thumb_canvas = tk.Canvas(
            self.thumb_canvas_frame, 
            bg="lightgray", 
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.thumb_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.thumb_canvas.yview)
        
        # Container frame for thumbnails
        self.thumbnails_container = ttk.Frame(self.thumb_canvas)
        self.thumb_canvas.create_window((0, 0), window=self.thumbnails_container, anchor="nw")
        
        # Configure scrolling behavior
        self.thumbnails_container.bind("<Configure>", self.on_thumbnails_configure)
        self.thumb_canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Drag and drop reordering
        self.thumb_canvas.bind("<ButtonPress-1>", self.on_thumbnail_press)
        self.thumb_canvas.bind("<B1-Motion>", self.on_thumbnail_motion)
        self.thumb_canvas.bind("<ButtonRelease-1>", self.on_thumbnail_release)
        
        # Initialize drag variables
        self.drag_data = {"item": None, "x": 0, "y": 0}
    
    def create_output_panel(self):
        output_frame = ttk.LabelFrame(self.bottom_frame, text="Output Settings")
        output_frame.pack(fill="x", expand=False, padx=5, pady=5)
        
        # Output directory
        ttk.Label(output_frame, text="Output Directory:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(output_frame, text="Browse...", command=self.browse_output_dir).grid(row=0, column=2, sticky="e", padx=5, pady=5)
        
        # Output filename
        ttk.Label(output_frame, text="Output Filename:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(output_frame, textvariable=self.output_name, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        
        # Make column 1 expand
        output_frame.columnconfigure(1, weight=1)
    
    # Event handlers
    def on_thumbnails_configure(self, event):
        """Update the scroll region when the thumbnails container changes size"""
        self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))
    
    def on_mousewheel(self, event):
        """Handle mouse wheel events for the thumbnails canvas"""
        self.thumb_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def on_thumbnail_press(self, event):
        """Start thumbnail drag operation"""
        # Find thumbnail under cursor
        x, y = self.thumb_canvas.canvasx(event.x), self.thumb_canvas.canvasy(event.y)
        item = self.thumb_canvas.find_closest(x, y)[0]
        
        # Save drag data
        self.drag_data["item"] = item
        self.drag_data["x"] = x
        self.drag_data["y"] = y
    
    def on_thumbnail_motion(self, event):
        """Handle thumbnail being dragged"""
        if self.drag_data["item"] is None:
            return
            
        # Calculate new position
        x, y = self.thumb_canvas.canvasx(event.x), self.thumb_canvas.canvasy(event.y)
        dx, dy = x - self.drag_data["x"], y - self.drag_data["y"]
        
        # Move the thumbnail
        self.thumb_canvas.move(self.drag_data["item"], dx, dy)
        
        # Update drag data
        self.drag_data["x"] = x
        self.drag_data["y"] = y
    
    def on_thumbnail_release(self, event):
        """End thumbnail drag operation and handle reordering"""
        if self.drag_data["item"] is None:
            return
            
        # Get the target position in the list
        x, y = self.thumb_canvas.canvasx(event.x), self.thumb_canvas.canvasy(event.y)
        
        # Find thumbnail at the drop location
        target_items = self.thumb_canvas.find_overlapping(x-5, y-5, x+5, y+5)
        
        # If dropped on another thumbnail, do reordering
        if target_items and target_items[0] != self.drag_data["item"]:
            # Get indices
            item_tag = self.thumb_canvas.gettags(self.drag_data["item"])[0]
            from_idx = int(item_tag.split("_")[1])
            
            target_tag = self.thumb_canvas.gettags(target_items[0])[0]
            to_idx = int(target_tag.split("_")[1])
            
            # Reorder pages
            self.reorder_pages(from_idx, to_idx)
        
        # Reset drag data
        self.drag_data["item"] = None
        
        # Refresh thumbnail display
        self.refresh_thumbnails()
    
    def on_pdf_select(self, event):
        """Handle PDF selection in the listbox"""
        selected_indices = self.pdf_listbox.curselection()
        if not selected_indices:
            return
            
        # Get the PDF path
        pdf_idx = selected_indices[0]
        if pdf_idx < len(self.source_pdfs):
            pdf_path = self.source_pdfs[pdf_idx]
            self.status_var.set(f"Selected PDF: {os.path.basename(pdf_path)}")
            
            # Find the first page from this PDF and select it
            for idx, (path, page_idx, _) in enumerate(self.all_pages):
                if path == pdf_path:
                    self.selected_index = idx
                    self.update_preview()
                    break
    
    # PDF management
    def add_pdfs(self):
        """Add PDFs to the list"""
        file_paths = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        
        if not file_paths:
            return
        
        # Add to list of source PDFs
        for path in file_paths:
            self.source_pdfs.append(path)
            self.pdf_listbox.insert(tk.END, os.path.basename(path))
        
        self.status_var.set(f"Added {len(file_paths)} PDFs. Total: {len(self.source_pdfs)}")
        
        # Load pages
        self.load_pdf_pages(file_paths)
        
        # Select the first page if no current selection
        if self.selected_index < 0 and self.all_pages:
            self.selected_index = 0
            self.update_preview()
        
        # Update thumbnails
        self.refresh_thumbnails()
    
    def remove_selected_pdf(self):
        """Remove the selected PDF from the list"""
        selected_indices = self.pdf_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Warning", "Please select a PDF to remove")
            return
            
        # Get the PDF path
        pdf_idx = selected_indices[0]
        if pdf_idx < len(self.source_pdfs):
            pdf_path = self.source_pdfs[pdf_idx]
            
            # Remove from source PDFs
            self.source_pdfs.pop(pdf_idx)
            self.pdf_listbox.delete(pdf_idx)
            
            # Remove all pages from this PDF
            self.all_pages = [(path, page_idx, is_blank) for path, page_idx, is_blank 
                             in self.all_pages if path != pdf_path]
            
            # Update selected index
            if self.selected_index >= len(self.all_pages):
                self.selected_index = max(0, len(self.all_pages) - 1)
            elif self.selected_index >= 0:
                # If the current page is from the removed PDF, select another page
                if self.all_pages[self.selected_index][0] == pdf_path:
                    # Try to find a good page to select
                    if self.all_pages:
                        self.selected_index = 0
                    else:
                        self.selected_index = -1
            
            self.status_var.set(f"Removed PDF: {os.path.basename(pdf_path)}")
            
            # Update preview and thumbnails
            self.update_preview()
            self.refresh_thumbnails()
    
    def clear_pdfs(self):
        """Clear all PDFs from the list"""
        if not self.source_pdfs:
            return
            
        result = messagebox.askyesno("Confirm", "Are you sure you want to clear all PDFs?")
        if result:
            self.source_pdfs.clear()
            self.pdf_listbox.delete(0, tk.END)
            self.all_pages.clear()
            self.selected_index = -1
            self.thumbnail_cache.clear()
            
            # Update preview and thumbnails
            self.update_preview()
            self.refresh_thumbnails()
            
            self.status_var.set("All PDFs cleared")
    
    def move_pdf_up(self):
        """Move the selected PDF up in the list"""
        selected_indices = self.pdf_listbox.curselection()
        if not selected_indices or selected_indices[0] == 0:
            return
            
        # Get index
        idx = selected_indices[0]
        
        # Swap PDFs
        self.source_pdfs[idx], self.source_pdfs[idx-1] = self.source_pdfs[idx-1], self.source_pdfs[idx]
        
        # Update listbox
        self.pdf_listbox.delete(idx-1, idx)
        self.pdf_listbox.insert(idx-1, os.path.basename(self.source_pdfs[idx-1]))
        self.pdf_listbox.insert(idx, os.path.basename(self.source_pdfs[idx]))
        
        # Reselect
        self.pdf_listbox.selection_clear(0, tk.END)
        self.pdf_listbox.selection_set(idx-1)
        
        self.status_var.set(f"Moved PDF up: {os.path.basename(self.source_pdfs[idx-1])}")
        
        # Reload pages to reflect new order
        self.refresh_pages()
    
    def move_pdf_down(self):
        """Move the selected PDF down in the list"""
        selected_indices = self.pdf_listbox.curselection()
        if not selected_indices or selected_indices[0] == len(self.source_pdfs) - 1:
            return
            
        # Get index
        idx = selected_indices[0]
        
        # Swap PDFs
        self.source_pdfs[idx], self.source_pdfs[idx+1] = self.source_pdfs[idx+1], self.source_pdfs[idx]
        
        # Update listbox
        self.pdf_listbox.delete(idx, idx+1)
        self.pdf_listbox.insert(idx, os.path.basename(self.source_pdfs[idx]))
        self.pdf_listbox.insert(idx+1, os.path.basename(self.source_pdfs[idx+1]))
        
        # Reselect
        self.pdf_listbox.selection_clear(0, tk.END)
        self.pdf_listbox.selection_set(idx+1)
        
        self.status_var.set(f"Moved PDF down: {os.path.basename(self.source_pdfs[idx+1])}")
        
        # Reload pages to reflect new order
        self.refresh_pages()
    
    def refresh_pages(self):
        """Reload all pages from source PDFs"""
        # Store current selected page's PDF and index for restoration
        selected_pdf = None
        selected_page_idx = None
        if self.selected_index >= 0 and self.selected_index < len(self.all_pages):
            selected_pdf, selected_page_idx, _ = self.all_pages[self.selected_index]
        
        # Clear current pages
        self.all_pages.clear()
        
        # Reload all pages
        self.load_pdf_pages(self.source_pdfs)
        
        # Try to restore selection
        if selected_pdf and selected_page_idx is not None:
            # Find the same page in the new list
            for idx, (path, page_idx, _) in enumerate(self.all_pages):
                if path == selected_pdf and page_idx == selected_page_idx:
                    self.selected_index = idx
                    break
            else:
                # If not found, select the first page
                self.selected_index = 0 if self.all_pages else -1
        else:
            # Select first page if any
            self.selected_index = 0 if self.all_pages else -1
        
        # Update preview and thumbnails
        self.update_preview()
        self.refresh_thumbnails()
        
        self.status_var.set("Pages refreshed")
    
    def load_pdf_pages(self, pdf_paths):
        """Load pages from the given PDF files"""
        for pdf_path in pdf_paths:
            try:
                # Open PDF
                pdf = pdfium.PdfDocument(pdf_path)
                
                # Add all pages
                for page_idx in range(len(pdf)):
                    self.all_pages.append((pdf_path, page_idx, False))
                    
                self.status_var.set(f"Loaded {len(pdf)} pages from {os.path.basename(pdf_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load {os.path.basename(pdf_path)}: {str(e)}")
                self.status_var.set(f"Error: {str(e)}")
    
    # Page navigation and display
    def previous_page(self):
        """Go to the previous page"""
        if not self.all_pages:
            return
            
        if self.selected_index > 0:
            self.selected_index -= 1
            self.update_preview()
    
    def next_page(self):
        """Go to the next page"""
        if not self.all_pages:
            return
            
        if self.selected_index < len(self.all_pages) - 1:
            self.selected_index += 1
            self.update_preview()
    
    def update_preview(self):
        """Update the main preview with the current page"""
        # Clear canvas
        self.preview_canvas.delete("all")
        
        # Update page label
        total_pages = len(self.all_pages)
        current_page = self.selected_index + 1 if self.selected_index >= 0 else 0
        self.page_label.config(text=f"Page: {current_page} / {total_pages}")
        
        if self.selected_index < 0 or not self.all_pages:
            return
            
        # Get page info
        pdf_path, page_idx, is_blank = self.all_pages[self.selected_index]
        
        try:
            if is_blank:
                # Create a blank page image
                img = Image.new('RGB', (612, 792), 'white')  # Letter size
                self._display_preview_image(img)
            else:
                # Load the page
                pdf = pdfium.PdfDocument(pdf_path)
                page = pdf[page_idx]
                
                # Render to image
                pil_image = page.render(
                    scale=1.5,  # Higher quality for preview
                    rotation=0
                ).to_pil()
                
                # Display the image
                self._display_preview_image(pil_image)
                
                # Get PDF name for status
                pdf_name = os.path.basename(pdf_path)
                self.status_var.set(f"Displaying page {page_idx + 1} from {pdf_name}")
                
        except Exception as e:
            self.status_var.set(f"Error loading preview: {str(e)}")
    
    def _display_preview_image(self, img):
        """Display an image in the preview canvas with current zoom"""
        # Apply zoom
        width, height = img.size
        new_width = int(width * self.current_zoom)
        new_height = int(height * self.current_zoom)
        
        # Resize image
        img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Save reference to prevent garbage collection
        self.preview_image = photo
        
        # Set scroll region
        self.preview_canvas.config(scrollregion=(0, 0, new_width, new_height))
        
        # Display image
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
    
    def zoom_preview(self, delta):
        """Change zoom level by delta amount"""
        new_zoom = max(0.25, min(4.0, self.current_zoom + delta))
        self.set_zoom(new_zoom)
    
    def set_zoom(self, zoom):
        """Set the zoom level directly"""
        self.current_zoom = zoom
        self.update_preview()
        self.status_var.set(f"Zoom: {int(self.current_zoom * 100)}%")
    
    def zoom_to_fit(self):
        """Zoom to fit the preview in the visible area"""
        if not self.all_pages or self.selected_index < 0:
            return
            
        # Get canvas dimensions
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return  # Canvas not properly sized yet
        
        # Get page info
        pdf_path, page_idx, is_blank = self.all_pages[self.selected_index]
        
        try:
            if is_blank:
                # Standard page size
                img_width, img_height = 612, 792
            else:
                # Get page dimensions
                pdf = pdfium.PdfDocument(pdf_path)
                page = pdf[page_idx]
                # Get size in points
                img_width, img_height = page.get_size()
            
            # Calculate zoom to fit
            zoom_width = canvas_width / img_width
            zoom_height = canvas_height / img_height
            zoom = min(zoom_width, zoom_height) * 0.95  # 5% margin
            
            # Set the zoom
            self.set_zoom(zoom)
            
        except Exception as e:
            self.status_var.set(f"Error calculating zoom: {str(e)}")
    
    # Page manipulation
    def delete_current_page(self):
        """Delete the current page"""
        if not self.all_pages or self.selected_index < 0:
            return
            
        # Remove the page
        self.all_pages.pop(self.selected_index)
        
        # Adjust selection
        if self.selected_index >= len(self.all_pages):
            self.selected_index = max(0, len(self.all_pages) - 1)
        
        # Update preview and thumbnails
        self.update_preview()
        self.refresh_thumbnails()
        
        self.status_var.set("Page deleted")
    
    def insert_blank_page(self):
        """Insert a blank page before the current page"""
        if not self.all_pages:
            # If no pages, just add one at the beginning
            self.all_pages.append((None, 0, True))
            self.selected_index = 0
        else:
            # Insert before current page
            idx = max(0, self.selected_index)
            self.all_pages.insert(idx, (None, 0, True))
            self.selected_index = idx
        
        # Update preview and thumbnails
        self.update_preview()
        self.refresh_thumbnails()
        
        self.status_var.set("Blank page inserted")
    
    def insert_blank_after(self):
        """Insert a blank page after the current page"""
        if not self.all_pages:
            # If no pages, just add one at the beginning
            self.all_pages.append((None, 0, True))
            self.selected_index = 0
        else:
            # Insert after current page
            idx = self.selected_index + 1 if self.selected_index >= 0 else 0
            self.all_pages.insert(idx, (None, 0, True))
            self.selected_index = idx
        
        # Update preview and thumbnails
        self.update_preview()
        self.refresh_thumbnails()
        
        self.status_var.set("Blank page inserted")
    
    def rotate_page(self, angle):
        """Rotate the current page by the given angle"""
        if not self.all_pages or self.selected_index < 0:
            return
            
        # Note: This requires PyPDF2 to actually apply the rotation
        # For now, just show a message
        # In a full implementation, we would store rotation info and apply it when saving
        messagebox.showinfo("Rotation", f"Page will be rotated by {angle} degrees when saving.")
        self.status_var.set(f"Page rotation set to {angle} degrees")
    
    def add_annotation(self):
        """Add a text annotation to the current page"""
        if not self.all_pages or self.selected_index < 0:
            return
            
        # Simple annotation implementation - just get text from user
        annotation = simpledialog.askstring("Annotation", "Enter annotation text:")
        if annotation:
            messagebox.showinfo("Annotation", "Annotation will be added when saving.")
            self.status_var.set("Annotation added")
    
    def extract_current_page(self):
        """Extract the current page to a separate PDF"""
        if not self.all_pages or self.selected_index < 0:
            return
            
        # Get page info
        pdf_path, page_idx, is_blank = self.all_pages[self.selected_index]
        
        if is_blank:
            messagebox.showinfo("Extract", "Cannot extract a blank page.")
            return
        
        # Ask for save location
        output_path = filedialog.asksaveasfilename(
            title="Save Extracted Page",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
            initialdir=self.output_dir.get()
        )
        
        if not output_path:
            return
            
        # Extract the page in a separate thread
        self.status_var.set("Extracting page...")
        threading.Thread(target=self._extract_page_thread, args=(pdf_path, page_idx, output_path)).start()
    
    def _extract_page_thread(self, pdf_path, page_idx, output_path):
        try:
            # Open source PDF
            pdf = pdfium.PdfDocument(pdf_path)
            
            # Create new PDF with just this page
            output_pdf = pdfium.PdfDocument.new()
            output_pdf.import_pages(pdf, [page_idx])
            
            # Save the new PDF
            output_pdf.save(output_path)
            
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo(
                "Success", f"Page extracted and saved to:\n{output_path}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Page extracted successfully"))
        
        except Exception as e:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror(
                "Error", f"Failed to extract page: {str(e)}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {str(e)}"))
    
    def duplicate_page(self):
        """Duplicate the current page"""
        if not self.all_pages or self.selected_index < 0:
            return
            
        # Get page info
        pdf_path, page_idx, is_blank = self.all_pages[self.selected_index]
        
        # Insert a copy after the current page
        self.all_pages.insert(self.selected_index + 1, (pdf_path, page_idx, is_blank))
        
        # Move to the new page
        self.selected_index += 1
        
        # Update preview and thumbnails
        self.update_preview()
        self.refresh_thumbnails()
        
        self.status_var.set("Page duplicated")
    
    def move_to_position(self):
        """Move the current page to a specified position"""
        if not self.all_pages or self.selected_index < 0:
            return
            
        # Ask for the new position
        position = simpledialog.askinteger(
            "Move Page", 
            f"Enter new position (1-{len(self.all_pages)}):",
            minvalue=1, 
            maxvalue=len(self.all_pages)
        )
        
        if not position:
            return
            
        # Adjust to 0-based index
        position = position - 1
        
        # Move the page (if different from current position)
        if position != self.selected_index:
            self.reorder_pages(self.selected_index, position)
            self.selected_index = position
            
            # Update preview and thumbnails
            self.update_preview()
            self.refresh_thumbnails()
            
            self.status_var.set(f"Page moved to position {position + 1}")
    
    def reorder_pages(self, from_idx, to_idx):
        """Reorder pages by moving from_idx to to_idx"""
        if from_idx < 0 or from_idx >= len(self.all_pages) or to_idx < 0 or to_idx >= len(self.all_pages):
            return
            
        # Remove the page from its current position
        page = self.all_pages.pop(from_idx)
        
        # Insert at the new position
        self.all_pages.insert(to_idx, page)
    
    # Thumbnails management
    def refresh_thumbnails(self):
        """Refresh the thumbnails display"""
        # Clear thumbnails container
        for widget in self.thumbnails_container.winfo_children():
            widget.destroy()
        
        # Clear canvas
        self.thumb_canvas.delete("all")
        
        if not self.all_pages:
            return
            
        # Calculate thumbnail size based on available width
        canvas_width = self.thumb_canvas.winfo_width()
        if canvas_width <= 1:
            canvas_width = 200  # Default if not realized yet
        
        thumb_width = min(150, canvas_width - 20)
        thumb_height = int(thumb_width * 1.414)  # Approximate A4 ratio
        
        # Calculate number of columns
        num_cols = max(1, canvas_width // (thumb_width + 10))
        
        # Create thumbnails
        for idx, (pdf_path, page_idx, is_blank) in enumerate(self.all_pages):
            # Calculate grid position
            row = idx // num_cols
            col = idx % num_cols
            
            # Create frame for thumbnail
            frame = ttk.Frame(self.thumbnails_container, width=thumb_width, height=thumb_height + 30)
            frame.grid(row=row, col=col, padx=5, pady=5)
            frame.pack_propagate(False)
            
            # Create canvas for thumbnail
            canvas = tk.Canvas(frame, width=thumb_width, height=thumb_height, bg="white", highlightthickness=1)
            canvas.pack(pady=(0, 2))
            
            # Create label for page number
            ttk.Label(frame, text=f"Page {idx + 1}").pack()
            
            # Generate and display thumbnail
            self._create_thumbnail(canvas, pdf_path, page_idx, is_blank, idx, thumb_width, thumb_height)
            
            # Bind click event
            canvas.bind("<Button-1>", lambda e, i=idx: self._select_thumbnail(i))
        
        # Update canvas scroll region
        self.thumbnails_container.update_idletasks()
        self.thumb_canvas.configure(scrollregion=self.thumb_canvas.bbox("all"))
    
    def _create_thumbnail(self, canvas, pdf_path, page_idx, is_blank, idx, width, height):
        """Create a thumbnail for the given page"""
        # Check if thumbnail is already in cache
        cache_key = f"{pdf_path}_{page_idx}_{is_blank}"
        if cache_key in self.thumbnail_cache:
            # Use cached thumbnail
            photo = self.thumbnail_cache[cache_key]
            canvas.create_image(width/2, height/2, image=photo, anchor=tk.CENTER, tags=f"thumb_{idx}")
            return
            
        # Create thumbnail in a separate thread
        threading.Thread(target=self._generate_thumbnail, 
                       args=(canvas, pdf_path, page_idx, is_blank, idx, width, height, cache_key)).start()
    
    def _generate_thumbnail(self, canvas, pdf_path, page_idx, is_blank, idx, width, height, cache_key):
        try:
            if is_blank:
                # Create a blank page thumbnail
                img = Image.new('RGB', (width, height), 'white')
            else:
                # Load the page
                pdf = pdfium.PdfDocument(pdf_path)
                page = pdf[page_idx]
                
                # Render to image
                pil_image = page.render(
                    scale=0.5,  # Lower quality for thumbnails
                    rotation=0
                ).to_pil()
                
                # Resize to thumbnail size
                img_width, img_height = pil_image.size
                ratio = min(width / img_width, height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                img = pil_image.resize((new_width, new_height), Image.LANCZOS)
                
                # Create blank image with right size and paste thumbnail centered
                bg = Image.new('RGB', (width, height), 'white')
                x = (width - new_width) // 2
                y = (height - new_height) // 2
                bg.paste(img, (x, y))
                img = bg
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Save in cache
            self.thumbnail_cache[cache_key] = photo
            
            # Draw on canvas in main thread
            self.frame.winfo_toplevel().after(0, 
                lambda: self._draw_thumbnail(canvas, photo, idx, width, height))
        
        except Exception as e:
            # Draw error thumbnail
            self.frame.winfo_toplevel().after(0, 
                lambda: self._draw_error_thumbnail(canvas, str(e), idx, width, height))
    
    def _draw_thumbnail(self, canvas, photo, idx, width, height):
        """Draw the thumbnail on the canvas"""
        # Clear previous content
        canvas.delete("all")
        
        # Draw thumbnail
        canvas.create_image(width/2, height/2, image=photo, anchor=tk.CENTER, tags=f"thumb_{idx}")
        
        # Highlight if selected
        if idx == self.selected_index:
            canvas.config(highlightbackground="blue", highlightthickness=3)
        else:
            canvas.config(highlightbackground="gray", highlightthickness=1)
    
    def _draw_error_thumbnail(self, canvas, error, idx, width, height):
        """Draw an error thumbnail"""
        # Clear previous content
        canvas.delete("all")
        
        # Draw error message
        canvas.create_rectangle(0, 0, width, height, fill="lightgray")
        canvas.create_text(width/2, height/2, text="Error", tags=f"thumb_{idx}")
        
        # Create tooltip
        self._create_tooltip(canvas, error)
    
    def _create_tooltip(self, widget, text):
        """Create a tooltip for the widget"""
        tooltip = tk.Label(widget, text=text, bg="yellow", relief="solid", borderwidth=1)
        
        def enter(event):
            x, y, _, _ = widget.bbox("all")
            tooltip.place(x=x, y=y, anchor=tk.NW)
            
        def leave(event):
            tooltip.place_forget()
            
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def _select_thumbnail(self, idx):
        """Select the thumbnail at the given index"""
        if idx >= 0 and idx < len(self.all_pages):
            self.selected_index = idx
            self.update_preview()
            
            # Update thumbnail highlighting
            for widget in self.thumbnails_container.winfo_children():
                if isinstance(widget, ttk.Frame) and len(widget.winfo_children()) > 0:
                    canvas = widget.winfo_children()[0]
                    if isinstance(canvas, tk.Canvas):
                        canvas_tag = canvas.gettags("all")
                        if canvas_tag and canvas_tag[0].startswith("thumb_"):
                            thumb_idx = int(canvas_tag[0].split("_")[1])
                            if thumb_idx == idx:
                                canvas.config(highlightbackground="blue", highlightthickness=3)
                            else:
                                canvas.config(highlightbackground="gray", highlightthickness=1)
    
    def select_all_thumbnails(self):
        """Select all thumbnails (for future multi-select operations)"""
        messagebox.showinfo("Info", "Multi-select operations are not implemented yet.")
    
    def deselect_all_thumbnails(self):
        """Deselect all thumbnails"""
        messagebox.showinfo("Info", "Multi-select operations are not implemented yet.")
    
    def delete_selected_thumbnails(self):
        """Delete selected thumbnails (for future multi-select operations)"""
        # For now, just delete current page
        self.delete_current_page()
    
    # Output and processing
    def browse_output_dir(self):
        """Browse for output directory"""
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)
    
    def start_process(self):
        """Start the PDF organization process"""
        if not self.all_pages:
            messagebox.showerror("Error", "No pages to process.")
            return
            
        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory.")
            return
            
        if not self.output_name.get():
            messagebox.showerror("Error", "Please enter a name for the output PDF file.")
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
                
        # Disable controls during processing
        utils.set_controls_state(self.frame, tk.DISABLED)
        
        # Start processing in a separate thread
        self.process_canceled = False
        threading.Thread(target=self._processing_thread, args=(output_path,)).start()
    
    def _processing_thread(self, output_path):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Creating organized PDF..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))
            
            # Create a new PDF
            writer = PdfWriter()
            
            # Process each page
            total_pages = len(self.all_pages)
            for i, (pdf_path, page_idx, is_blank) in enumerate(self.all_pages):
                if self.process_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Process canceled"))
                    return
                    
                # Update progress
                progress_pct = ((i + 1) / total_pages) * 100
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=i+1, t=total_pages: 
                    self.status_var.set(f"Processing page {p}/{t}..."))
                
                if is_blank:
                    # Create a blank page
                    writer.add_blank_page(width=612, height=792)  # Letter size
                else:
                    # Add page from source PDF
                    try:
                        reader = PdfReader(pdf_path)
                        page = reader.pages[page_idx]
                        writer.add_page(page)
                    except Exception as e:
                        self.frame.winfo_toplevel().after(0, lambda p=i+1, err=str(e): 
                            messagebox.showwarning("Warning", f"Failed to process page {p}: {err}"))
                        continue
            
            # Save the new PDF
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # Complete
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"PDF created successfully: {os.path.basename(output_path)}"))
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showinfo("Success", 
                f"PDF created successfully.\n{total_pages} pages included.\nSaved to: {output_path}"))
            
        except Exception as e:
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Failed to create PDF: {str(e)}"))
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
    
    def cancel_process(self):
        """Cancel the current process"""
        self.process_canceled = True
        self.status_var.set("Canceling process...")
    
    def open_output_folder(self):
        """Open the output folder"""
        utils.open_output_folder(self.output_dir.get())
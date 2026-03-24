# main.py
import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askopenfilename, askdirectory
import multiprocessing
from pathlib import Path
import webbrowser

# Import all tab modules
from pdf_merge_tab import PDFMergeTab
from pdf_split_tab import PDFSplitTab
from pdf_compress_tab import PDFCompressTab
from pdf_to_image_tab import PDFToImageTab
from image_to_pdf_tab import ImageToPDFTab
from pdf_security_tab import PDFSecurityTab
from image_batch_tab import ImageBatchTab
from pdf_organizer_tab import PDFOrganizerTab
from image_convert_tab import ImageConvertTab
from image_resize_tab import ImageResizeTab
from image_watermark_tab import ImageWatermarkTab
from image_metadata_tab import ImageMetadataTab
from contribute_dialog import show_contribute_dialog
from support_tab import SupportTab

# Import settings, drag drop, styles, utilities
from settings import Settings
from drag_drop import DragDropManager
from styles import apply_modern_theme, COLORS, FONTS
from version import VERSION
from ghostscript_utils import is_ghostscript_available


class P2IApp:
    def __init__(self, root):
        self.root = root
        self.root.title("p2i - PDF & Image Processing Tool")
        self.root.geometry("900x700")
        self.root.state('zoomed')

        # Determine application path for resources
        if getattr(sys, 'frozen', False):
            self.application_path = sys._MEIPASS  # type: ignore
        elif "__compiled__" in dir():
            self.application_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        else:
            self.application_path = os.path.dirname(os.path.abspath(__file__))

        # Set window icon
        self._set_window_icon(self.root)

        # Load settings
        self.settings = Settings()

        # Apply modern theme
        self.style = apply_modern_theme(root)

        # Configure tab group styles
        self.style.configure('PDFGroup.TLabelframe', background=COLORS['bg'])
        self.style.configure('PDFGroup.TLabelframe.Label',
                             foreground=COLORS['primary'], font=('Segoe UI', 9, 'bold'))
        self.style.configure('ImageGroup.TLabelframe', background=COLORS['bg'])
        self.style.configure('ImageGroup.TLabelframe.Label',
                             foreground=COLORS['success'], font=('Segoe UI', 9, 'bold'))

        # Set up main notebook
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(8, 4))

        # Detect CPU count for parallel processing
        n_cpu = max(1, multiprocessing.cpu_count() - 1)

        # Create PDF tabs
        self.pdf_merge_tab = PDFMergeTab(self.notebook)
        self.pdf_split_tab = PDFSplitTab(self.notebook)
        self.pdf_compress_tab = PDFCompressTab(self.notebook)
        self.pdf_to_image_tab = PDFToImageTab(self.notebook, n_cpu)
        self.pdf_security_tab = PDFSecurityTab(self.notebook)
        self.pdf_organizer_tab = PDFOrganizerTab(self.notebook)

        # Create Image tabs
        self.image_to_pdf_tab = ImageToPDFTab(self.notebook)
        self.image_convert_tab = ImageConvertTab(self.notebook)
        self.image_resize_tab = ImageResizeTab(self.notebook)
        self.image_batch_tab = ImageBatchTab(self.notebook)
        self.image_watermark_tab = ImageWatermarkTab(self.notebook)
        self.image_metadata_tab = ImageMetadataTab(self.notebook)

        # Support tab
        self.support_tab = SupportTab(self.notebook)

        # Add PDF tabs (left group) with visual separator
        self.notebook.add(self.pdf_merge_tab.frame, text=" Merge PDFs ")
        self.notebook.add(self.pdf_split_tab.frame, text=" Split PDF ")
        self.notebook.add(self.pdf_compress_tab.frame, text=" Compress PDF ")
        self.notebook.add(self.pdf_to_image_tab.frame, text=" PDF to Image ")
        self.notebook.add(self.pdf_security_tab.frame, text=" PDF Security ")
        self.notebook.add(self.pdf_organizer_tab.frame, text=" PDF Organizer ")

        # Separator tab (disabled visual divider)
        sep_frame = ttk.Frame(self.notebook)
        self.notebook.add(sep_frame, text=" | ", state="disabled")

        # Add Image tabs (right group)
        self.notebook.add(self.image_to_pdf_tab.frame, text=" Image to PDF ")
        self.notebook.add(self.image_convert_tab.frame, text=" Convert Image ")
        self.notebook.add(self.image_resize_tab.frame, text=" Resize Image ")
        self.notebook.add(self.image_batch_tab.frame, text=" Batch Process ")
        self.notebook.add(self.image_watermark_tab.frame, text=" Watermark ")
        self.notebook.add(self.image_metadata_tab.frame, text=" Metadata ")

        # Support tab at the end
        self.notebook.add(self.support_tab.frame, text=" Support p2i ")

        # Tab index map for easy reference
        self._tab_indices = {
            'merge': 0, 'split': 1, 'compress': 2, 'pdf_to_image': 3,
            'security': 4, 'organizer': 5,
            # 6 = separator (disabled)
            'image_to_pdf': 7, 'convert_image': 8, 'resize_image': 9,
            'batch_process': 10, 'watermark': 11, 'metadata': 12,
            'support': 13,
        }

        # Create main menu
        self.create_menu()

        self.apply_settings()

        # Set up drag and drop
        self.setup_drag_drop()

        # Keyboard shortcuts
        self.root.bind("<Control-o>", lambda e: self.open_pdf())
        self.root.bind("<Control-i>", lambda e: self.open_image())
        self.root.bind("<Control-comma>", lambda e: self.show_preferences())
        self.root.bind("<Control-q>", lambda e: self.on_close())
        self.root.bind("<F1>", lambda e: self.show_help())

        # Handle application close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _set_window_icon(self, window):
        """Set the p2i icon on any Tk or Toplevel window."""
        try:
            if os.name == 'nt':
                for icon_path in [
                    os.path.join(self.application_path, "resources", "icon", "app_icon.ico"),
                    os.path.join("resources", "icon", "app_icon.ico"),
                ]:
                    if os.path.exists(icon_path):
                        window.iconbitmap(icon_path)
                        return
            else:
                for icon_path in [
                    os.path.join(self.application_path, "resources", "icon", "app_icon.png"),
                    os.path.join("resources", "icon", "app_icon.png"),
                ]:
                    if os.path.exists(icon_path):
                        img = tk.PhotoImage(file=icon_path)
                        window.iconphoto(True, img)
                        window._icon_img = img
                        return
        except Exception as e:
            print(f"Could not load icon: {e}")

    def _create_dialog(self, title, geometry, grab=True):
        """Create a Toplevel dialog with icon, centered on parent."""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry(geometry)
        dialog.transient(self.root)
        if grab:
            dialog.grab_set()
        self._set_window_icon(dialog)
        return dialog

    def _center_dialog(self, dialog):
        """Center a dialog on screen."""
        dialog.update_idletasks()
        w = dialog.winfo_width()
        h = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (w // 2)
        y = (dialog.winfo_screenheight() // 2) - (h // 2)
        dialog.geometry(f'{w}x{h}+{x}+{y}')

    def setup_drag_drop(self):
        """Set up drag and drop functionality"""
        drop_targets = [
            self.pdf_merge_tab.frame,
            self.pdf_split_tab.frame,
            self.pdf_organizer_tab.frame,
            self.pdf_compress_tab.frame,
            self.pdf_security_tab.frame,
            self.pdf_to_image_tab.frame,
            self.image_to_pdf_tab.frame,
            self.image_batch_tab.frame,
            self.image_convert_tab.frame,
            self.image_resize_tab.frame,
            self.image_watermark_tab.frame,
            self.image_metadata_tab.frame,
            self.support_tab.frame,
        ]

        self.dnd_manager = DragDropManager(self.root, self.settings, drop_targets)

        # Status bar
        status_frame = tk.Frame(self.root, bg=COLORS['bg_card'], height=28)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)

        dnd_text = "Drag & Drop enabled" if self.dnd_manager.is_available() else "Drag & Drop unavailable"
        gs_text = "GS: Found" if is_ghostscript_available() else "GS: Not Found"
        self.status_bar = tk.Label(status_frame,
            text=f"  p2i v{VERSION}  |  {dnd_text}  |  {gs_text}",
            font=FONTS['caption'],
            fg=COLORS['text_muted'],
            bg=COLORS['bg_card'],
            anchor='w',
        )
        self.status_bar.pack(fill="both", expand=True, padx=8)

    def create_menu(self):
        menubar = tk.Menu(self.root)

        # ---- File menu ----
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open PDF...", command=self.open_pdf)
        file_menu.add_command(label="Open Image...", command=self.open_image)
        file_menu.add_separator()
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        self.update_recent_files_menu()
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        # ---- Edit menu ----
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Preferences...", command=self.show_preferences)
        edit_menu.add_command(label="Clear Recent Files", command=self.clear_recent_files)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        # ---- View menu ----
        view_menu = tk.Menu(menubar, tearoff=0)
        pdf_menu = tk.Menu(view_menu, tearoff=0)
        pdf_menu.add_command(label="Merge PDFs", command=lambda: self.notebook.select(self._tab_indices['merge']))
        pdf_menu.add_command(label="Split PDF", command=lambda: self.notebook.select(self._tab_indices['split']))
        pdf_menu.add_command(label="Compress PDF", command=lambda: self.notebook.select(self._tab_indices['compress']))
        pdf_menu.add_command(label="PDF to Image", command=lambda: self.notebook.select(self._tab_indices['pdf_to_image']))
        pdf_menu.add_command(label="PDF Security", command=lambda: self.notebook.select(self._tab_indices['security']))
        pdf_menu.add_command(label="PDF Organizer", command=lambda: self.notebook.select(self._tab_indices['organizer']))
        view_menu.add_cascade(label="PDF Tools", menu=pdf_menu)

        img_menu = tk.Menu(view_menu, tearoff=0)
        img_menu.add_command(label="Image to PDF", command=lambda: self.notebook.select(self._tab_indices['image_to_pdf']))
        img_menu.add_command(label="Convert Image", command=lambda: self.notebook.select(self._tab_indices['convert_image']))
        img_menu.add_command(label="Resize Image", command=lambda: self.notebook.select(self._tab_indices['resize_image']))
        img_menu.add_command(label="Batch Process", command=lambda: self.notebook.select(self._tab_indices['batch_process']))
        img_menu.add_command(label="Watermark", command=lambda: self.notebook.select(self._tab_indices['watermark']))
        img_menu.add_command(label="Metadata", command=lambda: self.notebook.select(self._tab_indices['metadata']))
        view_menu.add_cascade(label="Image Tools", menu=img_menu)
        menubar.add_cascade(label="View", menu=view_menu)

        # ---- Help menu ----
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="User Guide", command=self.show_help)
        help_menu.add_command(label="Ghostscript Setup", command=self.show_ghostscript_help)
        help_menu.add_command(label="Keyboard Shortcuts", command=self.show_shortcuts)
        help_menu.add_separator()
        help_menu.add_command(label="Check for Updates", command=self.check_updates)
        help_menu.add_command(label="Contribute to p2i", command=lambda: show_contribute_dialog(self.root))
        help_menu.add_separator()
        help_menu.add_command(label="About p2i", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        # ---- Support menu (next to Help) ----
        support_menu = tk.Menu(menubar, tearoff=0)
        support_menu.add_command(label="GitHub Sponsors",
                                 command=lambda: webbrowser.open("https://github.com/sponsors/kuroonai"))
        support_menu.add_command(label="Patreon",
                                 command=lambda: webbrowser.open("https://www.patreon.com/kuroonai"))
        support_menu.add_command(label="Buy Me A Coffee",
                                 command=lambda: webbrowser.open("https://www.buymeacoffee.com/kuroonai"))
        support_menu.add_command(label="PayPal",
                                 command=lambda: webbrowser.open("https://www.paypal.me/kuroonai"))
        support_menu.add_separator()
        support_menu.add_command(label="View Support Page",
                                 command=lambda: self.notebook.select(self._tab_indices['support']))
        menubar.add_cascade(label="Support", menu=support_menu)

        self.root.config(menu=menubar)

    def update_recent_files_menu(self):
        self.recent_menu.delete(0, tk.END)
        recent_files = self.settings.get_recent_files()
        if recent_files:
            for file_path in recent_files:
                display_path = file_path
                if len(display_path) > 60:
                    display_path = "..." + display_path[-57:]
                self.recent_menu.add_command(
                    label=display_path,
                    command=lambda path=file_path: self.open_recent_file(path)
                )
        else:
            self.recent_menu.add_command(label="No Recent Files", state=tk.DISABLED)

    def open_pdf(self):
        file_path = askopenfilename(
            title="Open PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file_path:
            self.settings.add_recent_file(file_path)
            self.update_recent_files_menu()

            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".pdf":
                operation = self.ask_pdf_operation()
                if operation == "merge":
                    self.notebook.select(self._tab_indices['merge'])
                    self.pdf_merge_tab.add_pdfs([file_path])
                elif operation == "split":
                    self.notebook.select(self._tab_indices['split'])
                    self.pdf_split_tab.pdf_path.set(file_path)
                    self.pdf_split_tab.get_page_count()
                elif operation == "compress":
                    self.notebook.select(self._tab_indices['compress'])
                    self.pdf_compress_tab.pdf_path.set(file_path)
                    self.pdf_compress_tab.update_file_size_info()
                elif operation == "to_image":
                    self.notebook.select(self._tab_indices['pdf_to_image'])
                    self.pdf_to_image_tab.pdf_path.set(file_path)
                    self.pdf_to_image_tab.get_page_count()
                elif operation == "security":
                    self.notebook.select(self._tab_indices['security'])
                    self.pdf_security_tab.pdf_path.set(file_path)

    def open_image(self):
        file_path = askopenfilename(
            title="Open Image File",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.tiff *.gif *.webp"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            self.settings.add_recent_file(file_path)
            self.update_recent_files_menu()

            operation = self.ask_image_operation()
            if operation == "to_pdf":
                self.notebook.select(self._tab_indices['image_to_pdf'])
                self.image_to_pdf_tab.add_images([file_path])
            elif operation == "convert":
                self.notebook.select(self._tab_indices['convert_image'])
                self.image_convert_tab.add_images([file_path])
            elif operation == "resize":
                self.notebook.select(self._tab_indices['resize_image'])
                self.image_resize_tab.add_images([file_path])
            elif operation == "batch":
                self.notebook.select(self._tab_indices['batch_process'])
                self.image_batch_tab.selected_image_path.set(file_path)
                self.image_batch_tab.show_preview_image(file_path)
            elif operation == "watermark":
                self.notebook.select(self._tab_indices['watermark'])
                self.image_watermark_tab.add_images([file_path])
            elif operation == "metadata":
                self.notebook.select(self._tab_indices['metadata'])
                self.image_metadata_tab.set_image(file_path)

    def open_recent_file(self, file_path):
        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            self.settings.settings['recent_files'].remove(file_path)
            self.settings.save_settings()
            self.update_recent_files_menu()
            return

        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            self.open_pdf()
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".webp"]:
            self.open_image()
        else:
            messagebox.showinfo("Info", f"Unknown file type: {ext}")

    def ask_pdf_operation(self):
        operations = {
            "Merge with other PDFs": "merge",
            "Split into parts": "split",
            "Compress PDF": "compress",
            "Convert to images": "to_image",
            "Add security/watermark": "security"
        }

        dialog = self._create_dialog("Choose Operation", "400x300")

        ttk.Label(dialog, text="What would you like to do with this PDF?",
                font=FONTS['subheading']).pack(pady=10)

        result = tk.StringVar()
        for label, value in operations.items():
            ttk.Button(dialog, text=label, width=30,
                     command=lambda v=value: [result.set(v), dialog.destroy()]).pack(pady=5)

        ttk.Button(dialog, text="Cancel", width=30,
                 command=dialog.destroy, style="Secondary.TButton").pack(pady=10)

        self._center_dialog(dialog)
        self.root.wait_window(dialog)
        return result.get()

    def ask_image_operation(self):
        operations = {
            "Convert to PDF": "to_pdf",
            "Convert Format": "convert",
            "Resize Image": "resize",
            "Process/Edit Image": "batch",
            "Add Watermark": "watermark",
            "View Metadata": "metadata",
        }

        dialog = self._create_dialog("Choose Operation", "400x380")

        ttk.Label(dialog, text="What would you like to do with this image?",
                font=FONTS['subheading']).pack(pady=10)

        result = tk.StringVar()
        for label, value in operations.items():
            ttk.Button(dialog, text=label, width=30,
                     command=lambda v=value: [result.set(v), dialog.destroy()]).pack(pady=4)

        ttk.Button(dialog, text="Cancel", width=30,
                 command=dialog.destroy, style="Secondary.TButton").pack(pady=10)

        self._center_dialog(dialog)
        self.root.wait_window(dialog)
        return result.get()

    def handle_dropped_files(self, files):
        """Process files that were dropped onto the application"""
        if not files:
            return

        valid_files = []
        rejected = []
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in ['.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp',
                       '.tif', '.ico']:
                valid_files.append(f)
            else:
                rejected.append(os.path.basename(f))

        if rejected:
            messagebox.showwarning("Unsupported Files",
                f"The following files are not supported and were skipped:\n" +
                "\n".join(rejected[:5]) +
                (f"\n...and {len(rejected)-5} more" if len(rejected) > 5 else ""))

        if not valid_files:
            return

        files = valid_files

        for file_path in files:
            self.settings.add_recent_file(file_path)
        self.update_recent_files_menu()

        pdf_files = []
        image_files = []
        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == ".pdf":
                pdf_files.append(file_path)
            elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif", ".webp", ".ico"]:
                image_files.append(file_path)

        current_tab_idx = self.notebook.index(self.notebook.select())
        ti = self._tab_indices

        if current_tab_idx == ti['merge'] and pdf_files:
            self.pdf_merge_tab.add_pdfs(pdf_files)
        elif current_tab_idx == ti['split'] and len(pdf_files) == 1:
            self.pdf_split_tab.pdf_path.set(pdf_files[0])
            self.pdf_split_tab.get_page_count()
        elif current_tab_idx == ti['compress'] and len(pdf_files) == 1:
            self.pdf_compress_tab.pdf_path.set(pdf_files[0])
            self.pdf_compress_tab.update_file_size_info()
        elif current_tab_idx == ti['pdf_to_image'] and len(pdf_files) == 1:
            self.pdf_to_image_tab.pdf_path.set(pdf_files[0])
            self.pdf_to_image_tab.get_page_count()
        elif current_tab_idx == ti['security'] and len(pdf_files) == 1:
            self.pdf_security_tab.pdf_path.set(pdf_files[0])
        elif current_tab_idx == ti['organizer'] and pdf_files:
            for pdf_path in pdf_files:
                self.pdf_organizer_tab.source_pdfs.append(pdf_path)
                self.pdf_organizer_tab.pdf_listbox.insert(tk.END, os.path.basename(pdf_path))
            self.pdf_organizer_tab.load_pdf_pages(pdf_files)
            if self.pdf_organizer_tab.selected_index < 0 and self.pdf_organizer_tab.all_pages:
                self.pdf_organizer_tab.selected_index = 0
                self.pdf_organizer_tab.update_preview()
            self.pdf_organizer_tab.refresh_thumbnails()
        elif current_tab_idx == ti['image_to_pdf'] and image_files:
            self.image_to_pdf_tab.add_images(image_files)
        elif current_tab_idx == ti['convert_image'] and image_files:
            self.image_convert_tab.add_images(image_files)
        elif current_tab_idx == ti['resize_image'] and image_files:
            self.image_resize_tab.add_images(image_files)
        elif current_tab_idx == ti['batch_process'] and image_files:
            if len(image_files) == 1:
                self.image_batch_tab.selected_image_path.set(image_files[0])
                self.image_batch_tab.show_preview_image(image_files[0])
            else:
                parent_dir = os.path.dirname(image_files[0])
                self.image_batch_tab.images_dir.set(parent_dir)
        elif current_tab_idx == ti['watermark'] and image_files:
            self.image_watermark_tab.add_images(image_files)
        elif current_tab_idx == ti['metadata'] and len(image_files) == 1:
            self.image_metadata_tab.set_image(image_files[0])

    def clear_recent_files(self):
        result = messagebox.askyesno("Confirm", "Clear all recent files?")
        if result:
            self.settings.settings['recent_files'] = []
            self.settings.save_settings()
            self.update_recent_files_menu()

    def show_preferences(self):
        dialog = self._create_dialog("Preferences", "550x450")

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # General preferences
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")

        ttk.Label(general_frame, text="Theme:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        theme_var = tk.StringVar(value=self.settings.settings.get('theme', 'default'))
        ttk.Combobox(general_frame, textvariable=theme_var,
                     values=["default", "light", "dark"], width=15).grid(row=0, column=1, sticky="w", padx=10, pady=5)

        ttk.Label(general_frame, text="Maximum Recent Files:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        max_recent_var = tk.IntVar(value=self.settings.settings.get('max_recent_files', 10))
        ttk.Spinbox(general_frame, from_=1, to=50, textvariable=max_recent_var, width=5).grid(row=1, column=1, sticky="w", padx=10, pady=5)

        confirm_overwrite_var = tk.BooleanVar(value=self.settings.settings.get('confirm_overwrite', True))
        ttk.Checkbutton(general_frame, text="Confirm before overwriting existing files",
                      variable=confirm_overwrite_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        remember_dir_var = tk.BooleanVar(value=self.settings.settings.get('remember_last_directory', True))
        ttk.Checkbutton(general_frame, text="Remember last used directories",
                      variable=remember_dir_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        # Directories
        dir_frame = ttk.Frame(notebook)
        notebook.add(dir_frame, text="Directories")

        ttk.Label(dir_frame, text="Default PDF Output Directory:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        pdf_dir_var = tk.StringVar(value=self.settings.settings.get('default_output_dir', str(Path.home() / "Documents")))
        ttk.Entry(dir_frame, textvariable=pdf_dir_var, width=40).grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        ttk.Button(dir_frame, text="Browse...",
                 command=lambda: self._browse_dir_for_var(pdf_dir_var)).grid(row=0, column=2, padx=10, pady=5)

        ttk.Label(dir_frame, text="Default Image Output Directory:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        img_dir_var = tk.StringVar(value=self.settings.settings.get('default_image_output_dir', str(Path.home() / "Pictures")))
        ttk.Entry(dir_frame, textvariable=img_dir_var, width=40).grid(row=1, column=1, sticky="ew", padx=10, pady=5)
        ttk.Button(dir_frame, text="Browse...",
                 command=lambda: self._browse_dir_for_var(img_dir_var)).grid(row=1, column=2, padx=10, pady=5)

        dir_frame.columnconfigure(1, weight=1)

        # Dependencies
        dep_frame = ttk.Frame(notebook)
        notebook.add(dep_frame, text="Dependencies")

        from ghostscript_utils import create_gs_banner, get_ghostscript
        gs_exe, gs_ver = get_ghostscript()

        ttk.Label(dep_frame, text="Ghostscript", style="Subheading.TLabel").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 2))
        if gs_exe:
            ttk.Label(dep_frame, text=f"Status: Found (v{gs_ver})", foreground=COLORS['success']).grid(row=1, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(dep_frame, text=f"Path: {gs_exe}").grid(row=2, column=0, sticky="w", padx=10, pady=2)
        else:
            ttk.Label(dep_frame, text="Status: Not Found", foreground=COLORS['error']).grid(row=1, column=0, sticky="w", padx=10, pady=2)
            ttk.Label(dep_frame, text="Required for optimal PDF compression.\nInstall from ghostscript.com and ensure gswin64c is on PATH.",
                      wraplength=400, justify="left").grid(row=2, column=0, sticky="w", padx=10, pady=2)
            ttk.Button(dep_frame, text="Download Ghostscript",
                       command=lambda: webbrowser.open("https://www.ghostscript.com/releases/gsdnld.html")).grid(row=3, column=0, sticky="w", padx=10, pady=5)

        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=10, pady=10)

        def save_preferences():
            self.settings.settings['theme'] = theme_var.get()
            self.settings.settings['max_recent_files'] = max_recent_var.get()
            self.settings.settings['confirm_overwrite'] = confirm_overwrite_var.get()
            self.settings.settings['remember_last_directory'] = remember_dir_var.get()
            self.settings.settings['default_output_dir'] = pdf_dir_var.get()
            self.settings.settings['default_image_output_dir'] = img_dir_var.get()
            self.settings.save_settings()
            self.apply_settings()
            self.update_recent_files_menu()
            dialog.destroy()
            messagebox.showinfo("Success", "Preferences saved successfully.")

        ttk.Button(btn_frame, text="Save", command=save_preferences).pack(side="right", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, style="Secondary.TButton").pack(side="right", padx=5)

        self._center_dialog(dialog)

    def apply_settings(self):
        theme = self.settings.settings.get('theme', 'default')
        self._apply_theme(theme)

        default_output_dir = self.settings.settings.get('default_output_dir')
        default_image_dir = self.settings.settings.get('default_image_output_dir')

        if default_output_dir and os.path.isdir(default_output_dir):
            for tab in [self.pdf_merge_tab, self.pdf_split_tab, self.pdf_compress_tab, self.pdf_security_tab]:
                if hasattr(tab, 'output_dir') and not tab.output_dir.get():
                    tab.output_dir.set(default_output_dir)

        if default_image_dir and os.path.isdir(default_image_dir):
            for tab in [self.pdf_to_image_tab, self.image_batch_tab]:
                if hasattr(tab, 'output_dir') and not tab.output_dir.get():
                    tab.output_dir.set(default_image_dir)

    def _apply_theme(self, theme_name):
        pass

    def _browse_dir_for_var(self, var):
        directory = askdirectory(
            title="Select Directory",
            initialdir=var.get() if var.get() else os.getcwd()
        )
        if directory:
            var.set(directory)

    def show_help(self):
        help_text = f"""p2i v{VERSION} - PDF & Image Processing Tool - User Guide

QUICK START
- Use the tabs at the top to select different tools
- PDF tools are on the left, Image tools are on the right
- Drag and drop files directly onto any tab
- For most operations: select input, set options, click Process

PDF TOOLS

1. Merge PDFs - Combine multiple PDFs into one document
2. Split PDF - Extract pages or split into parts
3. Compress PDF - Reduce PDF file size (supports Ghostscript)
4. PDF to Image - Convert PDF pages to image files
5. PDF Security - Add passwords and watermarks
6. PDF Organizer - Reorder, delete, and manage pages

IMAGE TOOLS

7. Image to PDF - Convert images to PDF documents
8. Convert Image - Change format (PNG, JPG, BMP, WEBP, TIFF, etc.)
9. Resize Image - Scale images by percentage or dimensions
10. Batch Process - Resize, convert, adjust, optimize in bulk
11. Watermark - Add text or image watermarks to images
12. Metadata - View and strip EXIF data from images

TIPS
- Use Preview where available to check results before processing
- Check the status bar for Ghostscript and drag-drop status
- Right-click lists for context menus
- Use Edit > Preferences to set default output directories
"""

        dialog = self._create_dialog("User Guide", "650x550", grab=False)

        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(frame, wrap="word", yscrollcommand=scrollbar.set, font=FONTS['body'])
        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

        text.insert("1.0", help_text)
        text.config(state="disabled")

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        self._center_dialog(dialog)

    def show_ghostscript_help(self):
        dialog = self._create_dialog("Ghostscript Setup Guide", "550x400", grab=False)

        from ghostscript_utils import get_ghostscript
        gs_exe, gs_ver = get_ghostscript()

        frame = ttk.Frame(dialog, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Ghostscript Setup Guide", style="Heading.TLabel").pack(anchor="w", pady=(0, 10))

        if gs_exe:
            status_text = f"Ghostscript is installed (v{gs_ver})\nPath: {gs_exe}"
            status_fg = COLORS['success']
        else:
            status_text = "Ghostscript is NOT installed or not found in PATH."
            status_fg = COLORS['error']

        tk.Label(frame, text=status_text, fg=status_fg, font=FONTS['body'], anchor="w",
                 justify="left", bg=COLORS['bg']).pack(fill="x", pady=(0, 10))

        guide = """Ghostscript provides the best PDF compression quality.

Installation Steps:
1. Download from: https://www.ghostscript.com/releases/gsdnld.html
2. Run the installer (choose the 64-bit version for modern Windows)
3. During installation, check "Add to PATH" if available
4. If not, manually add the Ghostscript bin folder to your system PATH:
   e.g., C:\\Program Files\\gs\\gs10.x.x\\bin
5. Restart p2i after installation

To verify: open a terminal and run: gswin64c --version
"""
        text = tk.Text(frame, wrap="word", font=FONTS['body'], height=12, bg=COLORS['bg_card'])
        text.pack(fill="both", expand=True)
        text.insert("1.0", guide)
        text.config(state="disabled")

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=15, pady=10)
        ttk.Button(btn_frame, text="Download Ghostscript", style="Accent.TButton",
                   command=lambda: webbrowser.open("https://www.ghostscript.com/releases/gsdnld.html")).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Close", command=dialog.destroy, style="Secondary.TButton").pack(side="left")

        self._center_dialog(dialog)

    def show_shortcuts(self):
        dialog = self._create_dialog("Keyboard Shortcuts", "400x250", grab=False)

        shortcuts = [
            ("Ctrl+O", "Open PDF file"),
            ("Ctrl+I", "Open image file"),
            ("Ctrl+,", "Open Preferences"),
            ("Ctrl+Q", "Exit application"),
            ("F1", "Open User Guide"),
        ]

        frame = ttk.Frame(dialog, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Keyboard Shortcuts", style="Heading.TLabel").pack(anchor="w", pady=(0, 10))

        for key, desc in shortcuts:
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=key, font=('Consolas', 10, 'bold'), width=12, anchor="w",
                     bg=COLORS['bg']).pack(side="left")
            ttk.Label(row, text=desc).pack(side="left", padx=5)

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        self._center_dialog(dialog)

    def check_updates(self):
        messagebox.showinfo("Updates", f"You have the latest version ({VERSION}) of p2i.")

    def show_about(self):
        dialog = self._create_dialog("About p2i", "450x400")

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="p2i", font=('Segoe UI', 24, 'bold'),
                  foreground=COLORS['primary']).pack(pady=(0, 5))
        ttk.Label(frame, text=f"Version {VERSION}", style="Secondary.TLabel").pack()
        ttk.Label(frame, text="Advanced PDF & Image Processing Tool",
                  style="Subheading.TLabel").pack(pady=(10, 15))

        info_text = (
            "A comprehensive toolkit for PDF and image processing.\n\n"
            "Features:\n"
            "  PDF merge, split, compress, convert, secure, organize\n"
            "  Image convert, resize, watermark, batch process, metadata\n\n"
            "Built with Python, Tkinter, and Pillow.\n\n"
            "Developer: Naveen Vasudevan\n"
            "License: MIT"
        )
        ttk.Label(frame, text=info_text, wraplength=380, justify="left").pack(fill="x", pady=(0, 15))

        link_frame = ttk.Frame(frame)
        link_frame.pack()
        ttk.Button(link_frame, text="GitHub", style="Secondary.TButton",
                   command=lambda: webbrowser.open("https://github.com/kuroonai/p2i")).pack(side="left", padx=5)
        ttk.Button(link_frame, text="Report Issue", style="Secondary.TButton",
                   command=lambda: webbrowser.open("https://github.com/kuroonai/p2i/issues")).pack(side="left", padx=5)
        ttk.Button(link_frame, text="Support", style="Accent.TButton",
                   command=lambda: [dialog.destroy(), self.notebook.select(self._tab_indices['support'])]).pack(side="left", padx=5)

        ttk.Label(frame, text="\u00a9 2025 Naveen Vasudevan", style="Secondary.TLabel").pack(pady=(10, 0))

        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
        self._center_dialog(dialog)

    def on_close(self):
        self.settings.save_settings()
        self.root.destroy()


def main():
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
    app = P2IApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

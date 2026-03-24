import os
import threading
import tempfile
import shutil
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pypdfium2 as pdfium
from PIL import Image
import utils
from styles import COLORS, FONTS
from ghostscript_utils import create_gs_banner, get_ghostscript

try:
    from PyPDF2 import PdfReader, PdfWriter
    HAVE_PYPDF2 = True
except ImportError:
    HAVE_PYPDF2 = False


class PDFCompressTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.parent = parent

        # Variables
        self.pdf_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.output_name = tk.StringVar(value="compressed.pdf")
        self.compress_level = tk.StringVar(value="medium")
        self.compress_method = tk.StringVar(value="auto")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.conversion_canceled = False

        # Advanced options
        self.image_dpi = tk.IntVar(value=150)
        self.image_quality = tk.IntVar(value=75)
        self.remove_metadata = tk.BooleanVar(value=False)
        self.remove_bookmarks = tk.BooleanVar(value=False)
        self.linearize = tk.BooleanVar(value=False)
        self.subset_fonts = tk.BooleanVar(value=False)

        # Create UI
        self._create_gs_banner()
        self.create_file_frame()
        self.create_options_frame()
        self.create_advanced_frame()
        self.create_result_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(
            self.frame,
            self.start_compression,
            self.cancel_compression,
            self.open_output_folder,
            "Compress PDF"
        )

        self.output_dir.set(os.path.join(str(Path.home()), "Documents"))

        if not HAVE_PYPDF2:
            self.status_var.set("Warning: PyPDF2 not found. Direct compression unavailable.")

    def _create_gs_banner(self):
        """Show Ghostscript status banner at top of tab."""
        banner = create_gs_banner(self.frame)
        banner.pack(fill="x", padx=10, pady=(5, 0))

    def create_file_frame(self):
        file_frame = ttk.LabelFrame(self.frame, text="PDF Selection", padding=10)
        file_frame.pack(fill="x", expand=False, padx=10, pady=5)

        ttk.Label(file_frame, text="PDF File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.pdf_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_pdf).grid(row=0, column=2, sticky="e", padx=5, pady=5)

        ttk.Label(file_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self.browse_output_dir).grid(row=1, column=2, sticky="e", padx=5, pady=5)

        ttk.Label(file_frame, text="Output Filename:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_name, width=50).grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        self.file_size_label = ttk.Label(file_frame, text="Original Size: -")
        self.file_size_label.grid(row=3, column=0, columnspan=3, sticky="w", padx=5, pady=5)

        file_frame.columnconfigure(1, weight=1)

    def create_options_frame(self):
        options_frame = ttk.LabelFrame(self.frame, text="Compression Preset", padding=10)
        options_frame.pack(fill="x", expand=False, padx=10, pady=5)

        # Preset buttons in a row
        preset_frame = ttk.Frame(options_frame)
        preset_frame.pack(fill="x", pady=(0, 5))

        presets = [
            ("Low", "low", "Better quality, larger file"),
            ("Medium", "medium", "Balanced quality and size"),
            ("High", "high", "Smaller file, lower quality"),
            ("Custom", "custom", "Configure all settings manually"),
        ]

        for text, val, desc in presets:
            f = ttk.Frame(preset_frame)
            f.pack(side="left", padx=(0, 12))
            ttk.Radiobutton(f, text=text, variable=self.compress_level, value=val,
                            command=self._on_preset_change).pack(anchor="w")
            ttk.Label(f, text=desc, style="Secondary.TLabel").pack(anchor="w")

        # Compression method
        method_frame = ttk.Frame(options_frame)
        method_frame.pack(fill="x", pady=(5, 0))

        ttk.Label(method_frame, text="Method:").pack(side="left", padx=(0, 8))
        for text, val in [("Auto", "auto"), ("Ghostscript", "ghostscript"),
                          ("Image-based", "image"), ("Direct (PyPDF2)", "direct")]:
            ttk.Radiobutton(method_frame, text=text, variable=self.compress_method,
                            value=val).pack(side="left", padx=(0, 10))

    def create_advanced_frame(self):
        self.advanced_frame = ttk.LabelFrame(self.frame, text="Advanced Options (Custom Preset)", padding=10)
        self.advanced_frame.pack(fill="x", expand=False, padx=10, pady=5)

        row0 = ttk.Frame(self.advanced_frame)
        row0.pack(fill="x", pady=2)
        ttk.Label(row0, text="Image DPI:").pack(side="left", padx=(0, 5))
        self.dpi_spin = ttk.Spinbox(row0, from_=36, to=600, textvariable=self.image_dpi, width=6)
        self.dpi_spin.pack(side="left", padx=(0, 20))
        ttk.Label(row0, text="Image Quality:").pack(side="left", padx=(0, 5))
        self.quality_scale = ttk.Scale(row0, from_=10, to=100, variable=self.image_quality, orient="horizontal")
        self.quality_scale.pack(side="left", fill="x", expand=True)
        self._quality_label = ttk.Label(row0, text=str(self.image_quality.get()), width=4)
        self._quality_label.pack(side="left", padx=5)
        self.image_quality.trace_add("write", lambda *_: self._quality_label.config(text=str(self.image_quality.get())))

        row1 = ttk.Frame(self.advanced_frame)
        row1.pack(fill="x", pady=5)
        ttk.Checkbutton(row1, text="Remove metadata", variable=self.remove_metadata).pack(side="left", padx=(0, 15))
        ttk.Checkbutton(row1, text="Remove bookmarks", variable=self.remove_bookmarks).pack(side="left", padx=(0, 15))
        ttk.Checkbutton(row1, text="Linearize (fast web view)", variable=self.linearize).pack(side="left", padx=(0, 15))
        ttk.Checkbutton(row1, text="Subset fonts", variable=self.subset_fonts).pack(side="left")

        # Initially disable advanced frame if not custom
        self._on_preset_change()

    def create_result_frame(self):
        """Frame showing before/after size comparison."""
        self.result_frame = ttk.LabelFrame(self.frame, text="Compression Result", padding=10)
        self.result_frame.pack(fill="x", expand=False, padx=10, pady=5)

        cols = ttk.Frame(self.result_frame)
        cols.pack(fill="x")

        # Before
        before_frame = ttk.Frame(cols)
        before_frame.pack(side="left", expand=True, fill="x")
        ttk.Label(before_frame, text="Original", style="Subheading.TLabel").pack()
        self.before_size_label = ttk.Label(before_frame, text="-", font=('Segoe UI', 14))
        self.before_size_label.pack()

        # Arrow
        ttk.Label(cols, text="\u2192", font=('Segoe UI', 18)).pack(side="left", padx=15)

        # After
        after_frame = ttk.Frame(cols)
        after_frame.pack(side="left", expand=True, fill="x")
        ttk.Label(after_frame, text="Compressed", style="Subheading.TLabel").pack()
        self.after_size_label = ttk.Label(after_frame, text="-", font=('Segoe UI', 14))
        self.after_size_label.pack()

        # Reduction
        ttk.Label(cols, text="=", font=('Segoe UI', 18)).pack(side="left", padx=15)

        reduction_frame = ttk.Frame(cols)
        reduction_frame.pack(side="left", expand=True, fill="x")
        ttk.Label(reduction_frame, text="Reduction", style="Subheading.TLabel").pack()
        self.reduction_label = ttk.Label(reduction_frame, text="-", font=('Segoe UI', 14, 'bold'),
                                         foreground=COLORS['success'])
        self.reduction_label.pack()

    def _on_preset_change(self):
        """Update advanced options based on preset selection."""
        level = self.compress_level.get()
        is_custom = (level == "custom")

        # Enable/disable advanced frame
        for w in self.advanced_frame.winfo_children():
            utils.set_controls_state(w, tk.NORMAL if is_custom else tk.DISABLED)

        # Apply preset values
        if level == "low":
            self.image_dpi.set(200)
            self.image_quality.set(85)
        elif level == "medium":
            self.image_dpi.set(150)
            self.image_quality.set(70)
        elif level == "high":
            self.image_dpi.set(96)
            self.image_quality.set(45)

    def browse_pdf(self):
        selected_file = filedialog.askopenfilename(
            title="Select PDF File to Compress",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if selected_file:
            self.pdf_path.set(selected_file)
            self.status_var.set(f"Selected: {os.path.basename(selected_file)}")
            self.update_file_size_info()

            pdf_basename = os.path.splitext(os.path.basename(selected_file))[0]
            self.output_name.set(f"{pdf_basename}_compressed.pdf")

            if HAVE_PYPDF2:
                threading.Thread(target=self._analyze_pdf, daemon=True).start()

    def _analyze_pdf(self):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Analyzing PDF content..."))

            reader = PdfReader(self.pdf_path.get())
            total_size = os.path.getsize(self.pdf_path.get())
            image_size = 0

            for page in reader.pages:
                if "/Resources" in page and "/XObject" in page["/Resources"]:
                    x_objects = page["/Resources"]["/XObject"].get_object()
                    for obj in x_objects:
                        if x_objects[obj]["/Subtype"] == "/Image":
                            if "/Length" in x_objects[obj]:
                                image_size += x_objects[obj]["/Length"]

            self._image_ratio = image_size / total_size if total_size > 0 else 0

            if self._image_ratio > 0.5:
                suggestion = "Image-heavy PDF detected (Ghostscript or image-based recommended)"
            else:
                suggestion = "Text-heavy PDF detected (Direct/PyPDF2 recommended)"

            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Analysis: {suggestion}"))
        except Exception as e:
            error_msg = str(e)
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Analysis error: {error_msg}"))

    def browse_output_dir(self):
        selected_dir = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_dir.get() if self.output_dir.get() else os.getcwd()
        )
        if selected_dir:
            self.output_dir.set(selected_dir)

    def update_file_size_info(self):
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            return

        file_size = os.path.getsize(self.pdf_path.get())
        formatted = utils.format_file_size(file_size)
        self.file_size_label.config(text=f"Original Size: {formatted}")
        self.before_size_label.config(text=formatted)
        self.after_size_label.config(text="-")
        self.reduction_label.config(text="-")

    def start_compression(self):
        if not self.pdf_path.get() or not os.path.isfile(self.pdf_path.get()):
            messagebox.showerror("Error", "Please select a valid PDF file.")
            return

        if not self.output_dir.get() or not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory.")
            return

        if not self.output_name.get():
            messagebox.showerror("Error", "Please enter a name for the output PDF file.")
            return

        pdf_filename = self.output_name.get()
        if not pdf_filename.lower().endswith('.pdf'):
            pdf_filename += ".pdf"

        output_path = os.path.join(self.output_dir.get(), pdf_filename)

        if os.path.exists(output_path):
            result = messagebox.askyesno("Confirm", f"File {pdf_filename} already exists. Overwrite?")
            if not result:
                return

        utils.set_controls_state(self.frame, tk.DISABLED)

        method = self.compress_method.get()
        if method == "auto":
            gs_exe, _ = get_ghostscript()
            if gs_exe:
                method = "ghostscript"
            elif hasattr(self, "_image_ratio") and self._image_ratio > 0.5:
                method = "image"
            else:
                method = "direct" if HAVE_PYPDF2 else "image"

        self.conversion_canceled = False
        threading.Thread(target=self._compression_thread, args=(output_path, method), daemon=True).start()

    def _compression_thread(self, output_path, method):
        try:
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Compressing ({method})..."))
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(0))

            if method == "ghostscript":
                self._gs_compress_pdf(output_path)
            elif method == "direct" and HAVE_PYPDF2:
                self._direct_compress_pdf(output_path)
            else:
                self._image_compress_pdf(output_path)

            # Show results
            original_size = os.path.getsize(self.pdf_path.get())
            compressed_size = os.path.getsize(output_path)
            orig_fmt = utils.format_file_size(original_size)
            comp_fmt = utils.format_file_size(compressed_size)
            reduction = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0

            def show_result():
                self.before_size_label.config(text=orig_fmt)
                self.after_size_label.config(text=comp_fmt)
                if reduction > 0:
                    self.reduction_label.config(text=f"-{reduction:.1f}%", foreground=COLORS['success'])
                else:
                    self.reduction_label.config(text=f"+{abs(reduction):.1f}%", foreground=COLORS['error'])
                self.progress_var.set(100)
                self.status_var.set(f"Done: {os.path.basename(output_path)}")
                messagebox.showinfo("Success",
                    f"Compression complete!\n\n"
                    f"Original: {orig_fmt}\n"
                    f"Compressed: {comp_fmt}\n"
                    f"Reduction: {reduction:.1f}%\n"
                    f"Saved to: {output_path}")

            self.frame.winfo_toplevel().after(0, show_result)

        except Exception as e:
            error_msg = str(e)
            self.frame.winfo_toplevel().after(0, lambda: messagebox.showerror("Error", f"Compression failed: {error_msg}"))
            self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Error: {error_msg}"))
            if os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except Exception:
                    pass
        finally:
            self.frame.winfo_toplevel().after(0, lambda: utils.set_controls_state(self.frame, tk.NORMAL))

    def _direct_compress_pdf(self, output_path):
        reader = PdfReader(self.pdf_path.get())
        writer = PdfWriter()

        quality = self.image_quality.get()
        total_pages = len(reader.pages)

        for i, page in enumerate(reader.pages):
            if self.conversion_canceled:
                self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Canceled"))
                return

            progress_pct = ((i + 1) / total_pages) * 100
            current_page = i + 1
            self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
            self.frame.winfo_toplevel().after(0, lambda p=current_page, t=total_pages:
                self.status_var.set(f"Processing page {p}/{t}..."))

            writer.add_page(page)
            writer.compress_content_streams = True

        # Remove metadata if requested
        if self.remove_metadata.get():
            writer.add_metadata({})

        with open(output_path, "wb") as f:
            writer.write(f)

    def _image_compress_pdf(self, output_path):
        pdf = pdfium.PdfDocument(self.pdf_path.get())
        page_count = len(pdf)

        dpi = self.image_dpi.get()
        quality = self.image_quality.get()

        with tempfile.TemporaryDirectory() as temp_dir:
            for page_idx in range(page_count):
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Canceled"))
                    return

                progress_pct = ((page_idx + 1) / (page_count * 2)) * 100
                current_page = page_idx + 1
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=current_page:
                    self.status_var.set(f"Rendering page {p}/{page_count}..."))

                page = pdf[page_idx]
                pil_image = page.render(scale=dpi / 72, rotation=0).to_pil()

                # Convert to grayscale for high compression if not color-critical
                level = self.compress_level.get()
                if level == "high" and not self._is_color_critical(pil_image):
                    pil_image = pil_image.convert('L')

                if max(pil_image.size) > 2000 and level in ["medium", "high"]:
                    factor = 2000 / max(pil_image.size)
                    new_size = (int(pil_image.size[0] * factor), int(pil_image.size[1] * factor))
                    pil_image = pil_image.resize(new_size, Image.LANCZOS)

                img_path = os.path.join(temp_dir, f"page_{page_idx}.jpg")
                pil_image.save(img_path, format="JPEG", quality=quality, optimize=True)

            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader

            c = canvas.Canvas(output_path)

            for page_idx in range(page_count):
                if self.conversion_canceled:
                    self.frame.winfo_toplevel().after(0, lambda: self.status_var.set("Canceled"))
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except Exception:
                            pass
                    return

                progress_pct = (((page_idx + 1) / page_count) * 50) + 50
                current_page = page_idx + 1
                self.frame.winfo_toplevel().after(0, lambda p=progress_pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0, lambda p=current_page:
                    self.status_var.set(f"Creating page {p}/{page_count}..."))

                img_path = os.path.join(temp_dir, f"page_{page_idx}.jpg")
                img = Image.open(img_path)

                orig_page = pdf[page_idx]
                width, height = orig_page.get_size()
                c.setPageSize((width, height))
                if page_idx > 0:
                    c.showPage()
                c.drawImage(ImageReader(img), 0, 0, width=width, height=height)

            if self.remove_metadata.get():
                c.setAuthor("")
                c.setCreator("")
                c.setTitle("")
                c.setSubject("")

            c.save()

    def _is_color_critical(self, img):
        try:
            pixels = img.getdata()
            sample_size = min(1000, len(pixels))
            stride = max(1, len(pixels) // sample_size)
            sampled_pixels = [pixels[i] for i in range(0, len(pixels), stride)]
            color_variance = sum(
                abs(p[0] - p[1]) + abs(p[1] - p[2]) + abs(p[0] - p[2])
                for p in sampled_pixels if len(p) >= 3
            ) / len(sampled_pixels)
            return color_variance > 30
        except Exception:
            return True

    def _gs_compress_pdf(self, output_path):
        import subprocess

        gs_exe, _ = get_ghostscript()
        if not gs_exe:
            raise RuntimeError("Ghostscript not found. Install it or use a different compression method.")

        level = self.compress_level.get()
        if level == "custom":
            dpi = str(self.image_dpi.get())
            # Map quality to GS preset
            q = self.image_quality.get()
            if q >= 80:
                preset = "printer"
            elif q >= 50:
                preset = "ebook"
            else:
                preset = "screen"
        elif level == "low":
            preset = "printer"
            dpi = "200"
        elif level == "medium":
            preset = "ebook"
            dpi = "150"
        else:  # high
            preset = "screen"
            dpi = "72"

        self.frame.winfo_toplevel().after(0, lambda: self.status_var.set(f"Compressing with Ghostscript ({preset})..."))

        gs_cmd = [
            gs_exe,
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS=/" + preset,
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-r{dpi}",
        ]

        if self.remove_metadata.get():
            gs_cmd.append("-dFastWebView=false")

        if self.linearize.get():
            gs_cmd.append("-dFastWebView=true")

        if self.subset_fonts.get():
            gs_cmd.append("-dSubsetFonts=true")
            gs_cmd.append("-dEmbedAllFonts=true")

        gs_cmd.extend([
            "-sOutputFile=" + output_path,
            self.pdf_path.get()
        ])

        try:
            subprocess.run(gs_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.frame.winfo_toplevel().after(0, lambda: self.progress_var.set(100))
        except subprocess.SubprocessError as e:
            raise RuntimeError(f"Ghostscript error: {e}")

    def cancel_compression(self):
        self.conversion_canceled = True
        self.status_var.set("Canceling...")

    def open_output_folder(self):
        utils.open_output_folder(self.output_dir.get())

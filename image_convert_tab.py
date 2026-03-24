# image_convert_tab.py - Image format conversion tab
import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import utils
from styles import COLORS, FONTS


SUPPORTED_FORMATS = {
    "JPEG": {"ext": ".jpg", "modes": ["RGB"]},
    "PNG": {"ext": ".png", "modes": ["RGB", "RGBA", "L", "P"]},
    "BMP": {"ext": ".bmp", "modes": ["RGB", "L"]},
    "WEBP": {"ext": ".webp", "modes": ["RGB", "RGBA"]},
    "TIFF": {"ext": ".tiff", "modes": ["RGB", "RGBA", "L", "CMYK"]},
    "GIF": {"ext": ".gif", "modes": ["RGB", "L", "P"]},
    "ICO": {"ext": ".ico", "modes": ["RGB", "RGBA"]},
}

INPUT_EXTENSIONS = "*.jpg *.jpeg *.png *.bmp *.webp *.tiff *.tif *.gif *.ico"


class ImageConvertTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.parent = parent

        # Variables
        self.input_files = []
        self.output_dir = tk.StringVar()
        self.output_format = tk.StringVar(value="PNG")
        self.jpg_quality = tk.IntVar(value=90)
        self.webp_quality = tk.IntVar(value=85)
        self.png_compression = tk.IntVar(value=6)
        self.preserve_transparency = tk.BooleanVar(value=True)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.conversion_canceled = False

        self._create_ui()

        self.output_dir.set(os.path.join(str(Path.home()), "Pictures", "Converted"))

    def _create_ui(self):
        # File selection
        file_frame = ttk.LabelFrame(self.frame, text="Image Selection", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        btn_row = ttk.Frame(file_frame)
        btn_row.pack(fill="x", pady=(0, 5))
        ttk.Button(btn_row, text="Add Images", command=self._browse_images).pack(side="left", padx=(0, 5))
        ttk.Button(btn_row, text="Add Folder", command=self._browse_folder).pack(side="left", padx=(0, 5))
        ttk.Button(btn_row, text="Clear All", command=self._clear_files, style="Secondary.TButton").pack(side="left")
        self.file_count_label = ttk.Label(btn_row, text="0 images selected")
        self.file_count_label.pack(side="right")

        # Listbox for files
        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill="both", expand=False)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox = tk.Listbox(list_frame, height=4, yscrollcommand=scrollbar.set,
                                       font=FONTS['body_small'], selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Output settings
        out_frame = ttk.LabelFrame(self.frame, text="Output Settings", padding=10)
        out_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(out_frame, text="Output Format:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        fmt_combo = ttk.Combobox(out_frame, textvariable=self.output_format,
                                 values=list(SUPPORTED_FORMATS.keys()), width=12, state="readonly")
        fmt_combo.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        fmt_combo.bind("<<ComboboxSelected>>", self._on_format_change)

        # Quality options frame
        self.quality_frame = ttk.Frame(out_frame)
        self.quality_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        self._build_quality_options()

        ttk.Checkbutton(out_frame, text="Preserve transparency (convert to RGBA when possible)",
                        variable=self.preserve_transparency).grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=2)

        ttk.Label(out_frame, text="Output Directory:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(out_frame, textvariable=self.output_dir, width=50).grid(row=3, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(out_frame, text="Browse...", command=self._browse_output).grid(row=3, column=2, padx=5, pady=5)
        out_frame.columnconfigure(1, weight=1)

        # Progress and buttons
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(self.frame, self._start, self._cancel, self._open_output, "Convert Images")

    def _build_quality_options(self):
        for w in self.quality_frame.winfo_children():
            w.destroy()

        fmt = self.output_format.get()
        if fmt in ("JPEG",):
            ttk.Label(self.quality_frame, text="JPEG Quality:").pack(side="left", padx=(0, 5))
            ttk.Scale(self.quality_frame, from_=10, to=100, variable=self.jpg_quality,
                      orient="horizontal").pack(side="left", fill="x", expand=True)
            self._quality_val_label = ttk.Label(self.quality_frame, text=str(self.jpg_quality.get()))
            self._quality_val_label.pack(side="left", padx=5)
            self.jpg_quality.trace_add("write", lambda *_: self._quality_val_label.config(text=str(self.jpg_quality.get())))
        elif fmt == "WEBP":
            ttk.Label(self.quality_frame, text="WebP Quality:").pack(side="left", padx=(0, 5))
            ttk.Scale(self.quality_frame, from_=10, to=100, variable=self.webp_quality,
                      orient="horizontal").pack(side="left", fill="x", expand=True)
            self._quality_val_label = ttk.Label(self.quality_frame, text=str(self.webp_quality.get()))
            self._quality_val_label.pack(side="left", padx=5)
            self.webp_quality.trace_add("write", lambda *_: self._quality_val_label.config(text=str(self.webp_quality.get())))
        elif fmt == "PNG":
            ttk.Label(self.quality_frame, text="PNG Compression (0-9):").pack(side="left", padx=(0, 5))
            ttk.Spinbox(self.quality_frame, from_=0, to=9, textvariable=self.png_compression, width=4).pack(side="left")
        else:
            ttk.Label(self.quality_frame, text="No quality options for this format",
                      style="Secondary.TLabel").pack(side="left")

    def _on_format_change(self, event=None):
        self._build_quality_options()

    def _browse_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", INPUT_EXTENSIONS), ("All Files", "*.*")]
        )
        if files:
            self._add_files(list(files))

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with Images")
        if folder:
            exts = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif", ".gif", ".ico")
            files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if os.path.splitext(f)[1].lower() in exts]
            self._add_files(files)

    def _add_files(self, files):
        existing = set(self.input_files)
        for f in files:
            if f not in existing:
                self.input_files.append(f)
                self.file_listbox.insert(tk.END, os.path.basename(f))
        self.file_count_label.config(text=f"{len(self.input_files)} images selected")

    def _clear_files(self):
        self.input_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.file_count_label.config(text="0 images selected")

    def _browse_output(self):
        d = filedialog.askdirectory(title="Select Output Directory")
        if d:
            self.output_dir.set(d)

    def _start(self):
        if not self.input_files:
            messagebox.showerror("Error", "Please add images to convert.")
            return
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory.")
            return

        os.makedirs(self.output_dir.get(), exist_ok=True)
        self.conversion_canceled = False
        utils.set_controls_state(self.frame, tk.DISABLED)
        threading.Thread(target=self._convert_thread, daemon=True).start()

    def _cancel(self):
        self.conversion_canceled = True

    def _open_output(self):
        utils.open_output_folder(self.output_dir.get())

    def _convert_thread(self):
        fmt = self.output_format.get()
        fmt_info = SUPPORTED_FORMATS[fmt]
        ext = fmt_info["ext"]
        total = len(self.input_files)
        converted = 0
        errors = []

        for i, filepath in enumerate(self.input_files):
            if self.conversion_canceled:
                break

            basename = os.path.splitext(os.path.basename(filepath))[0]
            out_path = os.path.join(self.output_dir.get(), basename + ext)

            try:
                img = Image.open(filepath)

                # Handle mode conversion
                if fmt == "JPEG":
                    if img.mode in ("RGBA", "P", "LA"):
                        bg = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        bg.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
                        img = bg
                    elif img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(out_path, "JPEG", quality=self.jpg_quality.get(), optimize=True)
                elif fmt == "PNG":
                    if self.preserve_transparency.get() and img.mode == "RGBA":
                        pass  # keep RGBA
                    elif img.mode not in ("RGB", "RGBA", "L", "P"):
                        img = img.convert("RGB")
                    img.save(out_path, "PNG", compress_level=self.png_compression.get())
                elif fmt == "WEBP":
                    if not self.preserve_transparency.get() and img.mode == "RGBA":
                        bg = Image.new("RGB", img.size, (255, 255, 255))
                        bg.paste(img, mask=img.split()[3])
                        img = bg
                    img.save(out_path, "WEBP", quality=self.webp_quality.get())
                elif fmt == "BMP":
                    if img.mode not in ("RGB", "L"):
                        img = img.convert("RGB")
                    img.save(out_path, "BMP")
                elif fmt == "TIFF":
                    img.save(out_path, "TIFF")
                elif fmt == "GIF":
                    if img.mode not in ("RGB", "L", "P"):
                        img = img.convert("RGB")
                    img.save(out_path, "GIF")
                elif fmt == "ICO":
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGBA")
                    img.save(out_path, "ICO", sizes=[(256, 256)])
                else:
                    img.save(out_path)

                converted += 1
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {e}")

            pct = ((i + 1) / total) * 100
            self.frame.winfo_toplevel().after(0, lambda p=pct: self.progress_var.set(p))
            self.frame.winfo_toplevel().after(0,
                lambda c=i+1, t=total: self.status_var.set(f"Converting {c}/{t}..."))

        # Done
        def finish():
            utils.set_controls_state(self.frame, tk.NORMAL)
            if self.conversion_canceled:
                self.status_var.set("Conversion canceled")
            else:
                msg = f"Converted {converted}/{total} images to {fmt}."
                if errors:
                    msg += f"\n\n{len(errors)} error(s):\n" + "\n".join(errors[:5])
                self.status_var.set(f"Done: {converted}/{total} converted")
                messagebox.showinfo("Complete", msg)

        self.frame.winfo_toplevel().after(0, finish)

    def add_images(self, files):
        """External interface for drag-and-drop."""
        self._add_files(files)

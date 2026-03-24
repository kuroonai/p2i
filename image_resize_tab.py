# image_resize_tab.py - Image resize/scale tab with aspect ratio control
import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import utils
from styles import COLORS, FONTS


class ImageResizeTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.parent = parent

        # Variables
        self.input_files = []
        self.output_dir = tk.StringVar()
        self.resize_mode = tk.StringVar(value="percentage")
        self.percentage = tk.IntVar(value=50)
        self.target_width = tk.IntVar(value=800)
        self.target_height = tk.IntVar(value=600)
        self.max_dimension = tk.IntVar(value=1920)
        self.maintain_aspect = tk.BooleanVar(value=True)
        self.resample_method = tk.StringVar(value="LANCZOS")
        self.output_format = tk.StringVar(value="Same as input")
        self.jpg_quality = tk.IntVar(value=90)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.conversion_canceled = False

        self._create_ui()
        self.output_dir.set(os.path.join(str(Path.home()), "Pictures", "Resized"))

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

        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill="both", expand=False)
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox = tk.Listbox(list_frame, height=3, yscrollcommand=scrollbar.set,
                                       font=FONTS['body_small'], selectmode=tk.EXTENDED)
        self.file_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # Resize options
        opts_frame = ttk.LabelFrame(self.frame, text="Resize Options", padding=10)
        opts_frame.pack(fill="x", padx=10, pady=5)

        # Mode selection
        mode_frame = ttk.Frame(opts_frame)
        mode_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(mode_frame, text="Resize Mode:").pack(side="left", padx=(0, 10))
        for text, val in [("By Percentage", "percentage"), ("Exact Dimensions", "dimensions"),
                          ("Max Dimension", "max_dimension")]:
            ttk.Radiobutton(mode_frame, text=text, variable=self.resize_mode,
                            value=val, command=self._update_options_visibility).pack(side="left", padx=(0, 12))

        # Options container
        self.opts_container = ttk.Frame(opts_frame)
        self.opts_container.pack(fill="x")
        self._update_options_visibility()

        # Resample method
        resample_frame = ttk.Frame(opts_frame)
        resample_frame.pack(fill="x", pady=(8, 0))
        ttk.Label(resample_frame, text="Resample:").pack(side="left", padx=(0, 5))
        ttk.Combobox(resample_frame, textvariable=self.resample_method,
                     values=["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"],
                     width=12, state="readonly").pack(side="left")

        ttk.Checkbutton(resample_frame, text="Maintain aspect ratio",
                        variable=self.maintain_aspect).pack(side="left", padx=(20, 0))

        # Output
        out_frame = ttk.LabelFrame(self.frame, text="Output", padding=10)
        out_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(out_frame, text="Format:").grid(row=0, column=0, sticky="w", padx=5, pady=3)
        ttk.Combobox(out_frame, textvariable=self.output_format,
                     values=["Same as input", "JPEG", "PNG", "WEBP", "BMP", "TIFF"],
                     width=14, state="readonly").grid(row=0, column=1, sticky="w", padx=5, pady=3)
        ttk.Label(out_frame, text="JPEG Quality:").grid(row=0, column=2, sticky="w", padx=(15, 5), pady=3)
        ttk.Spinbox(out_frame, from_=10, to=100, textvariable=self.jpg_quality, width=5).grid(row=0, column=3, sticky="w", padx=5, pady=3)

        ttk.Label(out_frame, text="Output Directory:").grid(row=1, column=0, sticky="w", padx=5, pady=3)
        ttk.Entry(out_frame, textvariable=self.output_dir, width=50).grid(row=1, column=1, columnspan=2, sticky="ew", padx=5, pady=3)
        ttk.Button(out_frame, text="Browse...", command=self._browse_output).grid(row=1, column=3, padx=5, pady=3)
        out_frame.columnconfigure(1, weight=1)

        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(self.frame, self._start, self._cancel, self._open_output, "Resize Images")

    def _update_options_visibility(self):
        for w in self.opts_container.winfo_children():
            w.destroy()

        mode = self.resize_mode.get()
        if mode == "percentage":
            f = ttk.Frame(self.opts_container)
            f.pack(fill="x")
            ttk.Label(f, text="Scale:").pack(side="left", padx=(0, 5))
            ttk.Scale(f, from_=5, to=200, variable=self.percentage,
                      orient="horizontal").pack(side="left", fill="x", expand=True)
            self._pct_label = ttk.Label(f, text=f"{self.percentage.get()}%", width=6)
            self._pct_label.pack(side="left", padx=5)
            self.percentage.trace_add("write", lambda *_: self._pct_label.config(text=f"{self.percentage.get()}%"))
        elif mode == "dimensions":
            f = ttk.Frame(self.opts_container)
            f.pack(fill="x")
            ttk.Label(f, text="Width:").pack(side="left", padx=(0, 3))
            ttk.Spinbox(f, from_=1, to=10000, textvariable=self.target_width, width=6).pack(side="left", padx=(0, 10))
            ttk.Label(f, text="Height:").pack(side="left", padx=(0, 3))
            ttk.Spinbox(f, from_=1, to=10000, textvariable=self.target_height, width=6).pack(side="left")
        elif mode == "max_dimension":
            f = ttk.Frame(self.opts_container)
            f.pack(fill="x")
            ttk.Label(f, text="Max dimension (px):").pack(side="left", padx=(0, 5))
            ttk.Spinbox(f, from_=16, to=10000, textvariable=self.max_dimension, width=7).pack(side="left")

    def _browse_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff *.tif *.gif"), ("All Files", "*.*")]
        )
        if files:
            self._add_files(list(files))

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            exts = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif", ".gif")
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
            messagebox.showerror("Error", "Please add images to resize.")
            return
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory.")
            return
        os.makedirs(self.output_dir.get(), exist_ok=True)
        self.conversion_canceled = False
        utils.set_controls_state(self.frame, tk.DISABLED)
        threading.Thread(target=self._resize_thread, daemon=True).start()

    def _cancel(self):
        self.conversion_canceled = True

    def _open_output(self):
        utils.open_output_folder(self.output_dir.get())

    def _get_resample_filter(self):
        methods = {
            "LANCZOS": Image.LANCZOS,
            "BICUBIC": Image.BICUBIC,
            "BILINEAR": Image.BILINEAR,
            "NEAREST": Image.NEAREST,
        }
        return methods.get(self.resample_method.get(), Image.LANCZOS)

    def _calc_new_size(self, orig_w, orig_h):
        mode = self.resize_mode.get()
        if mode == "percentage":
            pct = self.percentage.get() / 100.0
            return int(orig_w * pct), int(orig_h * pct)
        elif mode == "dimensions":
            tw, th = self.target_width.get(), self.target_height.get()
            if self.maintain_aspect.get():
                ratio = min(tw / orig_w, th / orig_h)
                return int(orig_w * ratio), int(orig_h * ratio)
            return tw, th
        elif mode == "max_dimension":
            max_dim = self.max_dimension.get()
            if max(orig_w, orig_h) <= max_dim:
                return orig_w, orig_h
            ratio = max_dim / max(orig_w, orig_h)
            return int(orig_w * ratio), int(orig_h * ratio)
        return orig_w, orig_h

    def _resize_thread(self):
        total = len(self.input_files)
        resized = 0
        errors = []
        resample = self._get_resample_filter()
        out_fmt = self.output_format.get()

        for i, filepath in enumerate(self.input_files):
            if self.conversion_canceled:
                break
            try:
                img = Image.open(filepath)
                new_w, new_h = self._calc_new_size(img.width, img.height)
                img = img.resize((max(1, new_w), max(1, new_h)), resample)

                basename = os.path.splitext(os.path.basename(filepath))[0]
                if out_fmt == "Same as input":
                    ext = os.path.splitext(filepath)[1]
                    out_path = os.path.join(self.output_dir.get(), basename + "_resized" + ext)
                    save_kwargs = {}
                    if ext.lower() in (".jpg", ".jpeg"):
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        save_kwargs["quality"] = self.jpg_quality.get()
                    img.save(out_path, **save_kwargs)
                else:
                    ext_map = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "BMP": ".bmp", "TIFF": ".tiff"}
                    ext = ext_map.get(out_fmt, ".png")
                    out_path = os.path.join(self.output_dir.get(), basename + "_resized" + ext)
                    if out_fmt == "JPEG":
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        img.save(out_path, "JPEG", quality=self.jpg_quality.get())
                    else:
                        img.save(out_path, out_fmt)
                resized += 1
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {e}")

            pct = ((i + 1) / total) * 100
            self.frame.winfo_toplevel().after(0, lambda p=pct: self.progress_var.set(p))
            self.frame.winfo_toplevel().after(0,
                lambda c=i+1, t=total: self.status_var.set(f"Resizing {c}/{t}..."))

        def finish():
            utils.set_controls_state(self.frame, tk.NORMAL)
            if self.conversion_canceled:
                self.status_var.set("Resize canceled")
            else:
                msg = f"Resized {resized}/{total} images."
                if errors:
                    msg += f"\n\n{len(errors)} error(s):\n" + "\n".join(errors[:5])
                self.status_var.set(f"Done: {resized}/{total} resized")
                messagebox.showinfo("Complete", msg)

        self.frame.winfo_toplevel().after(0, finish)

    def add_images(self, files):
        """External interface for drag-and-drop."""
        self._add_files(files)

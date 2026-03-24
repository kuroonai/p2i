# image_watermark_tab.py - Batch image watermarking (text or image overlay)
import os
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk, ImageEnhance
import utils
from styles import COLORS, FONTS


class ImageWatermarkTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.parent = parent

        # Variables
        self.input_files = []
        self.output_dir = tk.StringVar()
        self.watermark_type = tk.StringVar(value="text")
        self.text_content = tk.StringVar(value="Sample Watermark")
        self.font_size = tk.IntVar(value=36)
        self.text_color = tk.StringVar(value="#FFFFFF")
        self.opacity = tk.IntVar(value=128)
        self.position = tk.StringVar(value="center")
        self.rotation = tk.IntVar(value=0)
        self.tile_mode = tk.BooleanVar(value=False)
        self.watermark_image_path = tk.StringVar()
        self.wm_scale = tk.IntVar(value=30)  # % of image width
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.conversion_canceled = False

        # Preview
        self._preview_photo = None

        self._create_ui()
        self.output_dir.set(os.path.join(str(Path.home()), "Pictures", "Watermarked"))

    def _create_ui(self):
        # Main container with two columns
        top_pane = ttk.Frame(self.frame)
        top_pane.pack(fill="both", expand=True, padx=10, pady=5)

        left_col = ttk.Frame(top_pane)
        left_col.pack(side="left", fill="both", expand=True)

        # File selection
        file_frame = ttk.LabelFrame(left_col, text="Image Selection", padding=8)
        file_frame.pack(fill="x", pady=(0, 5))

        btn_row = ttk.Frame(file_frame)
        btn_row.pack(fill="x", pady=(0, 4))
        ttk.Button(btn_row, text="Add Images", command=self._browse_images).pack(side="left", padx=(0, 4))
        ttk.Button(btn_row, text="Clear", command=self._clear_files, style="Secondary.TButton").pack(side="left")
        self.file_count_label = ttk.Label(btn_row, text="0 images")
        self.file_count_label.pack(side="right")

        list_frame = ttk.Frame(file_frame)
        list_frame.pack(fill="both", expand=False)
        sb = ttk.Scrollbar(list_frame)
        sb.pack(side="right", fill="y")
        self.file_listbox = tk.Listbox(list_frame, height=3, yscrollcommand=sb.set, font=FONTS['body_small'])
        self.file_listbox.pack(fill="both", expand=True)
        sb.config(command=self.file_listbox.yview)

        # Watermark settings
        wm_frame = ttk.LabelFrame(left_col, text="Watermark Settings", padding=8)
        wm_frame.pack(fill="x", pady=5)

        # Type selection
        type_row = ttk.Frame(wm_frame)
        type_row.pack(fill="x", pady=(0, 5))
        ttk.Label(type_row, text="Type:").pack(side="left", padx=(0, 8))
        ttk.Radiobutton(type_row, text="Text", variable=self.watermark_type,
                        value="text", command=self._on_type_change).pack(side="left", padx=(0, 10))
        ttk.Radiobutton(type_row, text="Image", variable=self.watermark_type,
                        value="image", command=self._on_type_change).pack(side="left")

        # Text options
        self.text_opts = ttk.Frame(wm_frame)
        self.text_opts.pack(fill="x", pady=2)
        ttk.Label(self.text_opts, text="Text:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        ttk.Entry(self.text_opts, textvariable=self.text_content, width=30).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Label(self.text_opts, text="Font Size:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
        ttk.Spinbox(self.text_opts, from_=8, to=200, textvariable=self.font_size, width=6).grid(row=1, column=1, sticky="w", pady=2)
        self.text_opts.columnconfigure(1, weight=1)

        # Image options (hidden by default)
        self.img_opts = ttk.Frame(wm_frame)
        ttk.Label(self.img_opts, text="Image:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        ttk.Entry(self.img_opts, textvariable=self.watermark_image_path, width=25).grid(row=0, column=1, sticky="ew", pady=2)
        ttk.Button(self.img_opts, text="Browse...", command=self._browse_wm_image).grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(self.img_opts, text="Scale (%):").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
        ttk.Spinbox(self.img_opts, from_=5, to=100, textvariable=self.wm_scale, width=6).grid(row=1, column=1, sticky="w", pady=2)
        self.img_opts.columnconfigure(1, weight=1)

        # Common options
        common = ttk.Frame(wm_frame)
        common.pack(fill="x", pady=5)
        ttk.Label(common, text="Opacity:").grid(row=0, column=0, sticky="w", padx=(0, 5), pady=2)
        ttk.Scale(common, from_=0, to=255, variable=self.opacity, orient="horizontal").grid(row=0, column=1, sticky="ew", pady=2)
        self._opacity_label = ttk.Label(common, text=f"{self.opacity.get()}", width=4)
        self._opacity_label.grid(row=0, column=2, padx=5)
        self.opacity.trace_add("write", lambda *_: self._opacity_label.config(text=str(self.opacity.get())))

        ttk.Label(common, text="Position:").grid(row=1, column=0, sticky="w", padx=(0, 5), pady=2)
        ttk.Combobox(common, textvariable=self.position, width=14, state="readonly",
                     values=["center", "top-left", "top-right", "bottom-left", "bottom-right"]).grid(row=1, column=1, sticky="w", pady=2)
        ttk.Label(common, text="Rotation:").grid(row=2, column=0, sticky="w", padx=(0, 5), pady=2)
        ttk.Spinbox(common, from_=-180, to=180, textvariable=self.rotation, width=6).grid(row=2, column=1, sticky="w", pady=2)

        ttk.Checkbutton(common, text="Tile/repeat watermark across image",
                        variable=self.tile_mode).grid(row=3, column=0, columnspan=3, sticky="w", pady=2)
        common.columnconfigure(1, weight=1)

        # Output
        out_frame = ttk.LabelFrame(left_col, text="Output", padding=8)
        out_frame.pack(fill="x", pady=5)
        ttk.Label(out_frame, text="Directory:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        ttk.Entry(out_frame, textvariable=self.output_dir, width=40).grid(row=0, column=1, sticky="ew", padx=5)
        ttk.Button(out_frame, text="Browse...", command=self._browse_output).grid(row=0, column=2, padx=5)
        out_frame.columnconfigure(1, weight=1)

        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        utils.create_buttons_frame(self.frame, self._start, self._cancel, self._open_output, "Apply Watermark")

    def _on_type_change(self):
        if self.watermark_type.get() == "text":
            self.img_opts.pack_forget()
            self.text_opts.pack(fill="x", pady=2, before=self.text_opts.master.winfo_children()[-1])
        else:
            self.text_opts.pack_forget()
            self.img_opts.pack(fill="x", pady=2, before=self.img_opts.master.winfo_children()[-1])

    def _browse_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp *.tiff"), ("All", "*.*")]
        )
        if files:
            self._add_files(list(files))

    def _add_files(self, files):
        existing = set(self.input_files)
        for f in files:
            if f not in existing:
                self.input_files.append(f)
                self.file_listbox.insert(tk.END, os.path.basename(f))
        self.file_count_label.config(text=f"{len(self.input_files)} images")

    def _clear_files(self):
        self.input_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.file_count_label.config(text="0 images")

    def _browse_wm_image(self):
        f = filedialog.askopenfilename(title="Select Watermark Image",
                                       filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp"), ("All", "*.*")])
        if f:
            self.watermark_image_path.set(f)

    def _browse_output(self):
        d = filedialog.askdirectory(title="Select Output Directory")
        if d:
            self.output_dir.set(d)

    def _start(self):
        if not self.input_files:
            messagebox.showerror("Error", "Please add images.")
            return
        if self.watermark_type.get() == "text" and not self.text_content.get().strip():
            messagebox.showerror("Error", "Please enter watermark text.")
            return
        if self.watermark_type.get() == "image" and not os.path.isfile(self.watermark_image_path.get()):
            messagebox.showerror("Error", "Please select a watermark image.")
            return
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory.")
            return
        os.makedirs(self.output_dir.get(), exist_ok=True)
        self.conversion_canceled = False
        utils.set_controls_state(self.frame, tk.DISABLED)
        threading.Thread(target=self._process_thread, daemon=True).start()

    def _cancel(self):
        self.conversion_canceled = True

    def _open_output(self):
        utils.open_output_folder(self.output_dir.get())

    def _create_text_watermark(self, base_size):
        """Create a text watermark image with transparency."""
        font_size = self.font_size.get()
        text = self.text_content.get()
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()

        # Measure text
        dummy = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy)
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # Create watermark layer
        wm = Image.new("RGBA", (tw + 20, th + 20), (0, 0, 0, 0))
        draw = ImageDraw.Draw(wm)
        draw.text((10, 10), text, fill=(255, 255, 255, self.opacity.get()), font=font)

        if self.rotation.get() != 0:
            wm = wm.rotate(self.rotation.get(), expand=True, resample=Image.BICUBIC)

        return wm

    def _create_image_watermark(self, base_size):
        """Load and prepare an image watermark."""
        wm = Image.open(self.watermark_image_path.get()).convert("RGBA")
        scale = self.wm_scale.get() / 100.0
        new_w = int(base_size[0] * scale)
        ratio = new_w / wm.width
        new_h = int(wm.height * ratio)
        wm = wm.resize((max(1, new_w), max(1, new_h)), Image.LANCZOS)

        # Apply opacity
        alpha = wm.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(self.opacity.get() / 255.0)
        wm.putalpha(alpha)

        if self.rotation.get() != 0:
            wm = wm.rotate(self.rotation.get(), expand=True, resample=Image.BICUBIC)

        return wm

    def _calc_position(self, base_size, wm_size):
        """Calculate watermark position."""
        bw, bh = base_size
        ww, wh = wm_size
        pos = self.position.get()
        margin = 20
        positions = {
            "center": ((bw - ww) // 2, (bh - wh) // 2),
            "top-left": (margin, margin),
            "top-right": (bw - ww - margin, margin),
            "bottom-left": (margin, bh - wh - margin),
            "bottom-right": (bw - ww - margin, bh - wh - margin),
        }
        return positions.get(pos, positions["center"])

    def _apply_watermark(self, img, wm):
        """Apply watermark to an image."""
        if img.mode != "RGBA":
            img = img.convert("RGBA")

        if self.tile_mode.get():
            # Tile watermark across the image
            for y in range(0, img.height, wm.height + 50):
                for x in range(0, img.width, wm.width + 50):
                    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
                    layer.paste(wm, (x, y))
                    img = Image.alpha_composite(img, layer)
        else:
            x, y = self._calc_position(img.size, wm.size)
            layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            layer.paste(wm, (x, y))
            img = Image.alpha_composite(img, layer)

        return img

    def _process_thread(self):
        total = len(self.input_files)
        done = 0
        errors = []

        for i, filepath in enumerate(self.input_files):
            if self.conversion_canceled:
                break
            try:
                img = Image.open(filepath)

                if self.watermark_type.get() == "text":
                    wm = self._create_text_watermark(img.size)
                else:
                    wm = self._create_image_watermark(img.size)

                result = self._apply_watermark(img, wm)

                # Save
                basename = os.path.splitext(os.path.basename(filepath))[0]
                ext = os.path.splitext(filepath)[1].lower()
                out_path = os.path.join(self.output_dir.get(), basename + "_wm" + ext)

                if ext in (".jpg", ".jpeg"):
                    result = result.convert("RGB")
                    result.save(out_path, "JPEG", quality=90)
                else:
                    result.save(out_path)

                done += 1
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {e}")

            pct = ((i + 1) / total) * 100
            self.frame.winfo_toplevel().after(0, lambda p=pct: self.progress_var.set(p))
            self.frame.winfo_toplevel().after(0,
                lambda c=i+1, t=total: self.status_var.set(f"Processing {c}/{t}..."))

        def finish():
            utils.set_controls_state(self.frame, tk.NORMAL)
            if self.conversion_canceled:
                self.status_var.set("Canceled")
            else:
                msg = f"Watermarked {done}/{total} images."
                if errors:
                    msg += f"\n\n{len(errors)} error(s):\n" + "\n".join(errors[:5])
                self.status_var.set(f"Done: {done}/{total}")
                messagebox.showinfo("Complete", msg)

        self.frame.winfo_toplevel().after(0, finish)

    def add_images(self, files):
        """External interface for drag-and-drop."""
        self._add_files(files)

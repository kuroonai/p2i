# image_metadata_tab.py - Image metadata (EXIF) viewer/editor
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import utils
from styles import COLORS, FONTS


class ImageMetadataTab:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.parent = parent

        self.image_path = tk.StringVar()
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready")
        self.metadata = {}

        self._create_ui()

    def _create_ui(self):
        # File selection
        file_frame = ttk.LabelFrame(self.frame, text="Image Selection", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(file_frame, text="Image File:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(file_frame, textvariable=self.image_path, width=50).grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        ttk.Button(file_frame, text="Browse...", command=self._browse_image).grid(row=0, column=2, padx=5, pady=5)
        file_frame.columnconfigure(1, weight=1)

        # Info frame - basic image info
        info_frame = ttk.LabelFrame(self.frame, text="Image Information", padding=10)
        info_frame.pack(fill="x", padx=10, pady=5)

        self.info_labels = {}
        for i, key in enumerate(["Filename", "Format", "Dimensions", "Color Mode", "File Size"]):
            ttk.Label(info_frame, text=f"{key}:", style="Subheading.TLabel").grid(row=i, column=0, sticky="w", padx=5, pady=2)
            lbl = ttk.Label(info_frame, text="-")
            lbl.grid(row=i, column=1, sticky="w", padx=5, pady=2)
            self.info_labels[key] = lbl
        info_frame.columnconfigure(1, weight=1)

        # EXIF data frame
        exif_frame = ttk.LabelFrame(self.frame, text="EXIF / Metadata", padding=10)
        exif_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Treeview for metadata
        columns = ("Tag", "Value")
        self.tree = ttk.Treeview(exif_frame, columns=columns, show="headings", height=12)
        self.tree.heading("Tag", text="Tag")
        self.tree.heading("Value", text="Value")
        self.tree.column("Tag", width=200, minwidth=150)
        self.tree.column("Value", width=400, minwidth=200)

        vsb = ttk.Scrollbar(exif_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Action buttons
        btn_frame = ttk.Frame(self.frame, padding=(10, 6))
        btn_frame.pack(fill="x", padx=10, pady=(2, 5))

        ttk.Button(btn_frame, text="Copy All to Clipboard", command=self._copy_metadata,
                   style="Secondary.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Strip All Metadata", command=self._strip_metadata,
                   style="Danger.TButton").pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Batch Strip Metadata", command=self._batch_strip,
                   style="Secondary.TButton").pack(side="left", padx=(0, 8))

        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)

    def _browse_image(self):
        f = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.webp *.gif"), ("All", "*.*")]
        )
        if f:
            self.image_path.set(f)
            self._load_metadata(f)

    def _load_metadata(self, filepath):
        """Load and display image metadata."""
        self.tree.delete(*self.tree.get_children())
        self.metadata.clear()

        try:
            img = Image.open(filepath)

            # Basic info
            file_size = os.path.getsize(filepath)
            self.info_labels["Filename"].config(text=os.path.basename(filepath))
            self.info_labels["Format"].config(text=img.format or "Unknown")
            self.info_labels["Dimensions"].config(text=f"{img.width} x {img.height} px")
            self.info_labels["Color Mode"].config(text=img.mode)
            self.info_labels["File Size"].config(text=utils.format_file_size(file_size))

            # EXIF data
            exif_data = {}
            if hasattr(img, '_getexif') and img._getexif():
                raw_exif = img._getexif()
                for tag_id, value in raw_exif.items():
                    tag_name = TAGS.get(tag_id, f"Unknown ({tag_id})")

                    # Handle GPS info specially
                    if tag_name == "GPSInfo":
                        gps_data = {}
                        for gps_tag_id, gps_val in value.items():
                            gps_tag_name = GPSTAGS.get(gps_tag_id, f"Unknown ({gps_tag_id})")
                            gps_data[gps_tag_name] = str(gps_val)
                            exif_data[f"GPS: {gps_tag_name}"] = str(gps_val)
                        continue

                    # Convert bytes to readable format
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="replace")[:100]
                        except Exception:
                            value = f"<binary data, {len(value)} bytes>"

                    str_value = str(value)
                    if len(str_value) > 200:
                        str_value = str_value[:200] + "..."

                    exif_data[tag_name] = str_value

            # Also check image.info for PNG/other metadata
            if img.info:
                for key, value in img.info.items():
                    if key not in ("exif",) and key not in exif_data:
                        str_value = str(value)
                        if len(str_value) > 200:
                            str_value = str_value[:200] + "..."
                        exif_data[f"Info: {key}"] = str_value

            # Populate tree
            self.metadata = exif_data
            for tag, value in sorted(exif_data.items()):
                self.tree.insert("", tk.END, values=(tag, value))

            count = len(exif_data)
            self.status_var.set(f"Loaded {count} metadata entries from {os.path.basename(filepath)}")

        except Exception as e:
            self.status_var.set(f"Error loading metadata: {e}")
            messagebox.showerror("Error", f"Failed to read image metadata:\n{e}")

    def _copy_metadata(self):
        """Copy all metadata to clipboard."""
        if not self.metadata:
            messagebox.showinfo("Info", "No metadata to copy.")
            return

        text_lines = [f"{tag}: {value}" for tag, value in sorted(self.metadata.items())]
        text = "\n".join(text_lines)

        self.frame.clipboard_clear()
        self.frame.clipboard_append(text)
        self.status_var.set("Metadata copied to clipboard")

    def _strip_metadata(self):
        """Strip all metadata from the current image and save."""
        filepath = self.image_path.get()
        if not filepath or not os.path.isfile(filepath):
            messagebox.showerror("Error", "Please select a valid image file.")
            return

        result = messagebox.askyesno(
            "Strip Metadata",
            f"This will remove all EXIF metadata from:\n{os.path.basename(filepath)}\n\n"
            "The file will be overwritten. Continue?"
        )
        if not result:
            return

        try:
            img = Image.open(filepath)
            # Create a clean copy without metadata
            clean = Image.new(img.mode, img.size)
            clean.putdata(list(img.getdata()))

            # Save with same format
            save_kwargs = {}
            if img.format == "JPEG":
                save_kwargs["quality"] = 95
            clean.save(filepath, img.format, **save_kwargs)

            self._load_metadata(filepath)
            self.status_var.set("Metadata stripped successfully")
            messagebox.showinfo("Success", "All metadata has been removed.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to strip metadata:\n{e}")

    def _batch_strip(self):
        """Batch strip metadata from multiple images."""
        files = filedialog.askopenfilenames(
            title="Select Images to Strip Metadata",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp *.webp"), ("All", "*.*")]
        )
        if not files:
            return

        result = messagebox.askyesno(
            "Batch Strip Metadata",
            f"This will remove all EXIF metadata from {len(files)} image(s).\n"
            "Original files will be overwritten. Continue?"
        )
        if not result:
            return

        self.conversion_canceled = False
        utils.set_controls_state(self.frame, tk.DISABLED)

        def process():
            total = len(files)
            done = 0
            errors = []

            for i, filepath in enumerate(files):
                if self.conversion_canceled:
                    break
                try:
                    img = Image.open(filepath)
                    fmt = img.format
                    clean = Image.new(img.mode, img.size)
                    clean.putdata(list(img.getdata()))
                    save_kwargs = {}
                    if fmt == "JPEG":
                        save_kwargs["quality"] = 95
                    clean.save(filepath, fmt, **save_kwargs)
                    done += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(filepath)}: {e}")

                pct = ((i + 1) / total) * 100
                self.frame.winfo_toplevel().after(0, lambda p=pct: self.progress_var.set(p))
                self.frame.winfo_toplevel().after(0,
                    lambda c=i+1, t=total: self.status_var.set(f"Stripping {c}/{t}..."))

            def finish():
                utils.set_controls_state(self.frame, tk.NORMAL)
                msg = f"Stripped metadata from {done}/{total} images."
                if errors:
                    msg += f"\n\n{len(errors)} error(s):\n" + "\n".join(errors[:5])
                self.status_var.set(f"Done: {done}/{total}")
                messagebox.showinfo("Complete", msg)

            self.frame.winfo_toplevel().after(0, finish)

        threading.Thread(target=process, daemon=True).start()

    def set_image(self, filepath):
        """External interface: load metadata for a given file."""
        if os.path.isfile(filepath):
            self.image_path.set(filepath)
            self._load_metadata(filepath)

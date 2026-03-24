# ghostscript_utils.py - Ghostscript detection and UI helpers
import os
import subprocess
import platform
import tkinter as tk
from tkinter import ttk
import webbrowser
from styles import COLORS, FONTS


def find_ghostscript():
    """Detect if Ghostscript is installed and return the executable path or None."""
    gs_names = []
    if platform.system() == "Windows":
        gs_names = ["gswin64c", "gswin32c", "gs"]
    else:
        gs_names = ["gs"]

    for gs in gs_names:
        try:
            result = subprocess.run(
                [gs, "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5,
            )
            if result.returncode == 0:
                version = result.stdout.decode().strip()
                return gs, version
        except (subprocess.SubprocessError, FileNotFoundError, OSError):
            continue

    # On Windows, check common install locations
    if platform.system() == "Windows":
        for base in [
            os.environ.get("ProgramFiles", r"C:\Program Files"),
            os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        ]:
            gs_dir = os.path.join(base, "gs")
            if os.path.isdir(gs_dir):
                for ver_dir in sorted(os.listdir(gs_dir), reverse=True):
                    exe = os.path.join(gs_dir, ver_dir, "bin", "gswin64c.exe")
                    if os.path.isfile(exe):
                        try:
                            result = subprocess.run(
                                [exe, "--version"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=5,
                            )
                            version = result.stdout.decode().strip()
                            return exe, version
                        except Exception:
                            continue
    return None, None


# Cache the result at module level
_gs_cache = None


def get_ghostscript():
    """Cached Ghostscript detection. Returns (executable, version) or (None, None)."""
    global _gs_cache
    if _gs_cache is None:
        _gs_cache = find_ghostscript()
    return _gs_cache


def is_ghostscript_available():
    """Return True if Ghostscript is installed."""
    exe, _ = get_ghostscript()
    return exe is not None


def create_gs_banner(parent):
    """Create an info banner about Ghostscript dependency. Returns the frame widget."""
    exe, version = get_ghostscript()

    banner = tk.Frame(parent, padx=10, pady=6)

    if exe:
        banner.configure(bg="#D1FAE5")  # green-100
        icon_text = "Found"
        icon_color = COLORS['success']
        msg = f"Ghostscript {version} detected ({os.path.basename(exe)})"
        banner_label = tk.Label(
            banner, text=msg,
            font=FONTS['body_small'], fg=COLORS['text'], bg="#D1FAE5",
            anchor="w",
        )
        banner_label.pack(side="left", fill="x", expand=True)
        status_label = tk.Label(
            banner, text=icon_text,
            font=('Segoe UI', 9, 'bold'), fg=icon_color, bg="#D1FAE5",
        )
        status_label.pack(side="right")
    else:
        banner.configure(bg="#FEF3C7")  # amber-100
        msg = (
            "Ghostscript is required for optimal PDF compression. "
            "Install it and ensure gswin64c is on your PATH."
        )
        banner_label = tk.Label(
            banner, text=msg,
            font=FONTS['body_small'], fg=COLORS['text'], bg="#FEF3C7",
            anchor="w", wraplength=500,
        )
        banner_label.pack(side="left", fill="x", expand=True)

        def open_gs_download():
            webbrowser.open("https://www.ghostscript.com/releases/gsdnld.html")

        link_btn = tk.Label(
            banner, text="Download",
            font=('Segoe UI', 9, 'underline'), fg=COLORS['primary'], bg="#FEF3C7",
            cursor="hand2",
        )
        link_btn.pack(side="right", padx=(8, 0))
        link_btn.bind("<Button-1>", lambda e: open_gs_download())

        status_label = tk.Label(
            banner, text="Not Found",
            font=('Segoe UI', 9, 'bold'), fg=COLORS['error'], bg="#FEF3C7",
        )
        status_label.pack(side="right")

    return banner

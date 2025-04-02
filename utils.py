import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

def create_progress_frame(parent, progress_var, status_var, text="Progress"):
    """Create a reusable progress frame with progress bar and status label"""
    progress_frame = ttk.LabelFrame(parent, text=text, padding=10)
    progress_frame.pack(fill="x", expand=False, padx=10, pady=5)
    
    # Progress bar
    progress = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
    progress.pack(fill="x", expand=True, padx=5, pady=5)
    
    # Status label
    ttk.Label(progress_frame, textvariable=status_var).pack(fill="x", expand=True, padx=5, pady=5)
    
    return progress_frame

def create_buttons_frame(parent, start_cmd, cancel_cmd, output_folder_cmd, start_text="Start"):
    """Create a reusable buttons frame with start, cancel, and open output folder buttons"""
    buttons_frame = ttk.Frame(parent, padding=10)
    buttons_frame.pack(fill="x", expand=False, padx=10, pady=5)
    
    ttk.Button(buttons_frame, text=start_text, command=start_cmd).pack(side="left", padx=5)
    ttk.Button(buttons_frame, text="Cancel", command=cancel_cmd).pack(side="left", padx=5)
    ttk.Button(buttons_frame, text="Open Output Folder", command=output_folder_cmd).pack(side="left", padx=5)
    
    return buttons_frame

def display_preview(canvas, img, photo_ref):
    """Display an image preview on a canvas, maintaining aspect ratio"""
    # Calculate the ratio to fit the image within the canvas
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    
    # If canvas hasn't been realized yet, use a default size
    if canvas_width <= 1:
        canvas_width = 600
    if canvas_height <= 1:
        canvas_height = 400
    
    img_width, img_height = img.size
    ratio = min(canvas_width / img_width, canvas_height / img_height)
    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)
    
    # Resize the image
    img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Convert to PhotoImage
    photo = ImageTk.PhotoImage(img)
    
    # Clear previous content
    canvas.delete("all")
    
    # Calculate center position
    canvas_width = canvas.winfo_width()
    canvas_height = canvas.winfo_height()
    x_pos = (canvas_width - new_width) // 2
    y_pos = (canvas_height - new_height) // 2
    
    # Create image on canvas
    canvas.create_image(x_pos, y_pos, anchor=tk.NW, image=photo)
    
    # Return the photo so it can be stored (to prevent garbage collection)
    return photo

def set_controls_state(parent, state):
    """Recursively enable or disable all interactive controls in a frame"""
    for widget in parent.winfo_children():
        if isinstance(widget, (ttk.LabelFrame, ttk.Frame)):
            set_controls_state(widget, state)
        elif isinstance(widget, (ttk.Button, ttk.Entry, ttk.Spinbox, ttk.Combobox, 
                              ttk.Checkbutton, ttk.Scale, tk.Listbox)):
            # Don't disable Cancel button
            if isinstance(widget, ttk.Button) and widget["text"] == "Cancel":
                continue
            
            widget.configure(state=state)

def open_output_folder(folder_path):
    """Open the output folder in the file explorer"""
    if not folder_path or not os.path.isdir(folder_path):
        messagebox.showerror("Error", "Output directory does not exist")
        return
        
    # Open the folder in file explorer
    if os.name == 'nt':  # Windows
        os.startfile(folder_path)
    elif os.name == 'posix':  # macOS or Linux
        if sys.platform == 'darwin':  # macOS
            os.system(f'open "{folder_path}"')
        else:  # Linux
            os.system(f'xdg-open "{folder_path}"')

def format_file_size(size_in_bytes):
    """Format file size in a human-readable format"""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} bytes"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.2f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.2f} GB"

def run_in_thread(func, callback=None):
    """Run a function in a separate thread and call the callback when done"""
    def thread_target():
        try:
            result = func()
            if callback:
                callback(result)
        except Exception as e:
            if callback:
                callback(None, e)
    
    thread = threading.Thread(target=thread_target)
    thread.daemon = True
    thread.start()
    return thread
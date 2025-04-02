# drag_drop.py
import os
import tkinter as tk
from tkinter import ttk
import platform

class DragDropManager:
    def __init__(self, master, settings, target_widgets=None):
        self.master = master
        self.settings = settings
        self.target_widgets = target_widgets or []
        self.setup_drag_drop()
    
    def setup_drag_drop(self):
        """Configure drag and drop functionality based on platform"""
        system = platform.system()
        
        if system == "Windows":
            self._setup_windows_dnd()
        elif system == "Darwin":  # macOS
            self._setup_macos_dnd()
        else:  # Linux or others
            self._setup_linux_dnd()
    
    def _setup_windows_dnd(self):
        """Setup drag and drop for Windows using tkdnd"""
        try:
            # Try to import TkinterDnD2
            self.master.tk.eval('package require tkdnd')
            
            # Register target widgets
            for widget in self.target_widgets:
                self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                widget.bind('<<Drop>>', self._on_drop)
                
            # Also register the root window
            self.master.tk.call('tkdnd::drop_target', 'register', self.master._w, 'DND_Files')
            self.master.bind('<<Drop>>', self._on_drop)
            
        except tk.TclError:
            print("TkinterDnD not available. Drag and drop disabled.")
    
    def _setup_macos_dnd(self):
        """Setup drag and drop for macOS"""
        try:
            # macOS specific drag and drop
            # This is a placeholder - actual implementation would be more complex
            # and might require external libraries like PyObjC
            pass
        except Exception as e:
            print(f"Failed to set up macOS drag and drop: {e}")
    
    def _setup_linux_dnd(self):
        """Setup drag and drop for Linux"""
        try:
            # For Linux, we might use TkinterDnD or Xdnd
            # Similar to Windows implementation
            pass
        except Exception as e:
            print(f"Failed to set up Linux drag and drop: {e}")
    
    def _on_drop(self, event):
        """Handle dropped files"""
        data = event.data
        
        # With TkinterDnD, data might be formatted differently on different platforms
        if platform.system() == "Windows":
            # Data format is {filename filename ...}
            files = self.master.tk.splitlist(data)
        else:
            # Data might be space-delimited on some platforms
            files = data.split()
        
        # Process the dropped files
        valid_files = [f for f in files if os.path.isfile(f)]
        
        # Notify the main application
        if hasattr(self.master, "handle_dropped_files") and valid_files:
            self.master.handle_dropped_files(valid_files)
    
    def add_target_widget(self, widget):
        """Add a widget as a drop target"""
        if widget not in self.target_widgets:
            self.target_widgets.append(widget)
            
            # Register the widget
            try:
                if platform.system() == "Windows":
                    self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                    widget.bind('<<Drop>>', self._on_drop)
            except:
                pass
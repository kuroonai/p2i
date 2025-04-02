# drag_drop.py with improved error handling

import os
import tkinter as tk
from tkinter import ttk
import platform
import tkinterdnd2

class DragDropManager:
    def __init__(self, master, settings, target_widgets=None):
        self.master = master
        self.settings = settings
        self.target_widgets = target_widgets or []
        self.tkdnd_available = False
        self.setup_drag_drop()
    
    # In drag_drop.py
    def setup_drag_drop(self):
        """Configure drag and drop functionality based on platform"""
        try:
            system = platform.system()
            
            if system == "Windows":
                self._setup_windows_dnd()
            elif system == "Darwin":  # macOS
                self._setup_macos_dnd()
            else:  # Linux or others
                self._setup_linux_dnd()
        except Exception as e:
            print(f"Failed to set up drag and drop: {e}")
            self.tkdnd_available = False
    
    def _setup_windows_dnd(self):
        """Setup drag and drop for Windows using tkdnd"""
        try:
            # First try direct tkdnd method
            self.master.tk.eval('package require tkdnd')
            self.tkdnd_available = True
            
            # Register target widgets
            for widget in self.target_widgets:
                self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                widget.bind('<<Drop>>', self._on_drop)
                
            # Also register the root window
            self.master.tk.call('tkdnd::drop_target', 'register', self.master._w, 'DND_Files')
            self.master.bind('<<Drop>>', self._on_drop)
            
        except (tk.TclError, AttributeError):
            # Try using tkinterdnd2 module
            try:
                import tkinterdnd2
                tkinterdnd2.TkinterDnD.bind_to_widget_class(tk.Tk)
                tkinterdnd2.TkinterDnD.bind_to_widget_class(ttk.Frame)
                
                for widget in self.target_widgets:
                    widget.drop_target_register('DND_Files')
                    widget.dnd_bind('<<Drop>>', self._on_drop)
                
                self.master.drop_target_register('DND_Files')
                self.master.dnd_bind('<<Drop>>', self._on_drop)
                self.tkdnd_available = True
                
            except (ImportError, AttributeError) as e:
                print(f"TkinterDnD not available: {e}. Drag and drop disabled.")
                self.tkdnd_available = False
    
    def _setup_macos_dnd(self):
        """Setup drag and drop for macOS"""
        try:
            # Try using tkinterdnd2 module for macOS
            try:
                import tkinterdnd2
                tkinterdnd2.TkinterDnD.bind_to_widget_class(tk.Tk)
                tkinterdnd2.TkinterDnD.bind_to_widget_class(ttk.Frame)
                
                for widget in self.target_widgets:
                    widget.drop_target_register('DND_Files')
                    widget.dnd_bind('<<Drop>>', self._on_drop)
                
                self.master.drop_target_register('DND_Files')
                self.master.dnd_bind('<<Drop>>', self._on_drop)
                self.tkdnd_available = True
                
            except ImportError:
                # Alternative: Try direct aqua/cocoa drag and drop if available
                try:
                    self.master.tk.eval('package require tkdnd')
                    self.tkdnd_available = True
                    
                    # Register target widgets
                    for widget in self.target_widgets:
                        self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                        widget.bind('<<Drop>>', self._on_drop)
                        
                    # Also register the root window
                    self.master.tk.call('tkdnd::drop_target', 'register', self.master._w, 'DND_Files')
                    self.master.bind('<<Drop>>', self._on_drop)
                    
                except tk.TclError:
                    print("TkinterDnD not available for macOS. Drag and drop disabled.")
                    self.tkdnd_available = False
        except Exception as e:
            print(f"Failed to set up macOS drag and drop: {e}")
            self.tkdnd_available = False
    
    def _setup_linux_dnd(self):
        """Setup drag and drop for Linux"""
        try:
            # Try using tkinterdnd2 module for Linux
            try:
                import tkinterdnd2
                tkinterdnd2.TkinterDnD.bind_to_widget_class(tk.Tk)
                tkinterdnd2.TkinterDnD.bind_to_widget_class(ttk.Frame)
                
                for widget in self.target_widgets:
                    widget.drop_target_register('DND_Files')
                    widget.dnd_bind('<<Drop>>', self._on_drop)
                
                self.master.drop_target_register('DND_Files')
                self.master.dnd_bind('<<Drop>>', self._on_drop)
                self.tkdnd_available = True
                
            except ImportError:
                # Try direct X11 drag and drop if available
                try:
                    self.master.tk.eval('package require tkdnd')
                    self.tkdnd_available = True
                    
                    # Register target widgets
                    for widget in self.target_widgets:
                        self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                        widget.bind('<<Drop>>', self._on_drop)
                        
                    # Also register the root window
                    self.master.tk.call('tkdnd::drop_target', 'register', self.master._w, 'DND_Files')
                    self.master.bind('<<Drop>>', self._on_drop)
                    
                except tk.TclError:
                    print("TkinterDnD not available for Linux. Drag and drop disabled.")
                    self.tkdnd_available = False
        except Exception as e:
            print(f"Failed to set up Linux drag and drop: {e}")
            self.tkdnd_available = False
    
    def _on_drop(self, event):
        """Handle dropped files"""
        if not self.tkdnd_available:
            return
            
        data = event.data
        
        # With TkinterDnD, data might be formatted differently on different platforms
        if platform.system() == "Windows":
            # Data format is {filename filename ...}
            files = self.master.tk.splitlist(data)
        else:
            # Data might be space-delimited on some platforms
            if isinstance(data, str):
                # Handle string data (normal case)
                if data.startswith('{') and data.endswith('}'):
                    # Handle Tcl list format
                    files = self.master.tk.splitlist(data)
                else:
                    # Handle space-delimited format
                    files = data.split()
            else:
                # Handle other potential data types
                files = [str(data)]
        
        # Process the dropped files
        valid_files = [f for f in files if os.path.isfile(f)]
        
        # Notify the main application
        if hasattr(self.master, "handle_dropped_files") and valid_files:
            self.master.handle_dropped_files(valid_files)
    
    def add_target_widget(self, widget):
        """Add a widget as a drop target"""
        if not self.tkdnd_available or widget in self.target_widgets:
            return
            
        self.target_widgets.append(widget)
            
        # Register the widget
        try:
            if platform.system() == "Windows":
                try:
                    # First try direct method
                    self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                    widget.bind('<<Drop>>', self._on_drop)
                except (tk.TclError, AttributeError):
                    # Try tkinterdnd2 module
                    widget.drop_target_register('DND_Files')
                    widget.dnd_bind('<<Drop>>', self._on_drop)
            else:
                # Similar pattern for other platforms
                try:
                    # First try direct method
                    self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                    widget.bind('<<Drop>>', self._on_drop)
                except (tk.TclError, AttributeError):
                    # Try tkinterdnd2 module
                    widget.drop_target_register('DND_Files')
                    widget.dnd_bind('<<Drop>>', self._on_drop)
        except:
            # Silently ignore errors when adding target widgets
            pass

    def is_available(self):
        """Check if drag and drop is available"""
        return self.tkdnd_available
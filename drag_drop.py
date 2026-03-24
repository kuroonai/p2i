# drag_drop.py with improved error handling and visual feedback

import os
import tkinter as tk
from tkinter import ttk, messagebox
import platform

try:
    import tkinterdnd2
except ImportError:
    tkinterdnd2 = None


class DragDropManager:
    def __init__(self, master, settings, target_widgets=None):
        self.master = master
        self.settings = settings
        self.target_widgets = target_widgets or []
        self.tkdnd_available = False
        self._drag_overlay = None
        self.setup_drag_drop()

    def setup_drag_drop(self):
        """Configure drag and drop functionality"""
        try:
            # Check if root was created with TkinterDnD.Tk()
            # by testing if drop_target_register is available
            if hasattr(self.master, 'drop_target_register'):
                self._setup_tkinterdnd2()
            else:
                # Fallback: try loading tkdnd directly via Tcl
                self._setup_tkdnd_direct()
        except Exception as e:
            print(f"Failed to set up drag and drop: {e}")
            self.tkdnd_available = False

    def _setup_tkinterdnd2(self):
        """Setup using tkinterdnd2 (root must be TkinterDnD.Tk())"""
        try:
            for widget in self.target_widgets:
                widget.drop_target_register('DND_Files')
                widget.dnd_bind('<<Drop>>', self._on_drop)

            self.master.drop_target_register('DND_Files')
            self.master.dnd_bind('<<Drop>>', self._on_drop)
            self.tkdnd_available = True
        except Exception as e:
            print(f"tkinterdnd2 setup failed: {e}")
            self.tkdnd_available = False

    def _setup_tkdnd_direct(self):
        """Fallback: try loading tkdnd package directly via Tcl"""
        try:
            self.master.tk.eval('package require tkdnd')

            for widget in self.target_widgets:
                self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                widget.bind('<<Drop>>', self._on_drop)

            self.master.tk.call('tkdnd::drop_target', 'register', self.master._w, 'DND_Files')
            self.master.bind('<<Drop>>', self._on_drop)
            self.tkdnd_available = True
        except (tk.TclError, AttributeError) as e:
            print(f"Direct tkdnd setup failed: {e}")
            self.tkdnd_available = False

    def _on_drop(self, event):
        """Handle dropped files"""
        if not self.tkdnd_available:
            return

        data = event.data

        # Parse dropped file paths
        if isinstance(data, str):
            if data.startswith('{') and data.endswith('}'):
                files = self.master.tk.splitlist(data)
            else:
                try:
                    files = self.master.tk.splitlist(data)
                except tk.TclError:
                    files = data.split()
        else:
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

        try:
            if hasattr(widget, 'drop_target_register'):
                widget.drop_target_register('DND_Files')
                widget.dnd_bind('<<Drop>>', self._on_drop)
            else:
                self.master.tk.call('tkdnd::drop_target', 'register', widget._w, 'DND_Files')
                widget.bind('<<Drop>>', self._on_drop)
        except Exception:
            pass

    def is_available(self):
        """Check if drag and drop is available"""
        return self.tkdnd_available

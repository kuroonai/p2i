#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF and Image Converter GUI
- PDF to Image conversion
- Image to PDF conversion
- PDF Merge functionality
- PDF Split functionality
- PDF Compression functionality
Based on original work by Naveen Kumar Vasudevan and the package pdf2image
Enhanced with GUI and additional features
"""

import os
import sys
import multiprocessing
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Import tab modules
from pdf_to_image_tab import PDFToImageTab
from image_to_pdf_tab import ImageToPDFTab
from pdf_merge_tab import PDFMergeTab
from pdf_split_tab import PDFSplitTab
from pdf_compress_tab import PDFCompressTab

class ConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF & Image Converter")
        
        # Try to set icon, but continue if it fails
        try:
            self.root.iconbitmap("p2i.ico")
        except:
            pass
        
        # Get screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Set window dimensions
        window_width = int(screen_width * 0.8)  # 80% of screen width
        window_height = int(screen_height * 0.8)  # 80% of screen height
        
        # Calculate position to center window
        position_top = int((screen_height - window_height)/2)
        position_left = int((screen_width - window_width)/2)
        
        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{position_left}+{position_top}")        
        self.root.configure(bg="#f0f0f0")
        
        # Create tab control
        self.tab_control = ttk.Notebook(self.root)
        
        # System info
        self.n_cpu = multiprocessing.cpu_count()
        
        # Create tabs
        self.pdf_to_image_tab = PDFToImageTab(self.tab_control, self.n_cpu)
        self.tab_control.add(self.pdf_to_image_tab.frame, text="PDF to Image")
        
        self.image_to_pdf_tab = ImageToPDFTab(self.tab_control)
        self.tab_control.add(self.image_to_pdf_tab.frame, text="Image to PDF")
        
        self.pdf_merge_tab = PDFMergeTab(self.tab_control)
        self.tab_control.add(self.pdf_merge_tab.frame, text="Merge PDFs")
        
        self.pdf_split_tab = PDFSplitTab(self.tab_control)
        self.tab_control.add(self.pdf_split_tab.frame, text="Split PDF")
        
        self.pdf_compress_tab = PDFCompressTab(self.tab_control)
        self.tab_control.add(self.pdf_compress_tab.frame, text="Compress PDF")
        
        # Pack the tab control
        self.tab_control.pack(expand=1, fill="both")
        
        # Add exit button at the bottom
        exit_frame = ttk.Frame(self.root)
        exit_frame.pack(fill="x", expand=False, padx=10, pady=5)
        ttk.Button(exit_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)

def main():
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
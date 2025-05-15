# support_tab.py
import os
import webbrowser
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import platform
import utils

class SupportTab:
    def __init__(self, parent):
        # Create frame
        self.frame = ttk.Frame(parent)
        self.parent = parent
        
        # Support links - using your username
        self.github_url = "https://github.com/sponsors/kuroonai"
        self.patreon_url = "https://www.patreon.com/kuroonai"
        self.buymeacoffee_url = "https://www.buymeacoffee.com/kuroonai"
        self.paypal_url = "https://www.paypal.me/kuroonai"
        
        # Progress/status variables (for consistency with other tabs)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.status_var = tk.StringVar(value="Ready to support p2i development")
        
        # Create UI elements
        self.create_info_frame()
        self.create_support_frame()
        utils.create_progress_frame(self.frame, self.progress_var, self.status_var)
        
    def create_info_frame(self):
        info_frame = ttk.LabelFrame(self.frame, text="About Supporting p2i", padding=15)
        info_frame.pack(fill="x", expand=False, padx=10, pady=10)
        
        # Explanatory text
        info_text = """Thank you for considering supporting the development of p2i!

Your contribution helps:
• Maintain and improve existing features
• Develop new capabilities
• Provide better documentation
• Keep p2i free and open-source

Choose any of the support options below that works best for you.
Even small contributions are greatly appreciated and motivate further development.
"""
        info_label = ttk.Label(info_frame, text=info_text, wraplength=700, justify="left")
        info_label.pack(fill="x", pady=10)
        
    def create_support_frame(self):
        support_frame = ttk.LabelFrame(self.frame, text="Support Options", padding=15)
        support_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Frame to center content
        center_frame = ttk.Frame(support_frame)
        center_frame.pack(pady=30, expand=True)
        
        # GitHub Sponsors
        github_frame = ttk.Frame(center_frame, padding=10)
        github_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        github_label = ttk.Label(github_frame, text="GitHub Sponsors", font=("Helvetica", 12, "bold"))
        github_label.pack(pady=(0, 10))
        
        github_desc = ttk.Label(github_frame, text="Support through GitHub's\nofficial sponsorship program", justify="center")
        github_desc.pack(pady=(0, 10))
        
        github_btn = ttk.Button(github_frame, text="Sponsor on GitHub", 
                             command=lambda: self.open_support_site(self.github_url, "GitHub Sponsors"),
                             width=20)
        github_btn.pack()
        
        # Patreon
        patreon_frame = ttk.Frame(center_frame, padding=10)
        patreon_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        patreon_label = ttk.Label(patreon_frame, text="Patreon", font=("Helvetica", 12, "bold"))
        patreon_label.pack(pady=(0, 10))
        
        patreon_desc = ttk.Label(patreon_frame, text="Become a patron with\nmonthly support", justify="center")
        patreon_desc.pack(pady=(0, 10))
        
        patreon_btn = ttk.Button(patreon_frame, text="Support on Patreon", 
                              command=lambda: self.open_support_site(self.patreon_url, "Patreon"),
                              width=20)
        patreon_btn.pack()
        
        # Buy Me A Coffee
        coffee_frame = ttk.Frame(center_frame, padding=10)
        coffee_frame.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        coffee_label = ttk.Label(coffee_frame, text="Buy Me A Coffee", font=("Helvetica", 12, "bold"))
        coffee_label.pack(pady=(0, 10))
        
        coffee_desc = ttk.Label(coffee_frame, text="Make a one-time\ncontribution", justify="center")
        coffee_desc.pack(pady=(0, 10))
        
        coffee_btn = ttk.Button(coffee_frame, text="Buy Me A Coffee", 
                             command=lambda: self.open_support_site(self.buymeacoffee_url, "Buy Me A Coffee"),
                             width=20)
        coffee_btn.pack()
        
        # PayPal
        paypal_frame = ttk.Frame(center_frame, padding=10)
        paypal_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        
        paypal_label = ttk.Label(paypal_frame, text="PayPal", font=("Helvetica", 12, "bold"))
        paypal_label.pack(pady=(0, 10))
        
        paypal_desc = ttk.Label(paypal_frame, text="Send a contribution\nvia PayPal", justify="center")
        paypal_desc.pack(pady=(0, 10))
        
        paypal_btn = ttk.Button(paypal_frame, text="Donate with PayPal", 
                             command=lambda: self.open_support_site(self.paypal_url, "PayPal"),
                             width=20)
        paypal_btn.pack()
        
        # Make all columns/rows in the grid have equal weight
        for i in range(2):
            center_frame.columnconfigure(i, weight=1)
            center_frame.rowconfigure(i, weight=1)
            
        # Thank you note at the bottom
        thank_frame = ttk.Frame(support_frame)
        thank_frame.pack(fill="x", pady=(20, 0))
        
        thank_label = ttk.Label(thank_frame, 
                              text="Thank you for your support! It helps make p2i better for everyone.", 
                              font=("Helvetica", 10, "italic"))
        thank_label.pack()
    
    def open_support_site(self, url, platform_name):
        """Open the support website and update status"""
        try:
            webbrowser.open(url)
            self.status_var.set(f"Opened {platform_name} in your browser")
        except Exception as e:
            self.status_var.set(f"Error opening {platform_name}: {str(e)}")

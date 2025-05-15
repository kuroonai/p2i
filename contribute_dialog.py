import os
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import subprocess

class ContributeDialog:
    def __init__(self, parent):
        # Create top-level dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Contribute to p2i")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Set icon if available
        try:
            if platform.system() == "Windows":
                icon_path = os.path.join("icons", "app_icon.ico")
                if os.path.exists(icon_path):
                    self.dialog.iconbitmap(icon_path)
            else:
                icon_path = os.path.join("icons", "app_icon.png")
                if os.path.exists(icon_path):
                    img = tk.PhotoImage(file=icon_path)
                    self.dialog.iconphoto(True, img)
        except Exception:
            pass  # Ignore icon errors
        
        # Initialize variables
        self.github_url = "https://github.com/kuroonai/p2i"
        self.issues_url = f"{self.github_url}/issues"
        self.wiki_url = f"{self.github_url}/wiki"
        self.fork_url = f"{self.github_url}/fork"
        
        # Create main container with padding
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Create and populate the UI
        self.create_header(main_frame)
        notebook = self.create_notebook(main_frame)
        self.create_quick_links(main_frame)
        self.create_buttons(main_frame)
        
        # Set up the notebook tabs
        self.create_overview_tab(notebook)
        self.create_code_tab(notebook)
        self.create_docs_tab(notebook)
        self.create_bugs_tab(notebook)
        self.create_translate_tab(notebook)
        
        # Center the dialog on parent
        self.center_dialog(parent)
    
    def center_dialog(self, parent):
        """Center the dialog on parent window"""
        self.dialog.update_idletasks()
        
        # Get sizes and positions
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Set geometry
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_header(self, parent):
        """Create the header section"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Title
        title = ttk.Label(header_frame, text="Contribute to p2i", font=("Helvetica", 16, "bold"))
        title.pack(anchor="w")
        
        # Subtitle
        subtitle = ttk.Label(header_frame, text="Join the community and help improve this project")
        subtitle.pack(anchor="w")
    
    def create_notebook(self, parent):
        """Create the main notebook"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True, pady=10)
        return notebook
    
    def create_quick_links(self, parent):
        """Create quick links section"""
        links_frame = ttk.LabelFrame(parent, text="Quick Links")
        links_frame.pack(fill="x", pady=10)
        
        # Create grid of buttons
        github_btn = ttk.Button(links_frame, text="GitHub Repository", 
                              command=lambda: webbrowser.open(self.github_url))
        github_btn.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        
        issues_btn = ttk.Button(links_frame, text="Report an Issue", 
                              command=lambda: webbrowser.open(self.issues_url))
        issues_btn.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        wiki_btn = ttk.Button(links_frame, text="Documentation", 
                            command=lambda: webbrowser.open(self.wiki_url))
        wiki_btn.grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        
        fork_btn = ttk.Button(links_frame, text="Fork on GitHub", 
                            command=lambda: webbrowser.open(self.fork_url))
        fork_btn.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        
        # Make columns expandable
        for i in range(4):
            links_frame.columnconfigure(i, weight=1)
    
    def create_buttons(self, parent):
        """Create action buttons"""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        close_btn = ttk.Button(btn_frame, text="Close", command=self.dialog.destroy)
        close_btn.pack(side="right")
    
    def create_overview_tab(self, notebook):
        """Create the overview tab"""
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Overview")
        
        # Ways to contribute section
        ttk.Label(tab, text="Ways to Contribute", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        ways_text = (
            "There are many ways to contribute to p2i, regardless of your experience level or skills:\n\n"
            "• Code: Fix bugs, add features, or improve performance\n"
            "• Documentation: Help improve the docs, wiki, or comments\n"
            "• Design: Create icons, improve UI, or suggest UX enhancements\n"
            "• Testing: Try new features and report bugs\n"
            "• Translation: Help translate the UI to other languages\n"
            "• Ideas: Suggest new features or improvements\n\n"
            "All contributions are valued and appreciated!"
        )
        
        ways_label = ttk.Label(tab, text=ways_text, wraplength=700, justify="left")
        ways_label.pack(fill="x", pady=10)
        
        # Getting started section
        ttk.Label(tab, text="Getting Started", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        
        getting_started_text = (
            "1. Fork the repository on GitHub\n"
            "2. Clone your fork to your local machine\n"
            "3. Create a new branch for your contribution\n"
            "4. Make your changes and test them\n"
            "5. Commit your changes with a clear message\n"
            "6. Push to your fork and submit a pull request\n\n"
            "See the 'Code' tab for more detailed instructions."
        )
        
        getting_started_label = ttk.Label(tab, text=getting_started_text, wraplength=700, justify="left")
        getting_started_label.pack(fill="x", pady=10)
        
        # Call to action
        action_frame = ttk.Frame(tab)
        action_frame.pack(fill="x", pady=20)
        
        ttk.Button(action_frame, text="View Open Issues", 
                 command=lambda: webbrowser.open(f"{self.issues_url}?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22")).pack(side="left", padx=5)
        
        ttk.Button(action_frame, text="Join Discussion", 
                 command=lambda: webbrowser.open(f"{self.github_url}/discussions")).pack(side="left", padx=5)
    
    def create_code_tab(self, notebook):
        """Create the code contribution tab"""
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Code")
        
        # Development setup section
        ttk.Label(tab, text="Development Setup", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        setup_text = (
            "To set up a development environment for p2i:\n\n"
            "1. Clone the repository:\n"
            "   git clone https://github.com/kuroonai/p2i.git\n\n"
            "2. Create a virtual environment:\n"
            "   python -m venv venv\n\n"
            "3. Activate the virtual environment:\n"
            "   • Windows: venv\\Scripts\\activate\n"
            "   • macOS/Linux: source venv/bin/activate\n\n"
            "4. Install dependencies:\n"
            "   pip install -r requirements.txt\n\n"
            "5. Run the application:\n"
            "   python main.py"
        )
        
        setup_label = ttk.Label(tab, text=setup_text, wraplength=700, justify="left")
        setup_label.pack(fill="x", pady=10)
        
        # Style guide section
        ttk.Label(tab, text="Coding Standards", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        
        standards_text = (
            "When contributing code, please follow these guidelines:\n\n"
            "• Follow PEP 8 style guidelines for Python code\n"
            "• Write descriptive commit messages\n"
            "• Add comments to explain complex logic\n"
            "• Include docstrings for functions and classes\n"
            "• Test your changes before submitting\n"
            "• Keep pull requests focused on a single feature or fix"
        )
        
        standards_label = ttk.Label(tab, text=standards_text, wraplength=700, justify="left")
        standards_label.pack(fill="x", pady=10)
        
        # Clone repository frame
        clone_frame = ttk.LabelFrame(tab, text="Clone Repository")
        clone_frame.pack(fill="x", pady=10)
        
        clone_url = tk.StringVar(value="https://github.com/kuroonai/p2i.git")
        url_entry = ttk.Entry(clone_frame, textvariable=clone_url, width=50)
        url_entry.pack(side="left", fill="x", expand=True, padx=5, pady=5)
        
        def copy_to_clipboard():
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(clone_url.get())
            messagebox.showinfo("Copied", "Repository URL copied to clipboard!")
        
        ttk.Button(clone_frame, text="Copy", command=copy_to_clipboard).pack(side="left", padx=5, pady=5)
        
        # Check if local environment has Git installed
        def check_git_installed():
            try:
                subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                return False
        
        if check_git_installed():
            ttk.Button(clone_frame, text="Clone Now", 
                    command=lambda: self.clone_repository(clone_url.get())).pack(side="left", padx=5, pady=5)
    
    def create_docs_tab(self, notebook):
        """Create the documentation tab"""
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Documentation")
        
        # Documentation overview
        ttk.Label(tab, text="Improving Documentation", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        docs_text = (
            "Good documentation is crucial for any project. Here's how you can help:\n\n"
            "• Improve README and wiki pages\n"
            "• Add or update code comments and docstrings\n"
            "• Create tutorials or how-to guides\n"
            "• Write examples showing how to use different features\n"
            "• Make screencasts or screenshots demonstrating functionality\n\n"
            "The documentation is located in the GitHub wiki and in the code itself."
        )
        
        docs_label = ttk.Label(tab, text=docs_text, wraplength=700, justify="left")
        docs_label.pack(fill="x", pady=10)
        
        # Documentation guidelines
        ttk.Label(tab, text="Documentation Guidelines", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        
        guidelines_text = (
            "When contributing to documentation, please follow these guidelines:\n\n"
            "• Use clear, concise language\n"
            "• Include step-by-step instructions where appropriate\n"
            "• Add screenshots for UI-related documentation\n"
            "• Follow Markdown formatting conventions\n"
            "• Organize content logically with proper headings\n"
            "• Check spelling and grammar"
        )
        
        guidelines_label = ttk.Label(tab, text=guidelines_text, wraplength=700, justify="left")
        guidelines_label.pack(fill="x", pady=10)
        
        # Documentation links
        docs_frame = ttk.Frame(tab)
        docs_frame.pack(fill="x", pady=20)
        
        ttk.Button(docs_frame, text="View Wiki", 
                 command=lambda: webbrowser.open(self.wiki_url)).pack(side="left", padx=5)
        
        ttk.Button(docs_frame, text="Edit README", 
                 command=lambda: webbrowser.open(f"{self.github_url}/edit/main/README.md")).pack(side="left", padx=5)
    
    def create_bugs_tab(self, notebook):
        """Create the bug reporting tab"""
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Report Bugs")
        
        # Bug reporting guide
        ttk.Label(tab, text="How to Report Bugs", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        bugs_text = (
            "Found a bug? Your feedback helps improve p2i for everyone. Here's how to report it effectively:\n\n"
            "1. Check if the bug has already been reported by searching the Issues page\n"
            "2. Create a new issue with a clear title describing the problem\n"
            "3. Include the following information in your report:\n"
            "   • Steps to reproduce the bug\n"
            "   • What you expected to happen\n"
            "   • What actually happened\n"
            "   • Your operating system and p2i version\n"
            "   • Screenshots if applicable\n"
            "   • Any error messages you received\n\n"
            "The more details you provide, the easier it will be to fix the issue."
        )
        
        bugs_label = ttk.Label(tab, text=bugs_text, wraplength=700, justify="left")
        bugs_label.pack(fill="x", pady=10)
        
        # System info collection
        ttk.Label(tab, text="Your System Information", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        
        # Collect system info
        system_info = (
            f"Operating System: {platform.system()} {platform.release()}\n"
            f"Python Version: {platform.python_version()}\n"
            f"p2i Version: 1.0.0\n"  # Replace with actual version
        )
        
        info_frame = ttk.LabelFrame(tab, text="System Information")
        info_frame.pack(fill="x", pady=10)
        
        info_text = tk.Text(info_frame, height=5, width=80, wrap="word")
        info_text.pack(padx=5, pady=5, fill="both", expand=True)
        info_text.insert("1.0", system_info)
        info_text.config(state="disabled")
        
        def copy_system_info():
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(system_info)
            messagebox.showinfo("Copied", "System information copied to clipboard!")
        
        ttk.Button(info_frame, text="Copy to Clipboard", 
                 command=copy_system_info).pack(padx=5, pady=5)
        
        # Quick buttons
        buttons_frame = ttk.Frame(tab)
        buttons_frame.pack(fill="x", pady=20)
        
        ttk.Button(buttons_frame, text="Report New Bug", 
                 command=lambda: webbrowser.open(f"{self.issues_url}/new")).pack(side="left", padx=5)
        
        ttk.Button(buttons_frame, text="View Existing Bugs", 
                 command=lambda: webbrowser.open(f"{self.issues_url}?q=is%3Aissue+is%3Aopen+label%3Abug")).pack(side="left", padx=5)
    
    def create_translate_tab(self, notebook):
        """Create the translation tab"""
        tab = ttk.Frame(notebook, padding=15)
        notebook.add(tab, text="Translate")
        
        # Translation overview
        ttk.Label(tab, text="Help Translate p2i", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        
        translation_text = (
            "Help make p2i accessible to users around the world by contributing translations!\n\n"
            "Currently, we're working on establishing a translation framework to make the UI available in multiple languages. "
            "Once implemented, you'll be able to help translate the application into your native language.\n\n"
            "Benefits of translating:\n"
            "• Make p2i accessible to non-English speakers\n"
            "• Improve user experience for international users\n"
            "• Help grow the global p2i community"
        )
        
        translation_label = ttk.Label(tab, text=translation_text, wraplength=700, justify="left")
        translation_label.pack(fill="x", pady=10)
        
        # How to translate
        ttk.Label(tab, text="Translation Process", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        
        process_text = (
            "The translation system is currently being set up. Once ready, it will involve:\n\n"
            "1. Creating language files for each supported language\n"
            "2. Translating UI strings from English to target languages\n"
            "3. Testing translations in the application\n"
            "4. Submitting translations via pull requests\n\n"
            "If you're interested in helping with translations, please check the GitHub repository for updates."
        )
        
        process_label = ttk.Label(tab, text=process_text, wraplength=700, justify="left")
        process_label.pack(fill="x", pady=10)
        
        # Express interest
        interest_frame = ttk.LabelFrame(tab, text="Express Interest in Translating")
        interest_frame.pack(fill="x", pady=20)
        
        ttk.Label(interest_frame, text="Language you can translate:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        language_var = tk.StringVar()
        language_entry = ttk.Entry(interest_frame, textvariable=language_var, width=30)
        language_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        
        def express_interest():
            language = language_var.get().strip()
            if not language:
                messagebox.showwarning("Input Required", "Please enter a language name.")
                return
                
            # Open GitHub issue with pre-filled template
            issue_title = f"Translation help offered: {language}"
            issue_body = f"I'd like to help translate p2i to {language}."
            issue_url = f"{self.issues_url}/new?title={issue_title}&body={issue_body}&labels=translation"
            
            webbrowser.open(issue_url)
        
        ttk.Button(interest_frame, text="Submit Interest", 
                 command=express_interest).grid(row=1, column=0, columnspan=2, padx=5, pady=10)
    
    def clone_repository(self, repo_url):
        """Clone the repository to local machine"""
        # Ask for directory
        from tkinter import filedialog
        
        target_dir = filedialog.askdirectory(
            title="Select Directory for Repository",
            mustexist=True
        )
        
        if not target_dir:
            return
            
        # Show progress dialog
        progress = tk.Toplevel(self.dialog)
        progress.title("Cloning Repository")
        progress.geometry("400x150")
        progress.transient(self.dialog)
        progress.grab_set()
        
        ttk.Label(progress, text="Cloning repository...").pack(pady=(20, 10))
        
        progressbar = ttk.Progressbar(progress, mode="indeterminate")
        progressbar.pack(fill="x", padx=20, pady=10)
        progressbar.start()
        
        status_var = tk.StringVar(value="Initializing...")
        status_label = ttk.Label(progress, textvariable=status_var)
        status_label.pack(pady=10)
        
        # Clone in separate thread
        def clone_thread():
            result = False
            message = ""
            try:
                # Update status
                progress.after(0, lambda: status_var.set("Cloning repository..."))
                
                # Execute git clone
                process = subprocess.run(
                    ["git", "clone", repo_url, target_dir],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if process.returncode == 0:
                    message = f"Repository cloned successfully to {target_dir}"
                    result = True
                else:
                    message = f"Error: {process.stderr}"
            except Exception as e:
                message = f"Error: {str(e)}"
            
            # Update UI in main thread
            progress.after(0, lambda: self._finish_clone(progress, result, message))
        
        threading.Thread(target=clone_thread).start()
    
    def _finish_clone(self, progress_dialog, success, message):
        """Finish the cloning process"""
        progress_dialog.destroy()
        
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)

# Function to show the contribute dialog
def show_contribute_dialog(parent):
    ContributeDialog(parent)

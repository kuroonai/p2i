import os
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import platform
import subprocess
from version import VERSION
import utils


def _make_scrollable_tab(notebook, tab_text):
    """Create a notebook tab with a vertical scrollbar. Returns the inner frame to pack into."""
    outer = ttk.Frame(notebook)
    notebook.add(outer, text=tab_text)

    canvas = tk.Canvas(outer, highlightthickness=0)
    scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
    inner = ttk.Frame(canvas, padding=15)

    inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_wheel(event):
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_wheel(event):
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _bind_wheel)
    canvas.bind("<Leave>", _unbind_wheel)

    # Make inner frame stretch to canvas width
    def _on_canvas_configure(event):
        canvas.itemconfig(canvas.find_all()[0], width=event.width)

    canvas.bind("<Configure>", _on_canvas_configure)

    return inner


class ContributeDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Contribute to p2i")
        self.dialog.geometry("800x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.focus_set()

        utils.set_dialog_icon(self.dialog)

        self.github_url = "https://github.com/kuroonai/p2i"
        self.issues_url = f"{self.github_url}/issues"
        self.wiki_url = f"{self.github_url}/wiki"
        self.fork_url = f"{self.github_url}/fork"

        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill="both", expand=True)

        self.create_header(main_frame)
        notebook = self.create_notebook(main_frame)
        self.create_quick_links(main_frame)
        self.create_buttons(main_frame)

        self.create_overview_tab(notebook)
        self.create_code_tab(notebook)
        self.create_docs_tab(notebook)
        self.create_bugs_tab(notebook)
        self.create_translate_tab(notebook)

        self.center_dialog(parent)

    def center_dialog(self, parent):
        self.dialog.update_idletasks()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill="x", pady=(0, 20))
        ttk.Label(header_frame, text="Contribute to p2i", font=("Helvetica", 16, "bold")).pack(anchor="w")
        ttk.Label(header_frame, text="Join the community and help improve this project").pack(anchor="w")

    def create_notebook(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill="both", expand=True, pady=10)
        return notebook

    def create_quick_links(self, parent):
        links_frame = ttk.LabelFrame(parent, text="Quick Links")
        links_frame.pack(fill="x", pady=10)

        ttk.Button(links_frame, text="GitHub Repository",
                   command=lambda: webbrowser.open(self.github_url)).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        ttk.Button(links_frame, text="Report an Issue",
                   command=lambda: webbrowser.open(self.issues_url)).grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        ttk.Button(links_frame, text="Documentation",
                   command=lambda: webbrowser.open(self.wiki_url)).grid(row=0, column=2, padx=10, pady=10, sticky="ew")
        ttk.Button(links_frame, text="Fork on GitHub",
                   command=lambda: webbrowser.open(self.fork_url)).grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        for i in range(4):
            links_frame.columnconfigure(i, weight=1)

    def create_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(btn_frame, text="Close", command=self.dialog.destroy).pack(side="right")

    def create_overview_tab(self, notebook):
        tab = _make_scrollable_tab(notebook, "Overview")

        ttk.Label(tab, text="Ways to Contribute", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(tab, text=(
            "There are many ways to contribute to p2i, regardless of your experience level or skills:\n\n"
            "\u2022 Code: Fix bugs, add features, or improve performance\n"
            "\u2022 Documentation: Help improve the docs, wiki, or comments\n"
            "\u2022 Design: Create icons, improve UI, or suggest UX enhancements\n"
            "\u2022 Testing: Try new features and report bugs\n"
            "\u2022 Translation: Help translate the UI to other languages\n"
            "\u2022 Ideas: Suggest new features or improvements\n\n"
            "All contributions are valued and appreciated!"
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        ttk.Label(tab, text="Getting Started", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        ttk.Label(tab, text=(
            "1. Fork the repository on GitHub\n"
            "2. Clone your fork to your local machine\n"
            "3. Create a new branch for your contribution\n"
            "4. Make your changes and test them\n"
            "5. Commit your changes with a clear message\n"
            "6. Push to your fork and submit a pull request\n\n"
            "See the 'Code' tab for more detailed instructions."
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        action_frame = ttk.Frame(tab)
        action_frame.pack(fill="x", pady=20)
        ttk.Button(action_frame, text="View Open Issues",
                   command=lambda: webbrowser.open(f"{self.issues_url}?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22")).pack(side="left", padx=5)
        ttk.Button(action_frame, text="Join Discussion",
                   command=lambda: webbrowser.open(f"{self.github_url}/discussions")).pack(side="left", padx=5)

    def create_code_tab(self, notebook):
        tab = _make_scrollable_tab(notebook, "Code")

        ttk.Label(tab, text="Development Setup", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(tab, text=(
            "To set up a development environment for p2i:\n\n"
            "1. Clone the repository:\n"
            "   git clone https://github.com/kuroonai/p2i.git\n\n"
            "2. Create a virtual environment:\n"
            "   python -m venv venv\n\n"
            "3. Activate the virtual environment:\n"
            "   \u2022 Windows: venv\\Scripts\\activate\n"
            "   \u2022 macOS/Linux: source venv/bin/activate\n\n"
            "4. Install dependencies:\n"
            "   pip install -r requirements.txt\n\n"
            "5. Run the application:\n"
            "   python main.py"
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        ttk.Label(tab, text="Coding Standards", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        ttk.Label(tab, text=(
            "When contributing code, please follow these guidelines:\n\n"
            "\u2022 Follow PEP 8 style guidelines for Python code\n"
            "\u2022 Write descriptive commit messages\n"
            "\u2022 Add comments to explain complex logic\n"
            "\u2022 Include docstrings for functions and classes\n"
            "\u2022 Test your changes before submitting\n"
            "\u2022 Keep pull requests focused on a single feature or fix"
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        clone_frame = ttk.LabelFrame(tab, text="Clone Repository")
        clone_frame.pack(fill="x", pady=10)
        clone_url = tk.StringVar(value="https://github.com/kuroonai/p2i.git")
        ttk.Entry(clone_frame, textvariable=clone_url, width=50).pack(side="left", fill="x", expand=True, padx=5, pady=5)

        def copy_to_clipboard():
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(clone_url.get())
            messagebox.showinfo("Copied", "Repository URL copied to clipboard!")

        ttk.Button(clone_frame, text="Copy", command=copy_to_clipboard).pack(side="left", padx=5, pady=5)

        def check_git():
            try:
                subprocess.run(["git", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                return False

        if check_git():
            ttk.Button(clone_frame, text="Clone Now",
                       command=lambda: self.clone_repository(clone_url.get())).pack(side="left", padx=5, pady=5)

    def create_docs_tab(self, notebook):
        tab = _make_scrollable_tab(notebook, "Documentation")

        ttk.Label(tab, text="Improving Documentation", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(tab, text=(
            "Good documentation is crucial for any project. Here's how you can help:\n\n"
            "\u2022 Improve README and wiki pages\n"
            "\u2022 Add or update code comments and docstrings\n"
            "\u2022 Create tutorials or how-to guides\n"
            "\u2022 Write examples showing how to use different features\n"
            "\u2022 Make screencasts or screenshots demonstrating functionality\n\n"
            "The documentation is located in the GitHub wiki and in the code itself."
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        ttk.Label(tab, text="Documentation Guidelines", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        ttk.Label(tab, text=(
            "When contributing to documentation, please follow these guidelines:\n\n"
            "\u2022 Use clear, concise language\n"
            "\u2022 Include step-by-step instructions where appropriate\n"
            "\u2022 Add screenshots for UI-related documentation\n"
            "\u2022 Follow Markdown formatting conventions\n"
            "\u2022 Organize content logically with proper headings\n"
            "\u2022 Check spelling and grammar"
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        docs_frame = ttk.Frame(tab)
        docs_frame.pack(fill="x", pady=20)
        ttk.Button(docs_frame, text="View Wiki",
                   command=lambda: webbrowser.open(self.wiki_url)).pack(side="left", padx=5)
        ttk.Button(docs_frame, text="Edit README",
                   command=lambda: webbrowser.open(f"{self.github_url}/edit/main/README.md")).pack(side="left", padx=5)

    def create_bugs_tab(self, notebook):
        tab = _make_scrollable_tab(notebook, "Report Bugs")

        ttk.Label(tab, text="How to Report Bugs", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(tab, text=(
            "Found a bug? Your feedback helps improve p2i for everyone. Here's how to report it effectively:\n\n"
            "1. Check if the bug has already been reported by searching the Issues page\n"
            "2. Create a new issue with a clear title describing the problem\n"
            "3. Include the following information in your report:\n"
            "   \u2022 Steps to reproduce the bug\n"
            "   \u2022 What you expected to happen\n"
            "   \u2022 What actually happened\n"
            "   \u2022 Your operating system and p2i version\n"
            "   \u2022 Screenshots if applicable\n"
            "   \u2022 Any error messages you received\n\n"
            "The more details you provide, the easier it will be to fix the issue."
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        ttk.Label(tab, text="Your System Information", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))

        system_info = (
            f"Operating System: {platform.system()} {platform.release()}\n"
            f"Python Version: {platform.python_version()}\n"
            f"p2i Version: {VERSION}\n"
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

        ttk.Button(info_frame, text="Copy to Clipboard", command=copy_system_info).pack(padx=5, pady=5)

        buttons_frame = ttk.Frame(tab)
        buttons_frame.pack(fill="x", pady=20)
        ttk.Button(buttons_frame, text="Report New Bug",
                   command=lambda: webbrowser.open(f"{self.issues_url}/new")).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="View Existing Bugs",
                   command=lambda: webbrowser.open(f"{self.issues_url}?q=is%3Aissue+is%3Aopen+label%3Abug")).pack(side="left", padx=5)

    def create_translate_tab(self, notebook):
        tab = _make_scrollable_tab(notebook, "Translate")

        ttk.Label(tab, text="Help Translate p2i", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(tab, text=(
            "Help make p2i accessible to users around the world by contributing translations!\n\n"
            "Currently, we're working on establishing a translation framework to make the UI available in multiple languages. "
            "Once implemented, you'll be able to help translate the application into your native language.\n\n"
            "Benefits of translating:\n"
            "\u2022 Make p2i accessible to non-English speakers\n"
            "\u2022 Improve user experience for international users\n"
            "\u2022 Help grow the global p2i community"
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        ttk.Label(tab, text="Translation Process", font=("Helvetica", 12, "bold")).pack(anchor="w", pady=(10, 10))
        ttk.Label(tab, text=(
            "The translation system is currently being set up. Once ready, it will involve:\n\n"
            "1. Creating language files for each supported language\n"
            "2. Translating UI strings from English to target languages\n"
            "3. Testing translations in the application\n"
            "4. Submitting translations via pull requests\n\n"
            "If you're interested in helping with translations, please check the GitHub repository for updates."
        ), wraplength=700, justify="left").pack(fill="x", pady=10)

        interest_frame = ttk.LabelFrame(tab, text="Express Interest in Translating")
        interest_frame.pack(fill="x", pady=20)
        ttk.Label(interest_frame, text="Language you can translate:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        language_var = tk.StringVar()
        ttk.Entry(interest_frame, textvariable=language_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        def express_interest():
            language = language_var.get().strip()
            if not language:
                messagebox.showwarning("Input Required", "Please enter a language name.")
                return
            issue_title = f"Translation help offered: {language}"
            issue_body = f"I'd like to help translate p2i to {language}."
            issue_url = f"{self.issues_url}/new?title={issue_title}&body={issue_body}&labels=translation"
            webbrowser.open(issue_url)

        ttk.Button(interest_frame, text="Submit Interest",
                   command=express_interest).grid(row=1, column=0, columnspan=2, padx=5, pady=10)

    def clone_repository(self, repo_url):
        from tkinter import filedialog
        target_dir = filedialog.askdirectory(title="Select Directory for Repository", mustexist=True)
        if not target_dir:
            return

        progress = tk.Toplevel(self.dialog)
        progress.title("Cloning Repository")
        progress.geometry("400x150")
        progress.transient(self.dialog)
        progress.grab_set()
        utils.set_dialog_icon(progress)

        ttk.Label(progress, text="Cloning repository...").pack(pady=(20, 10))
        progressbar = ttk.Progressbar(progress, mode="indeterminate")
        progressbar.pack(fill="x", padx=20, pady=10)
        progressbar.start()
        status_var = tk.StringVar(value="Initializing...")
        ttk.Label(progress, textvariable=status_var).pack(pady=10)

        def clone_thread():
            result = False
            message = ""
            try:
                progress.after(0, lambda: status_var.set("Cloning repository..."))
                process = subprocess.run(
                    ["git", "clone", repo_url, target_dir],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
                if process.returncode == 0:
                    message = f"Repository cloned successfully to {target_dir}"
                    result = True
                else:
                    message = f"Error: {process.stderr}"
            except Exception as e:
                message = f"Error: {str(e)}"
            progress.after(0, lambda: self._finish_clone(progress, result, message))

        threading.Thread(target=clone_thread, daemon=True).start()

    def _finish_clone(self, progress_dialog, success, message):
        progress_dialog.destroy()
        if success:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)


def show_contribute_dialog(parent):
    ContributeDialog(parent)

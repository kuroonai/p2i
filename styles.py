# styles.py - Centralized modern styling for p2i
import tkinter as tk
from tkinter import ttk

# Color palette
COLORS = {
    'primary': '#2563EB',        # Blue 600
    'primary_hover': '#1D4ED8',  # Blue 700
    'primary_light': '#DBEAFE',  # Blue 100
    'accent': '#F59E0B',         # Amber 500
    'success': '#10B981',        # Emerald 500
    'error': '#EF4444',          # Red 500
    'warning': '#F59E0B',        # Amber 500
    'bg': '#F8FAFC',             # Slate 50
    'bg_card': '#FFFFFF',        # White
    'bg_dark': '#1E293B',        # Slate 800
    'border': '#E2E8F0',         # Slate 200
    'border_focus': '#2563EB',   # Blue 600
    'text': '#1E293B',           # Slate 800
    'text_secondary': '#64748B', # Slate 500
    'text_muted': '#94A3B8',     # Slate 400
    'drop_zone_bg': '#F0F9FF',   # Sky 50
    'drop_zone_border': '#7DD3FC', # Sky 300
    'drop_zone_active': '#BAE6FD', # Sky 200
    'tab_active': '#2563EB',
    'tab_inactive': '#94A3B8',
    'progress_bar': '#2563EB',
    'progress_bg': '#E2E8F0',
}

FONTS = {
    'heading': ('Segoe UI', 14, 'bold'),
    'subheading': ('Segoe UI', 11, 'bold'),
    'body': ('Segoe UI', 10),
    'body_small': ('Segoe UI', 9),
    'caption': ('Segoe UI', 8),
    'button': ('Segoe UI', 10),
    'mono': ('Consolas', 10),
}


def apply_modern_theme(root):
    """Apply a modern, cohesive theme to the entire application."""
    style = ttk.Style()

    # Use clam as base theme (most customizable on Windows)
    style.theme_use('clam')

    # General widget styling
    style.configure('.',
        background=COLORS['bg'],
        foreground=COLORS['text'],
        font=FONTS['body'],
        borderwidth=0,
        focusthickness=0,
    )

    # Frame
    style.configure('TFrame', background=COLORS['bg'])
    style.configure('Card.TFrame', background=COLORS['bg_card'], relief='flat')

    # Label
    style.configure('TLabel',
        background=COLORS['bg'],
        foreground=COLORS['text'],
        font=FONTS['body'],
    )
    style.configure('Heading.TLabel',
        font=FONTS['heading'],
        foreground=COLORS['text'],
    )
    style.configure('Subheading.TLabel',
        font=FONTS['subheading'],
        foreground=COLORS['text'],
    )
    style.configure('Secondary.TLabel',
        foreground=COLORS['text_secondary'],
        font=FONTS['body_small'],
    )
    style.configure('Status.TLabel',
        foreground=COLORS['text_secondary'],
        font=FONTS['body_small'],
        background=COLORS['bg'],
    )

    # LabelFrame
    style.configure('TLabelframe',
        background=COLORS['bg_card'],
        foreground=COLORS['text'],
        borderwidth=1,
        relief='solid',
        bordercolor=COLORS['border'],
    )
    style.configure('TLabelframe.Label',
        background=COLORS['bg_card'],
        foreground=COLORS['primary'],
        font=FONTS['subheading'],
    )

    # Button
    style.configure('TButton',
        background=COLORS['primary'],
        foreground='white',
        font=FONTS['button'],
        padding=(12, 6),
        borderwidth=0,
        focusthickness=0,
        focuscolor='',
    )
    style.map('TButton',
        background=[
            ('active', COLORS['primary_hover']),
            ('disabled', COLORS['border']),
        ],
        foreground=[
            ('disabled', COLORS['text_muted']),
        ],
    )

    # Accent Button
    style.configure('Accent.TButton',
        background=COLORS['accent'],
        foreground='white',
        font=('Segoe UI', 10, 'bold'),
        padding=(16, 8),
    )
    style.map('Accent.TButton',
        background=[('active', '#D97706')],
    )

    # Success Button
    style.configure('Success.TButton',
        background=COLORS['success'],
        foreground='white',
        font=('Segoe UI', 10, 'bold'),
        padding=(16, 8),
    )
    style.map('Success.TButton',
        background=[('active', '#059669')],
    )

    # Secondary/outline button
    style.configure('Secondary.TButton',
        background=COLORS['bg_card'],
        foreground=COLORS['primary'],
        font=FONTS['button'],
        padding=(12, 6),
        borderwidth=1,
        relief='solid',
    )
    style.map('Secondary.TButton',
        background=[('active', COLORS['primary_light'])],
    )

    # Danger Button
    style.configure('Danger.TButton',
        background=COLORS['error'],
        foreground='white',
        padding=(12, 6),
    )
    style.map('Danger.TButton',
        background=[('active', '#DC2626')],
    )

    # Entry
    style.configure('TEntry',
        fieldbackground='white',
        foreground=COLORS['text'],
        borderwidth=1,
        relief='solid',
        padding=(8, 4),
    )
    style.map('TEntry',
        bordercolor=[
            ('focus', COLORS['border_focus']),
            ('!focus', COLORS['border']),
        ],
    )

    # Combobox
    style.configure('TCombobox',
        fieldbackground='white',
        foreground=COLORS['text'],
        borderwidth=1,
        padding=(8, 4),
    )
    style.map('TCombobox',
        bordercolor=[
            ('focus', COLORS['border_focus']),
            ('!focus', COLORS['border']),
        ],
    )

    # Spinbox
    style.configure('TSpinbox',
        fieldbackground='white',
        foreground=COLORS['text'],
        borderwidth=1,
        padding=(8, 4),
    )

    # Notebook (tabs)
    style.configure('TNotebook',
        background=COLORS['bg'],
        borderwidth=0,
        tabmargins=(2, 5, 2, 0),
    )
    style.configure('TNotebook.Tab',
        background=COLORS['bg'],
        foreground=COLORS['text_secondary'],
        font=FONTS['body'],
        padding=(14, 8),
        borderwidth=0,
    )
    style.map('TNotebook.Tab',
        background=[
            ('selected', COLORS['bg_card']),
            ('active', COLORS['primary_light']),
        ],
        foreground=[
            ('selected', COLORS['primary']),
            ('active', COLORS['primary']),
        ],
        font=[
            ('selected', ('Segoe UI', 10, 'bold')),
        ],
    )

    # Progressbar
    style.configure('Horizontal.TProgressbar',
        background=COLORS['progress_bar'],
        troughcolor=COLORS['progress_bg'],
        borderwidth=0,
        thickness=8,
    )

    # Scale
    style.configure('Horizontal.TScale',
        background=COLORS['bg'],
        troughcolor=COLORS['progress_bg'],
    )

    # Checkbutton
    style.configure('TCheckbutton',
        background=COLORS['bg'],
        foreground=COLORS['text'],
        font=FONTS['body'],
    )
    style.map('TCheckbutton',
        background=[('active', COLORS['bg'])],
    )

    # Radiobutton
    style.configure('TRadiobutton',
        background=COLORS['bg'],
        foreground=COLORS['text'],
        font=FONTS['body'],
    )
    style.map('TRadiobutton',
        background=[('active', COLORS['bg'])],
    )

    # PanedWindow
    style.configure('TPanedwindow',
        background=COLORS['border'],
    )

    # Scrollbar
    style.configure('Vertical.TScrollbar',
        background=COLORS['border'],
        troughcolor=COLORS['bg'],
        borderwidth=0,
        arrowsize=12,
    )

    # Separator
    style.configure('TSeparator',
        background=COLORS['border'],
    )

    # Configure the root window
    root.configure(bg=COLORS['bg'])

    return style


def create_drop_zone(parent, text="Drop PDF files here or click to browse",
                     on_click=None, on_drop_files=None):
    """Create a visual drop zone widget with dashed border effect."""
    frame = tk.Frame(parent,
        bg=COLORS['drop_zone_bg'],
        highlightbackground=COLORS['drop_zone_border'],
        highlightthickness=2,
        highlightcolor=COLORS['border_focus'],
        padx=20, pady=30,
    )

    icon_label = tk.Label(frame,
        text="PDF",
        font=('Segoe UI', 24, 'bold'),
        fg=COLORS['primary'],
        bg=COLORS['drop_zone_bg'],
    )
    icon_label.pack(pady=(0, 8))

    text_label = tk.Label(frame,
        text=text,
        font=FONTS['body'],
        fg=COLORS['text_secondary'],
        bg=COLORS['drop_zone_bg'],
    )
    text_label.pack(pady=(0, 4))

    hint_label = tk.Label(frame,
        text="Supports .pdf files",
        font=FONTS['caption'],
        fg=COLORS['text_muted'],
        bg=COLORS['drop_zone_bg'],
    )
    hint_label.pack()

    if on_click:
        for widget in [frame, icon_label, text_label, hint_label]:
            widget.configure(cursor='hand2')
            widget.bind('<Button-1>', lambda e: on_click())

    # Hover effects
    def on_enter(e):
        frame.configure(bg=COLORS['drop_zone_active'],
                       highlightbackground=COLORS['border_focus'])
        for w in [icon_label, text_label, hint_label]:
            w.configure(bg=COLORS['drop_zone_active'])

    def on_leave(e):
        frame.configure(bg=COLORS['drop_zone_bg'],
                       highlightbackground=COLORS['drop_zone_border'])
        for w in [icon_label, text_label, hint_label]:
            w.configure(bg=COLORS['drop_zone_bg'])

    frame.bind('<Enter>', on_enter)
    frame.bind('<Leave>', on_leave)

    return frame


def create_empty_state(parent, title="No file selected",
                       description="Upload a PDF to get started",
                       button_text="Browse Files", on_click=None):
    """Create an empty state placeholder with icon and CTA."""
    frame = ttk.Frame(parent)

    # Spacer
    ttk.Label(frame, text="").pack(pady=20)

    # Icon placeholder
    icon = tk.Label(frame,
        text="PDF",
        font=('Segoe UI', 32, 'bold'),
        fg=COLORS['text_muted'],
        bg=COLORS['bg'],
    )
    icon.pack(pady=(0, 12))

    # Title
    title_label = ttk.Label(frame, text=title, style='Heading.TLabel')
    title_label.pack(pady=(0, 6))

    # Description
    desc_label = ttk.Label(frame, text=description, style='Secondary.TLabel')
    desc_label.pack(pady=(0, 16))

    # Button
    if on_click and button_text:
        btn = ttk.Button(frame, text=button_text, command=on_click, style='Accent.TButton')
        btn.pack()

    return frame

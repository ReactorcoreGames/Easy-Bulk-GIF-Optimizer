"""
Custom neo-retro theme for Easy Bulk GIF Optimizer.
Dark background with yellow/orange/red/violet accents.
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def get_custom_theme():
    """
    Returns custom theme configuration dict.

    Color scheme:
    - Backgrounds: Dark (#1a1a1a, #0d0d0d, #000000)
    - Text: White (#ffffff)
    - Accents: Yellow (#FFD700) → Orange (#FF8C00) → Red (#FF4444) → Violet (#9C27B0)
    """
    return {
        'type': 'dark',
        'colors': {
            'primary': '#FFD700',      # Yellow - Primary buttons
            'secondary': '#FF8C00',    # Orange - Secondary buttons
            'success': '#FF8C00',      # Orange - Success states
            'info': '#9C27B0',         # Violet - Info/sliders
            'warning': '#FF8C00',      # Orange - Warnings
            'danger': '#FF4444',       # Red - Cancel/errors
            'light': '#ffffff',        # White text
            'dark': '#1a1a1a',         # Dark background
            'bg': '#0d0d0d',           # Darker background
            'fg': '#ffffff',           # White text
            'selectbg': '#9C27B0',     # Violet - Selected items
            'selectfg': '#ffffff',     # White text on selected
            'border': '#333333',       # Subtle borders
            'inputfg': '#ffffff',      # White input text
            'inputbg': '#1a1a1a',      # Dark input background
        }
    }


def apply_custom_styles(root):
    """
    Apply custom styles to ttk widgets.

    Args:
        root: The root tkinter window
    """
    style = ttk.Style()

    # Configure frame backgrounds
    style.configure('TFrame', background='#0d0d0d')
    style.configure('Dark.TFrame', background='#000000')

    # Configure labels
    style.configure('TLabel',
                   background='#0d0d0d',
                   foreground='#ffffff',
                   font=('Segoe UI', 10))

    style.configure('Title.TLabel',
                   background='#0d0d0d',
                   foreground='#FFD700',  # Yellow title
                   font=('Segoe UI', 18, 'bold'))

    style.configure('Subtitle.TLabel',
                   background='#0d0d0d',
                   foreground='#FF8C00',  # Orange subtitle
                   font=('Segoe UI', 11))

    style.configure('Header.TLabel',
                   background='#0d0d0d',
                   foreground='#FFD700',  # Yellow headers
                   font=('Segoe UI', 12, 'bold'))

    # Configure buttons
    style.configure('Primary.TButton',
                   background='#FFD700',  # Yellow
                   foreground='#000000',
                   borderwidth=0,
                   font=('Segoe UI', 10, 'bold'))

    style.configure('Secondary.TButton',
                   background='#FF8C00',  # Orange
                   foreground='#000000',
                   borderwidth=0,
                   font=('Segoe UI', 10, 'bold'))

    style.configure('Danger.TButton',
                   background='#FF4444',  # Red
                   foreground='#ffffff',
                   borderwidth=0,
                   font=('Segoe UI', 10, 'bold'))

    style.configure('Violet.TButton',
                   background='#9C27B0',  # Violet
                   foreground='#ffffff',
                   borderwidth=0,
                   font=('Segoe UI', 10, 'bold'))

    style.configure('Large.Violet.TButton',
                   background='#9C27B0',  # Violet
                   foreground='#ffffff',
                   borderwidth=0,
                   font=('Segoe UI', 12, 'bold'))  # Larger and bold

    # Configure entries
    style.configure('TEntry',
                   fieldbackground='#1a1a1a',
                   foreground='#ffffff',
                   borderwidth=1,
                   relief='solid')

    # Configure radiobuttons
    style.configure('TRadiobutton',
                   background='#0d0d0d',
                   foreground='#ffffff',
                   font=('Segoe UI', 10))

    # Configure checkbuttons
    style.configure('TCheckbutton',
                   background='#0d0d0d',
                   foreground='#ffffff',
                   font=('Segoe UI', 10))

    # Configure progressbar (violet)
    style.configure('Violet.Horizontal.TProgressbar',
                   background='#9C27B0',
                   troughcolor='#1a1a1a',
                   borderwidth=0,
                   thickness=20)

    # Configure scales/sliders (violet)
    style.configure('Violet.Horizontal.TScale',
                   background='#0d0d0d',
                   troughcolor='#1a1a1a',
                   sliderthickness=20,
                   sliderrelief='flat')

    # Configure labelframes
    style.configure('TLabelframe',
                   background='#0d0d0d',
                   foreground='#FFD700',  # Yellow labels
                   borderwidth=2,
                   relief='solid')

    style.configure('TLabelframe.Label',
                   background='#0d0d0d',
                   foreground='#FFD700',
                   font=('Segoe UI', 10, 'bold'))


def setup_theme(root):
    """
    Initialize and apply the custom theme to the root window.

    Args:
        root: The root tkinter window
    """
    # Set dark theme as base
    style = ttk.Style('darkly')  # ttkbootstrap dark theme

    # Apply custom styles on top
    apply_custom_styles(root)

    # Configure root window
    root.configure(bg='#0d0d0d')

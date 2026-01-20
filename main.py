"""
Easy Bulk GIF Optimizer
Main application entry point.

Author: Reactorcore
Powered by: Gifski (https://gif.ski/)
"""

import sys
import tkinter as tk
import ttkbootstrap as ttk

from gui.main_window import MainWindow
from core.gifski_wrapper import check_gifski_available


def main():
    """Application entry point."""
    # Create root window
    root = ttk.Window(themename="darkly")

    # Check for gifski before initializing GUI
    if not check_gifski_available():
        from tkinter import messagebox
        messagebox.showerror(
            "Dependency Missing",
            "gifski.exe not found!\n\n"
            "Please ensure gifski.exe is in the 'gifski' folder\n"
            "next to this application.\n\n"
            "Download from: https://gif.ski/"
        )
        sys.exit(1)

    # Create and run main window
    app = MainWindow(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()

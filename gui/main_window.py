"""
Main application window for Easy Bulk GIF Optimizer.
Provides unified interface for all three modes.
"""

import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from pathlib import Path
import threading
import webbrowser
import ctypes
import platform
import sys

from gui.theme import setup_theme
from core.batch_processor import BatchProcessor
from core.gifski_wrapper import check_gifski_available
from core.ffmpeg_wrapper import check_ffmpeg_available
from core.logger import log_info
from utils.validators import validate_quality, validate_dimension, validate_fps
from utils.config import Config
from utils.file_utils import scan_all_file_types


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running in development mode - now files are in root
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


class MainWindow:
    """Main application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("Easy Bulk GIF Optimizer")

        # Set window size and position: 900x950 positioned 150px from top, centered horizontally
        window_width = 900
        window_height = 950  # Increased from 900 to 950 (50px taller)

        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate position (centered horizontally, 100px from top)
        x_position = (screen_width - window_width) // 2
        y_position = 100  # Start 100px from top instead of default

        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.resizable(True, True)  # Allow window resizing
        self.root.minsize(800, 800)  # Set minimum size

        # Set application icon
        icon_path = get_resource_path('assets/icon.ico')
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))

        # Set dark title bar on Windows (must happen after window is visible)
        if platform.system() == 'Windows':
            def set_dark_titlebar():
                try:
                    # Windows 10/11 dark title bar
                    hwnd = ctypes.windll.user32.GetForegroundWindow()
                    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                    value = ctypes.c_int(1)
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                        ctypes.byref(value), ctypes.sizeof(value)
                    )
                except:
                    pass  # Silently fail on older Windows versions

            # Apply after window is visible
            self.root.after(100, set_dark_titlebar)

        # Initialize config manager
        self.config = Config()

        # Initialize theme
        setup_theme(root)

        # State variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.selected_mode = tk.StringVar(value="mode3")  # Default to Mode 3 (simplest)

        # Gifski settings with new defaults (will be loaded from config)
        self.quality = tk.IntVar(value=70)
        self.width = tk.IntVar(value=320)  # New default
        self.height = tk.IntVar(value=0)
        self.fps = tk.IntVar(value=20)  # New default
        self.lossy_quality = tk.IntVar(value=80)
        self.motion_quality = tk.IntVar(value=80)

        # Mode 1 specific: Keep temp files option (default ON)
        self.keep_temp_files = tk.BooleanVar(value=True)

        # Processing state
        self.is_processing = False
        self.should_cancel = False
        self.batch_processor = None

        # Build UI first (widgets must exist before loading settings)
        self._build_ui()

        # Load saved settings from config (after UI is built)
        self._load_settings()

        # Check for gifski on startup
        self._check_dependencies()

    def _build_ui(self):
        """Build the complete user interface."""
        # Create main container frame
        container = ttk.Frame(self.root)
        container.pack(fill=BOTH, expand=YES)

        # Create canvas and scrollbar for scrolling support
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=VERTICAL, command=canvas.yview)

        # Create scrollable frame with fixed width to account for scrollbar
        scrollable_frame = ttk.Frame(canvas, padding=20)

        # Configure canvas
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Create window with width that accounts for scrollbar
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor=tk.NW)

        # Update the canvas window width when canvas is resized
        def _configure_canvas(event):
            # Set the width of the scrollable_frame to match canvas width
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind("<Configure>", _configure_canvas)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollbar first (right side), then canvas (fills remaining space)
        scrollbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Use scrollable_frame as the main container
        main_frame = scrollable_frame

        # Header
        self._build_header(main_frame)

        # Mode selector
        self._build_mode_selector(main_frame)

        # Folder selection
        self._build_folder_selection(main_frame)

        # Settings panel
        self._build_settings_panel(main_frame)

        # Progress section
        self._build_progress_section(main_frame)

        # Action buttons
        self._build_action_buttons(main_frame)

        # Footer
        self._build_footer(main_frame)

    def _build_header(self, parent):
        """Build header with title, subtitle, and Help button in upper right."""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=X, pady=(0, 20))

        # Help button in upper right corner
        self.help_btn = ttk.Button(header_frame,
                                    text="Help",
                                    style='Violet.TButton',
                                    command=self._on_help,
                                    width=8)
        self.help_btn.pack(side=RIGHT, anchor=NE)
        ToolTip(self.help_btn,
               text="Open user documentation",
               bootstyle=INFO)

        # Configure the help button to be larger and bold
        self.help_btn.configure(style='Large.Violet.TButton')

        title = ttk.Label(header_frame,
                         text="Easy Bulk GIF Optimizer",
                         style='Title.TLabel')
        title.pack()

        subtitle = ttk.Label(header_frame,
                           text="Convert videos & images to high-quality GIFs • Optimize existing GIFs",
                           style='Subtitle.TLabel')
        subtitle.pack()

    def _build_mode_selector(self, parent):
        """Build mode selection radio buttons."""
        mode_frame = ttk.LabelFrame(parent, text="Select Mode", padding=15)
        mode_frame.pack(fill=X, pady=(0, 15))

        modes = [
            ("mode1", "Mode 1: Video → GIF (Bulk)", "Convert all videos in a folder to GIFs"),
            ("mode2", "Mode 2: Images → GIF (Bulk with Smart Grouping)", "Convert image sequences to animated GIFs"),
            ("mode3", "Mode 3: Optimize GIF (Bulk)", "Re-encode GIFs for better compression")
        ]

        for value, text, description in modes:
            rb = ttk.Radiobutton(mode_frame,
                                text=text,
                                variable=self.selected_mode,
                                value=value,
                                command=self._on_mode_changed)
            rb.pack(anchor=W, pady=5)
            ToolTip(rb, text=description, bootstyle=INFO)

    def _build_folder_selection(self, parent):
        """Build input and output folder selection."""
        folder_frame = ttk.LabelFrame(parent, text="Folders", padding=15)
        folder_frame.pack(fill=X, pady=(0, 15))

        # Input folder
        input_row = ttk.Frame(folder_frame)
        input_row.pack(fill=X, pady=(0, 10))

        ttk.Label(input_row, text="Input Folder:", width=12).pack(side=LEFT)

        input_entry = ttk.Entry(input_row, textvariable=self.input_folder)
        input_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ToolTip(input_entry, text="Folder containing files to process", bootstyle=INFO)

        browse_input_btn = ttk.Button(input_row,
                                      text="Browse",
                                      command=self._browse_input_folder,
                                      width=10)
        browse_input_btn.pack(side=LEFT, padx=(0, 5))
        ToolTip(browse_input_btn, text="Select input folder", bootstyle=INFO)

        open_input_btn = ttk.Button(input_row,
                                    text="Open",
                                    command=self._open_input_folder,
                                    width=8)
        open_input_btn.pack(side=LEFT)
        ToolTip(open_input_btn, text="Open input folder in file explorer", bootstyle=INFO)

        # Output folder
        output_row = ttk.Frame(folder_frame)
        output_row.pack(fill=X)

        ttk.Label(output_row, text="Output Folder:", width=12).pack(side=LEFT)

        output_entry = ttk.Entry(output_row, textvariable=self.output_folder)
        output_entry.pack(side=LEFT, fill=X, expand=YES, padx=5)
        ToolTip(output_entry, text="Folder where GIFs will be saved", bootstyle=INFO)

        browse_output_btn = ttk.Button(output_row,
                                       text="Browse",
                                       command=self._browse_output_folder,
                                       width=10)
        browse_output_btn.pack(side=LEFT, padx=(0, 5))
        ToolTip(browse_output_btn, text="Select output folder", bootstyle=INFO)

        open_output_btn = ttk.Button(output_row,
                                     text="Open",
                                     command=self._open_output_folder,
                                     width=8)
        open_output_btn.pack(side=LEFT)
        ToolTip(open_output_btn, text="Open output folder to view results", bootstyle=INFO)

        # File count display label and keep temp files checkbox
        file_count_frame = ttk.Frame(folder_frame)
        file_count_frame.pack(fill=X, pady=(10, 0))

        self.file_count_label = ttk.Label(file_count_frame,
                                          text="Found: 0 videos, 0 images, 0 gifs",
                                          font=('Segoe UI', 9),
                                          foreground='#888888')
        self.file_count_label.pack(side=LEFT, anchor=W)

        # Vertical divider
        divider = ttk.Separator(file_count_frame, orient=VERTICAL)
        divider.pack(side=LEFT, fill=Y, padx=15)

        # Keep temp files checkbox (Mode 1 only)
        self.keep_temp_checkbox = ttk.Checkbutton(
            file_count_frame,
            text="Keep extracted video frame images (Mode 1)",
            variable=self.keep_temp_files,
            command=self._on_keep_temp_files_changed
        )
        self.keep_temp_checkbox.pack(side=LEFT, anchor=W)
        ToolTip(self.keep_temp_checkbox,
               text="When enabled, extracted video frame images are saved in the output's temp subfolder. "
                    "Useful if you want individual images from each frame of your video. Only applies to Mode 1 (Video → GIF).",
               bootstyle=INFO)

    def _build_settings_panel(self, parent):
        """Build gifski settings panel with sliders."""
        settings_frame = ttk.LabelFrame(parent, text="Gifski Settings", padding=15)
        settings_frame.pack(fill=X, pady=(0, 15))

        # Create 2 columns for settings with divider
        left_col = ttk.Frame(settings_frame)
        left_col.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))

        # Vertical divider between columns
        divider = ttk.Separator(settings_frame, orient=VERTICAL)
        divider.pack(side=LEFT, fill=Y, padx=10)

        right_col = ttk.Frame(settings_frame)
        right_col.pack(side=LEFT, fill=BOTH, expand=YES, padx=(10, 0))

        # Left column settings (increments of 5 for quality, 20 for dimensions)
        self._create_slider(left_col, "Quality (1-100):", self.quality, 1, 100, 5,
                          "Overall GIF quality. Higher = better quality, larger file size")

        self._create_slider(left_col, "Width (pixels, 0=original):", self.width, 0, 2000, 20,
                          "Output width in pixels. 0 keeps original width")

        self._create_slider(left_col, "Height (pixels, 0=original):", self.height, 0, 2000, 20,
                          "Output height in pixels. 0 keeps original height")

        # Right column settings (increments of 5 for quality, FPS)
        self._create_slider(right_col, "FPS (5-60):", self.fps, 5, 60, 5,
                          "Frames per second. Higher = smoother, larger file size")

        self._create_slider(right_col, "Lossy Quality (1-100):", self.lossy_quality, 1, 100, 5,
                          "Compression level. Lower = smaller files, less quality")

        self._create_slider(right_col, "Motion Quality (1-100):", self.motion_quality, 1, 100, 5,
                          "Motion handling quality. Higher = better motion, larger files")

    def _create_slider(self, parent, label_text, variable, from_, to, increment, tooltip):
        """Create a labeled slider with value display, tooltip, and step increments.

        Args:
            parent: Parent widget
            label_text: Label text for the slider
            variable: tkinter variable to bind to
            from_: Minimum value
            to: Maximum value
            increment: Step size for slider (e.g., 5 or 20)
            tooltip: Tooltip text
        """
        frame = ttk.Frame(parent)
        frame.pack(fill=X, pady=(0, 10))

        # Label and value display
        label_row = ttk.Frame(frame)
        label_row.pack(fill=X)

        label = ttk.Label(label_row, text=label_text)
        label.pack(side=LEFT)

        # Fixed-width value label to prevent layout shifts
        value_label = ttk.Label(label_row,
                               text=str(variable.get()),
                               foreground='#9C27B0',  # Violet
                               font=('Segoe UI', 10, 'bold'),
                               width=5,  # Fixed width for up to 4 digits
                               anchor=E)  # Right-align text
        value_label.pack(side=RIGHT)

        # Store reference to value label for reset functionality
        if not hasattr(self, '_value_labels'):
            self._value_labels = []
        self._value_labels.append((variable, value_label))

        # Callback to snap to increments and update label
        def on_slider_change(v):
            value = int(float(v))
            # Snap to nearest increment
            snapped = round(value / increment) * increment
            # Clamp to valid range
            snapped = max(from_, min(to, snapped))
            variable.set(snapped)
            value_label.config(text=str(snapped))
            # Auto-save settings when changed
            self._save_settings()

        # Slider
        slider = ttk.Scale(frame,
                          from_=from_,
                          to=to,
                          variable=variable,
                          orient=HORIZONTAL,
                          style='Violet.Horizontal.TScale',
                          command=on_slider_change)
        slider.pack(fill=X, pady=(5, 0))

        # Tooltip
        ToolTip(label, text=tooltip, bootstyle=INFO)
        ToolTip(slider, text=tooltip, bootstyle=INFO)

    def _build_progress_section(self, parent):
        """Build progress section with status label and dual progress indicators."""
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=X, pady=(0, 15))

        # Status label (shows detailed operation info)
        self.status_label = ttk.Label(progress_frame,
                                      text="Ready to process",
                                      font=('Segoe UI', 10))
        self.status_label.pack(fill=X, pady=(0, 10))

        # Dual progress row: Activity indicator (left) + Overall progress bar (right)
        progress_row = ttk.Frame(progress_frame)
        progress_row.pack(fill=X)

        # Compact activity indicator (indeterminate - shows "working" state)
        self.activity_indicator = ttk.Progressbar(progress_row,
                                                 mode='indeterminate',
                                                 style='Violet.Horizontal.TProgressbar',
                                                 length=80)  # Doubled size from 40 to 80
        self.activity_indicator.pack(side=LEFT, padx=(0, 10))

        # Overall batch progress bar (determinate - shows file progress)
        self.progress_bar = ttk.Progressbar(progress_row,
                                           mode='determinate',
                                           style='Violet.Horizontal.TProgressbar')
        self.progress_bar.pack(side=LEFT, fill=X, expand=YES)

    def _build_action_buttons(self, parent):
        """Build action buttons (test, process, cancel, reset)."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=X, pady=(0, 15))

        # Test file button (yellow)
        self.test_btn = ttk.Button(button_frame,
                                   text="Generate Test File",
                                   style='Primary.TButton',
                                   command=self._on_generate_test,
                                   width=18)
        self.test_btn.pack(side=LEFT, padx=(0, 8))
        ToolTip(self.test_btn,
               text="Process first item only to preview results",
               bootstyle=INFO)

        # Process all button (orange)
        self.process_btn = ttk.Button(button_frame,
                                      text="Process All Files",
                                      style='Secondary.TButton',
                                      command=self._on_process_all,
                                      width=18)
        self.process_btn.pack(side=LEFT, padx=(0, 8))
        ToolTip(self.process_btn,
               text="Process all files in input folder (skips already processed)",
               bootstyle=INFO)

        # Cancel button (red)
        self.cancel_btn = ttk.Button(button_frame,
                                     text="Cancel",
                                     style='Danger.TButton',
                                     command=self._on_cancel,
                                     width=12,
                                     state=DISABLED)
        self.cancel_btn.pack(side=LEFT, padx=(0, 8))
        ToolTip(self.cancel_btn,
               text="Stop processing",
               bootstyle=INFO)

        # Reset to defaults button (violet)
        self.reset_btn = ttk.Button(button_frame,
                                     text="Reset to Defaults",
                                     style='Violet.TButton',
                                     command=self._reset_to_defaults,
                                     width=18)
        self.reset_btn.pack(side=LEFT)
        ToolTip(self.reset_btn,
               text="Reset all settings to default values (Quality: 70, Width: 320, Height: 0, FPS: 20, Lossy: 80, Motion: 80)",
               bootstyle=INFO)

    def _build_footer(self, parent):
        """Build footer with credits and links."""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=X, pady=(10, 0))

        # Separator
        separator = ttk.Separator(footer_frame, orient=HORIZONTAL)
        separator.pack(fill=X, pady=(0, 10))

        # Credits
        credits_text = "Created by "
        credits = ttk.Label(footer_frame, text=credits_text)
        credits.pack(side=LEFT)

        # Reactorcore link
        reactorcore_link = ttk.Label(footer_frame,
                                     text="Reactorcore",
                                     foreground='#9C27B0',  # Violet
                                     cursor='hand2')
        reactorcore_link.pack(side=LEFT)
        reactorcore_link.bind('<Button-1>',
                             lambda e: webbrowser.open('https://github.com/ReactorcoreGames'))
        ToolTip(reactorcore_link, text="Visit Reactorcore Games on GitHub", bootstyle=INFO)

        # Separator
        ttk.Label(footer_frame, text=" • ").pack(side=LEFT)

        # Powered by text
        ttk.Label(footer_frame, text="Powered by ").pack(side=LEFT)

        # Gifski link
        gifski_link = ttk.Label(footer_frame,
                               text="Gifski",
                               foreground='#FF8C00',  # Orange
                               cursor='hand2')
        gifski_link.pack(side=LEFT)
        gifski_link.bind('<Button-1>',
                        lambda e: webbrowser.open('https://gif.ski/'))
        ToolTip(gifski_link, text="Visit Gifski website", bootstyle=INFO)

    def _check_dependencies(self):
        """Check for required dependencies on startup."""
        # Check gifski
        if not check_gifski_available():
            self._show_error("gifski.exe not found!\n\n"
                           "Please ensure gifski.exe is in the 'gifski' folder.")
            self.test_btn.config(state=DISABLED)
            self.process_btn.config(state=DISABLED)

    def _on_mode_changed(self):
        """Handle mode selection change."""
        mode = self.selected_mode.get()

        # Check FFmpeg for Mode 1
        if mode == "mode1":
            ffmpeg_available, ffmpeg_msg = check_ffmpeg_available()
            if not ffmpeg_available:
                self._show_warning("FFmpeg not found in PATH!\n\n"
                                 "Mode 1 (Video → GIF) requires FFmpeg.\n"
                                 "Please install FFmpeg and add it to your system PATH.")

        # Update status
        mode_names = {
            "mode1": "Mode 1: Video → GIF",
            "mode2": "Mode 2: Images → GIF",
            "mode3": "Mode 3: Optimize GIF"
        }
        self._update_status(f"{mode_names[mode]} selected")

        # Update file count display based on new mode
        self._update_file_count()

    def _on_keep_temp_files_changed(self):
        """Handle keep temp files checkbox change."""
        # Auto-save settings when changed
        self._save_settings()

    def _browse_input_folder(self):
        """Open folder browser for input folder."""
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
            self._update_file_count()
            # Auto-save folder path
            self._save_settings()

    def _browse_output_folder(self):
        """Open folder browser for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
            log_info(f"Output folder selected: {folder}")
            # Update file count in case input == output
            self._update_file_count()
            # Auto-save folder path
            self._save_settings()

    def _open_input_folder(self):
        """Open input folder in file explorer."""
        folder = self.input_folder.get()
        if folder and Path(folder).exists():
            webbrowser.open(folder)
        else:
            self._show_error("Input folder not set or does not exist")

    def _open_output_folder(self):
        """Open output folder in file explorer."""
        folder = self.output_folder.get()
        if folder:
            Path(folder).mkdir(parents=True, exist_ok=True)
            webbrowser.open(folder)
        else:
            self._show_error("Output folder not set")

    def _load_settings(self):
        """Load settings from config file."""
        settings = self.config.load()
        self.quality.set(settings.get('quality', 70))
        self.width.set(settings.get('width', 320))
        self.height.set(settings.get('height', 0))
        self.fps.set(settings.get('fps', 20))
        self.lossy_quality.set(settings.get('lossy_quality', 80))
        self.motion_quality.set(settings.get('motion_quality', 80))
        self.keep_temp_files.set(settings.get('keep_temp_files', True))

        # Update slider value labels to match loaded settings
        self._update_value_labels()

        # Load folder paths (only if they exist)
        last_input = settings.get('last_input_folder', '')
        if last_input and Path(last_input).exists():
            self.input_folder.set(last_input)
            self._update_file_count()

        last_output = settings.get('last_output_folder', '')
        if last_output and Path(last_output).exists():
            self.output_folder.set(last_output)

    def _save_settings(self):
        """Save current settings to config file."""
        settings = self._get_current_settings()
        self.config.save(settings)

    def _update_value_labels(self):
        """Update all slider value labels to match their IntVar values."""
        if hasattr(self, '_value_labels'):
            for var, label in self._value_labels:
                label.config(text=str(var.get()))

    def _reset_to_defaults(self):
        """Reset all settings to default values."""
        defaults = self.config.reset_to_defaults()

        # Update all IntVar values
        self.quality.set(defaults['quality'])
        self.width.set(defaults['width'])
        self.height.set(defaults['height'])
        self.fps.set(defaults['fps'])
        self.lossy_quality.set(defaults['lossy_quality'])
        self.motion_quality.set(defaults['motion_quality'])

        # Update all value labels to match
        self._update_value_labels()

        self._update_status("Settings reset to defaults")

    def _get_current_settings(self):
        """Get current gifski settings as dict."""
        return {
            'quality': self.quality.get(),
            'width': self.width.get(),
            'height': self.height.get(),
            'fps': self.fps.get(),
            'lossy_quality': self.lossy_quality.get(),
            'motion_quality': self.motion_quality.get(),
            'keep_temp_files': self.keep_temp_files.get(),
            'last_input_folder': self.input_folder.get(),
            'last_output_folder': self.output_folder.get()
        }

    def _validate_inputs(self):
        """Validate all inputs before processing."""
        # Check folders
        if not self.input_folder.get():
            self._show_error("Please select an input folder")
            return False

        if not self.output_folder.get():
            self._show_error("Please select an output folder")
            return False

        input_path = Path(self.input_folder.get())
        if not input_path.exists():
            self._show_error("Input folder does not exist")
            return False

        # Validate settings
        try:
            validate_quality(self.quality.get())
            validate_quality(self.lossy_quality.get())
            validate_quality(self.motion_quality.get())
            validate_dimension(self.width.get())
            validate_dimension(self.height.get())
            validate_fps(self.fps.get())
        except ValueError as e:
            self._show_error(f"Invalid settings: {e}")
            return False

        return True

    def _on_generate_test(self):
        """Handle 'Generate Test File' button click."""
        if not self._validate_inputs():
            return

        # Disable buttons
        self._set_processing_state(True)
        self.should_cancel = False

        # Start background thread
        thread = threading.Thread(target=self._generate_test_worker, daemon=True)
        thread.start()

    def _generate_test_worker(self):
        """Worker function for test file generation."""
        try:
            mode = self.selected_mode.get()
            input_folder = Path(self.input_folder.get())
            output_folder = Path(self.output_folder.get())
            settings = self._get_current_settings()

            # Create batch processor
            self.batch_processor = BatchProcessor(
                mode=mode,
                input_folder=input_folder,
                output_folder=output_folder,
                settings=settings,
                progress_callback=self._on_progress,
                log_callback=self._on_log
            )

            # Process test file
            stats = self.batch_processor.process_test_file()

            # Success message with mode-specific details
            processed = stats.get('processed', 0)
            skipped = stats.get('skipped', 0)

            if processed == 0 and skipped > 0:
                # Nothing was processed (everything skipped)
                message = f"✓ Test complete! File already exists (skipped)"
                self._update_status_threadsafe(message)
            elif mode == 'mode3' and processed > 0:
                # Mode 3: Show size comparison
                original = stats.get('original_size_mb', 0)
                optimized = stats.get('optimized_size_mb', 0)
                reduction = ((original - optimized) / original * 100) if original > 0 else 0
                message = f"✓ Test complete! {original:.2f} MB → {optimized:.2f} MB ({reduction:.1f}% reduction)"
                self._update_status_threadsafe(message)
            else:
                self._update_status_threadsafe("✓ Test file generated successfully!")

        except Exception as e:
            self._show_error_threadsafe(f"Error generating test file: {e}")

        finally:
            self._set_processing_state_threadsafe(False)
            # Update file count after processing (in case new files were created)
            self.root.after(100, self._update_file_count)  # Small delay to ensure files are written

    def _on_process_all(self):
        """Handle 'Process All Files' button click."""
        if not self._validate_inputs():
            return

        # Disable buttons
        self._set_processing_state(True)
        self.should_cancel = False

        # Start background thread
        thread = threading.Thread(target=self._process_all_worker, daemon=True)
        thread.start()

    def _process_all_worker(self):
        """Worker function for processing all files."""
        try:
            mode = self.selected_mode.get()
            input_folder = Path(self.input_folder.get())
            output_folder = Path(self.output_folder.get())
            settings = self._get_current_settings()

            # Create batch processor
            self.batch_processor = BatchProcessor(
                mode=mode,
                input_folder=input_folder,
                output_folder=output_folder,
                settings=settings,
                progress_callback=self._on_progress,
                log_callback=self._on_log
            )

            # Process all files
            stats = self.batch_processor.process_all_files()

            # Success message with mode-specific details
            processed = stats.get('processed', 0)
            skipped = stats.get('skipped', 0)
            failed = stats.get('failed', 0)

            if processed == 0 and skipped > 0 and failed == 0:
                # Nothing was processed (everything skipped, nothing failed)
                message = f"✓ Complete! All {skipped} file(s) already exist (skipped)"
            elif mode == 'mode3' and processed > 0:
                # Mode 3: Show size comparison
                original = stats.get('original_size_mb', 0)
                optimized = stats.get('optimized_size_mb', 0)
                reduction = ((original - optimized) / original * 100) if original > 0 else 0
                message = (f"✓ Complete! Processed: {processed} | Skipped: {skipped} | Failed: {failed} | "
                          f"Size saved: {original:.2f} MB → {optimized:.2f} MB ({reduction:.1f}% reduction)")
            else:
                # Mode 1 & 2: Standard message
                message = f"✓ Complete! Processed: {processed} | Skipped: {skipped} | Failed: {failed}"
            self._update_status_threadsafe(message)

        except Exception as e:
            self._show_error_threadsafe(f"Error processing files: {e}")

        finally:
            self._set_processing_state_threadsafe(False)
            # Update file count after processing (in case new files were created)
            self.root.after(100, self._update_file_count)  # Small delay to ensure files are written

    def _on_cancel(self):
        """Handle 'Cancel' button click."""
        self.should_cancel = True
        if self.batch_processor:
            self.batch_processor.cancel()
        self._update_status("Cancelling...")

    def _on_progress(self, current, total, message):
        """Callback for progress updates from batch processor."""
        progress = (current / total * 100) if total > 0 else 0
        self._update_progress_threadsafe(progress, message)

    def _on_log(self, message):
        """Callback for status/log messages from batch processor."""
        # Update status label with detailed processing messages
        self._update_status_threadsafe(message)

    def _update_status(self, message):
        """Update status label."""
        self.status_label.config(text=message)

    def _update_status_threadsafe(self, message):
        """Update status label from background thread."""
        self.root.after(0, lambda: self._update_status(message))

    def _update_file_count(self):
        """Update file count label to show all file types found in input folder."""
        # Don't update during processing to avoid confusion
        if self.is_processing:
            return

        input_folder_path = self.input_folder.get()
        if not input_folder_path:
            self.file_count_label.config(text="Found: 0 videos, 0 images, 0 gifs")
            return

        input_path = Path(input_folder_path)
        if not input_path.exists():
            self.file_count_label.config(text="Found: 0 videos, 0 images, 0 gifs")
            return

        try:
            # Scan for all file types
            all_files = scan_all_file_types(input_path)
            video_count = len(all_files['videos'])
            image_count = len(all_files['images'])
            gif_count = len(all_files['gifs'])

            # Update label
            self.file_count_label.config(
                text=f"Found: {video_count} videos, {image_count} images, {gif_count} gifs"
            )

            # Only log if this is a manual folder selection (not post-processing update)
            if not hasattr(self, '_last_logged_count') or self._last_logged_count != (video_count, image_count, gif_count):
                log_info(f"Input folder selected: {input_folder_path} - "
                        f"Found {video_count} videos, {image_count} images, {gif_count} gifs")
                self._last_logged_count = (video_count, image_count, gif_count)

        except Exception as e:
            log_info(f"Error scanning input folder: {e}")
            self.file_count_label.config(text="Found: 0 videos, 0 images, 0 gifs")

    def _update_progress_threadsafe(self, progress, message):
        """Update progress bar and status from background thread."""
        def update():
            self.progress_bar['value'] = progress
            self.status_label.config(text=message)

        self.root.after(0, update)

    def _set_processing_state(self, is_processing):
        """Enable/disable buttons and control activity indicator based on processing state."""
        self.is_processing = is_processing

        if is_processing:
            self.test_btn.config(state=DISABLED)
            self.process_btn.config(state=DISABLED)
            self.cancel_btn.config(state=NORMAL)
            # Start activity indicator animation
            self.activity_indicator.start(8)  # 8ms interval for very fast animation
        else:
            self.test_btn.config(state=NORMAL)
            self.process_btn.config(state=NORMAL)
            self.cancel_btn.config(state=DISABLED)
            # Stop activity indicator and reset progress bar
            self.activity_indicator.stop()
            self.progress_bar['value'] = 0
            # DON'T reset status text here - let completion messages persist

    def _set_processing_state_threadsafe(self, is_processing):
        """Set processing state from background thread."""
        self.root.after(0, lambda: self._set_processing_state(is_processing))

    def _show_error(self, message):
        """Show error message dialog."""
        from tkinter import messagebox
        messagebox.showerror("Error", message)

    def _show_error_threadsafe(self, message):
        """Show error message from background thread."""
        self.root.after(0, lambda: self._show_error(message))

    def _show_warning(self, message):
        """Show warning message dialog."""
        from tkinter import messagebox
        messagebox.showwarning("Warning", message)

    def _on_help(self):
        """Handle Help button click - opens readme.md."""
        readme_path = get_resource_path('readme.md')
        if readme_path.exists():
            try:
                # Open readme.md with default text editor
                if platform.system() == 'Windows':
                    import os
                    os.startfile(str(readme_path))
                else:
                    webbrowser.open(str(readme_path))
            except Exception as e:
                self._show_error(f"Could not open readme.md: {e}")
        else:
            self._show_error("readme.md not found in application directory")

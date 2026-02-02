# Easy Bulk GIF Optimizer - Developer Reference

**Last Updated:** 2026-02-02
**Status:** Complete and ready for distribution

---

## Project Overview

Modern Python GUI application for bulk GIF creation and optimization. Three modes:
1. **Video → GIF** - Convert videos to GIFs (requires FFmpeg)
2. **Images → GIF** - Convert image sequences to GIFs (intelligent grouping)
3. **Optimize GIF** - Re-encode GIFs for better compression

---

## Tech Stack

- **Python 3.10+**
- **GUI:** tkinter + ttkbootstrap (neo-retro dark theme)
- **GIF Processing:** gifski.exe (bundled)
- **Video Processing:** FFmpeg (user must install)
- **Build:** PyInstaller

---

## Project Structure

```
main.py                      # Entry point
gui/
├── main_window.py           # Main GUI
└── theme.py                 # Custom theme
core/
├── batch_processor.py       # Multi-threaded processing
├── gifski_wrapper.py        # Gifski integration
├── ffmpeg_wrapper.py        # FFmpeg integration
└── logger.py                # Logging
utils/
├── config.py                # Settings persistence
├── file_utils.py            # File operations
└── validators.py            # Input validation
gifski/                      # Gifski binary + docs
assets/                      # Icon file
log.txt                      # Application log (auto-created)
```

**Key Principle:** All Python modules (`gui`, `core`, `utils`) are in the root directory for simplicity. All imports use relative notation (e.g., `from core.logger import log_info`) which works both during development AND when PyInstaller bundles everything. No complex path manipulation needed.

---

## Key Features

- **Bulk processing** - Folder-based workflow
- **Skip already processed** - Resume-friendly
- **Test file system** - Preview first item before bulk processing
- **Multi-threaded** - Responsive GUI during processing
- **Settings persistence** - Auto-save/load via config.json
- **Intelligent image grouping** - Groups by filename patterns (Mode 2)
- **File count display** - Shows how many files found when folder is selected
- **Comprehensive logging** - Auto-creates log.txt on startup, all logs append to single file in program directory
- **Scrollable interface** - Vertical scrollbar prevents UI elements from being cut off
- **Keep temp files option** - Checkbox to preserve extracted video frames (Mode 1 only, enabled by default)
- **Dual progress feedback** - Animated activity indicator + batch progress bar with detailed status messages

---

## Building the Executable

### Quick Build:
```bash
build_exe.bat
```

This will:
1. Check dependencies (install PyInstaller if needed)
2. Clean old builds
3. Build standalone .exe with PyInstaller
4. Create RELEASE folder with:
   - Easy-Bulk-GIF-Optimizer.exe
   - readme.md
   - gifski/ folder with gifski.exe and docs
5. Clean up temporary files

### Output:
`RELEASE/Easy-Bulk-GIF-Optimizer.exe` - Ready to distribute

---

## Development Setup

1. Install Python 3.10+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run from source:
   ```bash
   python main.py
   ```

---

## Critical Implementation Notes

### Console Window Suppression
All `subprocess.run()` calls use `creationflags=CREATE_NO_WINDOW` on Windows to prevent console popups during FFmpeg/gifski processing.

### Resource Path Resolution (PyInstaller Compatible)
Both `gifski_wrapper.py` and `main_window.py` use a `get_resource_path()` helper function to resolve paths correctly in both development and PyInstaller exe modes:

```python
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running in development mode - files are in root
        base_path = Path(__file__).parent.parent

    return base_path / relative_path

# Usage:
GIFSKI_PATH = get_resource_path('gifski/gifski.exe')
```

This ensures gifski.exe and other resources are found correctly whether running from source or as a bundled executable.

### Logging System
- Logger auto-initializes on program start, creating `log.txt` in the application directory (uses `sys.executable` for exe, `__file__` for dev)
- All logs are appended to a single `log.txt` file in the program's root directory throughout the session
- All folder selections and file processing operations are logged
- Thread-safe logging for multi-threaded operations

### Skip Logic
All modes check output folder for existing files before processing:
- Mode 1: Skip if `video_name.gif` exists
- Mode 2: Skip if `group_name.gif` exists
- Mode 3: Skip if `optimized_filename.gif` exists

Test mode ignores skip logic (always processes first item).

### File Count Display
When input folder is selected (or mode is changed), the GUI displays how many valid files were found:
- Mode 1: Counts video files (VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'} - GIFs are NOT considered videos)
- Mode 2: Counts image files (IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp'})
- Mode 3: Counts GIF files only

This helps users verify they selected the correct folder and mode.

### Settings Persistence
`utils/config.py` auto-saves settings to `config.json` after every slider change and folder selection. Config file is created with defaults on first startup. Settings are auto-loaded on startup. This includes:
- All gifski settings (quality, width, height, fps, lossy_quality, motion_quality)
- Keep temp files checkbox state
- Last used input and output folder paths (only loaded if folders still exist)

---

## Dependencies (requirements.txt)

```
ttkbootstrap==1.10.1
Pillow==10.1.0
```

Note: tkinter is included with Python on Windows.

---

## Known Issues / Future Improvements

None currently. Application is production-ready.

---

## Build Configuration Details

PyInstaller is configured via command-line arguments in `build_exe.bat`:

- `--onefile` - Single executable (not a folder)
- `--windowed` - No console window
- `--icon` - Custom application icon
- `--add-data` - Bundle gifski/ and assets/ folders
- `--hidden-import` - Ensure tkinter, ttkbootstrap, PIL are included
- `--exclude-module` - Exclude unused heavy libraries (matplotlib, numpy, pandas, etc.)

---

## Testing Checklist

Before release:
- [ ] Test all 3 modes (Video → GIF, Images → GIF, Optimize GIF)
- [ ] Verify skip-already-processed logic works
- [ ] Test "Generate Test File" creates test_*.gif
- [ ] Test "Process All Files" with bulk processing
- [ ] Verify settings persist after restart
- [ ] Test "Reset to Defaults" button
- [ ] Check FFmpeg detection (Mode 1)
- [ ] Test on clean Windows machine without Python installed
- [ ] Verify no console windows popup during processing
- [ ] Check log.txt is created in program directory on startup
- [ ] Verify all logs append to single log.txt in program directory (no log files in output folders)
- [ ] Verify file count displays correctly when folders are selected
- [ ] Verify Mode 1 only counts actual video files (not GIFs)

---

## Distribution

Users only need:
- `Easy-Bulk-GIF-Optimizer.exe`
- `readme.md` (user documentation)
- `gifski/` folder (gifski.exe + readme)

FFmpeg must be installed separately for Mode 1 (Video → GIF).

---

## Recent Updates

### 2026-02-02 (Latest)

#### New Feature: Enhanced Progress Feedback
**Dual-progress UI with detailed status updates** - Significantly improved visual feedback during processing:

**What's New:**
- **Dual Progress Indicators:**
  - Compact animated activity indicator (shows "working" state)
  - Full-width progress bar (shows overall batch progress)
- **Detailed Status Messages:**
  - Real-time operation updates: "Extracting frames from video.mp4...", "Creating GIF from 1079 frames..."
  - File progress tracking: "[2/5] Extracting frames from..."
  - Operation-specific feedback for each processing step
- **Streamlined Completion Messages:**
  - Single-line summary: "✓ Complete! Processed: 5 | Skipped: 2 | Failed: 0"
  - Mode 3 shows size savings: "Size saved: 10.5 MB → 7.2 MB (31.4% reduction)"

**Technical Changes:**
- Updated `_build_progress_section()` in `main_window.py` to add dual progress row
- Added `activity_indicator` (indeterminate progressbar) that animates during processing
- Enhanced status callbacks in `batch_processor.py` to send detailed operation messages
- Updated `_set_processing_state()` to control activity indicator (start/stop animation)
- Improved completion messages for cleaner, more informative output
- Updated `_on_log()` callback to display real-time status updates

### 2026-02-02 (Earlier)

#### Bug Fix:
**Fixed Windows command line length limit error** - Fixed `[WinError 206] The filename or extension is too long` error when processing videos with many frames (1000+). The issue occurred because gifski was being called with all frame paths as individual command-line arguments, which exceeded Windows' 32,767 character limit. Now for videos with more than 50 frames, the application uses a shell glob pattern (`frame*.png`) instead of individual file paths, which works around the command line length restriction. This allows processing of longer videos without errors.

**Technical Changes:**
- Updated `create_gif_from_frames()` in `gifski_wrapper.py` to detect large frame counts
- For >50 frames, uses `shell=True` with glob pattern to avoid command line length limits
- For ≤50 frames, continues using direct file list (original behavior)
- Added `tempfile` import (though not currently used, kept for future enhancements)

### 2026-01-20 (Latest - Evening)

#### Bug Fix:
**Fixed log.txt appearing in output folders** - Logger now correctly writes all logs to a single `log.txt` file in the program's root directory throughout the session. Previously, selecting an output folder would redirect logging to `output_folder/log.txt`, creating multiple log files. Now all logs append to the single root-level log file as intended.

#### New Feature:
**Remember last used folders** - Application now remembers and auto-loads the last used input and output folders on startup (only if they still exist). Folder paths are saved to `config.json` automatically when folders are selected.

#### Changes:
- Removed `configure_logger()` function and `configure()` method from `logger.py`
- Removed `configure_logger()` call from `_browse_output_folder()` in `main_window.py`
- Updated tooltip text for output folder field to remove mention of log.txt
- Added `keep_temp_files`, `last_input_folder`, and `last_output_folder` to `config.py` DEFAULT_SETTINGS
- Updated `config.py` `load()` method to create config.json with defaults on first startup
- Updated `_load_settings()` to load and validate folder paths from config
- Updated `_get_current_settings()` to include folder paths
- Updated `_browse_input_folder()` and `_browse_output_folder()` to auto-save settings when folders change

### 2026-01-20 (Earlier - Afternoon)

#### New Features:
1. **Scrollable GUI** - Added vertical scrollbar to main window to prevent bottom UI elements from being cut off when processing results are displayed
2. **Keep Temp Files Option** - Added checkbox control (enabled by default) to preserve extracted video frames in temp folder for Mode 1
   - Setting is persisted in config.json
   - Only affects Mode 1 (Video → GIF)
   - Useful for debugging or manual inspection of extracted frames

#### Implementation Details:
- GUI now uses Canvas + Scrollbar for scrollable content
- Canvas width dynamically adjusts to prevent content from being cut off by scrollbar
- Mousewheel scrolling enabled
- `keep_temp_files` checkbox placed in Folders section, on same line as file count label with vertical divider
- `keep_temp_files` setting added to config management
- `batch_processor.py` updated to respect the setting - only cleans up temp folder when checkbox is unchecked

### 2026-01-20 (Earlier)

#### Major Refactor:
**Removed src/ folder structure** - All Python modules now live in the root directory for simplicity:
- Moved `gui/`, `core/`, `utils/`, `main.py`, `assets/`, and `gifski/` from `src/` to root
- Updated all path resolution logic to reflect new structure
- Updated `build_exe.bat` to use `main.py` instead of `src/main.py`
- Removed `--paths=src` flag from PyInstaller command

#### Fixed Issues:
1. **GIF Not Considered Video**: Confirmed VIDEO_EXTENSIONS does NOT include `.gif` - GIFs are correctly excluded from video scans
2. **Logger Path Resolution**: Logger now correctly creates `log.txt` in app directory (uses `sys.executable` for exe, `__file__` for dev)
3. **Path Resolution**: Updated `get_resource_path()` in both `gifski_wrapper.py` and `main_window.py` to use `parent.parent` instead of `parent.parent.parent`

#### Why the Change:
The `src/` folder was causing confusion and path resolution headaches. With everything in root:
- Simpler project structure
- No need for sys.path manipulation
- Easier to understand path resolution
- PyInstaller configuration is cleaner

---

*Last build: 2026-01-20*

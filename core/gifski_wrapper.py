"""Wrapper for gifski.exe operations."""

import subprocess
import sys
from pathlib import Path
from typing import Optional, List
from core.logger import log_info, log_error, log_debug

# Windows-specific flag to prevent console window popup
if sys.platform == 'win32':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(sys._MEIPASS)
    except AttributeError:
        # Running in development mode - now files are in root
        base_path = Path(__file__).parent.parent

    return base_path / relative_path


# Path to gifski.exe (relative to project root)
GIFSKI_PATH = get_resource_path('gifski/gifski.exe')


def check_gifski_available() -> tuple[bool, str]:
    """Check if gifski.exe is available.

    Returns:
        Tuple of (is_available, error_message)
    """
    if not GIFSKI_PATH.exists():
        return False, f"gifski.exe not found at: {GIFSKI_PATH}"

    try:
        # Try running gifski --version
        result = subprocess.run(
            [str(GIFSKI_PATH), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            log_debug(f"gifski available: {result.stdout.strip()}")
            return True, ""
        else:
            return False, "gifski.exe failed to run"
    except Exception as e:
        return False, f"Error checking gifski: {e}"


def build_gifski_command(
    mode: str,
    input_path: Path,
    output_path: Path,
    settings: dict,
    frame_files: Optional[List[Path]] = None
) -> List[str]:
    """Build gifski command with all settings.

    Args:
        mode: Processing mode ('video', 'frames', 'optimize')
        input_path: Input file/folder path
        output_path: Output GIF path
        settings: Dictionary of gifski settings
        frame_files: List of frame files (for 'frames' mode)

    Returns:
        List of command arguments
    """
    cmd = [str(GIFSKI_PATH), '-o', str(output_path)]

    # Quality (always included)
    cmd.extend(['--quality', str(settings['quality'])])

    # Width (if specified)
    if settings.get('width', 0) > 0:
        cmd.extend(['--width', str(settings['width'])])

    # Height (if specified)
    if settings.get('height', 0) > 0:
        cmd.extend(['--height', str(settings['height'])])

    # FPS (for video and frames modes)
    if mode in ['video', 'frames']:
        cmd.extend(['--fps', str(settings['fps'])])

    # Lossy quality (always included)
    cmd.extend(['--lossy-quality', str(settings['lossy_quality'])])

    # Motion quality (always included)
    cmd.extend(['--motion-quality', str(settings['motion_quality'])])

    # Add input files
    if mode == 'frames' and frame_files:
        # Add frame files in order
        cmd.extend([str(f) for f in frame_files])
    else:
        # Add single input file
        cmd.append(str(input_path))

    return cmd


def create_gif_from_frames(
    frame_files: List[Path],
    output_path: Path,
    settings: dict
) -> tuple[bool, str]:
    """Create GIF from frame files using gifski.

    Args:
        frame_files: List of frame file paths (sorted)
        output_path: Output GIF path
        settings: Dictionary of gifski settings

    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Build command
        cmd = build_gifski_command('frames', None, output_path, settings, frame_files)

        log_debug(f"Running gifski command: {' '.join(cmd[:10])}... ({len(frame_files)} frames)")

        # Run gifski
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            creationflags=CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            log_info(f"Created GIF: {output_path.name}")
            return True, ""
        else:
            error = result.stderr or "Unknown error"
            log_error(f"gifski failed: {error}")
            return False, error

    except subprocess.TimeoutExpired:
        error = "gifski timed out (5 minute limit)"
        log_error(error)
        return False, error
    except Exception as e:
        error = f"Error running gifski: {e}"
        log_error(error)
        return False, error


def create_gif_from_video(
    video_path: Path,
    output_path: Path,
    settings: dict
) -> tuple[bool, str]:
    """Create GIF from video file using gifski.

    Note: This requires FFmpeg to extract frames first.
    Use create_gif_from_frames after extracting frames.

    Args:
        video_path: Video file path
        output_path: Output GIF path
        settings: Dictionary of gifski settings

    Returns:
        Tuple of (success, error_message)
    """
    # This is a placeholder - actual implementation uses FFmpeg extraction
    # followed by create_gif_from_frames
    return False, "Use FFmpeg extraction + create_gif_from_frames instead"


def optimize_gif(
    gif_path: Path,
    output_path: Path,
    settings: dict
) -> tuple[bool, str]:
    """Optimize existing GIF using gifski.

    Args:
        gif_path: Input GIF path
        output_path: Output GIF path
        settings: Dictionary of gifski settings

    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Build command
        cmd = build_gifski_command('optimize', gif_path, output_path, settings)

        log_debug(f"Running gifski command: {' '.join(cmd)}")

        # Run gifski
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            creationflags=CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            log_info(f"Optimized GIF: {output_path.name}")
            return True, ""
        else:
            error = result.stderr or "Unknown error"
            log_error(f"gifski optimization failed: {error}")
            return False, error

    except subprocess.TimeoutExpired:
        error = "gifski timed out (5 minute limit)"
        log_error(error)
        return False, error
    except Exception as e:
        error = f"Error running gifski: {e}"
        log_error(error)
        return False, error

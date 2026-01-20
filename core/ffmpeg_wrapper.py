"""Wrapper for FFmpeg operations."""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict
from core.logger import log_info, log_error, log_debug

# Windows-specific flag to prevent console window popup
if sys.platform == 'win32':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


def check_ffmpeg_available() -> tuple[bool, str]:
    """Check if FFmpeg is available in system PATH.

    Returns:
        Tuple of (is_available, error_message)
    """
    try:
        # Try running ffmpeg -version
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=5,
            creationflags=CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            # Extract version from output
            version_line = result.stdout.split('\n')[0]
            log_debug(f"FFmpeg available: {version_line}")
            return True, ""
        else:
            return False, "FFmpeg command failed"
    except FileNotFoundError:
        return False, "FFmpeg not found in system PATH. Please install FFmpeg."
    except Exception as e:
        return False, f"Error checking FFmpeg: {e}"


def get_video_info(video_path: Path) -> Optional[Dict]:
    """Get video information (duration, fps, dimensions).

    Args:
        video_path: Path to video file

    Returns:
        Dictionary with video info, or None if error
    """
    try:
        # Use ffprobe to get video info
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate,duration",
                "-of", "default=noprint_wrappers=1",
                str(video_path)
            ],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            info = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    info[key] = value
            return info
        else:
            log_error(f"Failed to get video info: {result.stderr}")
            return None

    except FileNotFoundError:
        log_error("ffprobe not found in system PATH")
        return None
    except Exception as e:
        log_error(f"Error getting video info: {e}")
        return None


def extract_frames(
    video_path: Path,
    output_folder: Path,
    fps: Optional[float] = None
) -> tuple[bool, str, list]:
    """Extract frames from video using FFmpeg.

    Args:
        video_path: Path to video file
        output_folder: Folder to save frames
        fps: Optional frame rate (if None, uses video's native fps)

    Returns:
        Tuple of (success, error_message, list_of_frame_paths)
    """
    try:
        # Ensure output folder exists
        output_folder.mkdir(parents=True, exist_ok=True)

        # Build FFmpeg command
        cmd = ["ffmpeg", "-i", str(video_path)]

        # Set frame rate if specified
        if fps is not None:
            cmd.extend(["-vf", f"fps={fps}"])

        # Output pattern for frames
        output_pattern = output_folder / "frame_%04d.png"
        cmd.extend(["-frame_pts", "0", str(output_pattern)])

        log_debug(f"Extracting frames from {video_path.name}...")

        # Run FFmpeg
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            creationflags=CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            # Get list of extracted frames
            frames = sorted(output_folder.glob("frame_*.png"))
            log_info(f"Extracted {len(frames)} frames from {video_path.name}")
            return True, "", frames
        else:
            error = result.stderr or "Unknown error"
            log_error(f"FFmpeg extraction failed: {error}")
            return False, error, []

    except subprocess.TimeoutExpired:
        error = "FFmpeg timed out (5 minute limit)"
        log_error(error)
        return False, error, []
    except FileNotFoundError:
        error = "FFmpeg not found in system PATH"
        log_error(error)
        return False, error, []
    except Exception as e:
        error = f"Error extracting frames: {e}"
        log_error(error)
        return False, error, []

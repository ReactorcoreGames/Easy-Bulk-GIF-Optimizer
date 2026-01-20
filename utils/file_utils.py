"""File operation utilities."""

import re
from pathlib import Path
from typing import List, Dict


# Supported file extensions
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp'}
GIF_EXTENSION = '.gif'


def scan_folder_for_files(folder: Path, extensions: set) -> List[Path]:
    """Scan folder for files with specific extensions.

    Args:
        folder: Folder to scan
        extensions: Set of file extensions (e.g., {'.mp4', '.avi'})

    Returns:
        List of file paths sorted naturally
    """
    files = []
    for ext in extensions:
        files.extend(folder.glob(f'*{ext}'))
        # Also check uppercase extensions
        files.extend(folder.glob(f'*{ext.upper()}'))

    # Remove duplicates (case-insensitive filesystems may return same file twice)
    unique_files = list(dict.fromkeys(files))

    return sorted(unique_files, key=lambda p: natural_sort_key(p.name))


def scan_for_videos(folder: Path) -> List[Path]:
    """Scan folder for video files (excludes GIFs).

    Args:
        folder: Folder to scan

    Returns:
        List of video file paths (GIFs not included)
    """
    # VIDEO_EXTENSIONS already excludes .gif
    return scan_folder_for_files(folder, VIDEO_EXTENSIONS)


def scan_for_images(folder: Path) -> List[Path]:
    """Scan folder for image files.

    Args:
        folder: Folder to scan

    Returns:
        List of image file paths
    """
    return scan_folder_for_files(folder, IMAGE_EXTENSIONS)


def scan_for_gifs(folder: Path) -> List[Path]:
    """Scan folder for GIF files.

    Args:
        folder: Folder to scan

    Returns:
        List of GIF file paths
    """
    return scan_folder_for_files(folder, {GIF_EXTENSION})


def scan_all_file_types(folder: Path) -> Dict[str, List[Path]]:
    """Scan folder for all supported file types.

    Args:
        folder: Folder to scan

    Returns:
        Dictionary with keys 'videos', 'images', 'gifs' mapping to file lists
    """
    return {
        'videos': scan_for_videos(folder),
        'images': scan_for_images(folder),
        'gifs': scan_for_gifs(folder)
    }


def natural_sort_key(s: str) -> list:
    """Generate natural sorting key for strings.

    Sorts strings naturally (1, 2, 10 not 1, 10, 2).

    Args:
        s: String to generate key for

    Returns:
        List of components for natural sorting
    """
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]


def group_images_by_name(image_files: List[Path]) -> Dict[str, List[Path]]:
    """Group images by base name, handling various numbering patterns.

    Supports patterns like:
    - animation_001.png -> animation.gif
    - frame (1).png -> frame.gif
    - image-0001.png -> image.gif

    Args:
        image_files: List of image file paths

    Returns:
        Dictionary mapping base names to lists of file paths
    """
    groups = {}

    for img_path in image_files:
        # Extract base name (remove numbering patterns)
        # Patterns: _001, (1), _0001, -001, etc.
        base_name = re.sub(r'[_\-\s]\(?(\d+)\)?$', '', img_path.stem)

        # If no pattern matched, use the full stem as base name
        if base_name == img_path.stem:
            # Check for space followed by number
            base_name = re.sub(r'\s+\d+$', '', img_path.stem)

        if base_name not in groups:
            groups[base_name] = []
        groups[base_name].append(img_path)

    # Natural sort within each group
    for base_name in groups:
        groups[base_name].sort(key=lambda p: natural_sort_key(p.name))

    return groups


def ensure_temp_folder(output_folder: Path) -> Path:
    """Ensure temp folder exists within output folder.

    Args:
        output_folder: Output folder path

    Returns:
        Path to temp folder
    """
    temp_folder = output_folder / "temp"
    temp_folder.mkdir(parents=True, exist_ok=True)
    return temp_folder


def cleanup_temp_folder(temp_folder: Path):
    """Clean up all files in temp folder.

    Args:
        temp_folder: Temp folder to clean
    """
    if temp_folder.exists() and temp_folder.is_dir():
        for file in temp_folder.iterdir():
            if file.is_file():
                try:
                    file.unlink()
                except Exception:
                    pass  # Ignore cleanup errors


def get_file_size_mb(file_path: Path) -> float:
    """Get file size in megabytes.

    Args:
        file_path: Path to file

    Returns:
        File size in MB
    """
    if file_path.exists():
        return file_path.stat().st_size / (1024 * 1024)
    return 0.0


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

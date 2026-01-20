"""Input validation utilities."""

from pathlib import Path


def validate_quality(value: int) -> tuple[bool, str]:
    """Validate quality value (1-100).

    Args:
        value: Quality value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        val = int(value)
        if 1 <= val <= 100:
            return True, ""
        return False, "Quality must be between 1 and 100"
    except (ValueError, TypeError):
        return False, "Quality must be a valid number"


def validate_dimension(value: int) -> tuple[bool, str]:
    """Validate width/height dimension (0 or positive).

    Args:
        value: Dimension value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        val = int(value)
        if val >= 0:
            return True, ""
        return False, "Dimension must be 0 (original) or positive"
    except (ValueError, TypeError):
        return False, "Dimension must be a valid number"


def validate_fps(value: float) -> tuple[bool, str]:
    """Validate FPS value (must be positive).

    Args:
        value: FPS value to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        val = float(value)
        if val > 0:
            return True, ""
        return False, "FPS must be positive"
    except (ValueError, TypeError):
        return False, "FPS must be a valid number"


def validate_folder_path(path: str) -> tuple[bool, str]:
    """Validate folder path exists and is a directory.

    Args:
        path: Folder path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path or path.strip() == "":
        return False, "Path cannot be empty"

    folder = Path(path)

    if not folder.exists():
        return False, f"Folder does not exist: {path}"

    if not folder.is_dir():
        return False, f"Path is not a directory: {path}"

    return True, ""


def validate_folders(input_folder: str, output_folder: str) -> tuple[bool, str]:
    """Validate both input and output folders.

    Args:
        input_folder: Input folder path
        output_folder: Output folder path

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate input folder exists
    valid, error = validate_folder_path(input_folder)
    if not valid:
        return False, f"Input folder error: {error}"

    # Validate output folder (must be specified but doesn't need to exist)
    if not output_folder or output_folder.strip() == "":
        return False, "Output folder must be specified"

    # Create output folder if it doesn't exist
    output_path = Path(output_folder)
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Cannot create output folder: {e}"

    return True, ""


def validate_settings(settings: dict) -> tuple[bool, str]:
    """Validate all gifski settings.

    Args:
        settings: Dictionary of settings to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate quality
    valid, error = validate_quality(settings.get('quality', 70))
    if not valid:
        return False, error

    # Validate width
    valid, error = validate_dimension(settings.get('width', 0))
    if not valid:
        return False, f"Width error: {error}"

    # Validate height
    valid, error = validate_dimension(settings.get('height', 0))
    if not valid:
        return False, f"Height error: {error}"

    # Validate FPS
    valid, error = validate_fps(settings.get('fps', 15))
    if not valid:
        return False, error

    # Validate lossy quality
    valid, error = validate_quality(settings.get('lossy_quality', 80))
    if not valid:
        return False, f"Lossy quality error: {error}"

    # Validate motion quality
    valid, error = validate_quality(settings.get('motion_quality', 80))
    if not valid:
        return False, f"Motion quality error: {error}"

    return True, ""

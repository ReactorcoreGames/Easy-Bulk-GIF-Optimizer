"""Multi-threaded batch processing for GIF operations."""

import threading
from pathlib import Path
from typing import Callable, List, Optional
from core.logger import log_info, log_warning, log_error
from core.gifski_wrapper import create_gif_from_frames, optimize_gif
from core.ffmpeg_wrapper import extract_frames
from utils.file_utils import (
    scan_for_videos,
    scan_for_images,
    scan_for_gifs,
    group_images_by_name,
    ensure_temp_folder,
    cleanup_temp_folder,
    get_file_size_mb
)


class BatchProcessor:
    """Multi-threaded batch processor for GIF operations."""

    def __init__(self, mode=None, input_folder=None, output_folder=None,
                 settings=None, progress_callback=None, log_callback=None):
        """Initialize batch processor.

        Args:
            mode: Processing mode ('mode1', 'mode2', 'mode3')
            input_folder: Input folder path
            output_folder: Output folder path
            settings: Dictionary of gifski settings
            progress_callback: Callback(current, total, message) for progress updates
            log_callback: Callback(message) for log messages
        """
        self.mode = mode
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.settings = settings or {}
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_flag = False
        self.current_thread = None

    def cancel(self):
        """Request cancellation of current processing."""
        self.cancel_flag = True
        log_info("Processing cancellation requested")

    def reset_cancel(self):
        """Reset cancellation flag."""
        self.cancel_flag = False

    def process_test_file(self):
        """Process first item only (test mode).

        Calls the appropriate mode-specific method with is_test=True.
        """
        self.reset_cancel()

        if self.mode == 'mode1':
            success, error, stats = self.process_mode1_video_to_gif(
                self.input_folder,
                self.output_folder,
                self.settings,
                self._wrap_progress_callback(),
                self._wrap_status_callback(),
                is_test=True
            )
        elif self.mode == 'mode2':
            success, error, stats = self.process_mode2_images_to_gif(
                self.input_folder,
                self.output_folder,
                self.settings,
                self._wrap_progress_callback(),
                self._wrap_status_callback(),
                is_test=True
            )
        elif self.mode == 'mode3':
            success, error, stats = self.process_mode3_optimize_gif(
                self.input_folder,
                self.output_folder,
                self.settings,
                self._wrap_progress_callback(),
                self._wrap_status_callback(),
                is_test=True
            )
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

        if not success:
            raise RuntimeError(error)

        return stats

    def process_all_files(self):
        """Process all files (bulk mode).

        Calls the appropriate mode-specific method with is_test=False.
        """
        self.reset_cancel()

        if self.mode == 'mode1':
            success, error, stats = self.process_mode1_video_to_gif(
                self.input_folder,
                self.output_folder,
                self.settings,
                self._wrap_progress_callback(),
                self._wrap_status_callback(),
                is_test=False
            )
        elif self.mode == 'mode2':
            success, error, stats = self.process_mode2_images_to_gif(
                self.input_folder,
                self.output_folder,
                self.settings,
                self._wrap_progress_callback(),
                self._wrap_status_callback(),
                is_test=False
            )
        elif self.mode == 'mode3':
            success, error, stats = self.process_mode3_optimize_gif(
                self.input_folder,
                self.output_folder,
                self.settings,
                self._wrap_progress_callback(),
                self._wrap_status_callback(),
                is_test=False
            )
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

        if not success:
            raise RuntimeError(error)

        return stats

    def _wrap_progress_callback(self):
        """Wrap progress callback to match expected signature."""
        if not self.progress_callback:
            return None

        def wrapper(current, total):
            # Calculate percentage
            progress = (current / total * 100) if total > 0 else 0
            # Update with detailed message
            self.progress_callback(current, total, f"Processing file {current} of {total} ({progress:.0f}%)")

        return wrapper

    def _wrap_status_callback(self):
        """Wrap status callback to pass through status messages."""
        if not self.log_callback:
            return None

        return self.log_callback

    def process_mode1_video_to_gif(
        self,
        input_folder: Path,
        output_folder: Path,
        settings: dict,
        progress_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
        is_test: bool = False
    ) -> tuple[bool, str, dict]:
        """Process videos to GIFs (Mode 1).

        Args:
            input_folder: Folder containing video files
            output_folder: Folder for output GIFs
            settings: Dictionary of gifski settings
            progress_callback: Callback for progress updates (current, total)
            status_callback: Callback for status messages
            is_test: If True, only process first video

        Returns:
            Tuple of (success, error_message, statistics)
        """
        try:
            # Scan for videos (excluding output GIFs if input == output folder)
            all_videos = scan_for_videos(input_folder)

            # Filter out GIFs if input folder == output folder
            if input_folder == output_folder:
                videos = [v for v in all_videos if v.suffix.lower() != '.gif']
            else:
                videos = all_videos

            if not videos:
                return False, "No video files found in input folder", {}

            # For test mode, only process first video
            if is_test:
                videos = videos[:1]
                log_info("Test mode: processing first video only")

            # Ensure temp folder exists
            temp_folder = ensure_temp_folder(output_folder)

            # Track statistics
            stats = {
                'total': len(videos),
                'processed': 0,
                'skipped': 0,
                'failed': 0
            }

            # Process each video
            for i, video_path in enumerate(videos):
                if self.cancel_flag:
                    log_info("Processing cancelled by user")
                    break

                # Determine output path
                if is_test:
                    output_path = output_folder / f"test_{video_path.stem}.gif"
                else:
                    output_path = output_folder / f"{video_path.stem}.gif"

                # Check skip logic (unless test mode)
                if not is_test and output_path.exists():
                    log_info(f"Skipped {video_path.name} (already processed)")
                    stats['skipped'] += 1
                    file_num = i + 1
                    if status_callback:
                        status_callback(f"[{file_num}/{stats['total']}] Skipped {video_path.name} (already exists)")
                    if progress_callback:
                        progress_callback(i + 1, stats['total'])
                    continue

                # Update status
                file_num = i + 1
                if status_callback:
                    status_callback(f"[{file_num}/{stats['total']}] Extracting frames from {video_path.name}...")

                log_info(f"Processing video: {video_path.name}")

                # Extract frames using FFmpeg
                success, error, frames = extract_frames(
                    video_path,
                    temp_folder,
                    settings.get('fps')
                )

                if not success or not frames:
                    log_error(f"Failed to extract frames from {video_path.name}: {error}")
                    stats['failed'] += 1
                    cleanup_temp_folder(temp_folder)
                    continue

                # Update status - creating GIF
                if status_callback:
                    status_callback(f"[{file_num}/{stats['total']}] Creating GIF from {len(frames)} frames ({video_path.name})...")

                # Create GIF from frames
                success, error = create_gif_from_frames(frames, output_path, settings)

                # Cleanup temp files (unless user wants to keep them)
                keep_temp_files = settings.get('keep_temp_files', True)
                if not keep_temp_files:
                    cleanup_temp_folder(temp_folder)
                else:
                    log_info(f"Keeping extracted frames in: {temp_folder}")

                if success:
                    stats['processed'] += 1
                    size_mb = get_file_size_mb(output_path)
                    log_info(f"Successfully created {output_path.name} ({size_mb:.2f} MB)")
                else:
                    stats['failed'] += 1
                    log_error(f"Failed to create GIF from {video_path.name}: {error}")

                # Update progress
                if progress_callback:
                    progress_callback(i + 1, stats['total'])

            return True, "", stats

        except Exception as e:
            error = f"Batch processing error: {e}"
            log_error(error)
            return False, error, {}

    def process_mode2_images_to_gif(
        self,
        input_folder: Path,
        output_folder: Path,
        settings: dict,
        progress_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
        is_test: bool = False
    ) -> tuple[bool, str, dict]:
        """Process image sequences to GIFs (Mode 2).

        Args:
            input_folder: Folder containing image files
            output_folder: Folder for output GIFs
            settings: Dictionary of gifski settings
            progress_callback: Callback for progress updates (current, total)
            status_callback: Callback for status messages
            is_test: If True, only process first group

        Returns:
            Tuple of (success, error_message, statistics)
        """
        try:
            # Scan for images
            images = scan_for_images(input_folder)
            if not images:
                return False, "No image files found in input folder", {}

            # Group images by base name
            groups = group_images_by_name(images)
            if not groups:
                return False, "No image groups detected", {}

            # For test mode, only process first group
            group_items = list(groups.items())
            if is_test:
                group_items = group_items[:1]
                log_info("Test mode: processing first group only")

            # Track statistics
            stats = {
                'total': len(group_items),
                'processed': 0,
                'skipped': 0,
                'failed': 0
            }

            # Ensure temp folder exists
            temp_folder = ensure_temp_folder(output_folder)

            # Process each group
            for i, (base_name, image_files) in enumerate(group_items):
                if self.cancel_flag:
                    log_info("Processing cancelled by user")
                    break

                # Determine output path
                if is_test:
                    output_path = output_folder / f"test_{base_name}.gif"
                else:
                    output_path = output_folder / f"{base_name}.gif"

                # Check skip logic (unless test mode)
                if not is_test and output_path.exists():
                    log_info(f"Skipped {base_name} group (already processed)")
                    stats['skipped'] += 1
                    file_num = i + 1
                    if status_callback:
                        status_callback(f"[{file_num}/{stats['total']}] Skipped {base_name} (already exists)")
                    if progress_callback:
                        progress_callback(i + 1, stats['total'])
                    continue

                # Update status
                file_num = i + 1
                if status_callback:
                    status_callback(f"[{file_num}/{stats['total']}] Creating GIF from {len(image_files)} images ({base_name})...")

                log_info(f"Processing group: {base_name} ({len(image_files)} images)")

                # Create GIF from images
                success, error = create_gif_from_frames(image_files, output_path, settings)

                if success:
                    stats['processed'] += 1
                    size_mb = get_file_size_mb(output_path)
                    log_info(f"Successfully created {output_path.name} ({size_mb:.2f} MB)")
                else:
                    stats['failed'] += 1
                    log_error(f"Failed to create GIF from {base_name}: {error}")

                # Update progress
                if progress_callback:
                    progress_callback(i + 1, stats['total'])

            return True, "", stats

        except Exception as e:
            error = f"Batch processing error: {e}"
            log_error(error)
            return False, error, {}

    def process_mode3_optimize_gif(
        self,
        input_folder: Path,
        output_folder: Path,
        settings: dict,
        progress_callback: Optional[Callable] = None,
        status_callback: Optional[Callable] = None,
        is_test: bool = False
    ) -> tuple[bool, str, dict]:
        """Optimize GIFs (Mode 3).

        Args:
            input_folder: Folder containing GIF files
            output_folder: Folder for optimized GIFs
            settings: Dictionary of gifski settings
            progress_callback: Callback for progress updates (current, total)
            status_callback: Callback for status messages
            is_test: If True, only process first GIF

        Returns:
            Tuple of (success, error_message, statistics)
        """
        try:
            # Scan for GIFs
            gifs = scan_for_gifs(input_folder)
            if not gifs:
                return False, "No GIF files found in input folder", {}

            # For test mode, only process first GIF
            if is_test:
                gifs = gifs[:1]
                log_info("Test mode: processing first GIF only")

            # Track statistics
            stats = {
                'total': len(gifs),
                'processed': 0,
                'skipped': 0,
                'failed': 0,
                'original_size_mb': 0.0,
                'optimized_size_mb': 0.0
            }

            # Process each GIF
            for i, gif_path in enumerate(gifs):
                if self.cancel_flag:
                    log_info("Processing cancelled by user")
                    break

                # Determine output path with quality and FPS in filename
                quality = settings.get('quality', 90)
                fps = settings.get('fps', 20)
                stem = gif_path.stem  # filename without extension

                if is_test:
                    output_path = output_folder / f"test_{stem}_optim_{quality}q_{fps}fps.gif"
                else:
                    output_path = output_folder / f"{stem}_optim_{quality}q_{fps}fps.gif"

                # Check skip logic (unless test mode)
                if not is_test and output_path.exists():
                    log_info(f"Skipped {gif_path.name} (already optimized)")
                    stats['skipped'] += 1
                    file_num = i + 1
                    if status_callback:
                        status_callback(f"[{file_num}/{stats['total']}] Skipped {gif_path.name} (already exists)")
                    if progress_callback:
                        progress_callback(i + 1, stats['total'])
                    continue

                # Update status
                file_num = i + 1
                if status_callback:
                    status_callback(f"[{file_num}/{stats['total']}] Optimizing {gif_path.name}...")

                log_info(f"Optimizing GIF: {gif_path.name}")

                # Get original size
                original_size = get_file_size_mb(gif_path)
                stats['original_size_mb'] += original_size

                # Optimize GIF
                success, error = optimize_gif(gif_path, output_path, settings)

                if success:
                    stats['processed'] += 1
                    optimized_size = get_file_size_mb(output_path)
                    stats['optimized_size_mb'] += optimized_size
                    reduction = ((original_size - optimized_size) / original_size * 100) if original_size > 0 else 0
                    log_info(f"Successfully optimized {output_path.name}: "
                            f"{original_size:.2f} MB → {optimized_size:.2f} MB ({reduction:.1f}% reduction)")
                else:
                    stats['failed'] += 1
                    log_error(f"Failed to optimize {gif_path.name}: {error}")

                # Update progress
                if progress_callback:
                    progress_callback(i + 1, stats['total'])

            return True, "", stats

        except Exception as e:
            error = f"Batch processing error: {e}"
            log_error(error)
            return False, error, {}

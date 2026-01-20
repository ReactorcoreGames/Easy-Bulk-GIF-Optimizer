# Easy Bulk GIF Optimizer

**Create amazing GIFs from videos and images • Optimize existing GIFs**

A simple Windows application for bulk GIF creation and optimization.

Also available for download here too: https://reactorcore.itch.io/easy-bulk-gif-optimizer

![itch cover](https://github.com/user-attachments/assets/b3ab771e-0bdb-4f94-8ab3-224b7da5dfbb)

<img width="902" height="954" alt="easy gif bulk optimizer screenshot" src="https://github.com/user-attachments/assets/9ec194c6-8164-48b5-b30f-f8aa1579659b" />

---

## What Does This Do?

### 🎬 Mode 1: Video → GIF
Convert all videos in a folder to high-quality GIFs in one click.
- Works with: MP4, AVI, MOV, MKV, WebM files
- Creates one GIF per video
- **Bonus Feature:** Extracts individual frames from videos
  - Enable "Keep temp files" checkbox to preserve extracted frames
  - Frames are saved as PNG files in a temp folder
  - Great for creating thumbnails, sprite sheets, or manual editing
  - Each video gets its own numbered frame sequence

### 🖼️ Mode 2: Images → GIF
Turn image sequences into animated GIFs automatically.
- Works with: PNG, JPG, JPEG, BMP files
- Smart grouping: Groups images by base name, removing numbers
- Supported numbering patterns:
  - Underscore: `animation_001.png`, `animation_002.png` → `animation.gif`
  - Dash: `frame-01.png`, `frame-02.png` → `frame.gif`
  - Parentheses: `scene (1).png`, `scene (2).png` → `scene.gif`
  - Space: `clip 001.png`, `clip 002.png` → `clip.gif`
- Images without numbers become individual GIFs

### ⚡ Mode 3: Optimize GIF
Make existing GIFs smaller without losing quality.
- Typically 20-50% smaller files
- Better compression than original

---

## Requirements

**For the application:**
- Windows 10 or later

**For Mode 1 only (Video → GIF):**
- FFmpeg must be installed
- Get it here: **https://reactorcore.itch.io/ffmpeg-to-path-installer**
  (This installer automatically sets up FFmpeg for you)

---

## How to Use

### Simple 7-Step Workflow:

1. **Pick a mode** - Video → GIF, Images → GIF, or Optimize GIF
2. **Choose input folder** - Where your source files are
3. **Choose output folder** - Where to save the GIFs
4. **Adjust settings** - Quality, size, speed (or use defaults)
5. **Generate test file** - Process just the first file to preview
6. **Click "Open"** next to Output Folder to view your test
7. **Process all files** - When happy with the test, process everything

**Tip:** Click the "Help" button in the app to open this guide anytime!

---

## Settings Guide

### Quality Settings (Three Types)

**Quality (1-100)** - Overall encoder quality
- Controls the main encoding quality level
- Higher = better visual quality but bigger files
- Web use: 60-70
- High quality: 80-90
- **Recommended starting point: 70**

**Lossy Quality (1-100)** - Compression aggressiveness
- Controls how much the image is compressed
- Lower = smaller files but more artifacts
- Higher = larger files but cleaner image
- Default: 80 (good balance)
- Smaller files: 60-70
- Best quality: 85-95
- **This has the biggest impact on file size**

**Motion Quality (1-100)** - Motion handling quality
- Controls how well motion/animation is preserved
- Higher = smoother motion but larger files
- Lower = choppier motion but smaller files
- Default: 80
- **Important for fast-moving animations**

**Quick Summary:**
- Want smaller files? Lower Lossy Quality
- Want better image quality? Raise Quality
- Want smoother motion? Raise Motion Quality

### Other Settings

**Width & Height** - Output size in pixels (0 = keep original)
- Web use: 640-800 width
- Full quality: 0 (original size)

**FPS** - Frames per second (how smooth the animation is)
- Normal: 15-20
- Smooth motion: 25-30

**Tip:** Use the "Reset to Defaults" button to start over. Default settings (Quality: 70, Lossy: 80, Motion: 80, Width: 320, FPS: 20) work well for most cases.

---

## Smart Features

### Automatic Skip
Already processed a file? The app automatically skips it next time. Safe to:
- Re-run after errors
- Resume interrupted batches
- Add new files to the same folder

### Test Before Processing
Always generate a test file first! This lets you:
- Preview results before processing hundreds of files
- Adjust settings to get exactly what you want
- Save time by avoiding re-processing

### Detailed Logs
Check `log.txt` in your output folder to see:
- What was processed
- What was skipped
- Any errors that occurred

---

## Tips

**For best quality:**
- Use high-quality source files
- Set Quality to 80-90
- Keep Width at 0 (original size)

**For smallest file size:**
- Set Quality to 50-60
- Set Width to 480-640
- Lower FPS to 10-15

**For web use:**
- Quality: 70, Width: 640, FPS: 15
- Try to keep under 5MB per GIF

**Working with image sequences (Mode 2):**
- Name files with numbers in these formats: `frame_001.png`, `frame-01.png`, `frame (1).png`, or `frame 001.png`
- All images with the same base name (before the number) will be grouped into one GIF
- **Leading zeroes are not required** - `file_1.png`, `file_2.png` works just as well as `file_001.png`, `file_002.png`
- Mixing formats like `file_021.png` and `file_22.png` will work but is not recommended for consistency
- Generate a test file first to verify grouping worked correctly
- Check the file count display after selecting input folder to see how many images were found

**Extracting frames from videos (Mode 1):**
- Enable "Keep temp files" checkbox to preserve extracted video frames
- Find frames in a `temp_videoname` folder inside your output directory
- Frames are saved as high-quality PNG files at your video's native resolution
- Perfect for creating video thumbnails, contact sheets, or picking specific frames
- You can then use Mode 2 to turn selected frames back into a custom GIF
- **Tip:** Process a video, keep the frames, delete unwanted ones, then use Mode 2 on the remaining frames for precise control

---

## Troubleshooting

**"FFmpeg not found" error**
- Only needed for Mode 1 (Video → GIF)
- Get it here: https://reactorcore.itch.io/ffmpeg-to-path-installer

**"No files found" error**
- Make sure input folder has the right file types
- Mode 1: Video files (.mp4, .avi, .mov, etc.)
- Mode 2: Image files (.png, .jpg, .bmp)
- Mode 3: GIF files (.gif)

**"No groups detected" error (Mode 2)**
- Image files need numbering in the filename
- Supported patterns: `file_001.png`, `file-01.png`, `file (1).png`, `file 001.png`
- The number must be at the END of the filename (before the extension)
- Make sure at least 2 images share the same base name

**Processing is slow**
- This is normal - high-quality GIF creation takes time
- Expect 10-30 seconds per video/group
- Lower the quality settings if you need faster results

**Output file is too big**
- Lower the Quality and Lossy Quality settings
- Reduce Width to 480-640
- Lower FPS to 10-15
- Run the result through Mode 3 to compress further

---

## File Output

**Mode 1:** Creates `video_name.gif` (matches input filename)
- Example: `myvideo.mp4` → `myvideo.gif`

**Mode 2:** Creates `group_name.gif` (base name without numbers)
- Example: `animation_001.png`, `animation_002.png` → `animation.gif`

**Mode 3:** Creates `filename_optim_[quality]q_[fps]fps.gif` (includes settings in filename)
- Example: `mygif.gif` with Quality=70, FPS=20 → `mygif_optim_70q_20fps.gif`
- This makes it easy to compare different optimization settings

**Test files:** Saved as `test_*.gif` in output folder (same naming pattern as above)

**Logs:** Check `log.txt` in output folder for details

---

## Credits

**Created by Reactorcore** (2026)
- https://linktr.ee/reactorcore

**Powered by:**
- [gifski](https://gif.ski) - The world's best GIF encoder by Kornel Lesiński
- [FFmpeg](https://ffmpeg.org) - Video processing by FFmpeg team

---

## Support

Having issues?
1. Check `log.txt` in your output folder for error details
2. For Mode 1: Make sure FFmpeg is installed
3. Try processing with default settings first
4. Generate a test file to preview before bulk processing

---

**Enjoy making beautiful GIFs!** 🎬✨

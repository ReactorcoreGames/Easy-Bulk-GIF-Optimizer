# Gifski Github Readme

Highest-quality GIF encoder based on [pngquant](https://pngquant.org).

**[gifski](https://gif.ski)** converts video frames to GIF animations using pngquant's fancy features for efficient cross-frame palettes and temporal dithering. It produces animated GIFs that use thousands of colors per frame.

## Usage

gifski is a command-line tool. There is no GUI for Windows or Linux (there is one for [macOS](https://sindresorhus.com/gifski)).

The recommended way is to first export video as PNG frames. If you have `ffmpeg` installed, you can run in terminal:

```sh
ffmpeg -i video.webm frame%04d.png
```

and then make the GIF from the frames:

```sh
gifski -o anim.gif frame*.png
```

You can also resize frames (with `-W <width in pixels>` option). If the input was ever encoded using a lossy video codec it's recommended to at least halve size of the frames to hide compression artefacts and counter chroma subsampling that was done by the video codec.


See `gifski -h` for more options.

### Tips for smaller GIF files

Expect to lose a lot of quality for little gain. GIF just isn't that good at compressing, no matter how much you compromise.

* Use `--width` and `--height` to make the animation smaller. This makes the biggest difference.
* Add `--quality=80` (or a lower number) to lower overall quality. You can fine-tune the quality with:
    * `--lossy-quality=60` lower values make animations noisier/grainy, but reduce file sizes.
    * `--motion-quality=60` lower values cause smearing or banding in frames with motion, but reduce file sizes.

If you need to make a GIF that fits a predefined file size, you have to experiment with different sizes and quality settings. The command line tool will display estimated total file size during compression, but keep in mind that the estimate is very imprecise.

===

# Gifski CLI Usage Readme

The CLI version must be run from a command line (a terminal, `cmd.exe`).

```
gifski --fps 10 --width 320 -o anim.gif video.mp4
```

The above example converts "video.mp4" file to GIF (replace the path with your video's actual path. Most terminals allow you to drag'n'drop the file!), with max resolution of 320 pixels and 10 frames per second. If you get erros about command not found, use full absolute path to gifski(.exe).

You may need **ffmpeg** to convert video to PNG frames first. In your favourite command line/terminal, run:

```
ffmpeg -i video.mp4 frame%04d.png
```

This command takes a file named "video.mp4" and makes files "frame0001.png", "frame0002.png", "frame0003.png", etc. from it (`%04d` makes the frame number. Windows may need `%%04d`). You can usually drag'n'drop files into the terminal window to avoid typing the paths.

and then make the GIF from the frames:

```
gifski -o file.gif frame*.png
```

This command makes file "file.gif" from PNG files with names starting with "frame" (`*` stands for frame numbers). It's equivalent of `gifski -o file.gif frame0001.png frame0002.png frame0003.png`, etc.

See `gifski -h` for more options. The conversion might be a bit slow, because it takes a lot of effort to nicely massage these pixels. Also, you should suffer waiting like the poor users who will be downloading these huge files.

### Large file sizes

By default Gifski maximizes quality at cost of file size, so it is expected that the GIF files will be massive. If you need smaller files:

- Use smaller pixel dimensions of the animation, e.g. `--width 320` on the command line. This helps the most!
- Use lower framerate. When converting from video, use lower fps, e.g. `--fps 10`. This helps a lot too.
- Use lower quality, e.g. `--quality 70`. This may help for movie-like content, but may not do anything for screencast content. Videos with shaky camera may compress better with `--motion-quality=50` and noisy content may compress better with `--lossy-quality=30`.
- Or don't use GIF and use a modern video codec like AV1 and the `<video>` element if you can.
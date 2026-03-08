---
name: tiktok-overlay
version: 1.0.0
description: Adds TikTok-style text overlays to images and videos with styled fonts, backgrounds, strokes, and timed animations.
user-invocable: true
metadata:
  {"openclaw": {"emoji": "🎵", "requires": {"bins": ["python3"]}, "install": [{"type": "uv", "packages": ["Pillow", "moviepy"]}]}}
---

# TikTok Text Overlay Skill

You are a TikTok-style text overlay tool. You add styled text overlays to images and videos, replicating the look and feel of TikTok's built-in text editor.

## Setup

The overlay scripts live in `{baseDir}`:

- `{baseDir}/tiktok_overlay.py` — image overlay engine
- `{baseDir}/tiktok_video_overlay.py` — video overlay engine (uses moviepy)

Before using, ensure dependencies are installed:

```bash
pip3 install Pillow moviepy
```

## Available Styles

| Style         | Value          | Description                          |
|---------------|----------------|--------------------------------------|
| Classic       | `classic`      | Clean bold sans-serif (Arial Bold)   |
| Typewriter    | `typewriter`   | Monospace typewriter look            |
| Handwriting   | `handwriting`  | Casual handwriting font              |
| Neon          | `neon`         | Rounded bold with glow effect        |
| Serif         | `serif`        | Traditional serif (Georgia)          |
| Strong        | `strong`       | Extra bold impact style              |
| Comic         | `comic`        | Playful comic sans style             |

## Background Styles

| Style       | Value        | Description                              |
|-------------|--------------|------------------------------------------|
| None        | `none`       | No background, text only                 |
| Highlight   | `highlight`  | Per-line rounded highlight (TikTok default) |
| Full BG     | `full_bg`    | Single rounded rectangle behind all text |
| Letter      | `letter`     | Per-line tight highlight                 |

## Image Overlay

Use `{baseDir}/tiktok_overlay.py` for images. Run as a Python script:

```python
import sys
sys.path.insert(0, "{baseDir}")
from tiktok_overlay import overlay_text, overlay_texts, TextOverlay, TikTokStyle

# Single text
overlay_text("input.jpg", "Your text here", "output.jpg",
    style=TikTokStyle.CLASSIC,
    font_size=48,
    text_color="#FFFFFF",
    bg_style="highlight",
    bg_color="#000000",
    bg_opacity=0.6,
    position="center",       # "top", "center", "bottom", or (x, y) tuple
    alignment="center",      # "left", "center", "right"
    stroke_width=0,
    stroke_color="#000000",
)

# Multiple overlays on one image
overlay_texts("input.jpg", [
    TextOverlay("Top text", position="top", style=TikTokStyle.CLASSIC, font_size=48, stroke_width=4),
    TextOverlay("Bottom text", position="bottom", style=TikTokStyle.STRONG, text_color="#FF6B6B"),
], "output.jpg")
```

### CLI

```bash
python3 {baseDir}/tiktok_overlay.py <input_image> "<text>" <output_image> [style]
```

## Video Overlay

Use `{baseDir}/tiktok_video_overlay.py` for videos. Supports timed text and fade in/out:

```python
import sys
sys.path.insert(0, "{baseDir}")
from tiktok_video_overlay import overlay_video_text, overlay_video_texts, VideoTextOverlay
from tiktok_overlay import TikTokStyle

# Single text on entire video
overlay_video_text("input.mp4", "Hello!", "output.mp4",
    style=TikTokStyle.CLASSIC, font_size=52, stroke_width=5)

# Multiple timed texts
overlay_video_texts("input.mp4", [
    VideoTextOverlay("Appears 0-3s", t_start=0, t_end=3,
        fade_in=0.5, fade_out=0.5,
        style=TikTokStyle.CLASSIC, position="top", font_size=48, stroke_width=4),
    VideoTextOverlay("Appears 2-5s", t_start=2, t_end=5,
        style=TikTokStyle.STRONG, position="center", font_size=56,
        text_color="#FF6B6B", stroke_width=5, bg_style="none"),
    VideoTextOverlay("Always visible",
        style=TikTokStyle.CLASSIC, position="bottom", font_size=40,
        bg_style="highlight"),
], "output.mp4")
```

### CLI

```bash
python3 {baseDir}/tiktok_video_overlay.py <input_video> "<text>" <output_video> [style]
```

## Key Parameters

| Parameter        | Type              | Default      | Description                                   |
|------------------|-------------------|--------------|-----------------------------------------------|
| `text`           | str               | —            | The text to overlay                           |
| `style`          | TikTokStyle       | `classic`    | Font style                                    |
| `font_size`      | int               | 48           | Font size in pixels                           |
| `text_color`     | str (hex)         | `#FFFFFF`    | Text color                                    |
| `bg_style`       | str               | `highlight`  | Background style                              |
| `bg_color`       | str (hex)         | `#000000`    | Background color                              |
| `bg_opacity`     | float (0-1)       | 0.6          | Background opacity                            |
| `position`       | str or (x,y)      | `center`     | Position: top/center/bottom or pixel coords   |
| `alignment`      | str               | `center`     | Text alignment: left/center/right             |
| `stroke_width`   | int               | 0            | Outline thickness (4-6 for TikTok look)       |
| `stroke_color`   | str (hex)         | `#000000`    | Outline color                                 |
| `max_width_ratio` | float            | 0.85         | Max text width as ratio of image width        |

### Video-only Parameters

| Parameter   | Type           | Default | Description                    |
|-------------|----------------|---------|--------------------------------|
| `t_start`   | float or None  | None    | Start time in seconds          |
| `t_end`     | float or None  | None    | End time in seconds            |
| `fade_in`   | float          | 0.0     | Fade in duration (seconds)     |
| `fade_out`  | float          | 0.0     | Fade out duration (seconds)    |

## Tips

- For the classic TikTok outlined text look, use `bg_style="none"` with `stroke_width=4` or `stroke_width=5`.
- For the TikTok highlight look, use `bg_style="highlight"` with `bg_opacity=0.6`.
- Word wrapping is automatic based on `max_width_ratio`.
- Position can be a string (`top`, `center`, `bottom`) or exact pixel coordinates `(x, y)`.
- Uses macOS system fonts as TikTok-style substitutes. Works out of the box on macOS.

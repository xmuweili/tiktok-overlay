"""
TikTok-style text overlay tool.

Usage:
    from tiktok_overlay import overlay_text, TikTokStyle

    # Simple usage
    overlay_text("input.jpg", "Hello World", "output.jpg")

    # With style
    overlay_text("input.jpg", "Hello World", "output.jpg",
        style=TikTokStyle.CLASSIC,
        font_size=60,
        text_color="#FFFFFF",
        bg_style="highlight",       # none, highlight, full_bg, letter
        bg_color="#000000",
        bg_opacity=0.6,
        position="center",          # top, center, bottom, or (x, y) tuple
        alignment="center",         # left, center, right
        stroke_width=2,
        stroke_color="#000000",
    )

    # Multiple text overlays
    from tiktok_overlay import overlay_texts, TextOverlay
    overlay_texts("input.jpg", [
        TextOverlay("Top text", position="top", style=TikTokStyle.CLASSIC),
        TextOverlay("Bottom text", position="bottom", style=TikTokStyle.NEON),
    ], "output.jpg")
"""

from PIL import Image, ImageDraw, ImageFont
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Union
import os


# --- Font mapping (macOS system fonts as TikTok-like substitutes) ---

FONT_DIR = "/System/Library/Fonts/Supplemental"
FONT_DIR_SYSTEM = "/System/Library/Fonts"


class TikTokStyle(str, Enum):
    CLASSIC = "classic"          # Clean sans-serif (like TikTok Classic)
    TYPEWRITER = "typewriter"    # Monospace/typewriter look
    HANDWRITING = "handwriting"  # Casual handwriting
    NEON = "neon"                # Bold glow effect
    SERIF = "serif"              # Traditional serif
    STRONG = "strong"            # Extra bold / impact
    COMIC = "comic"             # Playful comic style


FONT_MAP = {
    TikTokStyle.CLASSIC: [
        os.path.join(FONT_DIR, "Arial Bold.ttf"),
        os.path.join(FONT_DIR_SYSTEM, "Helvetica.ttc"),
    ],
    TikTokStyle.TYPEWRITER: [
        os.path.join(FONT_DIR, "AmericanTypewriter.ttc"),
        os.path.join(FONT_DIR, "Courier New Bold.ttf"),
    ],
    TikTokStyle.HANDWRITING: [
        os.path.join(FONT_DIR, "ChalkboardSE.ttc"),
        os.path.join(FONT_DIR, "Chalkboard.ttc"),
    ],
    TikTokStyle.NEON: [
        os.path.join(FONT_DIR, "Arial Rounded Bold.ttf"),
        os.path.join(FONT_DIR, "Arial Bold.ttf"),
    ],
    TikTokStyle.SERIF: [
        os.path.join(FONT_DIR, "Georgia Bold.ttf"),
        os.path.join(FONT_DIR, "Georgia.ttf"),
    ],
    TikTokStyle.STRONG: [
        os.path.join(FONT_DIR, "Impact.ttf"),
        os.path.join(FONT_DIR, "Arial Bold.ttf"),
    ],
    TikTokStyle.COMIC: [
        os.path.join(FONT_DIR, "Comic Sans MS Bold.ttf"),
        os.path.join(FONT_DIR, "Comic Sans MS.ttf"),
    ],
}


def _load_font(style: TikTokStyle, size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_MAP.get(style, []):
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)


def _hex_to_rgba(hex_color: str, opacity: float = 1.0) -> tuple:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r, g, b, int(opacity * 255))


def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        current_line = ""
        for word in words:
            test = f"{current_line} {word}".strip()
            bbox = font.getbbox(test)
            if bbox[2] - bbox[0] > max_width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test
        if current_line:
            lines.append(current_line)
    return lines if lines else [""]


@dataclass
class TextOverlay:
    text: str
    style: TikTokStyle = TikTokStyle.CLASSIC
    font_size: int = 48
    text_color: str = "#FFFFFF"
    bg_style: str = "highlight"   # none, highlight, full_bg, letter
    bg_color: str = "#000000"
    bg_opacity: float = 0.6
    position: Union[str, tuple] = "center"  # top, center, bottom, or (x, y)
    alignment: str = "center"     # left, center, right
    stroke_width: int = 0
    stroke_color: str = "#000000"
    padding: int = 8
    line_spacing: int = 6
    max_width_ratio: float = 0.85  # max text width as ratio of image width
    rotation: float = 0.0


def _compute_position(
    img_w: int, img_h: int,
    block_w: int, block_h: int,
    position: Union[str, tuple],
) -> tuple[int, int]:
    if isinstance(position, tuple):
        return position

    x = (img_w - block_w) // 2
    if position == "top":
        y = int(img_h * 0.08)
    elif position == "bottom":
        y = int(img_h * 0.92) - block_h
    else:  # center
        y = (img_h - block_h) // 2
    return x, y


def _draw_text_block(
    img: Image.Image,
    overlay: TextOverlay,
) -> Image.Image:
    """Draw a single text overlay onto the image (returns new image)."""
    img = img.convert("RGBA")
    font = _load_font(overlay.style, overlay.font_size)
    max_width = int(img.width * overlay.max_width_ratio)
    lines = _wrap_text(overlay.text, font, max_width)

    # Measure each line
    line_sizes = []
    for line in lines:
        bbox = font.getbbox(line)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_sizes.append((w, h))

    ascent, descent = font.getmetrics()
    line_height = ascent + descent
    pad = overlay.padding
    total_h = len(lines) * line_height + (len(lines) - 1) * overlay.line_spacing
    block_w = max(s[0] for s in line_sizes) + pad * 2
    block_h = total_h + pad * 2

    bx, by = _compute_position(img.width, img.height, block_w, block_h, overlay.position)

    # Create overlay layer for backgrounds
    bg_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(bg_layer)
    bg_rgba = _hex_to_rgba(overlay.bg_color, overlay.bg_opacity)

    # Draw backgrounds per line or full block
    if overlay.bg_style == "full_bg":
        bg_draw.rounded_rectangle(
            [bx, by, bx + block_w, by + block_h],
            radius=8, fill=bg_rgba,
        )
    elif overlay.bg_style in ("highlight", "letter"):
        y_cursor = by + pad
        for i, line in enumerate(lines):
            lw, _ = line_sizes[i]
            if overlay.alignment == "center":
                lx = bx + (block_w - lw) // 2 - pad
            elif overlay.alignment == "right":
                lx = bx + block_w - lw - pad * 2
            else:
                lx = bx

            bg_draw.rounded_rectangle(
                [lx, y_cursor - 2, lx + lw + pad * 2, y_cursor + line_height + 2],
                radius=4, fill=bg_rgba,
            )
            y_cursor += line_height + overlay.line_spacing

    img = Image.alpha_composite(img, bg_layer)

    # Draw text
    txt_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_layer)
    text_rgba = _hex_to_rgba(overlay.text_color)
    stroke_rgba = _hex_to_rgba(overlay.stroke_color) if overlay.stroke_width > 0 else None

    # Neon glow effect
    if overlay.style == TikTokStyle.NEON:
        glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_layer)
        glow_color = _hex_to_rgba(overlay.text_color, 0.15)
        y_cursor = by + pad
        for i, line in enumerate(lines):
            lw, _ = line_sizes[i]
            if overlay.alignment == "center":
                lx = bx + (block_w - lw) // 2
            elif overlay.alignment == "right":
                lx = bx + block_w - lw - pad
            else:
                lx = bx + pad
            for dx in range(-4, 5):
                for dy in range(-4, 5):
                    glow_draw.text((lx + dx, y_cursor + dy), line, font=font, fill=glow_color)
            y_cursor += line_height + overlay.line_spacing
        img = Image.alpha_composite(img, glow_layer)

    y_cursor = by + pad
    for i, line in enumerate(lines):
        lw, _ = line_sizes[i]
        if overlay.alignment == "center":
            lx = bx + (block_w - lw) // 2
        elif overlay.alignment == "right":
            lx = bx + block_w - lw - pad
        else:
            lx = bx + pad

        if overlay.stroke_width > 0:
            txt_draw.text(
                (lx, y_cursor), line, font=font, fill=text_rgba,
                stroke_width=overlay.stroke_width, stroke_fill=stroke_rgba,
            )
        else:
            txt_draw.text((lx, y_cursor), line, font=font, fill=text_rgba)

        y_cursor += line_height + overlay.line_spacing

    img = Image.alpha_composite(img, txt_layer)
    return img


def overlay_text(
    input_path: str,
    text: str,
    output_path: str,
    style: TikTokStyle = TikTokStyle.CLASSIC,
    font_size: int = 48,
    text_color: str = "#FFFFFF",
    bg_style: str = "highlight",
    bg_color: str = "#000000",
    bg_opacity: float = 0.6,
    position: Union[str, tuple] = "center",
    alignment: str = "center",
    stroke_width: int = 0,
    stroke_color: str = "#000000",
    padding: int = 8,
    line_spacing: int = 6,
    max_width_ratio: float = 0.85,
    rotation: float = 0.0,
) -> str:
    """Add a single TikTok-style text overlay to an image."""
    img = Image.open(input_path)
    t = TextOverlay(
        text=text, style=style, font_size=font_size, text_color=text_color,
        bg_style=bg_style, bg_color=bg_color, bg_opacity=bg_opacity,
        position=position, alignment=alignment, stroke_width=stroke_width,
        stroke_color=stroke_color, padding=padding, line_spacing=line_spacing,
        max_width_ratio=max_width_ratio, rotation=rotation,
    )
    result = _draw_text_block(img, t)
    result.convert("RGB").save(output_path, quality=95)
    return output_path


def overlay_texts(
    input_path: str,
    overlays: list[TextOverlay],
    output_path: str,
) -> str:
    """Add multiple TikTok-style text overlays to an image."""
    img = Image.open(input_path)
    for t in overlays:
        img = _draw_text_block(img, t)
    img.convert("RGB").save(output_path, quality=95)
    return output_path


# --- CLI usage ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 4:
        print("Usage: python tiktok_overlay.py <input_image> <text> <output_image> [style]")
        print(f"Styles: {', '.join(s.value for s in TikTokStyle)}")
        sys.exit(1)

    input_path = sys.argv[1]
    text = sys.argv[2]
    output_path = sys.argv[3]
    style = TikTokStyle(sys.argv[4]) if len(sys.argv) > 4 else TikTokStyle.CLASSIC

    overlay_text(input_path, text, output_path, style=style, stroke_width=2)
    print(f"Saved to {output_path}")

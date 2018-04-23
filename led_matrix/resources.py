from typing import Dict, List

from PIL import Image
from rgbmatrix import graphics

fonts: Dict[str, graphics.Font] = {}
colors: Dict[str, graphics.Color] = {}
images: Dict[str, Image.Image] = {}
animations: Dict[str, List[Image.Image]] = {}


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def load_color(color_hex: str):
    if color_hex not in colors:
        r, g, b = hex_to_rgb(color_hex)
        colors[color_hex] = graphics.Color(r, g, b)
    return colors[color_hex]


def load_font(name: str):
    if name not in fonts:
        font = graphics.Font()
        font.LoadFont("resources/fonts/" + name + ".bdf")
        fonts[name] = font
    return fonts[name]


def load_image(image_path):
    if image_path not in images:
        image = Image.open(image_path)
        image = image.convert("RGB")
        images[image_path] = image
    return images[image_path]


def load_animation(image_path):
    if image_path not in images:
        image = Image.open(image_path)
        palette = image.getpalette()
        frames = []
        try:
            while True:
                image.putpalette(palette)
                frame = Image.new("RGB", image.size)
                frame.paste(image)
                frames.append(frame)
                image.seek(image.tell() + 1)
        except EOFError:
            pass
        animations[image_path] = frames
    return animations[image_path]


print("Loading common fonts...")
load_font("7x13")
load_font("7x13B")
load_font("7x13O")


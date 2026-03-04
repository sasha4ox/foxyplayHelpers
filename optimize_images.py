import os
from PIL import Image, ImageFilter

SRC_DIR = "game-images"
OUT_DIR = "game-banners"

WIDTH = 960
HEIGHT = 480
QUALITY = 85

os.makedirs(OUT_DIR, exist_ok=True)

def make_banner(im, width, height):
    im = im.convert("RGBA")

    # scale to fit height
    scale = height / im.height
    new_w = int(im.width * scale)
    new_h = height
    fg = im.resize((new_w, new_h), Image.LANCZOS)

    # background = blurred version
    bg = im.resize((width, height), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(20))

    canvas = Image.new("RGBA", (width, height))
    canvas.paste(bg, (0, 0))

    x = (width - new_w) // 2
    canvas.paste(fg, (x, 0), fg)

    return canvas

count = 0

SUPPORTED = (".png", ".jpg", ".jpeg", ".webp", ".avif")

for file in os.listdir(SRC_DIR):
    if not file.lower().endswith(SUPPORTED):
        continue

    src = os.path.join(SRC_DIR, file)
    name = os.path.splitext(file)[0] + ".webp"
    out = os.path.join(OUT_DIR, name)

    try:
        im = Image.open(src)
        banner = make_banner(im, WIDTH, HEIGHT)
        banner.save(out, "WEBP", quality=QUALITY, method=6)
        count += 1
    except Exception:
        pass

print(f"Created {count} banners → {OUT_DIR}")
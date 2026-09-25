"""Render the Open Graph card for blacksalamander.studio.

    py tools/make_og.py [--bg <name>]

This is the image people see when the link is pasted into Discord, Slack or a
social post, so it is the first thing many will ever see of the studio. It uses
a real screenshot rather than a wordmark on a flat background, and the same
Newsreader the site sets its headings in.

The font on disk is a subset woff2, which Pillow cannot read, so it is
decompressed and instanced to a static weight in memory via fontTools. That way
there is exactly one font file in the repo and the card cannot drift away from
the site's type.
"""
import io
import os
import sys

from fontTools import ttLib
from fontTools.varLib import instancer
from PIL import Image, ImageDraw, ImageFilter

W, H = 1200, 630
SS = 2                                   # supersample, then downsample
# JPEG, not PNG: this is a photograph, and the same card is 272KB as a PNG
# against 47KB here. Preview fetchers are not patient.
OUT = "public/assets/og.jpg"

# Chosen over the others because the fog carries the mood without exposing the
# placeholder characters, it is cold like the rest of the site, and unlike the
# Grogan shot it has no HUD bars in frame.
BG_DEFAULT = "public/assets/img/bleak-isles-walking.jpg"
MARK = "public/assets/mark.png"
FONT = "public/assets/fonts/newsreader-var.woff2"

TEXT = (231, 238, 251)
DIM = (176, 190, 214)
BONE = (204, 198, 176)
GROUND = (10, 14, 23)


def newsreader(size, weight=500):
    """Pillow cannot open woff2, and this file is variable. Decompress, pin the
    weight axis, hand Pillow a plain static TTF from memory."""
    font = ttLib.TTFont(FONT)                     # fontTools reads woff2
    font.flavor = None                            # drop woff2 compression
    if "fvar" in font:
        font = instancer.instantiateVariableFont(font, {"wght": weight})
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    from PIL import ImageFont
    return ImageFont.truetype(buf, size * SS)


def backdrop(path):
    """Cover-crop the screenshot to the card, then push it back so type reads."""
    im = Image.open(path).convert("RGB")
    scale = max(W * SS / im.width, H * SS / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left = (im.width - W * SS) // 2
    top = (im.height - H * SS) // 2
    im = im.crop((left, top, left + W * SS, top + H * SS))

    # a touch of blur keeps placeholder assets from reading as the subject
    im = im.filter(ImageFilter.GaussianBlur(radius=2.5 * SS))

    # darken overall, then a stronger wash from the left where the type sits
    im = Image.blend(im, Image.new("RGB", im.size, GROUND), 0.55)
    scrim = Image.new("L", im.size, 0)
    px = scrim.load()
    for x in range(im.width):
        t = x / im.width
        # opaque at the left edge, gone by two thirds across
        v = max(0.0, 1.0 - (t / 0.66)) ** 1.4
        col = int(235 * v)
        for y in range(im.height):
            px[x, y] = col
    return Image.composite(Image.new("RGB", im.size, GROUND), im, scrim)


def main():
    bg = BG_DEFAULT
    if "--bg" in sys.argv:
        bg = sys.argv[sys.argv.index("--bg") + 1]

    img = backdrop(bg)
    d = ImageDraw.Draw(img)

    M = 84 * SS

    mark = Image.open(MARK).convert("RGBA")
    mark = mark.resize((118 * SS, 118 * SS), Image.LANCZOS)
    img.paste(mark, (M, 96 * SS), mark)

    f_name = newsreader(74, 500)
    f_tag = newsreader(33, 400)
    f_url = newsreader(23, 500)

    d.text((M, 262 * SS), "Black Salamander", font=f_name, fill=TEXT)
    d.text((M, 344 * SS), "Studios", font=f_name, fill=TEXT)

    d.text((M, 452 * SS), "Real videogames, made by real humans.",
           font=f_tag, fill=DIM)

    d.line([(M, 532 * SS), (M + 74 * SS, 532 * SS)], fill=BONE, width=2 * SS)
    d.text((M, 548 * SS), "blacksalamander.studio", font=f_url, fill=BONE)

    img = img.resize((W, H), Image.LANCZOS)
    img.save(OUT, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"wrote {OUT} from {os.path.basename(bg)} "
          f"({os.path.getsize(OUT) // 1024}KB)")


main()

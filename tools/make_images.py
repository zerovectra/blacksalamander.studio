"""Turn the raw screenshots into web-sized images.

    py tools/make_images.py

Reads every PNG in tools/source/screenshots/ and writes JPEGs to
public/assets/img/ at two widths, so the page can hand the browser a srcset and
phones do not download desktop-sized files.

The originals stay in the repo. They are large, but they are the only copy of
these frames outside the game, and keeping them means the site can be rebuilt
at different sizes later without asking for screenshots again.

Nothing here crops or colour-corrects. These are development shots and should
look like development shots.
"""
import os
import glob

from PIL import Image

SRC = "tools/source/screenshots"
OUT = "public/assets/img"

# wide is for a lead image, narrow for the development strip and for phones
WIDTHS = {"": 1600, "-sm": 800}
QUALITY = 82


def process(path):
    name = os.path.splitext(os.path.basename(path))[0]
    im = Image.open(path)

    # JPEG has no alpha; these are opaque screenshots, so flatten rather than
    # silently dropping the channel
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        flat = Image.new("RGB", im.size, (0, 0, 0))
        flat.paste(im, mask=im.split()[-1])
        im = flat
    else:
        im = im.convert("RGB")

    written = []
    for suffix, width in WIDTHS.items():
        out = im
        if im.width > width:
            height = round(im.height * width / im.width)
            out = im.resize((width, height), Image.LANCZOS)
        dest = f"{OUT}/{name}{suffix}.jpg"
        # no exif, no icc: strip everything the game may have attached
        out.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        written.append((dest, out.size, os.path.getsize(dest) // 1024))
    return written


def main():
    os.makedirs(OUT, exist_ok=True)
    sources = sorted(glob.glob(f"{SRC}/*.png")) + sorted(glob.glob(f"{SRC}/*.jpg"))
    if not sources:
        raise SystemExit(f"no screenshots found in {SRC}")

    total = 0
    for path in sources:
        for dest, size, kb in process(path):
            print(f"  {dest:<52} {size[0]}x{size[1]:<5} {kb}KB")
            total += kb
    print(f"{len(sources)} sources, {total}KB written to {OUT}")


main()

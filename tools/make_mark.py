"""Derive the site's mark and favicons from the studio logo.

The source is the Discord server icon, which is 100x100 ink-on-parchment with the
background baked in. This keys the parchment out along the parchment-to-ink axis,
which gives a proper antialiased coverage mask rather than a hard threshold, then
recolours the ink to bone so it reads on the dark site.

Nothing here upscales the mark for the site itself: the 100px source is downscaled
by the browser to 34px, so it stays crisp. Only the apple-touch icon enlarges it,
and that is a soft brush texture, so it survives.

    py tools/make_mark.py

Replace tools/source/logo-discord-100.png with a higher resolution original when
one exists, and re-run. Nothing else needs to change.
"""
from PIL import Image

SRC = "tools/source/logo-discord-100.png"
OUT = "public/assets/"

PARCHMENT = (204.0, 198.0, 176.0)   # the source background
INK = (58.0, 43.0, 48.0)            # the source foreground
BONE = (204, 198, 176)              # what we draw with on the dark site
GROUND = (10, 14, 23)               # site background, for the touch icon


def coverage(path):
    """Alpha mask: how much ink covers each pixel, 0..255."""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()

    axis = tuple(INK[i] - PARCHMENT[i] for i in range(3))
    den = sum(c * c for c in axis)

    mask = Image.new("L", (w, h))
    mp = mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            t = ((r - PARCHMENT[0]) * axis[0]
                 + (g - PARCHMENT[1]) * axis[1]
                 + (b - PARCHMENT[2]) * axis[2]) / den
            mp[x, y] = max(0, min(255, int(t * 255)))
    return mask


def tinted(mask, rgb, size):
    img = Image.new("RGBA", mask.size, rgb + (0,))
    img.putalpha(mask)
    if size != mask.size[0]:
        img = img.resize((size, size), Image.LANCZOS)
    return img


def main():
    mask = coverage(SRC)

    # header mark and favicons: transparent, bone ink
    tinted(mask, BONE, 100).save(OUT + "mark.png")
    tinted(mask, BONE, 64).save(OUT + "favicon-64.png")
    tinted(mask, BONE, 32).save(OUT + "favicon-32.png")

    # apple touch icon wants an opaque square with its own padding
    touch = Image.new("RGB", (180, 180), GROUND)
    m = tinted(mask, BONE, 140)
    touch.paste(m, (20, 20), m)
    touch.save(OUT + "apple-touch-icon.png")

    print("wrote mark.png, favicon-64.png, favicon-32.png, apple-touch-icon.png")


main()

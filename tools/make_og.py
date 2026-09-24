"""Render the Open Graph card for blacksalamander.studio.

Same palette and salamander mark as the site. Drawn at 2x and downsampled so the
curves come out antialiased, since Pillow's line drawing is not.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1200, 630
SS = 2                      # supersample factor
BG = (10, 14, 23)
ACCENT = (125, 211, 252)
VIOLET = (167, 139, 250)
TEXT = (231, 238, 251)
DIM = (166, 182, 208)
FAINT = (115, 134, 163)
RING = (36, 52, 73)

FONT_DIR = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size * SS)


def cubic(p0, p1, p2, p3, n=80):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        x = u**3 * p0[0] + 3 * u*u*t * p1[0] + 3 * u*t*t * p2[0] + t**3 * p3[0]
        y = u**3 * p0[1] + 3 * u*u*t * p1[1] + 3 * u*t*t * p2[1] + t**3 * p3[1]
        pts.append((x, y))
    return pts


def glow(size, center, radius, color, strength):
    """A soft radial wash, composited additively onto the background."""
    g = Image.radial_gradient("L").resize((radius * 2, radius * 2), Image.LANCZOS)
    g = ImageOps.invert(g).point(lambda v: int(v * strength))
    layer = Image.new("RGB", size, color)
    mask = Image.new("L", size, 0)
    mask.paste(g, (center[0] - radius, center[1] - radius))
    return layer, mask


def tracked_text(draw, xy, text, fnt, fill, tracking):
    """Pillow has no letter-spacing, so place each glyph by hand."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + tracking * SS
    return x


def draw_mark(draw, ox, oy, k):
    """The site's salamander mark, defined in a 100x100 box."""
    def P(p):
        return (ox + p[0] * k, oy + p[1] * k)

    # ring
    r = 44 * k
    draw.ellipse(
        [ox + 50*k - r, oy + 50*k - r, ox + 50*k + r, oy + 50*k + r],
        outline=RING, width=max(1, int(2.2 * k)),
    )

    # spine: three cubic segments, drawn as one polyline
    spine = (
        cubic((20, 78), (34, 78), (28, 62), (39, 56))
        + cubic((39, 56), (50, 50), (56, 57), (62, 48))
        + cubic((62, 48), (68, 39), (62, 31), (69, 27))
    )
    draw.line([P(p) for p in spine], fill=ACCENT,
              width=int(6.5 * k), joint="curve")

    for a, b in [((39, 56), (29, 66)), ((39, 56), (48, 66)),
                 ((63, 46), (55, 38)), ((63, 46), (71, 53))]:
        draw.line([P(a), P(b)], fill=ACCENT, width=int(5 * k))
        for pt in (a, b):                      # round the caps
            cr = 2.5 * k
            cx, cy = P(pt)
            draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=ACCENT)

    hr = 6 * k
    hx, hy = P((73, 24))
    draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=ACCENT)


def main():
    size = (W * SS, H * SS)
    img = Image.new("RGB", size, BG)

    for center, radius, color, strength in [
        ((260 * SS, 90 * SS), 520 * SS, ACCENT, 0.17),
        ((1010 * SS, 40 * SS), 430 * SS, VIOLET, 0.13),
    ]:
        layer, mask = glow(size, center, radius, color, strength)
        img = Image.composite(layer, img, mask)

    d = ImageDraw.Draw(img)

    # faint vertical rules, echoing the hero background
    for x in range(120, W, 108):
        d.line([(x * SS, 0), (x * SS, H * SS)], fill=(19, 26, 39), width=1 * SS)

    M = 96 * SS                               # left margin

    draw_mark(d, M, 74 * SS, 1.55 * SS)

    f_eyebrow = font("consolab.ttf", 19)
    f_title = font("segoeuib.ttf", 78)
    f_tag = font("segoeui.ttf", 31)
    f_url = font("consola.ttf", 24)

    y = 268 * SS
    d.line([(M, y + 9 * SS), (M + 34 * SS, y + 9 * SS)], fill=ACCENT, width=2 * SS)
    tracked_text(d, (M + 50 * SS, y), "INDEPENDENT GAME STUDIO", f_eyebrow, ACCENT, 4.5)

    d.text((M, 306 * SS), "Black Salamander", font=f_title, fill=TEXT)
    d.text((M, 392 * SS), "Studio", font=f_title, fill=TEXT)

    d.text((M, 500 * SS), "We build worlds that keep going after you log off.",
           font=f_tag, fill=DIM)

    d.line([(M, 566 * SS), ((W - 96) * SS, 566 * SS)], fill=(30, 41, 59), width=2 * SS)
    d.text((M, 580 * SS), "blacksalamander.studio", font=f_url, fill=FAINT)

    img = img.resize((W, H), Image.LANCZOS)
    out = "Z:/Modding/blacksalamander.studio/public/assets/og.png"
    img.save(out, "PNG", optimize=True)
    print("wrote", out, img.size)


main()

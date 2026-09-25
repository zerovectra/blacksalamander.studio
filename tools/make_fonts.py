"""Fetch and subset the display typeface, and write it into public/assets/fonts/.

    py tools/make_fonts.py

The site sets font-src 'self' and makes no external requests, so the font is
self-hosted rather than loaded from Google Fonts. That also means no third
party sees who visits the site.

Subsetting to Latin plus the punctuation actually used takes the file from
tens of kilobytes to a few, which matters because this is a render-blocking
resource on a page whose whole point is loading fast.

Newsreader is licensed under the SIL Open Font License 1.1, which permits
self-hosting and redistribution. The licence is written alongside the fonts.
"""
import os
import re
import subprocess
import sys
import urllib.request

FAMILY = "Newsreader"
WEIGHTS = [400, 600]          # requested from Google; both return the same variable file
OUT = "public/assets/fonts"

# Latin letters, digits, and the punctuation this site actually sets in display
# type. Anything outside this falls back to the body stack, which is fine: the
# display face is only ever used for headings and the wordmark.
GLYPHS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    " .,:;!?'\"()[]/&@#%+-–—…·"
)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

LICENCE = "https://raw.githubusercontent.com/google/fonts/main/ofl/newsreader/OFL.txt"


def get(url, binary=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if binary else data.decode("utf-8")


def latin_woff2_urls():
    """Ask Google Fonts for the CSS, take the latin block's woff2 per weight."""
    css = get(
        "https://fonts.googleapis.com/css2?family="
        + FAMILY.replace(" ", "+")
        + ":wght@"
        + ";".join(str(w) for w in WEIGHTS)
        + "&display=swap",
        binary=False,
    )

    urls = {}
    for block in css.split("@font-face")[1:]:
        # the latin range is the one containing U+0000-00FF
        if "U+0000-00FF" not in block:
            continue
        weight = re.search(r"font-weight:\s*(\d+)", block)
        url = re.search(r"url\((https://[^)]+\.woff2)\)", block)
        if weight and url and int(weight.group(1)) in WEIGHTS:
            urls[int(weight.group(1))] = url.group(1)
    missing = [w for w in WEIGHTS if w not in urls]
    if missing:
        raise SystemExit(f"no latin woff2 found for weights {missing}")
    return urls


def main():
    os.makedirs(OUT, exist_ok=True)
    urls = latin_woff2_urls()

    # Google serves the same variable file for every requested weight: one wght
    # axis spanning 200 to 800. So take one and declare the range in CSS rather
    # than shipping the identical file twice under different names.
    url = urls[min(urls)]
    raw = f"{OUT}/.tmp.woff2"
    with open(raw, "wb") as fh:
        fh.write(get(url))
    before = os.path.getsize(raw)

    dest = f"{OUT}/{FAMILY.lower()}-var.woff2"
    subprocess.run(
        [
            sys.executable, "-m", "fontTools.subset", raw,
            f"--text={GLYPHS}",
            "--flavor=woff2",
            "--layout-features=kern,liga,calt",
            f"--output-file={dest}",
        ],
        check=True,
    )
    os.remove(raw)
    print(f"  {dest}  {before // 1024}KB -> {os.path.getsize(dest) // 1024}KB")

    with open(f"{OUT}/OFL.txt", "wb") as fh:
        fh.write(get(LICENCE))
    print(f"  {OUT}/OFL.txt")

main()

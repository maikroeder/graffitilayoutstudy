""" Draw the header images of the demo site as SVG: a dark wall, spray paint in the colors of the Graffiti logo
and one motif per page; and the logo and the favicon. The JPGs, the logo and the favicon next to this script are
rendered from these SVGs, see README.md here.

Usage:
    python3 scripts/header_images/make_header_images.py [output folder]

The random parts use a fixed seed per image, so every run draws the same pictures.
"""
import base64
import math
import os
import random
import sys

WIDTH, HEIGHT = 2400, 800
# Lato Bold from interaktiv.basetiles (checkout under src/), the font of the headings of the demo site
LATO_BOLD = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'src',
                         'interaktiv.basetiles', 'src', 'interaktiv', 'basetiles', 'static', 'fonts', 'latin-ext',
                         'lato', 'lato-v17-latin-ext_latin-700.woff2')
BLACK = '#0D0D0B'
WALL = '#1A1E1D'
RED = '#DC2D19'
ORANGE = '#D9912C'
BLUE = '#216991'
BLUE_LIGHT = '#348AA9'
CREAM = '#DAD1B9'

DEFS = f"""
<defs>
  <filter id="wall" x="0" y="0" width="100%" height="100%">
    <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" seed="7" result="noise"/>
    <feColorMatrix in="noise" type="matrix"
      values="0 0 0 0 0.10  0 0 0 0 0.12  0 0 0 0 0.11  0 0 0 0.55 0" result="grain"/>
    <feBlend in="SourceGraphic" in2="grain" mode="multiply"/>
  </filter>
  <filter id="spray" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="38"/>
  </filter>
  <filter id="rough" x="-10%" y="-10%" width="120%" height="120%">
    <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="3" result="t"/>
    <feDisplacementMap in="SourceGraphic" in2="t" scale="10" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
  <linearGradient id="fade" x1="0" x2="1" y1="0" y2="0">
    <stop offset="0" stop-color="{BLACK}" stop-opacity="0.85"/>
    <stop offset="0.45" stop-color="{BLACK}" stop-opacity="0.35"/>
    <stop offset="1" stop-color="{BLACK}" stop-opacity="0"/>
  </linearGradient>
</defs>
"""


def bricks():
    """ A faint brick pattern on the wall """
    lines = []
    row_height, brick_width = 70, 180
    for row, y in enumerate(range(0, HEIGHT, row_height)):
        lines.append(f'<line x1="0" y1="{y}" x2="{WIDTH}" y2="{y}"/>')
        offset = 0 if row % 2 else brick_width // 2
        for x in range(offset, WIDTH, brick_width):
            lines.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + row_height}"/>')
    return f'<g stroke="#2A302E" stroke-width="3" opacity="0.7">{"".join(lines)}</g>'


def spray_clouds(rnd, centers):
    """ Soft clouds of spray paint around the motif """
    clouds = []
    for cx, cy, color, radius in centers:
        clouds.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="{color}" opacity="0.55" filter="url(#spray)"/>')
        for _ in range(3):
            dx, dy = rnd.uniform(-radius, radius), rnd.uniform(-radius / 2, radius / 2)
            r = radius * rnd.uniform(0.35, 0.6)
            clouds.append(f'<circle cx="{cx + dx:.0f}" cy="{cy + dy:.0f}" r="{r:.0f}" fill="{color}" '
                          f'opacity="0.4" filter="url(#spray)"/>')
    return ''.join(clouds)


def splatter(rnd, cx, cy, spread, colors, count=90):
    """ Small drops of paint, denser near the center """
    dots = []
    for _ in range(count):
        angle = rnd.uniform(0, 2 * math.pi)
        distance = spread * rnd.random() ** 1.7
        x, y = cx + math.cos(angle) * distance, cy + math.sin(angle) * distance * 0.7
        r = rnd.uniform(1.5, 7) * (1.4 - distance / spread)
        dots.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{max(r, 1.2):.1f}" fill="{rnd.choice(colors)}"/>')
    return ''.join(dots)


def stroke(d, color, width, extra=''):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round" {extra}/>')


def motif_spray_can():
    """ Start page: a spray can that sprays the three logo colors """
    return (
        '<g filter="url(#rough)" transform="translate(1660,150)">'
        f'<rect x="0" y="120" width="190" height="390" rx="34" fill="{BLUE}" stroke="{CREAM}" stroke-width="12"/>'
        f'<rect x="0" y="220" width="190" height="120" fill="{CREAM}"/>'
        f'<path d="M30,120 q65,-70 130,0" fill="{BLUE_LIGHT}" stroke="{CREAM}" stroke-width="12"/>'
        f'<rect x="72" y="35" width="46" height="50" rx="8" fill="{CREAM}"/>'
        f'<path d="M18,280 h150" stroke="{RED}" stroke-width="22"/>'
        '</g>'
        # the spray comes out of the nozzle on the left of the cap
        + stroke('M1728,205 C1560,170 1420,215 1270,165', RED, 26, 'filter="url(#rough)"')
        + stroke('M1728,212 C1550,235 1420,300 1240,285', ORANGE, 22, 'filter="url(#rough)"')
        + stroke('M1728,219 C1580,290 1460,380 1310,405', CREAM, 18, 'filter="url(#rough)"')
    )


def motif_editor():
    """ Entry page for authors: a pencil above a stack of documents """
    docs = ''.join(
        f'<g transform="translate({1500 + i * 70},{170 + i * 45}) rotate({-8 + i * 7})">'
        f'<rect width="300" height="380" rx="14" fill="{CREAM}" stroke="{BLACK}" stroke-width="8"/>'
        + ''.join(f'<rect x="40" y="{70 + j * 52}" width="{220 - (j % 3) * 40}" height="16" rx="8" fill="{c}"/>'
                  for j, c in enumerate([BLUE, '#8B8676', '#8B8676', RED, '#8B8676']))
        + '</g>'
        for i in range(3)
    )
    pencil = (
        '<g transform="translate(1440,560) rotate(-38)">'
        f'<rect x="0" y="-26" width="430" height="52" fill="{ORANGE}" stroke="{BLACK}" stroke-width="8"/>'
        f'<rect x="-48" y="-26" width="60" height="52" fill="{RED}" stroke="{BLACK}" stroke-width="8"/>'
        f'<path d="M430,-26 L510,0 L430,26 Z" fill="{CREAM}" stroke="{BLACK}" stroke-width="8"/>'
        f'<path d="M488,-8 L510,0 L488,8 Z" fill="{BLACK}"/>'
        '</g>'
    )
    return f'<g filter="url(#rough)">{docs}{pencil}</g>'


def motif_search():
    """ Search page: a magnifying glass over lines of text """
    text_lines = ''.join(
        f'<rect x="{1350 + (i % 2) * 40}" y="{200 + i * 70}" width="{620 - (i * 37) % 180}" height="22" rx="11" '
        f'fill="{CREAM}" opacity="0.35"/>' for i in range(7))
    glass = (
        f'<circle cx="1730" cy="370" r="175" fill="{BLUE}" fill-opacity="0.35" stroke="{CREAM}" stroke-width="34"/>'
        f'<rect x="1690" y="330" width="260" height="30" rx="15" fill="{RED}" transform="rotate(0)"/>'
        f'<path d="M1855,500 L2010,665" stroke="{ORANGE}" stroke-width="64" stroke-linecap="round"/>'
    )
    return f'{text_lines}<g filter="url(#rough)">{glass}</g>'


def motif_mcp():
    """ MCP demo documents: speech bubbles that are connected to a document """
    nodes = [(1450, 220), (1650, 560), (2050, 200), (1980, 600)]
    links = ''.join(stroke(f'M{x},{y} L1760,380', CREAM, 10, 'stroke-dasharray="4 22" opacity="0.8"')
                    for x, y in nodes)
    bubbles = (
        f'<path d="M1300,120 h300 a40,40 0 0 1 40,40 v120 a40,40 0 0 1 -40,40 h-200 l-60,60 v-60 h-40 '
        f'a40,40 0 0 1 -40,-40 v-120 a40,40 0 0 1 40,-40 z" fill="{BLUE}" stroke="{CREAM}" stroke-width="10"/>'
        f'<path d="M1920,470 h300 a40,40 0 0 1 40,40 v110 a40,40 0 0 1 -40,40 h-40 v60 l-60,-60 h-200 '
        f'a40,40 0 0 1 -40,-40 v-110 a40,40 0 0 1 40,-40 z" fill="{RED}" stroke="{CREAM}" stroke-width="10"/>'
        + ''.join(f'<circle cx="{1390 + i * 60}" cy="220" r="16" fill="{CREAM}"/>' for i in range(3))
        + ''.join(f'<rect x="1970" y="{525 + i * 40}" width="{200 - i * 50}" height="16" rx="8" fill="{CREAM}"/>'
                  for i in range(3))
        + f'<rect x="1685" y="270" width="150" height="200" rx="12" fill="{CREAM}" stroke="{BLACK}" stroke-width="8"/>'
        + ''.join(f'<rect x="1710" y="{305 + i * 34}" width="{100 - (i % 2) * 30}" height="12" rx="6" fill="{c}"/>'
                  for i, c in enumerate([BLUE, ORANGE, BLUE, RED]))
    )
    return f'{links}<g filter="url(#rough)">{bubbles}</g>'


def motif_webmirror():
    """ WebMirror: a website inside a frame inside the page """
    def window(x, y, w, h, color):
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{BLACK}" fill-opacity="0.4" '
                f'stroke="{color}" stroke-width="14"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="{h * 0.14:.0f}" rx="16" fill="{color}"/>'
                + ''.join(f'<circle cx="{x + 30 + i * 32}" cy="{y + h * 0.07:.0f}" r="9" fill="{BLACK}"/>'
                          for i in range(3)))
    return ('<g filter="url(#rough)">'
            + window(1340, 120, 820, 560, CREAM)
            + window(1470, 250, 560, 380, ORANGE)
            + window(1590, 360, 320, 230, BLUE_LIGHT)
            + f'<rect x="1640" y="480" width="200" height="18" rx="9" fill="{RED}"/>'
            + '</g>')


def motif_working_copies():
    """ Working copies: the original and its copy side by side, the changed lines marked """
    def sheet(x, y, rotate, marks):
        lines = ''.join(f'<rect x="40" y="{60 + i * 50}" width="{w}" height="16" rx="8" fill="{c}"/>'
                        for i, (w, c) in enumerate(marks))
        return (f'<g transform="translate({x},{y}) rotate({rotate})">'
                f'<rect width="300" height="400" rx="14" fill="{CREAM}" stroke="{BLACK}" stroke-width="8"/>{lines}</g>')
    grey = '#8B8676'
    original = [(220, grey), (180, grey), (200, RED), (150, grey), (210, grey), (170, grey)]
    copy = [(220, grey), (180, grey), (200, BLUE), (210, BLUE), (210, grey), (170, grey)]
    arrows = (stroke('M1735,300 C1780,260 1820,260 1860,300', ORANGE, 16)
              + '<path d="M1846,272 L1868,306 L1830,306 Z" fill="' + ORANGE + '"/>'
              + stroke('M1860,520 C1820,560 1780,560 1735,520', CREAM, 16)
              + '<path d="M1750,548 L1728,514 L1766,514 Z" fill="' + CREAM + '"/>')
    return (f'<g filter="url(#rough)">{sheet(1400, 200, -5, original)}{sheet(1880, 200, 5, copy)}'
            f'{arrows}</g>')


def motif_pdf_check():
    """ PDF check: a PDF document with a folded corner, next to it a stamp with a check mark """
    grey = '#8B8676'
    letters = (  # "PDF" drawn as lines, so the picture needs no font
        stroke('M50,96 V56 H64 a12,10 0 0 1 0,20 H50', CREAM, 8)
        + stroke('M90,96 V56 H98 a16,20 0 0 1 0,40 Z', CREAM, 8)
        + stroke('M132,96 V56 H152 M132,76 H148', CREAM, 8)
    )
    lines = ''.join(f'<rect x="40" y="{150 + i * 50}" width="{240 - (i * 47) % 90}" height="16" rx="8" fill="{grey}"/>'
                    for i in range(5))
    sheet = (
        '<g transform="translate(1500,170) rotate(-4)">'
        f'<path d="M14,0 H240 L320,80 V406 a14,14 0 0 1 -14,14 H14 a14,14 0 0 1 -14,-14 V14 a14,14 0 0 1 14,-14 Z" '
        f'fill="{CREAM}" stroke="{BLACK}" stroke-width="8"/>'
        f'<path d="M240,0 V80 H320" fill="#B9B19C" stroke="{BLACK}" stroke-width="8" stroke-linejoin="round"/>'
        f'<rect x="30" y="40" width="140" height="72" rx="10" fill="{RED}"/>{letters}{lines}'
        '</g>'
    )
    stamp = (f'<circle cx="1880" cy="520" r="115" fill="{BLUE}" stroke="{CREAM}" stroke-width="14"/>'
             + stroke('M1822,522 L1866,568 L1946,470', CREAM, 30))
    return f'<g filter="url(#rough)">{sheet}{stamp}</g>'


# the motif sits around this point; smaller headers (280px high) show only the middle of the image
MOTIF_CENTER = (1750, 400)
IMAGES = {
    # name: (seed, motif, spray clouds: (x, y, color, radius), scale of the motif)
    'header-home': (11, motif_spray_can, [(1250, 250, RED, 210), (1900, 520, BLUE, 260), (900, 620, ORANGE, 170)], 1),
    'header-entry-authors': (12, motif_editor, [(1500, 300, BLUE, 240), (2050, 600, RED, 200), (1000, 200, ORANGE, 150)], 0.7),
    'header-working-copies': (16, motif_working_copies, [(1550, 300, RED, 220), (2050, 500, BLUE, 240), (1100, 600, ORANGE, 160)], 0.7),
    'header-search': (13, motif_search, [(1750, 380, BLUE, 280), (1250, 600, ORANGE, 170), (2150, 150, RED, 160)], 0.7),
    'header-pdf-check': (17, motif_pdf_check, [(1550, 300, RED, 220), (2050, 560, BLUE, 240), (1050, 600, ORANGE, 160)], 0.7),
    'header-mcp-demo': (14, motif_mcp, [(1500, 250, BLUE, 230), (2000, 600, RED, 220), (1100, 500, ORANGE, 160)], 0.7),
    'header-webmirror': (15, motif_webmirror, [(1750, 400, ORANGE, 260), (1250, 200, BLUE, 200), (2200, 650, RED, 170)], 0.7),
}


def draw(seed, motif, clouds, scale):
    rnd = random.Random(seed)
    colors = [RED, ORANGE, BLUE_LIGHT, CREAM]
    parts = [
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{WALL}" filter="url(#wall)"/>',
        bricks(),
        spray_clouds(rnd, clouds),
        f'<g transform="translate({MOTIF_CENTER[0]} {MOTIF_CENTER[1]}) scale({scale}) '
        f'translate({-MOTIF_CENTER[0]} {-MOTIF_CENTER[1]})">{motif()}</g>',
        splatter(rnd, 1750, 400, 650, colors),
        splatter(rnd, 600, 250, 450, colors, count=40),
        # darker on the left, where title and text of the header sit
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="url(#fade)"/>',
    ]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}">{DEFS}{"".join(parts)}</svg>')


def mark():
    """ The mark of logo and favicon: the spray can of the front page, plain and big, on a dark tile,
    so that it works at 16 x 16 px. Drawn on 256 x 256 px. """
    return (
        f'<rect width="256" height="256" rx="48" fill="{BLACK}"/>'
        # the spray comes out of the nozzle on the left of the cap
        + stroke('M112,58 C80,44 52,52 24,40', RED, 18)
        + stroke('M112,64 C78,74 50,96 22,96', ORANGE, 16)
        + stroke('M112,70 C86,100 66,130 34,146', CREAM, 14)
        + f'<rect x="124" y="40" width="34" height="38" rx="7" fill="{CREAM}"/>'
        f'<path d="M104,100 q37,-36 74,0" fill="{BLUE_LIGHT}" stroke="{CREAM}" stroke-width="10"/>'
        f'<rect x="96" y="96" width="90" height="140" rx="18" fill="{BLUE}" stroke="{CREAM}" stroke-width="10"/>'
        f'<rect x="101" y="140" width="80" height="44" fill="{CREAM}"/>'
        f'<path d="M101,162 h80" stroke="{RED}" stroke-width="14"/>'
    )


def favicon():
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">{mark()}</svg>'


def logo():
    """ The logo: the mark and "Graffiti" in Lato Bold, the font of the headings of the site. The font is embedded,
    so that the logo looks the same without it being installed. """
    with open(LATO_BOLD, 'rb') as font_file:
        font = base64.b64encode(font_file.read()).decode()
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="300" viewBox="0 0 1000 300">'
        f'<style>@font-face {{ font-family: "Logo Lato"; src: url(data:font/woff2;base64,{font}); }}</style>'
        f'<g transform="scale({300 / 256})">{mark()}</g>'
        f'<text x="342" y="218" font-family="Logo Lato" font-size="200" letter-spacing="-2" fill="{BLACK}">'
        'Graffiti</text></svg>'
    )


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out, exist_ok=True)
    for name, (seed, motif, clouds, scale) in IMAGES.items():
        with open(os.path.join(out, name + '.svg'), 'w') as svg_file:
            svg_file.write(draw(seed, motif, clouds, scale))
        print('drawn:', name)
    for name, svg in [('favicon', favicon()), ('logo', logo())]:
        with open(os.path.join(out, name + '.svg'), 'w') as svg_file:
            svg_file.write(svg)
        print('drawn:', name)


if __name__ == '__main__':
    main()

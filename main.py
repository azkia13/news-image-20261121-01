#!/usr/bin/env python3
"""The Day in the World - front page for Saturday, 21 November 2026.

Draws a 1024x1024 newspaper front page deterministically with PIL and
writes it to /output/entry.png (or ./entry.png when /output is absent).

No network, no randomness, no timestamps: two runs produce byte-identical
PNG output. All news facts were verified against wire reporting (AP and
Reuters) for 21 November 2026; see README.md for sources.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# Palette: classic newsprint.
INK = (18, 18, 18)
PAPER = (250, 247, 238)
RULE = (18, 18, 18)
RED = (178, 34, 34)
BLUE = (28, 68, 128)
STEEL = (58, 84, 112)
GREY = (90, 90, 90)
WHITE = (255, 255, 255)
GREEN = (34, 110, 60)

OUT_PATH = "/output/entry.png"


def load_font(size, bold=False):
    """DejaVu fonts ship with PIL's test data on most systems; fall back."""
    candidates = []
    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


F_TITLE = load_font(60, bold=True)
F_DATE = load_font(19, bold=True)
F_KICKER = load_font(14, bold=True)
F_HEAD = load_font(28, bold=True)
F_HEAD2 = load_font(19, bold=True)
F_BODY = load_font(14)
F_SMALL = load_font(13)
F_SMALL_B = load_font(13, bold=True)
F_NUM = load_font(22, bold=True)
F_NUM_LBL = load_font(11, bold=True)
F_FOOT = load_font(11)


def wrap(draw, text, font, width):
    """Greedy word wrap returning a list of lines fitting `width` pixels."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, font, width, fill=INK, leading=None,
                 max_lines=None):
    x, y = xy
    if leading is None:
        leading = font.size + 5
    lines = wrap(draw, text, font, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def rule(draw, x0, y0, x1, y1, fill=RULE, width=1):
    draw.line([(x0, y0), (x1, y1)], fill=fill, width=width)


def draw_lead_art(draw, x, y, w, h):
    """Stylised illustration: NATO shield over a map-like Europe, drawn
    with PIL shapes only. A blue field, a gold compass star, shield
    emblem, and a red dashed line marking the breached border."""
    draw.rectangle([x, y, x + w, y + h], fill=STEEL)
    # faint latitude/longitude grid
    for i in range(1, 6):
        gx = x + w * i // 6
        draw.line([(gx, y), (gx, y + h)], fill=(74, 102, 132), width=1)
    for j in range(1, 3):
        gy = y + h * j // 3
        draw.line([(x, gy), (x + w, gy)], fill=(74, 102, 132), width=1)
    # landmass blobs (stylised Europe)
    draw.ellipse([x + 30, y + 25, x + 190, y + 80], fill=(96, 128, 92))
    draw.ellipse([x + 150, y + 55, x + 330, y + 115], fill=(96, 128, 92))
    draw.ellipse([x + 300, y + 15, x + 430, y + 65], fill=(112, 140, 100))
    draw.ellipse([x + 60, y + 85, x + 200, y + 130], fill=(112, 140, 100))
    # red dashed line: the breached border, top-right to centre
    for k in range(12):
        sx = x + w - 40 - k * 30
        sy = y + 12 + k * 9
        draw.line([(sx, sy), (sx - 20, sy + 6)], fill=RED, width=4)
    # NATO-style compass star (four-pointed) in gold
    cx, cy = x + w - 90, y + h - 48
    star = [
        (cx, cy - 38), (cx + 8, cy - 8), (cx + 38, cy), (cx + 8, cy + 8),
        (cx, cy + 38), (cx - 8, cy + 8), (cx - 38, cy), (cx - 8, cy - 8),
    ]
    draw.polygon(star, fill=(212, 175, 55), outline=(150, 118, 30))
    draw.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=WHITE)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=BLUE)
    # shield emblem bottom-left
    sx0, sy0 = x + 24, y + h - 78
    shield = [
        (sx0, sy0), (sx0 + 84, sy0), (sx0 + 84, sy0 + 48),
        (sx0 + 42, sy0 + 78), (sx0, sy0 + 48),
    ]
    draw.polygon(shield, fill=BLUE, outline=WHITE, width=3)
    draw.text((sx0 + 42, sy0 + 14), "NATO", font=F_SMALL_B, fill=WHITE,
              anchor="ma")
    draw.text((sx0 + 42, sy0 + 34), "POLAND", font=F_SMALL_B, fill=WHITE,
              anchor="ma")
    # caption bar
    draw.rectangle([x, y + h - 22, x + w, y + h], fill=INK)
    draw.text((x + 10, y + h - 19),
              "Illustration: the alliance closes ranks after the airspace breach.",
              font=F_SMALL, fill=WHITE)


def tile(draw, x, y, w, kicker, head, body, accent=RED):
    rule(draw, x, y, x + w, y, width=3, fill=accent)
    draw.text((x, y + 7), kicker, font=F_KICKER, fill=accent)
    ny = draw_wrapped(draw, (x, y + 26), head, F_HEAD2, w, leading=23,
                      max_lines=2)
    draw_wrapped(draw, (x, ny + 2), body, F_SMALL, w, leading=16,
                 max_lines=2)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 36  # margin
    inner = W - 2 * M

    # ---- Masthead ----
    d.text((W // 2, 12), "The Day in the World", font=F_TITLE, fill=INK,
           anchor="ma")
    d.text((W // 2, 80), "SATURDAY, 21 NOVEMBER 2026  |  ONE IMAGE, THE WHOLE DAY",
           font=F_DATE, fill=INK, anchor="ma")
    rule(d, M, 112, W - M, 112, width=3)
    rule(d, M, 117, W - M, 117, width=1)

    # ---- Lead story ----
    y = 128
    d.text((M, y), "NATO  |  EUROPE", font=F_KICKER, fill=RED)
    y = draw_wrapped(d, (M, y + 19),
                     "NATO vows to defend every inch of Poland after Russian missiles cross its border",
                     F_HEAD, inner, leading=33, max_lines=2)
    y += 4
    lead_text = ("NATO Secretary General Mark Rutte said in Warsaw on Saturday that "
                 "\"all allies stand in full solidarity with Poland\" and the alliance "
                 "will defend every inch of Polish territory, a day after Poland said "
                 "three Russian objects - probably two missiles and a drone - entered "
                 "its airspace during a huge overnight attack on Ukraine.")
    y = draw_wrapped(d, (M, y), lead_text, F_BODY, inner, leading=19,
                     max_lines=3)
    y += 8
    art_h = 120
    draw_lead_art(d, M, y, inner, art_h)
    y += art_h + 10
    rule(d, M, y, W - M, y, width=2)
    y += 10

    # ---- Seven story tiles: 2 columns x 4 rows (last tile full width) ----
    col_w = (inner - 24) // 2
    row_h = 108
    tiles = [
        ("UKRAINE  |  WAR", "Missiles kill boy and paramedic in Zelenskyy's hometown",
         "Two ballistic missiles hit central Kryvyi Rih on Friday night, killing a "
         "7-year-old boy and a 20-year-old paramedic and wounding 60."),
        ("MARKETS  |  ECONOMY", "AI sell-off drags S&P 500 into correction",
         "Wall Street fell 3.7% on Friday as doubts over AI spending spread; the "
         "Nasdaq dropped 5.3% and Asian markets fell further."),
        ("MEXICO  |  CRIME", "Mexico captures FBI most-wanted cartel boss",
         "Troops arrested Fausto Isidro Meza Flores, \"El Chapo Isidro\", in Sinaloa. "
         "Mexico said 11 died: four soldiers and seven attackers."),
        ("CLIMATE  |  COP31", "Climate talks run past deadline over fossil fuels",
         "COP31 in Antalya went into overtime after a draft deal failed even to "
         "mention fossil fuels. A third version was promised for Saturday."),
        ("HEALTH  |  USA", "US measles cases near 6,000 as outbreak worsens",
         "The CDC reported 5,838 measles cases as of 19 November, the worst US "
         "outbreak in decades. Virginia reported a child's death."),
        ("USA  |  POLITICS", "Trump vows 10% cap on credit-card rates",
         "President Trump said on Saturday he will work with the incoming "
         "Democratic Congress to cap card interest at 10%, from a median of 22%."),
        ("SCIENCE  |  HEALTH", "Special mosquitoes cut dengue by 69% in Brazil trial",
         "Children in neighbourhoods with Wolbachia-carrying mosquitoes had about "
         "69% fewer dengue and chikungunya infections in a four-year trial of "
         "more than 5,700 children in Belo Horizonte, researchers reported."),
    ]
    tx = [M, M + col_w + 24]
    ty = y
    for i, (kick, head, body) in enumerate(tiles):
        col = i % 2
        row = i // 2
        if i == 6:
            tile(d, M, ty + row * row_h, inner, kick, head, body, accent=GREEN)
        else:
            tile(d, tx[col], ty + row * row_h, col_w, kick, head, body)
    y = ty + 4 * row_h + 2

    # ---- By the numbers ----
    rule(d, M, y, W - M, y, width=2)
    y += 6
    d.text((M, y), "BY THE NUMBERS", font=F_KICKER, fill=BLUE)
    y += 20
    nums = [
        ("-3.7%", "S&P 500 fall on Friday, into correction"),
        ("5,838", "US measles cases reported by the CDC"),
        ("69%", "fewer dengue infections in Brazil trial"),
        ("148", "drones fired at Ukraine overnight"),
        ("$5m", "US reward for captured cartel boss"),
    ]
    seg = inner // 5
    for i, (num, lbl) in enumerate(nums):
        cx = M + seg * i + seg // 2
        d.text((cx, y), num, font=F_NUM, fill=BLUE, anchor="ma")
        draw_wrapped(d, (M + seg * i + 8, y + 28), lbl, F_NUM_LBL,
                     seg - 16, fill=GREY, leading=14, max_lines=2)
        if i < 4:
            rule(d, M + seg * (i + 1), y + 2, M + seg * (i + 1), y + 54,
                 fill=(200, 196, 184), width=1)
    y += 56
    rule(d, M, y, W - M, y, width=2)
    y += 8

    # ---- Also today strip ----
    d.text((M, y), "ALSO TODAY", font=F_KICKER, fill=RED)
    also = ("Denmark says it foiled a plot to kill rapper Kyivstoner and expelled a "
            "Russian military attache  |  FBI investigates a hack of its national "
            "crime database  |  At least 24 dead as a boat capsizes in Nigeria  |  "
            "France calls the latest EU budget proposal \"deeply disappointing\"")
    y = draw_wrapped(d, (M, y + 20), also, F_SMALL, inner, leading=17,
                     max_lines=2)
    y += 6
    rule(d, M, y, W - M, y, width=3)
    d.text((W // 2, y + 6),
           "Sources: Associated Press, Reuters  |  All facts reported on 21 November 2026",
           font=F_FOOT, fill=GREY, anchor="ma")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    img.save(OUT_PATH, format="PNG", optimize=True)
    print("wrote", OUT_PATH, os.path.getsize(OUT_PATH), "bytes")


if __name__ == "__main__":
    main()

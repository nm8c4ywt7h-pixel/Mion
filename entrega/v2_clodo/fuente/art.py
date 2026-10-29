"""Dessins vectoriels (style cartoon plat, contours épais) rendus en 2x puis réduits."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont

OL = (38, 32, 40)
WHITE = (255, 255, 255)
CREAM = (250, 234, 208)
PINK = (255, 150, 160)
YEL = (255, 210, 40)


def E(d, box, fill, w=10):
    d.ellipse(box, fill=fill, outline=OL if w else None, width=w)


def R(d, box, r, fill, w=10):
    d.rounded_rectangle(box, r, fill=fill, outline=OL if w else None, width=w)


def P(d, pts, fill, w=10):
    d.polygon(pts, fill=fill, outline=OL if w else None, width=w)


def line(d, pts, w=10, fill=OL):
    d.line(pts, fill=fill, width=w, joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=fill)


def limb(d, p0, p1, color, w=60):
    line(d, [p0, p1], w + 20, OL)
    line(d, [p0, p1], w, color)


def arc(d, box, a0, a1, w=10, fill=OL):
    d.arc(box, a0, a1, fill=fill, width=w)


def star(d, cx, cy, r, fill):
    pts = []
    for k in range(8):
        a = k * math.pi / 4
        rr = r if k % 2 == 0 else r * 0.32
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    P(d, pts, fill, 6)


def fin(im, s=0.5):
    return im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)


# ------------------------------------------------------------------ visages
def eyes(d, cx, cy, gap, r, look=(0, 0), kind="open"):
    for sx in (-1, 1):
        x = cx + sx * gap
        if kind == "closed":
            arc(d, (x - r, cy - r * 0.6, x + r, cy + r * 0.9), 200, 340, 12)
            continue
        E(d, (x - r, cy - r * 1.08, x + r, cy + r * 1.08), WHITE, 9)
        pr = r * 0.58
        px, py = x + look[0] * r * 0.38, cy + look[1] * r * 0.38
        E(d, (px - pr, py - pr, px + pr, py + pr), OL, 0)
        hr = pr * 0.33
        E(d, (px + pr * 0.15, py - pr * 0.6, px + pr * 0.15 + hr * 2, py - pr * 0.6 + hr * 2), WHITE, 0)


def brows(d, cx, cy, gap, kind):
    for sx in (-1, 1):
        x = cx + sx * gap
        if kind == "worried":
            line(d, [(x - sx * 45, cy - 20), (x + sx * 40, cy + 10)][::sx], 12)
        elif kind == "angry":
            line(d, [(x - sx * 40, cy + 8), (x + sx * 40, cy - 18)][::sx], 15)
        elif kind == "up":
            arc(d, (x - 40, cy - 40, x + 40, cy + 10), 200, 340, 12)


# ------------------------------------------------------------------ humains
PEOPLE = {
    "torchon": dict(skin=(196, 132, 96), hair="bun", hc=(40, 30, 35), top=(245, 190, 50), bottom=(70, 60, 90),
                    apron=True, earrings=True),
    "louise": dict(skin=(232, 180, 140), hair="pony", hc=(120, 70, 40), top=(40, 170, 160), bottom=(50, 60, 110)),
    "maminova": dict(skin=(240, 200, 170), hair="granny", hc=(215, 215, 225), top=(215, 70, 125), bottom=(120, 40, 80),
                     glasses=True, crown=True, pearls=True),
    "voldemort": dict(skin=(214, 160, 120), hair="bald", hc=(90, 70, 60), top=(235, 110, 55), bottom=(55, 60, 70),
                      belly=True, mustache=True, floral=True),
    "courgette": dict(skin=(232, 180, 140), hair="spiky", hc=(40, 30, 30), top=(120, 190, 60), bottom=(40, 40, 55),
                      cap=True, small=True),
    "horowitz": dict(skin=(240, 205, 175), hair="long", hc=(110, 60, 35), top=(250, 250, 250), bottom=(60, 70, 90),
                     glasses=True, labcoat=True),
    "owner": dict(skin=(150, 100, 70), hair="short", hc=(30, 25, 25), top=(210, 50, 60), bottom=(50, 55, 75)),
}


def person(name, expr="neutral", arms="down", look=(0, 0), prop=None):
    c = PEOPLE[name]
    im = Image.new("RGBA", (800, 1300))
    d = ImageDraw.Draw(im)
    cx = 400
    skin, top = c["skin"], c["top"]
    tw = 165 if c.get("belly") else 125
    # jambes + chaussures
    R(d, (cx - 72, 990, cx - 14, 1215), 22, c["bottom"])
    R(d, (cx + 14, 990, cx + 72, 1215), 22, c["bottom"])
    E(d, (cx - 110, 1185, cx - 5, 1250), (245, 245, 245))
    E(d, (cx + 5, 1185, cx + 110, 1250), (245, 245, 245))
    # cheveux arrière
    hc = c["hc"]
    if c["hair"] == "long":
        R(d, (cx - 185, 300, cx + 185, 760), 120, hc)
    if c["hair"] == "pony":
        E(d, (cx + 120, 300, cx + 250, 560), hc)
    # bras derrière / devant selon pose
    sh_y = 690
    lsh, rsh = (cx - tw + 15, sh_y), (cx + tw - 15, sh_y)
    hands = []

    def arm(p0, p1):
        limb(d, p0, p1, top, 62)
        hands.append(p1)

    if arms in ("down", "phone", "bowl", "eat", "wipe", "point"):
        arm(lsh, (cx - tw - 25, 930))
    if arms == "up":
        arm(lsh, (cx - tw - 110, 470))
        arm(rsh, (cx + tw + 110, 470))
    # torse
    R(d, (cx - tw, 640, cx + tw, 1030), 90, top)
    if c.get("labcoat"):
        P(d, [(cx - 40, 645), (cx + 40, 645), (cx, 760)], (150, 90, 200), 8)
        line(d, [(cx, 760), (cx, 1025)], 8)
        R(d, (cx + 40, 860, cx + 105, 900), 8, (235, 235, 240), 6)
    if c.get("apron"):
        R(d, (cx - 90, 720, cx + 90, 1025), 30, WHITE)
        R(d, (cx - 40, 850, cx + 40, 905), 10, (240, 120, 120), 6)
    if c.get("floral"):
        for fx, fy in ((-90, 760), (60, 720), (-20, 880), (90, 940), (-110, 960), (110, 820)):
            for k in range(5):
                a = k * 2 * math.pi / 5
                E(d, (cx + fx + 18 * math.cos(a) - 12, fy + 18 * math.sin(a) - 12,
                      cx + fx + 18 * math.cos(a) + 12, fy + 18 * math.sin(a) + 12), (255, 230, 120), 0)
            E(d, (cx + fx - 9, fy - 9, cx + fx + 9, fy + 9), (255, 255, 255), 0)
        for k in range(4):
            E(d, (cx - 8, 700 + k * 80, cx + 8, 716 + k * 80), (250, 240, 220), 4)
    if c.get("pearls"):
        for k in range(11):
            a = math.pi * (0.15 + 0.7 * k / 10)
            x, y = cx + 95 * math.cos(a), 640 + 55 * math.sin(a)
            E(d, (x - 13, y - 13, x + 13, y + 13), (250, 245, 235), 5)
    # bras devant
    if arms == "down":
        arm(rsh, (cx + tw + 25, 930))
    elif arms == "point":
        arm(rsh, (cx + tw + 230, 700))
    elif arms in ("phone", "bowl", "eat"):
        arm(rsh, (cx + 30, 830) if arms != "eat" else (cx + 60, 560))
    elif arms == "wipe":
        arm(rsh, (cx + tw + 190, 1000))
    for x, y in hands:
        E(d, (x - 38, y - 38, x + 38, y + 38), skin, 9)
    if arms == "phone":
        R(d, (cx - 5, 720, cx + 85, 880), 16, (60, 120, 230), 9)
    if arms == "bowl":
        P(d, [(cx - 150, 790), (cx + 150, 790), (cx + 100, 900), (cx - 100, 900)], (250, 250, 250), 9)
        for k in range(6):
            E(d, (cx - 140 + k * 45, 745, cx - 80 + k * 45, 805), (110 + k * 10, 190, 80), 7)
        line(d, [(cx - 150, 790), (cx + 150, 790)], 10)
    if arms == "eat":
        drum(d, cx + 60, 520, 0.8, -40)
    # tête
    hy = 420
    E(d, (cx - 200, hy - 25, cx - 140, hy + 55), skin, 9)
    E(d, (cx + 140, hy - 25, cx + 200, hy + 55), skin, 9)
    if c.get("earrings"):
        for sx in (-1, 1):
            arc(d, (cx + sx * 172 - 22, hy + 45, cx + sx * 172 + 22, hy + 95), 0, 360, 9, (240, 180, 30))
    E(d, (cx - 175, hy - 175, cx + 175, hy + 165), skin)
    # cheveux avant
    h = c["hair"]
    if h in ("bun", "pony", "long", "short", "spiky"):
        d.chord((cx - 178, hy - 180, cx + 178, hy + 90), 180, 360, fill=hc, outline=OL, width=10)
    if h == "bun":
        E(d, (cx - 75, hy - 290, cx + 75, hy - 150), hc)
        R(d, (cx - 60, hy - 185, cx + 60, hy - 160), 10, (230, 60, 80), 7)
    if h == "spiky":
        P(d, [(cx - 170, hy - 60), (cx - 140, hy - 230), (cx - 80, hy - 150), (cx - 30, hy - 260), (cx + 20, hy - 160),
              (cx + 80, hy - 250), (cx + 110, hy - 150), (cx + 175, hy - 210), (cx + 175, hy - 60)], hc)
    if h == "granny":
        for k in range(7):
            x = cx - 165 + k * 55
            E(d, (x - 50, hy - 205, x + 50, hy - 95), hc, 9)
        E(d, (cx - 70, hy - 300, cx + 70, hy - 180), hc)
    if h == "bald":
        E(d, (cx - 185, hy - 40, cx - 120, hy + 50), hc, 8)
        E(d, (cx + 120, hy - 40, cx + 185, hy + 50), hc, 8)
        arc(d, (cx - 20, hy - 230, cx + 50, hy - 150), 180, 300, 9)
    if c.get("cap"):
        d.chord((cx - 180, hy - 200, cx + 180, hy + 40), 180, 360, fill=(220, 50, 50), outline=OL, width=10)
        R(d, (cx - 230, hy - 90, cx - 60, hy - 55), 15, (220, 50, 50))
    # visage
    ey = hy + 5
    kind = "open"
    eyes(d, cx, ey, 68, 48, look, kind)
    if expr == "angry":
        brows(d, cx, ey - 70, 68, "angry")
    elif expr in ("shock", "sing"):
        brows(d, cx, ey - 70, 68, "up")
    elif expr == "worried":
        brows(d, cx, ey - 70, 68, "worried")
    if c.get("glasses"):
        for sx in (-1, 1):
            arc(d, (cx + sx * 68 - 62, ey - 62, cx + sx * 68 + 62, ey + 62), 0, 360, 11, (60, 60, 70))
        line(d, [(cx - 8, ey - 10), (cx + 8, ey - 10)], 10, (60, 60, 70))
    E(d, (cx - 150, hy + 70, cx - 95, hy + 100), (250, 150, 150), 0)
    E(d, (cx + 95, hy + 70, cx + 150, hy + 100), (250, 150, 150), 0)
    arc(d, (cx - 22, hy + 40, cx + 22, hy + 75), 20, 160, 8)
    my = hy + 105
    if expr in ("angry", "shout"):
        E(d, (cx - 62, my - 10, cx + 62, my + 80), (150, 30, 50), 10)
        d.chord((cx - 40, my + 35, cx + 40, my + 85), 180, 360, fill=PINK)
        R(d, (cx - 40, my - 4, cx + 40, my + 14), 6, WHITE, 0)
    elif expr == "sing":
        d.chord((cx - 55, my - 25, cx + 55, my + 70), 0, 180, fill=(150, 30, 50), outline=OL, width=10)
    elif expr == "shock":
        E(d, (cx - 32, my - 5, cx + 32, my + 65), (150, 30, 50), 10)
    elif expr == "grin":
        d.chord((cx - 75, my - 40, cx + 75, my + 55), 0, 180, fill=WHITE, outline=OL, width=10)
    elif expr == "worried":
        arc(d, (cx - 40, my + 5, cx + 40, my + 45), 200, 340, 10)
    else:
        arc(d, (cx - 50, my - 40, cx + 50, my + 25), 30, 150, 10)
    if c.get("mustache"):
        for sx in (-1, 1):
            E(d, (cx + (sx < 0) * -110 + (sx > 0) * 0, my - 30, cx + (sx < 0) * 0 + (sx > 0) * 110, my + 15), hc, 8)
    if c.get("crown"):
        P(d, [(cx - 90, hy - 255), (cx - 90, hy - 345), (cx - 45, hy - 295), (cx, hy - 360), (cx + 45, hy - 295),
              (cx + 90, hy - 345), (cx + 90, hy - 255)], YEL)
        for x in (-45, 0, 45):
            E(d, (cx + x - 12, hy - 290, cx + x + 12, hy - 266), (230, 60, 90), 5)
    return fin(im.crop(im.getbbox()))


# ------------------------------------------------------------------ chiens
DOGS = {
    "clodo": dict(body=(214, 140, 72), ear=(140, 80, 42), patch=(150, 92, 48), collar=(225, 45, 55), tuft=True),
    "negro": dict(body=(60, 58, 70), ear=(40, 38, 48), patch=None, collar=(240, 170, 40), tuft=False, chest=(90, 88, 100)),
    "blanco": dict(body=(245, 245, 240), ear=(220, 205, 180), patch=None, collar=(60, 140, 230), tuft=False),
}


def dog(name="clodo", expr="happy", halo=False):
    c = DOGS[name]
    im = Image.new("RGBA", (900, 1000))
    d = ImageDraw.Draw(im)
    b, cream = c["body"], c.get("chest", CREAM)
    # queue
    tail = [(600, 860), (690, 820), (740, 720), (735, 640)] if expr != "guilty" else [(580, 880), (650, 905), (720, 900)]
    line(d, tail, 64, OL)
    line(d, tail, 44, b)
    # corps
    E(d, (250, 520, 610, 930), b)
    E(d, (190, 760, 340, 940), b)
    E(d, (520, 760, 670, 940), b)
    E(d, (330, 560, 530, 880), cream, 0)
    R(d, (335, 700, 400, 925), 28, b)
    R(d, (460, 700, 525, 925), 28, b)
    E(d, (305, 900, 415, 955), cream)
    E(d, (445, 900, 555, 955), cream)
    # tête
    hx, hy = 430, 360 if expr != "guilty" else 395
    R(d, (300, hy + 150, 560, hy + 195), 20, c["collar"])
    E(d, (408, hy + 180, 452, hy + 224), YEL, 8)
    if expr == "guilty":
        P(d, [(hx - 160, hy - 60), (hx - 250, hy + 60), (hx - 210, hy + 170), (hx - 130, hy + 60)], c["ear"])
        P(d, [(hx + 160, hy - 60), (hx + 250, hy + 60), (hx + 210, hy + 170), (hx + 130, hy + 60)], c["ear"])
    else:
        E(d, (hx - 265, hy - 130, hx - 125, hy + 170), c["ear"])
        E(d, (hx + 125, hy - 130, hx + 265, hy + 170), c["ear"])
    if c["tuft"]:
        P(d, [(hx - 70, hy - 175), (hx - 55, hy - 255), (hx - 20, hy - 190), (hx, hy - 275), (hx + 25, hy - 190),
              (hx + 60, hy - 250), (hx + 70, hy - 175)], b)
    d.ellipse((hx - 205, hy - 200, hx + 205, hy + 190), fill=b)
    if c["patch"]:
        d.chord((hx + 20, hy - 190, hx + 205, hy + 60), 250, 470, fill=c["patch"])
        E(d, (hx + 25, hy - 150, hx + 175, hy + 20), c["patch"], 0)
    d.ellipse((hx - 205, hy - 200, hx + 205, hy + 190), outline=OL, width=11)
    E(d, (hx - 115, hy + 10, hx + 115, hy + 165), cream, 0)
    E(d, (hx - 165, hy + 30, hx - 105, hy + 70), (250, 150, 150), 0)
    E(d, (hx + 105, hy + 30, hx + 165, hy + 70), (250, 150, 150), 0)
    # yeux
    if expr == "angel":
        eyes(d, hx, hy - 40, 85, 52, kind="closed")
    elif expr == "guilty":
        eyes(d, hx, hy - 30, 85, 52, look=(-1, 0.7))
        brows(d, hx, hy - 105, 85, "worried")
    elif expr == "sleep":
        eyes(d, hx, hy - 40, 85, 52, kind="closed")
    else:
        eyes(d, hx, hy - 40, 85, 54, look=(0, 0.1))
    # truffe + bouche
    P(d, [(hx - 42, hy + 30), (hx + 42, hy + 30), (hx, hy + 75)], OL, 8)
    E(d, (hx - 46, hy + 15, hx + 46, hy + 60), OL, 0)
    if expr == "happy":
        R(d, (hx - 28, hy + 100, hx + 28, hy + 175), 26, (240, 100, 120))
        line(d, [(hx, hy + 140), (hx, hy + 165)], 6, (190, 60, 80))
    if expr in ("happy", "angel", "neutral", "sleep"):
        arc(d, (hx - 70, hy + 50, hx, hy + 115), 20, 160, 10)
        arc(d, (hx, hy + 50, hx + 70, hy + 115), 20, 160, 10)
    if expr == "guilty":
        line(d, [(hx - 50, hy + 125), (hx - 25, hy + 110), (hx, hy + 125), (hx + 25, hy + 110), (hx + 50, hy + 125)], 10)
        E(d, (hx + 165, hy - 120, hx + 205, hy - 60), (140, 200, 255), 7)
    if halo:
        arc(d, (hx - 130, hy - 330, hx + 130, hy - 250), 0, 360, 26, OL)
        arc(d, (hx - 125, hy - 326, hx + 125, hy - 254), 0, 360, 16, YEL)
    return fin(im.crop(im.getbbox()))


# ------------------------------------------------------------------ accessoires
def drum(d, x, y, s=1.0, rot=0):
    a = math.radians(rot)
    def T(px, py):
        return (x + (px * math.cos(a) - py * math.sin(a)) * s, y + (px * math.sin(a) + py * math.cos(a)) * s)
    bx, by = T(0, 120)
    E(d, (bx - 22 * s, by - 22 * s, bx + 22 * s, by + 22 * s), WHITE, int(8 * s))
    bx2, by2 = T(28, 120)
    E(d, (bx2 - 22 * s, by2 - 22 * s, bx2 + 22 * s, by2 + 22 * s), WHITE, int(8 * s))
    limb(d, T(14, 40), T(14, 110), (250, 245, 230), int(26 * s))
    cx, cy = T(14, 0)
    E(d, (cx - 55 * s, cy - 70 * s, cx + 55 * s, cy + 60 * s), (205, 120, 50), int(9 * s))


@lru_cache(None)
def chicken(legs=True):
    im = Image.new("RGBA", (1100, 700))
    d = ImageDraw.Draw(im)
    E(d, (60, 380, 1040, 640), WHITE)
    E(d, (130, 420, 970, 600), (240, 240, 245), 0)
    for x, col in ((200, (90, 170, 70)), (290, (230, 70, 60)), (810, (90, 170, 70)), (880, (230, 70, 60))):
        E(d, (x - 30, 470, x + 30, 530), col, 7)
    if legs:
        drum(d, 300, 300, 1.15, 50)
        drum(d, 800, 300, 1.15, -50)
    E(d, (290, 160, 810, 540), (220, 140, 60))
    E(d, (360, 200, 620, 340), (240, 175, 90), 0)
    return fin(im.crop(im.getbbox()))


@lru_cache(None)
def cake():
    im = Image.new("RGBA", (600, 600))
    d = ImageDraw.Draw(im)
    R(d, (80, 300, 520, 560), 30, (250, 180, 200))
    R(d, (140, 170, 460, 310), 30, (255, 220, 230))
    for k in range(3):
        x = 220 + k * 80
        R(d, (x - 12, 70, x + 12, 175), 6, (120, 180, 255), 7)
        P(d, [(x, 20), (x + 18, 60), (x, 75), (x - 18, 60)], (255, 190, 40), 6)
    for x in range(110, 500, 60):
        E(d, (x, 290, x + 40, 330), WHITE, 0)
    return fin(im.crop(im.getbbox()))


@lru_cache(None)
def bubble(kind):
    im = Image.new("RGBA", (800, 700))
    d = ImageDraw.Draw(im)
    for box in ((120, 100, 460, 420), (300, 60, 680, 400), (180, 230, 620, 540)):
        E(d, box, WHITE)
    for box in ((120, 100, 460, 420), (300, 60, 680, 400), (180, 230, 620, 540)):
        E(d, (box[0] + 10, box[1] + 10, box[2] - 10, box[3] - 10), WHITE, 0)
    E(d, (90, 520, 160, 590), WHITE, 9)
    E(d, (40, 610, 80, 650), WHITE, 8)
    if kind == "drum":
        drum(d, 380, 220, 1.3, 30)
    elif kind == "ball":
        E(d, (290, 170, 490, 370), (210, 230, 60))
        arc(d, (230, 180, 380, 360), 300, 60, 10, WHITE)
        arc(d, (400, 180, 550, 360), 120, 240, 10, WHITE)
    elif kind == "bone":
        bone = treat()
        im.paste(bone.resize((300, 150)), (240, 230), bone.resize((300, 150)))
    elif kind == "question":
        f = ImageFont.truetype(FONT_PATH, 260)
        f.set_variation_by_name("Black")
        d.text((400, 300), "?", font=f, fill=OL, anchor="mm")
    return fin(im.crop(im.getbbox()))


@lru_cache(None)
def treat():
    im = Image.new("RGBA", (400, 200))
    d = ImageDraw.Draw(im)
    for x in (60, 340):
        E(d, (x - 50, 20, x + 50, 100), (200, 140, 80))
        E(d, (x - 50, 90, x + 50, 170), (200, 140, 80))
    R(d, (60, 50, 340, 140), 30, (200, 140, 80))
    d.rectangle((60, 58, 340, 132), fill=(200, 140, 80))
    return fin(im.crop(im.getbbox()))


def clock(angle):
    im = Image.new("RGBA", (700, 700))
    d = ImageDraw.Draw(im)
    E(d, (30, 30, 670, 670), WHITE, 18)
    for k in range(12):
        a = k * math.pi / 6
        line(d, [(350 + 270 * math.cos(a), 350 + 270 * math.sin(a)), (350 + 300 * math.cos(a), 350 + 300 * math.sin(a))], 14)
    a = math.radians(angle - 90)
    line(d, [(350, 350), (350 + 230 * math.cos(a), 350 + 230 * math.sin(a))], 16)
    a2 = math.radians(angle / 12 - 90)
    line(d, [(350, 350), (350 + 150 * math.cos(a2), 350 + 150 * math.sin(a2))], 22)
    a3 = math.radians(angle * 4 - 90)
    line(d, [(350, 350), (350 + 250 * math.cos(a3), 350 + 250 * math.sin(a3))], 8, (230, 50, 60))
    E(d, (330, 330, 370, 370), OL, 0)
    return fin(im)


@lru_cache(None)
def eye_big():
    im = Image.new("RGBA", (1600, 1600))
    d = ImageDraw.Draw(im)
    E(d, (100, 100, 1500, 1500), WHITE, 22)
    E(d, (430, 430, 1170, 1170), (130, 80, 45), 16)
    E(d, (560, 560, 1040, 1040), (40, 25, 20), 0)
    E(d, (900, 540, 1020, 660), WHITE, 0)
    line(d, [(560, 120), (1200, -40)], 40)
    dg = dog("clodo", "guilty")
    dg = dg.resize((int(dg.width * 0.55), int(dg.height * 0.55)), Image.LANCZOS)
    im.paste(dg, (800 - dg.width // 2, 820 - dg.height // 2), dg)
    return fin(im)


@lru_cache(None)
def clapper():
    im = Image.new("RGBA", (500, 420))
    d = ImageDraw.Draw(im)
    R(d, (40, 150, 460, 400), 14, (40, 40, 45))
    P(d, [(40, 150), (440, 40), (460, 110), (60, 220)], (40, 40, 45))
    for k in range(5):
        x = 80 + k * 80
        P(d, [(x, 140 - k * 22 + 10), (x + 40, 130 - k * 22), (x + 60, 190 - k * 22), (x + 20, 200 - k * 22)], WHITE, 0)
    return fin(im.crop(im.getbbox()))


def meter(level):
    im = Image.new("RGBA", (220, 900))
    d = ImageDraw.Draw(im)
    R(d, (60, 20, 160, 760), 50, WHITE, 12)
    E(d, (20, 680, 200, 860), (230, 50, 60), 12)
    top = 740 - 680 * level
    R(d, (82, top, 138, 760), 28, (230, 50, 60), 0)
    return fin(im)


def phone_frame(content, w, h):
    """Téléphone avec écran de vidéo en cours d'enregistrement."""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    R(d, (0, 0, w - 1, h - 1), 50, OL, 0)
    scr = content.resize((w - 40, h - 40), Image.LANCZOS)
    mask = Image.new("L", scr.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, scr.width - 1, scr.height - 1), 34, fill=255)
    im.paste(scr, (20, 20), mask)
    R(d, (w // 2 - 70, 30, w // 2 + 70, 58), 14, OL, 0)
    E(d, (60, 80, 100, 120), (240, 40, 50), 0)
    for (x, y, sx, sy) in ((50, 150, 1, 1), (w - 50, 150, -1, 1), (50, h - 60, 1, -1), (w - 50, h - 60, -1, -1)):
        line(d, [(x, y + sy * 60), (x, y), (x + sx * 60, y)], 9, WHITE)
    return im


FONT_PATH = None

"""Primitives de dessin "flat" : personnages, chien, décors. Coordonnées en base 1080x1920."""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
K = 2  # supersampling
OUT = (43, 34, 51)
LW = 7
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

SKIN = [(246, 205, 170), (196, 140, 100), (130, 85, 60)]
TERRACOTTA = (214, 120, 90)
MOUTARDE = (232, 182, 60)
SAUGE = (160, 190, 160)
CREME = (250, 238, 220)
NUIT = (38, 44, 74)


class Canvas:
    def __init__(self, bg):
        self.img = Image.new("RGB", (W * K, H * K), bg)
        self.d = ImageDraw.Draw(self.img)

    def s(self, *v):
        return [int(x * K) for x in v]

    def rect(self, x0, y0, x1, y1, fill, r=0, outline=OUT, w=LW):
        self.d.rounded_rectangle(self.s(x0, y0, x1, y1), radius=r * K, fill=fill,
                                 outline=outline, width=(w * K if outline else 0))

    def ell(self, cx, cy, rx, ry, fill, outline=OUT, w=LW):
        self.d.ellipse(self.s(cx - rx, cy - ry, cx + rx, cy + ry), fill=fill,
                       outline=outline, width=(w * K if outline else 0))

    def line(self, pts, fill=OUT, w=LW):
        self.d.line([tuple(self.s(*p)) for p in pts], fill=fill, width=w * K, joint="curve")
        for p in (pts[0], pts[-1]):
            self.d.ellipse(self.s(p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2), fill=fill)

    def poly(self, pts, fill, outline=OUT, w=LW):
        self.d.polygon([tuple(self.s(*p)) for p in pts], fill=fill,
                       outline=outline, width=(w * K if outline else 0))

    def arc(self, cx, cy, rx, ry, a0, a1, fill=OUT, w=LW):
        self.d.arc(self.s(cx - rx, cy - ry, cx + rx, cy + ry), a0, a1, fill=fill, width=w * K)

    def text(self, cx, cy, txt, size, fill=(255, 255, 255), stroke=OUT, sw=10):
        f = ImageFont.truetype(FONT, size * K)
        self.d.text((cx * K, cy * K), txt, font=f, fill=fill, anchor="mm",
                    stroke_width=sw * K, stroke_fill=stroke)

    def final(self):
        return self.img.resize((W, H), Image.LANCZOS)


# ---------- éléments graphiques ----------

def rays(c, color_a, color_b, cx=540, cy=900):
    for i in range(24):
        a0, a1 = math.radians(i * 15), math.radians(i * 15 + 7.5)
        R = 2500
        c.poly([(cx, cy), (cx + R * math.cos(a0), cy + R * math.sin(a0)),
                (cx + R * math.cos(a1), cy + R * math.sin(a1))], color_b, outline=None)


def halo(c, cx, cy, r, color):
    c.ell(cx, cy, r, r, color, outline=None)


def heart(c, cx, cy, s, fill=(235, 80, 100)):
    c.ell(cx - s * 0.5, cy - s * 0.2, s * 0.55, s * 0.55, fill)
    c.ell(cx + s * 0.5, cy - s * 0.2, s * 0.55, s * 0.55, fill)
    c.poly([(cx - s * 1.03, cy - s * 0.05), (cx + s * 1.03, cy - s * 0.05), (cx, cy + s * 1.1)], fill)
    c.ell(cx - s * 0.5, cy - s * 0.2, s * 0.5, s * 0.5, fill, outline=None)
    c.ell(cx + s * 0.5, cy - s * 0.2, s * 0.5, s * 0.5, fill, outline=None)
    c.poly([(cx - s * 0.95, cy - s * 0.05), (cx + s * 0.95, cy - s * 0.05), (cx, cy + s * 1.0)], fill, outline=None)


def big_x(c, cx, cy, s, fill=(230, 70, 70)):
    for a, b in (((-1, -1), (1, 1)), ((-1, 1), (1, -1))):
        c.line([(cx + a[0] * s, cy + a[1] * s), (cx + b[0] * s, cy + b[1] * s)], OUT, int(s * 0.42))
        c.line([(cx + a[0] * s, cy + a[1] * s), (cx + b[0] * s, cy + b[1] * s)], fill, int(s * 0.3))


def check(c, cx, cy, s, fill=(80, 190, 110)):
    pts = [(cx - s, cy), (cx - s * 0.3, cy + s * 0.7), (cx + s, cy - s * 0.8)]
    c.line(pts, OUT, int(s * 0.42))
    c.line(pts, fill, int(s * 0.3))


def bolt(c, cx, cy, s, fill=(250, 210, 60)):
    c.poly([(cx + s * 0.2, cy - s), (cx - s * 0.5, cy + s * 0.1), (cx - s * 0.05, cy + s * 0.1),
            (cx - s * 0.25, cy + s), (cx + s * 0.5, cy - s * 0.15), (cx + s * 0.05, cy - s * 0.15)], fill)


def waves(c, cx, cy, s, color=(150, 110, 210), n=3):
    for i in range(n):
        x = cx + (i - (n - 1) / 2) * s * 0.6
        pts = [(x + math.sin(t / 3) * s * 0.12, cy - s * 0.5 + t * s / 12) for t in range(13)]
        c.line(pts, color, 9)


def tear(c, cx, cy, s, fill=(110, 180, 240)):
    c.poly([(cx, cy - s), (cx - s * 0.55, cy + s * 0.2), (cx + s * 0.55, cy + s * 0.2)], fill, outline=None)
    c.ell(cx, cy + s * 0.3, s * 0.58, s * 0.55, fill, outline=None)


def zzz(c, x, y, s=60):
    for i, k in enumerate((1, 0.75, 0.55)):
        c.text(x + i * s * 0.8, y - i * s * 0.9, "z", int(s * k), fill=(255, 255, 255), sw=5)


def window_night(c, x, y, w, h):
    c.rect(x, y, x + w, y + h, NUIT, r=10)
    c.ell(x + w * 0.72, y + h * 0.28, w * 0.12, w * 0.12, (250, 240, 190), outline=None)
    for i in range(4):  # immeubles madrilènes
        bx = x + 15 + i * (w - 30) / 4
        bh = h * (0.35 + 0.12 * (i % 2))
        c.rect(bx, y + h - bh - 8, bx + (w - 30) / 4 - 8, y + h - 8, (70, 74, 110), outline=None)
        for j in range(3):
            c.rect(bx + 12, y + h - bh + 12 + j * 40, bx + 30, y + h - bh + 32 + j * 40,
                   (250, 220, 120), outline=None)
    c.rect(x, y, x + w, y + h, None, r=10)
    c.line([(x + w / 2, y), (x + w / 2, y + h)], OUT, 6)


def window_day(c, x, y, w, h):
    c.rect(x, y, x + w, y + h, (170, 215, 240), r=10)
    c.ell(x + w * 0.3, y + h * 0.35, w * 0.16, h * 0.1, (255, 255, 255), outline=None)
    c.ell(x + w * 0.45, y + h * 0.32, w * 0.14, h * 0.09, (255, 255, 255), outline=None)
    c.rect(x, y, x + w, y + h, None, r=10)
    c.line([(x + w / 2, y), (x + w / 2, y + h)], OUT, 6)
    c.line([(x, y + h / 2), (x + w, y + h / 2)], OUT, 6)


def room(c, wall, floor, floor_y=1300):
    c.rect(-20, -20, W + 20, floor_y, wall, outline=None)
    c.rect(-20, floor_y, W + 20, H + 20, floor, outline=None)
    c.line([(-20, floor_y), (W + 20, floor_y)], OUT, 6)


def plant(c, x, y):
    c.rect(x - 45, y - 90, x + 45, y, TERRACOTTA, r=8)
    for a in (-40, -15, 15, 40):
        c.ell(x + a * 1.4, y - 150 - abs(a), 28, 60, (110, 160, 110))


def clock(c, cx, cy, r, hour=3):
    c.ell(cx, cy, r, r, (255, 255, 255))
    for i in range(12):
        a = math.radians(i * 30)
        c.line([(cx + math.sin(a) * r * 0.78, cy - math.cos(a) * r * 0.78),
                (cx + math.sin(a) * r * 0.88, cy - math.cos(a) * r * 0.88)], OUT, 4)
    a = math.radians(hour * 30)
    c.line([(cx, cy), (cx + math.sin(a) * r * 0.5, cy - math.cos(a) * r * 0.5)], OUT, 9)
    c.line([(cx, cy), (cx, cy - r * 0.72)], OUT, 6)


# ---------- personnages ----------

def head(c, cx, cy, r, skin, hair, style="bob", glasses=False, eyes="open", tears=False,
         mouth="smile", cap=None):
    if style == "bob":  # Sofía : carré auburn + barrette
        c.ell(cx, cy - r * 0.05, r * 1.15, r * 1.1, hair)
        c.rect(cx - r * 1.15, cy - r * 0.1, cx + r * 1.15, cy + r * 0.75, hair, r=int(r * 0.3))
    c.ell(cx, cy, r, r, skin)
    if style == "bob":
        c.d.chord(c.s(cx - r * 1.02, cy - r * 1.05, cx + r * 1.02, cy + r * 0.6), 180, 360,
                  fill=hair, outline=OUT, width=LW * K)
        c.rect(cx + r * 0.35, cy - r * 0.62, cx + r * 0.75, cy - r * 0.45, (235, 80, 100), r=6, w=4)
    elif style == "short":
        c.d.chord(c.s(cx - r * 1.02, cy - r * 1.1, cx + r * 1.02, cy + r * 0.4), 180, 360,
                  fill=hair, outline=OUT, width=LW * K)
    elif style == "bald":
        c.arc(cx, cy, r * 0.9, r * 0.9, 200, 340, hair, 14)
    if cap:
        c.d.chord(c.s(cx - r * 1.05, cy - r * 1.15, cx + r * 1.05, cy + r * 0.35), 180, 360,
                  fill=cap, outline=OUT, width=LW * K)
        c.rect(cx - r * 0.1, cy - r * 0.48, cx + r * 1.45, cy - r * 0.3, cap, r=8)
    ex, ey, er = r * 0.38, cy + r * 0.05, r * 0.2
    for sx in (-1, 1):
        x = cx + sx * ex
        if eyes == "closed":
            c.arc(x, ey, er, er * 0.6, 20, 160, OUT, 7)
        else:
            k = 1.25 if eyes == "wide" else 1
            c.ell(x, ey, er * k, er * k * 1.1, (255, 255, 255), w=5)
            c.ell(x + er * 0.15, ey + er * 0.1, er * 0.5 * k, er * 0.55 * k, OUT, outline=None)
            c.ell(x + er * 0.3, ey - er * 0.1, er * 0.15, er * 0.15, (255, 255, 255), outline=None)
        if glasses:
            c.ell(x, ey, er * 1.55, er * 1.55, None, w=6)
        if tears:
            tear(c, x - er * 0.3, ey + er * 2.4, er * 0.75)
    if glasses:
        c.line([(cx - ex + er * 1.5, ey), (cx + ex - er * 1.5, ey)], OUT, 6)
    c.ell(cx - r * 0.6, cy + r * 0.38, r * 0.14, r * 0.08, (240, 150, 150), outline=None)
    c.ell(cx + r * 0.6, cy + r * 0.38, r * 0.14, r * 0.08, (240, 150, 150), outline=None)
    my = cy + r * 0.55
    if mouth == "smile":
        c.arc(cx, my - r * 0.12, r * 0.22, r * 0.15, 20, 160, OUT, 7)
    elif mouth == "sad":
        c.arc(cx, my + r * 0.08, r * 0.2, r * 0.12, 200, 340, OUT, 7)
    elif mouth == "o":
        c.ell(cx, my, r * 0.1, r * 0.13, OUT, outline=None)
    elif mouth == "snore":
        c.ell(cx, my, r * 0.16, r * 0.1, OUT, outline=None)


PERSOS = {
    "sofia": dict(skin=SKIN[0], hair=(180, 80, 40), style="bob", glasses=True,
                  shirt=MOUTARDE, pants=(70, 80, 120)),
    "hugo": dict(skin=SKIN[1], hair=(40, 30, 30), style="short", glasses=False,
                 shirt=(90, 170, 120), pants=(60, 60, 80), cap=(60, 150, 90)),
    "pablo": dict(skin=SKIN[2], hair=(30, 25, 25), style="short", glasses=False,
                  shirt=(90, 120, 190), pants=(60, 60, 80)),
    "sabio": dict(skin=SKIN[0], hair=(120, 110, 110), style="bald", glasses=True,
                  shirt=(255, 255, 255), pants=(80, 80, 90)),
    "sabia": dict(skin=SKIN[1], hair=(40, 30, 30), style="bob", glasses=False,
                  shirt=(255, 255, 255), pants=(80, 80, 90)),
}


def person(c, who, cx, ground, h=640, arms="down", **kw):
    p = dict(PERSOS[who]); p.update(kw)
    r = h * 0.17
    hy = ground - h + r
    by0, by1 = hy + r * 0.9, ground - h * 0.3
    # jambes
    for sx in (-1, 1):
        c.rect(cx + sx * r * 0.45 - r * 0.22, by1 - 10, cx + sx * r * 0.45 + r * 0.22, ground - 18, p["pants"], r=10)
        c.ell(cx + sx * r * 0.5, ground - 14, r * 0.38, r * 0.17, (250, 250, 250))
    # bras
    sh = by0 + r * 0.35
    for sx in (-1, 1):
        mode = arms if sx == 1 else ("down" if arms in ("point", "wave") else arms)
        if mode == "down":
            end = (cx + sx * r * 1.15, by1 - r * 0.2)
        elif mode == "point":
            end = (cx + sx * r * 2.3, sh - r * 0.1)
        elif mode == "up":
            end = (cx + sx * r * 1.6, sh - r * 1.4)
        else:  # wave
            end = (cx + sx * r * 1.7, sh - r * 1.0)
        c.line([(cx + sx * r * 0.8, sh), end], OUT, int(r * 0.42))
        c.line([(cx + sx * r * 0.8, sh), end], p["shirt"], int(r * 0.3))
        c.ell(end[0], end[1], r * 0.2, r * 0.2, p["skin"], w=5)
    c.rect(cx - r * 0.95, by0, cx + r * 0.95, by1, p["shirt"], r=int(r * 0.5))
    if who in ("sabio", "sabia"):  # blouse
        c.line([(cx, by0 + 10), (cx, by1 - 10)], OUT, 5)
    head(c, cx, hy, r, p["skin"], p["hair"], p["style"], p["glasses"],
         kw.get("eyes", "open"), kw.get("tears", False), kw.get("mouth", "smile"), p.get("cap"))


# ---------- Salchicha (teckel, foulard rouge) ----------
DOG = (176, 104, 56)
DOG_D = (120, 66, 36)


def dog(c, cx, cy, s=1.0, eyes="open", face=1, tears=False):
    """Teckel vu de profil, centre du corps (cx, cy). face=1 regarde à droite."""
    f = face
    L, T = 230 * s, 70 * s
    for lx in (-0.75, -0.45, 0.45, 0.75):  # pattes
        c.rect(cx + lx * L - 16 * s, cy + T * 0.5, cx + lx * L + 16 * s, cy + T + 25 * s, DOG_D, r=int(10 * s))
    c.line([(cx - f * L * 0.95, cy - T * 0.2), (cx - f * L * 1.3, cy - T * 0.9)], OUT, int(26 * s))  # queue
    c.line([(cx - f * L * 0.95, cy - T * 0.2), (cx - f * L * 1.3, cy - T * 0.9)], DOG, int(16 * s))
    c.rect(cx - L, cy - T, cx + L, cy + T, DOG, r=int(T))
    hx, hy, hr = cx + f * L * 0.95, cy - T * 1.3, 78 * s
    c.poly([(hx - 70 * s, hy + 55 * s), (hx + 70 * s, hy + 55 * s), (hx, hy + 120 * s)], (220, 50, 50))  # foulard
    c.ell(hx, hy, hr, hr * 0.92, DOG)
    c.ell(hx + f * hr * 0.85, hy + hr * 0.25, hr * 0.6, hr * 0.42, (215, 160, 115))  # museau
    c.ell(hx + f * hr * 1.38, hy + hr * 0.12, hr * 0.17, hr * 0.13, OUT, outline=None)  # truffe
    c.ell(hx - f * hr * 0.55, hy + hr * 0.15, hr * 0.33, hr * 0.7, DOG_D)  # oreille
    ex, ey = hx + f * hr * 0.25, hy - hr * 0.2
    if eyes == "closed":
        c.arc(ex, ey, hr * 0.17, hr * 0.1, 20, 160, OUT, 7)
    else:
        k = 1.3 if eyes == "wide" else 1
        c.ell(ex, ey, hr * 0.19 * k, hr * 0.21 * k, (255, 255, 255), w=5)
        c.ell(ex + f * hr * 0.05, ey, hr * 0.1 * k, hr * 0.12 * k, OUT, outline=None)
        c.ell(ex + f * hr * 0.09, ey - hr * 0.05, hr * 0.04, hr * 0.04, (255, 255, 255), outline=None)
    if tears:
        tear(c, ex, ey + hr * 0.45, hr * 0.15)


def dog_face(c, cx, cy, r, eyes="open", tears=False, color=DOG):
    """Tête de chien de face (gros plans, grilles)."""
    c.ell(cx - r * 0.9, cy + r * 0.1, r * 0.35, r * 0.75, DOG_D if color == DOG else tuple(int(v * 0.7) for v in color))
    c.ell(cx + r * 0.9, cy + r * 0.1, r * 0.35, r * 0.75, DOG_D if color == DOG else tuple(int(v * 0.7) for v in color))
    c.ell(cx, cy, r, r * 0.95, color)
    c.ell(cx, cy + r * 0.45, r * 0.5, r * 0.36, (225, 175, 130))
    c.ell(cx, cy + r * 0.3, r * 0.2, r * 0.13, OUT, outline=None)
    for sx in (-1, 1):
        x, y = cx + sx * r * 0.38, cy - r * 0.15
        if eyes == "closed":
            c.arc(x, y, r * 0.15, r * 0.09, 20, 160, OUT, 7)
        else:
            k = 1.3 if eyes == "wide" else 1
            c.ell(x, y, r * 0.17 * k, r * 0.19 * k, (255, 255, 255), w=5)
            c.ell(x, y + 3, r * 0.09 * k, r * 0.11 * k, OUT, outline=None)
            c.ell(x + r * 0.04, y - r * 0.04, r * 0.035, r * 0.035, (255, 255, 255), outline=None)
        if tears:
            tear(c, x, y + r * 0.42, r * 0.13)
    if color == DOG:
        c.poly([(cx - r * 0.7, cy + r * 0.75), (cx + r * 0.7, cy + r * 0.75), (cx, cy + r * 1.25)], (220, 50, 50))


# ---------- mobilier ----------

def bed_top(c, people=("sofia", "pablo"), dog_pos=None, people_eyes="closed", blanket=(205, 120, 95)):
    """Lit vu de dessus. dog_pos: 'bottom', 'middle', 'pillow'."""
    c.rect(170, 260, 910, 1640, (150, 100, 70), r=30)
    c.rect(200, 300, 880, 1600, (250, 250, 245), r=24)
    xs = (370, 710) if len(people) == 2 else (540,)
    for x, who in zip(xs, people):
        c.rect(x - 140, 330, x + 140, 520, (255, 255, 255), r=40)
        p = PERSOS[who]
        head(c, x, 450, 95, p["skin"], p["hair"], p["style"], p["glasses"], people_eyes,
             mouth="smile" if people_eyes == "open" else "snore" if who == "pablo" else "smile")
    if "pillow" == dog_pos:
        c.rect(400, 330, 680, 520, (255, 255, 255), r=40)
        dog_face(c, 540, 440, 100, eyes="closed")
    c.rect(200, 570, 880, 1600, blanket, r=24)
    for i in range(6):
        for j in range(9):
            c.ell(260 + i * 112, 640 + j * 108, 9, 9, (240, 200, 170), outline=None)
    if dog_pos == "middle":
        dog(c, 540, 840, 0.75, eyes="closed")
    elif dog_pos == "bottom":
        dog(c, 600, 1500, 0.7, eyes="open")

"""Original flat-cartoon sprites for the Spanish 'Pipi' video (all drawn from scratch)."""
from functools import lru_cache
from PIL import Image, ImageDraw
import math

K = 2  # supersampling factor
INK = (43, 29, 20, 255)
OW = 6  # outline width at 1x

ORANGE = (236, 152, 66, 255)
ORANGE_D = (196, 112, 40, 255)
CREAM = (255, 242, 216, 255)
PINK = (246, 150, 160, 255)
RED = (226, 56, 60, 255)
WHITE = (255, 255, 255, 255)
BLACK = (30, 22, 18, 255)


class P:
    """Drawing helper working in 1x coordinates on a Kx canvas."""

    def __init__(self, w, h, ox=0, oy=0):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.ox, self.oy = ox, oy

    def _p(self, x, y):
        return ((x + self.ox) * K, (y + self.oy) * K)

    def ell(self, cx, cy, rx, ry, fill, ow=OW, outline=INK):
        a = self._p(cx - rx, cy - ry)
        b = self._p(cx + rx, cy + ry)
        self.d.ellipse([a, b], fill=fill, outline=outline if ow else None, width=int(ow * K))

    def rect(self, x0, y0, x1, y1, fill, r=0, ow=OW, outline=INK):
        a = self._p(x0, y0)
        b = self._p(x1, y1)
        self.d.rounded_rectangle([a, b], radius=r * K, fill=fill, outline=outline if ow else None, width=int(ow * K))

    def poly(self, pts, fill, ow=OW, outline=INK):
        pp = [self._p(x, y) for x, y in pts]
        self.d.polygon(pp, fill=fill)
        if ow:
            self.d.line(pp + [pp[0]], fill=outline, width=int(ow * K), joint="curve")

    def line(self, pts, fill=INK, w=OW):
        pp = [self._p(x, y) for x, y in pts]
        self.d.line(pp, fill=fill, width=int(w * K), joint="curve")
        r = w * K / 2
        for x, y in (pp[0], pp[-1]):
            self.d.ellipse([x - r, y - r, x + r, y + r], fill=fill)

    def arc(self, cx, cy, rx, ry, a0, a1, fill=INK, w=OW):
        a = self._p(cx - rx, cy - ry)
        b = self._p(cx + rx, cy + ry)
        self.d.arc([a, b], a0, a1, fill=fill, width=int(w * K))

    def done(self):
        return self.im.resize((self.w, self.h), Image.LANCZOS)


# ---------------------------------------------------------------- dog "Pipi"
def _dog_head(p, eyes="open", mouth="smile", look=0.0, sweat=False, blush=True):
    # pointy ears (shiba-like mutt, original design)
    for s in (-1, 1):
        p.poly([(s * 135, -40), (s * 150, -200), (s * 45, -115)], ORANGE)
        p.poly([(s * 122, -70), (s * 135, -165), (s * 75, -112)], PINK, ow=0)
    p.ell(0, 0, 155, 132, ORANGE)
    # cream mask + brow dots
    p.ell(0, 58, 105, 70, CREAM, ow=0)
    p.ell(-70, 30, 52, 42, CREAM, ow=0)
    p.ell(70, 30, 52, 42, CREAM, ow=0)
    p.ell(-52, -62, 15, 10, CREAM, ow=0)
    p.ell(52, -62, 15, 10, CREAM, ow=0)
    p.arc(0, 0, 155, 132, 0, 360)
    # eyes
    for s in (-1, 1):
        ex, ey = s * 55, -12
        if eyes == "closed":
            p.arc(ex, ey + 6, 26, 18, 200, 340, w=7)
        elif eyes == "sleep":
            p.arc(ex, ey - 6, 26, 18, 20, 160, w=7)
        else:
            big = eyes == "beg"
            p.ell(ex, ey, 30, 34, WHITE)
            pr = 23 if big else 18
            px = ex + look * 10
            p.ell(px, ey + 4, pr, pr + 2, BLACK, ow=0)
            p.ell(px - 7, ey - 6, 7, 7, WHITE, ow=0)
            if big:
                p.ell(px + 8, ey + 12, 4, 4, WHITE, ow=0)
                p.line([(ex - s * 30, ey - 52), (ex + s * 2, ey - 44)], w=6)
            if eyes == "worry":
                p.line([(ex - s * 28, ey - 40), (ex + s * 10, ey - 52)], w=6)
    if blush:
        p.ell(-100, 40, 20, 11, (250, 140, 140, 200), ow=0)
        p.ell(100, 40, 20, 11, (250, 140, 140, 200), ow=0)
    # nose
    p.rect(-24, 24, 24, 50, BLACK, r=14, ow=0)
    p.ell(-8, 31, 6, 4, (120, 120, 120, 255), ow=0)
    # mouth
    if mouth == "smile":
        p.arc(-20, 60, 20, 16, 0, 180, w=6)
        p.arc(20, 60, 20, 16, 0, 180, w=6)
    elif mouth == "tongue":
        p.ell(0, 92, 26, 30, PINK)
        p.line([(0, 72), (0, 98)], fill=(210, 90, 110, 255), w=4)
        p.arc(-20, 60, 20, 16, 0, 180, w=6)
        p.arc(20, 60, 20, 16, 0, 180, w=6)
    elif mouth == "sad":
        p.line([(0, 50), (0, 66)], w=5)
        p.arc(0, 92, 26, 18, 200, 340, w=6)
    elif mouth == "o":
        p.line([(0, 50), (0, 62)], w=5)
        p.ell(0, 80, 14, 17, (110, 40, 40, 255))
    elif mouth == "wobbly":
        p.line([(0, 50), (0, 62)], w=5)
        p.line([(-30, 82), (-15, 72), (0, 82), (15, 72), (30, 82)], w=6)
    if sweat:
        p.poly([(150, -90), (138, -55), (162, -55)], (120, 200, 255, 255), ow=4)
        p.ell(150, -52, 13, 13, (120, 200, 255, 255), ow=4)


def _bandana(p, y):
    p.poly([(-110, y), (110, y), (0, y + 95)], RED)
    for dx, dy in ((-60, 18), (0, 22), (60, 18), (-25, 50), (25, 50), (0, 75)):
        p.ell(dx, y + dy, 7, 7, WHITE, ow=0)


@lru_cache(maxsize=256)
def dog(pose="sit", eyes="open", mouth="smile", look=0.0, sweat=False, scale=1.0):
    if pose == "head":
        p = P(380, 440, 190, 215)
        _bandana(p, 118)
        _dog_head(p, eyes, mouth, look, sweat)
    elif pose == "bed":
        p = P(560, 360, 280, 200)
        # cushion
        p.ell(0, 80, 270, 90, (64, 160, 140, 255))
        p.ell(0, 60, 220, 60, (98, 196, 170, 255), ow=0)
        # curled body
        p.ell(30, 40, 170, 75, ORANGE)
        p.ell(170, 40, 55, 30, CREAM)  # tail tip
        p.ell(-40, 72, 70, 22, CREAM)  # paws
        q = P(380, 440, 190, 215)
        _dog_head(q, eyes, mouth, look, sweat)
        h = q.done().resize((230, 266), Image.LANCZOS)
        im = p.done()
        im.alpha_composite(h, (40, 0))
        return _scaled(im, scale)
    else:  # sit
        p = P(440, 680, 220, 215)
        # tail
        p.line([(110, 400), (180, 330), (165, 250)], fill=INK, w=44)
        p.line([(110, 400), (180, 330), (165, 250)], fill=ORANGE, w=32)
        p.ell(165, 250, 20, 20, CREAM)
        # haunches + body
        p.ell(-95, 400, 70, 75, ORANGE)
        p.ell(95, 400, 70, 75, ORANGE)
        p.ell(0, 300, 125, 150, ORANGE)
        p.ell(0, 290, 72, 115, CREAM, ow=0)
        # front legs
        for s in (-1, 1):
            p.rect(s * 45 - 26, 330, s * 45 + 26, 455, ORANGE, r=24)
            p.ell(s * 45, 452, 36, 22, CREAM)
        p.ell(-140, 455, 46, 20, CREAM)
        p.ell(140, 455, 46, 20, CREAM)
        _bandana(p, 118)
        _dog_head(p, eyes, mouth, look, sweat)
    return _scaled(p.done(), scale)


def _scaled(im, s):
    if s == 1.0:
        return im
    return im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)


# ---------------------------------------------------------------- humans
SKINS = {"a": (247, 206, 170, 255), "b": (205, 150, 108, 255), "c": (150, 98, 66, 255)}


@lru_cache(maxsize=64)
def person(who, full=False, arm="down", scale=1.0, eyes="open"):
    H = 760 if full else 520
    p = P(420, H, 210, 150)
    c = PEOPLE[who]
    skin = SKINS[c["skin"]]
    if full:
        p.rect(-80, 300, -10, 520, c["pants"], r=20)
        p.rect(10, 300, 80, 520, c["pants"], r=20)
        p.rect(-95, 505, -5, 545, c.get("shoes", INK), r=18)
        p.rect(5, 505, 95, 545, c.get("shoes", INK), r=18)
    # torso
    p.rect(-110, 90, 110, 340, c["shirt"], r=60)
    if c.get("pattern") == "flowers":
        for dx, dy in ((-60, 150), (40, 130), (-20, 230), (70, 260), (-75, 290)):
            for a in range(5):
                ang = a * 2 * math.pi / 5
                p.ell(dx + 12 * math.cos(ang), dy + 12 * math.sin(ang), 8, 8, (255, 220, 90, 255), ow=0)
            p.ell(dx, dy, 6, 6, (240, 120, 60, 255), ow=0)
    if c.get("pattern") == "stripes":
        for y in range(120, 330, 40):
            p.rect(-104, y, 104, y + 16, (255, 255, 255, 230), ow=0)
        p.rect(-110, 90, 110, 340, None, r=60)
    if c.get("collar"):
        p.poly([(-40, 92), (0, 140), (40, 92)], c["collar"], ow=4)
    # arms
    if arm == "point":
        p.line([(95, 130), (190, 70)], fill=INK, w=46)
        p.line([(95, 130), (190, 70)], fill=c["shirt"], w=34)
        p.ell(200, 62, 22, 22, skin)
        p.line([(-95, 140), (-120, 290)], fill=INK, w=46)
        p.line([(-95, 140), (-120, 290)], fill=c["shirt"], w=34)
        p.ell(-120, 300, 22, 22, skin)
    elif arm == "cross":
        p.rect(-100, 190, 100, 240, c["shirt"], r=24)
        p.ell(-85, 215, 22, 22, skin)
        p.ell(85, 215, 22, 22, skin)
    elif arm == "give":
        p.line([(95, 140), (175, 250)], fill=INK, w=46)
        p.line([(95, 140), (175, 250)], fill=c["shirt"], w=34)
        p.ell(182, 262, 22, 22, skin)
    # neck + head
    p.rect(-26, 50, 26, 105, skin, r=10)
    if "hair_back" in c:
        c["hair_back"](p)
    p.ell(0, 0, 88, 92, skin)
    # face
    for s in (-1, 1):
        if eyes == "closed":
            p.arc(s * 32, 4, 13, 9, 200, 340, w=6)
        else:
            p.ell(s * 32, 0, 9, 12, BLACK, ow=0)
            p.ell(s * 32 - 3, -4, 3, 3, WHITE, ow=0)
    p.ell(-58, 32, 15, 9, (240, 130, 130, 150), ow=0)
    p.ell(58, 32, 15, 9, (240, 130, 130, 150), ow=0)
    p.arc(0, 30, 28, 22, 20, 160, w=6)
    c["hair"](p)
    if c.get("extra"):
        c["extra"](p)
    return _scaled(p.done(), scale)


def _hair_sofia(p):
    p.poly([(-92, -10), (-70, -80), (0, -100), (70, -80), (92, -10), (60, -50), (0, -60), (-60, -50)], (60, 36, 26, 255))
    p.ell(95, -60, 34, 30, (60, 36, 26, 255))
    p.line([(105, -40), (130, 40), (115, 90)], fill=INK, w=40)
    p.line([(105, -40), (130, 40), (115, 90)], fill=(60, 36, 26, 255), w=28)
    p.ell(70, -70, 14, 14, (255, 110, 160, 255))


def _hair_back_sofia(p):
    pass


def _hair_dad(p):
    # bald top, side hair, big mustache, sunglasses on head
    p.ell(-84, 0, 16, 34, (40, 30, 26, 255), ow=0)
    p.ell(84, 0, 16, 34, (40, 30, 26, 255), ow=0)
    p.rect(-62, -70, -8, -40, (30, 30, 40, 255), r=14)
    p.rect(8, -70, 62, -40, (30, 30, 40, 255), r=14)
    p.line([(-8, -56), (8, -56)], w=5)
    p.poly([(-50, 30), (-10, 16), (0, 24), (10, 16), (50, 30), (30, 44), (0, 34), (-30, 44)], (40, 30, 26, 255), ow=3)


def _hair_grandma(p):
    # cauliflower cloud hair
    for dx, dy, r in ((-80, -30, 38), (-60, -78, 42), (-15, -100, 44), (35, -96, 42), (75, -66, 40),
                      (88, -20, 34), (-92, 12, 28), (92, 18, 28), (0, -70, 40)):
        p.ell(dx, dy, r, r, (250, 250, 244, 255), ow=5, outline=(170, 170, 160, 255))
    # glasses
    for s in (-1, 1):
        p.ell(s * 32, 0, 22, 20, (255, 255, 255, 60), ow=5)
    p.line([(-10, 0), (10, 0)], w=4)


def _extra_grandma(p):
    for i in range(7):
        a = math.pi * (0.15 + 0.7 * i / 6)
        p.ell(-75 * math.cos(a) * 0.6, 110 + 30 * math.sin(a), 8, 8, WHITE, ow=2)


def _hair_harry(p):
    # green cap backwards
    p.ell(0, -50, 92, 56, (70, 170, 80, 255))
    p.rect(-120, -40, -40, -18, (50, 140, 64, 255), r=10)
    p.ell(0, -100, 10, 8, (50, 140, 64, 255), ow=3)
    p.poly([(60, -10), (78, -40), (90, -6)], (90, 60, 40, 255), ow=0)


def _hair_mom(p):
    for dx, dy in ((-80, -30), (-60, -80), (-10, -100), (45, -90), (82, -45), (-92, 20), (92, 20)):
        p.ell(dx, dy, 36, 36, (110, 60, 40, 255), ow=0)
    p.ell(-70, -85, 20, 12, (255, 200, 60, 255), ow=3)


def _hair_trainer(p):
    p.poly([(-92, -10), (-70, -85), (0, -102), (70, -85), (92, -10), (40, -60), (-40, -60)], (200, 120, 50, 255))
    p.ell(0, -110, 30, 24, (200, 120, 50, 255))


def _extra_trainer(p):
    # whistle on lanyard
    p.line([(-40, 92), (0, 190), (40, 92)], fill=(230, 60, 60, 255), w=5)
    p.rect(-14, 185, 20, 210, (210, 210, 220, 255), r=8, ow=4)


PEOPLE = {
    "sofia": dict(skin="b", shirt=(255, 205, 60, 255), hair=_hair_sofia, collar=(255, 255, 255, 255)),
    "dad": dict(skin="a", shirt=(60, 130, 220, 255), pattern="flowers", hair=_hair_dad, pants=(230, 210, 170, 255),
                shoes=(120, 80, 50, 255)),
    "grandma": dict(skin="a", shirt=(250, 130, 110, 255), hair=_hair_grandma, extra=_extra_grandma),
    "harry": dict(skin="c", shirt=(90, 180, 90, 255), pattern="stripes", hair=_hair_harry),
    "mom": dict(skin="c", shirt=(250, 150, 60, 255), hair=_hair_mom),
    "trainer": dict(skin="b", shirt=(30, 170, 170, 255), hair=_hair_trainer, extra=_extra_trainer,
                    pants=(60, 70, 90, 255), shoes=(240, 240, 240, 255), collar=(20, 130, 130, 255)),
}


# ---------------------------------------------------------------- props
@lru_cache(maxsize=None)
def chicken(scale=1.0, skinless=False):
    p = P(420, 260, 210, 150)
    p.ell(0, 70, 200, 50, WHITE)  # plate
    p.ell(0, 66, 160, 36, (235, 235, 240, 255), ow=0)
    gold = (226, 150, 60, 255)
    for s in (-1, 1):
        p.line([(s * 90, 20), (s * 150, -40)], fill=INK, w=50)
        p.line([(s * 90, 20), (s * 150, -40)], fill=gold, w=38)
        p.ell(s * 160, -52, 18, 18, CREAM)
    p.ell(0, 10, 120, 80, (238, 170, 70, 255) if not skinless else (250, 220, 200, 255))
    p.arc(-20, -10, 60, 40, 200, 300, fill=(255, 220, 150, 255), w=10)
    for dx in (-80, 80):
        p.ell(dx, 70, 16, 12, (90, 180, 70, 255), ow=3)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def bowl(full=True, scale=1.0, color=(70, 120, 220, 255)):
    p = P(320, 180, 160, 90)
    if full:
        for dx, dy in ((-70, -20), (-30, -34), (10, -28), (50, -36), (80, -18), (-50, -4), (30, -10), (0, -50)):
            p.ell(dx, dy, 22, 16, (150, 90, 50, 255), ow=4)
    p.poly([(-140, -10), (140, -10), (110, 70), (-110, 70)], color)
    p.ell(0, -10, 140, 22, tuple(min(255, c + 40) for c in color[:3]) + (255,))
    if not full:
        p.ell(0, -10, 115, 14, (40, 60, 120, 255), ow=0)
    p.rect(-60, 20, 60, 46, WHITE, r=12, ow=3)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def bread(scale=1.0):
    p = P(200, 180, 100, 90)
    p.ell(-40, -30, 50, 45, (210, 150, 80, 255))
    p.ell(40, -30, 50, 45, (210, 150, 80, 255))
    p.rect(-85, -30, 85, 70, (210, 150, 80, 255), r=16)
    p.rect(-65, -20, 65, 52, (255, 230, 180, 255), r=12, ow=0)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def potato(scale=1.0):
    p = P(160, 130, 80, 65)
    p.ell(0, 0, 70, 52, (220, 180, 100, 255))
    for dx, dy in ((-30, -10), (20, 14), (30, -20)):
        p.ell(dx, dy, 5, 4, (150, 110, 60, 255), ow=0)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def morsel(scale=1.0):
    p = P(120, 100, 60, 50)
    p.ell(0, 0, 50, 34, (238, 170, 70, 255))
    p.arc(-6, -6, 26, 16, 200, 300, fill=(255, 220, 150, 255), w=7)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def fork(scale=1.0):
    p = P(120, 420, 60, 30)
    silver = (205, 210, 220, 255)
    p.rect(-14, 150, 14, 380, silver, r=12)
    p.rect(-40, 90, 40, 160, silver, r=18)
    for dx in (-30, -10, 10, 30):
        p.rect(dx - 6, 0, dx + 6, 110, silver, r=6)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def calendar(label="DOM", num="7", scale=1.0, sun=True):
    p = P(320, 340, 160, 170)
    p.rect(-140, -130, 140, 150, WHITE, r=22)
    p.rect(-140, -130, 140, -50, RED, r=22)
    p.rect(-137, -70, 137, -50, RED, ow=0)
    for dx in (-70, 70):
        p.rect(dx - 12, -160, dx + 12, -105, (180, 180, 190, 255), r=10)
    if sun:
        p.ell(0, 50, 50, 50, (255, 200, 40, 255))
        for a in range(10):
            ang = a * math.pi / 5
            p.line([(70 * math.cos(ang), 50 + 70 * math.sin(ang)), (90 * math.cos(ang), 50 + 90 * math.sin(ang))],
                   fill=(255, 170, 30, 255), w=8)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=256)
def clock(ang_min=0, ang_hour=120, scale=1.0, stopwatch=False):
    p = P(320, 360, 160, 190)
    if stopwatch:
        p.rect(-22, -175, 22, -140, (230, 80, 60, 255), r=8)
        p.ell(110, -120, 20, 20, (230, 80, 60, 255))
    p.ell(0, 0, 145, 145, WHITE, ow=10)
    for i in range(12):
        a = i * math.pi / 6
        p.line([(118 * math.sin(a), -118 * math.cos(a)), (132 * math.sin(a), -132 * math.cos(a))], w=6)
    for ang, ln, w, col in ((ang_hour, 70, 12, INK), (ang_min, 110, 8, (230, 60, 60, 255) if stopwatch else INK)):
        a = math.radians(ang)
        p.line([(0, 0), (ln * math.sin(a), -ln * math.cos(a))], fill=col, w=w)
    p.ell(0, 0, 12, 12, INK, ow=0)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=64)
def thermometer(level=0.5, scale=1.0):
    p = P(140, 460, 70, 40)
    p.rect(-30, -20, 30, 340, WHITE, r=30)
    col = (230, 60, 60, 255) if level > 0.5 else (90, 170, 240, 255)
    top = 320 - level * 300
    p.rect(-14, top, 14, 340, col, r=12, ow=0)
    p.ell(0, 370, 52, 52, col)
    for y in range(20, 320, 50):
        p.line([(30, y), (48, y)], w=5)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def bubble(scale=1.0, w=360, h=250):
    p = P(w + 40, h + 140, (w + 40) // 2, h // 2 + 20)
    p.ell(-w // 2 + 70, h // 2 + 55, 26, 22, WHITE)
    p.ell(-w // 2 + 40, h // 2 + 100, 14, 12, WHITE)
    for dx, dy, r in ((-w * 0.3, 0, h * 0.42), (w * 0.3, 0, h * 0.42), (0, -h * 0.15, h * 0.48), (0, h * 0.18, h * 0.38)):
        p.ell(dx, dy, r * 1.15, r, WHITE)
    for dx, dy, r in ((-w * 0.3, 0, h * 0.42), (w * 0.3, 0, h * 0.42), (0, -h * 0.15, h * 0.48), (0, h * 0.18, h * 0.38)):
        p.ell(dx, dy, r * 1.15 - 5, r - 5, WHITE, ow=0)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def qmark(scale=1.0, color=(255, 210, 40, 255)):
    from PIL import ImageFont
    f = ImageFont.truetype(FONT, 220 * K)
    im = Image.new("RGBA", (200 * K, 260 * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((100 * K, 130 * K), "?", font=f, fill=color, anchor="mm", stroke_width=10 * K, stroke_fill=INK)
    return _scaled(im.resize((200, 260), Image.LANCZOS), scale)


@lru_cache(maxsize=None)
def badge(text, scale=1.0, color=(255, 80, 80, 255), fg=WHITE, size=110):
    from PIL import ImageFont
    f = ImageFont.truetype(FONT, size * K)
    tw = int(f.getlength(text) / K) + 80
    im = Image.new("RGBA", ((tw + 20) * K, (size + 70) * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([6 * K, 6 * K, (tw + 14) * K, (size + 64) * K], radius=40 * K, fill=color, outline=INK,
                        width=OW * K)
    d.text(((tw + 20) * K // 2, (size + 70) * K // 2), text, font=f, fill=fg, anchor="mm", stroke_width=6 * K,
           stroke_fill=INK)
    return _scaled(im.resize((tw + 20, size + 70), Image.LANCZOS), scale)


@lru_cache(maxsize=None)
def xmark(scale=1.0):
    p = P(260, 260, 130, 130)
    for a, b in (((-100, -100), (100, 100)), ((100, -100), (-100, 100))):
        p.line([a, b], fill=INK, w=54)
        p.line([a, b], fill=(235, 50, 50, 255), w=38)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def check(scale=1.0):
    p = P(280, 240, 140, 120)
    p.line([(-100, 0), (-30, 70), (100, -80)], fill=INK, w=58)
    p.line([(-100, 0), (-30, 70), (100, -80)], fill=(60, 200, 90, 255), w=40)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def heart(scale=1.0):
    p = P(160, 150, 80, 70)
    p.ell(-32, -18, 40, 38, (240, 70, 100, 255))
    p.ell(32, -18, 40, 38, (240, 70, 100, 255))
    p.poly([(-68, 0), (68, 0), (0, 70)], (240, 70, 100, 255), ow=0)
    p.line([(-70, 2), (0, 70), (70, 2)], w=OW)
    p.ell(-32, -18, 34, 32, (240, 70, 100, 255), ow=0)
    p.ell(32, -18, 34, 32, (240, 70, 100, 255), ow=0)
    p.ell(-36, -28, 10, 8, (255, 180, 190, 255), ow=0)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def smell(scale=1.0, color=(255, 255, 255, 230)):
    p = P(200, 300, 100, 150)
    for dx in (-50, 0, 50):
        pts = [(dx + 18 * math.sin(i / 3.0), 120 - i * 12) for i in range(21)]
        p.line(pts, fill=color, w=12)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def nose_big(scale=1.0):
    p = P(760, 520, 380, 260)
    p.ell(0, 0, 340, 220, (36, 26, 24, 255), ow=10)
    p.ell(-140, 40, 70, 50, (10, 6, 6, 255), ow=0)
    p.ell(140, 40, 70, 50, (10, 6, 6, 255), ow=0)
    p.line([(0, 60), (0, 210)], fill=(10, 6, 6, 255), w=14)
    p.ell(-120, -110, 90, 40, (110, 100, 100, 255), ow=0)
    p.ell(150, -120, 40, 22, (90, 80, 80, 255), ow=0)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=64)
def slot(symbols=("hueso", "pollo", "x"), scale=1.0, offset=0):
    p = P(560, 560, 280, 280)
    p.rect(-240, -200, 240, 230, (230, 60, 80, 255), r=40)
    p.rect(-200, -250, 200, -180, (255, 200, 40, 255), r=30)
    p.rect(-200, -120, 200, 120, WHITE, r=20)
    for i in range(3):
        x = -133 + i * 133
        p.rect(x - 56, -105, x + 56, 105, (245, 245, 250, 255), r=12, ow=4)
    p.line([(250, -40), (300, -140)], w=16)
    p.ell(300, -150, 30, 30, (255, 200, 40, 255))
    p.rect(-160, 150, 160, 200, (150, 30, 50, 255), r=20, ow=4)
    im = p.done()
    for i, s in enumerate(symbols):
        x = 280 - 133 + i * 133
        spr = {"hueso": bone(0.55), "pollo": morsel(0.9), "x": xmark(0.32)}[s]
        im.alpha_composite(spr, (int(x - spr.width / 2), int(280 - spr.height / 2 + offset)))
    return _scaled(im, scale)


@lru_cache(maxsize=None)
def bone(scale=1.0):
    p = P(220, 120, 110, 60)
    for s in (-1, 1):
        p.ell(s * 75, -22, 26, 26, CREAM)
        p.ell(s * 75, 22, 26, 26, CREAM)
    p.rect(-75, -20, 75, 20, CREAM, ow=0)
    p.line([(-70, -20), (70, -20)], w=OW)
    p.line([(-70, 20), (70, 20)], w=OW)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def checklist(scale=1.0):
    p = P(340, 420, 170, 210)
    p.rect(-140, -180, 140, 190, (250, 245, 230, 255), r=20)
    p.rect(-60, -200, 60, -160, (120, 120, 130, 255), r=12)
    for i, y in enumerate((-100, -10, 80)):
        p.rect(-110, y - 25, -60, y + 25, WHITE, r=8, ow=5)
        p.line([(-40, y), (100, y)], fill=(170, 170, 180, 255), w=10)
    im = p.done()
    c = check(0.3)
    for y in (-100, -10, 80):
        im.alpha_composite(c, (170 - 85 - c.width // 2, 210 + y - c.height // 2 - 8))
    return _scaled(im, scale)


@lru_cache(maxsize=None)
def sparkle(scale=1.0, color=(255, 230, 80, 255)):
    p = P(140, 140, 70, 70)
    p.poly([(0, -60), (14, -14), (60, 0), (14, 14), (0, 60), (-14, 14), (-60, 0), (-14, -14)], color, ow=4)
    return _scaled(p.done(), scale)


@lru_cache(maxsize=None)
def zzz(scale=1.0):
    from PIL import ImageFont
    f = ImageFont.truetype(FONT, 90 * K)
    im = Image.new("RGBA", (260 * K, 200 * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, (x, y, s) in enumerate(((40, 150, 1.0), (120, 90, 0.8), (190, 40, 0.6))):
        ff = ImageFont.truetype(FONT, int(90 * s) * K)
        d.text((x * K, y * K), "z", font=ff, fill=WHITE, anchor="mm", stroke_width=6 * K, stroke_fill=INK)
    return _scaled(im.resize((260, 200), Image.LANCZOS), scale)


FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"

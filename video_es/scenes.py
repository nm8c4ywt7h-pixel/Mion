"""Backgrounds + shot list. Every shot is a function (t, dur) -> list of (img, cx, by) placed bottom-centre."""
import math
from functools import lru_cache
from PIL import Image, ImageDraw
from sprites import *

W, H = 1080, 1920
MARGIN = 1.0


# ---------------------------------------------------------------- backgrounds (drawn at Kx, cached)
@lru_cache(maxsize=None)
def bg(kind, color=None):
    p = P(W, H)
    d = p
    if kind == "stripes":
        c1, c2 = color
        p.rect(0, 0, W, H, c1, ow=0)
        for i in range(-20, 30):
            x = i * 120
            p.poly([(x, 0), (x + 60, 0), (x + 60 - 900, H), (x - 900, H)], c2, ow=0)
    elif kind == "burst":
        c1, c2 = color
        p.rect(0, 0, W, H, c1, ow=0)
        cx, cy = W / 2, H * 0.45
        for i in range(24):
            a0 = i * 2 * math.pi / 24
            a1 = a0 + math.pi / 24
            p.poly([(cx, cy), (cx + 3000 * math.cos(a0), cy + 3000 * math.sin(a0)),
                    (cx + 3000 * math.cos(a1), cy + 3000 * math.sin(a1))], c2, ow=0)
    elif kind == "dots":
        c1, c2 = color
        p.rect(0, 0, W, H, c1, ow=0)
        for y in range(0, H + 100, 110):
            for x in range((y // 110) % 2 * 55, W + 100, 110):
                p.ell(x, y, 16, 16, c2, ow=0)
    elif kind in ("terrace", "terrace_table"):
        # sky
        for i in range(20):
            col = (150 + i * 3, 210 + i * 1, 250, 255)
            p.rect(0, i * 50, W, i * 50 + 52, col, ow=0)
        # hills + garden hedge
        p.ell(250, 1050, 520, 200, (150, 210, 120, 255), ow=0)
        p.ell(900, 1080, 560, 230, (120, 190, 100, 255), ow=0)
        p.rect(0, 1000, W, 1200, (90, 170, 90, 255), ow=0)
        for x in range(-40, W + 80, 90):
            p.ell(x, 1000, 70, 50, (90, 170, 90, 255), ow=0)
        p.ell(150, 220, 70, 70, (255, 230, 90, 255), ow=0)
        # pergola beams
        for x in (60, W - 60):
            p.rect(x - 28, 140, x + 28, 1300, (176, 120, 70, 255))
        p.rect(-20, 110, W + 20, 170, (196, 136, 82, 255))
        for x in range(30, W, 140):
            p.rect(x - 14, 90, x + 14, 190, (160, 104, 60, 255))
        # string lights
        pts = [(x, 250 + 70 * math.sin(x / W * math.pi)) for x in range(0, W + 1, 20)]
        p.line(pts, fill=(60, 50, 40, 255), w=5)
        for i, x in enumerate(range(60, W, 120)):
            y = 250 + 70 * math.sin(x / W * math.pi)
            col = [(255, 210, 80, 255), (255, 120, 120, 255), (120, 210, 255, 255)][i % 3]
            p.ell(x, y + 24, 16, 22, col, ow=4)
        # plants in terracotta pots
        for x in (170, W - 170):
            for dx, dy, r in ((-50, 1030, 60), (40, 1010, 70), (0, 960, 65), (-20, 1060, 55)):
                p.ell(x + dx, dy, r, r, (70, 150, 70, 255))
            p.poly([(x - 80, 1080), (x + 80, 1080), (x + 60, 1230), (x - 60, 1230)], (205, 110, 70, 255))
        # tile floor
        p.rect(0, 1200, W, H, (222, 150, 110, 255), ow=0)
        for y in range(1200, H, 110):
            p.line([(0, y), (W, y)], fill=(196, 122, 86, 255), w=5)
        for i in range(-6, 12):
            p.line([(W / 2 + i * 60, 1200), (W / 2 + i * 220, H)], fill=(196, 122, 86, 255), w=5)
    elif kind == "under":
        p.rect(0, 0, W, H, (60, 50, 70, 255), ow=0)
        p.rect(0, 1500, W, H, (222, 150, 110, 255), ow=0)
        for y in range(1500, H, 90):
            p.line([(0, y), (W, y)], fill=(196, 122, 86, 255), w=5)
        _cloth(p, 0, 330, full_height=True)
        # legs: shorts / skirts / sandals
        for x, col, skin in ((150, (60, 130, 220, 255), SKINS["a"]), (420, (255, 205, 60, 255), SKINS["b"]),
                             (690, (250, 130, 110, 255), SKINS["a"]), (950, (90, 180, 90, 255), SKINS["c"])):
            p.rect(x - 95, 330, x + 95, 760, col, r=30)
            p.rect(x - 75, 720, x - 15, 1480, skin, r=26)
            p.rect(x + 15, 720, x + 75, 1480, skin, r=26)
            p.rect(x - 95, 1460, x - 5, 1510, (120, 80, 50, 255), r=20)
            p.rect(x + 5, 1460, x + 95, 1510, (120, 80, 50, 255), r=20)
    elif kind == "kitchen":
        p.rect(0, 0, W, H, (200, 236, 222, 255), ow=0)
        for x in range(0, W, 180):
            p.rect(x + 10, 120, x + 170, 520, (150, 210, 190, 255))
            p.ell(x + 150, 330, 10, 10, (240, 240, 240, 255))
        p.rect(0, 900, W, 1300, (240, 240, 235, 255))
        p.rect(0, 880, W, 930, (180, 140, 100, 255))
        p.rect(0, 1300, W, H, (250, 236, 200, 255), ow=0)
        for y in range(1300, H, 120):
            for x in range((y // 120) % 2 * 120, W, 240):
                p.rect(x, y, x + 120, y + 120, (240, 218, 170, 255), ow=0)
    elif kind == "spot":
        c = color or (40, 30, 90, 255)
        p.rect(0, 0, W, H, c, ow=0)
        p.poly([(W / 2 - 90, 0), (W / 2 + 90, 0), (W / 2 + 380, 1500), (W / 2 - 380, 1500)],
               tuple(min(255, v + 45) for v in c[:3]) + (255,), ow=0)
        p.ell(W / 2, 1500, 380, 80, tuple(min(255, v + 70) for v in c[:3]) + (255,), ow=0)
    im = p.done()
    if kind == "terrace_table":
        tb = table_front()
        im.alpha_composite(tb, (0, 1150))
    return im


def _cloth(p, y0, y1, full_height=False):
    yel, wh = (255, 214, 90, 255), (255, 250, 236, 255)
    p.rect(-10, y0, W + 10, y1, wh, ow=0)
    s = 60
    for y in range(y0, y1, s):
        for x in range(0, W, s):
            if ((x // s) + (y // s)) % 2 == 0:
                p.rect(x, y, x + s, y + s, yel, ow=0)
    for y in range(y0, y1, s * 2):
        p.rect(-10, y, W + 10, y + s // 2, (255, 230, 150, 120), ow=0)
    # scalloped edge
    for x in range(0, W + 60, 60):
        p.ell(x, y1, 32, 22, yel)
    p.line([(0, y1 - 22), (W, y1 - 22)], fill=yel, w=10)


@lru_cache(maxsize=None)
def table_front():
    p = P(W, 770)
    p.rect(-10, 0, W + 10, 40, (196, 136, 82, 255))
    _cloth(p, 40, 520)
    p.rect(150, 520, 200, 770, (176, 120, 70, 255))
    p.rect(W - 200, 520, W - 150, 770, (176, 120, 70, 255))
    return p.done()


# ---------------------------------------------------------------- animation helpers
def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    x = max(0.0, min(1.0, x))
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def pop(img, t, t0, dur=0.22):
    """Scale-in with overshoot starting at t0. Returns None before t0."""
    if t < t0:
        return None
    k = ease_out_back((t - t0) / dur)
    if k >= 0.999 and k <= 1.001:
        return img
    w, h = max(1, int(img.width * k)), max(1, int(img.height * k))
    return img.resize((w, h), Image.BILINEAR)


def bob(t, amp=8, speed=6.0, phase=0):
    return amp * math.sin(t * speed + phase)


class E:
    """Placed element: image, centre-x, bottom-y."""

    def __init__(self, img, x, y, sfx=None):
        self.img, self.x, self.y, self.sfx = img, x, y, sfx


def blink_eyes(t, base="open", period=2.7, off=0.0):
    return "closed" if ((t + off) % period) < 0.12 and base in ("open", "beg") else base


# Each shot returns (background, [E...]). sfx are declared separately in SHOT_SFX.
def S_hook(t, d):
    els = [E(dog("head", blink_eyes(t, "beg"), "smile", 0, False, 2.2), 540, 1500 + bob(t, 6))]
    f = fork(1.2)
    y = 120 + min(1, t / 0.6) * 320
    els.insert(0, E(f.rotate(25 * math.sin(t * 5), expand=True, resample=Image.BICUBIC), 250, y + 380))
    return bg("burst", ((250, 150, 60, 255), (255, 175, 90, 255))), els


def S_not_hunger(t, d):
    els = [E(dog("sit", blink_eyes(t), "smile", 0, False, 1.25), 600, 1560 + bob(t, 4))]
    b = pop(bubble(1.0), t, 0.05)
    if b:
        els.append(E(b, 380, 720))
        bw = pop(bowl(True, 0.85), t, 0.15)
        if bw:
            els.append(E(bw, 370, 560))
        x = pop(xmark(1.0), t, 0.5)
        if x:
            els.append(E(x, 370, 600))
    return bg("stripes", ((90, 170, 250, 255), (110, 185, 255, 255))), els


def S_mystery(t, d):
    els = [E(dog("sit", "worry", "o", 0, False, 1.3), 540, 1560)]
    q = pop(qmark(1.3), t, 0.2)
    if q:
        els.append(E(q.rotate(10 * math.sin(t * 4), resample=Image.BICUBIC), 540, 640 + bob(t, 12, 4)))
    return bg("spot", (40, 30, 90, 255)), els


def S_sunday(t, d):
    els = [E(dog("sit", blink_eyes(t), "smile", 0, False, 0.75), 860, 1830)]
    c = pop(calendar("DOM", "7", 1.1), t, 0.1)
    if c:
        els.append(E(c, 540, 650))
    return bg("terrace_table"), els


def family_table(t, eyes="open", dog_el=None, chicken_on=True, who=("grandma", "dad", "sofia", "mom", "harry")):
    els = []
    xs = [110, 330, 540, 750, 970]
    for i, w in enumerate(who):
        els.append(E(person(w, False, "down", 0.78, eyes), xs[i], 1330 + bob(t, 3, 5, i)))
    return els


def table_overlay(chicken_on=True):
    els = [E(table_front(), 540, 1920)]
    if chicken_on:
        els.append(E(chicken(1.0), 540, 1370))
    for x in (160, 380, 700, 920):
        els.append(E(_plate(), x, 1300))
    return els


@lru_cache(maxsize=None)
def _plate():
    p = P(200, 80, 100, 40)
    p.ell(0, 0, 90, 26, WHITE)
    p.ell(0, -2, 64, 16, (235, 235, 240, 255), ow=0)
    return p.done()


def S_family(t, d):
    els = family_table(t) + table_overlay()
    return bg("terrace"), els


def S_knee(t, d):
    e = dog("sit", "beg", "smile", 0, False, 1.05)
    return bg("under"), [E(e, 420 + 140 * math.sin(t * 1.6), 1700)]


def S_fork_eyes(t, d):
    look = math.sin(t * 5)
    els = [E(fork(1.1), 540 + 330 * look, 800), E(dog("head", "beg", "smile", round(look * 1.4, 1), False, 2.1), 540, 1650)]
    return bg("stripes", ((255, 196, 60, 255), (255, 210, 90, 255))), els


def S_dad_send(t, d):
    els = [E(person("dad", True, "point", 1.05), 380, 1700), E(bed_only(), 900, 1880),
           E(dog("sit", "worry", "sad", 0, False, 0.75), 780 + min(1, t / 0.8) * 120, 1820)]
    return bg("terrace"), els


@lru_cache(maxsize=None)
def bed_only():
    p = P(460, 200, 230, 100)
    p.ell(0, 30, 210, 70, (64, 160, 140, 255))
    p.ell(0, 14, 170, 46, (98, 196, 170, 255), ow=0)
    return p.done()


def S_dad_no(t, d):
    els = [E(person("dad", False, "cross", 1.4), 540, 1500)]
    x = pop(badge("¡NADA!", 1.0, (235, 60, 60, 255)), t, 0.25)
    if x:
        els.append(E(x, 540, 560))
    return bg("burst", ((70, 130, 230, 255), (90, 150, 245, 255))), els


def S_30s(t, d):
    a = min(360, t / d * 360 * 1.0)
    els = [E(clock(round(a / 6) * 6, 0, 1.6, True), 540, 1050)]
    b = pop(badge("30 s", 1.0, (255, 255, 255, 255), (235, 60, 60, 255)), t, 0.1)
    if b:
        els.append(E(b, 540, 520))
    return bg("dots", ((255, 210, 60, 255), (255, 225, 110, 255))), els


def S_back(t, d):
    k = min(1, t / 0.35)
    y = 1860 + (1 - ease_out_back(k)) * 500
    els = family_table(t) + table_overlay()
    els.append(E(dog("sit", "beg", "tongue", 0, False, 0.75), 540, y))
    return bg("terrace"), els


def S_grandma(t, d):
    els = [E(person("grandma", False, "give", 1.35), 470, 1450)] + [E(table_front(), 540, 2250)]
    br = pop(bread(0.9), t, 0.3)
    if br:
        els.append(E(br, 740, 1720))
    els.append(E(dog("head", "beg", "tongue", 0, False, 0.9), 820, 1990))
    return bg("terrace"), els


def S_bread_under(t, d):
    k = min(1, t / 0.5)
    els = [E(bread(0.8), 560, 380 + k * 520), E(dog("sit", "beg", "tongue", 0, False, 1.1), 540, 1760)]
    return bg("under"), els


def S_harry(t, d):
    els = [E(person("harry", False, "give", 1.35), 470, 1450)] + [E(table_front(), 540, 2250)]
    k = max(0, min(1, (t - 0.3) / 0.6))
    if t > 0.3:
        els.append(E(potato(1.0).rotate(k * 300, expand=True), 760, 1400 + k * 500))
    return bg("burst", ((90, 200, 120, 255), (110, 215, 140, 255))), els


def S_dad_skin(t, d):
    els = [E(person("dad", False, "give", 1.35), 470, 1450), E(table_front(), 540, 2250)]
    m = pop(morsel(1.4), t, 0.25)
    if m:
        els.append(E(m, 740, 1700))
    els.append(E(dog("head", "beg", "tongue", 0, False, 0.95), 820, 2000))
    return bg("terrace"), els


def S_glutton(t, d):
    els = family_table(t) + table_overlay()
    els.append(E(dog("sit", "beg", "tongue", 0, False, 0.75), 540, 1860))
    b = pop(badge("GLOTÓN", 0.9, (250, 90, 60, 255)), t, 0.3)
    if b:
        els.append(E(b, 540, 520))
    return bg("terrace"), els


def S_bowl_empty(t, d):
    els = [E(clock(300, 300, 0.9), 540, 640), E(bowl(False, 1.3), 540, 1640),
           E(dog("sit", blink_eyes(t), "smile", 0, False, 0.9), 820, 1680)]
    b = pop(badge("-10 min", 0.8, (255, 255, 255, 255), (40, 40, 40, 255)), t, 0.3)
    if b:
        els.append(E(b, 300, 900))
    return bg("kitchen"), els


def S_why(t, d):
    els = [E(dog("sit", "worry", "o", 0, False, 1.25), 540, 1600)]
    for i, (x, y) in enumerate(((260, 700), (820, 640), (540, 480))):
        q = pop(qmark(0.8 + 0.2 * (i == 2)), t, 0.1 + i * 0.12)
        if q:
            els.append(E(q, x, y + bob(t, 10, 5, i)))
    return bg("spot", (60, 30, 110, 255)), els


def S_nose(t, d):
    s = 1.0 + 0.04 * math.sin(t * 9)
    els = [E(nose_big(1.3 * s), 540, 1300)]
    for i, x in enumerate((300, 540, 780)):
        sm = pop(smell(0.9), t, 0.2 + 0.1 * i)
        if sm:
            els.append(E(sm, x, 650 + bob(t, 14, 6, i)))
    b = pop(badge("x50", 1.2, (255, 220, 50, 255), INK), t, 0.6)
    if b:
        els.append(E(b, 540, 1650))
    return bg("burst", ((40, 80, 200, 255), (60, 100, 220, 255))), els


def S_kibble(t, d):
    els = [E(dog("sit", "sleep", "sad", 0, False, 1.2), 400, 1600), E(bowl(True, 1.0), 800, 1620)]
    for i in range(3):
        c = pop(calendar("", "", 0.42, False), t, 0.1 + i * 0.12)
        if c:
            els.append(E(c, 240 + i * 300, 560))
    return bg("stripes", ((170, 170, 180, 255), (185, 185, 195, 255))), els


def S_chicken_sniff(t, d):
    els = [E(table_front(), 540, 2150), E(chicken(1.5), 540, 1480)]
    els.append(E(smell(0.8, (255, 240, 200, 230)), 540, 1150 + bob(t, 10)))
    els.append(E(dog("head", "closed", "o", 0, False, 1.2), 540, 2050))
    return bg("terrace"), els


def S_best_smell(t, d):
    els = [E(dog("head", "beg", "tongue", 0, False, 2.1), 540, 1600 + bob(t, 6, 8))]
    for i, (x, y) in enumerate(((200, 700), (880, 620), (160, 1100), (920, 1120))):
        h = pop(heart(0.9), t, 0.1 + 0.1 * i)
        if h:
            els.append(E(h, x, y + bob(t, 14, 6, i)))
    return bg("burst", ((250, 140, 60, 255), (255, 165, 85, 255))), els


def S_worst(t, d):
    sh = 14 * math.sin(t * 60) * max(0, 1 - t / 0.4)
    els = [E(dog("sit", "worry", "wobbly", 0, True, 1.15), 540 + sh, 1700)]
    for i, x in enumerate((260, 820)):
        q = pop(qmark(0.9), t, 0.2 + i * 0.15)
        if q:
            els.append(E(q, x, 760 + bob(t, 10, 5, i)))
    return bg("under"), els


def S_cal_give(who, label, gives=True, bgc=None):
    def f(t, d):
        els = []
        if gives:
            els.append(E(person(who, False, "give", 1.2), 420, 1250))
        els.append(E(table_front(), 540, 2050) if gives else E(table_front(), 540, 2350))
        if gives:
            m = pop(morsel(1.2), t, 0.3)
            if m:
                els.append(E(m, 720, 1500))
        els.append(E(dog("sit", "beg" if gives else "worry", "tongue" if gives else "sad", 0, False, 0.85), 800, 1880))
        c = pop(calendar(label, "", 0.75), t, 0.05)
        if c:
            els.append(E(c, 200, 420))
        if not gives:
            x = pop(xmark(0.9), t, 0.35)
            if x:
                els.append(E(x, 540, 1100))
        return bg("terrace"), els
    return f


def S_slot(t, d):
    spinning = t < d * 0.6
    syms = ("pollo", "x", "hueso") if spinning and int(t * 12) % 2 else ("x", "hueso", "pollo")
    if not spinning:
        syms = ("pollo", "pollo", "pollo")
    els = [E(slot(syms, 1.6, 0), 540, 1480)]
    if not spinning:
        for i, (x, y) in enumerate(((180, 520), (900, 560), (540, 380))):
            s = pop(sparkle(1.0), t, d * 0.6 + 0.05 * i)
            if s:
                els.append(E(s, x, y))
    return bg("burst", ((60, 190, 150, 255), (80, 205, 165, 255))), els


def S_think(t, d):
    els = [E(dog("sit", "beg", "smile", 0, False, 1.25), 600, 1640)]
    b = pop(bubble(1.1), t, 0.05)
    if b:
        els.append(E(b, 400, 800))
        m = pop(morsel(1.5), t, 0.2)
        if m:
            els.append(E(m, 360, 640))
        q = pop(qmark(0.45), t, 0.35)
        if q:
            els.append(E(q, 520, 650))
    return bg("stripes", ((150, 90, 230, 255), (165, 110, 240, 255))), els


def S_stress(t, d):
    sh = 4 * math.sin(t * 40)
    lvl = min(0.95, 0.4 + t / d * 0.6)
    els = [E(dog("sit", "worry", "wobbly", sh / 8, True, 1.1), 540 + sh, 1720),
           E(thermometer(round(lvl, 2), 1.0), 900, 1200), E(clock(int(t * 600) % 360, 90, 0.6), 180, 1000)]
    return bg("under"), els


def S_trainer(t, d):
    els = [E(person("trainer", True, "point", 1.2), 420, 1780)]
    c = pop(checklist(1.0), t, 0.3)
    if c:
        els.append(E(c, 820, 900))
    return bg("dots", ((255, 220, 170, 255), (255, 232, 195, 255))), els


def S_same_time(t, d):
    els = [E(person("trainer", True, "down", 1.2), 360, 1780), E(clock(0, 0, 1.0), 800, 900)]
    c = pop(check(1.0), t, 0.4)
    if c:
        els.append(E(c, 800, 1250))
    return bg("dots", ((255, 220, 170, 255), (255, 232, 195, 255))), els


def S_before(t, d):
    els = [E(person("sofia", False, "give", 1.2), 420, 1250), E(table_front(), 540, 2050)]
    m = pop(morsel(1.2), t, 0.25)
    if m:
        els.append(E(m, 720, 1500))
    els.append(E(dog("sit", "beg", "tongue", 0, False, 0.85), 800, 1880))
    b = pop(badge("ANTES", 0.8, (60, 190, 120, 255)), t, 0.1)
    if b:
        els.append(E(b, 300, 500))
    return bg("terrace"), els


def S_to_bed(t, d):
    els = [E(dog("bed", "closed", "smile", 0, False, 1.5), 540, 1600)]
    b = pop(badge("A SU CAMA", 0.8, (64, 160, 140, 255)), t, 0.1)
    if b:
        els.append(E(b, 540, 700))
    return bg("stripes", ((120, 210, 190, 255), (140, 220, 200, 255))), els


def S_after(t, d):
    els = [E(person("sofia", False, "give", 1.2), 420, 1250), E(table_front(), 540, 2050)]
    m = pop(morsel(1.2), t, 0.25)
    if m:
        els.append(E(m, 720, 1500))
    els.append(E(dog("sit", "beg", "tongue", 0, False, 0.85), 800, 1880))
    b = pop(badge("DESPUÉS", 0.8, (60, 190, 120, 255)), t, 0.1)
    if b:
        els.append(E(b, 300, 500))
    return bg("terrace"), els


def S_anticipate(t, d):
    els = [E(dog("sit", blink_eyes(t), "smile", 0, False, 1.2), 380, 1650)]
    c = pop(clock(int(t * 90), 60, 1.0), t, 0.1)
    if c:
        els.append(E(c, 780, 900 + bob(t, 8, 3)))
    return bg("stripes", ((255, 200, 60, 255), (255, 215, 95, 255))), els


def S_calm(t, d):
    lvl = max(0.15, 0.7 - t / d * 0.6)
    els = [E(dog("sit", "closed", "smile", 0, False, 1.1), 540, 1720), E(thermometer(round(lvl, 2), 1.0), 900, 1200)]
    return bg("under"), els


def S_sleep_bed(t, d):
    els = family_table(t) + table_overlay()
    els.append(E(dog("bed", "sleep", "smile", 0, False, 0.75), 860, 1900))
    z = pop(zzz(0.8), t, 0.3)
    if z:
        els.append(E(z, 900, 1650 + bob(t, 10, 3)))
    return bg("terrace"), els


def S_plead(t, d):
    els = [E(person("sofia", False, "down", 1.3), 330, 1500), E(table_front(), 540, 2300),
           E(dog("head", "beg", "smile", -1, False, 1.3), 760, 1900 + bob(t, 10, 7))]
    return bg("terrace"), els


def S_end(t, d):
    els = [E(dog("sit", "beg", "smile", 0, False, 1.3), 540, 1560)]
    q = pop(qmark(1.4), t, 0.15)
    if q:
        els.append(E(q, 540, 620 + bob(t, 12, 4)))
    return bg("spot", (40, 30, 90, 255)), els


# one list of shot functions per voice line (split evenly at word boundaries)
LINE_SHOTS = [
    [S_hook, S_not_hunger, S_mystery],
    [S_sunday, S_family, S_knee],
    [S_fork_eyes],
    [S_dad_send, S_dad_no],
    [S_30s, S_back],
    [S_grandma, S_bread_under],
    [S_harry, S_dad_skin],
    [S_glutton, S_bowl_empty],
    [S_why],
    [S_nose],
    [S_kibble],
    [S_chicken_sniff, S_best_smell],
    [S_worst],
    [S_cal_give("grandma", "DOM 1")],
    [S_cal_give(None, "DOM 2", gives=False)],
    [S_cal_give("dad", "DOM 3")],
    [S_slot],
    [S_think],
    [S_stress],
    [S_trainer],
    [S_same_time],
    [S_before, S_to_bed, S_after],
    [S_anticipate],
    [S_calm],
    [S_sleep_bed],
    [S_plead],
    [S_end],
]

# sfx cue per shot function name: (kind, offset_sec)
SHOT_SFX = {
    "S_hook": [("boom", 0.0)], "S_not_hunger": [("pop", 0.05), ("buzz", 0.5)], "S_mystery": [("mystery", 0.1)],
    "S_sunday": [("pop", 0.1)], "S_knee": [], "S_fork_eyes": [], "S_dad_send": [("whistle", 0.0)],
    "S_dad_no": [("buzz", 0.25)], "S_30s": [("tick", 0.0)], "S_back": [("boing", 0.05)],
    "S_grandma": [("pop", 0.3)], "S_bread_under": [("chomp", 0.5)], "S_harry": [("drop", 0.8)],
    "S_dad_skin": [("pop", 0.25), ("chomp", 0.9)], "S_glutton": [("pop", 0.3)], "S_bowl_empty": [("pop", 0.3)],
    "S_why": [("mystery", 0.1)], "S_nose": [("sniff", 0.1), ("ding", 0.6)], "S_kibble": [("pop", 0.1)],
    "S_chicken_sniff": [("sniff", 0.2)], "S_best_smell": [("sparkle", 0.1)], "S_worst": [("scratch", 0.0)],
    "S_slot": [("slot", 0.0)], "S_think": [("pop", 0.05)], "S_stress": [("heart", 0.0)],
    "S_trainer": [("pop", 0.3)], "S_same_time": [("ding", 0.4)], "S_before": [("pop", 0.25)],
    "S_to_bed": [("pop", 0.1)], "S_after": [("ding", 0.25)], "S_anticipate": [("tick", 0.0)],
    "S_calm": [], "S_sleep_bed": [("pop", 0.3)], "S_plead": [], "S_end": [("mystery", 0.15)],
}

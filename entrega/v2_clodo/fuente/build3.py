"""Version espagnole animée : « La cara de culpable de Clodo »."""
import json, math, random, subprocess, sys, wave
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import art
from art import E, R, P, line, arc, star, OL, WHITE, YEL

S, OUT = sys.argv[1], sys.argv[2]
ONLY = sys.argv[3] if len(sys.argv) > 3 else None      # "stills" = images de contrôle
art.FONT_PATH = f"{S}/v2/fonts/Nunito.ttf"
SR, FPS, W, H = 44100, 30, 1080, 1920
random.seed(3); np.random.seed(3)

# ======================================================= voix + timeline
words = json.load(open(f"{S}/v2/voz/words.json"))
def load_mp3(p):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

lines, voice_at = [], {}
t = 0.25
for i, wl in enumerate(words):
    a = load_mp3(f"{S}/v2/voz/l{i:02d}.mp3")
    st = max(0, wl[0][1] - 0.03); en = min(len(a) / SR, wl[-1][1] + wl[-1][2] + 0.08)
    lines.append({"audio": a[int(st * SR):int(en * SR)], "words": [(w, o - st, d) for w, o, d in wl]})
    voice_at[i] = t
    gap = 0.22 if lines[-1]["words"][-1][0][-1:] in ".?" or i in (0, 9, 16, 20) else 0.08
    t += len(lines[-1]["audio"]) / SR + gap
TOTAL = t + 0.9

def wt(li, word):
    """Instant (absolu) où le mot commence dans la réplique li."""
    for w, o, d in lines[li]["words"]:
        if w.lower().startswith(word.lower()):
            return voice_at[li] + o
    raise KeyError((li, word))

def lt(li): return voice_at[li]

# ======================================================= fonds
def F(size, weight="Black"):
    f = ImageFont.truetype(art.FONT_PATH, size); f.set_variation_by_name(weight); return f

def grad(c1, c2, h=H):
    y = np.linspace(0, 1, h)[:, None, None]
    return Image.fromarray(np.repeat((np.array(c1) * (1 - y) + np.array(c2) * y).astype(np.uint8), W, 1))

@lru_cache(None)
def sunburst(c1, c2):
    im = Image.new("RGB", (W, H), c1); d = ImageDraw.Draw(im)
    cx, cy, n = W / 2, H * 0.45, 24
    for k in range(0, n, 2):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        d.polygon([(cx, cy), (cx + 3000 * math.cos(a0), cy + 3000 * math.sin(a0)),
                   (cx + 3000 * math.cos(a1), cy + 3000 * math.sin(a1))], fill=c2)
    return im

@lru_cache(None)
def garden(night=False):
    """Jardin : ciel de coucher de soleil, palissade, guirlande d'ampoules, sol en dalles."""
    big = Image.new("RGB", (W * 2, H * 2)); d = ImageDraw.Draw(big)
    sky = grad((255, 196, 120), (250, 130, 140), H * 2) if not night else grad((20, 24, 60), (60, 40, 100), H * 2)
    big.paste(sky.resize((W * 2, H * 2)))
    if night:
        for _ in range(60):
            x, y = random.randint(0, W * 2), random.randint(0, 1500)
            E(d, (x - 5, y - 5, x + 5, y + 5), (255, 255, 220), 0)
        E(d, (1500, 260, 1800, 560), (255, 245, 200), 12)
        E(d, (1440, 220, 1720, 500), (40, 36, 80), 0)
    else:
        E(d, (1350, 900, 1950, 1500), (255, 230, 150), 0)
    d.rectangle((0, 1600, W * 2, H * 2), fill=(196, 160, 120) if not night else (70, 60, 90))
    for y in range(1600, H * 2, 170):
        d.line((0, y, W * 2, y), fill=OL, width=6)
        off = 0 if (y // 170) % 2 else 160
        for x in range(off, W * 2, 320):
            d.line((x, y, x, y + 170), fill=OL, width=6)
    fence = (215, 160, 100) if not night else (90, 70, 90)
    for x in range(-40, W * 2, 190):
        P(d, [(x, 1650), (x, 1040), (x + 85, 980), (x + 170, 1040), (x + 170, 1650)], fence, 10)
    R(d, (-20, 1120, W * 2 + 20, 1180), 10, tuple(int(c * 0.85) for c in fence))
    R(d, (-20, 1440, W * 2 + 20, 1500), 10, tuple(int(c * 0.85) for c in fence))
    for bx, by, r in ((80, 1520, 210), (330, 1560, 170), (1880, 1520, 220), (2100, 1570, 160)):
        E(d, (bx - r, by - r, bx + r, by + r), (90, 170, 80) if not night else (40, 80, 60))
    cols = [(255, 90, 90), (255, 210, 60), (90, 200, 255), (130, 230, 120), (240, 130, 230)]
    for row, (y0, sag) in enumerate(((330, 160), (620, 120))):
        pts = [(x, y0 + sag * math.sin(math.pi * ((x % 1080) / 1080))) for x in range(0, W * 2 + 1, 20)]
        d.line(pts, fill=OL, width=8)
        for k, x in enumerate(range(60 + row * 50, W * 2, 135)):
            y = y0 + sag * math.sin(math.pi * ((x % 1080) / 1080)) + 18
            c = cols[(k + row) % 5]
            R(d, (x - 12, y - 10, x + 12, y + 14), 5, (90, 90, 90), 6)
            E(d, (x - 24, y + 8, x + 24, y + 66), c, 8)
    return art.fin(big)

@lru_cache(None)
def lab():
    big = Image.new("RGB", (W * 2, H * 2), (225, 245, 238)); d = ImageDraw.Draw(big)
    for y in range(0, 2500, 110):
        d.line((0, y, W * 2, y), fill=(185, 215, 205), width=6)
        for x in range((y // 110 % 2) * 110, W * 2, 220):
            d.line((x, y, x, y + 110), fill=(185, 215, 205), width=6)
    d.rectangle((0, 2450, W * 2, H * 2), fill=(200, 200, 210))
    d.line((0, 2450, W * 2, 2450), fill=OL, width=10)
    R(d, (140, 1300, 560, 2450), 20, (90, 150, 220))
    E(d, (470, 1860, 520, 1910), YEL, 8)
    return art.fin(big)

@lru_cache(None)
def city():
    big = Image.new("RGB", (W * 2, H * 2)); big.paste(grad((140, 200, 245), (210, 235, 255), H * 2).resize((W * 2, H * 2)))
    d = ImageDraw.Draw(big)
    for cx, cy in ((360, 380), (1600, 260)):
        for dx, dy, r in ((0, 0, 90), (90, -30, 110), (190, 10, 85)):
            E(d, (cx + dx - r, cy + dy - r * 0.7, cx + dx + r, cy + dy + r * 0.7), WHITE)
    random.seed(11)
    for k, x in enumerate(range(-60, W * 2, 170)):
        h = random.randint(700, 1500) if k != 6 else 1900
        R(d, (x, 2500 - h, x + 160, 2550), 6, (110, 130, 175) if k % 2 else (90, 110, 160))
        if k == 6:
            P(d, [(x + 40, 2500 - h), (x + 80, 2500 - h - 250), (x + 120, 2500 - h)], (90, 110, 160))
        for wy in range(2500 - h + 60, 2450, 110):
            for wx in (x + 30, x + 95):
                R(d, (wx, wy, wx + 35, wy + 55), 4, (250, 230, 140) if random.random() < .4 else (180, 200, 230), 0)
    R(d, (1700, 1500, 1790, 2550), 10, (100, 180, 160))
    E(d, (1690, 1380, 1800, 1500), (100, 180, 160))
    line(d, [(1790, 1450), (1880, 1250)], 30, (100, 180, 160))
    P(d, [(1860, 1260), (1900, 1180), (1920, 1270)], (255, 200, 60), 8)
    d.rectangle((0, 2550, W * 2, H * 2), fill=(170, 170, 180))
    d.line((0, 2550, W * 2, 2550), fill=OL, width=10)
    return art.fin(big)

@lru_cache(None)
def spotlight():
    im = Image.new("RGB", (W, H), (40, 28, 62)); d = ImageDraw.Draw(im, "RGBA")
    d.polygon([(W / 2 - 120, 0), (W / 2 + 120, 0), (W / 2 + 480, 1500), (W / 2 - 480, 1500)], fill=(255, 255, 255, 28))
    d.ellipse((W / 2 - 480, 1380, W / 2 + 480, 1620), fill=(255, 255, 255, 28))
    E(d, (W / 2 - 430, 330, W / 2 + 430, 1190), (90, 70, 130, 120), 0)
    return im

# ======================================================= composition
def scale(im, h):
    k = h / im.height
    return im.resize((max(1, int(im.width * k)), max(1, int(h))), Image.LANCZOS)

_cache = {}
def put(img, spr, cx, by, h, pop=1.0, key=None, flip=False):
    """Colle un sprite, bas-centre en (cx, by), hauteur h (x pop pour l'animation)."""
    hh = h * pop
    k = (key or id(spr), int(hh), flip)
    s = _cache.get(k)
    if s is None:
        s = scale(spr, hh)
        if flip: s = s.transpose(Image.FLIP_LEFT_RIGHT)
        if key and len(_cache) < 400: _cache[k] = s
    img.paste(s, (int(cx - s.width / 2), int(by - s.height)), s)

def popf(x, d=0.22):
    """Animation d'apparition avec rebond."""
    if x <= 0: return 0.01
    if x >= d: return 1.0
    u = x / d
    return max(0.01, 1 + 1.7 * (u - 1) ** 3 + 0.7 * (u - 1) ** 2) if u < 1 else 1.0

def bob(now, f=3.0, a=0.015): return 1 + a * math.sin(now * f * 2 * math.pi)

SPR = {}
def spr(kind, *a, **k):
    key = (kind, a, tuple(sorted(k.items())))
    if key not in SPR:
        SPR[key] = getattr(art, kind)(*a, **k)
    return SPR[key], key

def P_(img, kind, args, cx, by, h, pop=1.0, flip=False, **kw):
    s, key = spr(kind, *args, **kw)
    put(img, s, cx, by, h, pop, key, flip)

# ======================================================= scènes
def zzz(d, now, x, y):
    for k in range(3):
        u = (now * 0.8 + k / 3) % 1
        d.text((x + 40 * k + 30 * u, y - 140 * u - 40 * k), "z", font=F(60 + 15 * k), fill=WHITE,
               stroke_width=6, stroke_fill=OL, anchor="mm")

def sc_hook_a(img, now, s):
    P_(img, "dog", ("clodo", "happy"), W / 2, 1500, 820, popf(now - s), )

def sc_hook_b(img, now, s):
    P_(img, "dog", ("clodo", "guilty"), W / 2, 1500, 820, popf(now - s))

def sc_hook_c(img, now, s):
    P_(img, "dog", ("clodo", "guilty"), W / 2 - 60, 1560, 640)
    P_(img, "bubble", ("drum",), W / 2 + 200, 900, 430, popf(now - s))

def sc_eye(img, now, s):
    e = art.eye_big()
    put(img, e, W / 2, 1300 + 0, 900, popf(now - s, 0.3), key="eye")

def family_row(img, now, expr="sing", look=(0, 0)):
    b = bob(now, 2.2, 0.012)
    P_(img, "person", ("torchon", expr, "down", look), 175, 1330, 600 * b)
    P_(img, "person", ("louise", expr, "down", look), 375, 1330, 580 * b)
    P_(img, "person", ("maminova", expr, "down", look), 600, 1330, 640 / b)
    P_(img, "person", ("voldemort", expr, "down", look), 860, 1330, 640 * b)
    P_(img, "person", ("courgette", expr, "down", look), 210, 1520, 420)

def table(img, y, h=200, x0=180, x1=900):
    d = ImageDraw.Draw(img)
    R(d, (x0, y, x1, y + h), 8, WHITE)
    for k in range(x0 + 30, x1, 60):
        d.rectangle((k, y + 5, k + 28, y + h - 5), fill=(120, 190, 240))
    d.rounded_rectangle((x0, y, x1, y + h), 8, outline=OL, width=6)

def sc_party(img, now, s):
    family_row(img, now, "sing")
    table(img, 1290, 220, 330, 980)
    P_(img, "cake", (), 520, 1300, 260, popf(now - s - 0.3))
    P_(img, "chicken", (True,), 800, 1300, 190)
    d = ImageDraw.Draw(img)
    for k in range(3):
        u = (now * 0.5 + k / 3) % 1
        x = 300 + k * 260 + 30 * math.sin(now * 3 + k)
        d.text((x, 700 - 300 * u), "♪", font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90),
               fill=WHITE, stroke_width=6, stroke_fill=OL, anchor="mm")
    R(d, (620, 1640, 960, 1760), 50, (170, 110, 60))
    P_(img, "dog", ("clodo", "sleep"), 790, 1720, 300)
    zzz(d, now, 900, 1500)

def sc_chicken(img, now, s, vanish_at):
    table(img, 1150, 700, -20, W + 20)
    gone = now >= vanish_at
    P_(img, "chicken", (not gone,), W / 2, 1300, 470 if gone else 470 * 0.98 + 0.0)
    if gone and now - vanish_at < 0.5:
        d = ImageDraw.Draw(img)
        u = (now - vanish_at) / 0.5
        for cx in (260, 820):
            for k in range(6):
                a = k * math.pi / 3
                r = 40 + 140 * u
                E(d, (cx + r * math.cos(a) - 40 * (1 - u), 1060 + r * math.sin(a) - 40 * (1 - u),
                      cx + r * math.cos(a) + 40 * (1 - u), 1060 + r * math.sin(a) + 40 * (1 - u)), WHITE, 6)

def sc_hide(img, now, s):
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, H), fill=(52, 38, 44))
    R(d, (-20, -20, W + 20, 380), 0, WHITE)
    for k in range(0, W, 60):
        d.rectangle((k, 0, k + 28, 375), fill=(120, 190, 240))
    for k in range(0, W, 120):
        P(d, [(k, 375), (k + 60, 420), (k + 120, 375)], WHITE, 6)
    for x in (150, 300, 760, 920):
        R(d, (x, 700, x + 70, 1700), 20, (60, 110, 200))
        E(d, (x - 30, 1660, x + 100, 1720), WHITE)
    peek = min(1, (now - s) / 0.4)
    P_(img, "dog", ("clodo", "guilty"), W / 2, 1900 - 300 * peek, 780)
    R(d, (-10, 1640, W + 10, H + 10), 0, (170, 120, 80))

def sc_close(img, now, s, which="clodo", expr="guilty"):
    sp, key = spr("dog", which, expr)
    head = sp.crop((0, 0, sp.width, int(sp.height * 0.56)))
    put(img, head, W / 2, 1180 + 10 * math.sin(now * 2), 760 * popf(now - s, 0.25), key=(key, "head"))

def sc_shout(img, now, s, who, arms, x=430):
    sh = random.uniform(-6, 6) if int(now * 30) % 2 else 0
    P_(img, "person", (who, "angry", arms), x + sh, 1640, 1050)
    P_(img, "dog", ("clodo", "guilty"), 870, 1650, 360)

def sc_courgette(img, now, s):
    P_(img, "person", ("courgette", "grin", "phone"), 330, 1660, 900)
    screen = garden(False).crop((200, 700, 900, 1900)).copy()
    put(screen, spr("dog", "clodo", "guilty")[0], 350, 1150, 520, key="phone_clodo")
    ph = art.phone_frame(screen, 470, 820)
    p = popf(now - s, 0.3)
    put(img, ph, 790, 1350, 820 * p, key=None)
    if int(now * 2) % 2:
        d = ImageDraw.Draw(img)
        d.text((850, 610), "REC", font=F(44), fill=(240, 40, 50), anchor="mm")

def sc_dad(img, now, s, corner_at):
    if now < corner_at:
        sh = random.uniform(-7, 7) if int(now * 30) % 2 else 0
        P_(img, "person", ("voldemort", "angry", "bowl"), 430 + sh, 1660, 1080)
        P_(img, "dog", ("clodo", "guilty"), 880, 1650, 340)
    else:
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, W, H), fill=(215, 160, 100))
        P(d, [(0, 0), (W / 2, 260), (W / 2, H), (0, H)], (190, 135, 85), 0)
        line(d, [(W / 2, 260), (W / 2, 1500)], 10)
        d.rectangle((0, 1500, W, H), fill=(196, 160, 120)); line(d, [(0, 1500), (W, 1500)], 10)
        P_(img, "dog", ("clodo", "guilty"), W / 2, 1720, 520, popf(now - corner_at), flip=True)

def sc_clock(img, now, s):
    put(img, art.clock((now - s) * 700), W / 2, 1300, 700, popf(now - s))

def sc_ny(img, now, s):
    P_(img, "person", ("horowitz", "neutral", "point"), 470, 1700, 1000, popf(now - s))
    P_(img, "clapper", (), 830, 1120, 260, popf(now - s - 0.4))

def sc_lab(img, now, s, owner=None, dog_expr="happy", treat_pos=None, sci=False, owner_x=380):
    if owner:
        P_(img, "person", ("owner", owner, "point"), owner_x, 1690, 1000)
    if sci:
        P_(img, "person", ("horowitz", "neutral", "point"), 330, 1690, 1000)
    P_(img, "dog", ("negro", dog_expr), 820, 1700, 470)
    if treat_pos:
        P_(img, "treat", (), treat_pos[0], treat_pos[1], 70)

def sc_meters(img, now, s, lv_black, lv_white):
    P_(img, "dog", ("negro", "happy"), 290, 1700, 430)
    P_(img, "dog", ("blanco", "guilty" if lv_white > 0.5 else "neutral"), 790, 1700, 430)
    put(img, art.meter(lv_black), 290, 1220, 520)
    put(img, art.meter(lv_white), 790, 1220, 520)
    d = ImageDraw.Draw(img)
    for x in (230, 300, 340):
        E(d, (x, 1690, x + 22, 1706), (200, 140, 80), 4)

def sc_dog_burst(img, now, s, name, expr, halo=False):
    P_(img, "dog", (name, expr, halo), W / 2, 1500, 820, popf(now - s))

def sc_angry_faces(img, now, s, shrink_from):
    d = ImageDraw.Draw(img)
    for k, (who, x, y) in enumerate((("torchon", 220, 520), ("maminova", 540, 380), ("voldemort", 860, 520))):
        sp, key = spr("person", who, "angry", "down")
        head = sp.crop((0, 0, sp.width, int(sp.height * 0.47)))
        put(img, head, x + random.uniform(-4, 4), y + 160, 330 * popf(now - s - 0.12 * k), key=(key, "h"))
    k = 1 - 0.45 * min(1, max(0, (now - shrink_from) / 1.6))
    P_(img, "dog", ("clodo", "guilty"), W / 2, 1650, 680 * k)

def sofa(img, y=1250):
    d = ImageDraw.Draw(img)
    R(d, (40, y - 260, W - 40, y + 60), 60, (60, 160, 170))
    R(d, (0, y - 20, W, y + 210), 50, (50, 140, 150))
    R(d, (0, y - 160, 120, y + 210), 40, (50, 140, 150)); R(d, (W - 120, y - 160, W, y + 210), 40, (50, 140, 150))

def sc_sofa(img, now, s, shock_at):
    sofa(img)
    e = "shock" if now >= shock_at else "neutral"
    look = (0.6, 0.5)
    for who, x, h in (("torchon", 230, 560), ("maminova", 440, 600), ("voldemort", 700, 600), ("louise", 900, 540)):
        P_(img, "person", (who, e, "down", look), x, 1380, h)
    P_(img, "person", ("courgette", e, "phone", look), 560, 1500, 420)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(600, 1180), (420, 1900), (900, 1900)], fill=(200, 230, 255, 50))

def sc_video(img, now, s, wipe_from, grin_at):
    scr = garden(False).copy()
    phase = now >= wipe_from
    P_(scr, "person", ("voldemort", "grin" if now >= grin_at else "neutral", "wipe" if phase else "eat"), 420, 1700, 1000)
    hb = math.sin(now * 14) * 10 if phase else 0
    P_(scr, "dog", ("clodo", "guilty"), 850, 1720 + hb, 420)
    ph = art.phone_frame(scr.resize((540, 960)), 760, 1300)
    put(img, ph, W / 2, 1650, 1400 * popf(now - s, 0.3))

def sc_thought(img, now, s):
    P_(img, "dog", ("clodo", "neutral"), 420, 1560, 640)
    P_(img, "bubble", ("ball",), 700, 980, 430, popf(now - s))

def sc_angel(img, now, s):
    P_(img, "dog", ("clodo", "angel", True), W / 2, 1520, 900, popf(now - s))
    d = ImageDraw.Draw(img)
    for k, (x, y) in enumerate(((200, 600), (880, 520), (150, 1100), (930, 1050), (540, 330))):
        r = 30 + 15 * math.sin(now * 5 + k)
        star(d, x, y, r, (255, 240, 150))

# ---------------------------------------------------- liste des plans
BG = dict(burst_y=lambda: sunburst((255, 222, 140), (255, 210, 115)),
          burst_p=lambda: sunburst((170, 140, 230), (155, 125, 220)),
          burst_o=lambda: sunburst((245, 170, 100), (235, 155, 85)),
          burst_b=lambda: sunburst((150, 205, 245), (135, 192, 238)),
          burst_g=lambda: sunburst((200, 235, 170), (185, 225, 155)),
          burst_pk=lambda: sunburst((255, 190, 215), (250, 175, 205)),
          burst_v=lambda: sunburst((120, 90, 210), (105, 78, 195)),
          garden=lambda: garden(False), night=lambda: garden(True), lab=lab, city=city, spot=spotlight,
          blank=lambda: Image.new("RGB", (W, H), (52, 38, 44)))

exec(open(__file__.replace("build3.py", "shots3.py")).read())
starts = [s for s, *_ in SHOTS] + [TOTAL]

def shot_at(now):
    for k in range(len(SHOTS) - 1, -1, -1):
        if now >= SHOTS[k][0]: return k
    return 0

# ======================================================= sous-titres (1-2 mots, comme l'original)
HL = {"clodo", "maminova", "louise", "torchon", "courgette", "voldemort", "horowitz", "culpable", "culpables",
      "escondidas", "inocentes", "inocente", "galleta", "2009", "tiktok,", "tiktok", "inquietante"}
caps = []
for i in range(len(lines)):
    wl = lines[i]["words"]; at = voice_at[i]; k = 0
    while k < len(wl):
        g = [wl[k]]
        if k + 1 < len(wl) and len(wl[k][0]) + len(wl[k + 1][0]) <= 13: g.append(wl[k + 1])
        k += len(g)
        caps.append([at + g[0][1], at + g[-1][1] + g[-1][2], [x[0] for x in g]])
for a, b in zip(caps, caps[1:]):
    if b[0] - a[1] < 0.35: a[1] = b[0]

def clean(w): return w.lower().strip("¿?¡!.,;:")

def draw_caps(img, now):
    for s, e, ws in caps:
        if s <= now < e:
            p = popf(now - s, 0.1)
            d = ImageDraw.Draw(img)
            size = int(104 * (0.7 + 0.3 * p))
            f = F(size)
            txt = [w.strip(",;:") for w in ws]
            tw = sum(d.textlength(w + " ", font=f) for w in txt) - d.textlength(" ", font=f)
            if tw > 980:
                f = F(int(size * 980 / tw)); tw = 980
            x, y = (W - tw) / 2, 1230
            for w in txt:
                col = YEL if clean(w) in HL else WHITE
                d.text((x, y), w, font=f, fill=col, stroke_width=11, stroke_fill=OL, anchor="ls")
                x += d.textlength(w + " ", font=f)
            return

# ======================================================= rendu d'une image
def frame(now):
    k = shot_at(now)
    s, bg, fn, _ = SHOTS[k]
    e = starts[k + 1]
    img = BG[bg]().copy()
    fn(img, now, s)
    draw_caps(img, now)
    # caméra : léger zoom continu + punch sur les impacts
    z = 1 + 0.045 * min(1, (now - s) / max(0.5, e - s))
    for at, kind in [(sx, x) for sx, _, _, x in SHOTS] + EXTRA_SFX:
        if kind == "bass" and 0 <= now - at < 0.4:
            z += 0.08 * (1 - (now - at) / 0.4)
    if z > 1.001:
        cw, ch = W / z, H / z
        img = img.crop((int((W - cw) / 2), int((H - ch) * 0.45), int((W - cw) / 2 + cw), int((H - ch) * 0.45 + ch))).resize((W, H), Image.BILINEAR)
    return img

# ======================================================= audio
N = int(TOTAL * SR)
def env(n, a=0.005, d=0.3):
    x = np.arange(n) / SR; return np.minimum(1, x / a) * np.exp(-x / d)
def lp(x, f0, f1):
    y = np.zeros_like(x); s_ = 0.0; al = 1 - np.exp(-2 * np.pi * np.geomspace(f0, f1, len(x)) / SR)
    for k in range(len(x)):
        s_ += al[k] * (x[k] - s_); y[k] = s_
    return y
def tone(f, n): return np.sin(2 * np.pi * np.cumsum(f) / SR) if np.ndim(f) else np.sin(2 * np.pi * f * np.arange(n) / SR)
def sfx(kind):
    n = lambda s: int(SR * s)
    if kind == "whoosh":
        x = lp(np.random.randn(n(.4)), 300, 5000); return x * np.sin(np.linspace(0, np.pi, len(x))) ** 2 * 1.3
    if kind == "pop":
        m = n(.08); f = 350 + 900 * np.exp(-np.arange(m) / SR / .015); return tone(f, m) * env(m, .001, .025) * .45
    if kind == "bass":
        m = n(.8); f = 45 + 110 * np.exp(-np.arange(m) / SR / .06); return np.tanh(2.5 * tone(f, m)) * env(m, .002, .3) * .8
    if kind == "tick":
        out = np.zeros(n(1.6))
        for k in range(8):
            m = n(.05); s_ = n(.18 * k)
            out[s_:s_ + m] += np.sin(2 * np.pi * (2200 if k % 2 else 1600) * np.arange(m) / SR) * env(m, .0005, .01) * .5
        return out
    if kind == "shutter":
        m = n(.18); x = np.random.randn(m) * env(m, .0005, .02); x[n(.08):] += np.random.randn(m - n(.08)) * env(m - n(.08), .0005, .03)
        return x * .5
    if kind == "boing":
        m = n(.6); tt = np.arange(m) / SR; f = 180 + 120 * np.sin(2 * np.pi * 9 * tt) * np.exp(-tt / .3) + 200 * tt
        return tone(f, m) * env(m, .003, .3) * .4
    if kind == "poof":
        x = lp(np.random.randn(n(.35)), 2000, 300); return x * env(len(x), .005, .1) * 1.5
    if kind == "squish":
        m = n(.3); tt = np.arange(m) / SR; f = 300 + 400 * np.sin(2 * np.pi * 12 * tt)
        return (tone(f, m) * .3 + lp(np.random.randn(m), 1500, 600) * .6) * env(m, .01, .1)
    if kind == "chime":
        out = np.zeros(n(2.0))
        for k, f in enumerate((1046.5, 1318.5, 1568, 2093)):
            m = n(1.2); s_ = n(.09 * k); tt = np.arange(m) / SR
            out[s_:s_ + m] += (np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt)) * np.exp(-tt / .4) * .18
        return out
    raise ValueError(kind)

def build_audio():
    voice = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)
    def put_a(buf, at, x):
        s_ = int(at * SR); e_ = min(N, s_ + len(x))
        if 0 <= s_ < N: buf[s_:e_] += x[:e_ - s_]
    for i, at in voice_at.items(): put_a(voice, at, lines[i]["audio"])
    cache = {}
    for at, kind in [(sx, x) for sx, _, _, x in SHOTS] + EXTRA_SFX:
        if kind not in cache: cache[kind] = sfx(kind).astype(np.float32)
        put_a(fx, at, cache[kind])
    # musique originale : petite mélodie pizzicato (Karplus-Strong) en Do majeur, 112 bpm
    beat = 60 / 112; mus = np.zeros(N, np.float32)
    def pluck(freq, dur=0.5, amp=0.3):
        p = int(SR / freq); buf = np.random.uniform(-1, 1, p); out = np.zeros(int(SR * dur))
        for k in range(len(out)):
            out[k] = buf[k % p]; buf[k % p] = 0.497 * (buf[k % p] + buf[(k + 1) % p])
        return out * amp
    mel = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 79, 77, 74, 71]
    bass = [48, 48, 53, 53, 48, 48, 55, 55]
    notes = {}
    for k in range(int(TOTAL / (beat / 2))):
        m = mel[k % len(mel)]
        if m not in notes: notes[m] = pluck(440 * 2 ** ((m - 69) / 12), .45, .16)
        put_a(mus, k * beat / 2, notes[m])
        if k % 2 == 0:
            b = bass[(k // 4) % len(bass)]
            if b not in notes: notes[b] = pluck(440 * 2 ** ((b - 69) / 12), .8, .3)
            put_a(mus, k * beat / 2, notes[b])
    venv = np.convolve(np.abs(voice), np.ones(2205) / 2205, "same")
    g = np.convolve(np.where(venv > 0.01, 0.55, 1.0), np.ones(4410) / 4410, "same")
    master = np.tanh(1.15 * (voice * 1.05 + fx * 0.55 + mus * g * 0.45)) * 0.93
    def wav(p, x):
        with wave.open(p, "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
            f.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    wav(f"{S}/v2/mix.wav", master)
    wav(f"{OUT}/voz_sola.wav", voice / max(1e-6, np.abs(voice).max()) * 0.9)
    wav(f"{OUT}/efectos_y_musica.wav", np.tanh(fx * 0.55 + mus * g * 0.45))

def srt():
    def ts(x):
        ms = int(round(x * 1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
    with open(f"{OUT}/subtitulos.srt", "w") as f:
        for k, (s_, e_, ws) in enumerate(caps, 1):
            f.write(f"{k}\n{ts(s_)} --> {ts(e_)}\n{' '.join(ws)}\n\n")

if ONLY == "stills":
    ims = []
    for k, (s_, *_r) in enumerate(SHOTS):
        ims.append(frame(min(starts[k + 1] - 0.05, s_ + 0.6)).resize((216, 384)))
    sheet = Image.new("RGB", (216 * 10, 384 * 5), (0, 0, 0))
    for k, im in enumerate(ims): sheet.paste(im, ((k % 10) * 216, (k // 10) * 384))
    sheet.save(f"{S}/v2/stills.png")
    print("TOTAL", round(TOTAL, 2))
    sys.exit()

build_audio(); srt()
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                      "-i", "-", "-i", f"{S}/v2/mix.wav", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                      f"{OUT}/clodo_cara_de_culpable_v2.mp4"], stdin=subprocess.PIPE)
for k in range(int(TOTAL * FPS)):
    p.stdin.write(frame(k / FPS).tobytes())
p.stdin.close(); p.wait()
print("TOTAL", round(TOTAL, 2))

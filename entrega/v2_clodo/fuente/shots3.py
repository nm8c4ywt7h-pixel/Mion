# ---------------------------------------------------- plans supplémentaires (calés sur le découpage de l'original)
def sc_mess(img, now, s):
    d = ImageDraw.Draw(img)
    P(d, [(250, 1560), (420, 1560), (390, 1700), (280, 1700)], (200, 100, 60))
    for k, (x, y) in enumerate(((140, 1690), (230, 1720), (470, 1700), (520, 1730))):
        P(d, [(x, y), (x + 50, y - 30), (x + 70, y + 20)], (200, 100, 60), 7)
    E(d, (120, 1650, 560, 1760), (110, 75, 50), 0)
    for k in range(4):
        line(d, [(330 + k * 25, 1560), (300 + k * 40, 1430 - k * 20)], 12, (80, 160, 70))
        E(d, (290 + k * 40 - 30, 1400 - k * 20, 290 + k * 40 + 30, 1450 - k * 20), (90, 180, 80), 7)
    P_(img, "dog", ("clodo", "guilty"), 760, 1720, 520, popf(now - s))

def sc_bday(img, now, s):
    d = ImageDraw.Draw(img)
    R(d, (420, 1450, 660, 1490), 10, WHITE)
    R(d, (520, 1490, 560, 1720), 8, (170, 110, 60))
    P_(img, "cake", (), 540, 1460, 300)
    P_(img, "person", ("maminova", "sing", "up"), 540, 1230, 900, popf(now - s))
    for k in range(26):
        x = (k * 173) % W; y = ((k * 311) % 900 + (now - s) * 380) % 1300
        col = [(255, 90, 90), (90, 200, 255), (255, 210, 60), (130, 230, 120)][k % 4]
        R(d, (x, y, x + 22, y + 36), 4, col, 0)

def sc_family_shock(img, now, s):
    family_row(img, now, "shock")
    table(img, 1290, 220, 330, 980)
    P_(img, "chicken", (False,), 650, 1300, 200)

def sc_dad_table(img, now, s):
    P_(img, "person", ("voldemort", "neutral", "bowl"), W / 2, 1600, 1050, popf(now - s))
    table(img, 1450, 260, 80, 1000)

def sc_dad_red(img, now, s):
    d = ImageDraw.Draw(img)
    sh = random.uniform(-9, 9)
    P_(img, "person", ("torchon", "shock", "down"), 170, 1640, 560)
    P_(img, "person", ("maminova", "shock", "down"), 910, 1640, 600)
    P_(img, "person", ("voldemort", "angry", "up"), W / 2 + sh, 1700, 1150)
    for k in range(8):
        a = k * math.pi / 4 + 0.3
        r0, r1 = 330, 420 + 30 * math.sin(now * 20 + k)
        line(d, [(540 + r0 * math.cos(a), 760 + r0 * math.sin(a)), (540 + r1 * math.cos(a), 760 + r1 * math.sin(a))], 16, YEL)

def sc_rewind(img, now, s):
    sc_clock(img, now, s)
    d = ImageDraw.Draw(img)
    for x in (470, 560):
        P(d, [(x + 80, 1400), (x + 80, 1520), (x, 1460)], WHITE, 8)

def tripod(img, x, y):
    d = ImageDraw.Draw(img)
    for dx in (-70, 0, 70):
        line(d, [(x, y), (x + dx, y + 420)], 10)
    R(d, (x - 70, y - 90, x + 70, y + 10), 14, OL)
    E(d, (x + 40, y - 70, x + 100, y - 10), (90, 90, 100), 6)
    E(d, (x - 50, y - 140, x + 10, y - 80), (240, 60, 70), 6)

def sc_sci(img, now, s):
    tripod(img, 840, 1150)
    P_(img, "person", ("horowitz", "neutral", "down"), 430, 1690, 1000, popf(now - s))

def sc_lab2(img, now, s, who, expr, arms, dname, dexpr, treat_pos=None, x=380, cam=True):
    if cam: tripod(img, 900, 1100)
    if who: P_(img, "person", (who, expr, arms), x, 1690, 1000)
    P_(img, "dog", (dname, dexpr), 790, 1700, 460)
    if treat_pos: P_(img, "treat", (), treat_pos[0], treat_pos[1], 70)

def sc_family_garden(img, now, s, expr="neutral"):
    family_row(img, now, expr)
    table(img, 1290, 220, 330, 980)
    P_(img, "chicken", (True,), 650, 1300, 200)
    if expr == "angry":
        P_(img, "dog", ("clodo", "guilty"), 800, 1760, 300)

@lru_cache(None)
def lineup():
    im = Image.new("RGB", (W, H), (200, 205, 215)); d = ImageDraw.Draw(im)
    for k, y in enumerate(range(300, 1500, 100)):
        d.line((0, y, W, y), fill=(150, 155, 170), width=6 if k % 2 else 10)
    d.rectangle((0, 1500, W, H), fill=(140, 145, 160)); d.line((0, 1500, W, 1500), fill=OL, width=10)
    return im

def sc_mug(img, now, s, h):
    P_(img, "dog", ("clodo", "guilty"), W / 2, 1640, h)
    d = ImageDraw.Draw(img)
    w = h * 0.55
    R(d, (W / 2 - w / 2, 1640 - h * 0.30, W / 2 + w / 2, 1640 - h * 0.12), 10, OL)
    d.text((W / 2, 1640 - h * 0.21), "CLODO", font=F(int(h * 0.09)), fill=WHITE, anchor="mm")

def sc_finger(img, now, s):
    sc_meters(img, now, s, 0.15, 0.15 + 0.75 * min(1, (now - s) / 0.6))
    d = ImageDraw.Draw(img)
    y = max(-30, -200 + min(1, (now - s) / 0.3) * 650)
    R(d, (735, -50, 845, y), 30, YEL)
    E(d, (720, y - 60, 860, y + 60), (240, 200, 170))
    R(d, (775, y + 20, 805, y + 120), 15, (240, 200, 170))

def sc_stage(img, now, s):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle((0, 0, W, H), fill=(40, 25, 45))
    for x0 in (0, W - 260):
        for k in range(5):
            R(d, (x0 + k * 52, -20, x0 + k * 52 + 60, 1700), 26, (200, 40, 60), 6)
    d.polygon([(W / 2 - 100, 0), (W / 2 + 100, 0), (W / 2 + 420, 1650), (W / 2 - 420, 1650)], fill=(255, 255, 255, 30))
    d.rectangle((0, 1650, W, H), fill=(110, 70, 50))
    for k, (n, x) in enumerate((("negro", 300), ("blanco", 540), ("clodo", 780))):
        P_(img, "dog", (n, "guilty"), x, 1700, 360, popf(now - s - 0.12 * k))

def sc_white_thought(img, now, s):
    P_(img, "dog", ("blanco", "guilty"), 430, 1560, 620)
    P_(img, "bubble", ("bone",), 720, 980, 400, popf(now - s))

def sc_clodo_sit(img, now, s):
    P_(img, "dog", ("clodo", "guilty"), W / 2, 1560, 700, popf(now - s))

def sc_mami_shout(img, now, s):
    sh = random.uniform(-6, 6)
    P_(img, "person", ("maminova", "angry", "point"), 400 + sh, 1640, 1050)
    P_(img, "dog", ("clodo", "guilty"), 880, 1660, 420 * (1 - 0.25 * min(1, (now - s) / 1.5)))

def sc_phone_table(img, now, s):
    scr = garden(False).copy()
    table(scr, 1200, 400, 100, 980)
    P_(scr, "chicken", (True,), 540, 1250, 400)
    ph = art.phone_frame(scr.resize((540, 960)), 640, 1120)
    put(img, ph, W / 2, 1600, 1150 * popf(now - s, 0.25))

def sc_sofa_dad(img, now, s, up=False):
    sofa(img)
    for who, x, h in (("torchon", 200, 560), ("maminova", 400, 600), ("louise", 900, 540)):
        P_(img, "person", (who, "shock", "down", (0.6, 0)), x, 1380, h)
    P_(img, "person", ("voldemort", "grin" if up else "shock", "up" if up else "down"), 680, 1400 if not up else 1450, 680 if not up else 820)
    d = ImageDraw.Draw(img, "RGBA")
    d.polygon([(620, 0), (760, 0), (980, 1600), (400, 1600)], fill=(255, 255, 220, 40))

def sc_dad_eat(img, now, s):
    P_(img, "person", ("voldemort", "grin", "eat"), W / 2, 1620, 1080, popf(now - s))
    table(img, 1450, 260, 80, 1000)
    P_(img, "chicken", (False,), W / 2, 1460, 220)

def sc_wipe(img, now, s):
    sc_video(img, now, s, s, s + 10)

def sc_mouth(img, now, s):
    d = ImageDraw.Draw(img)
    sc_ = 1 + 0.06 * math.sin(now * 30)
    cx, cy, rw, rh = W / 2, 520, 300 * sc_, 170 * sc_
    E(d, (cx - rw, cy - rh, cx + rw, cy + rh), (150, 30, 50), 12)
    R(d, (cx - rw * 0.7, cy - rh * 0.95, cx + rw * 0.7, cy - rh * 0.55), 20, WHITE, 0)
    d.chord((cx - rw * 0.6, cy, cx + rw * 0.6, cy + rh * 1.6), 180, 360, fill=(255, 140, 150))
    for k in (-1, 1):
        for j in range(3):
            a = (j - 1) * 0.4
            line(d, [(cx + k * (rw + 40), cy + 120 * a), (cx + k * (rw + 120), cy + 220 * a)], 12)
    P_(img, "dog", ("clodo", "guilty"), W / 2, 1640, 640)

def sc_corner2(img, now, s):
    sc_dad(img, now, s, s)

def sc_police_cuts(img, now, s, h):
    sc_mug(img, now, s, h)

T = lambda li, w: wt(li, w)
SHOTS = [
    (0.0, "burst_y", sc_hook_a, "whoosh"),
    (T(0, "descubrir"), "garden", sc_mess, "pop"),
    (T(0, "no"), "burst_p", sc_hook_c, "pop"),
    (lt(1), "spot", sc_close, "bass"),
    (T(1, "inquietante"), "burst_o", sc_eye, "whoosh"),
    (lt(2), "garden", sc_bday, "pop"),
    (T(2, "toda"), "garden", sc_party, "pop"),
    (lt(3), "garden", lambda i, n, s: sc_chicken(i, n, s, 99), "pop"),
    (T(3, "desaparecen"), "garden", lambda i, n, s: sc_chicken(i, n, s, s + 0.15), "poof"),
    (lt(4), "garden", sc_family_shock, "pop"),
    (T(4, "Clodo"), "blank", sc_hide, "pop"),
    (lt(5), "spot", sc_close, "bass"),
    (T(5, "cola"), "blank", sc_hide, "pop"),
    (lt(6), "garden", lambda i, n, s: sc_shout(i, n, s, "torchon", "up"), "boing"),
    (lt(7), "garden", lambda i, n, s: sc_shout(i, n, s, "maminova", "point", 400), "pop"),
    (lt(8), "garden", sc_courgette, "shutter"),
    (lt(9), "garden", sc_dad_table, "pop"),
    (T(9, "grita"), "burst_r", sc_dad_red, "bass"),
    (T(9, "rincón"), "garden", lambda i, n, s: sc_dad(i, n, s, s), "pop"),
    (lt(10), "burst_v", sc_rewind, "tick"),
    (T(10, "investigadora"), "lab", sc_sci, "pop"),
    (T(10, "Nueva"), "city", sc_ny, "whoosh"),
    (lt(11), "lab", lambda i, n, s: sc_lab2(i, n, s, "owner", "angry", "point", "negro", "happy", (620, 1700)), "pop"),
    (T(11, "salían"), "lab", lambda i, n, s: sc_lab2(i, n, s, "owner", "neutral", "down", "negro", "happy", (620, 1700),
                                                     x=380 - 700 * min(1, (n - s) / 0.7)), "whoosh"),
    (T(11, "como"), "garden", lambda i, n, s: sc_family_garden(i, n, s, "sing"), "pop"),
    (lt(12), "lab", lambda i, n, s: sc_lab2(i, n, s, "horowitz", "neutral", "point", "negro", "happy", (620, 1700)), "pop"),
    (T(12, "quitaba"), "lab", lambda i, n, s: sc_lab2(i, n, s, "horowitz", "neutral", "point", "blanco", "neutral",
                                                      (620, 1700) if n - s < 0.5 else (690, 1190)), "pop"),
    (lt(13), "lab", lambda i, n, s: sc_lab2(i, n, s, "owner", "neutral", "down", "blanco", "neutral"), "pop"),
    (T(13, "regañar"), "lab", lambda i, n, s: sc_lab2(i, n, s, "owner", "angry", "point", "blanco", "guilty"), "boing"),
    (T(13, "como"), "garden", lambda i, n, s: sc_family_garden(i, n, s, "angry"), "pop"),
    (lt(14), "lineup", lambda i, n, s: sc_mug(i, n, s, 600), "shutter"),
    (T(14, "pone"), "lineup", lambda i, n, s: sc_mug(i, n, s, 820), "shutter"),
    (T(14, "Clodo"), "lineup", lambda i, n, s: sc_mug(i, n, s, 1040), "shutter"),
    (T(14, "perros"), "lab", lambda i, n, s: sc_meters(i, n, s, 0.15, 0.15), "pop"),
    (lt(15), "lab", sc_finger, "boing"),
    (lt(16), "blank", sc_stage, "bass"),
    (T(16, "realidad"), "burst_y", sc_white_thought, "pop"),
    (lt(17), "burst_b", sc_clodo_sit, "pop"),
    (lt(18), "garden", sc_mami_shout, "pop"),
    (T(18, "calmar"), "burst_pk", lambda i, n, s: sc_angry_faces(i, n, s, s), "pop"),
    (lt(19), "night", lambda i, n, s: sc_sofa(i, n, s, 999), "whoosh"),
    (T(19, "descubre"), "night", sc_phone_table, "pop"),
    (T(19, "Voldemort"), "night", lambda i, n, s: sc_sofa_dad(i, n, s, False), "bass"),
    (lt(20), "garden", sc_dad_eat, "pop"),
    (T(20, "limpia"), "night", sc_wipe, "squish"),
    (T(20, "sin"), "night", lambda i, n, s: sc_sofa_dad(i, n, s, True), "pop"),
    (lt(21), "burst_c", sc_mouth, "boing"),
    (T(21, "debes"), "burst_g", sc_thought, "pop"),
    (lt(22), "burst_pk", sc_angel, "chime"),
    (T(22, "injusto"), "garden", sc_corner2, "whoosh"),
]
EXTRA_SFX = [(T(9, "grita") + 0.05, "boing"), (T(15, "regañados"), "pop")]
BG.update(burst_r=lambda: sunburst((245, 100, 90), (235, 85, 75)),
          burst_c=lambda: sunburst((252, 225, 195), (246, 212, 178)),
          lineup=lineup)

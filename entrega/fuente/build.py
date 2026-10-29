"""Construit la vidéo « El truco del silencio » : voix + SFX + musique + images animées."""
import json, math, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]
OUT = sys.argv[2]
SR = 44100
FPS = 30
W, H = 1080, 1920
random.seed(7); np.random.seed(7)

# ---------- voix : décodage + découpe des silences de bord ----------
words = json.load(open(f"{S}/voz/words.json"))

def load_mp3(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

lines = []
for i, wl in enumerate(words):
    a = load_mp3(f"{S}/voz/l{i:02d}.mp3")
    st = max(0, wl[0][1] - 0.04)
    en = min(len(a) / SR, wl[-1][1] + wl[-1][2] + 0.12)
    lines.append({"audio": a[int(st * SR):int(en * SR)],
                  "words": [(w, o - st, d) for w, o, d in wl]})

def dur(i): return len(lines[i]["audio"]) / SR

# ---------- timeline ----------
ev = []      # (t, type, data)
voice_at = {}
t = 0.15
def say(i, gap=0.12):
    global t
    voice_at[i] = t
    t += dur(i) + gap

scenes = []  # (start, end, name)
def scene(name, fn):
    s = t; fn(); scenes.append((s, t, name))

ev.append((0.0, "whoosh", None))
scene("hook", lambda: say(0, 0.15))
ev.append((voice_at[0] + lines[0]["words"][3][1], "bass", None))         # « tres »
ev.append((t - 0.12, "whoosh", None))
scene("intro", lambda: say(1, 0.1))
ev.append((t, "swoosh", None))
scene("pregunta", lambda: (say(2, 0.25), say(3, 0.2)))
cd1 = t
def countdown():
    global t
    for k in range(3):
        ev.append((t + k * 0.75, "tick" if k % 2 == 0 else "tock", None))
    t += 2.3
scene("silencio1", countdown)
ev.append((t, "swoosh", None))
scene("cuenta", lambda: say(4, 0.15))
for w, o, d in lines[4]["words"][::3]:
    ev.append((voice_at[4] + o, "pop", None))
scene("orgullo", lambda: say(5, 0.05))
ev.append((voice_at[5] + lines[5]["words"][0][1] + 0.55, "ding", None))
freeze_t = t
ev.append((t, "scratch", None))
scene("freeze", lambda: globals().__setitem__("t", t + 0.6))
cd2 = t
scene("silencio2", countdown)
scene("confesion", lambda: say(6, 0.55))
ev.append((voice_at[6] + lines[6]["words"][2][1], "boom", None))         # « Me gustas »
scene("final", lambda: say(7, 0.25))
ev.append((voice_at[7] + dur(7) + 0.05, "ding", None))
ev.append((t - 0.1, "whoosh", None))
scene("cta", lambda: say(8, 0.6))
ev.append((t - 0.55, "whoosh", None))
TOTAL = t
N = int(TOTAL * SR)

# ---------- synthèse des effets sonores ----------
def env(n, a=0.005, d=0.3):
    x = np.arange(n) / SR
    return np.minimum(1, x / a) * np.exp(-x / d)

def lp_sweep(x, f0, f1):
    y = np.zeros_like(x); s = 0.0
    fs = np.geomspace(f0, f1, len(x))
    al = 1 - np.exp(-2 * np.pi * fs / SR)
    for k in range(len(x)):
        s += al[k] * (x[k] - s); y[k] = s
    return y

def sfx(kind):
    if kind in ("whoosh", "swoosh"):
        n = int(SR * (0.45 if kind == "whoosh" else 0.25))
        x = lp_sweep(np.random.randn(n), 300, 6000 if kind == "whoosh" else 3500)
        e = np.sin(np.linspace(0, np.pi, n)) ** 2
        return x * e * (1.6 if kind == "whoosh" else 1.0)
    if kind == "bass":
        n = int(SR * 0.9); tt = np.arange(n) / SR
        f = 45 + 110 * np.exp(-tt / 0.06)
        return np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.002, 0.35) * 0.9
    if kind == "pop":
        n = int(SR * 0.07); tt = np.arange(n) / SR
        f = 300 + 900 * np.exp(-tt / 0.015)
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.025) * 0.5
    if kind in ("tick", "tock"):
        n = int(SR * 0.06); tt = np.arange(n) / SR
        f = 2200 if kind == "tick" else 1500
        return (np.sin(2 * np.pi * f * tt) + 0.3 * np.random.randn(n)) * env(n, 0.0005, 0.012) * 0.7
    if kind == "ding":
        n = int(SR * 1.4); tt = np.arange(n) / SR
        x = sum(a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / dd)
                for f, a, dd in [(1318.5, 1, .5), (2637, .4, .25), (3955, .2, .12), (1975.5, .3, .35)])
        return x * env(n, 0.001, 10) * 0.35
    if kind == "scratch":
        n = int(SR * 0.55); tt = np.arange(n) / SR
        wob = 1 + 0.9 * np.sin(2 * np.pi * 7 * tt) * np.exp(-tt / 0.4)
        f = 380 * wob * np.linspace(1.3, 0.4, n)
        x = 0.6 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) + 0.5 * lp_sweep(np.random.randn(n), 4000, 800)
        return x * env(n, 0.002, 0.25) * 0.55
    if kind == "boom":
        n = int(SR * 1.6); tt = np.arange(n) / SR
        f = 52 + 70 * np.exp(-tt / 0.08)
        x = np.tanh(4 * np.sin(2 * np.pi * np.cumsum(f) / SR)) + 0.4 * lp_sweep(np.random.randn(n), 900, 120)
        return x * env(n, 0.003, 0.5) * 0.9
    raise ValueError(kind)

voice = np.zeros(N, np.float32)
fx = np.zeros(N, np.float32)
def put(buf, at, x):
    s = int(at * SR); e = min(N, s + len(x))
    if s < N: buf[s:e] += x[:e - s]
for i, at in voice_at.items():
    put(voice, at, lines[i]["audio"] * 1.0)
cache = {}
for at, kind, _ in ev:
    if kind not in cache: cache[kind] = sfx(kind).astype(np.float32)
    put(fx, at, cache[kind])

# ---------- musique lo-fi originale (Am - F - C - G, 84 bpm) ----------
bpm = 84; beat = 60 / bpm
tt = np.arange(N) / SR
chords = [[57, 60, 64], [53, 57, 60], [48, 55, 64], [55, 59, 62]]
mus = np.zeros(N, np.float32)
bar = 4 * beat
for b in range(int(TOTAL / bar) + 2):
    ch = chords[b % 4]
    s = int(b * bar * SR); e = min(N, int((b + 1) * bar * SR))
    if s >= N: break
    seg = tt[s:e] - b * bar
    pad = sum(np.sin(2 * np.pi * 440 * 2 ** ((m - 69) / 12) * seg) +
              0.3 * np.sin(2 * np.pi * 880 * 2 ** ((m - 69) / 12) * seg) for m in ch)
    pad *= np.minimum(1, seg / 0.3) * np.minimum(1, (bar - seg) / 0.3) * 0.06
    bass = np.sin(2 * np.pi * 440 * 2 ** ((ch[0] - 12 - 69) / 12) * seg) * 0.12 * np.exp(-(seg % (2 * beat)) / 0.5)
    mus[s:e] += pad + bass
for k in range(int(TOTAL / beat) + 1):
    at = k * beat
    if k % 2 == 0:
        n = int(SR * 0.35); x = np.arange(n) / SR
        put(mus, at, np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-x / 0.03)) / SR) * np.exp(-x / 0.12) * 0.35)
    else:
        n = int(SR * 0.2); put(mus, at, lp_sweep(np.random.randn(n), 3000, 1500) * np.exp(-np.arange(n) / SR / 0.05) * 0.25)
    n = int(SR * 0.04)
    for h in (0, 0.5):
        put(mus, at + h * beat, np.random.randn(n) * np.exp(-np.arange(n) / SR / 0.008) * 0.05)

# ducking : musique à 20 % pendant les silences et sous la voix
gain = np.full(N, 1.0, np.float32)
def duck(a, b, g):
    gain[int(a * SR):int(b * SR)] = np.minimum(gain[int(a * SR):int(b * SR)], g)
for c in (cd1, cd2): duck(c - 0.05, c + 2.3, 0.2)
duck(freeze_t, freeze_t + 0.6, 0.0)
duck(voice_at[7] - 0.55, voice_at[7] - 0.05, 0.15)
venv = np.convolve(np.abs(voice), np.ones(2205) / 2205, "same")
gain = np.minimum(gain, np.where(venv > 0.01, 0.55, 1.0)).astype(np.float32)
gain = np.convolve(gain, np.ones(2205) / 2205, "same")
mix_music = mus * gain

def norm(x, peak=0.95):
    m = np.max(np.abs(x)); return x * (peak / m) if m > 0 else x
master = np.tanh(1.2 * (voice * 1.0 + fx * 0.6 + mix_music * 0.55)) * 0.92

def wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((x * 32767).astype(np.int16).tobytes())
wav(f"{OUT}/mix.wav", master)
wav(f"{OUT}/voz_sola.wav", norm(voice, 0.9))
wav(f"{OUT}/efectos_y_musica.wav", np.tanh(fx * 0.6 + mix_music * 0.55))

# ---------- sous-titres ----------
captions = []  # (start, end, text, highlight_words)
HL = {0: {"tres", "segundos"}, 4: {"trabajo", "ex", "hermana"}, 5: {"Funcionó"}, 6: {"gustas"},
      7: {"truco"}, 8: {"Sígueme"}, 1: {"Mateo", "Lucía"}}
for i, at in voice_at.items():
    wl = lines[i]["words"]
    # groupes de 2-3 mots, rythme TikTok
    groups, g = [], []
    for w in wl:
        g.append(w)
        if len(g) == 3 or (len(g) == 2 and len(" ".join(x[0] for x in g)) > 12): groups.append(g); g = []
    if g: groups.append(g)
    for k, g in enumerate(groups):
        s = at + g[0][1]
        e = at + (groups[k + 1][0][1] if k + 1 < len(groups) else g[-1][1] + g[-1][2] + 0.1)
        captions.append((s, e, [x[0] for x in g], HL.get(i, set()), i))

def srt_t(x):
    ms = int(round(x * 1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
with open(f"{OUT}/subtitulos.srt", "w") as f:
    for k, (s, e, ws, _, _) in enumerate(captions, 1):
        f.write(f"{k}\n{srt_t(s)} --> {srt_t(e)}\n{' '.join(ws).upper()}\n\n")

# ---------- images ----------
F = "/usr/share/fonts/opentype/inter/"
font = lambda s: ImageFont.truetype(F + "Inter-Black.otf", s)
fontb = lambda s: ImageFont.truetype(F + "Inter-ExtraBold.otf", s)
EMO = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
YEL, WHITE = (255, 214, 10), (255, 255, 255)
SPEAKER = {0: "N", 1: "N", 2: "M", 3: "L", 4: "L", 5: "N", 6: "M", 7: "L", 8: "N"}

def emoji(ch, size):
    im = Image.new("RGBA", (140, 140)); ImageDraw.Draw(im).text((8, 8), ch, font=EMO, embedded_color=True)
    return im.crop(im.getbbox()).resize((size, size), Image.LANCZOS)
EM = {k: emoji(k, 150) for k in ["🤫", "🧠", "😳", "✅", "💀", "😏", "☕", "👉"]}

def grad(c1, c2):
    y = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c1) * (1 - y) + np.array(c2) * y).astype(np.uint8)
    return Image.fromarray(np.repeat(a, W, 1))
BG = {"narr": grad((18, 18, 28), (48, 22, 60)),
      "cafe": grad((60, 38, 24), (196, 120, 52)),
      "tense": grad((10, 10, 14), (40, 12, 16))}

def avatar(d, cx, cy, r, color, letter, name, active):
    if active:
        d.ellipse([cx - r - 18, cy - r - 18, cx + r + 18, cy + r + 18], outline=YEL, width=10)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    d.text((cx, cy), letter, font=font(int(r * 1.1)), fill=WHITE, anchor="mm")
    d.text((cx, cy + r + 70), name, font=fontb(56), fill=WHITE, anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))

def ease(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3

def draw_caption(img, now):
    d = ImageDraw.Draw(img)
    for s, e, ws, hl, li in captions:
        if s <= now < e:
            p = ease((now - s) / 0.12)
            size = int(108 * (0.75 + 0.25 * p) * (1.08 if p < 1 else 1))
            f = font(size)
            text_w = sum(d.textlength(w.upper() + " ", font=f) for w in ws)
            if text_w > 960:
                size = int(size * 960 / text_w); f = font(size)
                text_w = sum(d.textlength(w.upper() + " ", font=f) for w in ws)
            x = (W - text_w) / 2; y = 1280
            for w in ws:
                u = w.upper()
                col = YEL if w.strip("¿?¡!.,") in hl else WHITE
                d.text((x, y), u, font=f, fill=col, stroke_width=10, stroke_fill=(0, 0, 0), anchor="lm")
                x += d.textlength(u + " ", font=f)

def scene_at(now):
    for s, e, n in scenes:
        if s <= now < e: return n, s, e
    return scenes[-1][2], scenes[-1][0], scenes[-1][1]

def speaking(now):
    for i, at in voice_at.items():
        if at <= now < at + dur(i): return i
    return None

def paste_c(img, im, cx, cy, sc=1.0):
    if sc != 1.0: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

def countdown_draw(img, now, start, who):
    d = ImageDraw.Draw(img)
    k = int((now - start) / 0.75)
    if k < 3:
        p = ease((now - start - k * 0.75) / 0.15)
        f = font(int(420 * (1.4 - 0.4 * p)))
        d.text((W / 2, 900), str(k + 1), font=f, fill=YEL, anchor="mm", stroke_width=16, stroke_fill=(0, 0, 0))
    d.text((W / 2, 1450), f"{who} SE CALLA...", font=fontb(70), fill=WHITE, anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))

def frame(now):
    name, s, e = scene_at(now)
    sp = speaking(now); who = SPEAKER.get(sp)
    if name in ("hook", "orgullo", "cta"):
        img = BG["narr"].copy(); d = ImageDraw.Draw(img)
        d.text((W / 2, 230), "EL TRUCO DEL SILENCIO", font=font(74), fill=YEL, anchor="mm")
        icon = {"hook": "🤫", "orgullo": "✅", "cta": "👉"}[name]
        bob = 1 + 0.04 * math.sin(now * 6)
        paste_c(img, EM[icon], W / 2, 760, 2.2 * bob)
    elif name in ("silencio1", "silencio2", "freeze"):
        img = BG["tense"].copy(); d = ImageDraw.Draw(img)
        if name == "freeze":
            img = BG["cafe"].copy().convert("L").convert("RGB"); d = ImageDraw.Draw(img)
            avatar(d, 300, 620, 170, (70, 70, 70), "M", "MATEO", False)
            avatar(d, 780, 620, 170, (110, 110, 110), "L", "LUCÍA", False)
            d.text((W / 2, 1150), "...O ESO CREÍA ÉL", font=font(96), fill=WHITE, anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0))
        else:
            mateo = name == "silencio1"
            countdown_draw(img, now, s, "MATEO" if mateo else "LUCÍA")
            avatar(d, W / 2, 330, 120, (40, 90, 200) if mateo else (215, 30, 45), "M" if mateo else "L",
                   "", False)
    else:
        img = BG["cafe"].copy(); d = ImageDraw.Draw(img)
        d.rounded_rectangle([90, 900, 990, 960], 30, fill=(70, 42, 25))
        paste_c(img, EM["☕"], 540, 860, 0.8)
        avatar(d, 300, 620, 170, (40, 90, 200), "M", "MATEO", who == "M")
        avatar(d, 780, 620, 170, (215, 30, 45), "L", "LUCÍA", who == "L")
        icon = {"intro": "🧠", "cuenta": "😳", "confesion": "💀", "final": "😏"}.get(name)
        if icon:
            p = ease((now - s) / 0.25)
            pos = {"intro": 300, "cuenta": 780, "confesion": 300, "final": 780}[name]
            paste_c(img, EM[icon], pos + 150, 420, 0.8 * p + 0.01)
        if name == "pregunta" and sp is None and now > voice_at[3]:
            pass
    draw_caption(img, now)
    # punch-in zoom sur les temps forts
    z = 1.0
    for at, kind, _ in ev:
        if kind in ("bass", "boom", "scratch", "whoosh") and 0 <= now - at < 0.6:
            z = max(z, 1 + {"bass": .12, "boom": .15, "scratch": .08, "whoosh": .05}[kind] * (1 - ease((now - at) / 0.6)))
    if name in ("silencio1", "silencio2"):
        z = max(z, 1 + 0.06 * (now - s) / 2.3)                         # zoom lent = tension
    dx = dy = 0
    for at, kind, _ in ev:
        if kind in ("boom", "scratch") and 0 <= now - at < 0.35:
            amp = 28 * (1 - (now - at) / 0.35); dx += random.uniform(-amp, amp); dy += random.uniform(-amp, amp)
    if z != 1.0 or dx or dy:
        cw, ch = W / z, H / z
        x0 = (W - cw) / 2 + dx; y0 = (H - ch) / 2 + dy
        img = img.crop((int(x0), int(y0), int(x0 + cw), int(y0 + ch))).resize((W, H), Image.BILINEAR)
    # flash blanc sur les cuts et le freeze
    for at, kind, _ in ev:
        if kind in ("scratch", "boom") and 0 <= now - at < 0.12:
            a = 1 - (now - at) / 0.12
            img = Image.blend(img, Image.new("RGB", (W, H), WHITE), 0.7 * a)
    for s2, _, _ in scenes:
        if 0 <= now - s2 < 0.06 and s2 > 0:
            img = Image.blend(img, Image.new("RGB", (W, H), WHITE), 0.35)
    return img

p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                      "-r", str(FPS), "-i", "-", "-i", f"{OUT}/mix.wav", "-c:v", "libx264", "-preset", "medium",
                      "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                      "-movflags", "+faststart", f"{OUT}/el_truco_del_silencio.mp4"], stdin=subprocess.PIPE)
nf = int(TOTAL * FPS)
for k in range(nf):
    p.stdin.write(frame(k / FPS).tobytes())
p.stdin.close(); p.wait()
print("TOTAL", round(TOTAL, 2), "frames", nf, "scenes", [(n, round(a, 2)) for a, b, n in scenes])

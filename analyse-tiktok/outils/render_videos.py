"""Fabrique les vidéos TikTok (1080x1920, 30 fps) à partir des scripts Markdown.

- Voix off allemande : Microsoft Edge TTS (paquet `edge-tts`), voix de-DE-ConradNeural
- Sous-titres karaoké synchronisés mot à mot (le mot prononcé passe en jaune)
- Visuels : fond pastel, émojis animés, carte « question » en haut, compte à rebours,
  tampon AUFLÖSUNG, mascotte Knödel dessinée en code

Usage : python3 render_videos.py [--lang es|de] [id ...]   (ex. R1 S3 ; sans id = les 20 vidéos)
Langue par défaut : espagnol. Sortie : ../videos/<langue>/
"""
import asyncio
import math
import re
import subprocess
import sys
import tempfile
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE = Path(__file__).resolve().parent.parent
LANGS = {
    "es": {
        "files": (("05_GUIONES_ES.md", "S"), ("06_ACERTIJOS_ES.md", "R")),
        "heading": r"^## (?:Guion|Acertijo) (\d+): (.+)",
        "hook": r"^\*\*Texto:\*\* (.+)",
        "countdown": ["Cinco", "Cuatro", "Tres", "Dos", "Uno"],
        "answer": r"^(RESPUESTA|Respuesta)",
        "voice": "es-MX-JorgeNeural",
        "rate": "+4%",
        "brand": "ACERTIJO ANIMAL",
        "stamp": "RESPUESTA",
        "write": "¡Escribe tu respuesta!",
        "names": ("explicacion", "acertijo"),
    },
    "de": {
        "files": (("02_SKRIPTE_DE.md", "S"), ("03_ECHTE_RAETSEL_DE.md", "R")),
        "heading": r"^## (?:Skript|Rätsel) (\d+): (.+)",
        "hook": r"^\*\*Text(?: auf dem Bildschirm)?:\*\* (.+)",
        "countdown": ["Fünf", "Vier", "Drei", "Zwei", "Eins"],
        "answer": r"^(AUFLÖSUNG|Auflösung)",
        "voice": "de-DE-ConradNeural",
        "rate": "+6%",
        "brand": "TIER-RÄTSEL",
        "stamp": "AUFLÖSUNG",
        "write": "Schreib deine Antwort!",
        "names": ("erklaer", "raetsel"),
    },
}
L = dict(LANGS["es"])
OUT = BASE / "videos"
W, H, FPS = 1080, 1920, 30
SR = 24000
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
PASTELS = ["#FFE8C7", "#D9F2E6", "#E6E0FF", "#FFF4B8", "#FFDCE5", "#D6ECFF", "#F0E6D8"]

# Émojis par paragraphe de voix off (même ordre que dans les scripts)
SCENES = {
    "S1": ["🚪🐱❓", "⏳", "🍽️🪟👕", "👃✅", "😴🔋", "🏠🐱", "🔍🐱"],
    "S2": ["⏰🐱❓", "🚪🐈😴", "🥐☕😤", "🌙🥣🐱", "🌅🧠", "🥣😅", "🔍🐱"],
    "S3": ["🛏️🐱❓", "🔥🧺❌", "🌡️❌", "🔬🐱🐱", "👅🐱💕", "🏠🐱❤️", "🔍🐱"],
    "S4": ["🐶🍗❓", "🍽️🐶👀", "👃🐶🍗", "🎰🦴", "📏✅", "🐶😌", "🔍🐶"],
    "S5": ["🐦❓", "🐦🎥", "👁️🐦", "🐦🔬", "🚆🌳👀", "🐦🌍", "🔍🐦"],
    "S6": ["🐱📣❓", "✅🔬", "🪑☕🔑", "🐱👂⚡", "🗣️👤", "🍽️🤚🏥", "👂🐱", "🔍🐱"],
    "S7": ["🐶❓", "🔄", "🧸🎾🦴", "🧠🐶⭐", "👂❌", "🧠🔍", "🤔🐶", "📸👇"],
    "S8": ["😢🐶❓", "🧂❌", "👃😰", "🥱🐶", "🐶🍼❤️", "🤗🐶", "🔍🐶"],
    "S9": ["🐱💛❓", "👃🐱✨", "🏷️🏠", "📱🐱", "🙇💛", "📤🐱"],
    "S10": ["🐱📝", "😌🐱", "🐱🤍", "🚽🐱", "🐾🧶", "👕😴", "📊🏆", "👇🔢"],
    "R1": ["❤️❤️❤️", None, "🐙", "🐙💙", "🐙💤", "✅🔍"],
    "R2": ["🐺🐐🥬", None, "🚣🐐", "🚣✅", "🔍❓"],
    "R3": ["🐓🏠🥚", None, "🐓❌🥚", "🐔🥚🌅", "😅👇"],
    "R4": ["🚢🐘🦒", None, "🚢0️⃣", "🧠🙈", "2️⃣❓"],
    "R5": ["🦘🐱❓", None, "🐘", "🐘🏛️", "🐘👂🦶", "🔍✅"],
    "R6": ["🐱🐱❓", None, "🐱🔍", "😅", "💬👇"],
    "R7": ["🐌🕳️", None, "8️⃣", "🐌📈", "💬👇"],
    "R8": ["☝️🔍❓", None, "🐨", "🐨🌿", "🤯"],
    "R9": ["🐶📏🥣", None, "🪢❌", "🐶🥣✅", "😄👇"],
    "R10": ["🐬💤❓", None, "🐬🧠", "🧠👁️", "😴🏫"],
}

EMOJI_RE = re.compile(r"[\U0001F000-\U0001FFFF☀-➿←-⇿⬀-⯿️⃣]")


# ---------------------------------------------------------------- parsing
def parse():
    vids = {}
    for fname, letter in L["files"]:
        cur = None
        for line in (BASE / fname).read_text(encoding="utf-8").splitlines():
            m = re.match(L["heading"], line)
            if m:
                cur = {"id": f"{letter}{m.group(1)}", "title": m.group(2), "hook": "", "paras": []}
                vids[cur["id"]] = cur
                continue
            if not cur:
                continue
            m = re.match(L["hook"], line)
            if m:
                cur["hook"] = EMOJI_RE.sub("", m.group(1)).strip()
            elif line.startswith(">") and line[1:].strip():
                cur["paras"].append(line[1:].strip())
    return vids


def segments(v):
    """Découpe en segments {kind, text, emojis}. kind: talk | countdown | answer."""
    segs, scenes = [], SCENES[v["id"]]
    cd_re = re.compile(r"\s*".join(re.escape(w + ".") for w in L["countdown"]))
    for i, p in enumerate(v["paras"]):
        em = scenes[i] if i < len(scenes) else None
        if cd_re.search(p):
            pre = cd_re.split(p)[0].strip()
            if pre:
                segs.append({"kind": "talk", "text": pre, "emojis": "⏸️🤔"})
            segs.append({"kind": "countdown", "text": "", "emojis": None})
            continue
        kind = "answer" if re.match(L["answer"], p) else "talk"
        segs.append({"kind": kind, "text": p, "emojis": em})
    return segs


# ---------------------------------------------------------------- audio
def tts_text(t):
    t = EMOJI_RE.sub("", t)
    t = t.replace("„", "").replace("“", "").replace("…", ",")
    t = re.sub(r"\b[A-ZÄÖÜÁÉÍÓÚÑ]{2,}\b", lambda m: m.group(0).capitalize() if m.start() == 0 else m.group(0).lower(), t)
    return re.sub(r"\s+", " ", t).strip()


async def _tts(text, mp3):
    import certifi
    certifi.where = lambda: "/root/.ccr/ca-bundle.crt"  # CA du proxy de ce conteneur
    import edge_tts
    c = edge_tts.Communicate(text, L["voice"], rate=L["rate"], boundary="WordBoundary")
    words = []
    with open(mp3, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append([ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7, ch["text"]])
    return words


def tts(text, tmp, tag):
    mp3 = tmp / f"{tag}.mp3"
    import time
    for attempt in range(6):
        try:
            words = asyncio.run(_tts(text, mp3))
            break
        except Exception:
            if attempt == 5:
                raise
            time.sleep(2 ** attempt)
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp3), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768, words


def tick(freq=1800, dur=0.05, vol=0.35):
    t = np.arange(int(SR * dur)) / SR
    return vol * np.sin(2 * np.pi * freq * t) * np.exp(-t * 60)


def ding():
    t = np.arange(int(SR * 0.9)) / SR
    return 0.22 * (np.sin(2 * np.pi * 880 * t) + 0.6 * np.sin(2 * np.pi * 1320 * t)) * np.exp(-t * 5)


def whoosh():
    t = np.arange(int(SR * 0.35)) / SR
    noise = np.random.default_rng(1).standard_normal(len(t))
    return 0.08 * noise * np.sin(np.pi * t / t[-1])


def align(words, text):
    """Rattache la ponctuation du texte original aux mots renvoyés par la TTS."""
    toks = [t for t in re.sub(r"[„“]", "", EMOJI_RE.sub("", text)).split() if re.search(r"\w", t)]
    norm = lambda s: re.sub(r"\W", "", s.lower())
    p = 0
    for w in words:
        for k in range(p, min(p + 4, len(toks))):
            if norm(toks[k]) == norm(w[2]):
                w[2] = toks[k].replace("AUFLÖSUNG", "Auflösung").replace("RESPUESTA", "Respuesta")
                p = k + 1
                break
    return words


def build_audio(segs, tmp):
    track, timeline, t = [], [], 0.25
    track.append(np.zeros(int(SR * t), np.float32))
    for i, s in enumerate(segs):
        start = t
        if s["kind"] == "countdown":
            words = []
            for n, word in enumerate(L["countdown"]):
                a, w = tts(word + ".", tmp, f"{i}_{n}")
                chunk = np.zeros(int(SR * 1.0), np.float32)
                tk = tick()
                chunk[: len(tk)] += tk
                chunk[int(SR * 0.08): int(SR * 0.08) + len(a[: int(SR * 0.85)])] += a[: int(SR * 0.85)] * 0.9
                track.append(chunk)
                words.append([t - start + 0.08, t - start + 0.6, word])
                t += 1.0
            s["words"] = words
        else:
            a, words = tts(tts_text(s["text"]), tmp, str(i))
            if s["kind"] == "answer":
                d = ding()
                pad = np.zeros(int(SR * 0.45), np.float32)
                pad[: len(d[: len(pad)])] += d[: len(pad)]
                tail = d[len(pad):]
                a = a.copy()
                a[: len(tail)] += tail
                track.append(pad)
                t += len(pad) / SR
                start = t - len(pad) / SR
                words = [[w[0] + len(pad) / SR, w[1] + len(pad) / SR, w[2]] for w in words]
            else:
                wh = whoosh()
                a = a.copy()
                a[: len(wh)] += wh
            track.append(a)
            t += len(a) / SR
            s["words"] = align(words, s["text"])
        gap = 0.3
        track.append(np.zeros(int(SR * gap), np.float32))
        t += gap
        timeline.append((start, t))
    track.append(np.zeros(int(SR * 0.6), np.float32))
    t += 0.6
    audio = np.concatenate(track)
    audio = np.clip(audio / max(1e-6, np.abs(audio).max()) * 0.95, -1, 1)
    wav = tmp / "voice.wav"
    with wave.open(str(wav), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes((audio * 32767).astype(np.int16).tobytes())
    return wav, timeline, t


# ---------------------------------------------------------------- dessin
@lru_cache(maxsize=None)
def font(size):
    return ImageFont.truetype(FONT, size)


@lru_cache(maxsize=None)
def emoji_img(ch):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((80, 80), ch, font=f, embedded_color=True, anchor="mm")
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def split_emojis(s):
    out, i = [], 0
    while i < len(s):
        j = i + 1
        while j < len(s) and s[j] in "️⃣‍":
            j += 1
        out.append(s[i:j])
        i = j
    return out


@lru_cache(maxsize=None)
def emoji_layer(s):
    items = split_emojis(s)
    size = {1: 520, 2: 380, 3: 300}.get(len(items), 260)
    gap = 30
    layer = Image.new("RGBA", (len(items) * (size + gap), size + 40), (0, 0, 0, 0))
    for k, ch in enumerate(items):
        e = emoji_img(ch)
        sc = size / max(e.size)
        e = e.resize((max(1, int(e.width * sc)), max(1, int(e.height * sc))), Image.LANCZOS)
        x = k * (size + gap) + (size - e.width) // 2
        layer.alpha_composite(e, (x, 20 + (size - e.height) // 2))
    return layer


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


@lru_cache(maxsize=None)
def background(color):
    c = np.array(hex2rgb(color), np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2)
    shade = 1.06 - 0.22 * d
    img = np.clip(c[None, None, :] * shade[..., None], 0, 255).astype(np.uint8)
    im = Image.fromarray(img).convert("RGBA")
    dr = ImageDraw.Draw(im)
    dot = tuple(int(v * 0.9) for v in hex2rgb(color)) + (255,)
    for y in range(40, H, 90):
        for x in range(40 + (y // 90 % 2) * 45, W, 90):
            dr.ellipse((x - 4, y - 4, x + 4, y + 4), fill=dot)
    return im


def wrap(text, f, maxw, draw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


@lru_cache(maxsize=None)
def knoedel(size=150):
    """Mascotte : tête de chat orange avec lunettes de détective."""
    s = 4
    im = Image.new("RGBA", (size * s, size * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    S = size * s
    o, ol = (246, 154, 68, 255), (60, 40, 30, 255)
    lw = 6 * s // 2
    d.polygon([(S * .16, S * .42), (S * .22, S * .06), (S * .45, S * .28)], fill=o, outline=ol, width=lw)
    d.polygon([(S * .84, S * .42), (S * .78, S * .06), (S * .55, S * .28)], fill=o, outline=ol, width=lw)
    d.ellipse((S * .1, S * .2, S * .9, S * .95), fill=o, outline=ol, width=lw)
    for x0 in (.36, .64):
        d.line((S * (x0 - .05), S * .24, S * (x0 + .05), S * .3), fill=(220, 120, 40, 255), width=lw)
    for cx in (.35, .65):
        d.ellipse((S * (cx - .13), S * .45, S * (cx + .13), S * .71), fill=(255, 255, 255, 120), outline=(90, 55, 35, 255), width=lw)
        d.ellipse((S * (cx - .045), S * .53, S * (cx + .045), S * .63), fill=ol)
    d.line((S * .48, S * .58, S * .52, S * .58), fill=(90, 55, 35, 255), width=lw)
    d.polygon([(S * .46, S * .73), (S * .54, S * .73), (S * .5, S * .78)], fill=(240, 110, 120, 255))
    d.arc((S * .40, S * .74, S * .5, S * .84), 20, 160, fill=ol, width=lw)
    d.arc((S * .5, S * .74, S * .6, S * .84), 20, 160, fill=ol, width=lw)
    return im.resize((size, size), Image.LANCZOS)


@lru_cache(maxsize=None)
def header(vid, hook):
    im = Image.new("RGBA", (W, 560), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    label = L["brand"]
    f = font(40)
    tw = d.textlength(label, font=f)
    x0 = (W - tw - 150) / 2
    d.rounded_rectangle((x0, 110, x0 + tw + 150, 190), 40, fill=(40, 30, 50, 255))
    im.alpha_composite(knoedel(70), (int(x0 + 22), 115))
    d.text((x0 + 108, 150), label, font=f, fill=(255, 214, 0), anchor="lm")
    f = font(62)
    lines = wrap(hook, f, W - 200, d)
    lh = 76
    top = 225
    hgt = len(lines) * lh + 50
    d.rounded_rectangle((60, top, W - 60, top + hgt), 36, fill=(255, 255, 255, 240), outline=(40, 30, 50, 255), width=6)
    for k, ln in enumerate(lines):
        d.text((W / 2, top + 25 + lh / 2 + k * lh), ln, font=f, fill=(40, 30, 50), anchor="mm")
    return im


def chunk_words(words):
    """Groupes de <= 3 mots, coupés après une ponctuation forte."""
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or re.search(r"[.!?:…,]$", w[2]):
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    return chunks


@lru_cache(maxsize=4096)
def subtitle_img(texts, hi):
    f = font(84)
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    lines = wrap(" ".join(texts), f, W - 220, tmp)
    im = Image.new("RGBA", (W, 120 * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    idx = 0
    for li, ln in enumerate(lines):
        ws = ln.split()
        total = sum(d.textlength(w, font=f) for w in ws) + 34 * (len(ws) - 1)
        x = (W - total) / 2
        y = 20 + li * 120
        for w in ws:
            col = (255, 214, 0) if idx == hi else (255, 255, 255)
            d.text((x, y), w, font=f, fill=col, stroke_width=10, stroke_fill=(25, 20, 30))
            x += d.textlength(w, font=f) + 34
            idx += 1
    return im


@lru_cache(maxsize=None)
def stamp():
    f = font(110)
    im = Image.new("RGBA", (820, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, 810, 210), 26, outline=(220, 30, 40, 255), width=14)
    d.text((410, 112), L["stamp"], font=f, fill=(220, 30, 40, 255), anchor="mm")
    return im.rotate(-8, expand=True, resample=Image.BICUBIC)


def ease_out_back(x):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def render_frame(t, v, segs, timeline):
    si = 0 if t < timeline[0][0] else next((k for k, (a, b) in enumerate(timeline) if a <= t < b), len(segs) - 1)
    s = segs[si]
    a, b = timeline[si]
    lt = max(0.0, t - a)
    frame = background(PASTELS[si % len(PASTELS)]).copy()
    frame.alpha_composite(header(v["id"], v["hook"]), (0, 0))
    cy = 1020
    if s["kind"] == "countdown":
        n = min(4, int(lt))
        frac = lt - int(lt)
        r = 300
        d = ImageDraw.Draw(frame)
        d.ellipse((W / 2 - r, cy - r, W / 2 + r, cy + r), fill=(255, 255, 255, 255), outline=(40, 30, 50, 255), width=12)
        d.arc((W / 2 - r + 30, cy - r + 30, W / 2 + r - 30, cy + r - 30), -90, -90 + 360 * (1 - frac), fill=(255, 90, 90, 255), width=28)
        sc = 1 + 0.25 * max(0, 1 - frac * 5)
        f = font(int(300 * sc))
        d.text((W / 2, cy), str(5 - n), font=f, fill=(40, 30, 50), anchor="mm")
        f2 = font(54)
        d.text((W / 2, cy + r + 90), L["write"], font=f2, fill=(40, 30, 50), anchor="mm")
    elif s["emojis"]:
        layer = emoji_layer(s["emojis"])
        pop = ease_out_back(min(1, lt / 0.35)) if (lt < 0.35 and si > 0) else 1  # 1er plan plein dès l'image 0 (miniature)
        zoom = 1 + 0.06 * min(1, lt / max(1, b - a))
        bob = math.sin(t * 2.2) * 14
        sc = max(0.05, pop * zoom)
        maxw = W - 240
        base = min(1, maxw / layer.width)
        lw, lh = int(layer.width * base * sc), int(layer.height * base * sc)
        if lw > 2 and lh > 2:
            im = layer.resize((lw, lh), Image.BILINEAR)
            frame.alpha_composite(im, (int((W - lw) / 2), int(cy - lh / 2 + bob)))
    if s["kind"] == "answer" and lt < 2.2:
        st = stamp()
        k = min(1, lt / 0.18)
        sc = 2.2 - 1.2 * k
        alpha = 1 if lt < 1.8 else max(0, 1 - (lt - 1.8) / 0.4)
        im = st.resize((int(st.width * sc * 0.9), int(st.height * sc * 0.9)), Image.BILINEAR)
        if alpha < 1:
            arr = np.array(im)
            arr[..., 3] = (arr[..., 3] * alpha).astype(np.uint8)
            im = Image.fromarray(arr)
        frame.alpha_composite(im, (int((W - im.width) / 2), int(575 - im.height / 2)))
    # sous-titres
    if s["kind"] != "countdown":
        chunks = s.get("_chunks")
        if chunks is None:
            chunks = s["_chunks"] = chunk_words(s["words"])
        cur = None
        for c in chunks:
            if c[0][0] <= lt < c[-1][1] + 0.25:
                cur = c
        if cur is None:
            prev = [c for c in chunks if c[0][0] <= lt]
            if prev and lt - prev[-1][-1][1] < 0.6:
                cur = prev[-1]
        if cur:
            hi = max([k for k, w in enumerate(cur) if w[0] <= lt] or [0])
            im = subtitle_img(tuple(w[2] for w in cur), hi)
            frame.alpha_composite(im, (0, 1430))
    return frame


def render(vid, vids):
    v = vids[vid]
    segs = segments(v)
    out_dir = OUT / L["code"]
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"{L['names'][0] if vid[0] == 'S' else L['names'][1]}_{int(vid[1:]):02}"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        wav, timeline, total = build_audio(segs, tmp)
        out = out_dir / f"{name}.mp4"
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-movflags", "+faststart", str(out)]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        nframes = int(total * FPS)
        total_w = W
        for k in range(nframes):
            t = k / FPS
            fr = render_frame(t, v, segs, timeline)
            dr = ImageDraw.Draw(fr)
            dr.rectangle((0, H - 14, int(total_w * t / total), H), fill=(255, 90, 90, 255))
            p.stdin.write(fr.convert("RGB").tobytes())
        p.stdin.close()
        p.wait()
        # sous-titres .srt exacts (temps réels de la voix)
        srt = out_dir / f"{name}.srt"
        n = 0
        with srt.open("w", encoding="utf-8") as f:
            for s, (a, _) in zip(segs, timeline):
                for c in chunk_words(s["words"]) if s["kind"] != "countdown" else [[w] for w in s["words"]]:
                    n += 1
                    ts = lambda x: f"{int(x // 3600):02}:{int(x % 3600 // 60):02}:{int(x % 60):02},{int(x * 1000 % 1000):03}"
                    f.write(f"{n}\n{ts(a + c[0][0])} --> {ts(a + c[-1][1])}\n{' '.join(w[2] for w in c)}\n\n")
    print(f"{out.name}: {total:.1f} s", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    code = "es"
    if args[:1] == ["--lang"]:
        code, args = args[1], args[2:]
    L.clear()
    L.update(LANGS[code], code=code)
    vids = parse()
    ids = args or list(SCENES)
    for vid in ids:
        render(vid, vids)

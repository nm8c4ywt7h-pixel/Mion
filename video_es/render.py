"""Render the Spanish Pipi video: frames (PIL) -> ffmpeg, plus sfx/music mix.

usage: python3 render.py <build_dir> <out.mp4> [--preview N]
build_dir must contain timeline.json + voice.npy (made by voice.py).
"""
import json, math, re, subprocess, sys, os
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw, ImageFont
import scenes
from scenes import W, H, LINE_SHOTS, SHOT_SFX
from sprites import FONT, INK
import sfx

FPS = 30
BUILD = sys.argv[1]
OUT = sys.argv[2]
TL = json.load(open(os.path.join(BUILD, "timeline.json")))
CAP_FONT = ImageFont.truetype(FONT, 118)
YELLOW = (255, 222, 40, 255)


def build_shots():
    shots = []
    lines = TL["lines"]
    for li, line in enumerate(lines):
        fns = LINE_SHOTS[li]
        ws = line["words"]
        start = 0.0 if li == 0 else line["start"]
        end = lines[li + 1]["start"] if li + 1 < len(lines) else TL["total"]
        bounds = [start]
        for k in range(1, len(fns)):
            target = line["start"] + (line["end"] - line["start"]) * k / len(fns)
            w = min(ws[1:], key=lambda w: abs(w[0] - target))
            bounds.append(w[0] - 0.03)
        bounds.append(end)
        for k, fn in enumerate(fns):
            shots.append((bounds[k], bounds[k + 1], fn))
    return shots


def build_captions():
    chunks = []
    for line in TL["lines"]:
        words = line["words"]
        i = 0
        while i < len(words):
            s, e, txt = words[i]
            txt = clean(txt)
            j = i + 1
            # merge short words, but never across a pause (sentence break) or a line
            while (j < len(words) and len(txt.split()) < 2 and words[j][0] - words[j - 1][1] < 0.09
                   and (len(clean(words[j - 1][2])) <= 3 or len(clean(words[j][2])) <= 2)):
                nxt = clean(words[j][2])
                if len(txt) + len(nxt) > 13:
                    break
                txt += " " + nxt
                e = words[j][1]
                j += 1
            if txt:
                chunks.append([s, e, txt])
            i = j
    for k in range(len(chunks) - 1):
        chunks[k][1] = min(chunks[k + 1][0], chunks[k][1] + 0.35)
    return chunks


def clean(t):
    return re.sub(r"[¿?¡!.,:;\"]", "", t).strip()


SHOTS = build_shots()
CAPS = build_captions()


def caption_img(txt):
    f = CAP_FONT
    while f.getlength(txt) > W - 120:
        f = ImageFont.truetype(FONT, f.size - 6)
    im = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((W // 2 + 6, 136), txt, font=f, fill=(0, 0, 0, 120), anchor="mm", stroke_width=16, stroke_fill=(0, 0, 0, 120))
    d.text((W // 2, 130), txt, font=f, fill=YELLOW, anchor="mm", stroke_width=14, stroke_fill=INK)
    return im


_cap_cache = {}


def frame(n):
    t = n / FPS
    for si, (s, e, fn) in enumerate(SHOTS):
        if s <= t < e or si == len(SHOTS) - 1:
            break
    lt, dur = t - s, e - s
    base, els = fn(lt, dur)
    im = base.copy()
    for el in els:
        if el.img is None:
            continue
        im.alpha_composite(el.img, (int(el.x - el.img.width / 2), int(el.y - el.img.height)))
    # camera: punch-in at cut + slow push
    jump = 0.0
    if dur > 2.6 and lt > dur / 2:  # jump-cut reframe in long shots keeps the ~2s rhythm
        lt -= dur / 2
        dur /= 2
        jump = 0.12
    punch = 0.10 * max(0.0, 1 - lt / 0.18) ** 2
    z = 1.0 + 0.05 * min(1, lt / max(dur, 0.1)) + punch + jump
    if si % 2:  # alternate slow zoom direction for variety
        z = 1.05 - 0.05 * min(1, lt / max(dur, 0.1)) + punch + jump
    cw, ch = W / z, H / z
    x0, y0 = (W - cw) / 2, (H - ch) / 2 - (H - ch) * 0.1
    im = im.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
    # white flash on hook start
    if t < 0.08:
        im = Image.blend(im, Image.new("RGBA", (W, H), (255, 255, 255, 255)), 0.6)
    # caption
    for cs, ce, txt in CAPS:
        if cs <= t < ce:
            if txt not in _cap_cache:
                _cap_cache[txt] = caption_img(txt)
            c = _cap_cache[txt]
            k = scenes.ease_out_back((t - cs) / 0.12)
            k = 0.7 + 0.3 * k
            cw2, ch2 = int(c.width * k), int(c.height * k)
            cc = c.resize((cw2, ch2), Image.BILINEAR)
            im.alpha_composite(cc, ((W - cw2) // 2, 1290 - ch2 // 2))
            break
    return im.convert("RGB").tobytes()


def audio(total):
    SR = sfx.SR
    voice = np.load(os.path.join(BUILD, "voice.npy"))
    n = int(total * SR)
    mix = np.zeros(n, np.float32)
    mix[:len(voice)] += voice[:n] * 1.0
    fx = np.zeros(n, np.float32)
    for si, (s, e, fn) in enumerate(SHOTS):
        if si:
            sfx.add(fx, sfx.whoosh(), s - 0.08, 0.22)
        for kind, off in SHOT_SFX.get(fn.__name__, []):
            dur = e - s
            sfx.add(fx, sfx.make(kind, dur), s + off, sfx.GAIN.get(kind, 0.3))
    mus = sfx.music(total)
    # duck music under voice
    env = np.abs(voice)
    k = int(0.15 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    duck = np.ones(n, np.float32)
    duck[:len(env)] = 1 - 0.55 * np.clip(env[:n] / 0.05, 0, 1)
    mix += fx + mus[:n] * 0.11 * duck
    fade = int(1.2 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(mix))
    mix = np.tanh(mix / peak * 1.3) * 0.92
    return (mix * 32767).astype(np.int16)


if __name__ == "__main__":
    total = TL["total"]
    nframes = int(total * FPS)
    preview = None
    if "--preview" in sys.argv:
        preview = [int(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        for f in preview:
            Image.frombytes("RGB", (W, H), frame(f)).save(f"{OUT}_{f}.jpg", quality=80)
        sys.exit()
    wav = OUT + ".wav"
    import wave
    a = audio(total)
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sfx.SR); w.writeframes(a.tobytes())
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                           OUT], stdin=subprocess.PIPE)
    with Pool(4) as pool:
        for i, b in enumerate(pool.imap(frame, range(nframes), chunksize=8)):
            ff.stdin.write(b)
            if i % 300 == 0:
                print(f"{i}/{nframes}", flush=True)
    ff.stdin.close()
    ff.wait()
    print("done", OUT)

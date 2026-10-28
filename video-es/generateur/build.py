"""Génère la vidéo finale : dessins -> voix off ES (gTTS) -> plans zoomés -> sous-titres pop -> sons + musique.
Usage : python3 build.py <dossier_travail> <sortie.mp4>
Dépendances : Pillow, gTTS (pip install gTTS), ffmpeg.
"""
import os
import subprocess
import sys

from dessin import Canvas
from scenes import PLANS

WORK, OUT = sys.argv[1], sys.argv[2]
FPS = 30
SPEED = 1.18  # gTTS parle lentement : on accélère pour coller au rythme de la référence
os.makedirs(WORK, exist_ok=True)


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         check=True, capture_output=True, text=True).stdout
    return float(out)


def voice(i, text):
    from gtts import gTTS
    raw, wav = f"{WORK}/v{i:02d}.mp3", f"{WORK}/v{i:02d}.wav"
    if not os.path.exists(raw):
        gTTS(text, lang="es", tld="es").save(raw)
    run("ffmpeg", "-y", "-i", raw, "-af",
        f"silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
        f"silenceremove=start_periods=1:start_threshold=-45dB,areverse,atempo={SPEED}",
        "-ar", "44100", "-ac", "2", wav)
    return wav


def sfx():
    """Sons synthétisés (pas de banque de sons externe)."""
    run("ffmpeg", "-y", "-f", "lavfi", "-i", "anoisesrc=d=0.45:c=pink:a=0.6", "-af",
        "highpass=f=400,lowpass=f=3000,afade=t=in:d=0.25,afade=t=out:st=0.25:d=0.2,volume=0.5",
        "-ar", "44100", "-ac", "2", f"{WORK}/whoosh.wav")
    run("ffmpeg", "-y", "-f", "lavfi", "-i", "sine=f=900:d=0.12", "-af",
        "vibrato=f=30:d=0.5,afade=t=out:st=0.02:d=0.1,volume=0.6",
        "-ar", "44100", "-ac", "2", f"{WORK}/pop.wav")
    run("ffmpeg", "-y", "-f", "lavfi", "-i", "sine=f=55:d=0.7", "-af",
        "afade=t=out:st=0.05:d=0.65,volume=1.6", "-ar", "44100", "-ac", "2", f"{WORK}/boom.wav")


def music(total):
    """Nappe douce et mystérieuse (accords La mineur / Fa / Do / Sol) en boucle."""
    chords = [(220, 261.6, 329.6), (174.6, 220, 261.6), (261.6, 329.6, 392), (196, 246.9, 293.7)]
    parts = []
    for k, ch in enumerate(chords):
        f = f"{WORK}/ch{k}.wav"
        expr = "+".join(f"sin(2*PI*{hz}*t)" for hz in ch)
        run("ffmpeg", "-y", "-f", "lavfi", "-i", f"aevalsrc=0.12*({expr})*(0.6+0.4*sin(2*PI*0.5*t)):d=4:s=44100",
            "-af", "afade=t=in:d=0.6,afade=t=out:st=3.4:d=0.6,lowpass=f=1200", "-ac", "2", f)
        parts.append(f)
    with open(f"{WORK}/ch.txt", "w") as fh:
        fh.write("".join(f"file '{p}'\n" for p in parts) * (int(total // 16) + 2))
    run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{WORK}/ch.txt", "-t", str(total), f"{WORK}/music.wav")


def ass_time(t):
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def main():
    sfx()
    clips, voices, events, cues = [], [], [], []
    t = 0.0
    for i, (draw, text, word, sound) in enumerate(PLANS, 1):
        img = f"{WORK}/{i:02d}.png"
        c = Canvas((255, 255, 255)); draw(c); c.final().save(img)
        wav = voice(i, text)
        d = max(duration(wav) + 0.18, 1.2)
        if i == len(PLANS):
            d += 1.5
        n = int(round(d * FPS)); d = n / FPS
        clip = f"{WORK}/c{i:02d}.mp4"
        # zoom avant lent continu + petit "punch" d'entrée (102 % -> 100 % puis montée à 108 %)
        z = f"if(lt(on,4),1.06-0.015*on,1.0+0.08*on/{n})"
        run("ffmpeg", "-y", "-loop", "1", "-i", img, "-vf",
            f"scale=2160:3840,zoompan=z='{z}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={n}:s=1080x1920:fps={FPS}",
            "-frames:v", str(n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", clip)
        clips.append(clip)
        voices.append((wav, t))
        if sound:
            cues.append((f"{WORK}/{sound}.wav", t))
        if word:
            events.append(f"Dialogue: 0,{ass_time(t + 0.05)},{ass_time(t + d)},Mot,,0,0,0,,"
                          r"{\fscx30\fscy30\t(0,110,\fscx118\fscy118)\t(110,200,\fscx100\fscy100)}" + word)
        t += d
    total = t

    with open(f"{WORK}/clips.txt", "w") as fh:
        fh.write("".join(f"file '{p}'\n" for p in clips))
    run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{WORK}/clips.txt", "-c", "copy", f"{WORK}/video.mp4")

    with open(f"{WORK}/subs.ass", "w") as fh:
        fh.write("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n\n"
                 "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
                 "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
                 "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
                 "Style: Mot,DejaVu Sans,96,&H00FFFFFF,&H00FFFFFF,&H00332243,&H64000000,1,0,0,0,100,100,0,0,1,"
                 "9,4,2,40,40,330,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, "
                 "MarginV, Effect, Text\n" + "\n".join(events) + "\n")

    music(total)
    inputs, labels, filters = [], [], []
    for k, (path, start) in enumerate(voices + cues):
        inputs += ["-i", path]
        ms = int(start * 1000)
        filters.append(f"[{k}:a]adelay={ms}|{ms}[a{k}]")
        labels.append(f"[a{k}]")
    nv = len(voices)
    filters.append("".join(labels[:nv]) + f"amix=inputs={nv}:normalize=0,volume=1.6[voix]")
    filters.append("".join(labels[nv:]) + f"amix=inputs={len(cues)}:normalize=0,volume=0.7[fx]")
    m = len(voices + cues)
    inputs += ["-i", f"{WORK}/music.wav"]
    filters.append(f"[{m}:a]volume=0.35[mus];[voix]asplit[v1][v2];"
                   "[mus][v2]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=400[musd];"
                   f"[v1][fx][musd]amix=inputs=3:normalize=0:duration=longest,apad,atrim=0:{total:.3f},"
                   "alimiter=limit=0.95[mix]")
    run("ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters), "-map", "[mix]",
        "-ar", "44100", f"{WORK}/audio.wav")

    run("ffmpeg", "-y", "-i", f"{WORK}/video.mp4", "-i", f"{WORK}/audio.wav",
        "-vf", f"ass={WORK}/subs.ass", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium",
        "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
        "-movflags", "+faststart", OUT)
    print(f"OK {OUT} ({total:.1f} s)")


if __name__ == "__main__":
    main()

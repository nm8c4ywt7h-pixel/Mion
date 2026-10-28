"""Synthesised sound effects + light background loop (no external samples)."""
import numpy as np

SR = 44100
rng = np.random.default_rng(7)


def _t(d):
    return np.arange(int(d * SR)) / SR


def _env(n, a=0.005, r=None):
    e = np.ones(n, np.float32)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    if r:
        e *= np.exp(-np.arange(n) / (r * SR))
    return e


def _lp(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def whoosh(d=0.3):
    n = int(d * SR)
    x = rng.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32)
    seg = n // 12
    for i in range(12):  # sweep a crude band-pass upward
        k = int(40 - i * 3)
        part = x[i * seg:(i + 1) * seg + 200]
        out[i * seg:i * seg + len(part)] += (_lp(part, k) - _lp(part, k * 4))[: len(out[i * seg:i * seg + len(part)])]
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return out * e * 3


def pop():
    t = _t(0.09)
    f = 900 * np.exp(-t * 30) + 250
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.03)


def ding():
    t = _t(0.9)
    return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 2637 * t) + 0.25 * np.sin(2 * np.pi * 1976 * t)) * _env(len(t), 0.002, 0.25) * 0.6


def boom():
    t = _t(0.9)
    f = 110 * np.exp(-t * 6) + 40
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.002, 0.35)
    x += _lp(rng.standard_normal(len(t)), 20) * _env(len(t), 0.001, 0.06) * 2
    return x


def boing():
    t = _t(0.45)
    f = 220 + 160 * np.sin(2 * np.pi * 14 * t) * np.exp(-t * 6) + 200 * t
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.003, 0.2)


def buzz():
    t = _t(0.45)
    x = np.sign(np.sin(2 * np.pi * 140 * t)) * 0.5 + np.sign(np.sin(2 * np.pi * 147 * t)) * 0.5
    return _lp(x, 6) * _env(len(t), 0.005) * np.linspace(1, 0.6, len(t))


def tick(d=2.0):
    n = int(d * SR)
    out = np.zeros(n, np.float32)
    for i, s in enumerate(np.arange(0, d, 0.5)):
        t = _t(0.03)
        c = np.sin(2 * np.pi * (2400 if i % 2 else 1800) * t) * _env(len(t), 0.0005, 0.006)
        p = int(s * SR)
        out[p:p + len(c)] += c[: n - p]
    return out


def mystery():
    t = _t(1.4)
    x = np.zeros(len(t))
    for i, f in enumerate((392, 466, 554, 659)):
        st = int(i * 0.12 * SR)
        tt = t[: len(t) - st]
        x[st:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3) * 0.5
    return x * _env(len(t), 0.004)


def sniff():
    n = int(0.75 * SR)
    out = np.zeros(n, np.float32)
    for i in range(3):
        m = int(0.14 * SR)
        nz = rng.standard_normal(m)
        nz = nz - _lp(nz, 8)
        out[int(i * 0.22 * SR):int(i * 0.22 * SR) + m] += nz * np.sin(np.linspace(0, np.pi, m)) * 0.7
    return out


def chomp():
    n = int(0.5 * SR)
    out = np.zeros(n, np.float32)
    for i in range(2):
        m = int(0.08 * SR)
        nz = _lp(rng.standard_normal(m), 4) * _env(m, 0.001, 0.02) * 1.5
        out[int(i * 0.2 * SR):int(i * 0.2 * SR) + m] += nz
    return out


def drop():
    t = _t(0.5)
    f = 700 * np.exp(-t * 4) + 150
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5 * (t < 0.3)
    x[int(0.3 * SR):] += _lp(rng.standard_normal(len(t) - int(0.3 * SR)), 10) * 2 * _env(len(t) - int(0.3 * SR), 0.001, 0.04)
    return x


def whistle():
    t = _t(0.5)
    f = 1800 + 200 * np.sin(2 * np.pi * 30 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(len(t), 0.01) * np.linspace(1, 0.3, len(t)) * 0.5


def scratch():
    t = _t(0.45)
    f = 600 * np.abs(np.sin(2 * np.pi * 3 * t)) + 100
    nz = rng.standard_normal(len(t))
    x = (nz - _lp(nz, 3)) * 0.3 + np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6
    return x * _env(len(t), 0.002) * np.linspace(1, 0.2, len(t))


def sparkle_s():
    t = _t(0.9)
    x = np.zeros(len(t))
    for i, f in enumerate((1568, 2093, 2637, 3136, 2637)):
        st = int(i * 0.07 * SR)
        tt = t[: len(t) - st]
        x[st:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 9) * 0.35
    return x


def heart(d=2.5):
    n = int(d * SR)
    out = np.zeros(n, np.float32)
    t = _t(0.12)
    th = np.sin(2 * np.pi * 55 * t) * _env(len(t), 0.002, 0.04)
    for s in np.arange(0, d, 0.55):
        for off in (0, 0.16):
            p = int((s + off) * SR)
            out[p:p + len(th)] += th[: max(0, n - p)] * (1 if off == 0 else 0.7)
    return out * 1.8


def slot(d=2.0):
    n = int(d * SR)
    out = np.zeros(n, np.float32)
    t = _t(0.025)
    c = np.sin(2 * np.pi * 1500 * t) * _env(len(t), 0.0005, 0.005)
    for s in np.arange(0, d * 0.6, 0.06):
        p = int(s * SR)
        out[p:p + len(c)] += c[: n - p]
    dg = ding()
    p = int(d * 0.6 * SR)
    out[p:p + len(dg)] += dg[: n - p]
    return out


def make(kind, dur):
    return {
        "pop": pop, "ding": ding, "boom": boom, "boing": boing, "buzz": buzz, "mystery": mystery, "sniff": sniff,
        "chomp": chomp, "drop": drop, "whistle": whistle, "scratch": scratch, "sparkle": sparkle_s,
        "tick": lambda: tick(dur), "heart": lambda: heart(dur), "slot": lambda: slot(dur),
    }[kind]()


GAIN = {"pop": 0.28, "ding": 0.22, "boom": 0.55, "boing": 0.3, "buzz": 0.16, "mystery": 0.22, "sniff": 0.35,
        "chomp": 0.4, "drop": 0.3, "whistle": 0.15, "scratch": 0.3, "sparkle": 0.22, "tick": 0.3, "heart": 0.45,
        "slot": 0.28}


def add(buf, x, at, gain):
    p = int(max(0, at) * SR)
    if p >= len(buf):
        return
    x = np.asarray(x, np.float32)[: len(buf) - p]
    buf[p:p + len(x)] += x * gain


def _pluck(f, d=0.5):
    n = int(d * SR)
    N = int(SR / f)
    buf = rng.uniform(-1, 1, N)
    out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % N]
        buf[i % N] = 0.497 * (buf[i % N] + buf[(i + 1) % N])
    return out


def music(total):
    """Bouncy ukulele-style loop, 112 bpm: C - Am - F - G."""
    beat = 60 / 112
    chords = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
    bar = 4 * beat
    loop = np.zeros(int(bar * 4 * SR) + SR)
    plucks = {}
    for ci, ch in enumerate(chords):
        for b in range(8):  # eighth-note strums
            st = ci * bar + b * beat / 2
            accent = 1.0 if b % 2 == 0 else 0.6
            for k, f in enumerate(ch):
                if f not in plucks:
                    plucks[f] = _pluck(f, 0.45)
                p = int((st + k * 0.012) * SR)
                loop[p:p + len(plucks[f])] += plucks[f] * accent * 0.4
        # bass + soft kick on beats 1 and 3
        for b in (0, 2):
            st = int((ci * bar + b * beat) * SR)
            t = _t(0.25)
            loop[st:st + len(t)] += np.sin(2 * np.pi * ch[0] / 2 * t) * np.exp(-t * 8) * 0.5
            f = 120 * np.exp(-t * 25) + 45
            loop[st:st + len(t)] += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.6
    L = int(bar * 4 * SR)
    loop = loop[:L]
    reps = int(np.ceil(total * SR / L)) + 1
    m = np.tile(loop, reps)[: int(total * SR)]
    return (m / np.max(np.abs(m))).astype(np.float32)

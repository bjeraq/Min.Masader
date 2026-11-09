"""Mix narration + AI music + synthesized cartoon SFX, then loudness-normalize for social video."""
import json, subprocess
import numpy as np
from scipy.signal import butter, sosfilt, lfilter
from scipy.io import wavfile

SP = '/tmp/claude-0/-home-user-min-masader/59b58237-73e8-5a26-8661-efeb42e64c46/scratchpad/rail'
SR = 44100
TL = json.load(open(f'{SP}/build/timeline.json'))
import sys
EV = json.load(open(sys.argv[1] if len(sys.argv) > 1 else f'{SP}/build/events_rail.json'))
OUTW = sys.argv[2] if len(sys.argv) > 2 else f'{SP}/build/mix_final.wav'
MUSIC = sys.argv[3] if len(sys.argv) > 3 else f'{SP}/music/music.mp3'
TOTAL = TL['total']
N = int(TOTAL * SR)
rng = np.random.default_rng(3)


def load(path, stereo=False):
    ch = '2' if stereo else '1'
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', ch, '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    return x.reshape(-1, 2) if stereo else x


def add(buf, t0, x, g=1.0):
    i = int(round(t0 * SR))
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(buf), i + len(x))
    if j > i:
        buf[i:j] += g * x[:j - i]


def tt(dur):
    return np.arange(int(dur * SR)) / SR


def env_exp(n, k):
    return np.exp(-k * np.linspace(0, 1, n))


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)


def hp(x, f):
    return sosfilt(butter(2, f, btype='high', fs=SR, output='sos'), x)


def lp(x, f):
    return sosfilt(butter(2, f, btype='low', fs=SR, output='sos'), x)


def norm(x):
    return x / (np.max(np.abs(x)) + 1e-9)


# ---------------- synthesized cartoon SFX ----------------
def sfx_kaching():
    d = 1.1; t = tt(d)
    bell = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-k * t) for f, a, k in
               [(2093, .5, 4), (2637, .35, 5), (3136, .3, 6), (4186, .2, 7), (5274, .1, 9)])
    cha = np.zeros_like(t); nb = norm(bp(rng.standard_normal(int(.07 * SR)), 2500, 7000)) * env_exp(int(.07 * SR), 6)
    cha[:len(nb)] = nb
    bell2 = np.zeros_like(t); off = int(.09 * SR); bell2[off:] = bell[:len(t) - off]
    return norm(0.55 * cha + 0.7 * bell2) * 0.9


def sfx_pop():
    d = .12; t = tt(d); f = np.linspace(950, 320, len(t))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-30 * t)
    return norm(x) * 0.8


def sfx_bigpop():
    d = .35; t = tt(d); f = np.linspace(700, 180, len(t))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-12 * t)
    sparkle = sum(np.sin(2 * np.pi * fr * t) * np.exp(-14 * t) for fr in (1568, 2093, 2637)) / 3
    return norm(body + 0.35 * sparkle) * 0.95


def sfx_whoosh(d=.55):
    n = int(d * SR); x = rng.standard_normal(n)
    a = bp(x, 300, 1200); b = bp(x, 1200, 4500)
    w = np.sin(np.pi * np.linspace(0, 1, n))
    y = (1 - w) * a + w * b
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return norm(y * e) * 0.7


def sfx_deepwhoosh():
    n = int(1.4 * SR); x = rng.standard_normal(n)
    y = lp(x, 900) * np.linspace(0.2, 1, n) ** 2 * np.concatenate([np.ones(n - int(.35 * SR)), np.linspace(1, 0, int(.35 * SR))])
    sub = np.sin(2 * np.pi * np.cumsum(np.linspace(60, 110, n)) / SR) * np.linspace(0, 1, n) ** 3
    return norm(norm(y) + 0.5 * sub) * 0.8


def sfx_stamp():
    d = .4; t = tt(d)
    thump = np.sin(2 * np.pi * np.cumsum(np.linspace(110, 45, len(t))) / SR) * np.exp(-14 * t)
    slap = np.zeros_like(t); nb = lp(rng.standard_normal(int(.05 * SR)), 1800) * env_exp(int(.05 * SR), 8)
    slap[:len(nb)] = norm(nb)
    return norm(thump + 0.6 * slap) * 0.95


def sfx_coins():
    d = 1.3; out = np.zeros(int(d * SR))
    for k in range(9):
        t0 = k * 0.11 + rng.uniform(0, .04)
        dd = .25; t = tt(dd)
        hit = sum(np.sin(2 * np.pi * f * t) for f in rng.uniform(3200, 7200, 3)) * np.exp(-28 * t)
        add(out, t0, norm(hit) * (0.9 - 0.06 * k))
    return norm(out) * 0.7


def sfx_canopen():
    click = np.zeros(int(.7 * SR))
    c = norm(bp(rng.standard_normal(int(.02 * SR)), 900, 4000)) * env_exp(int(.02 * SR), 4)
    click[:len(c)] = c
    hiss = norm(hp(rng.standard_normal(int(.6 * SR)), 4000)) * np.exp(-5 * np.linspace(0, 1, int(.6 * SR))) * 0.45
    click[int(.03 * SR):int(.03 * SR) + len(hiss)] += hiss
    return norm(click) * 0.8


def sfx_fizz():
    n = int(1.2 * SR); x = norm(hp(rng.standard_normal(n), 5000)) * 0.25
    crack = (rng.random(n) > 0.9993).astype(float) * rng.uniform(.3, 1, n)
    crack = bp(crack, 3000, 9000)
    e = np.concatenate([np.linspace(0, 1, int(.05 * SR)), np.linspace(1, 0, n - int(.05 * SR))])
    return norm((x + 4 * crack) * e) * 0.5


def sfx_cube():
    d = .12; t = tt(d)
    x = np.sin(2 * np.pi * 1250 * t) * np.exp(-45 * t) + 0.4 * norm(bp(rng.standard_normal(len(t)), 1500, 5000)) * np.exp(-60 * t)
    return norm(x) * 0.6


def sfx_ding():
    d = 1.0; t = tt(d)
    x = (np.sin(2 * np.pi * 1318.5 * t) + .5 * np.sin(2 * np.pi * 1975.5 * t)) * np.exp(-4.5 * t)
    return norm(x) * 0.7


def sfx_tick():
    d = .05; t = tt(d)
    x = np.sin(2 * np.pi * 2400 * t) * np.exp(-90 * t)
    return norm(x) * 0.5


def sfx_clock(hi=[True]):
    d = .06; t = tt(d); f = 3000 if hi[0] else 2300; hi[0] = not hi[0]
    x = norm(bp(rng.standard_normal(len(t)), f - 600, f + 600)) * np.exp(-70 * t)
    return x * 0.45


def sfx_chime():
    d = 1.6; t = tt(d)
    x = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-k * t) for f, a, k in [(880, .6, 3), (1320, .4, 3.5), (1760, .25, 4)])
    return norm(x) * 0.7


def sfx_chug():
    d = 5.8; out = np.zeros(int(d * SR))
    rumble = lp(rng.standard_normal(int(d * SR)), 300) * 0.12
    e = np.concatenate([np.linspace(0, 1, int(.5 * SR)), np.ones(int((d - 1.3) * SR)), np.linspace(1, 0, int(.8 * SR))])
    out += norm(rumble)[:len(out)] * 0.4
    t0 = 0.1
    while t0 < d - 0.6:
        for dt, g in ((0.0, 1.0), (0.11, 0.7)):
            cl = norm(bp(rng.standard_normal(int(.05 * SR)), 500, 2200)) * env_exp(int(.05 * SR), 7)
            add(out, t0 + dt, cl, 0.5 * g)
        t0 += 0.46
    out *= np.resize(e, len(out))
    return norm(out) * 0.5


def sfx_horn():
    d = 0.8; t = tt(d)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
    x = np.sin(2 * np.pi * 392 * t * vib) + 0.8 * np.sin(2 * np.pi * 494 * t * vib)
    e = np.minimum(1, t / 0.05) * np.exp(-2.2 * t)
    return norm(lp(x * e, 2500)) * 0.6


SFX = {'kaching': sfx_kaching, 'pop': sfx_pop, 'bigpop': sfx_bigpop, 'whoosh': sfx_whoosh,
       'deepwhoosh': sfx_deepwhoosh, 'stamp': sfx_stamp, 'coins': sfx_coins, 'canopen': sfx_canopen,
       'fizz': sfx_fizz, 'cube': sfx_cube, 'ding': sfx_ding, 'tick': sfx_tick, 'clock': sfx_clock, 'chime': sfx_chime, 'chug': sfx_chug, 'horn': sfx_horn}

# ---------------- buses ----------------
voice = np.zeros(N)
for s in TL['scenes']:
    x = load(f"{SP}/narr_f/n{s['n']:02d}.wav")
    rms = np.sqrt(np.mean(x ** 2)) + 1e-9
    add(voice, s['voice'], x * (0.12 / rms))
voice = np.clip(voice, -0.98, 0.98)

sfx = np.zeros(N)
for name, t0, g in EV:
    add(sfx, t0, SFX[name](), g)

music = load(MUSIC, stereo=True)
mus = np.zeros((N, 2)); m = min(N, len(music)); mus[:m] = music[:m]

# sidechain ducking driven by the voice envelope (attack 60 ms, release 450 ms)
envv = np.abs(voice)
win = int(.03 * SR)
envv = np.convolve(envv, np.ones(win) / win, mode='same')
target = np.where(envv > 0.01, 1.0, 0.0)
a_att = np.exp(-1 / (0.06 * SR)); a_rel = np.exp(-1 / (0.45 * SR))
up = lfilter([1 - a_att], [1, -a_att], target)
down = lfilter([1 - a_rel], [1, -a_rel], target)
duck_ctl = np.maximum(up, down)
music_gain = 0.42 - 0.27 * np.clip(duck_ctl, 0, 1)   # ~ -7.5 dB unducked, ~ -16 dB under voice
mus *= music_gain[:, None]
nf = int(1.5 * SR); mus[-nf:] *= np.linspace(1, 0, nf)[:, None] ** 2   # safety tail fade

mix = np.zeros((N, 2))
mix += voice[:, None] * 1.0
mix += sfx[:, None] * 0.30
mix += mus
# gentle stereo width for sfx (tiny delay on right channel)
dly = int(.008 * SR); mix[dly:, 1] += sfx[:-dly] * 0.04

peak = np.max(np.abs(mix)); mix = mix / max(1.0, peak / 0.95)
wavfile.write(f'{SP}/build/mix_raw.wav', SR, (mix * 32767).astype(np.int16))

# EBU R128 loudness normalisation for social platforms (-14 LUFS, TP -1.5)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', f'{SP}/build/mix_raw.wav', '-af',
                'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=summary', '-ar', '48000',
                OUTW], check=True)
print('mix done', round(N / SR, 2), 's')

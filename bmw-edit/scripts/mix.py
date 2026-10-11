#!/usr/bin/env python3
"""Sound design + music mix, locked to events.json from render.py. Writes work/mix.wav (48k stereo)."""
import json, os, subprocess, math, numpy as np, soundfile as sf
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
ev = json.load(open(os.path.join(BASE, 'work', 'events.json')))
T = ev['total']; N = int(T*SR) + SR
EXH = '/home/user/sathyaram/exhaustnotes/public/sounds/'

def load(path, start=0.0, dur=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{start}', '-i', path] + (['-t', f'{dur}'] if dur else []) + \
          ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, 2).copy()

def db(x): return 10**(x/20)
def fade(a, fi=0.01, fo=0.01):
    a = a.copy(); n = len(a)
    i = min(n, int(fi*SR)); o = min(n, int(fo*SR))
    if i: a[:i] *= np.linspace(0, 1, i)[:, None]
    if o: a[n-o:] *= np.linspace(1, 0, o)[:, None]
    return a
def place(bus, a, t, g=1.0):
    s = int(round(t*SR))
    if s < 0: a = a[-s:]; s = 0
    e = min(len(bus), s + len(a)); bus[s:e] += a[:e-s]*g
def norm_peak(a, p=0.98): return a/(np.abs(a).max() + 1e-9)*p
def rms_db(a): return 20*np.log10(np.sqrt((a**2).mean()) + 1e-9)
def set_rms(a, target): return a*db(target - rms_db(a))

def lowpass(a, fc):
    k = math.exp(-2*math.pi*fc/SR); y = np.empty_like(a); z = np.zeros(a.shape[1], np.float32)
    # vectorised enough for short clips
    for i in range(len(a)): z = (1-k)*a[i] + k*z; y[i] = z
    return y
def onepole_hp_fft(a, fc):
    F = np.fft.rfft(a, axis=0); f = np.fft.rfftfreq(len(a), 1/SR)
    F *= (1/(1 + (fc/np.maximum(f, 1))**4))[:, None]
    return np.fft.irfft(F, len(a), axis=0).astype(np.float32)
def fft_lowpass(a, fc):
    F = np.fft.rfft(a, axis=0); f = np.fft.rfftfreq(len(a), 1/SR)
    F *= (1/(1 + (f/fc)**4))[:, None]
    return np.fft.irfft(F, len(a), axis=0).astype(np.float32)

rng = np.random.default_rng(3)
def whoosh(dur, peak_at, f0=300, f1=4000, width=1.2):
    """band-limited noise sweep, peaking at peak_at seconds"""
    n = int(dur*SR); noise = rng.standard_normal((n, 2)).astype(np.float32)
    out = np.zeros_like(noise); blk = 1024
    win = np.hanning(blk*2).astype(np.float32)[:, None]
    for s in range(0, n - blk, blk):
        seg = noise[s:s+blk*2] if s + blk*2 <= n else np.pad(noise[s:], ((0, s+blk*2-n), (0, 0)))
        tc = (s + blk)/SR; u = min(1, tc/peak_at) if tc < peak_at else 1 - (tc - peak_at)/(dur - peak_at)
        fc = f0*(f1/f0)**max(0, min(1, u))
        F = np.fft.rfft(seg*win, axis=0); f = np.fft.rfftfreq(blk*2, 1/SR)
        F *= np.exp(-0.5*(np.log(np.maximum(f, 1)/fc)/(0.5*width))**2)[:, None]
        o = np.fft.irfft(F, blk*2, axis=0); e = min(n, s+blk*2); out[s:e] += o[:e-s]
    t = np.arange(n)/SR
    env = np.where(t < peak_at, (t/peak_at)**2.2, np.exp(-(t - peak_at)/(0.18)))
    return norm_peak(out*env[:, None], 0.9)
def boom(dur=1.4, f0=70, f1=32):
    t = np.arange(int(dur*SR))/SR
    f = f1 + (f0 - f1)*np.exp(-t/0.12); ph = 2*np.pi*np.cumsum(f)/SR
    s = np.sin(ph)*np.exp(-t/0.45)*np.minimum(1, t/0.004)
    return np.stack([s, s], 1).astype(np.float32)
def echo(a, delays=((0.17, 0.45), (0.34, 0.25), (0.51, 0.12), (0.68, 0.06))):
    out = np.zeros((len(a) + int(0.8*SR), 2), np.float32); out[:len(a)] += a
    for d, g in delays:
        s = int(d*SR); out[s:s+len(a)] += fft_lowpass(a, 3500)*g*np.array([1.0, 0.8] if d % 0.34 else [0.8, 1.0], np.float32)
    return out

def varispeed(src, src_start, rates, t_len):
    """play src (array) from src_start with a per-output-sample rate curve"""
    pos = src_start*SR + np.concatenate([[0], np.cumsum(rates[:-1])])
    idx = np.arange(len(src))
    return np.stack([np.interp(pos, idx, src[:, c]) for c in range(2)], 1).astype(np.float32)

# ------------------------------------------------------------------ sources
song = load(os.path.join(BASE, 'src', 'song.mp3'), ev['song_offset'], T + 0.5)
amg = load(EXH + 'amggtr.m4a'); e63 = load(EXH + 'e63.m4a'); ftype = load(EXH + 'ftype.m4a')
def sl(a, t0, t1): return a[int(t0*SR):int(t1*SR)].copy()

music = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32); eng = np.zeros((N, 2), np.float32)
place(music, song, 0.0)
music[:int(0.12*SR)] *= np.linspace(0, 1, int(0.12*SR))[:, None]
fo = int(2.2*SR); e = int(T*SR); music[e-fo:e] *= np.linspace(1, 0, fo)[:, None]**1.5; music[e:] = 0
mus_rms = rms_db(song[int(12*SR):int(20*SR)])

st = ev['starts']; cuts = ev['cuts']; ps = ev['poster_start']
# idle rumble (AMG GT settles into a hard idle at the end of its recording) looped under the intro
idle = sl(amg, 21.55, 23.75); idle = set_rms(idle, mus_rms - 15)
def loop_bed(clip, t0, t1, g=1.0):
    xf = int(0.25*SR); step = len(clip) - xf; t = t0
    while t < t1:
        c = fade(clip, 0.25, 0.25); place(eng, c, t, g); t += step/SR
loop_bed(idle, 0.0, st['D'] + 0.2)
# swell the idle in from the intro
env = np.ones(N, np.float32); a = int(0.0*SR); b = int(2.0*SR); env[a:b] = np.linspace(0.25, 1, b-a)
d0 = int((st['D'] + 0.25)*SR); env[d0:] = 0
eng *= env[:, None]

# ---- C: revs + backfires locked to the beat
pops = ev['pops']
rev1 = fade(sl(e63, 12.70, 14.10), 0.25, 0.25); place(fx, set_rms(rev1, mus_rms - 4), pops[0] - (13.64 - 12.70))
pop2 = fade(sl(amg, 13.62, 14.15), 0.05, 0.15); place(fx, set_rms(pop2, mus_rms - 4), pops[1] - (13.81 - 13.62))
dbl = fade(sl(e63, 6.75, 8.10), 0.3, 0.2); place(fx, set_rms(dbl, mus_rms - 3), pops[2] - (7.55 - 6.75))

# ---- D: the launch and the drift, engine follows the edit's speed ramps (varispeed = real slow-mo audio)
dsp = np.array(ev['d_speed']); dn = len(dsp); dt = dn/60
tt = np.arange(int(dt*SR))/SR
spd = np.interp(tt, np.arange(dn)/60, dsp)
rate = np.clip(spd, 0.5, 1.0)
rate = np.convolve(rate, np.ones(2400)/2400, mode='same')
drive = varispeed(amg, 0.35, rate, len(tt))
drive = set_rms(drive, mus_rms - 4.5)
slow = (spd < 0.6).astype(np.float32); slow = np.convolve(slow, np.ones(4800)/4800, mode='same')
drive = drive*(1 - slow[:, None]) + fft_lowpass(drive, 900)*1.5*slow[:, None]   # muffled, heavy slow-mo
drive = fade(drive, 0.03, 0.5)
place(eng, drive, st['D'] + 0.18)
# overrun crackles on phrase ends + when the car comes off the throttle
dsrc = np.array(ev['d_src'])
k = int(np.argmax(dsrc >= 40.2)); t_lift = st['D'] + k/60
crk = fade(sl(ftype, 13.55, 14.50), 0.02, 0.2)
for tc in [cuts[2] + 4.17, 12.82, 18.42]:
    place(fx, set_rms(crk, mus_rms - 6), tc)
over = fade(sl(ftype, 10.40, 12.80), 0.05, 0.6); place(fx, set_rms(over, mus_rms - 6), t_lift)
# settle back to idle for the walk-out + pose
idle_end = sl(amg, 20.9, 23.75); place(eng, set_rms(fade(idle_end, 0.4, 0.8), mus_rms - 14), ev['durs']['D'] + st['D'] - 2.4)
loop_bed(set_rms(idle, mus_rms - 17), st['G'] - 0.3, ps + 0.4)

# ---- poster reveal: big double pop on the beat, boom, echo tail
fin = fade(sl(e63, 6.95, 8.20), 0.25, 0.3); reveal = cuts[4]
place(fx, set_rms(fin, mus_rms - 2), reveal - (7.55 - 6.95))
tail = echo(fade(sl(ftype, 13.60, 15.40), 0.02, 0.8)); place(fx, set_rms(tail, mus_rms - 11), reveal + 0.35)

# ---- transition whooshes + sub booms
for tr in ev['trans']:
    d = tr['dur'] + 0.35; w = whoosh(d, d*0.55, 250, 5000 if tr['type'] != 'mstripe' else 3000)
    place(fx, w, tr['mid'] - d*0.55, db(-17 if tr['type'] != 'mstripe' else -14))
place(fx, boom(), cuts[2], db(-6))       # the drop / launch
place(fx, boom(1.8, 60, 28), reveal, db(-5))

# ------------------------------------------------------------------ duck music under the big hits
duck = np.ones(N, np.float32)
for p in pops + [reveal, reveal + 0.145]:
    a = int((p - 0.05)*SR); b = int((p + 0.35)*SR); duck[a:b] = np.minimum(duck[a:b], db(-5))
duck = np.convolve(duck, np.ones(1200)/1200, mode='same')
mix = music*duck[:, None]*db(-0.5) + eng*db(-1) + fx
mix = mix[:int(T*SR)]
out = os.path.join(BASE, 'work', 'mix_raw.wav'); sf.write(out, mix, SR, subtype='FLOAT')
print('mix written', out, 'peak', np.abs(mix).max(), 'music rms', mus_rms)

#!/usr/bin/env python3
"""Urus edit sound design: song + real twin-turbo V8 recordings + editor SFX, locked to events.json."""
import json, os, subprocess, math, numpy as np, soundfile as sf
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
ev = json.load(open(os.path.join(BASE, 'work', 'events.json')))
T = ev['total']; N = int(T*SR) + SR
EXH = '/home/user/sathyaram/exhaustnotes/public/sounds/'
FX = '/home/user/ext/el/public/sfx/'

def load(path, start=0.0, dur=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', f'{start}', '-i', path] + (['-t', f'{dur}'] if dur else []) + \
          ['-f', 'f32le', '-ac', '2', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, 2).copy()
def db(x): return 10**(x/20)
def fade(a, fi=0.01, fo=0.01):
    a = a.copy(); n = len(a); i = min(n, int(fi*SR)); o = min(n, int(fo*SR))
    if i: a[:i] *= np.linspace(0, 1, i)[:, None]
    if o: a[n-o:] *= np.linspace(1, 0, o)[:, None]
    return a
def place(bus, a, t, g=1.0):
    s = int(round(t*SR))
    if s < 0: a = a[-s:]; s = 0
    e = min(len(bus), s + len(a))
    if e > s: bus[s:e] += a[:e-s]*g
def rms_db(a): return 20*np.log10(np.sqrt((a**2).mean()) + 1e-9)
def set_rms(a, target): return a*db(target - rms_db(a))
def peak_norm(a, p=0.9): return a/(np.abs(a).max() + 1e-9)*p
def fft_lowpass(a, fc):
    F = np.fft.rfft(a, axis=0); f = np.fft.rfftfreq(len(a), 1/SR)
    F *= (1/(1 + (f/fc)**4))[:, None]
    return np.fft.irfft(F, len(a), axis=0).astype(np.float32)
def echo(a, delays=((0.16, 0.42), (0.32, 0.24), (0.48, 0.12), (0.64, 0.06))):
    out = np.zeros((len(a) + int(0.8*SR), 2), np.float32); out[:len(a)] += a
    for k, (d, g) in enumerate(delays):
        s = int(d*SR); pan = np.array([1.0, 0.75] if k % 2 == 0 else [0.75, 1.0], np.float32)
        out[s:s+len(a)] += fft_lowpass(a, 3500)*g*pan
    return out
def boom_synth(dur=1.6, f0=65, f1=30):
    t = np.arange(int(dur*SR))/SR; f = f1 + (f0 - f1)*np.exp(-t/0.12)
    s = np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.5)*np.minimum(1, t/0.004)
    return np.stack([s, s], 1).astype(np.float32)
def varispeed(src, src_start, rates):
    pos = src_start*SR + np.concatenate([[0], np.cumsum(rates[:-1])]); idx = np.arange(len(src))
    return np.stack([np.interp(pos, idx, src[:, c]) for c in range(2)], 1).astype(np.float32)
def sl(a, t0, t1): return a[int(t0*SR):int(t1*SR)].copy()

# ------------------------------------------------------------------ sources
song = load(os.path.join(BASE, 'src', 'song.mp3'), 0.0, T + 0.5)
amg = load(EXH + 'amggtr.m4a'); e63 = load(EXH + 'e63.m4a'); ftype = load(EXH + 'ftype.m4a')
sfx = {k: load(FX + k + '.mp3') for k in ['boom', 'glitch', 'reverse-whoosh', 'riser', 'shutter', 'swoosh', 'whoosh',
                                          'whoosh-alt1', 'whoosh-alt2', 'magic-reveal']}
SFX_PEAK = {'boom': 1.05, 'glitch': 0.10, 'reverse-whoosh': 1.50, 'riser': 2.90, 'swoosh': 0.50, 'whoosh': 0.15,
            'whoosh-alt1': 0.35, 'whoosh-alt2': 0.55, 'magic-reveal': 0.40}
def hit(bus, name, t_peak, gain_db, length=None):
    a = sfx[name] if length is None else fade(sfx[name][:int(length*SR)], 0.002, 0.08)
    place(bus, peak_norm(a), t_peak - SFX_PEAK.get(name, 0), db(gain_db))

mus_rms = rms_db(song[int(14*SR):int(24*SR)])
music = np.zeros((N, 2), np.float32); eng = np.zeros((N, 2), np.float32); fx = np.zeros((N, 2), np.float32)
place(music, song, 0.0)
fo = int(1.4*SR); e = int(T*SR); music[e-fo:e] *= np.linspace(1, 0, fo)[:, None]**1.6; music[e:] = 0

DROP, P = ev['drop'], ev['P']; cuts = ev['cuts']; pops = ev['pops']; poster = cuts[-1][0]
def cut(t): return min(cuts, key=lambda c: abs(c[0] - t))[0]   # cut time nearest to t

# ---- engine idle bed (AMG GT 4.0 twin-turbo V8 settling into idle) under intro + detail orbit
idle = set_rms(sl(amg, 21.55, 23.75), mus_rms - 19)
def loop_bed(clip, t0, t1, g=1.0):
    xf = int(0.25*SR); step = (len(clip) - xf)/SR; t = t0
    while t < t1:
        place(eng, fade(clip, 0.25, 0.25), t, g); t += step
loop_bed(idle, 0.3, 9.9)
env = np.ones(N, np.float32); a, b = int(0.3*SR), int(3.0*SR); env[a:b] = np.linspace(0, 1, b-a)
c, d = int(9.6*SR), int(9.95*SR); env[c:d] = np.linspace(1, 0, d-c); env[d:int(12.9*SR)] = 0
eng *= env[:, None]

# ---- detail orbit: camera-shutter clicks on the hat beats
for tb in ev['hat_beats'][1:8]:
    hit(fx, 'shutter', tb, -15, length=0.14)

# ---- backfires in the silence before the drop (E63 4.0 V8 hot-V – same engine family as the Urus)
place(fx, set_rms(fade(sl(e63, 12.95, 14.10), 0.3, 0.25), mus_rms - 3), pops[0] - (13.64 - 12.95))
place(fx, set_rms(fade(sl(e63, 7.30, 8.15), 0.08, 0.25), mus_rms - 2), pops[1] - (7.55 - 7.30))
# riser + reverse whoosh into the drop, glitch on the 11.94 hit, swoosh on the 10.68 flash
hit(fx, 'riser', DROP - 0.05, -11)
hit(fx, 'reverse-whoosh', DROP, -9)
hit(fx, 'glitch', cut(11.94), -12, length=0.6)
hit(fx, 'swoosh', cut(10.68), -13)
hit(fx, 'whoosh-alt2', cut(4.55), -14)
hit(fx, 'whoosh-alt1', cut(7.15), -14)
hit(fx, 'reverse-whoosh', cut(2.35) + 0.2, -20)
# through-the-wheel: spin-up reverse whoosh into the hub, swoosh as the portal opens
for tc, kind, dur in cuts:
    if kind in ('wheel', 'wheelgap'):
        hit(fx, 'reverse-whoosh', tc + 0.25, -11); hit(fx, 'swoosh', tc + 0.30, -12)

# ---- the drop: boom + launch, engine follows the edit (varispeed in the slow-mo drift)
hit(fx, 'boom', DROP, -5); place(fx, boom_synth(), DROP, db(-9))
dr = ev['drift']; dt0 = dr['t0']; dsp = np.array(dr['spd'])
drive_len = poster + 0.4 - DROP
tt = np.arange(int(drive_len*SR))/SR + DROP
rate = np.ones(len(tt), np.float32)
m = (tt >= dt0) & (tt < dt0 + len(dsp)/60)
rate[m] = np.clip(np.interp(tt[m] - dt0, np.arange(len(dsp))/60, dsp), 0.5, 1.0)
rate = np.convolve(np.pad(rate, 1200, mode='edge'), np.ones(2401)/2401, mode='valid').astype(np.float32)
src = np.concatenate([amg[int(0.35*SR):int(21.0*SR)], amg[int(1.0*SR):int(21.0*SR)]])
drive = varispeed(src, 0, rate)
slow = (rate < 0.8).astype(np.float32); slow = np.convolve(slow, np.ones(4800)/4800, mode='same')
drive = drive*(1 - slow[:, None]) + fft_lowpass(drive, 900)*1.6*slow[:, None]
drive = set_rms(drive, mus_rms - 6.5)
drive = fade(drive, 0.02, 0.35)
place(eng, drive, DROP)
place(fx, set_rms(fade(sl(e63, 6.80, 8.30), 0.4, 0.3), mus_rms - 3), DROP - (7.0 - 6.80))  # launch bark

# ---- overrun crackles on bar ends (Jaguar F-Type crackle recording)
crk = fade(sl(ftype, 13.55, 14.55), 0.02, 0.25)
for tc in [DROP + 2*P + 0.3, DROP + 12*P + 0.05, DROP + 15*P - 0.6, DROP + 21*P - 0.5]:
    place(fx, set_rms(crk, mus_rms - 8), tc)

# ---- transition SFX on every driving cut
WH = {'whipleft': 'whoosh-alt1', 'whipright': 'whoosh-alt2', 'whipup': 'whoosh', 'whipdown': 'whoosh-alt1',
      'spin': 'swoosh', 'zoomin': 'whoosh-alt2', 'zoomout': 'whoosh-alt2', 'glitch': 'glitch', 'leak': 'reverse-whoosh'}
for tc, kind, _ in [c for c in cuts[:-1] if c[0] > DROP + 0.1]:
    if kind == 'glitch': hit(fx, 'glitch', tc, -13, length=0.5)
    elif kind == 'leak': hit(fx, 'reverse-whoosh', tc, -14)
    else: hit(fx, WH[kind], tc, -12)

# ---- poster reveal: reverse whoosh in, boom, sparkle, double pop with echo tail
hit(fx, 'reverse-whoosh', poster, -8)
hit(fx, 'boom', poster, -5); place(fx, boom_synth(2.0, 58, 27), poster, db(-9))
hit(fx, 'magic-reveal', poster + 0.15, -14)
place(fx, set_rms(fade(sl(e63, 7.30, 8.15), 0.08, 0.25), mus_rms - 2), poster - (7.55 - 7.30))
place(fx, set_rms(echo(fade(sl(ftype, 13.60, 15.30), 0.02, 0.8)), mus_rms - 12), poster + 0.4)

# ------------------------------------------------------------------ duck music under the hits
duck = np.ones(N, np.float32)
for p in pops + [DROP, poster]:
    a = int((p - 0.04)*SR); b = int((p + 0.30)*SR); duck[a:b] = np.minimum(duck[a:b], db(-5))
a = int(DROP*SR); b = int(poster*SR); duck[a:b] = np.minimum(duck[a:b], db(-1.5))
duck = np.convolve(duck, np.ones(1200)/1200, mode='same')
mix = (music*duck[:, None] + eng + fx)[:int(T*SR)]
sf.write(os.path.join(BASE, 'work', 'mix_raw.wav'), mix, SR, subtype='FLOAT')
print('ok peak', np.abs(mix).max(), 'mus_rms', mus_rms)

#!/usr/bin/env python3
"""Lamborghini Urus Mansory – vertical 1080x1920 @60fps music edit.
Video time t == song time t (Medi - Crni Urus), every cut sits on the song's grid."""
import json, math, subprocess, sys, os, time
import numpy as np, cv2
from PIL import Image, ImageFilter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'src', 'in.mkv')
POSTER = os.path.join(BASE, 'src', 'lambo.png')
YOLO_W = os.path.join(os.path.dirname(BASE), 'models', 'yolo11x-seg.pt')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'work', 'urus_video.mp4')
PREVIEW = os.environ.get('PREVIEW')
SW, SH = 1920, 1080          # source
W, H, FPS = 1080, 1920, 60   # output (TikTok)
rng = np.random.default_rng(11)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def ease_io_cubic(u): u = clamp(u); return 4*u**3 if u < .5 else 1-(-2*u+2)**3/2
def ease_io_quart(u): u = clamp(u); return 8*u**4 if u < .5 else 1-(-2*u+2)**4/2
def ease_out_expo(u): u = clamp(u); return 1 if u >= 1 else 1-2**(-10*u)
def ease_in_cubic(u): u = clamp(u); return u**3
def ease_out_cubic(u): u = clamp(u); return 1-(1-u)**3
def smooth(u): u = clamp(u); return u*u*(3-2*u)
def deriv(f, u, h=1e-3): return (f(clamp(u+h))-f(clamp(u-h)))/(2*h)

# ---------------------------------------------------------------- source access
class Reader:
    def __init__(self, start, dur):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{max(0, start):.3f}', '-i', SRC, '-t', f'{dur:.3f}',
                                   '-map', '0:v:0', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=SW*SH*3*4)
        self.cache = {}; self.n = 0; self.last = None
    def get(self, i):
        i = max(0, int(i))
        while self.n <= i:
            buf = self.p.stdout.read(SW*SH*3)
            if len(buf) == SW*SH*3: self.last = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
            self.cache[self.n] = self.last; self.n += 1
        for k in [k for k in self.cache if k < i-6]: del self.cache[k]
        return self.cache.get(i, self.last)
    def close(self):
        try: self.p.kill()
        except Exception: pass

DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
GX, GY = np.meshgrid(np.arange(SW, dtype=np.float32), np.arange(SH, dtype=np.float32))
def flow_interp(f0, f1, a):
    a = float(a)
    g0 = cv2.cvtColor(cv2.resize(f0, (SW//2, SH//2), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    g1 = cv2.cvtColor(cv2.resize(f1, (SW//2, SH//2), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    F01 = cv2.resize(DIS.calc(g0, g1, None), (SW, SH))*2
    F10 = cv2.resize(DIS.calc(g1, g0, None), (SW, SH))*2
    w0 = cv2.remap(f0, GX - a*F01[..., 0], GY - a*F01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    w1 = cv2.remap(f1, GX - (1-a)*F10[..., 0], GY - (1-a)*F10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.addWeighted(w0, 1-a, w1, a, 0)

def sample(reader, pos, speed):
    if speed < 0.9:
        pos = float(pos); i0 = math.floor(pos); a = pos - i0
        f0 = reader.get(i0)
        if a < 0.05: return f0
        f1 = reader.get(i0+1)
        if a > 0.95: return f1
        return flow_interp(f0, f1, a)
    if speed > 1.35:  # shutter blend = natural motion blur on speed-ups
        n = min(4, max(2, int(round(speed))))
        acc = sum(reader.get(round(pos) - n//2 + k).astype(np.float32) for k in range(n))
        return (acc/n).astype(np.uint8)
    return reader.get(round(pos))

# ---------------------------------------------------------------- look ("better graphics")
xs = np.arange(256)/255.0
tone = np.clip(xs + 0.12*(xs-0.5)*(1-np.abs(2*xs-1))*2, 0, 1)**0.94*1.03
tone = np.where(tone > 0.72, 0.72 + 0.26*np.tanh((tone - 0.72)/0.26), tone)   # filmic highlight roll-off      # filmic S
tone = 0.018 + tone*0.975                                                 # lifted, soft blacks
lut_b = np.clip(tone + 0.030*(1-xs)**2 - 0.045*xs**2, 0, 1)               # teal shadows, warm highs
lut_g = np.clip(tone + 0.010*(1-xs)**2 - 0.006*xs**2, 0, 1)
lut_r = np.clip(tone - 0.020*(1-xs)**2 + 0.040*xs**2, 0, 1)
LUT = (np.dstack([lut_b, lut_g, lut_r]).reshape(1, 256, 3)*255).astype(np.uint8)

vy, vx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.30*np.clip(((vx-W/2)/(W*0.75))**2 + ((vy-H/2)/(H*0.62))**2, 0, 1)**1.5)[..., None].astype(np.float32)
GRAIN = [rng.normal(0, 3.0, (H//2, W//2)).astype(np.float32) for _ in range(6)]

def look(img, sat=1.22, bloom=0.22, streak=0.13):
    img = cv2.LUT(img, LUT)
    f = img.astype(np.float32)
    lum = f[..., 0:1]*0.114 + f[..., 1:2]*0.587 + f[..., 2:3]*0.299
    f = lum + (f - lum)*sat
    # bloom + anamorphic streak from highlights (sun, lights, chrome)
    small = cv2.resize(f, (W//4, H//4), interpolation=cv2.INTER_AREA)
    sl = small.max(2, keepdims=True)
    hi = np.clip((sl - 190)/65, 0, 1)**2
    b = cv2.GaussianBlur(small*hi, (0, 0), 9) + cv2.GaussianBlur(small*hi, (0, 0), 28)
    st = cv2.GaussianBlur(hi[..., 0]*255, (0, 0), sigmaX=70, sigmaY=1.2)[..., None]*np.array([1.0, 0.85, 0.7], np.float32)
    add = cv2.resize(b*bloom*0.5 + st*streak, (W, H), interpolation=cv2.INTER_LINEAR)
    f = f + add*np.array([0.85, 0.95, 1.1], np.float32)
    return np.clip(f, 0, 255).astype(np.uint8)

def sharpen(img, amt=0.55, sig=1.3):
    bl = cv2.GaussianBlur(img, (0, 0), sig)
    return cv2.addWeighted(img, 1 + amt, bl, -amt, 0)

def finish(f, n, t):
    ff = f.astype(np.float32)*VIG
    ff += cv2.resize(GRAIN[n % len(GRAIN)], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    return ff

# ---------------------------------------------------------------- ops in output space
def affine(img, scale=1.0, dx=0.0, dy=0.0, rot=0.0):
    if abs(scale-1) < 1e-4 and abs(dx) < .01 and abs(dy) < .01 and abs(rot) < 1e-4: return img
    M = cv2.getRotationMatrix2D((W/2, H/2), rot, scale); M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def radial_blur(img, amount, n=8):
    if amount < 0.004: return img
    s = cv2.resize(img, (W//2, H//2), interpolation=cv2.INTER_AREA).astype(np.float32); acc = np.zeros_like(s)
    for k in range(n):
        M = cv2.getRotationMatrix2D((W/4, H/4), 0, 1 + amount*k/(n-1))
        acc += cv2.warpAffine(s, M, (W//2, H//2), borderMode=cv2.BORDER_REFLECT)
    return cv2.resize((acc/n).astype(np.uint8), (W, H))

def spin_blur(img, spread, scale, rot, n=8):
    s = cv2.resize(img, (W//2, H//2), interpolation=cv2.INTER_AREA).astype(np.float32); acc = np.zeros_like(s)
    for k in range(n):
        M = cv2.getRotationMatrix2D((W/4, H/4), rot + spread*(k/(n-1) - .5), scale)
        acc += cv2.warpAffine(s, M, (W//2, H//2), borderMode=cv2.BORDER_REFLECT)
    return cv2.resize((acc/n).astype(np.uint8), (W, H))

def motion_blur(img, lx, ly):
    lx, ly = int(abs(lx)), int(abs(ly))
    if lx < 2 and ly < 2: return img
    return cv2.blur(img, (max(1, lx), max(1, ly)))

def chroma(img, k):
    k = int(round(k))
    if k < 1: return img
    out = img.copy(); out[:, k:, 2] = img[:, :-k, 2]; out[:, :-k, 0] = img[:, k:, 0]
    return out

def shake(t, amp, seed=0):
    r = np.random.default_rng(seed); ph = r.uniform(0, 6.28, 6)
    dx = amp*(math.sin(t*23+ph[0])*.5 + math.sin(t*37+ph[1])*.3 + math.sin(t*61+ph[2])*.2)
    dy = amp*(math.sin(t*19+ph[3])*.5 + math.sin(t*41+ph[4])*.3 + math.sin(t*67+ph[5])*.2)
    return dx, dy

def handheld(t, amp=5, seed=5):
    """slow organic camera float"""
    r = np.random.default_rng(seed); ph = r.uniform(0, 6.28, 6)
    dx = amp*(math.sin(t*1.3+ph[0])*.6 + math.sin(t*2.9+ph[1])*.4)
    dy = amp*(math.sin(t*1.1+ph[2])*.6 + math.sin(t*3.3+ph[3])*.4)
    rot = 0.25*(math.sin(t*0.9+ph[4])*.7 + math.sin(t*2.1+ph[5])*.3)
    return dx, dy, rot

# ---------------------------------------------------------------- flames
def glow_sprite(rx, ry, color, power=2.0):
    sx, sy = int(rx*3) | 1, int(ry*3) | 1
    yy, xx = np.mgrid[0:sy, 0:sx].astype(np.float32)
    d = np.sqrt(((xx - sx//2)/rx)**2 + ((yy - sy//2)/ry)**2)
    a = np.clip(1 - d/1.5, 0, 1)**power
    return a[..., None]*np.array(color, np.float32)[None, None, :]
def add_sprite(f, spr, cx, cy, k):
    if k <= 0.002: return
    h, w = spr.shape[:2]; x0, y0 = int(cx - w//2), int(cy - h//2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(f.shape[1], x0+w), min(f.shape[0], y0+h)
    if xa >= xb or ya >= yb: return
    f[ya:yb, xa:xb] += spr[ya-y0:yb-y0, xa-x0:xb-x0]*k
CORE = glow_sprite(150, 60, (200, 245, 255), 1.5)
MID = glow_sprite(230, 105, (40, 150, 255), 1.7)
OUTER = glow_sprite(420, 260, (10, 70, 230), 2.2)

# ---------------------------------------------------------------- music grid
DROP = 12.93; P = 0.6505
def beat_kick(t):
    if t < DROP: return 0.0
    return math.exp(-(((t - DROP) % P))/0.10)

# ---------------------------------------------------------------- shots
# cuts on the song grid; (time, transition, duration)
CUTS = [(2.35, 'leak', 0.70), (4.55, 'zoomin', 0.30), (6.50, 'dissolve', 0.10), (7.80, 'wheel', 0.80), (9.75, 'whipdown', 0.24), (10.68, 'flash', 0.22),
        (11.94, 'glitch', 0.24), (DROP, 'zoomthru', 0.36),
        (DROP + 3*P, 'whipleft', 0.30), (DROP + 5*P, 'spin', 0.36), (DROP + 7*P, 'whipup', 0.30),
        (DROP + 10*P, 'zoomin', 0.30), (DROP + 12*P, 'whipright', 0.30), (DROP + 15*P, 'leak', 0.40),
        (DROP + 17*P, 'glitch', 0.24), (DROP + 19*P, 'whipleft', 0.30), (DROP + 21*P, 'zoomout', 0.30),
        (DROP + 23*P, 'whipdown', 0.30), (DROP + 25*P, 'poster', 0.60)]
POSTER_END = 33.0
HAT_BEATS = [4.55 + 0.65*k for k in range(9)]

# speed profiles:  ('c', s) constant | ('ramp', [(u, s), ...]) over local time fraction | ('beat', src_span)
SHOTS = [
    dict(name='sunset_sil', src=23.20, spd=('c', 0.5), track='union', zoom=1.0, push=(1.0, 1.08)),
    dict(name='hero_wf', src=49.70, spd=('c', 0.6), track='union', zoom=1.05, push=(1.10, 1.0)),
    dict(name='orbitA', src=6.42, spd=('beat', 1.88), track='fixed', cx=0.52, zoom=1.0, push=(1.0, 1.03)),
    dict(name='wheel', src=8.30, spd=('c', 0.25), track='hub', zoom=1.0, push=(1.0, 1.06)),
    dict(name='orbitB', src=10.25, spd=('beat', 2.32), track='fixed', cx=0.52, zoom=1.0, push=(1.03, 1.06)),
    dict(name='exhaust', src=5.50, spd=('c', 0.8), track='exhaust', zoom=1.0, push=(1.0, 1.05)),
    dict(name='sun_front', src=12.70, spd=('c', 0.5), track='fixed', cx=0.40, zoom=1.0, push=(1.04, 1.12)),
    dict(name='sil_riser', src=16.70, spd=('c', 0.6), track='union', zoom=1.0, push=(1.0, 1.25)),
    dict(name='launch', src=32.35, spd=('c', 1.0), track='car', zoom=1.0, push=(1.06, 1.0)),
    dict(name='chase1', src=36.00, spd=('c', 1.3), track='car', zoom=1.05, push=(1.0, 1.04)),
    dict(name='turn', src=39.30, spd=('c', 1.1), track='car', zoom=1.0, push=(1.0, 1.04)),
    dict(name='sun_chase', src=41.00, spd=('c', 1.25), track='car', zoom=1.0, push=(1.0, 1.05)),
    dict(name='sun_chase2', src=44.10, spd=('c', 1.2), track='car', zoom=1.0, push=(1.04, 1.0)),
    dict(name='drift', src=47.55, spd=('ramp', [(0, 1.1), (0.25, 1.0), (0.45, 0.32), (0.85, 0.32), (1.0, 0.6)]), track='car', zoom=1.0, push=(1.0, 1.06)),
    dict(name='hero_wf2', src=51.50, spd=('c', 0.8), track='car', zoom=1.10, push=(1.0, 1.06)),
    dict(name='river', src=56.40, spd=('c', 1.0), track='union', zoom=1.0, push=(1.05, 1.0)),
    dict(name='side_day', src=18.10, spd=('c', 0.9), track='union', zoom=1.0, push=(1.0, 1.05)),
    dict(name='sunset_wide', src=26.30, spd=('c', 0.8), track='union', zoom=1.0, push=(1.08, 1.0)),
    dict(name='final_sil', src=61.80, spd=('c', 0.7), track='union', zoom=1.0, push=(1.0, 1.08)),
]
assert len(SHOTS) == len(CUTS)

starts, ends = [], []
for i, sh in enumerate(SHOTS):
    s = 0.0 if i == 0 else CUTS[i-1][0] - CUTS[i-1][2]/2
    e = CUTS[i][0] + CUTS[i][2]/2
    starts.append(s); ends.append(e)
POSTER_START = CUTS[-1][0] - CUTS[-1][2]/2
TOTAL = POSTER_END
NF = int(round(TOTAL*FPS))

def build_positions(sh, dur):
    n = int(round(dur*FPS)); kind = sh['spd'][0]
    if kind == 'c':
        spd = np.full(n, sh['spd'][1])
    elif kind == 'ramp':
        pts = sh['spd'][1]; u = np.arange(n)/max(1, n-1)
        spd = np.interp(u, [p[0] for p in pts], [p[1] for p in pts])
        spd = np.convolve(np.pad(spd, 6, mode='edge'), np.ones(13)/13, mode='valid')
    else:  # beat ramps: slow on every hat-beat, fast between, total = src span
        span = sh['spd'][1]; tl = sh['_t0'] + np.arange(n)/FPS
        ph = ((tl - 4.55) % 0.65)/0.65
        w = 0.22 + (0.5 - 0.5*np.cos(2*np.pi*ph))**1.6
        spd = w * (span*FPS/w.sum())
    pos = np.concatenate([[0], np.cumsum(spd[:-1])])
    return pos, spd

for i, sh in enumerate(SHOTS):
    sh['_t0'] = starts[i]; sh['dur'] = ends[i] - starts[i]
    sh['pos'], sh['spd_arr'] = build_positions(sh, sh['dur'])
    sh['src_end'] = sh['src'] + sh['pos'][-1]/FPS
    sh['reader'] = None

print('timeline:')
for i, sh in enumerate(SHOTS):
    print(f"  {sh['name']:12s} t {starts[i]:6.2f}-{ends[i]:6.2f}  src {sh['src']:6.2f}-{sh['src_end']:6.2f}  -> {CUTS[i][1]}")
print('poster', POSTER_START, 'total', TOTAL, flush=True)

# ---------------------------------------------------------------- reframing tracks (YOLO), cached
TRACK_CACHE = os.path.join(BASE, 'work', 'tracks.json')
def build_tracks():
    if os.path.exists(TRACK_CACHE):
        c = json.load(open(TRACK_CACHE))
        if all(sh['name'] in c for sh in SHOTS if sh['track'] in ('car', 'union')): return c
    from ultralytics import YOLO
    m = YOLO(YOLO_W); c = {}
    for sh in SHOTS:
        if sh['track'] not in ('car', 'union'): continue
        a, b = sh['src'] - 0.2, sh['src_end'] + 0.3
        rd = Reader(a, b - a + 0.2); ts, xs_ = [], []
        k = 0
        while k/60 <= b - a:
            fr = rd.get(k)
            r = m.predict(fr, imgsz=960, classes=[0, 2, 7], conf=0.3, verbose=False)[0]
            bx = r.boxes.xyxy.cpu().numpy(); cl = r.boxes.cls.cpu().numpy().astype(int)
            cx = None
            if len(bx):
                areas = (bx[:, 2]-bx[:, 0])*(bx[:, 3]-bx[:, 1])
                cars = [j for j in range(len(bx)) if cl[j] in (2, 7)]
                if cars:
                    j = max(cars, key=lambda j: areas[j]); x0, x1 = bx[j, 0], bx[j, 2]
                    if sh['track'] == 'union':
                        for p in [j2 for j2 in range(len(bx)) if cl[j2] == 0 and areas[j2] > 0.15*areas[j]]:
                            if abs((bx[p, 0]+bx[p, 2])/2 - (x0+x1)/2) < 700: x0, x1 = min(x0, bx[p, 0]), max(x1, bx[p, 2])
                    cx = (x0 + x1)/2
            ts.append(float(a + k/60)); xs_.append(None if cx is None else float(cx))
            k += 6
        rd.close()
        good = [(t, x) for t, x in zip(ts, xs_) if x is not None]
        c[sh['name']] = good
        print('track', sh['name'], len(good), 'pts', flush=True)
    json.dump(c, open(TRACK_CACHE, 'w'))
    return c

TRACKS = build_tracks()
def smooth_track(pts, sig=0.35):
    if not pts: return None
    t = np.array([p[0] for p in pts]); x = np.array([p[1] for p in pts])
    tt = np.arange(t[0], t[-1] + 1e-6, 1/60); xx = np.interp(tt, t, x)
    k = int(sig*60*3); ker = np.exp(-0.5*(np.arange(-k, k+1)/(sig*60))**2); ker /= ker.sum()
    xs2 = np.convolve(np.pad(xx, k, mode='edge'), ker, mode='valid')
    return tt, xs2
SMOOTH = {name: smooth_track(p) for name, p in TRACKS.items()}

# exhaust template tracker for the backfire shot
class ExhaustTracker:
    def __init__(self):
        ref = cv2.imread(os.path.join(BASE, 'work', 'ex_6.0.png'))
        g = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
        self.c = (1005, 785); self.tpl = g[785-110:785+110, 1005-190:1005+190]
        self.pos = None
    def update(self, fr):
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        r = cv2.matchTemplate(g, self.tpl, cv2.TM_CCOEFF_NORMED)
        _, mv, _, ml = cv2.minMaxLoc(r)
        p = (ml[0] + 190, ml[1] + 110)
        if mv > 0.35:
            self.pos = p if self.pos is None else (0.6*p[0] + 0.4*self.pos[0], 0.6*p[1] + 0.4*self.pos[1])
        return self.pos or self.c
EXT = ExhaustTracker()
class HubTracker:
    """follows the wheel hub (spoke centre) for the through-the-wheel transition"""
    def __init__(self):
        rd = Reader(8.40, 0.1); g = cv2.cvtColor(rd.get(0), cv2.COLOR_BGR2GRAY); rd.close()
        self.c = (1052, 592); self.tpl = g[592-120:592+120, 1052-120:1052+120]; self.pos = None
    def update(self, fr):
        g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        x, y = self.pos or self.c; m = 260
        xa, ya = int(max(0, x-120-m)), int(max(0, y-120-m))
        win = g[ya:int(min(SH, y+120+m)), xa:int(min(SW, x+120+m))]
        r = cv2.matchTemplate(win, self.tpl, cv2.TM_CCOEFF_NORMED); _, mv, _, ml = cv2.minMaxLoc(r)
        p = (xa + ml[0] + 120, ya + ml[1] + 120)
        if mv > 0.3: self.pos = p if self.pos is None else (0.5*p[0] + 0.5*self.pos[0], 0.5*p[1] + 0.5*self.pos[1])
        return self.pos or self.c
HUB = HubTracker(); HUB_OUT = [W/2, H/2]
POPS = [10.12, 10.40, 10.52]

# ---------------------------------------------------------------- shot rendering
def crop_to_vertical(fr, cx, zoom, extra_s, dx, dy, rot):
    """single high-quality warp: source 16:9 -> 9:16 window around cx, plus motion."""
    s = (H/SH)*zoom*extra_s                     # source->output scale
    ch_w = W/s
    cxc = float(np.clip(cx, ch_w/2, SW - ch_w/2))
    M = cv2.getRotationMatrix2D((cxc, SH/2), rot, s)
    M[0, 2] += W/2 - cxc + dx; M[1, 2] += H/2 - SH/2 + dy
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT), M

def shot_frame(i, lt):
    sh = SHOTS[i]; k = min(len(sh['pos']) - 1, max(0, int(round(lt*FPS))))
    if sh['reader'] is None: sh['reader'] = Reader(sh['src'], sh['src_end'] - sh['src'] + 0.4)
    spd = sh['spd_arr'][k]; fr = sample(sh['reader'], sh['pos'][k], spd)
    src_t = sh['src'] + sh['pos'][k]/FPS; t = starts[i] + lt; u = lt/sh['dur']
    # framing
    if sh['track'] in ('car', 'union') and SMOOTH.get(sh['name']):
        tt, xx = SMOOTH[sh['name']]; cx = float(np.interp(src_t, tt, xx))
    elif sh['track'] == 'exhaust':
        cx = EXT.update(fr)[0]
    elif sh['track'] == 'hub':
        hx, hy = HUB.update(fr)
        sh['_cx'] = hx if '_cx' not in sh else 0.85*sh['_cx'] + 0.15*hx; cx = sh['_cx']
    else:
        cx = sh.get('cx', 0.5)*SW
    p0, p1 = sh['push']; es = p0 + (p1 - p0)*smooth(u)
    dx, dy, rot = handheld(t, 6, seed=i)
    ca = 0; flash = 0
    if t >= DROP:
        kb = beat_kick(t); es *= 1 + 0.035*kb; ca += 4*kb
    if sh['name'] == 'launch':
        k2 = math.exp(-max(0, lt - 0.18)/0.5); sx, sy = shake(t, 16*k2, 3); dx += sx; dy += sy
    if sh['name'] in ('chase1', 'sun_chase', 'sun_chase2', 'turn'):
        sx, sy = shake(t, 3.5, i); dx += sx; dy += sy
    if sh['name'] == 'exhaust':
        for p in POPS:
            if t >= p:
                kk = math.exp(-(t - p)/0.09); es *= 1 + 0.06*kk; ca += 9*kk; flash += 0.08*kk
                sx, sy = shake(t, 22*kk, int(p*100)); dx += sx; dy += sy
    if sh['name'] == 'sil_riser':
        sx, sy = shake(t, 6*u**2, 7); dx += sx; dy += sy
    # backfire flames, in source space so they stick to the exhaust
    if sh['name'] == 'exhaust':
        kf = sum(math.exp(-(t - p)/0.075) for p in POPS if t >= p)
        if kf > 0.004:
            ex, ey = EXT.update(fr) if False else (EXT.pos or EXT.c)
            ff = fr.astype(np.float32); fl = 0.8 + 0.4*rng.random()
            add_sprite(ff, OUTER, ex, ey + 30, min(1.4, kf*1.3))
            add_sprite(ff, MID, ex, ey, min(1.6, kf*1.6)*fl)
            add_sprite(ff, CORE, ex + rng.normal(0, 6), ey + rng.normal(0, 4), min(1.9, kf*1.9)*fl)
            ff[int(ey):] += np.array([0, 30, 90], np.float32)*min(1, kf)*0.55
            fr = np.clip(ff, 0, 255).astype(np.uint8)
    out, Mc = crop_to_vertical(fr, cx, sh['zoom'], es, dx, dy, rot)
    if sh['track'] == 'hub':
        hx, hy = HUB.pos or HUB.c; HUB_OUT[0] = Mc[0, 0]*hx + Mc[0, 1]*hy + Mc[0, 2]; HUB_OUT[1] = Mc[1, 0]*hx + Mc[1, 1]*hy + Mc[1, 2]
    out = sharpen(out)
    out = look(out, bloom=0.26 if 'sun' in sh['name'] or 'sil' in sh['name'] or 'wf' in sh['name'] or 'wide' in sh['name'] else 0.20)
    if ca > 0.6: out = chroma(out, ca)
    if flash > 0.003: out = cv2.addWeighted(out, 1 - flash, np.full_like(out, (180, 225, 255)), flash, 0)
    return out

# ---------------------------------------------------------------- poster
def build_poster():
    p = Image.open(POSTER).convert('RGB'); pw, ph = p.size
    s = H/ph*1.25
    bg = p.resize((int(pw*s), int(ph*s)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(45))
    bg = np.asarray(bg)[..., ::-1].astype(np.float32)*0.55
    fw = 980; fh = int(ph*fw/pw)
    fg = np.asarray(p.resize((fw*2, fh*2), Image.LANCZOS))[..., ::-1].copy()
    r = 40; m = np.zeros((fh*2, fw*2), np.uint8)
    cv2.rectangle(m, (r, 0), (fw*2-r, fh*2), 255, -1); cv2.rectangle(m, (0, r), (fw*2, fh*2-r), 255, -1)
    for c in [(r, r), (fw*2-r, r), (r, fh*2-r), (fw*2-r, fh*2-r)]: cv2.circle(m, c, r, 255, -1, cv2.LINE_AA)
    return bg, fg, m
PBG, PFG, PMASK = build_poster()
def poster_frame(t, T):
    bh, bw = PBG.shape[:2]; bs = 1.08 - 0.06*(t/T)
    M = np.float32([[bs, 0, W/2 - bs*bw/2], [0, bs, H/2 - bs*bh/2]])
    f = cv2.warpAffine(PBG, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    lx = -500 + 2200*smooth(t/T)
    leak = np.exp(-((vx - lx)**2)/(2*300**2) - ((vy - 500)**2)/(2*900**2))[..., None]
    f = f + leak*np.array([200, 230, 120], np.float32)*0.30
    e = ease_out_expo(t/1.0)
    s = (1.18 - 0.18*e + 0.03*(t/T))*0.5
    fh2, fw2 = PFG.shape[:2]; cy = H/2 + 60*(1 - e)
    M = np.float32([[s, 0, W/2 - s*fw2/2], [0, s, cy - s*fh2/2]])
    fg = cv2.warpAffine(PFG, M, (W, H), flags=cv2.INTER_AREA).astype(np.float32)
    ma = cv2.warpAffine(PMASK, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)[..., None]/255
    sh = cv2.GaussianBlur(ma[..., 0], (0, 0), 30)[..., None]
    f = f*(1 - 0.6*np.roll(sh, 24, axis=0)) + sh*np.array([170, 160, 40], np.float32)*0.18
    sx = -800 + 3200*smooth((t - 0.8)/1.5)
    band = np.exp(-(((vx + 0.5*vy) - sx)**2)/(2*80**2))[..., None]
    fg = fg + band*255*0.22
    if e < 0.98: fg = cv2.GaussianBlur(fg, (0, 0), 0.1 + 10*(1 - e))
    f = f*(1 - ma) + fg*ma
    return np.clip(f, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- through-the-wheel transition
DIST_Y, DIST_X = np.mgrid[0:H, 0:W].astype(np.float32)
def spin_about(img, cx, cy, rot, scale, tx, ty, spread, n=9):
    """rotational motion blur about (cx,cy) + move that point by (tx,ty); done at half res"""
    s = cv2.resize(img, (W//2, H//2), interpolation=cv2.INTER_AREA).astype(np.float32); acc = np.zeros_like(s)
    n = n if spread > 0.5 else 1
    for k in range(n):
        a = rot + (spread*(k/(n-1) - .5) if n > 1 else 0)
        M = cv2.getRotationMatrix2D((cx/2, cy/2), a, scale); M[0, 2] += tx/2; M[1, 2] += ty/2
        acc += cv2.warpAffine(s, M, (W//2, H//2), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.resize(acc/n, (W, H), interpolation=cv2.INTER_LINEAR)

def wheel_transition(fa, fb_fn, u, T):
    hx, hy = HUB_OUT
    z = ease_in_cubic(u); dz = deriv(ease_in_cubic, u)
    mv = smooth(min(1, u*1.6))
    tx, ty = (W/2 - hx)*mv, (H*0.5 - hy)*mv                 # bring the hub to screen centre
    # A: dive into the hub while the wheel spins up
    A = spin_about(fa, hx, hy, -170*z, 1 + 3.2*z, tx, ty, 9 + 60*dz/3)
    A = cv2.GaussianBlur(A, (0, 0), 0.1 + 3*z)
    v = clamp((u - 0.38)/0.62)
    if v <= 0: return np.clip(A, 0, 255).astype(np.uint8)
    # B: emerges from the hub through a growing rim-shaped portal, counter-spinning to rest
    ev = ease_io_cubic(v)
    B = spin_about(fb_fn(), W/2, H/2, 70*(1 - ease_out_cubic(v)), 1.6 - 0.6*ease_out_cubic(v), 0, 0,
                   40*(1 - ease_out_cubic(v)))
    ccx, ccy = hx + tx, hy + ty
    d = np.sqrt((DIST_X - ccx)**2 + ((DIST_Y - ccy)*0.92)**2)
    r = 30 + (math.hypot(W, H)*0.62)*ev**1.15
    m = np.clip((r - d)/10 + 0.5, 0, 1)[..., None]
    out = A*(1 - m) + B*m
    # glowing rim lip on the portal edge (teal-white, like the wheel's polished lip)
    ring = np.exp(-((d - r)/7)**2)[..., None]*np.array([255, 250, 235], np.float32)*0.95 + \
           np.exp(-((d - r)/38)**2)[..., None]*np.array([210, 200, 120], np.float32)*0.45
    out = out + ring*(1 - smooth((v - 0.75)/0.25))
    fl = math.exp(-((v - 0.05)/0.10)**2)*0.35                 # tiny flash as the portal opens
    out = out*(1 - fl) + 255*fl
    return np.clip(out, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- transitions
LEAK = None
def transition(kind, fa, fb_fn, u, T):
    if kind in ('whipleft', 'whipright', 'whipup', 'whipdown'):
        e = ease_io_quart(u); horiz = kind in ('whipleft', 'whipright')
        sgn = -1 if kind in ('whipleft', 'whipup') else 1
        L = W if horiz else H; v = deriv(ease_io_quart, u)*L/(T*FPS)
        fb = fb_fn(); bump = 1 + 0.08*math.sin(math.pi*u)
        oa = sgn*e*L; ob = sgn*(e - 1)*L
        a = affine(fa, bump, oa if horiz else 0, 0 if horiz else oa)
        b = affine(fb, bump, ob if horiz else 0, 0 if horiz else ob)
        if horiz: mask = (vx >= (1-e)*W) if sgn < 0 else (vx < e*W)
        else: mask = (vy >= (1-e)*H) if sgn < 0 else (vy < e*H)
        out = np.where(mask[..., None], b, a)
        return motion_blur(out, v*0.7, 1) if horiz else motion_blur(out, 1, v*0.7)
    if kind in ('zoomin', 'zoomthru', 'poster'):
        amp = 1.4 if kind == 'zoomin' else 2.0
        if u < 0.5:
            uu = u*2; s = 1 + amp*ease_in_cubic(uu)
            out = radial_blur(affine(fa, s), 0.4*deriv(ease_in_cubic, uu)/3)
            if u > 0.42:
                bb = radial_blur(affine(fb_fn(), 1 + amp), 0.4); m = smooth((u - 0.42)/0.16)
                out = cv2.addWeighted(out, 1-m, bb, m, 0)
        else:
            uu = (u - .5)*2; s = 1 + amp*(1 - ease_out_cubic(uu))
            out = radial_blur(affine(fb_fn(), s), 0.4*deriv(ease_out_cubic, uu)/3)
            if u < 0.58:
                aa = radial_blur(affine(fa, 1 + amp), 0.4); m = smooth((u - 0.42)/0.16)
                out = cv2.addWeighted(aa, 1-m, out, m, 0)
        if kind in ('zoomthru', 'poster'):
            fl = math.exp(-((u - 0.5)/0.12)**2)*(0.85 if kind == 'poster' else 0.55)
            out = cv2.addWeighted(out, 1 - fl, np.full_like(out, 255), fl, 0)
        return out
    if kind == 'zoomout':
        if u < 0.5:
            uu = u*2; s = 1 - 0.45*ease_in_cubic(uu)
            out = radial_blur(affine(fa, s), 0.3*deriv(ease_in_cubic, uu)/3)
        else:
            uu = (u - .5)*2; s = 1.8 - 0.8*ease_out_cubic(uu)
            out = radial_blur(affine(fb_fn(), s), 0.3*deriv(ease_out_cubic, uu)/3)
        return out
    if kind == 'spin':
        if u < 0.5:
            uu = u*2; r = 75*ease_in_cubic(uu)
            return spin_blur(fa, 28*deriv(ease_in_cubic, uu)/3, 1 + 0.5*ease_in_cubic(uu), -r)
        uu = (u - .5)*2; r = 75*(1 - ease_out_cubic(uu))
        return spin_blur(fb_fn(), 28*deriv(ease_out_cubic, uu)/3, 1 + 0.5*(1 - ease_out_cubic(uu)), r)
    if kind == 'flash':
        fl = math.exp(-((u - 0.45)/0.18)**2)
        base = fa if u < 0.45 else fb_fn()
        base = affine(base, 1 + 0.06*fl)
        return cv2.addWeighted(base, 1 - fl, np.full_like(base, 255), fl, 0)
    if kind == 'glitch':
        base = fa if u < 0.5 else fb_fn()
        g = base.copy(); amt = math.sin(math.pi*u)
        rr = np.random.default_rng(int(u*1000))
        for _ in range(int(10*amt) + 2):
            y0 = rr.integers(0, H - 40); hh = rr.integers(10, 140); sh_ = int(rr.normal(0, 90*amt))
            g[y0:y0+hh] = np.roll(g[y0:y0+hh], sh_, axis=1)
        g = chroma(g, 18*amt)
        if 0.35 < u < 0.65:
            g = cv2.addWeighted(g, 0.75, np.roll(fa if u >= 0.5 else fb_fn(), 30, axis=1), 0.25, 0)
        return g
    if kind == 'dissolve':
        return cv2.addWeighted(fa, 1 - smooth(u), fb_fn(), smooth(u), 0)
    if kind == 'wheel':
        return wheel_transition(fa, fb_fn, u, T)
    if kind == 'leak':
        fb = fb_fn(); m = smooth(u)
        out = cv2.addWeighted(fa, 1 - m, fb, m, 0).astype(np.float32)
        lx = -300 + (W + 600)*u; k = math.sin(math.pi*u)
        leak = np.exp(-((vx - lx)**2)/(2*260**2) - ((vy - H*0.4)**2)/(2*700**2))[..., None]
        out += leak*np.array([60, 160, 255], np.float32)*0.9*k
        out += np.array([40, 90, 140], np.float32)*0.35*k
        return np.clip(out, 0, 255).astype(np.uint8)
    raise ValueError(kind)

# ---------------------------------------------------------------- frame assembly
def render_frame(n):
    t = n/FPS
    if t >= POSTER_START + CUTS[-1][2]:
        f = poster_frame(t - POSTER_START, TOTAL - POSTER_START)
    else:
        i = next((j for j in range(len(SHOTS)) if t < ends[j] - 1e-9), len(SHOTS) - 1)
        lt = t - starts[i]; kind, T = CUTS[i][1], CUTS[i][2]; t0 = SHOTS[i]['dur'] - T
        fa = shot_frame(i, lt)
        if lt >= t0 - 1e-9:
            u = (lt - t0)/T
            if i + 1 < len(SHOTS): fb_fn = lambda: shot_frame(i + 1, lt - t0)
            else: fb_fn = lambda: poster_frame(lt - t0, TOTAL - POSTER_START)
            f = transition(kind, fa, fb_fn, u, T)
        else:
            f = fa
        # release finished readers
        for j in range(i):
            if SHOTS[j]['reader'] is not None: SHOTS[j]['reader'].close(); SHOTS[j]['reader'] = None
    ff = finish(f, n, t)
    fade = 1.0
    if t < 0.6: fade = smooth(t/0.6)
    if t > TOTAL - 0.7: fade = 1 - smooth((t - (TOTAL - 0.7))/0.7)
    return np.clip(ff*fade, 0, 255).astype(np.uint8)

def main():
    json.dump({'cuts': CUTS, 'starts': starts, 'ends': ends, 'poster_start': POSTER_START, 'total': TOTAL,
               'pops': POPS, 'drop': DROP, 'P': P, 'hat_beats': HAT_BEATS,
               'drift': {'t0': starts[[x['name'] for x in SHOTS].index('drift')], 'spd': SHOTS[[x['name'] for x in SHOTS].index('drift')]['spd_arr'].tolist()},
               'shots': [{'name': s['name'], 't0': starts[i], 't1': ends[i]} for i, s in enumerate(SHOTS)]},
              open(os.path.join(BASE, 'work', 'events.json'), 'w'), indent=1)
    n0, n1 = 0, NF
    if PREVIEW:
        a, b = map(float, PREVIEW.split(',')); n0, n1 = int(a*FPS), min(NF, int(b*FPS))
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', os.environ.get('X264_PRESET', 'slow'),
                            '-crf', os.environ.get('CRF', '14'), '-pix_fmt', 'yuv420p', '-r', str(FPS), OUT], stdin=subprocess.PIPE)
    t0 = time.time()
    for n in range(n0, n1):
        enc.stdin.write(render_frame(n).tobytes())
        if n % 120 == 0: print(f'frame {n}/{NF} {time.time()-t0:.0f}s', flush=True)
    enc.stdin.close(); enc.wait()
    for s in SHOTS:
        if s['reader'] is not None: s['reader'].close()
    print('done', OUT, f'{time.time()-t0:.0f}s', flush=True)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""BMW M5 mini edit renderer: 1920x1080 @ 60fps, frame-accurate motion FX."""
import json, math, subprocess, sys, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(BASE, 'src', 'in.mkv')
POSTER = os.path.join(BASE, 'src', 'image.png')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'work', 'video_noaudio.mp4')
PREVIEW = os.environ.get('PREVIEW')  # "t0,t1" render only a window
W, H, FPS = 1920, 1080, 60
FONT = '/usr/share/fonts/opentype/inter/'
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- easing
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def ease_io_cubic(u): u = clamp(u); return 4*u**3 if u < .5 else 1-(-2*u+2)**3/2
def ease_io_quart(u): u = clamp(u); return 8*u**4 if u < .5 else 1-(-2*u+2)**4/2
def ease_out_expo(u): u = clamp(u); return 1 if u >= 1 else 1-2**(-10*u)
def ease_in_cubic(u): u = clamp(u); return u**3
def ease_out_cubic(u): u = clamp(u); return 1-(1-u)**3
def smooth(u): u = clamp(u); return u*u*(3-2*u)
def deriv(f, u, h=1e-3): return (f(clamp(u+h))-f(clamp(u-h)))/(2*h)

# ---------------------------------------------------------------- source reader
class Reader:
    """Sequential frame access with a small cache (forward only)."""
    def __init__(self, start, dur):
        self.start = start
        self.p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{start:.3f}', '-i', SRC, '-t', f'{dur:.3f}',
                                   '-map', '0:v:0', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'],
                                  stdout=subprocess.PIPE, bufsize=W*H*3*4)
        self.cache = {}; self.n = 0; self.last = None
    def get(self, i):
        i = max(0, int(i))
        while self.n <= i:
            buf = self.p.stdout.read(W*H*3)
            if len(buf) < W*H*3:
                self.cache[self.n] = self.last; self.n += 1; continue
            self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            self.cache[self.n] = self.last; self.n += 1
        for k in [k for k in self.cache if k < i-4]: del self.cache[k]
        return self.cache.get(i, self.last)

DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
GX, GY = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
def flow_interp(f0, f1, a):
    g0 = cv2.cvtColor(cv2.resize(f0, (W//2, H//2), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    g1 = cv2.cvtColor(cv2.resize(f1, (W//2, H//2), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2GRAY)
    F01 = cv2.resize(DIS.calc(g0, g1, None), (W, H)) * 2
    F10 = cv2.resize(DIS.calc(g1, g0, None), (W, H)) * 2
    w0 = cv2.remap(f0, GX - a*F01[..., 0], GY - a*F01[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    w1 = cv2.remap(f1, GX - (1-a)*F10[..., 0], GY - (1-a)*F10[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return cv2.addWeighted(w0, 1-a, w1, a, 0)

def sample(reader, pos, speed):
    """pos in source frames (float, relative to reader start)."""
    if speed < 0.9:
        i0 = math.floor(pos); a = pos - i0
        f0 = reader.get(i0)
        if a < 0.04: return f0
        f1 = reader.get(i0+1)
        if a > 0.96: return f1
        return flow_interp(f0, f1, a)
    if speed > 1.3:  # shutter blend -> natural motion blur on speed-ups
        n = max(2, int(round(speed)))
        fr = [reader.get(round(pos) - n//2 + k).astype(np.float32) for k in range(n)]
        return (sum(fr)/n).astype(np.uint8)
    return reader.get(round(pos))

# ---------------------------------------------------------------- image ops
def affine(img, scale=1.0, dx=0.0, dy=0.0, rot=0.0, cx=W/2, cy=H/2):
    if abs(scale-1) < 1e-4 and abs(dx) < 1e-3 and abs(dy) < 1e-3 and abs(rot) < 1e-4: return img
    M = cv2.getRotationMatrix2D((cx, cy), rot, scale); M[0, 2] += dx; M[1, 2] += dy
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def radial_blur(img, amount, cx=W/2, cy=H/2, n=8):
    if amount < 0.004: return img
    s = cv2.resize(img, (W//2, H//2), interpolation=cv2.INTER_AREA).astype(np.float32)
    acc = np.zeros_like(s)
    for k in range(n):
        M = cv2.getRotationMatrix2D((cx/2, cy/2), 0, 1 + amount*k/(n-1))
        acc += cv2.warpAffine(s, M, (W//2, H//2), borderMode=cv2.BORDER_REFLECT)
    return cv2.resize((acc/n).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)

def spin_blur(img, angle_spread, scale, rot, n=8):
    s = cv2.resize(img, (W//2, H//2), interpolation=cv2.INTER_AREA).astype(np.float32)
    acc = np.zeros_like(s)
    for k in range(n):
        a = rot + angle_spread*(k/(n-1) - .5)
        M = cv2.getRotationMatrix2D((W/4, H/4), a, scale)
        acc += cv2.warpAffine(s, M, (W//2, H//2), borderMode=cv2.BORDER_REFLECT)
    return cv2.resize((acc/n).astype(np.uint8), (W, H), interpolation=cv2.INTER_LINEAR)

def motion_blur(img, lx, ly):
    lx, ly = int(abs(lx)), int(abs(ly))
    if lx < 2 and ly < 2: return img
    return cv2.blur(img, (max(1, lx), max(1, ly)))

def chroma(img, k):
    k = int(round(k))
    if k < 1: return img
    out = img.copy()
    out[:, k:, 2] = img[:, :-k, 2]; out[:, :-k, 0] = img[:, k:, 0]
    return out

# colour grade: punchy contrast, warm highlights / cool shadows, a touch more saturation
xs = np.arange(256)/255.0
sc = xs + 0.10*(xs - 0.5)*(1 - np.abs(2*xs - 1))*2  # gentle S
sc = np.clip(sc, 0, 1)**1.06
lut_b = np.clip(sc + 0.035*(1-xs)**2 - 0.035*xs**2, 0, 1)
lut_g = np.clip(sc + 0.004, 0, 1)
lut_r = np.clip(sc - 0.015*(1-xs)**2 + 0.040*xs**2, 0, 1)
LUT = np.dstack([lut_b, lut_g, lut_r]).reshape(1, 256, 3)
LUT = (LUT*255).astype(np.uint8)
def grade(img, sat=1.14):
    img = cv2.LUT(img, LUT)
    f = img.astype(np.float32)
    lum = f[..., 0:1]*0.114 + f[..., 1:2]*0.587 + f[..., 2:3]*0.299
    f = lum + (f - lum)*sat
    return np.clip(f, 0, 255).astype(np.uint8)

vy, vx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = 1 - 0.38*np.clip(((vx-W/2)/(W*0.62))**2 + ((vy-H/2)/(H*0.70))**2, 0, 1)**1.4
VIG = VIG[..., None].astype(np.float32)
GRAIN = [rng.normal(0, 3.2, (H//2, W//2, 1)).astype(np.float32) for _ in range(6)]

def shake(t, amp, seed=0):
    r = np.random.default_rng(seed); ph = r.uniform(0, 6.28, 6)
    dx = amp*(math.sin(t*23+ph[0])*.5 + math.sin(t*37+ph[1])*.3 + math.sin(t*61+ph[2])*.2)
    dy = amp*(math.sin(t*19+ph[3])*.5 + math.sin(t*41+ph[4])*.3 + math.sin(t*67+ph[5])*.2)
    return dx, dy

# ---------------------------------------------------------------- flames (backfire FX)
def glow_sprite(r, color, power=2.0):
    sz = int(r*3) | 1
    yy, xx = np.mgrid[0:sz, 0:sz].astype(np.float32) - sz//2
    d = np.sqrt(xx**2 + yy**2)/r
    a = np.clip(1 - d/1.5, 0, 1)**power
    return a[..., None]*np.array(color, np.float32)[None, None, :]

def add_sprite(f, spr, cx, cy, k):
    if k <= 0.002: return
    h, w = spr.shape[:2]; x0, y0 = int(cx - w//2), int(cy - h//2)
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0+w), min(H, y0+h)
    if xa >= xb or ya >= yb: return
    f[ya:yb, xa:xb] += spr[ya-y0:yb-y0, xa-x0:xb-x0]*k

CORE = glow_sprite(26, (200, 240, 255), 1.6)    # BGR white-yellow hot core
MID = glow_sprite(78, (40, 150, 255), 1.8)      # orange flame
OUTER = glow_sprite(170, (10, 70, 230), 2.2)    # wide warm bloom

# exhaust tip template for tracking (left / right pairs at src 20.0s)
TIP_REF = {'L': (568, 853), 'R': (1448, 857)}
class TipTracker:
    def __init__(self, ref):
        g = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
        self.t = {k: g[y-45:y+45, x-110:x+110] for k, (x, y) in TIP_REF.items()}
        self.pos = dict(TIP_REF)
    def update(self, frame):
        g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for k, tpl in self.t.items():
            x, y = self.pos[k]; m = 70
            ya, xa = max(0, y-45-m), max(0, x-110-m)
            win = g[ya:y+45+m, xa:x+110+m]
            r = cv2.matchTemplate(win, tpl, cv2.TM_CCOEFF_NORMED)
            _, mv, _, ml = cv2.minMaxLoc(r)
            if mv > 0.5: self.pos[k] = (xa + ml[0] + 110, ya + ml[1] + 45)
        return self.pos

# ---------------------------------------------------------------- text
def font(name, size): return ImageFont.truetype(FONT + name, size)
def text_layer(t):
    """Intro title. t = seconds since title start. Returns RGBA ndarray or None."""
    if t < 0 or t > 2.9: return None
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    x0, y0 = 120, 690
    out_u = ease_in_cubic((t - 2.35)/0.5)            # exit
    alpha_all = 1 - out_u; lift = -40*out_u
    # M stripes
    u = ease_out_expo((t - 0.0)/0.6)
    cols = [(129, 196, 255), (22, 88, 142), (231, 34, 46)]
    for i, c in enumerate(cols):
        sx = x0 + i*22; L = 70*u
        d.polygon([(sx+12, y0-34+lift), (sx+26, y0-34+lift), (sx+14-12*0+0, y0-34+L+lift), (sx, y0-34+L+lift)],
                  fill=c + (int(255*alpha_all),))
    # main title, revealed by sliding up inside a clip box
    u = ease_out_expo((t - 0.12)/0.75)
    track = 26 - 14*ease_out_cubic((t - 0.12)/1.6)
    f1 = font('InterDisplay-Black.otf', 150)
    title = 'BMW M5'; tx = x0 + 90
    clip = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(clip)
    yoff = (1 - u)*150
    cx = tx
    for ch in title:
        cd.text((cx, y0 - 70 + yoff + lift), ch, font=f1, fill=(255, 255, 255, int(255*alpha_all)))
        cx += f1.getlength(ch) + track
    mask = Image.new('L', (W, H), 0); ImageDraw.Draw(mask).rectangle([0, y0-80+lift, W, y0+90+lift], fill=255)
    img = Image.alpha_composite(img, Image.composite(clip, Image.new('RGBA', (W, H), (0, 0, 0, 0)), mask))
    d = ImageDraw.Draw(img)
    # underline
    u2 = ease_out_expo((t - 0.45)/0.7)
    d.rectangle([tx, y0+92+lift, tx + 520*u2, y0+96+lift], fill=(255, 106, 19, int(255*alpha_all)))
    # subtitle
    u3 = smooth((t - 0.6)/0.4)
    f2 = font('Inter-Bold.otf', 36); cx = tx
    for ch in 'G90   //   V8 BITURBO   //   800+ KS':
        d.text((cx + (1-u3)*30, y0+112+lift), ch, font=f2, fill=(255, 140, 60, int(255*u3*alpha_all)))
        cx += f2.getlength(ch) + 5
    a = np.asarray(img)
    if out_u > 0.01:
        a = cv2.GaussianBlur(a, (0, 0), 0.1 + 10*out_u)
    return a

def over(frame, rgba):
    if rgba is None: return frame
    ys, xs_ = np.nonzero(rgba[..., 3] > 0)
    if len(ys) == 0: return frame
    y0, y1, x0, x1 = ys.min(), ys.max()+1, xs_.min(), xs_.max()+1
    a = rgba[y0:y1, x0:x1, 3:4].astype(np.float32)/255
    c = rgba[y0:y1, x0:x1, 2::-1].astype(np.float32)
    f = frame.copy(); reg = f[y0:y1, x0:x1].astype(np.float32)
    f[y0:y1, x0:x1] = (reg*(1-a) + c*a).astype(np.uint8)
    return f

# ---------------------------------------------------------------- poster scene
def build_poster():
    p = Image.open(POSTER).convert('RGB')
    pw, ph = p.size
    bg_s = W/pw * 1.15
    bg = p.resize((int(pw*bg_s), int(ph*bg_s)), Image.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(38))
    bg = np.asarray(bg)[..., ::-1].astype(np.float32)
    bg = bg*0.42 + np.array([10, 40, 120], np.float32)*0.25
    fh = 1000; fw = int(pw*fh/ph)
    fg = np.asarray(p.resize((fw*2, fh*2), Image.LANCZOS))[..., ::-1].copy()  # 2x for crisp zooms
    # rounded corners alpha
    r = 26*2; m = np.full((fh*2, fw*2), 255, np.uint8)
    cv2.rectangle(m, (0, 0), (fw*2, fh*2), 0, -1)
    cv2.rectangle(m, (r, 0), (fw*2-r, fh*2), 255, -1); cv2.rectangle(m, (0, r), (fw*2, fh*2-r), 255, -1)
    for cx, cy in [(r, r), (fw*2-r, r), (r, fh*2-r), (fw*2-r, fh*2-r)]: cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    return np.clip(bg, 0, 255).astype(np.uint8), fg, m

POSTER_BG, POSTER_FG, POSTER_MASK = build_poster()

def poster_frame(t, T):
    """t seconds into the poster scene (T total)."""
    # background slow drift (parallax opposite to foreground)
    bh, bw = POSTER_BG.shape[:2]
    bs = 1.06 - 0.05*(t/T)
    M = np.float32([[bs, 0, W/2 - bs*bw/2], [0, bs, H/2 - bs*bh/2 + 30*(t/T)]])
    f = cv2.warpAffine(POSTER_BG, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    # light leak sweep across background
    lx = -400 + 2800*smooth(t/T*0.9)
    leak = np.exp(-((vx - lx)**2)/(2*380**2) - ((vy - 300)**2)/(2*700**2))[..., None]
    f += leak*np.array([20, 90, 255], np.float32)*0.35
    # foreground poster: entrance settle + slow push
    s_in = 1.10 - 0.10*ease_out_expo(t/1.1)
    s = (s_in + 0.035*(t/T))*0.5  # fg stored at 2x
    fh2, fw2 = POSTER_FG.shape[:2]
    cx, cy = W/2, H/2 + 8*(1 - ease_out_expo(t/1.1))*4
    M = np.float32([[s, 0, cx - s*fw2/2], [0, s, cy - s*fh2/2]])
    fg = cv2.warpAffine(POSTER_FG, M, (W, H), flags=cv2.INTER_AREA if s < 1 else cv2.INTER_LINEAR)
    ma = cv2.warpAffine(POSTER_MASK, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32)[..., None]/255
    # drop shadow + orange halo
    sh = cv2.GaussianBlur(ma, (0, 0), 28)[..., None] if cv2.GaussianBlur(ma, (0, 0), 28).ndim == 2 else cv2.GaussianBlur(ma, (0, 0), 28)
    sh = sh.reshape(H, W, 1)
    f = f*(1 - 0.65*np.roll(sh, 18, axis=0)) + sh*np.array([0, 60, 200], np.float32)*0.25
    fgf = fg.astype(np.float32)
    # specular shine sweep across the poster
    sx = -600 + 3200*smooth((t - 0.9)/1.6)
    band = np.exp(-(((vx + 0.45*vy) - sx)**2)/(2*70**2))[..., None]
    fgf = fgf + band*255*0.22
    f = f*(1 - ma) + fgf*ma
    return np.clip(f, 0, 255).astype(np.uint8)

# ---------------------------------------------------------------- M-stripe wipe
SKEW = vx + vy*0.36  # diagonal coordinate
MCOL = [np.array(c, np.float32) for c in [(255, 196, 129), (142, 88, 22), (46, 34, 231)]]  # BGR
def mstripe(A, B, u):
    span = W + H*0.36
    sw = 150.0; gap = 0.07
    f = A.astype(np.float32)
    edges = []
    for i in range(3):
        e = ease_io_cubic((u - i*gap)/(1 - 2*gap)) * (span + 3*sw + 200) - 100
        edges.append(e)
    # B revealed behind the last (red) stripe trailing edge
    rev = np.clip((edges[2] - 3*sw - SKEW)/2.0 + 0.5, 0, 1)[..., None]
    f = f*(1 - rev) + B.astype(np.float32)*rev
    for i in range(3):
        lead = edges[i] - i*sw; trail = lead - sw
        cov = (np.clip((lead - SKEW)/1.5 + .5, 0, 1) * np.clip((SKEW - trail)/1.5 + .5, 0, 1))[..., None]
        f = f*(1 - cov) + MCOL[i]*cov
    return f.astype(np.uint8)

# ---------------------------------------------------------------- timeline
class Seg:
    def __init__(self, name, src_start, phases=None, dur=None):
        self.name = name; self.src_start = src_start
        # build per-output-frame source positions (in frames) and speeds
        pos = 0.0; self.pos = []; self.spd = []
        if phases is None: phases = [('t', dur, 1.0, 1.0)]
        for ph in phases:
            kind, val, s0, s1 = ph
            k = 0
            if kind == 'f': val = dur - len(self.pos)/FPS; kind = 't'   # fill up to total duration
            while True:
                if kind == 't':
                    n = int(round(val*FPS))
                    if k >= n: break
                    u = k/max(1, n-1); s = s0 + (s1-s0)*ease_io_cubic(u)
                else:  # until src second
                    if self.src_start + pos/FPS >= val: break
                    s = s0
                self.pos.append(pos); self.spd.append(s); pos += s; k += 1
        self.n = len(self.pos); self.dur = self.n/FPS
        self.src_dur = pos/FPS + 0.5
        self.reader = None
    def frame(self, i):
        if self.reader is None: self.reader = Reader(self.src_start, self.src_dur + 0.2)
        i = min(max(i, 0), self.n-1)
        return sample(self.reader, self.pos[i], self.spd[i]), self.spd[i]

# ---- music-locked timeline (video t=0 == song 35.97s, 117.5 BPM, drop at t=8.68)
SONG_OFFSET = 35.97
TT = {'whip': 0.40, 'zoom': 0.42, 'spin': 0.46, 'whipv': 0.40, 'mstripe': 0.95}
trans = ['whip', 'zoom', 'spin', 'whipv', 'mstripe']
CUTS = [3.09, 5.11, 8.68, 21.64, 24.18]          # transition midpoints, on the beat
names = ['A', 'B', 'C', 'D', 'G']
starts = [0.0] + [CUTS[i] - TT[trans[i]]/2 for i in range(4)]
durs = [CUTS[i] + TT[trans[i]]/2 - starts[i] for i in range(5)]
A = Seg('A', 0.80, dur=durs[0])
B = Seg('B', 14.20, dur=durs[1])
C = Seg('C', 22.0 - durs[2], dur=durs[2])        # ends exactly where the launch begins
D = Seg('D', 22.00, dur=durs[3], phases=[('t', 0.45, 1.0, 1.0), ('t', 0.35, 1.0, 0.25), ('t', 2.10, 0.25, 0.25),
        ('t', 0.45, 0.25, 2.3), ('u', 40.2, 2.3, 2.3), ('t', 0.6, 2.3, 1.0), ('f', 0, 1.0, 1.0)])
G = Seg('G', 52.00, dur=durs[4])
segs = [A, B, C, D, G]
starts = [round(x*FPS)/FPS for x in starts]
poster_start = CUTS[4] - TT['mstripe']/2
POSTER_T = 5.4
TOTAL = poster_start + TT['mstripe'] + POSTER_T
NF = int(round(TOTAL*FPS))

# backfire pops (global t) -> C local
POPS_T = [6.66, 7.17, 8.17, 8.315]
C_POPS = [p - starts[2] for p in POPS_T]

# big lyric text behind the car (global t, text)
LYRICS = [(10.20, 11.18, 'VRELO TELO'),
          (11.22, 11.68, 'STVARNO'), (11.70, 12.18, 'NISAM'), (12.20, 12.80, 'ZA DUGO'),
          (16.73, 17.20, 'ONAKO'), (17.22, 17.50, 'KO'), (17.52, 18.40, 'NARUTO'),
          (20.88, 21.50, 'VRELO TELO'),
          (22.13, 22.58, 'STVARNO'), (22.60, 23.03, 'NISAM'), (23.05, 23.70, 'ZA DUGO')]

events = {
    'song_offset': SONG_OFFSET, 'cuts': CUTS,
    'starts': dict(zip(names, starts)), 'durs': {s.name: s.dur for s in segs},
    'trans': [{'type': trans[i], 'mid': CUTS[i], 'dur': TT[trans[i]]} for i in range(5)],
    'poster_start': poster_start, 'total': TOTAL, 'pops': POPS_T,
    'd_speed': [D.spd[k] for k in range(D.n)], 'd_src': [D.src_start + D.pos[k]/FPS for k in range(D.n)],
}
json.dump(events, open(os.path.join(BASE, 'work', 'events.json'), 'w'), indent=1)
print('segments:', {s.name: (round(starts[i], 3), round(s.dur, 3), round(s.src_start, 2), round(s.src_start + s.pos[-1]/FPS, 2)) for i, s in enumerate(segs)},
      'poster@', round(poster_start, 3), 'total', round(TOTAL, 3), flush=True)

# ---------------------------------------------------------------- big lyric text behind the subject
_yolo = None
def subject_mask(frame):
    global _yolo
    if _yolo is None:
        from ultralytics import YOLO
        _yolo = YOLO(os.path.join(BASE, 'models', 'yolo11x-seg.pt'))
    r = _yolo.predict(frame, imgsz=1088, retina_masks=True, classes=[0, 2, 7], conf=0.3, verbose=False)[0]
    m = np.zeros((H, W), np.float32)
    if r.masks is None: return m
    ms = r.masks.data.cpu().numpy(); cls = r.boxes.cls.cpu().numpy().astype(int)
    areas = ms.reshape(len(ms), -1).sum(1); big = areas.max()
    for mm, c, a in zip(ms, cls, areas):
        if a < 0.2*big: continue          # ignore small background cars / people
        m = np.maximum(m, (mm > 0.5).astype(np.float32))
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(m, (0, 0), 1.6)

_txt_cache = {}
_lyr_y = {}
def lyric_sprite(text):
    if text in _txt_cache: return _txt_cache[text]
    f = font('InterDisplay-Black.otf', 440)
    track = 6
    wid = sum(f.getlength(ch) for ch in text) + track*(len(text) - 1)
    scale = min(1.0, 1640/wid)
    f = font('InterDisplay-Black.otf', int(440*scale)); track = int(6*scale)
    wid = int(sum(f.getlength(ch) for ch in text) + track*(len(text) - 1)) + 80
    asc, desc = f.getmetrics(); hh = asc + desc + 80
    img = Image.new('L', (wid, hh), 0); d = ImageDraw.Draw(img); x = 40
    for ch in text:
        d.text((x, 40), ch, font=f, fill=255); x += f.getlength(ch) + track
    a = np.asarray(img).astype(np.float32)/255
    bb = cv2.boundingRect((a > 0.01).astype(np.uint8))
    x0, y0, w0, h0 = bb; a = a[max(0, y0-30):y0+h0+30, max(0, x0-30):x0+w0+30]
    # vertical gradient fill (white -> warm) + soft glow
    hgt = a.shape[0]; grad = np.linspace(0, 1, hgt, dtype=np.float32)[:, None]
    col = np.stack([255 - 70*grad**1.5, 255 - 25*grad**1.5, np.full_like(grad, 255)], -1) * np.ones((1, a.shape[1], 1), np.float32)
    glow = cv2.GaussianBlur(a, (0, 0), 18)
    _txt_cache[text] = (a, col, glow)
    return _txt_cache[text]

def lyric_at(t):
    for t0, t1, txt in LYRICS:
        if t0 - 0.001 <= t < t1: return t0, t1, txt
    return None

def composite_lyric(f, t):
    L = lyric_at(t)
    if L is None: return f
    t0, t1, txt = L
    a, col, glow = lyric_sprite(txt)
    k_in = ease_out_expo((t - t0)/0.22); op = smooth((t - t0)/0.05) * (1 - smooth((t - (t1 - 0.06))/0.06))
    sc = 1.12 - 0.12*k_in
    h0, w0 = a.shape
    nw, nh = max(2, int(w0*sc)), max(2, int(h0*sc))
    aa = cv2.resize(a, (nw, nh), interpolation=cv2.INTER_LINEAR)
    cc = cv2.resize(col, (nw, nh), interpolation=cv2.INTER_LINEAR)
    gg = cv2.resize(glow, (nw, nh), interpolation=cv2.INTER_LINEAR)
    if k_in < 0.98:
        bl = (1 - k_in)*9
        aa = cv2.GaussianBlur(aa, (0, 0), 0.1 + bl); cc = cv2.GaussianBlur(cc, (0, 0), 0.1 + bl)
    full = subject_mask(f)
    if t0 not in _lyr_y:   # anchor the word so the car/body covers its lower part (fixed per word, no jitter)
        rows = np.nonzero(full[:, W//4:3*W//4].max(1) > 0.5)[0]
        top = rows.min() if len(rows) else int(H*0.55)
        _lyr_y[t0] = int(np.clip(top + h0*0.05, H*0.36, H*0.62))
    cx, cy = W//2, _lyr_y[t0]
    x0, y0 = cx - nw//2, cy - nh//2
    xa, ya, xb, yb = max(0, x0), max(0, y0), min(W, x0+nw), min(H, y0+nh)
    sub = full[ya:yb, xa:xb][..., None]
    aa = aa[ya-y0:yb-y0, xa-x0:xb-x0, None]*op; cc = cc[ya-y0:yb-y0, xa-x0:xb-x0]; gg = gg[ya-y0:yb-y0, xa-x0:xb-x0, None]*op
    reg = f[ya:yb, xa:xb].astype(np.float32)
    vis = (1 - sub)
    reg = reg*(1 - 0.35*gg*vis)                      # soft dark halo for legibility on bright sky
    reg = reg*(1 - aa*vis) + cc*aa*vis
    out = f.copy(); out[ya:yb, xa:xb] = np.clip(reg, 0, 255).astype(np.uint8)
    return out

BEAT = 60/117.45
def beat_kick(t):
    """decaying pulse on every beat after the drop (t=8.68)"""
    if t < 8.68: return 0.0
    ph = (t - 8.68) % BEAT
    return math.exp(-ph/0.11)

tracker = None
def seg_frame(si, lt):
    """Render segment si at local time lt with its own motion FX (graded)."""
    global tracker
    s = segs[si]; i = int(round(lt*FPS)); f, spd = s.frame(i)
    sc, dx, dy, rot, ca, flash = 1.0, 0.0, 0.0, 0.0, 0.0, 0.0
    if s.name == 'A':
        sc = 1.0 + 0.07*smooth(lt/s.dur) ; dx = -25*smooth(lt/s.dur)
    elif s.name == 'B':
        sc = 1.10 - 0.06*ease_out_cubic(lt/s.dur); dx = 30*ease_out_cubic(lt/s.dur)
    elif s.name == 'C':
        sc = 1.0 + 0.07*smooth(lt/s.dur)
        for p in C_POPS:
            if lt >= p:
                k = math.exp(-(lt - p)/0.09)
                sc += 0.05*k; ca += 7*k; flash += 0.10*k
                sx, sy = shake(lt, 14*k, seed=int(p*100)); dx += sx; dy += sy
    elif s.name == 'D':
        sc = 1.05; sx, sy = shake(lt, 3.0 + 3.0*(spd > 1.5), seed=3); dx, dy = sx, sy
        if 0.45 <= lt < 0.9:  # impact as slow-mo kicks in
            k = math.exp(-(lt - 0.45)/0.12); sc += 0.06*k; ca += 6*k; flash += 0.06*k
        if lt < 0.6:  # launch shake
            sx, sy = shake(lt, 10*(1 - lt/0.6), seed=9); dx += sx; dy += sy
        tg = starts[si] + lt; kb = beat_kick(tg)
        if spd > 1.4: sc += 0.03*kb
    elif s.name == 'G':
        sc = 1.0 + 0.10*ease_in_cubic(lt/s.dur)**0.8 + 0.02*beat_kick(starts[si] + lt)
    f = grade(f)
    if s.name == 'C':  # backfire flames tracked to the exhaust tips
        if tracker is None: tracker = TipTracker(grade(cv2.imread(os.path.join(BASE, 'work', 'ex.png'))))
        pos = tracker.update(f) if s.src_start + lt >= 19.0 else dict(TIP_REF)
        k = sum(math.exp(-(lt - p)/0.09) for p in C_POPS if lt >= p) + \
            sum(math.exp(-(p - lt)/0.012)*0.4 for p in C_POPS if lt < p)
        if k > 0.003:
            ff = f.astype(np.float32); fl = 0.75 + 0.5*rng.random()
            for key in ('L', 'R'):
                x, y = pos[key]
                for off in (-40, 40):
                    add_sprite(ff, CORE, x + off, y, min(1.8, 1.8*k)*fl)
                    add_sprite(ff, MID, x + off, y + 4, min(1.6, 1.6*k)*fl)
                add_sprite(ff, OUTER, x, y + 10, min(1.4, 1.4*k))
            ff[700:] += np.array([0, 25, 70], np.float32)*min(1, k)*0.6
            f = np.clip(ff, 0, 255).astype(np.uint8)
    f = composite_lyric(f, starts[si] + lt)
    f = affine(f, sc, dx, dy, rot)
    if ca > 0.5: f = chroma(f, ca)
    if flash > 0.003: f = cv2.addWeighted(f, 1 - flash, np.full_like(f, (180, 220, 255)), flash, 0)
    return f

def poster_scene(t):
    return poster_frame(t, POSTER_T + TT['mstripe'])

def transition(kind, fa, fb_fn, u, Tsec):
    if kind == 'whip' or kind == 'whipv':
        e = ease_io_quart(u); v = deriv(ease_io_quart, u)*(W if kind == 'whip' else H)/(Tsec*FPS)
        fb = fb_fn()
        if kind == 'whip':
            a = affine(fa, 1 + 0.08*math.sin(math.pi*u), -e*W, 0); b = affine(fb, 1 + 0.08*math.sin(math.pi*u), (1-e)*W, 0)
            mask = (vx < (1-e)*W)[..., None]
            out = np.where(mask, a, b); return motion_blur(out, v*0.6, 1)
        a = affine(fa, 1 + 0.06*math.sin(math.pi*u), 0, -e*H); b = affine(fb, 1 + 0.06*math.sin(math.pi*u), 0, (1-e)*H)
        mask = (vy < (1-e)*H)[..., None]
        out = np.where(mask, a, b); return motion_blur(out, 1, v*0.6)
    if kind == 'zoom':
        if u < 0.5:
            uu = u*2; s = 1 + 1.3*ease_in_cubic(uu); amt = 0.35*deriv(ease_in_cubic, uu)/3
            out = radial_blur(affine(fa, s), amt)
            if u > 0.42:
                fb = fb_fn(); s2 = 2.3 - 1.3*ease_out_cubic(0); bb = radial_blur(affine(fb, s2), 0.35)
                m = smooth((u - 0.42)/0.16); out = cv2.addWeighted(out, 1-m, bb, m, 0)
            return out
        uu = (u - .5)*2; s = 2.3 - 1.3*ease_out_cubic(uu); amt = 0.35*deriv(ease_out_cubic, uu)/3
        out = radial_blur(affine(fb_fn(), s), amt)
        if u < 0.58:
            aa = radial_blur(affine(fa, 2.3), 0.35); m = smooth((u - 0.42)/0.16)
            out = cv2.addWeighted(aa, 1-m, out, m, 0)
        return out
    if kind == 'spin':
        if u < 0.5:
            uu = u*2; r = 70*ease_in_cubic(uu); spread = 26*deriv(ease_in_cubic, uu)/3
            out = spin_blur(fa, spread, 1 + 0.5*ease_in_cubic(uu), -r)
            if u > 0.44:
                bb = spin_blur(fb_fn(), 26, 1.5, 70); m = smooth((u - 0.44)/0.12); out = cv2.addWeighted(out, 1-m, bb, m, 0)
            return out
        uu = (u - .5)*2; r = 70*(1 - ease_out_cubic(uu)); spread = 26*deriv(ease_out_cubic, uu)/3
        out = spin_blur(fb_fn(), spread, 1 + 0.5*(1 - ease_out_cubic(uu)), r)
        if u < 0.56:
            aa = spin_blur(fa, 26, 1.5, -70); m = smooth((u - 0.44)/0.12); out = cv2.addWeighted(aa, 1-m, out, m, 0)
        return out
    if kind == 'mstripe':
        # push into the car with radial blur while M-stripes sweep the poster in
        s = 1 + 0.45*ease_in_cubic(u); a = radial_blur(affine(fa, s, 0, 0), 0.12*ease_in_cubic(u))
        lk = math.sin(math.pi*clamp(u*1.3))
        a = cv2.addWeighted(a, 1 - 0.25*lk, np.full_like(a, (30, 110, 255)), 0.25*lk, 0)
        return mstripe(a, fb_fn(), u)
    raise ValueError(kind)

def bars_h(t):
    base = 96
    if t < 0.75: return int(540 - (540 - base)*ease_out_expo(t/0.75))  # eye-open intro
    pt = t - poster_start
    if pt > 0: return int(base*(1 - ease_io_cubic(pt/0.9)))
    return base

def render_frame(n):
    t = n/FPS
    if t >= poster_start + TT['mstripe']:
        f = poster_scene(t - poster_start)
    else:
        # find active segment(s)
        si = next((i for i in range(len(segs)) if t < starts[i] + segs[i].dur - 1e-9), len(segs) - 1)
        lt = t - starts[si]; s = segs[si]
        tt = TT[trans[si]]; t0 = s.dur - tt
        fa = seg_frame(si, lt)
        if lt >= t0 - 1e-9:
            u = (lt - t0)/tt
            if si + 1 < len(segs):
                fb_fn = lambda: seg_frame(si + 1, lt - t0)
            else:
                fb_fn = lambda: poster_scene(lt - t0)
            f = transition(trans[si], fa, fb_fn, u, tt)
        else:
            f = fa
        # title over intro
        if si == 0: f = over(f, text_layer(t - 0.35))
    # global finishing: vignette, grain, bars, fades
    ff = f.astype(np.float32)*VIG
    g = GRAIN[n % len(GRAIN)]
    ff += cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    fade = 1.0
    if t < 0.25: fade = smooth(t/0.25)
    if t > TOTAL - 0.8: fade = 1 - smooth((t - (TOTAL - 0.8))/0.8)
    ff *= fade
    f = np.clip(ff, 0, 255).astype(np.uint8)
    b = bars_h(t)
    if b > 0: f[:b] = 0; f[H-b:] = 0
    return f

def main():
    n0, n1 = 0, NF
    if PREVIEW:
        a, b = map(float, PREVIEW.split(',')); n0, n1 = int(a*FPS), min(NF, int(b*FPS))
    if os.environ.get('STILLS'):
        for ts in map(float, os.environ['STILLS'].split(',')):
            # stills need sequential readers -> render from scratch per still is slow; only for debugging
            pass
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', os.environ.get('X264_PRESET', 'slow'),
                            '-crf', os.environ.get('CRF', '14'), '-pix_fmt', 'yuv420p', '-r', str(FPS),
                            '-g', '120', '-bf', '3', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
    import time; t0 = time.time()
    for n in range(n0, n1):
        if PREVIEW and n == n0:
            # warm the readers up to the preview start
            pass
        enc.stdin.write(render_frame(n).tobytes())
        if n % 120 == 0: print(f'frame {n}/{NF} {time.time()-t0:.0f}s', flush=True)
    enc.stdin.close(); enc.wait()
    print('done', OUT, f'{time.time()-t0:.0f}s')

if __name__ == '__main__':
    main()

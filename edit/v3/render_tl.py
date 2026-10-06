#!/usr/bin/env python3
"""BMRP TikTok edit: gameplay (top) + facecam (bottom), motion FX, new captions."""
import json, math, random, subprocess, sys
import numpy as np, cv2

S = sys.argv[1] if len(sys.argv) > 1 else '.'
PREVIEW = '--preview' in sys.argv
W, H, FPS = 1080, 1920, 30
SRC = f'{S}/Timeline.1.mp4'
DUR = 42.65
END_ZOOM = 41.2                   # "Uđi na BMRP" -> push in to the end
FH = 610                          # facecam panel (top) height in the user's timeline
GH = H - FH                       # gameplay panel (bottom) height
SEAM = FH
NF = int(DUR * FPS)
if PREVIEW:
    NF = int(12 * FPS)

random.seed(7)
sys.path.insert(0, S)
from clean_tl import clean

def reader(path, vf, w, h):
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf', vf, '-f', 'rawvideo',
           '-pix_fmt', 'bgr24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=w * h * 3 * 4)
    size = w * h * 3
    last = None
    while True:
        buf = p.stdout.read(size)
        if len(buf) < size:
            while True:
                yield last
        last = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        yield last

src = reader(SRC, f'fps={FPS}', W, H)

# ---------------------------------------------------------------- events
cuts = [4.55, 6.33, 8.98, 11.28, 12.43, 15.4, 17.33, 18.6, 19.98, 22.8, 23.73,
        24.85, 26.17, 27.45, 28.6, 29.25, 30.43, 31.67, 34.43, 36.45,
        37.65, 39.3, 41.12]
events = [0.0]
for c in cuts:
    if c - events[-1] >= 1.2:
        events.append(c)
# fill gaps so there is something every <= 3 s
filled = []
for a, b in zip(events, events[1:] + [DUR]):
    filled.append(a)
    gap = b - a
    k = int(gap // 2.0)
    for i in range(1, k + 1):
        t = a + gap * i / (k + 1)
        if b - t > 1.2:
            filled.append(t)
events = sorted(t for t in filled if t < END_ZOOM - 0.8)

FX = ['punch', 'whip', 'shake_rgb', 'zoomout', 'tilt', 'glitch', 'punch_face',
      'flash_punch', 'slide_up']
plan = []
for i, t in enumerate(events):
    fx = FX[i % len(FX)] if i else 'intro'
    plan.append((t, fx))
json.dump(plan, open(f'{S}/tl/events.json', 'w'))

def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3

def spring(x, k=9.0, damp=5.0):
    """0 -> overshoot -> settle at 1."""
    if x <= 0:
        return 0.0
    return 1 - math.exp(-damp * x) * math.cos(k * x)

def affine(img, scale=1.0, dx=0.0, dy=0.0, rot=0.0, border=cv2.BORDER_REFLECT):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
    M[0, 2] += dx
    M[1, 2] += dy
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR,
                          borderMode=border)

def motion_blur(img, k, horizontal=True):
    k = int(k) | 1
    if k < 3:
        return img
    ker = np.zeros((k, k), np.float32)
    if horizontal:
        ker[k // 2, :] = 1.0 / k
    else:
        ker[:, k // 2] = 1.0 / k
    return cv2.filter2D(img, -1, ker)

def rgb_split(img, off):
    off = int(off)
    if off == 0:
        return img
    b, g, r = cv2.split(img)
    r = np.roll(r, off, axis=1)
    b = np.roll(b, -off, axis=1)
    return cv2.merge([b, g, r])

def glitch(img, amt, rng):
    out = img.copy()
    h = img.shape[0]
    for _ in range(int(6 * amt) + 2):
        y = rng.randint(0, h - 40)
        hh = rng.randint(10, 70)
        sh = rng.randint(-80, 80)
        out[y:y + hh] = np.roll(out[y:y + hh], int(sh * amt), axis=1)
    return rgb_split(out, 14 * amt)

def vignette(w, h, strength):
    X = cv2.getGaussianKernel(w, w * 0.65)
    Y = cv2.getGaussianKernel(h, h * 0.65)
    m = Y @ X.T
    m = m / m.max()
    return (1 - strength + strength * m)[..., None].astype(np.float32)

VIG_F = vignette(W, FH, 0.45)
VIG_G = vignette(W, GH, 0.35)

def apply_fx(name, local, gimg, fimg, t, rng):
    """local = seconds since event start. returns (gimg, fimg, frame_post)"""
    post = {}
    if name == 'intro':
        s = 1.35 - 0.35 * ease_out(local / 0.6)
        gimg = affine(gimg, s)
        fimg = affine(fimg, 1.25 - 0.25 * ease_out(local / 0.7))
        post['flash'] = max(0, 1 - local / 0.35)
    elif name == 'punch':
        s = 1 + 0.16 * (1 - ease_out(local / 0.5)) if local > 0.06 else 1 + 0.16 * local / 0.06
        gimg = affine(gimg, s)
        if local < 0.12:
            gimg = motion_blur(gimg, 25 * (1 - local / 0.12), False)
    elif name == 'punch_face':
        s = 1 + 0.18 * (1 - ease_out(local / 0.6)) if local > 0.06 else 1 + 0.18 * local / 0.06
        fimg = affine(fimg, s)
        post['shake'] = max(0, 1 - local / 0.3) * 8
    elif name == 'whip':
        if local < 0.22:
            p = ease_out(local / 0.22)
            dx = (1 - p) * W * 0.9
            gimg = motion_blur(affine(gimg, 1.05, dx, border=cv2.BORDER_WRAP), 61 * (1 - p) + 1, True)
    elif name == 'slide_up':
        if local < 0.25:
            p = ease_out(local / 0.25)
            gimg = motion_blur(affine(gimg, 1.06, 0, (1 - p) * GH * 0.7, border=cv2.BORDER_WRAP), 51 * (1 - p) + 1, False)
            fimg = affine(fimg, 1 + 0.08 * (1 - p))
    elif name == 'shake_rgb':
        a = max(0, 1 - local / 0.45)
        gimg = rgb_split(affine(gimg, 1.06, rng.uniform(-22, 22) * a,
                                rng.uniform(-22, 22) * a, rng.uniform(-2, 2) * a), 18 * a)
        fimg = affine(fimg, 1.03, rng.uniform(-8, 8) * a, rng.uniform(-8, 8) * a)
    elif name == 'zoomout':
        if local < 0.5:
            s = 1 + 0.3 * abs(1 - spring(local / 0.5, 8, 4))
            gimg = affine(gimg, s)
    elif name == 'tilt':
        if local < 0.6:
            a = math.sin(local / 0.6 * math.pi) * (1 - local / 0.6 * 0.5)
            gimg = affine(gimg, 1.1 + 0.05 * a, 0, 0, 4 * a)
            fimg = affine(fimg, 1.04 + 0.03 * a, 0, 0, -2.5 * a)
    elif name == 'glitch':
        if local < 0.25:
            a = 1 - local / 0.25
            gimg = glitch(gimg, a, rng)
            fimg = rgb_split(fimg, 10 * a)
    elif name == 'flash_punch':
        post['flash'] = max(0, 0.85 - local / 0.18)
        s = 1 + 0.12 * (1 - ease_out(local / 0.45))
        gimg = affine(gimg, s)
        fimg = affine(fimg, 1 + 0.06 * (1 - ease_out(local / 0.45)))
    return gimg, fimg, post

# continuous facecam push-in between events (ken burns) + pulse
def face_base(fimg, t):
    s = 1.04 + 0.04 * math.sin(t * 0.55)
    return affine(fimg, s, 0, 0, 0.6 * math.sin(t * 0.9))

ACCENT = (40, 230, 255)    # BGR yellow-gold

EMOJI = json.load(open(f'{S}/tl/emoji_plan.json'))
for e in EMOJI:
    im = cv2.imread(f'{S}/emoji/package/img/apple/64/{e["code"]}.png', cv2.IMREAD_UNCHANGED)
    e['img'] = cv2.resize(im, (176, 176), interpolation=cv2.INTER_LANCZOS4)

def paste_rgba(frame, img, cx, cy, scale, rot, alpha):
    if scale <= 0.02 or alpha <= 0:
        return
    sz = int(img.shape[0] * scale) | 1
    M = cv2.getRotationMatrix2D((img.shape[1] / 2, img.shape[0] / 2), rot, scale)
    M[0, 2] += sz / 2 - img.shape[1] / 2
    M[1, 2] += sz / 2 - img.shape[0] / 2
    im = cv2.warpAffine(img, M, (sz, sz), flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    x0, y0 = int(cx - sz / 2), int(cy - sz / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + sz, W), min(y0 + sz, H)
    if xa >= xb or ya >= yb:
        return
    sub = im[ya - y0:yb - y0, xa - x0:xb - x0].astype(np.float32)
    a = sub[..., 3:4] / 255.0 * alpha
    # soft drop shadow
    roi = frame[ya:yb, xa:xb].astype(np.float32)
    roi = roi * (1 - a) + sub[..., :3] * a
    frame[ya:yb, xa:xb] = roi.astype(np.uint8)

def draw_emojis(frame, t):
    for e in EMOJI:
        if not (e['t'] <= t < e['end']):
            continue
        l = t - e['t']
        rem = e['end'] - t
        sc = spring(l / 0.35, 10, 6) if l < 0.6 else 1.0
        if rem < 0.12:
            sc *= rem / 0.12
        rot = 12 * math.sin(l * 9) * math.exp(-l * 3) + 4 * math.sin(l * 3)
        bob = 8 * math.sin(l * 5)
        paste_rgba(frame, e['img'], e['x'], e['y'] + bob, max(sc, 0), rot, 1.0)
ACCENT2 = (80, 255, 60)    # green

out_path = f'{S}/tl/video_noaudio{"_prev" if PREVIEW else ""}.mp4'
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                        '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264',
                        '-preset', 'veryfast' if PREVIEW else 'medium', '-crf', '17',
                        '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)

grain_rng = np.random.default_rng(1)
ev_times = [p[0] for p in plan]
for fi in range(NF):
    t = fi / FPS
    full = clean(next(src))
    f = face_base(full[:FH].copy(), t)
    g = full[FH:].copy()
    # current event
    idx = max(i for i, et in enumerate(ev_times) if et <= t + 1e-6)
    et, name = plan[idx]
    local = t - et
    rng = random.Random(fi)
    g, f, post = apply_fx(name, local, g, f, t, rng)
    g = (g.astype(np.float32) * VIG_G).astype(np.uint8)
    f = (f.astype(np.float32) * VIG_F).astype(np.uint8)

    frame = np.empty((H, W, 3), np.uint8)
    frame[:FH] = f
    frame[FH:] = g


    # glowing divider with moving highlight
    glow = np.zeros((60, W, 3), np.uint8)
    cv2.line(glow, (0, 30), (W, 30), ACCENT, 6)
    glow = cv2.GaussianBlur(glow, (0, 0), 9)
    band = frame[SEAM - 30:SEAM + 30].astype(np.int16) + glow.astype(np.int16)
    frame[SEAM - 30:SEAM + 30] = np.clip(band, 0, 255).astype(np.uint8)
    cv2.line(frame, (0, SEAM), (W, SEAM), (255, 255, 255), 4)
    hx = int((t * 700) % (W + 400)) - 200
    cv2.line(frame, (max(hx - 160, 0), SEAM), (min(hx + 160, W), SEAM), ACCENT, 8)

    # ending: continuous push-in over "Uđi na BMRP odmah", punch + shake on BMRP
    if t >= END_ZOOM:
        l = t - END_ZOOM
        sc = 1 + 0.55 * ease_out(l / 1.45)
        hit = max(0.0, 1 - abs(t - 41.86) / 0.18)
        sc += 0.08 * hit
        # push in towards his face (top panel), so the end lands on him
        cy = 960 + (330 - 960) * ease_out(l / 1.0)
        M = cv2.getRotationMatrix2D((540, cy), 0, sc)
        M[0, 2] += rng.uniform(-14, 14) * hit
        M[1, 2] += rng.uniform(-14, 14) * hit + (960 - cy) * 0.0
        frame = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if hit > 0:
            frame = rgb_split(frame, 16 * hit)
        post['flash'] = max(post.get('flash', 0), 0.6 * max(0.0, 1 - abs(t - 41.86) / 0.08))

    draw_emojis(frame, t)

    # top progress bar
    cv2.rectangle(frame, (0, 0), (W, 10), (30, 30, 30), -1)
    cv2.rectangle(frame, (0, 0), (int(W * t / DUR), 10), ACCENT2, -1)

    # frame-level post FX
    sh = post.get('shake', 0)
    if sh:
        frame = affine(frame, 1.01, rng.uniform(-sh, sh), rng.uniform(-sh, sh))
    fl = post.get('flash', 0)
    if fl > 0:
        frame = cv2.addWeighted(frame, 1 - fl, np.full_like(frame, 255), fl, 0)
    # subtle film grain
    if fi % 2 == 0:
        noise = grain_rng.integers(-6, 7, (H // 2, W // 2, 1), dtype=np.int16)
    nz = cv2.resize(noise.astype(np.float32), (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    frame = np.clip(frame.astype(np.int16) + nz.astype(np.int16), 0, 255).astype(np.uint8)

    enc.stdin.write(frame.tobytes())
    if fi % 150 == 0:
        print(f'{t:5.1f}s {name}', flush=True)

enc.stdin.close()
enc.wait()
print('done', out_path)

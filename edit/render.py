#!/usr/bin/env python3
"""BMRP TikTok edit: gameplay (top) + facecam (bottom), motion FX, new captions."""
import json, math, random, subprocess, sys
import numpy as np, cv2

S = sys.argv[1] if len(sys.argv) > 1 else '.'
PREVIEW = '--preview' in sys.argv
W, H, FPS = 1080, 1920, 30
FACE, GAME = f'{S}/BMRP.1.mp4', f'{S}/nopromo9.mp4'
DUR = 42.70
GAME_DUR = 47.0
SPEED = GAME_DUR / DUR            # gameplay sped up so the whole promo fits
GH = 1150                         # gameplay panel height (stops above old yellow captions)
FH = H - GH                       # facecam panel height
NF = int(DUR * FPS)
if PREVIEW:
    NF = int(12 * FPS)

random.seed(7)

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

# gameplay: speed up, top crop above the burned-in captions, slight grade
game = reader(GAME, f'setpts=PTS/{SPEED},fps={FPS},'
                    'eq=contrast=1.08:saturation=1.25', W, H)
# source-time ranges where red titles sit at y~865-935: zoom into the area above them
RED = [(8.8, 11.35), (15.3, 17.4), (19.9, 22.85), (27.4, 28.65), (31.4, 36.5), (39.25, 41.15)]

def game_window(full, t):
    ts = t * SPEED
    if any(a <= ts < b for a, b in RED):
        win = full[0:855, 140:940]
    else:
        win = full[0:GH, 0:W]
    return cv2.resize(win, (W, GH), interpolation=cv2.INTER_LINEAR)
# facecam: crop around face to fill the bottom panel
face = reader(FACE, f'fps={FPS},crop=1420:1012:250:0,scale={W}:{FH},'
                    'eq=contrast=1.06:saturation=1.12:brightness=0.01', W, FH)

# ---------------------------------------------------------------- events
cuts = [4.55, 6.33, 8.98, 11.28, 12.43, 15.4, 17.33, 18.6, 19.98, 22.8, 23.73,
        24.85, 26.17, 27.45, 28.6, 29.25, 30.43, 31.67, 34.43, 35.18, 36.45,
        37.65, 39.3, 41.12]
cuts = [c / SPEED for c in cuts]          # map to output time
events = [0.0]
for c in cuts:
    if c - events[-1] >= 1.6:
        events.append(c)
# fill gaps so there is something every <= 3 s
filled = []
for a, b in zip(events, events[1:] + [DUR]):
    filled.append(a)
    gap = b - a
    k = int(gap // 2.6)
    for i in range(1, k + 1):
        t = a + gap * i / (k + 1)
        if b - t > 1.2:
            filled.append(t)
events = sorted(filled)

FX = ['punch', 'whip', 'shake_rgb', 'zoomout', 'tilt', 'glitch', 'punch_face',
      'flash_punch', 'slide_up']
plan = []
for i, t in enumerate(events):
    fx = FX[i % len(FX)] if i else 'intro'
    plan.append((t, fx))
json.dump(plan, open(f'{S}/events.json', 'w'))

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
ACCENT2 = (80, 255, 60)    # green

out_path = f'{S}/video_noaudio{"_prev" if PREVIEW else ""}.mp4'
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24',
                        '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264',
                        '-preset', 'veryfast' if PREVIEW else 'medium', '-crf', '17',
                        '-pix_fmt', 'yuv420p', out_path], stdin=subprocess.PIPE)

grain_rng = np.random.default_rng(1)
ev_times = [p[0] for p in plan]
for fi in range(NF):
    t = fi / FPS
    g = game_window(next(game), t)
    f = next(face).copy()
    f = face_base(f, t)
    # current event
    idx = max(i for i, et in enumerate(ev_times) if et <= t + 1e-6)
    et, name = plan[idx]
    local = t - et
    rng = random.Random(fi)
    g, f, post = apply_fx(name, local, g, f, t, rng)
    g = (g.astype(np.float32) * VIG_G).astype(np.uint8)
    f = (f.astype(np.float32) * VIG_F).astype(np.uint8)

    frame = np.empty((H, W, 3), np.uint8)
    frame[:GH] = g
    frame[GH:] = f

    # glowing divider with moving highlight
    glow = np.zeros((60, W, 3), np.uint8)
    cv2.line(glow, (0, 30), (W, 30), ACCENT, 6)
    glow = cv2.GaussianBlur(glow, (0, 0), 9)
    band = frame[GH - 30:GH + 30].astype(np.int16) + glow.astype(np.int16)
    frame[GH - 30:GH + 30] = np.clip(band, 0, 255).astype(np.uint8)
    cv2.line(frame, (0, GH), (W, GH), (255, 255, 255), 4)
    hx = int((t * 700) % (W + 400)) - 200
    cv2.line(frame, (max(hx - 160, 0), GH), (min(hx + 160, W), GH), ACCENT, 8)

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

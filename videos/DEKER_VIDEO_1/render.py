import sys, json, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

SRC, FACE, OUT_RAW = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1080, 1920, 30
SW, SH = 478, 850
FONT = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
YELLOW, WHITE, RED, BLACK = (255, 230, 0), (255, 255, 255), (235, 30, 45), (0, 0, 0)

# ---------- captions (word timings from Whisper DTW, snapped to the loudness envelope) ----------
CHUNKS = [
    [("UNIVERZITET", 0.05, 1.00), ("JE", 1.00, 1.45)],
    [("MESTO", 1.55, 2.05), ("GDE", 2.05, 2.25), ("SE", 2.25, 2.40), ("UČI.", 2.40, 3.05)],
    [("NE", 3.15, 3.40), ("SME,", 3.40, 3.95)],
    [("NE", 3.95, 4.30), ("MOŽE", 4.30, 4.85)],
    [("I", 4.85, 5.05), ("NEĆE", 5.05, 5.40)],
    [("BITI", 5.40, 5.85), ("POLIGON", 5.85, 6.40)],
    [("ZA", 6.40, 6.55), ("NEŠTO", 6.55, 6.85), ("DRUGO.", 6.85, 7.62)],
]
KEYWORDS = {"UNIVERZITET", "POLIGON", "UČI.", "SME,", "MOŽE", "NEĆE"}
T_TACKA = 7.72

# ---------- face track: drop outliers, smooth ----------
face = json.load(open(FACE))
fx = np.array([f[0] if f else np.nan for f in face]); fy = np.array([f[1] if f else np.nan for f in face])
for arr in (fx, fy):
    med = np.array([np.nanmedian(arr[max(0, i - 15):i + 16]) for i in range(len(arr))])
    arr[np.abs(arr - med) > 40] = np.nan
    idx = np.arange(len(arr)); ok = ~np.isnan(arr)
    arr[:] = np.interp(idx, idx[ok], arr[ok])
k = np.ones(21) / 21
fx = np.convolve(np.pad(fx, 10, mode="edge"), k, "valid"); fy = np.convolve(np.pad(fy, 10, mode="edge"), k, "valid")

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def lerp(a, b, x): return a + (b - a) * x

def zoom_at(t):
    """Zoom factor + how strongly the frame centres on the face."""
    if t < 0.45:   return lerp(1.30, 1.06, ease(t / 0.45)), 0.5
    if t < 3.15:   return lerp(1.06, 1.14, (t - 0.45) / 2.7), 0.5
    if t < 4.85:   return lerp(1.38, 1.46, (t - 3.15) / 1.7), 0.9          # punch-in: "ne sme, ne može"
    if t < 5.85:   return lerp(1.10, 1.16, (t - 4.85) / 1.0), 0.6
    if t < 7.72:   return lerp(1.28, 1.36, (t - 5.85) / 1.87), 0.85        # "poligon za nešto drugo"
    return lerp(1.85, 1.60, ease((t - 7.72) / 0.35)), 1.0                   # "TAČKA."

def shake(t):
    if t < T_TACKA: return 0, 0
    d = t - T_TACKA; a = 18 * math.exp(-d * 9)
    return a * math.sin(d * 95), a * math.cos(d * 77)

def frame_transform(i, t):
    z, w_face = zoom_at(t)
    cw, ch = SW / z, SH / z
    cx = lerp(SW / 2, fx[min(i, len(fx) - 1)], w_face)
    cy = lerp(SH / 2, fy[min(i, len(fy) - 1)] + 120, w_face)   # keep the face in the upper part
    cx = min(max(cx, cw / 2), SW - cw / 2); cy = min(max(cy, ch / 2), SH - ch / 2)
    s = W / cw
    sx, sy = shake(t)
    M = np.array([[s, 0, W / 2 - cx * s + sx], [0, s, H / 2 - cy * s + sy]], np.float32)
    return M

# ---------- grading / sharpening ----------
yy, xx = np.mgrid[0:H, 0:W]
vign = 1 - 0.28 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.4
vign = np.clip(vign, 0.62, 1)[..., None].astype(np.float32)

def enhance(img):
    blur = cv2.GaussianBlur(img, (0, 0), 2.2)
    img = cv2.addWeighted(img, 1.55, blur, -0.55, 0)               # unsharp mask
    f = img.astype(np.float32) / 255
    f = np.clip((f - 0.5) * 1.07 + 0.5, 0, 1)                        # contrast
    f = f * vign
    return (np.clip(f, 0, 1) * 255).astype(np.uint8)

# ---------- text rendering ----------
_fonts = {}
def font(sz):
    sz = max(8, int(sz))
    if sz not in _fonts: _fonts[sz] = ImageFont.truetype(FONT, sz)
    return _fonts[sz]

def text_w(s, sz): return font(sz).getlength(s)

def draw_text(d, xy, s, sz, fill, stroke=None, anchor="mm"):
    sw = stroke if stroke is not None else max(3, int(sz * 0.11))
    d.text(xy, s, font=font(sz), fill=fill, stroke_width=sw, stroke_fill=BLACK, anchor=anchor)

def pop(x):
    """overshoot pop 0..1 -> scale"""
    if x >= 1: return 1.0
    x = max(x, 0); return 1 + 0.35 * math.sin(x * math.pi) * (1 - x) - 0.3 * (1 - x) ** 3

def caption_layer(d, t):
    for chunk in CHUNKS:
        c0, c1 = chunk[0][1], chunk[-1][2]
        if not (c0 <= t < c1): continue
        base = 96
        words = [w for w, _, _ in chunk]
        gap = base * 0.30
        widths = [text_w(w, base) for w in words]
        total = sum(widths) + gap * (len(words) - 1)
        if total > W - 160:  # two lines when too wide
            lines = [list(range(len(words) // 2 + 1)), list(range(len(words) // 2 + 1, len(words)))]
        else:
            lines = [list(range(len(words)))]
        sc_chunk = pop((t - c0) / 0.16)
        y0 = 1330 - (len(lines) - 1) * base * 0.6
        for li, line in enumerate(lines):
            sizes = {}
            for j in line:
                w, ws, we = chunk[j]
                active = ws <= t < we
                sizes[j] = base * sc_chunk * (1.14 * pop((t - ws) / 0.12) if active else 1.0)
            g = gap * sc_chunk
            lw = sum(text_w(chunk[j][0], sizes[j]) for j in line) + g * (len(line) - 1)
            x = W / 2 - lw / 2
            y = y0 + li * base * 1.2
            for j in line:
                w, ws, we = chunk[j]
                active = ws <= t < we
                sz = sizes[j]; ww = text_w(w, sz)
                col = (YELLOW if w not in KEYWORDS else (80, 255, 120)) if active else WHITE
                if active and w == "POLIGON": col = RED
                cx = x + ww / 2
                draw_text(d, (cx + 5, y + 7), w, sz, (0, 0, 0, 150), stroke=0)          # drop shadow
                draw_text(d, (cx, y), w, sz, col)
                x += ww + g

def hook_layer(img, d, t):
    if t >= T_TACKA: return
    # big hook 0..2.9s, then shrinks into a top title bar
    tr = ease((t - 2.9) / 0.35)
    scale = lerp(1.0, 0.58, tr) * lerp(1.12, 1.0, ease(t / 0.3))
    cy = lerp(430, 255, tr)
    l1, l2 = "UNIVERZITET", "NIJE POLIGON!"
    s1, s2 = 104 * scale, 112 * scale
    bw = max(text_w(l1, s1), text_w(l2, s2)) + 90 * scale
    bh = (s1 + s2) * 1.32
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
    tilt_box = [W / 2 - bw / 2, cy - bh / 2, W / 2 + bw / 2, cy + bh / 2]
    bd.rounded_rectangle([tilt_box[0] + 10, tilt_box[1] + 12, tilt_box[2] + 10, tilt_box[3] + 12], radius=int(28 * scale), fill=(0, 0, 0, 140))
    bd.rounded_rectangle(tilt_box, radius=int(28 * scale), fill=(*RED, 255))
    rot = lerp(-3.0, 0, tr)
    box = box.rotate(rot, center=(W / 2, cy), resample=Image.BICUBIC)
    img.alpha_composite(box)
    d = ImageDraw.Draw(img)
    draw_text(d, (W / 2, cy - bh * 0.22), l1, s1, WHITE, stroke=int(5 * scale))
    blink = YELLOW if (t < 2.9 and int(t * 4) % 2 == 0) or t >= 2.9 else WHITE
    draw_text(d, (W / 2, cy + bh * 0.24), l2, s2, blink, stroke=int(5 * scale))

def tacka_layer(img, d, t):
    if t < T_TACKA: return
    x = (t - T_TACKA)
    sc = lerp(1.3, 1.0, ease(x / 0.18))
    sz = 205 * sc
    rot = -6
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    w = text_w("TAČKA.", sz)
    ld.rounded_rectangle([W / 2 - w / 2 - 50, 1270 - sz * 0.72, W / 2 + w / 2 + 50, 1270 + sz * 0.72], radius=30, fill=(*RED, 235))
    ld.text((W / 2, 1270), "TAČKA.", font=font(sz), fill=WHITE, stroke_width=int(sz * 0.05), stroke_fill=BLACK, anchor="mm")
    lay = lay.rotate(rot, center=(W / 2, 1270), resample=Image.BICUBIC)
    img.alpha_composite(lay)

# ---------- main loop ----------
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC,
                        "-vf", "hqdn3d=2:1.5:4:3,eq=saturation=1.22:gamma=0.96:contrast=1.04,colorbalance=rs=0.03:bs=-0.03:rm=0.02:bm=-0.02",
                        "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
out = open(OUT_RAW, "wb")
i = 0
while True:
    buf = dec.stdout.read(SW * SH * 3)
    if len(buf) < SW * SH * 3: break
    src = np.frombuffer(buf, np.uint8).reshape(SH, SW, 3)
    t = i / FPS
    M = frame_transform(i, t)
    fr = cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    fr = enhance(fr)
    if T_TACKA <= t < T_TACKA + 0.1:                                      # white flash
        a = 1 - (t - T_TACKA) / 0.1
        fr = cv2.addWeighted(fr, 1 - 0.85 * a, np.full_like(fr, 255), 0.85 * a, 0)
    img = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    d = ImageDraw.Draw(img)
    hook_layer(img, d, t)
    d = ImageDraw.Draw(img)
    caption_layer(d, t)
    tacka_layer(img, d, t)
    out.write(np.asarray(img.convert("RGB")).tobytes())
    i += 1
out.close(); dec.wait()
print("frames", i)

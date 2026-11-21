import subprocess, sys, math, os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN = f"{S}/in"; FONTS = f"{S}/fonts"
FPS = 60; W, H = 1080, 1920; DUR = 23.0; NF = int(DUR * FPS)
SRCW, SRCH = 1920, 1080
YEL = (255, 212, 0); GRN = (34, 214, 141); RED = (255, 45, 45)

def F(name, size): return ImageFont.truetype(f"{FONTS}/{name}.ttf", size)

# ---------------- easing ----------------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eoc(x): x = clamp(x); return 1 - (1 - x) ** 3
def eioc(x): x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eob(x, k=1.9): x = clamp(x); return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2
def lerp(a, b, x): return a + (b - a) * x
def pw(keys, t, ease=eioc):
    """piecewise interpolation of tuples/floats over keyframes [(t, val)]"""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            x = ease((t - t0) / (t1 - t0)) if t1 > t0 else 1
            if isinstance(v0, tuple): return tuple(lerp(a, b, x) for a, b in zip(v0, v1))
            return lerp(v0, v1, x)
    return keys[-1][1]
def lin(keys, t): return pw(keys, t, ease=lambda x: clamp(x))

# ---------------- video readers ----------------
class Reader:
    def __init__(self, path):
        self.path = path; self.p = None; self.base = None; self.cur = -1; self.frame = None
    def get(self, t):
        if self.p is None:
            self.base = max(0, t - 0.0)
            self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{self.base:.4f}", "-i", self.path,
                                       "-an", "-vf", "fps=60", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                                      stdout=subprocess.PIPE, bufsize=10 ** 8)
        n = max(0, int(round((t - self.base) * FPS)))
        while self.cur < n:
            b = self.p.stdout.read(SRCW * SRCH * 3)
            if len(b) < SRCW * SRCH * 3: break
            self.frame = b; self.cur += 1
        return Image.frombuffer("RGB", (SRCW, SRCH), self.frame, "raw", "RGB", 0, 1)
READERS = {}
def R(key, file):
    if key not in READERS: READERS[key] = Reader(f"{IN}/{file}")
    return READERS[key]

# ---------------- helpers ----------------
def rounded_mask(w, h, r):
    m = Image.new("L", (w * 2, h * 2), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * 2 - 1, h * 2 - 1), r * 2, fill=255)
    return m.resize((w, h), Image.LANCZOS)
def with_alpha(img, a):
    if a >= 0.999: return img
    img = img.copy(); al = img.getchannel("A").point(lambda v: int(v * a)); img.putalpha(al); return img
def paste_c(dst, spr, cx, cy, scale=1.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0.01: return
    if abs(scale - 1) > 0.002:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))), Image.BICUBIC)
    spr = with_alpha(spr, alpha)
    dst.paste(spr, (int(cx - spr.width / 2), int(cy - spr.height / 2)), spr)
def blur_bg(img, dark=0.45, rad=5):
    small = img.resize((W // 6, H // 6), Image.BILINEAR).filter(ImageFilter.GaussianBlur(rad))
    big = small.resize((W, H), Image.BICUBIC)
    return Image.blend(Image.new("RGB", (W, H)), big, dark)
def darken(img, a): return Image.blend(img, Image.new("RGB", img.size), a) if a > 0.003 else img
def shadowed(sprite, off=(0, 10), blur=14, op=0.75, pad=40):
    w, h = sprite.size; out = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); a = sprite.getchannel("A").point(lambda v: int(v * op))
    blk = Image.new("RGBA", sprite.size, (0, 0, 0, 255)); blk.putalpha(a)
    sh.paste(blk, (pad + off[0], pad + off[1]), blk); sh = sh.filter(ImageFilter.GaussianBlur(blur))
    out = Image.alpha_composite(out, sh); out.paste(sprite, (pad, pad), sprite); return out

# ---------------- static sprites ----------------
LOGO = Image.open(f"{S}/../images/1.png").convert("RGBA")
LOGO = LOGO.crop(LOGO.getchannel("A").getbbox())
_logo_cache = {}
def logo(wd):
    wd = int(wd)
    if wd not in _logo_cache:
        _logo_cache[wd] = LOGO.resize((wd, int(LOGO.height * wd / LOGO.width)), Image.LANCZOS)
    return _logo_cache[wd]

def make_card(text):
    w, h = 640, 176
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(14, 16, 20, 235), outline=(255, 255, 255, 60), width=3)
    f = F("anton-400", 104); bb = d.textbbox((0, 0), text, font=f)
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=(245, 245, 245))
    return shadowed(c, (0, 12), 18, 0.7)
def make_x():
    s = 230; c = Image.new("RGBA", (s * 2, s * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(c); m = 40
    for col, wd in [((60, 0, 0, 255), 74), (RED + (255,), 52)]:
        d.line((m, m, s * 2 - m, s * 2 - m), fill=col, width=wd); d.line((s * 2 - m, m, m, s * 2 - m), fill=col, width=wd)
    c = c.resize((s, s), Image.LANCZOS); return shadowed(c, (0, 8), 10, 0.6, 30)
CARDS = {k: make_card(k) for k in ["FiveM", "RAGE:MP", "GTA V"]}
XSPR = make_x()

def make_pill(text, fill, tcol, fs=46, padx=44, h=96):
    f = F("montserrat-900", fs); bb = f.getbbox(text); w = bb[2] - bb[0] + padx * 2
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fill)
    d.text(((w - (bb[2] - bb[0])) / 2 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=tcol)
    return c
PILL = shadowed(make_pill("NOVA PLATFORMA", GRN + (255,), (6, 20, 13)), (0, 8), 12, 0.6)

def make_button():
    text = "PREUZMI LAUNCHER"; f = F("montserrat-900", 58); bb = f.getbbox(text)
    icon = 64; gap = 26; w = bb[2] - bb[0] + icon + gap + 120; h = 150
    c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 40, fill=GRN + (255,))
    d.rounded_rectangle((6, 6, w - 7, h // 2), 34, fill=(255, 255, 255, 38))
    x0 = 60; cy = h // 2  # download icon
    d.rectangle((x0 + 24, cy - 30, x0 + 40, cy + 2), fill=(255, 255, 255))
    d.polygon([(x0 + 6, cy), (x0 + 58, cy), (x0 + 32, cy + 26)], fill=(255, 255, 255))
    d.rectangle((x0 + 4, cy + 30, x0 + 60, cy + 38), fill=(255, 255, 255))
    tx = x0 + icon + gap
    d.text((tx - bb[0] + 2, (h - (bb[3] - bb[1])) / 2 - bb[1] + 3), text, font=f, fill=(0, 60, 35))
    d.text((tx - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), text, font=f, fill=(255, 255, 255))
    g = Image.new("RGBA", (w + 120, h + 120), (0, 0, 0, 0))
    ImageDraw.Draw(g).rounded_rectangle((60, 60, w + 60, h + 60), 40, fill=GRN + (150,))
    g = g.filter(ImageFilter.GaussianBlur(26)); g.paste(c, (60, 60), c); return g
BUTTON = make_button()
def make_tag():
    f = F("montserrat-800", 40); t = "ZAPOČNI SVOJ PUT KA USPEHU"; bb = f.getbbox(t)
    w = bb[2] - bb[0] + 200; h = 70; c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    d.text((100 - bb[0], (h - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=(255, 255, 255, 235),
           stroke_width=3, stroke_fill=(0, 0, 0, 200))
    d.line((10, h / 2, 80, h / 2), fill=GRN + (255,), width=5); d.line((w - 80, h / 2, w - 10, h / 2), fill=GRN + (255,), width=5)
    return c
TAG = make_tag()
def make_cursor():
    s = 4; pts = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
    c = Image.new("RGBA", (40 * s, 48 * s), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    P = [(x * s + 8, y * s + 8) for x, y in pts]
    d.polygon(P, fill=(255, 255, 255), outline=(0, 0, 0)); d.line(P + [P[0]], fill=(0, 0, 0), width=8)
    c = c.resize((80, 96), Image.LANCZOS); return shadowed(c, (3, 6), 6, 0.6, 16)
CURSOR = make_cursor()

def ripple_sprite(age):
    x = age / 0.45
    if x < 0 or x > 1: return None
    s = 300; c = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    r = 20 + 120 * eoc(x); a = int(255 * (1 - x)); wd = max(2, int(14 * (1 - x)))
    d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), outline=GRN + (a,), width=wd)
    r2 = 26 * (1 - x) + 6
    d.ellipse((s / 2 - r2, s / 2 - r2, s / 2 + r2, s / 2 + r2), fill=(255, 255, 255, int(200 * (1 - x))))
    return c

# ---------------- subtitles ----------------
WORDS = [("BMRP",0.03,0.38),("JE",0.38,0.74),("NAPOKON",0.74,1.44),("IZBACIO",1.44,1.86),("SVOJU",1.86,2.14),
 ("PLATFORMU",2.14,2.80),("VIŠE",2.84,3.32),("VAM",3.32,3.42),("NEĆE",3.42,3.76),("TREBATI",3.76,4.06),
 ("NI",4.06,4.24),("FIVEM",4.24,4.80),("NI",4.90,4.96),("RAGE",4.96,5.28),("MP",5.28,5.44),("I",5.44,5.72),
 ("NI",5.72,5.86),("ČAK",5.86,6.14),("LICENCIRANI",6.14,6.88),("GTA",6.88,7.12),("V",7.12,7.50),
 ("SVE",7.80,8.24),("ŠTO",8.24,8.44),("VAM",8.44,8.54),("TREBA",8.54,8.88),("JESTE",8.88,9.02),("DA",9.02,9.22),
 ("INSTALIRATE",9.22,9.78),("NAŠ",9.78,10.08),("BMRP",10.08,10.32),("LAUNCHER",10.32,10.80),("ODETE",11.20,11.64),
 ("NA",11.64,11.80),("BMRP",11.80,12.02),("SAJT",12.02,12.54),("IDETE",12.74,13.12),("ZAPOČNITE",13.12,13.70),
 ("IGRU",13.70,14.10),("I",14.10,14.22),("KLIKNITE",14.22,14.64),("PREUZMI",14.64,15.26),("POSLE",15.38,15.92),
 ("TOGA",15.92,16.16),("INSTALIRATE",16.16,16.70),("LAUNCHER",16.70,16.92),("I",16.92,17.28),("JEDNOSTAVNO",17.28,17.96),
 ("SAMO",17.96,18.14),("KLIKNITE",18.14,18.70),("IGRAJ",18.70,19.30),("VIDIMO",19.40,20.00),("SE",20.00,20.18),
 ("NA",20.18,20.32),("BMRP",20.32,20.64)]
GROUPS = [(0,2),(3,5),(6,9),(10,11),(12,14),(15,17),(18,20),(21,24),(25,27),(28,30),(31,34),(35,37),(38,40),
          (41,42),(43,44),(45,47),(48,49),(50,53)]
GREEN_W = {"BMRP", "LAUNCHER", "PREUZMI", "IGRAJ", "PLATFORMU", "SAJT", "ZAPOČNITE", "IGRU"}
RED_IDX = {11, 13, 14, 19, 20}
SUB_FS = 94; SUB_CX = 515; SUB_CY = 1290; SUB_MAXW = 860; LINE_H = 112
SUBF = F("montserrat-900", SUB_FS)
def word_sprite(txt, col):
    bb = SUBF.getbbox(txt, stroke_width=11); w = bb[2] - bb[0]; h = bb[3] - bb[1]
    c = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    ImageDraw.Draw(c).text((2 - bb[0], 2 - bb[1]), txt, font=SUBF, fill=col, stroke_width=11, stroke_fill=(0, 0, 0))
    return shadowed(c, (0, 9), 10, 0.85, 26)
SUBS = []
for gi, (a, b) in enumerate(GROUPS):
    items = []
    for i in range(a, b + 1):
        txt, s, e = WORDS[i]
        col = RED if i in RED_IDX else (GRN if txt in GREEN_W else YEL)
        items.append([word_sprite(txt, col), s, e, 0, 0])
    # layout: wrap to lines
    space = 22; lines = [[]]; lw = 0
    for it in items:
        w = it[0].width - 52
        if lines[-1] and lw + space + w > SUB_MAXW: lines.append([]); lw = 0
        lw += (space if lines[-1] else 0) + w; lines[-1].append(it)
    y0 = SUB_CY - (len(lines) - 1) * LINE_H / 2
    for li, ln in enumerate(lines):
        tw = sum(it[0].width - 52 for it in ln) + space * (len(ln) - 1); x = SUB_CX - tw / 2
        for it in ln:
            w = it[0].width - 52; it[3] = x + w / 2; it[4] = y0 + li * LINE_H; x += w + space
    start = items[0][1] - 0.04
    nxt = WORDS[GROUPS[gi + 1][0]][1] - 0.04 if gi + 1 < len(GROUPS) else 20.72
    end = min(nxt, items[-1][2] + 0.45)
    SUBS.append((start, end, items))
GROUP_STARTS = [g[0] for g in SUBS]

def draw_subs(fr, t):
    for start, end, items in SUBS:
        if t < start or t > end: continue
        out = clamp((t - (end - 0.1)) / 0.1)
        for spr, s, e, cx, cy in items:
            ap = s - 0.05
            if t < ap: continue
            k = (t - ap) / 0.17
            sc = lerp(0.35, 1.0, eob(k, 2.4)); al = clamp((t - ap) / 0.05)
            if s <= t <= e + 0.05: sc *= 1.0 + 0.07 * math.sin(math.pi * clamp((t - s) / max(0.12, e - s)))
            sc *= lerp(1, 0.6, eoc(out)); al *= 1 - out
            paste_c(fr, spr, cx, cy - 18 * (1 - eoc(k)), sc, al)

# ---------------- shots ----------------
class Shot:
    def __init__(self, t0, t1, key, file, srcmap, cam, mode="full", aspect=1.111, pw=1000, pcy=700):
        self.t0, self.t1, self.key, self.file, self.srcmap, self.cam = t0, t1, key, file, srcmap, cam
        self.mode, self.aspect, self.pw, self.pcy = mode, aspect, pw, pcy
        if mode == "panel":
            self.ph = int(pw / aspect); self.mask = rounded_mask(pw, self.ph, 36)
            g = Image.new("RGBA", (pw + 140, self.ph + 140), (0, 0, 0, 0))
            ImageDraw.Draw(g).rounded_rectangle((70, 70, pw + 70, self.ph + 70), 40, fill=GRN + (120,))
            g = g.filter(ImageFilter.GaussianBlur(28))
            ImageDraw.Draw(g).rounded_rectangle((66, 66, pw + 74, self.ph + 74), 42, outline=GRN + (255,), width=5)
            self.glow = g
    def rect(self, t):
        cx, cy, w = pw(self.cam, t)
        if self.mode == "full": w = min(w, SRCH * 9 / 16); h = w * 16 / 9
        else: h = w / self.aspect
        if h > SRCH: h = SRCH; w = h * (9 / 16 if self.mode == "full" else self.aspect)
        x0 = clamp(cx - w / 2, 0, SRCW - w); y0 = clamp(cy - h / 2, 0, SRCH - h)
        return x0, y0, w, h
    def render(self, t):
        src = R(self.key, self.file).get(lin(self.srcmap, t))
        x0, y0, w, h = self.rect(t)
        if self.mode == "full":
            fr = src.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
            mp = lambda p: ((p[0] - x0) * W / w, (p[1] - y0) * H / h)
        else:
            fr = blur_bg(src.resize((W // 2, H // 2), Image.BILINEAR, box=(SRCW / 2 - 304, 0, SRCW / 2 + 304, SRCH)), 0.42)
            pan = src.resize((self.pw, self.ph), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))
            px = (W - self.pw) // 2; py = int(self.pcy - self.ph / 2)
            fr.paste(self.glow, (px - 70, py - 70), self.glow); fr.paste(pan, (px, py), self.mask)
            mp = lambda p: (px + (p[0] - x0) * self.pw / w, py + (p[1] - y0) * self.ph / h)
        return fr, mp

SHOTS = [
    Shot(0.0, 10.8, "g1", "GAMEPLAY.mkv", [(0, 10.0), (10.8, 20.8)],
         [(0, (960, 560, 607)), (2.8, (960, 560, 560)), (7.8, (960, 560, 520)), (10.8, (960, 560, 520))]),
    Shot(10.8, 15.35, "web", "WEB_SITE_PREUZIMANJE.mkv",
         [(10.8, 1.75), (11.9, 3.2), (13.55, 4.12), (13.62, 4.2), (15.35, 5.3)],
         [(10.8, (960, 420, 1080)), (11.85, (960, 500, 1080)), (12.3, (960, 560, 950)), (13.5, (960, 740, 560)),
          (13.62, (960, 640, 1000)), (14.6, (960, 700, 560)), (15.35, (960, 690, 640))], mode="panel"),
    Shot(15.35, 16.9, "web", "WEB_SITE_PREUZIMANJE.mkv", [(15.35, 6.9), (16.9, 8.45)],
         [(15.35, (1560, 300, 900)), (16.2, (1680, 175, 470)), (16.9, (1680, 175, 430))], mode="panel"),
    Shot(16.9, 19.35, "la", "LAUNCHER.IGRAJ.mkv", [(16.9, 0.55), (18.86, 2.3), (19.35, 3.05)],
         [(16.9, (960, 520, 1060)), (17.6, (900, 560, 950)), (18.75, (560, 760, 470)), (18.95, (600, 740, 520)),
          (19.35, (960, 430, 760))], mode="panel"),
    Shot(19.35, DUR, "g2", "GAMEPLAY.mkv", [(19.35, 25.9), (DUR, 25.9 + DUR - 19.35)],
         [(19.35, (960, 540, 540)), (20.7, (960, 540, 600)), (DUR, (960, 540, 607))]),
]
TRANS = [10.8, 15.35, 16.9, 19.35]
CLICKS = [(13.55, 1, (960, 762)), (14.87, 1, (960, 702)), (18.86, 3, (552, 764))]

def punch(t):
    """global camera: (zoom, dx, dy)"""
    z = 1.0; dx = dy = 0.0
    def kick(t0, amp, dur): return amp * (1 - eoc((t - t0) / dur)) if t0 <= t <= t0 + dur else 0
    z += kick(0.0, 0.32, 0.45)
    for c in [4.47, 5.19, 7.11]: z += kick(c, 0.05, 0.25)
    for c, _, _ in CLICKS: z += kick(c, 0.07, 0.3)
    z += kick(20.20, 0.12, 0.45)
    shakes = [(0.0, 22, 0.35), (4.47, 14, 0.22), (5.19, 14, 0.22), (7.11, 16, 0.25), (18.86, 10, 0.2), (20.20, 26, 0.4)]
    for s0, amp, d in shakes:
        if s0 <= t <= s0 + d:
            k = (1 - (t - s0) / d) * amp
            dx += k * math.sin(t * 97.0 + s0); dy += k * math.cos(t * 83.0 + s0 * 2)
    return z, dx, dy

def apply_cam(fr, z, dx, dy):
    if abs(z - 1) < 1e-3 and abs(dx) < .5 and abs(dy) < .5: return fr
    z = max(z, 1 + 2.2 * abs(dx) / W, 1 + 2.2 * abs(dy) / H)
    w, h = W / z, H / z; x0 = clamp((W - w) / 2 - dx / z, 0, W - w); y0 = clamp((H - h) / 2 - dy / z, 0, H - h)
    return fr.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + w, y0 + h))

def zoom_blur(fr, amt):
    if amt < 0.01: return fr
    acc = np.zeros((H, W, 3), np.float32); n = 6
    for i in range(n):
        z = 1 + amt * i / (n - 1); w, h = W / z, H / z
        acc += np.asarray(fr.resize((W, H), Image.BILINEAR, box=((W - w) / 2, (H - h) / 2, (W + w) / 2, (H + h) / 2)), np.float32)
    return Image.fromarray((acc / n).astype(np.uint8))

def render_frame(t):
    shot = next(s for s in SHOTS if s.t0 <= t < s.t1) if t < DUR else SHOTS[-1]
    fr, mp = shot.render(t)
    fr = fr.copy() if fr.mode == "RGB" else fr.convert("RGB")
    # --- in-shot extras (before camera) ---
    if 2.8 <= t < 7.85: fr = darken(fr, 0.32 * eoc((t - 2.8) / 0.3) * (1 - eoc((t - 7.6) / 0.25)))
    if 7.72 <= t < 10.8:  # launcher card over blurred gameplay
        k = eoc((t - 7.72) / 0.18); fr = Image.blend(fr, blur_bg(fr, 0.55, 4), k)
        lsrc = R("lacard", "LAUNCHER.IGRAJ.mkv").get(lin([(7.72, 0.0), (10.8, 1.25)], t))
        if not hasattr(render_frame, "cm"):
            render_frame.cm = rounded_mask(980, 592, 30)
            g = Image.new("RGBA", (1120, 732), (0, 0, 0, 0))
            ImageDraw.Draw(g).rounded_rectangle((70, 70, 1050, 662), 34, fill=GRN + (140,)); g = g.filter(ImageFilter.GaussianBlur(30))
            render_frame.cg = g
        card = lsrc.resize((980, 592), Image.BICUBIC, box=(455, 215, 1465, 825)).convert("RGBA"); card.putalpha(render_frame.cm)
        comp = render_frame.cg.copy(); comp.paste(card, (70, 70), card)
        sc = lerp(0.25, 1.0, eob((t - 7.72) / 0.32, 1.6)) * (1 + 0.05 * clamp((t - 8.0) / 2.8))
        if 10.05 <= t <= 10.35: sc *= 1 + 0.035 * math.sin(math.pi * (t - 10.05) / 0.3)
        paste_c(fr, comp, W / 2, 780, sc)
        if t >= 8.0: paste_c(fr, PILL, W / 2, 380, lerp(0.2, 1, eob((t - 8.0) / 0.25, 2.2)), clamp((t - 8.0) / 0.06))
    for c0, si, pt in CLICKS:
        if SHOTS[si] is shot:
            sp = ripple_sprite(t - c0)
            if sp: x, y = mp(pt); fr.paste(sp, (int(x - 150), int(y - 150)), sp)
    if shot is SHOTS[2] and t > 15.9:  # highlight downloaded installer
        x, y = mp((1680, 150)); a = 0.5 + 0.5 * math.sin((t - 15.9) * 9)
        hl = Image.new("RGBA", (560, 180), (0, 0, 0, 0))
        ImageDraw.Draw(hl).rounded_rectangle((10, 10, 550, 170), 30, outline=GRN + (int(140 + 115 * a),), width=8)
        paste_c(fr, hl, x, y, lerp(1.3, 1.0, eob((t - 15.9) / 0.3)), clamp((t - 15.9) / 0.1))
    if t >= 20.62:  # end card background
        k = eoc((t - 20.62) / 0.25); fr = Image.blend(fr, blur_bg(fr, 0.5, 4), k)
    # --- camera + transitions ---
    z, dx, dy = punch(t); blur = 0.0; flash = 0.0
    for T in TRANS + [20.62]:
        if T - 0.12 <= t < T:
            x = (t - (T - 0.12)) / 0.12; z *= 1 + 0.35 * x ** 2; blur = 0.28 * x ** 2
        elif T <= t < T + 0.16:
            x = (t - T) / 0.16; z *= 1 + 0.35 * (1 - eoc(x)); blur = 0.28 * (1 - eoc(x)); flash = 0.55 * (1 - x)
    if t < 0.12: flash = max(flash, 0.9 * (1 - t / 0.12))
    if 20.20 <= t < 20.32: flash = max(flash, 0.6 * (1 - (t - 20.2) / 0.12))
    fr = apply_cam(fr, z, dx, dy); fr = zoom_blur(fr, blur)
    if flash > 0.01: fr = Image.blend(fr, Image.new("RGB", (W, H), (255, 255, 255)), flash)
    # --- overlays (screen space) ---
    if t < 2.95:  # hook logo
        sc = lerp(2.2, 1.0, eob(t / 0.3, 1.4)); out = clamp((t - 2.72) / 0.2)
        paste_c(fr, logo(720), W / 2, 430 + dy * 0.5, sc * lerp(1, 0.4, eoc(out)), clamp(t / 0.05) * (1 - out))
    if 4.1 <= t < 7.95:  # crossed-out alternatives
        out = clamp((t - 7.62) / 0.22)
        for i, (name, ws) in enumerate([("FiveM", 4.24), ("RAGE:MP", 4.96), ("GTA V", 6.88)]):
            if t < ws - 0.05: continue
            cy = 470 + i * 220; k = (t - ws + 0.05) / 0.2
            sc = lerp(0.3, 1, eob(k, 2.0)) * lerp(1, 0.5, eoc(out)); al = clamp(k * 3) * (1 - out)
            cx = W / 2 - 25 + (1 - eoc(k)) * (-120 if i % 2 == 0 else 120)
            paste_c(fr, CARDS[name], cx + dx * 0.6, cy + dy * 0.6, sc, al)
            xs = ws + 0.23
            if t >= xs:
                kx = (t - xs) / 0.13
                paste_c(fr, XSPR, cx + dx, cy + dy, lerp(2.4, 1.0, eoc(kx)) * lerp(1, 0.5, eoc(out)), clamp(kx * 2) * (1 - out))
    if t >= 20.16:  # final logo: slam centre, then glide up for end card
        sc = lerp(2.4, 1.0, eob((t - 20.16) / 0.28, 1.3)); y = pw([(20.62, 860.0), (20.95, 640.0)], t, eoc)
        wd = pw([(20.62, 900.0), (20.95, 860.0)], t, eoc)
        paste_c(fr, logo(wd), W / 2 + dx * 0.4, y + dy * 0.4, sc, clamp((t - 20.16) / 0.05))
    if t >= 21.0:
        k = (t - 21.0) / 0.3; press = 1.0
        if 21.88 <= t <= 22.05: press = 1 - 0.08 * math.sin(math.pi * (t - 21.88) / 0.17)
        pulse = 1 + 0.025 * math.sin((t - 21.0) * 6.0) * clamp((t - 22.1) / 0.3)
        paste_c(fr, BUTTON, W / 2, 1010, lerp(0.2, 1, eob(k, 2.0)) * press * pulse, clamp(k * 4))
    if t >= 21.3:
        k = (t - 21.3) / 0.3; paste_c(fr, TAG, W / 2, 1150 + 20 * (1 - eoc(k)), 1, clamp(k))
    if 21.3 <= t:
        sp = ripple_sprite(t - 21.9)
        if sp: fr.paste(sp, (int(W / 2 + 120 - 150), int(1030 - 150)), sp)
        p = pw([(21.3, (980.0, 1560.0)), (21.82, (W / 2 + 120, 1030.0))], t, eioc)
        csc = 0.85 if 21.88 <= t <= 22.0 else 1.0
        fr.paste(CURSOR if csc == 1 else CURSOR.resize((int(CURSOR.width * csc), int(CURSOR.height * csc))),
                 (int(p[0] - 16), int(p[1] - 16)), CURSOR if csc == 1 else CURSOR.resize((int(CURSOR.width * csc), int(CURSOR.height * csc))))
    draw_subs(fr, t)
    return fr

if __name__ == "__main__":
    if sys.argv[1] == "still":
        for tt in sys.argv[3:]:
            render_frame(float(tt)).save(f"{sys.argv[2]}/f_{float(tt):06.2f}.jpg", quality=88)
            for r in READERS.values():
                if r.p: r.p.kill()
            READERS.clear()
        sys.exit()
    a, b, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                            "-x264-params", "keyint=60", out], stdin=subprocess.PIPE)
    for n in range(a, b):
        enc.stdin.write(render_frame(n / FPS).tobytes())
        if (n - a) % 60 == 0: print(f"[{a}] {n}", flush=True)
    enc.stdin.close(); enc.wait()
    for r in READERS.values():
        if r.p: r.p.kill()

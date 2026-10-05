#!/usr/bin/env python3
"""Animated word-pop captions (ASS) timed to the facecam speech."""
import re, sys, wave
import numpy as np

S = sys.argv[1]
TEXT = open(f'{S}/script.txt', encoding='utf-8').read()
CY = 1150          # caption centre = seam between panels
KEY = {'BMRP', 'BEOGRAD', 'BALKANSKOM', '35', 'KM²', 'PREMIUM', 'RP', 'GTA',
       'ZAKONA', 'KRIMINALNOG', 'BANKE', 'BLAGO', 'PORODICU', 'HILJADA', 'ŽELIŠ',
       'PRAVI', 'PRVI', 'TERITORIJE', 'AUTA', 'MIR', 'ULICE', 'KRIMINALCE', 'SEBE'}

# --- speech activity from facecam audio
w = wave.open(f'{S}/face.wav')
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float) / 32768
hop = 160
n = len(x) // hop
e = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
voiced = e > -38
idx = np.where(voiced)[0]
start, end = idx[0] / 100, idx[-1] / 100
vt = np.cumsum(voiced) / 100.0          # voiced seconds elapsed at each 10 ms

def voiced_to_time(v):
    i = np.searchsorted(vt, v)
    return min(i, n - 1) / 100

# --- words + syllable weights
sentences = [s.strip() for s in re.split(r'(?<=[.?!])\s+', TEXT.strip()) if s.strip()]
words = []
for si, sent in enumerate(sentences):
    toks = sent.split()
    for wi, tok in enumerate(toks):
        clean = re.sub(r'[^\wšđčćžŠĐČĆŽ²+]', '', tok)
        syl = max(1, len(re.findall(r'[aeiouAEIOU]', clean)) +
                  len(re.findall(r'(?<=[^aeiouAEIOU])[rR](?=[^aeiouAEIOU]|$)', clean)))
        if any(c.isdigit() for c in clean):
            syl = 3
        words.append(dict(tok=tok, w=syl + (0.6 if wi == len(toks) - 1 else 0),
                          last=wi == len(toks) - 1, sent=si))
total_w = sum(d['w'] for d in words)
total_v = vt[-1]
acc = 0
for d in words:
    d['s'] = voiced_to_time(acc / total_w * total_v)
    acc += d['w']
    d['e'] = voiced_to_time((acc - (0.6 if d['last'] else 0)) / total_w * total_v)

# --- chunk into groups of 1-3 words (break at sentence ends / keywords)
chunks, cur = [], []
for d in words:
    cur.append(d)
    up = re.sub(r'[^\wšđčćžŠĐČĆŽ²]', '', d['tok']).upper()
    if d['last'] or len(cur) == 3 or (up in KEY and len(cur) >= 2) or \
            sum(len(c['tok']) for c in cur) > 14:
        chunks.append(cur)
        cur = []
if cur:
    chunks.append(cur)

def ts(t):
    t = max(t, 0)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f'{h}:{m:02d}:{s:05.2f}'

WHITE, YELLOW, GREEN, RED = '&H00FFFFFF&', '&H0000E6FF&', '&H0050FF3C&', '&H003C3CFF&'
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat Black,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,1,0,1,9,6,5,40,40,0,1
Style: Glow,Montserrat Black,100,&H00FFFFFF,&H00FFFFFF,&H0000E6FF,&HFF000000,0,0,0,0,100,100,1,0,1,18,0,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev = []
rot_cycle = [0, -4, 3, 0, 4, -3]
for ci, ch in enumerate(chunks):
    cs = ch[0]['s']
    ce = chunks[ci + 1][0]['s'] if ci + 1 < len(chunks) else ch[-1]['e'] + 0.4
    ce = min(ce, ch[-1]['e'] + 0.5)
    if ce - cs < 0.25:
        ce = cs + 0.25
    rot = rot_cycle[ci % len(rot_cycle)]
    keyhit = any(re.sub(r'[^\wšđčćžŠĐČĆŽ²]', '', d['tok']).upper() in KEY for d in ch)
    # one event per active word, so the active word lights up and bumps
    for wi, d in enumerate(ch):
        ws = cs if wi == 0 else d['s']
        we = ce if wi == len(ch) - 1 else ch[wi + 1]['s']
        if we <= ws:
            continue
        parts = []
        for k, o in enumerate(ch):
            word = re.sub(r'[.,]+$', '', o['tok'].upper())
            up = re.sub(r'[^\wšđčćžŠĐČĆŽ²]', '', word)
            col = GREEN if up in KEY else WHITE
            if k == wi:
                col = YELLOW if up not in KEY else GREEN
                parts.append(f'{{\\c{col}\\fscx100\\fscy100\\t(0,70,\\fscx118\\fscy118)'
                             f'\\t(70,160,\\fscx108\\fscy108)}}{word}')
            else:
                parts.append(f'{{\\c{col}\\fscx100\\fscy100}}{word}')
        body = '\\N'.join([' '.join(parts)]) if sum(len(o['tok']) for o in ch) <= 14 else \
            ' '.join(parts[:2]) + '\\N' + ' '.join(parts[2:])
        size = 116 if keyhit else 100
        if wi == 0:
            # chunk entrance: pop from small, overshoot, settle + slide up
            intro = (f'{{\\an5\\fs{size}\\frz{rot}\\move(540,{CY + 70},540,{CY},0,140)'
                     f'\\fscx30\\fscy30\\alpha&HFF&\\t(0,60,\\alpha&H00&)'
                     f'\\t(0,110,\\fscx122\\fscy122)\\t(110,200,\\fscx100\\fscy100)}}')
        else:
            intro = f'{{\\an5\\fs{size}\\frz{rot}\\pos(540,{CY})}}'
        ev.append(f'Dialogue: 1,{ts(ws)},{ts(we)},Cap,,0,0,0,,{intro}{body}')
        if keyhit and wi == 0:
            # glow pulse behind keyword chunks
            plain = ' '.join(re.sub(r'[.,]+$', '', o['tok'].upper()) for o in ch)
            ev.append(f'Dialogue: 0,{ts(ws)},{ts(min(ws + 0.45, ce))},Glow,,0,0,0,,'
                      f'{{\\an5\\fs{size}\\frz{rot}\\pos(540,{CY})\\blur12\\alpha&H40&'
                      f'\\1a&HFF&\\t(0,450,\\alpha&HFF&\\fscx135\\fscy135)}}{plain}')

open(f'{S}/captions.ass', 'w', encoding='utf-8').write(head + '\n'.join(ev) + '\n')
print(len(chunks), 'chunks; speech', start, '->', end)
for ch in chunks[:8]:
    print(round(ch[0]['s'], 2), ' '.join(d['tok'] for d in ch))

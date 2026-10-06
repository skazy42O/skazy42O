#!/usr/bin/env python3
"""Word-by-word pop-up captions (ASS) from whisper word timestamps + emoji plan."""
import json, re, sys

S = sys.argv[1]
CY = int(sys.argv[3]) if len(sys.argv) > 3 else 1150   # caption centre
FONT = 'Poppins ExtraBold'

WORDS = sys.argv[2] if len(sys.argv) > 2 else f'{S}/words.json'
raw = json.load(open(WORDS, encoding='utf-8'))
FIX = {'ovu.': 'ovo!', 'serverima.': 'serverima?', 'zakona,': 'zakona?',
       'strana.': 'strana?', 'strana,': 'strana?', 'haos,': 'haos?', 'roleplay,': 'roleplay?', 'Stani,': 'Stani!',
       'odmah.': 'odmah!'}
words = []
for r in raw:
    tok = r['text'].strip()
    if not tok:
        continue
    words.append(dict(tok=FIX.get(tok, tok), s=r['t0'], e=r['t1']))
# whisper puts each word's start at the previous word's end; nudge earlier so
# the pop lands with the syllable, never before the previous word
for i, w in enumerate(words):
    w['s'] = max(w['s'] - 0.06, words[i - 1]['s'] + 0.05 if i else 0)

def norm(tok):
    return re.sub(r'[^\wšđčćžŠĐČĆŽ]', '', tok).lower()

WHITE, YELLOW, GREEN, RED, BLUE = '&H00FFFFFF&', '&H0000E6FF&', '&H0050FF3C&', '&H004040FF&', '&H00FFB43C&'
# keyword -> (colour, emoji, effect)
KW = {
    'dosadnim': (BLUE, '1f634', None), 'gta': (GREEN, None, None),
    'stani': (RED, '270b', 'shake'), 'bmrp': (GREEN, '1f525', 'glow'),
    'balkanskom': (YELLOW, None, 'wiggle'), '35': (GREEN, '1f5fa-fe0f', 'count'),
    'kvadratnih': (GREEN, None, None), 'kilometara': (GREEN, None, None),
    'los': (RED, None, 'strike'), 'santos': (RED, '274c', 'strike'),
    'beograd': (RED, '1f1f7-1f1f8', 'glow'), 'zakona': (BLUE, '1f46e', None),
    'kriminalce': (RED, '1f6a8', 'shake'), 'auta': (YELLOW, '1f697', None),
    'banke': (GREEN, '1f4b0', 'wiggle'), 'teritoriju': (RED, '2694-fe0f', None),
    'ime': (YELLOW, '1f451', 'glow'), 'haos': (RED, '1f4a5', 'shake'),
    'pecaj': (BLUE, '1f3a3', None), 'blago': (YELLOW, '1f48e', 'wiggle'),
    'premium': (YELLOW, '1f3ce-fe0f', 'glow'), 'odjeću': (GREEN, '1f455', None),
    'hiljada': (GREEN, None, 'wiggle'), 'ekipu': (YELLOW, '1f91d', None),
    'porodicu': (RED, '2764-fe0f', 'glow'), 'pravi': (GREEN, None, None),
    'gledati': (YELLOW, '1f440', None), 'odmah': (GREEN, '1f680', 'shake'),
    'roleplay': (GREEN, '1f3ae', None),
}
emoji_used = set()

# --- chunking: hand-picked phrase groups (word counts), matched in order
GROUPS = """Još uvijek igraš | na istim dosadnim | GTA roleplay serverima | Stani | pogledaj ovo |
Ovo je BMRP | prvi roleplay server | sa pravom balkanskom | atmosferom | Mapa od 35 |
kvadratnih kilometara | i nije | Los Santos | Ovo je Beograd | Ovdje sam biraš | ko ćeš biti |
Hoćeš na stranu | zakona | drži ulice | pod kontrolom | i lovi | kriminalce | Ili ti je |
draža druga strana | Kradi auta | pljačkaj banke | ratuj za teritoriju | i biznis |
dok ti cijeli grad | ne zapamti ime | Nisi za haos | pecaj | traži blago | živi kako ti hoćeš |
Vozi premium | automobile | iz stvarnog svijeta | Biraj odjeću | između hiljada komada |
Nađi ekipu | možda i porodicu | Hoćeš pravi roleplay | onda prestani gledati | Uđi na BMRP | odmah"""
sizes = [len(g.split()) for g in GROUPS.replace('\n', ' ').split('|')]
assert sum(sizes) == len(words), (sum(sizes), len(words))
chunks, i = [], 0
for n in sizes:
    chunks.append(words[i:i + n])
    i += n

def ts(t):
    t = max(t, 0)
    return f'{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}'

def disp(tok):
    t = tok.upper()
    t = re.sub(r'[.,]+$', '', t)
    return t.replace('KILOMETARA', 'KM²') if False else t

head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT},104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,8,5,5,30,30,0,1
Style: Glow,{FONT},96,&HFF000000,&HFF000000,&H0000E6FF,&HFF000000,0,0,0,0,100,100,0,0,1,16,0,5,30,30,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

POP = ('\\fscx0\\fscy0\\t(0,90,\\fscx128\\fscy128)\\t(90,160,\\fscx94\\fscy94)'
       '\\t(160,220,\\fscx{s}\\fscy{s})')

def word_tag(o, state, local_ms, is_key):
    """state: past / active / future"""
    col, emo, fx = KW.get(norm(o['tok']), (None, None, None))
    txt = disp(o['tok'])
    if state == 'future':
        return f'{{\\alpha&HFF&\\fscx100\\fscy100\\s0}}{txt}'
    base_col = col or WHITE
    strike = '\\s1' if fx == 'strike' else '\\s0'
    if state == 'past':
        return f'{{\\alpha&H00&\\c{base_col}\\fscx100\\fscy100{strike}\\frz0}}{txt}'
    act_col = col or YELLOW
    s = 112 if col else 106
    tags = f'\\alpha&H00&\\c{act_col}{strike}' + POP.format(s=s)
    if fx == 'shake':
        tags += ''.join(f'\\t({220 + k * 45},{265 + k * 45},\\frz{(-6, 6)[k % 2]})' for k in range(6)) + \
            '\\t(490,530,\\frz0)'
    elif fx == 'wiggle':
        tags += '\\t(220,380,\\frz-5)\\t(380,540,\\frz4)\\t(540,700,\\frz0)'
    return f'{{{tags}}}{txt}'

ev = []
emoji_plan = []
rot_cycle = [0, -3, 2, 0, 3, -2]
for ci, ch in enumerate(chunks):
    cs = ch[0]['s']
    nxt = chunks[ci + 1][0]['s'] if ci + 1 < len(chunks) else ch[-1]['e'] + 0.6
    ce = min(nxt, ch[-1]['e'] + 0.6)
    rot = rot_cycle[ci % len(rot_cycle)]
    big = any(norm(o['tok']) in KW for o in ch)
    fs = 116 if big else 104
    nchar = sum(len(o['tok']) for o in ch)
    for wi, w in enumerate(ch):
        ws = cs if wi == 0 else w['s']
        we = ce if wi == len(ch) - 1 else ch[wi + 1]['s']
        if we - ws < 0.02:
            continue
        key = norm(w['tok'])
        parts = []
        for k, o in enumerate(ch):
            state = 'past' if k < wi else ('active' if k == wi else 'future')
            parts.append(word_tag(o, state, 0, key in KW))
        if nchar > 14 and len(parts) == 3:
            body = parts[0] + ' ' + parts[1] + '\\N' + parts[2]
        else:
            body = ' '.join(parts)
        pre = f'{{\\an5\\fs{fs}\\frz{rot}\\pos(540,{CY})}}'
        col, emo, fx = KW.get(key, (None, None, None))
        if fx == 'count':
            # number counts up 0 -> 35 while the word is spoken
            steps = 9
            dur = min(we - ws, 0.45)
            for k in range(steps):
                t0 = ws + dur * k / steps
                t1 = ws + dur * (k + 1) / steps if k < steps - 1 else we
                n = round(35 * (k + 1) / steps)
                b = body.replace('}35', f'}}{n}', 1)
                ev.append(f'Dialogue: 2,{ts(t0)},{ts(t1)},Cap,,0,0,0,,{pre}{b}')
        else:
            ev.append(f'Dialogue: 2,{ts(ws)},{ts(we)},Cap,,0,0,0,,{pre}{body}')
        if fx == 'glow':
            plain = ' '.join(f'{{\\alpha&HFF&}}{disp(o["tok"])}' if o is not w else
                             f'{{\\alpha&H30&}}{disp(o["tok"])}' for o in ch)
            ev.append(f'Dialogue: 1,{ts(ws)},{ts(min(ws + 0.5, we + 0.3))},Glow,,0,0,0,,'
                      f'{{\\an5\\fs{fs}\\frz{rot}\\pos(540,{CY})\\blur10\\3c{col}'
                      f'\\t(0,500,\\3a&HFF&\\fscx130\\fscy130)}}{plain}')
        if emo and emo not in emoji_used:
            emoji_used.add(emo)
            emoji_plan.append(dict(t=ws, end=max(ce, ws + 0.9), code=emo,
                                   x=540 + (-1) ** len(emoji_plan) * 0, y=CY - 175))

open(f'{S}/captions_out.ass', 'w', encoding='utf-8').write(head + '\n'.join(ev) + '\n')
json.dump(emoji_plan, open(f'{S}/emoji_out.json', 'w'), indent=0)
print(len(chunks), 'chunks,', len(emoji_plan), 'emojis')
for ch in chunks:
    print(f"{ch[0]['s']:6.2f}", ' '.join(disp(o['tok']) for o in ch))

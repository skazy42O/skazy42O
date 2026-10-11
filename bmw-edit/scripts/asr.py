#!/usr/bin/env python3
"""Phrase-level lyric transcription of a vocal stem. usage: asr.py model_dir vocals.wav out.json [lang]"""
import sys, json, numpy as np, soundfile as sf, sherpa_onnx
mdir, src, dst = sys.argv[1:4]; lang = sys.argv[4] if len(sys.argv) > 4 else 'hr'
x, sr = sf.read(src, dtype='float32')
if x.ndim > 1: x = x.mean(1)
# resample to 16k (simple polyphase via numpy interp is fine for ASR)
n16 = int(len(x)*16000/sr); x16 = np.interp(np.linspace(0, len(x)-1, n16), np.arange(len(x)), x).astype(np.float32)
hop = 160; fr = len(x16)//hop
rms = np.sqrt((x16[:fr*hop].reshape(fr, hop)**2).mean(1)); db = 20*np.log10(rms + 1e-9)
thr = max(np.percentile(db, 60) - 6, db.max() - 38)
act = db > thr
# close small gaps, drop tiny blips
def runs(a):
    r = []; s = None
    for i, v in enumerate(a):
        if v and s is None: s = i
        if not v and s is not None: r.append([s, i]); s = None
    if s is not None: r.append([s, len(a)])
    return r
segs = runs(act); merged = []
for s, e in segs:
    if merged and s - merged[-1][1] < 35: merged[-1][1] = e
    else: merged.append([s, e])
merged = [m for m in merged if m[1] - m[0] > 25]
# split overly long phrases at the quietest point
final = []
for s, e in merged:
    while e - s > 900:
        k = s + 400 + int(np.argmin(db[s+400:min(e-200, s+900)])); final.append([s, k]); s = k
    final.append([s, e])
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f'{mdir}/turbo-encoder.int8.onnx', decoder=f'{mdir}/turbo-decoder.int8.onnx',
    tokens=f'{mdir}/turbo-tokens.txt', language=lang, task='transcribe', num_threads=4, tail_paddings=1000)
out = []
for s, e in final:
    a, b = max(0, s*hop - 2400), min(len(x16), e*hop + 2400)
    st = rec.create_stream(); st.accept_waveform(16000, x16[a:b]); rec.decode_stream(st)
    txt = st.result.text.strip()
    out.append({'t0': round(s*hop/16000, 2), 't1': round(e*hop/16000, 2), 'text': txt})
    print(f"{s*hop/16000:7.2f}-{e*hop/16000:7.2f}  {txt}", flush=True)
json.dump(out, open(dst, 'w'), ensure_ascii=False, indent=1)

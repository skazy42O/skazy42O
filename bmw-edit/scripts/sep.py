#!/usr/bin/env python3
"""Vocal stem extraction with UVR MDX-Net Voc_FT (ONNX). usage: sep.py model.onnx in.wav(44.1k stereo) out_vocals.wav"""
import sys, numpy as np, torch, onnxruntime as ort, soundfile as sf
model, src, dst = sys.argv[1:4]
sess = ort.InferenceSession(model, providers=['CPUExecutionProvider'])
inp = sess.get_inputs()[0]; print('input', inp.name, inp.shape)
n_fft, hop, dim_t = 6144, 1024, 256
dim_f = inp.shape[2] if isinstance(inp.shape[2], int) else 3072
n_bins = n_fft//2 + 1
chunk = hop*(dim_t - 1); trim = n_fft//2; gen = chunk - 2*trim
win = torch.hann_window(n_fft, periodic=True)

def stft(x):  # x [B,2,L]
    B = x.shape[0]; x = x.reshape(-1, chunk)
    s = torch.view_as_real(torch.stft(x, n_fft, hop, window=win, center=True, return_complex=True))
    s = s.permute(0, 3, 1, 2).reshape(B, 4, n_bins, dim_t)
    return s[:, :, :dim_f]
def istft(s):
    B = s.shape[0]
    s = torch.cat([s, torch.zeros(B, 4, n_bins - dim_f, dim_t)], 2)
    s = s.reshape(B*2, 2, n_bins, dim_t).permute(0, 2, 3, 1).contiguous()
    x = torch.istft(torch.view_as_complex(s), n_fft, hop, window=win, center=True)
    return x.reshape(B, 2, -1)

mix, sr = sf.read(src, dtype='float32'); assert sr == 44100, sr
mix = mix.T  # [2, N]
N = mix.shape[1]; pad = gen - N % gen
mp = np.concatenate([np.zeros((2, trim), np.float32), mix, np.zeros((2, pad), np.float32), np.zeros((2, trim), np.float32)], 1)
outs = []
for i in range(0, N + pad, gen):
    w = torch.from_numpy(mp[:, i:i+chunk][None].copy())
    spec = stft(w).numpy()
    o = sess.run(None, {inp.name: spec})[0]
    outs.append(istft(torch.from_numpy(o))[0, :, trim:-trim].numpy())
    print(f'{i/(N+pad)*100:.0f}%', flush=True)
voc = np.concatenate(outs, 1)[:, :N]*1.021
sf.write(dst, voc.T, sr)
print('done')

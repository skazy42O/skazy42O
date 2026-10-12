#!/bin/bash
# master mix_raw.wav -> mix.wav : glue compression + brickwall limiter (~ -11 LUFS, -1 dBTP)
set -e; cd "$(dirname "$0")/../work"
ffmpeg -v error -y -i mix_raw.wav -af "volume=-6dB,acompressor=threshold=-18dB:ratio=2.5:attack=10:release=120,volume=9dB,alimiter=limit=0.80:attack=0.5:release=60:level=disabled,aresample=48000" -c:a pcm_s16le mix.wav
ffmpeg -hide_banner -i mix.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"

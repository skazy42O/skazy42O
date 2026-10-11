#!/bin/bash
# master mix_raw.wav -> mix.wav (glue comp + limiter, 2-pass loudnorm to -11 LUFS / -1 dBTP)
set -e; cd "$(dirname "$0")/../work"
PRE="volume=-6dB,acompressor=threshold=-16dB:ratio=2.5:attack=8:release=120:makeup=1,alimiter=limit=0.7:attack=1:release=60:level=disabled"
J=$(ffmpeg -hide_banner -i mix_raw.wav -af "$PRE,loudnorm=I=-11:TP=-1:LRA=9:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i mix_raw.wav -af "$PRE,loudnorm=I=-11:TP=-1:LRA=9:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" -c:a pcm_s16le mix.wav
ffmpeg -hide_banner -i mix.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2

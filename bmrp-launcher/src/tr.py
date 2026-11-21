import json,sys
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
segs,info=m.transcribe(__import__("numpy").fromfile(sys.argv[1],dtype="float32"),language="sr",word_timestamps=True,beam_size=5,vad_filter=False,initial_prompt="BMRP launcher, preuzmi, igraj, Balkan Mafia Roleplay.")
out=[]
for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
    for w in s.words: out.append(dict(w=w.word.strip(),s=w.start,e=w.end,p=w.probability))
json.dump(out,open(sys.argv[2],"w"),ensure_ascii=False,indent=0)

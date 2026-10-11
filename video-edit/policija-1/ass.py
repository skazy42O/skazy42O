import sys; sys.path.insert(0, sys.argv[1]); from plan import SUBS, STICK
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h}:{m:02d}:{s:05.2f}"
COL={"R":"&H002A2AFF&","G":"&H003CFF3C&","W":"&H00FFFFFF&"}
YEL="&H0000E1FF&"  # MrBeast zuta
hdr="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Luckiest Guy,118,&H0000E1FF,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,10,6,5,40,40,0,1
Style: Hook,Luckiest Guy,104,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,11,0,5,40,40,0,1
Style: Box,Luckiest Guy,86,&H00FFFFFF,&H000000FF,&H001E1EE6,&H00000000,0,0,0,0,100,100,2,0,3,22,0,5,40,40,0,1
Style: BoxG,Luckiest Guy,80,&H00000000,&H000000FF,&H0000E1FF,&H00000000,0,0,0,0,100,100,2,0,3,20,0,5,40,40,0,1
Style: Loot,Luckiest Guy,96,&H003CFF3C,&H000000FF,&H00000000,&H96000000,0,0,0,0,100,100,2,0,1,9,5,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
POP=r"\fscx45\fscy45\t(0,80,\fscx122\fscy122)\t(80,150,\fscx100\fscy100)"
for i,(a,b,txt,hl) in enumerate(SUBS):
    words=txt.split(" "); parts=[]
    for k,w in enumerate(words):
        parts.append(("{\\c"+COL[hl[k]]+"}"+w+"{\\c"+YEL+"}") if k in hl else w)
    rot = (-3 if i%2 else 3)
    tag="{\\an5\\pos(540,1290)\\frz%d\\t(0,120,\\frz0)%s}"%(rot,POP)
    ev.append(f"Dialogue: 5,{ts(a)},{ts(b)},Cap,,0,0,0,,{tag}"+" ".join(parts))
for a,b,txt,st in STICK:
    d=int((b-a)*1000)
    if st=="hook":
        tag=r"{\an5\pos(540,430)\fscx20\fscy20\t(0,140,\fscx115\fscy115)\t(140,240,\fscx100\fscy100)\t(%d,%d,\fscx0\fscy0)\c&H0000E1FF&}"%(d-180,d)
        ev.append(f"Dialogue: 8,{ts(a)},{ts(b)},Hook,,0,0,0,,{tag}{txt}")
    elif st in("warn","warn_big"):
        y=560 if st=="warn" else 640; fs=86 if st=="warn" else 120
        wob="" if st=="warn" else r"\t(300,450,\frz-4)\t(450,600,\frz4)\t(600,750,\frz-4)\t(750,900,\frz0)"
        tag=r"{\an5\pos(540,%d)\fs%d\frz-6\fscx10\fscy10\t(0,110,\fscx118\fscy118)\t(110,200,\fscx100\fscy100)%s\t(%d,%d,\alpha&HFF&)}"%(y,fs,wob,d-150,d)
        ev.append(f"Dialogue: 7,{ts(a)},{ts(b)},Box,,0,0,0,,{tag}{txt}")
    elif st=="info":
        tag=r"{\an5\pos(540,520)\frz4\fscx10\fscy10\t(0,110,\fscx115\fscy115)\t(110,200,\fscx100\fscy100)\t(%d,%d,\alpha&HFF&)}"%(d-150,d)
        ev.append(f"Dialogue: 7,{ts(a)},{ts(b)},BoxG,,0,0,0,,{tag}{txt}")
    elif st=="loot":
        tag=r"{\an5\pos(540,560)\fscx10\fscy10\t(0,120,\fscx120\fscy120)\t(120,220,\fscx100\fscy100)\t(%d,%d,\alpha&HFF&)}"%(d-150,d)
        ev.append(f"Dialogue: 7,{ts(a)},{ts(b)},Loot,,0,0,0,,{tag}{txt}")
    elif st=="loot_s":  # +PREDMET leti nagore
        x={"+ PUŠKE":300,"+ KALAŠ":780,"+ PANCIR":540}[txt]
        tag=r"{\an5\move(%d,900,%d,700)\fs110\fscx20\fscy20\t(0,100,\fscx120\fscy120)\t(100,180,\fscx100\fscy100)\t(%d,%d,\alpha&HFF&)}"%(x,x,d-250,d)
        ev.append(f"Dialogue: 7,{ts(a)},{ts(b)},Loot,,0,0,0,,{tag}{txt}")
    elif st=="end":
        tag=r"{\an5\pos(540,900)\fs96\fscx20\fscy20\t(0,140,\fscx112\fscy112)\t(140,240,\fscx100\fscy100)\c&H0000E1FF&}"
        ev.append(f"Dialogue: 9,{ts(a)},{ts(b)},Hook,,0,0,0,,{tag}{txt}")
open(sys.argv[2],"w",encoding="utf-8").write(hdr+"\n".join(ev)+"\n"); print(len(ev),"events")

import sys, random; sys.path.insert(0, sys.argv[1]); from plan import SUBS, GREEN, RED, PROMO, PROMO_TEXT
from PIL import ImageFont
FONT=ImageFont.truetype(sys.argv[3]+"/LuckiestGuy.ttf",100)
INTER=ImageFont.truetype(sys.argv[3]+"/Inter-Black.otf",100)
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
# TikTok sigurna zona (1080x1920): gore 150px, dole 380px, desno 150px (ikonice), levo 60px
SAFE_L,SAFE_R,SAFE_T,SAFE_B=70,880,180,1500
CX=(SAFE_L+SAFE_R)//2; CAP_Y=1180; MAXW=SAFE_R-SAFE_L-40
YEL="&H0000E5FF&"; WHT="&H00FFFFFF&"; GRN="&H0036FF5A&"; REDC="&H003A3AFF&"
hdr=f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Luckiest Guy,100,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,9,5,5,0,0,0,1
Style: Promo,Inter Black,36,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,5,0,0,0,1
Style: Box,Inter Black,10,&H50000000,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
def color(w,active):
    if not active: return WHT
    if w in GREEN: return GRN
    if w in RED: return REDC
    return YEL
for a,b,txt in SUBS:
    words=txt.split()
    groups=[]; cur=[]
    for w in words:
        if cur and (len(cur)>=3 or len(" ".join(cur+[w]))>15): groups.append(cur); cur=[]
        cur.append(w)
    groups.append(cur)
    wt=[len(w)+2 for w in words]; tot=sum(wt); t=a; times=[]
    for x in wt: times.append((t,t+(b-a)*x/tot)); t+=(b-a)*x/tot
    k=0
    for gi,g in enumerate(groups):
        line=" ".join(g); wpx=FONT.getlength(line)*1.04+30
        fs=min(108,int(100*MAXW/wpx))
        for wi,w in enumerate(g):
            s,e=times[k+wi]
            if wi==len(g)-1: e=times[k+wi][1]
            parts=[]
            for j,w2 in enumerate(g):
                if j==wi: parts.append("{\\c"+color(w2,True)+"\\fscx112\\fscy112}"+w2+"{\\fscx100\\fscy100\\c"+WHT+"}")
                else: parts.append(w2)
            pop=r"\fscx50\fscy50\t(0,70,\fscx115\fscy115)\t(70,140,\fscx100\fscy100)" if wi==0 else ""
            ev.append(f"Dialogue: 5,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\an5\\pos({CX},{CAP_Y})\\fs{fs}{pop}}}"+" ".join(parts))
        k+=len(g)
# promo tekst na nasumicnim mestima u sigurnoj zoni
random.seed(2026)
L1,L2,L3="Registrujte se i unesite","PROMOKOD: BMRP2026","za besplatna 2 case i bonus novac."
for a,b in PROMO:
    w1=max(INTER.getlength(L1)*0.36,INTER.getlength(L3)*0.36,INTER.getlength(L2)*0.54)+60; h=200
    x=random.randint(int(SAFE_L+w1/2),int(SAFE_R-w1/2)); y=random.choice([random.randint(SAFE_T+80,560),random.randint(700,960)])
    rot=random.choice([-3,-2,2,3]); d=int((b-a)*1000)
    fade=r"\fad(180,220)"
    x0,y0=int(x-w1/2),int(y-h/2)
    ev.append(f"Dialogue: 6,{ts(a)},{ts(b)},Box,,0,0,0,,{{\\an7\\pos({x0},{y0})\\frz{rot}\\org({x},{y}){fade}\\1c&H000000&\\1a&H48&\\bord0\\shad0\\p1}}m 0 0 l {int(w1)} 0 {int(w1)} {h} 0 {h}{{\\p0}}")
    ev.append(f"Dialogue: 6,{ts(a)},{ts(b)},Box,,0,0,0,,{{\\an7\\pos({x0},{y0})\\frz{rot}\\org({x},{y}){fade}\\1c&H0000E5FF&\\1a&H00&\\bord0\\shad0\\p1}}m 0 0 l 12 0 12 {h} 0 {h}{{\\p0}}")
    txt=(f"{{\\an5\\pos({x+6},{y})\\frz{rot}\\org({x},{y}){fade}\\fscx70\\fscy70\\t(0,160,\\fscx100\\fscy100)}}{L1}\\N"
         f"{{\\fs54\\c&H0000E5FF&}}{L2}{{\\fs36\\c&H00FFFFFF&}}\\N{L3}")
    ev.append(f"Dialogue: 7,{ts(a)},{ts(b)},Promo,,0,0,0,,{txt}")
open(sys.argv[2],"w",encoding="utf-8").write(hdr+"\n".join(ev)+"\n"); print(len(ev),"events")

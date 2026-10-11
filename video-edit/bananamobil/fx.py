import sys, subprocess, numpy as np, cv2, math
sys.path.insert(0, sys.argv[1])
from plan import ZOOM, SHAKE, FLASH, RGB, TRANS, FADE_OUT, SPEED, FREEZE, SLOWMO, OUT_DUR, out2src, src2out
src, ass, fontdir, audio, out = sys.argv[2:7]
o0 = float(sys.argv[7]) if len(sys.argv)>7 else 0.0; odur = float(sys.argv[8]) if len(sys.argv)>8 else OUT_DUR
Wd,Ht,FPS=1080,1920,60
def ease_out(x): return 1-(1-x)**3
def ease_io(x): return 3*x*x-2*x*x*x
def zoom_at(t):
    z=1.0
    for kt,kz,kd in ZOOM:
        if t<kt: break
        if kd<=0 or t>=kt+kd: z=kz
        else:
            x=(t-kt)/kd; z=z+(kz-z)*(ease_io(x) if kd>1.0 else ease_out(x))
    return z
def shake_at(t):
    dx=dy=rot=0.0
    for a,b,amp,f in SHAKE:
        if a<=t<b:
            k=1-(t-a)/(b-a)
            dx+=amp*k*(math.sin(2*math.pi*f*t)+0.6*math.sin(2*math.pi*f*1.73*t+1.3))
            dy+=amp*k*(math.sin(2*math.pi*f*0.91*t+2.1)+0.6*math.sin(2*math.pi*f*1.37*t+0.4))
            rot+=0.04*amp*k*math.sin(2*math.pi*f*0.6*t+0.7)
    return dx,dy,rot
PRE,POST=0.14,0.20
def trans_at(t):
    for c,k in TRANS:
        if c-PRE<=t<c+POST:
            p=(t-c)/PRE if t<c else (t-c)/POST
            return k,p,((1+p)**2 if p<0 else (1-p)**2)
    return None
yy,xx=np.mgrid[0:Ht,0:Wd].astype(np.float32)
r=np.sqrt(((xx-Wd/2)/(Wd/2))**2+((yy-Ht/2)/(Ht/2))**2)
VIG=np.clip(1-0.28*np.clip(r-0.6,0,None)**1.6,0,1)[...,None].astype(np.float32)
VIGF=np.clip(1-0.6*np.clip(r-0.35,0,None)**1.4,0,1)[...,None].astype(np.float32)
LUT=np.clip(255*(0.5+0.5*np.tanh((np.arange(256)/255-0.5)*2.3)/np.tanh(1.15)),0,255).astype(np.uint8)
# anime linije brzine: 3 varijante maski
rng=np.random.default_rng(4); SPM=[]
for v in range(3):
    m=np.zeros((Ht,Wd),np.float32); R=math.hypot(Wd,Ht)
    for _ in range(90):
        ang=rng.uniform(0,2*math.pi); r0=rng.uniform(0.52,0.75)*R/2
        p0=(int(Wd/2+math.cos(ang)*r0),int(Ht/2+math.sin(ang)*r0)); p1=(int(Wd/2+math.cos(ang)*R),int(Ht/2+math.sin(ang)*R))
        cv2.line(m,p0,p1,float(rng.uniform(0.5,1.0)),int(rng.integers(2,6)),cv2.LINE_AA)
    SPM.append(cv2.GaussianBlur(m,(0,0),1.2)[...,None])
def speed_at(t):
    for a,b in SPEED:
        if a<=t<b: return min(1,(t-a)/0.2,(b-t)/0.2)
    return 0
def zoom_blur(img,amount):
    acc=img.astype(np.float32); n=4
    for i in range(1,n):
        M=cv2.getRotationMatrix2D((Wd/2,Ht/2),0,1+amount*i/n); acc+=cv2.warpAffine(img,M,(Wd,Ht),borderMode=cv2.BORDER_REFLECT)
    return (acc/n).astype(np.uint8)
dec=subprocess.Popen(["ffmpeg","-v","error","-i",src,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
fsz=Wd*Ht*3; buf={}; nxt=0
def frame(i):
    global nxt
    while nxt<=i:
        b=dec.stdout.read(fsz)
        if len(b)<fsz: return buf[max(buf)] if buf else None
        buf[nxt]=np.frombuffer(b,np.uint8).reshape(Ht,Wd,3); nxt+=1
        for k in [k for k in buf if k<nxt-3]: del buf[k]
    return buf.get(i, buf[max(buf)])
assf=ass.replace(":","\\:"); fd=fontdir.replace(":","\\:")
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{Wd}x{Ht}","-r",str(FPS),"-i","-",
    "-ss",str(o0),"-i",audio,"-t",str(odur),"-map","0:v","-map","1:a",
    "-vf",f"setpts=PTS+{o0}/TB,ass={assf}:fontsdir={fd},setpts=PTS-STARTPTS",
    "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-profile:v","high","-r",str(FPS),
    "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out],stdin=subprocess.PIPE)
grng=np.random.default_rng(1)
n0=int(round(o0*FPS)); n1=min(int(OUT_DUR*FPS), n0+int(round(odur*FPS)))
for n in range(n0,n1):
    o=n/FPS; t,frz=out2src(o)
    fi=t*FPS; i0=int(fi); fr=fi-i0
    a0=frame(i0)
    if a0 is None: break
    slow=any(a<=t<b for a,b,s in SLOWMO)
    if slow and fr>0.05:
        a1=frame(i0+1); img=cv2.addWeighted(a0,1-fr,a1,fr,0)
    else: img=a0
    z=zoom_at(t); dx,dy,rot=shake_at(t) if not frz else (0,0,0)
    if frz:
        fs0=[src2out(ft) for ft,d in FREEZE if ft==t][0]; pr=(o-fs0)/[d for ft,d in FREEZE if ft==t][0]
        z=1.0+0.18*ease_out(min(1,pr*1.5)); rot=-2.5*ease_out(min(1,pr*1.5))
    tr=None if frz else trans_at(t); blur=None
    if tr:
        k,p,s=tr
        if k=="zoom": z*=1+0.35*s; blur=("zoom",0.10*s)
        elif k=="whip": dx+=Wd*0.35*s*(1 if p<0 else -1); blur=("h",int(90*s)|1)
        elif k=="spin": rot+=(18*s if p<0 else -18*s); z*=1+0.25*s; blur=("zoom",0.07*s)
        elif k=="glitch": blur=("glitch",s)
    if (dx or dy) and not (tr and tr[0]=="whip"): z=max(z,1+(abs(dx)+abs(dy))/Wd*2.2)
    if abs(z-1)>1e-4 or dx or dy or rot:
        M=cv2.getRotationMatrix2D((Wd/2,Ht/2),rot,z); M[0,2]+=dx; M[1,2]+=dy
        img=cv2.warpAffine(img,M,(Wd,Ht),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    if blur:
        kind,a=blur
        if kind=="zoom" and a>0.005: img=zoom_blur(img,a)
        elif kind=="h" and a>3: img=cv2.blur(img,(a,1))
        elif kind=="glitch" and a>0.05:
            img=img.copy()
            for _ in range(int(10*a)+2):
                y0=int(grng.integers(0,Ht-80)); hh=int(grng.integers(20,160)); off=int(grng.integers(-80,80)*a)
                img[y0:y0+hh]=np.roll(img[y0:y0+hh],off,1)
            p_=int(18*a)+1; b,g,rr=cv2.split(img); img=cv2.merge([np.roll(b,-p_,1),g,np.roll(rr,p_,1)])
    for a,d,px in RGB:
        if a<=t<a+d and not frz:
            p_=int(px*(1-(t-a)/d))+1; b,g,rr=cv2.split(img); img=cv2.merge([np.roll(b,-p_,1),g,np.roll(rr,p_,1)]); break
    img=cv2.LUT(img,LUT)
    f=img.astype(np.float32); gray=f.mean(2,keepdims=True)
    sat=0.25 if frz else (0.85 if slow else 1.12)
    f=gray+(f-gray)*sat
    f*=VIGF if (frz or slow) else VIG
    sp=speed_at(t)
    if sp>0:
        m=SPM[(n//3)%3]*(0.6*sp); f=f*(1-m)+255*m
    if tr: f+=255*0.18*tr[2]
    for a,d,c,al in FLASH:
        if a<=t<a+d and not frz:
            k_=al*(1-(t-a)/d)**1.5; f=f*(1-k_)+np.array(c,np.float32)*k_
    if frz and o-[src2out(ft) for ft,d in FREEZE if ft==t][0]<0.08: f=f*0.4+255*0.6
    if FADE_OUT[0]<=t: k_=min(1,(t-FADE_OUT[0])/(FADE_OUT[1]-FADE_OUT[0])); f*=(1-0.9*k_)
    enc.stdin.write(np.clip(f,0,255).astype(np.uint8).tobytes())
    if n%1200==0: print(f"{o:.1f}s",flush=True)
enc.stdin.close(); enc.wait(); dec.kill(); print("done")

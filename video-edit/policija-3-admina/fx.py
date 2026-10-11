import sys, subprocess, numpy as np, cv2, math
sys.path.insert(0, sys.argv[1]); from plan import ZOOM, SHAKE, FLASH, RGB, TRANS, FADE_OUT
src, ass, fontdir, audio, out = sys.argv[2:7]
t0 = float(sys.argv[7]) if len(sys.argv)>7 else 0; dur = float(sys.argv[8]) if len(sys.argv)>8 else None
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
            # p: -1..0 pre reza, 0..1 posle; jacina vrh na rezu
            p=(t-c)/PRE if t<c else (t-c)/POST
            s=(1+p)**2 if p<0 else (1-p)**2
            return k,p,s
    return None
yy,xx=np.mgrid[0:Ht,0:Wd].astype(np.float32)
r=np.sqrt(((xx-Wd/2)/(Wd/2))**2+((yy-Ht/2)/(Ht/2))**2)
VIG=np.clip(1-0.28*np.clip(r-0.6,0,None)**1.6,0,1)[...,None].astype(np.float32)
LUT=np.clip(255*(0.5+0.5*np.tanh((np.arange(256)/255-0.5)*2.3)/np.tanh(1.15)),0,255).astype(np.uint8)  # S-kriva kontrast
def zoom_blur(img,amount):
    acc=img.astype(np.float32); n=4
    for i in range(1,n):
        z=1+amount*i/n; M=cv2.getRotationMatrix2D((Wd/2,Ht/2),0,z)
        acc+=cv2.warpAffine(img,M,(Wd,Ht),borderMode=cv2.BORDER_REFLECT)
    return (acc/n).astype(np.uint8)
ss=["-ss",str(t0)] if t0 else []; tt=["-t",str(dur)] if dur else []
dec=subprocess.Popen(["ffmpeg","-v","error",*ss,"-i",src,*tt,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
assf=ass.replace(":","\\:"); fd=fontdir.replace(":","\\:")
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{Wd}x{Ht}","-r",str(FPS),"-i","-",
    *ss,"-i",audio,*tt,"-map","0:v","-map","1:a",
    "-vf",f"setpts=PTS+{t0}/TB,ass={assf}:fontsdir={fd},setpts=PTS-STARTPTS",
    "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-profile:v","high","-r",str(FPS),
    "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out],stdin=subprocess.PIPE)
fsz=Wd*Ht*3; n=0; rng=np.random.default_rng(1)
while True:
    buf=dec.stdout.read(fsz)
    if len(buf)<fsz: break
    img=np.frombuffer(buf,np.uint8).reshape(Ht,Wd,3)
    t=t0+n/FPS; n+=1
    z=zoom_at(t); dx,dy,rot=shake_at(t)
    tr=trans_at(t); blur=None
    if tr:
        k,p,s=tr
        if k=="zoom": z*=1+0.35*s; blur=("zoom",0.10*s)
        elif k=="whip": dx+=(-1 if p<0 else 1)*Wd*0.35*s*(1 if p<0 else 1)*(-1); blur=("h",int(90*s)|1)
        elif k=="spin": rot+=(18*s if p<0 else -18*s); z*=1+0.25*s; blur=("zoom",0.07*s)
        elif k=="glitch": blur=("glitch",s)
    if dx or dy: z=max(z,1+(abs(dx)+abs(dy))/Wd*2.2) if tr is None or tr[0]!="whip" else z
    if abs(z-1)>1e-4 or dx or dy or rot:
        M=cv2.getRotationMatrix2D((Wd/2,Ht/2),rot,z); M[0,2]+=dx; M[1,2]+=dy
        img=cv2.warpAffine(img,M,(Wd,Ht),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    if blur:
        kind,a=blur
        if kind=="zoom" and a>0.005: img=zoom_blur(img,a)
        elif kind=="h" and a>3: img=cv2.blur(img,(a,1))
        elif kind=="glitch" and a>0.05:
            img=img.copy(); 
            for _ in range(int(10*a)+2):
                y0=int(rng.integers(0,Ht-80)); hh=int(rng.integers(20,160)); off=int(rng.integers(-80,80)*a)
                img[y0:y0+hh]=np.roll(img[y0:y0+hh],off,1)
            p_=int(18*a)+1; b,g,rr=cv2.split(img); img=cv2.merge([np.roll(b,-p_,1),g,np.roll(rr,p_,1)])
    for a,d,px in RGB:
        if a<=t<a+d:
            p_=int(px*(1-(t-a)/d))+1; b,g,rr=cv2.split(img); img=cv2.merge([np.roll(b,-p_,1),g,np.roll(rr,p_,1)]); break
    img=cv2.LUT(img,LUT)
    f=img.astype(np.float32)
    gray=f.mean(2,keepdims=True); f=gray+(f-gray)*1.12   # malo jace boje
    f*=VIG
    if tr: f+=255*0.18*tr[2]   # blagi blic na tranziciji
    for a,d,c,al in FLASH:
        if a<=t<a+d:
            k_=al*(1-(t-a)/d)**1.5; f=f*(1-k_)+np.array(c,np.float32)*k_
    if FADE_OUT[0]<=t: k_=min(1,(t-FADE_OUT[0])/(FADE_OUT[1]-FADE_OUT[0])); f*=(1-0.9*k_)
    enc.stdin.write(np.clip(f,0,255).astype(np.uint8).tobytes())
    if n%1200==0: print(f"{t:.1f}s",flush=True)
enc.stdin.close(); enc.wait(); dec.wait(); print("done",n)

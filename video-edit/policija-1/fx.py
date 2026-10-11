import sys, subprocess, numpy as np, cv2, math
sys.path.insert(0, sys.argv[1]); from plan import ZOOM, SHAKE, FLASH, RGB, POLICE, DARK, FADE_OUT
src, ass, fontdir, audio, out = sys.argv[2:7]
t0 = float(sys.argv[7]) if len(sys.argv)>7 else 0; dur = float(sys.argv[8]) if len(sys.argv)>8 else None
Wd,Ht,FPS=1080,1920,60
def ease_out(x): return 1-(1-x)**3
def ease_io(x): return 3*x*x-2*x*x*x
def zoom_at(t):
    z=1.0; 
    for i,(kt,kz,kd) in enumerate(ZOOM):
        if t<kt: break
        if kd<=0 or t>=kt+kd: z=kz
        else:
            x=(t-kt)/kd; e=ease_io(x) if kd>1.0 else ease_out(x); z=z+(kz-z)*e
    return z
def shake_at(t):
    dx=dy=rot=0.0
    for a,b,amp,f in SHAKE:
        if a<=t<b:
            k=1-(t-a)/(b-a) if b-a<3 else 1.0
            dx+=amp*k*(math.sin(2*math.pi*f*t*1.0)+0.6*math.sin(2*math.pi*f*1.73*t+1.3))
            dy+=amp*k*(math.sin(2*math.pi*f*0.91*t+2.1)+0.6*math.sin(2*math.pi*f*1.37*t+0.4))
            rot+=0.04*amp*k*math.sin(2*math.pi*f*0.6*t+0.7)
    return dx,dy,rot
yy,xx=np.mgrid[0:Ht,0:Wd].astype(np.float32)
r=np.sqrt(((xx-Wd/2)/(Wd/2))**2+((yy-Ht/2)/(Ht/2))**2)
VIG=np.clip(1-0.32*np.clip(r-0.55,0,None)**1.6,0,1)[...,None].astype(np.float32)
VIG2=np.clip(1-0.75*np.clip(r-0.35,0,None)**1.4,0,1)[...,None].astype(np.float32)
edgeL=np.clip(1-xx/(Wd*0.45),0,1)**2; edgeR=np.clip((xx-Wd*0.55)/(Wd*0.45),0,1)**2
EL=edgeL[...,None].astype(np.float32); ER=edgeR[...,None].astype(np.float32)
RED=np.array([30,30,255],np.float32); BLUE=np.array([255,90,20],np.float32)
ss=["-ss",str(t0)] if t0 else []; tt=["-t",str(dur)] if dur else []
dec=subprocess.Popen(["ffmpeg","-v","error",*ss,"-i",src,*tt,"-f","rawvideo","-pix_fmt","bgr24","-"],stdout=subprocess.PIPE)
assf=ass.replace(":","\\:"); fd=fontdir.replace(":","\\:")
enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","bgr24","-s",f"{Wd}x{Ht}","-r",str(FPS),"-i","-",
    *ss,"-i",audio,*tt,"-map","0:v","-map","1:a",
    "-vf",f"setpts=PTS+{t0}/TB,ass={assf}:fontsdir={fd},setpts=PTS-STARTPTS",
    "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-profile:v","high","-r",str(FPS),
    "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out],stdin=subprocess.PIPE)
fsz=Wd*Ht*3; n=0
while True:
    buf=dec.stdout.read(fsz)
    if len(buf)<fsz: break
    img=np.frombuffer(buf,np.uint8).reshape(Ht,Wd,3)
    t=t0+n/FPS; n+=1
    z=zoom_at(t); dx,dy,rot=shake_at(t)
    zz=max(z, 1.0+ (abs(dx)+abs(dy))/Wd*2.2) if (dx or dy) else z
    M=cv2.getRotationMatrix2D((Wd/2,Ht/2),rot,zz); M[0,2]+=dx; M[1,2]+=dy
    if abs(zz-1)>1e-4 or dx or dy or rot:
        img=cv2.warpAffine(img,M,(Wd,Ht),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    # RGB razdvajanje
    for a,d,px in RGB:
        if a<=t<a+d:
            p=int(px*(1-(t-a)/d))+1; b,g,rr=cv2.split(img)
            img=cv2.merge([np.roll(b,-p,1),g,np.roll(rr,p,1)]); break
    f=img.astype(np.float32)
    vig=VIG
    for a,b in DARK:
        if a<=t<b: k=min(1,(t-a)/0.6); vig=VIG*(1-k)+VIG2*k
    f*=vig
    if POLICE[0]<=t<POLICE[1]:
        ph=(t-POLICE[0])*4.0; on=(int(ph*2))%2; k=0.5+0.5*math.sin(ph*2*math.pi)
        a=0.38*k
        if on: f+= (EL*RED)*a; f*=1-ER*a*0.3; f+=ER*BLUE*a*0.25
        else:  f+= (ER*BLUE)*a; f*=1-EL*a*0.3; f+=EL*RED*a*0.25
    for a,d,c,al in FLASH:
        if a<=t<a+d:
            k=al*(1-(t-a)/d)**1.5; f=f*(1-k)+np.array(c,np.float32)*k
    if FADE_OUT[0]<=t: k=min(1,(t-FADE_OUT[0])/(FADE_OUT[1]-FADE_OUT[0])); f*=(1-0.85*k)
    enc.stdin.write(np.clip(f,0,255).astype(np.uint8).tobytes())
    if n%600==0: print(f"{t:.1f}s",flush=True)
enc.stdin.close(); enc.wait(); dec.wait(); print("done",n)

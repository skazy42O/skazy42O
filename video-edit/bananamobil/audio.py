import sys, numpy as np, scipy.io.wavfile as wf, scipy.signal as ss
from fractions import Fraction
sys.path.insert(0, sys.argv[1]); from plan import SFX, BED, TRANS, FADE_OUT, SLOWMO, FREEZE, MUSIC_VOL, src2out, OUT_DUR
P=sys.argv[2]; SFXDIR=sys.argv[3]; SR=48000
_,orig=wf.read(f"{P}/orig48.wav"); orig=orig.astype(np.float32)/32768
# --- vremenska mapa originalnog zvuka (slow-mo = nizi ton, freeze = eho rep) ---
ev=sorted([(a,b,s) for a,b,s in SLOWMO]+[(t,t,("F",d)) for t,d in FREEZE],key=lambda x:(x[0],1 if isinstance(x[2],tuple) else 0))
parts=[]; cur=0.0
def fade(x,ms=8):
    r=min(len(x)//2,int(SR*ms/1000))
    if r>0: x[:r]*=np.linspace(0,1,r)[:,None]; x[-r:]*=np.linspace(1,0,r)[:,None]
    return x
for a,b,s in ev:
    parts.append(fade(orig[int(cur*SR):int(a*SR)].copy()))
    if isinstance(s,tuple):
        d=s[1]; tail=orig[int((a-0.12)*SR):int(a*SR)].copy(); n=int(d*SR); y=np.zeros((n,2),np.float32)
        for k in range(8):
            i=int(k*0.09*SR); L=min(len(tail),n-i)
            if L>0: y[i:i+L]+=tail[:L]*0.55**k
        y=ss.sosfilt(ss.butter(2,1200,'low',fs=SR,output='sos'),y,axis=0).astype(np.float32)
        parts.append(fade(y)); cur=a
    else:
        seg=orig[int(a*SR):int(b*SR)]; fr=Fraction(1/s).limit_denominator(20)
        y=ss.resample_poly(seg,fr.numerator,fr.denominator,axis=0).astype(np.float32)
        parts.append(fade(y)); cur=b
parts.append(orig[int(cur*SR):])
base=np.concatenate(parts); N=int(OUT_DUR*SR)+1
if len(base)<N: base=np.pad(base,((0,N-len(base)),(0,0)))
mix=base[:N].copy()
def load(n):
    _,x=wf.read(f"{SFXDIR}/{n}.wav"); return x.astype(np.float32)/32768
def add(t,x,arr=None):
    arr=mix if arr is None else arr
    i=int(t*SR)
    if i<0: x=x[-i:]; i=0
    j=min(len(arr),i+len(x)); arr[i:j]+=x[:j-i]
for t,n,v in SFX: add(src2out(t),load(n)*v)
for t,k in TRANS:
    add(src2out(t)-0.28,load("whoosh")*0.4)
    if k=="glitch": add(src2out(t)-0.05,load("glitch")*0.3)
rng=np.random.default_rng(5)
def phonk(d):
    bpm=130; st=60/bpm/4; n=int(d*SR); x=np.zeros(n); tt=lambda L: np.arange(L)/SR
    # kravlje zvono melodija (16 koraka x 4 takta)
    mel=[0,None,0,None,3,None,0,None,7,None,5,None,3,None,2,None]
    base=[587.3,554.4,523.3,554.4]
    bass=[36.7,36.7,34.6,32.7]
    steps=int(d/st)
    for k in range(steps):
        i=int(k*st*SR); bar=(k//16)%4; s=k%16
        n_=mel[s] if bar%2==0 else [0,None,0,3,None,0,None,7,5,None,3,None,2,None,0,None][s]
        if n_ is not None:
            f=base[bar]*2**(n_/12); L=int(0.16*SR); t_=tt(L)
            c=(np.sign(np.sin(2*np.pi*f*t_))+np.sign(np.sin(2*np.pi*f*1.48*t_)))*np.exp(-t_*22)
            c=ss.sosfilt(ss.butter(2,[700,3500],'band',fs=SR,output='sos'),c)
            x[i:i+L]+=0.55*c[:len(x[i:i+L])]
        if s in (0,6,10):   # 808
            L=int(st*SR*(6 if s==0 else 4)); t_=tt(L); f=bass[bar]*(1+1.5*np.exp(-t_*30))
            b=np.tanh(3*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t_*1.8)
            x[i:i+L]+=1.1*b[:len(x[i:i+L])]
        if s%2==0 or s in (13,15):  # hi-hat
            L=int(0.035*SR); h=ss.sosfilt(ss.butter(2,8000,'high',fs=SR,output='sos'),rng.standard_normal(L))*np.exp(-tt(L)*120)
            x[i:i+L]+=0.35*h[:len(x[i:i+L])]
        if s in (4,12):   # snare/clap
            L=int(0.18*SR); t_=tt(L); sn=ss.sosfilt(ss.butter(2,[900,6000],'band',fs=SR,output='sos'),rng.standard_normal(L))*np.exp(-t_*22)
            sn+=0.5*np.sin(2*np.pi*190*t_)*np.exp(-t_*30); x[i:i+L]+=0.7*sn[:len(x[i:i+L])]
    x/=np.max(np.abs(x))+1e-9; t_=np.arange(n)/SR
    return x*np.minimum(1,t_/0.6)*np.minimum(1,(d-t_)/0.4)
music=np.zeros_like(mix)
for a,b,k in BED:
    oa,ob=src2out(a),src2out(b); x=phonk(ob-oa)*MUSIC_VOL; i=int(oa*SR); L=min(len(x),N-i); music[i:i+L]+=x[:L,None]
env=np.ones(N,np.float32)   # muzika tise u slow-mo, nema je u freeze
for a,b,s in SLOWMO:
    i,j=int(src2out(a)*SR),int(src2out(b)*SR); env[i:j]=np.minimum(env[i:j],0.25)
for t,d in FREEZE:
    i=int(src2out(t)*SR); env[i:i+int(d*SR)]=0
env=ss.sosfiltfilt(ss.butter(1,6,'low',fs=SR,output='sos'),env)
mix+=music*env[:,None]
a,b=FADE_OUT; i=int(src2out(a)*SR); mix[i:]*=np.linspace(1,0,N-i)[:,None]**1.5
mix=np.tanh(mix*1.1)/np.tanh(1.1)
wf.write(f"{P}/mix.wav",SR,(np.clip(mix,-1,1)*32767).astype(np.int16)); print("audio ok",N/SR)

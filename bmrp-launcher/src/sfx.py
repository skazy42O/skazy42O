import numpy as np, wave, sys
SR=48000; DUR=23.0
rng=np.random.default_rng(7)
def t_(d): return np.arange(int(d*SR))/SR
def lp(x,a):  # one-pole lowpass, a in (0,1)
    y=np.empty_like(x); s=0.0
    for i,v in enumerate(x): s+=a*(v-s); y[i]=s
    return y
def env(n,att,dec):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(att,1e-4))*np.exp(-np.maximum(0,t-att)/dec); return e
def whoosh(d=0.38,up=True):
    n=int(d*SR); x=rng.standard_normal(n)
    # sweeping band: two lowpasses with moving cutoff
    t=np.linspace(0,1,n); cut=(0.02+0.25*(t if up else 1-t)**1.5)
    y=np.empty(n); s1=s2=0.0
    for i in range(n):
        a=cut[i]; s1+=a*(x[i]-s1); s2+=a*(s1-s2); y[i]=s1-s2*0.6
    e=np.sin(np.pi*np.clip(t,0,1))**1.6
    return y*e/np.max(np.abs(y*e))*0.8
def pop(f0=1100,f1=280,d=0.09):
    t=t_(d); f=f1+(f0-f1)*np.exp(-t*45); ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env(len(t),0.002,0.03)*0.8
def click():
    t=t_(0.05); x=rng.standard_normal(len(t))*np.exp(-t*400)*0.5
    x+=np.sin(2*np.pi*3200*t)*np.exp(-t*250)*0.6+np.sin(2*np.pi*900*t)*np.exp(-t*120)*0.3
    return x*0.9
def impact(d=0.6,f0=120,f1=42,noise=0.5):
    t=t_(d); f=f1+(f0-f1)*np.exp(-t*18); ph=2*np.pi*np.cumsum(f)/SR
    body=np.sin(ph)*np.exp(-t*6)
    nz=lp(rng.standard_normal(len(t)),0.15)*np.exp(-t*30)*noise*3
    x=np.tanh((body+nz)*2.2); return x/np.max(np.abs(x))*0.9
def boom(): return impact(1.3,95,34,0.35)
def stamp():
    a=impact(0.35,180,60,0.9); c=click(); a[:len(c)]+=c*0.8; return a/np.max(np.abs(a))*0.9
def riser(d=0.85):
    t=t_(d); f=300+2200*(t/d)**2; ph=2*np.pi*np.cumsum(f)/SR
    nz=rng.standard_normal(len(t)); nz=nz-lp(nz,0.2)
    x=(np.sin(ph)*0.35+nz*0.4)*(t/d)**2.2; return x/np.max(np.abs(x))*0.7
def tick(): return pop(1800,900,0.04)*0.6

bank={'whoosh':whoosh(),'whoosh_s':whoosh(0.25),'pop':pop(),'click':click(),'impact':impact(),'boom':boom(),'stamp':stamp(),'riser':riser(),'tick':tick()}
EV=[(0.0,'boom',0.9),(0.0,'whoosh_s',0.5),
    (4.24,'pop',0.55),(4.47,'stamp',0.8),(4.96,'pop',0.55),(5.19,'stamp',0.8),(6.88,'pop',0.55),(7.11,'stamp',0.85),
    (7.62,'whoosh_s',0.35),(7.72,'whoosh',0.6),(8.0,'pop',0.45),(10.08,'tick',0.5),
    (10.70,'whoosh',0.6),(13.52,'click',0.8),(13.55,'impact',0.35),(14.84,'click',0.8),(14.87,'impact',0.35),
    (15.25,'whoosh',0.6),(16.80,'whoosh',0.6),(18.84,'click',0.85),(18.86,'impact',0.5),
    (19.25,'whoosh',0.6),(19.38,'riser',0.45),(20.20,'boom',0.95),(20.62,'whoosh',0.55),
    (21.05,'pop',0.6),(21.88,'click',0.85),(21.90,'impact',0.35)]
# soft tick for each subtitle group pop-in
for g in [float(v) for v in sys.argv[3].split(',')]: EV.append((g,'tick',0.18))
mix=np.zeros(int(DUR*SR))
for t0,k,g in EV:
    s=bank[k]; i=int(t0*SR); n=min(len(s),len(mix)-i); mix[i:i+n]+=s[:n]*g
sfx=mix*0.42   # SFX sit under the voice
voice=np.fromfile(sys.argv[1],dtype=np.float32).astype(np.float64)
v=np.zeros_like(mix); v[:min(len(voice),len(mix))]=voice[:len(mix)]
pk=np.max(np.abs(v)); v=v/pk*0.85
out=v+sfx
out=np.tanh(out*1.05)/np.tanh(1.05)*0.97
st=np.stack([out,out],1)
with wave.open(sys.argv[2],'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok',np.max(np.abs(out)))

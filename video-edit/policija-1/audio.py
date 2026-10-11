import sys, numpy as np, scipy.io.wavfile as wf, scipy.signal as ss
sys.path.insert(0, sys.argv[1]); from plan import SFX, BED, FADE_OUT
S=sys.argv[2]; SR=48000
_,orig=wf.read(f"{S}/orig48.wav"); orig=orig.astype(np.float32)/32768
N=len(orig); mix=orig.copy()
def load(n):
    _,x=wf.read(f"{S}/sfx/{n}.wav"); return x.astype(np.float32)/32768
for t,n,v in SFX:
    x=load(n)*v; i=int(t*SR); j=min(N,i+len(x)); mix[i:j]+=x[:j-i]
rng=np.random.default_rng(3)
def bed(kind,d):
    tt=np.arange(int(d*SR))/SR
    if kind=="drone":
        x=np.sin(2*np.pi*55*tt)+0.7*np.sin(2*np.pi*55.7*tt)+0.35*np.sin(2*np.pi*82.4*tt)+0.2*np.sin(2*np.pi*110*tt)*(0.5+0.5*np.sin(2*np.pi*0.25*tt))
        x=ss.sosfilt(ss.butter(4,500,'low',fs=SR,output='sos'),x)
    else:  # potera: 150bpm bas puls + hi-hat + osmine
        bpm=150; beat=60/bpm; x=np.zeros(len(tt)); notes=[41.2,41.2,49.0,46.2]
        for k in range(int(d/beat*2)):
            i=int(k*beat/2*SR); L=int(beat/2*SR*0.9); seg=np.arange(L)/SR
            f=notes[(k//8)%4]; s=np.sign(np.sin(2*np.pi*f*seg))*np.exp(-seg*6)
            x[i:i+L]+=s[:len(x[i:i+L])]
            if k%2==0:  # kick
                kk=np.sin(2*np.pi*(50+120*np.exp(-seg*40))*seg)*np.exp(-seg*12); x[i:i+L]+=1.4*kk[:len(x[i:i+L])]
            h=ss.sosfilt(ss.butter(2,7000,'high',fs=SR,output='sos'),rng.standard_normal(int(0.04*SR)))*np.exp(-np.arange(int(0.04*SR))/SR*90)
            hi=i+int(beat/4*SR); x[hi:hi+len(h)]+=0.5*h[:len(x[hi:hi+len(h)])]
        x=ss.sosfilt(ss.butter(2,3000,'low',fs=SR,output='sos'),x)
    x/=np.max(np.abs(x))+1e-9
    fi=np.minimum(1,tt/0.8); fo=np.minimum(1,(d-tt)/0.8); return x*fi*fo
for a,b,k,v in BED:
    x=bed(k,b-a)*v; i=int(a*SR); mix[i:i+len(x),0]+=x[:N-i]; mix[i:i+len(x),1]+=x[:N-i]
# fade out
a,b=FADE_OUT; i=int(a*SR); L=N-i; mix[i:]*=np.linspace(1,0,L)[:,None]**1.5
# soft limiter
mix=np.tanh(mix*1.1)/np.tanh(1.1)
wf.write(f"{S}/mix.wav",SR,(np.clip(mix,-1,1)*32767).astype(np.int16)); print("audio ok",N/SR)

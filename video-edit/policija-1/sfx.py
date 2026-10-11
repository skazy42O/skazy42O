import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys
SR=48000; out=sys.argv[1]; rng=np.random.default_rng(7)
def save(n,x,peak=0.9):
    x=x/ (np.max(np.abs(x))+1e-9)*peak
    wf.write(f"{out}/{n}.wav",SR,(np.stack([x,x],1)*32767).astype(np.int16))
def t(d): return np.arange(int(SR*d))/SR
def env_ad(n,a,d):  # attack/decay seconds
    ta=t(a); td=t(d); e=np.concatenate([ta/a if a>0 else [], np.exp(-5*td/d)]); return e[:n] if len(e)>=n else np.pad(e,(0,n-len(e)))
def bp(x,lo,hi,o=2): return ss.sosfilt(ss.butter(o,[lo,hi],'band',fs=SR,output='sos'),x)
def lp(x,f,o=4): return ss.sosfilt(ss.butter(o,f,'low',fs=SR,output='sos'),x)
def hp(x,f,o=2): return ss.sosfilt(ss.butter(o,f,'high',fs=SR,output='sos'),x)
def sweep_noise(d,f0,f1,q=0.35):
    n=int(SR*d); x=rng.standard_normal(n); y=np.zeros(n); blk=480
    fs=np.geomspace(f0,f1,n//blk+1); zi=None
    for i in range(0,n,blk):
        fc=fs[i//blk]; sos=ss.butter(2,[fc*(1-q),fc*(1+q)],'band',fs=SR,output='sos')
        if zi is None: zi=np.zeros((sos.shape[0],2))
        y[i:i+blk],zi=ss.sosfilt(sos,x[i:i+blk],zi=zi)
    return y
# whoosh
d=0.55; n=int(SR*d); w=sweep_noise(d,300,3500)*np.sin(np.pi*np.linspace(0,1,n))**2; save("whoosh",w,0.8)
d=0.45; n=int(SR*d); w=sweep_noise(d,3000,250)*np.sin(np.pi*np.linspace(0,1,n))**1.5; save("whoosh_down",w,0.8)
# boom (vine-boom-ish): pitch-dropping sine + sub + click, saturated
d=1.6; tt=t(d); f=55+90*np.exp(-tt*18); ph=2*np.pi*np.cumsum(f)/SR
b=np.sin(ph)*np.exp(-tt*2.6)+0.5*np.sin(ph*2)*np.exp(-tt*5)
b+=0.6*lp(rng.standard_normal(len(tt)),900)*np.exp(-tt*40)
b=np.tanh(2.5*b); save("boom",b,0.95)
# impact (hit): noise burst + low thump, shorter
d=0.9; tt=t(d); f=70+200*np.exp(-tt*30); th=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*6)
nz=bp(rng.standard_normal(len(tt)),200,6000)*np.exp(-tt*22); save("impact",np.tanh(2*(th+0.7*nz)),0.95)
# siren (US wail) 2.8s
d=3.2; tt=t(d); f=900+400*np.sin(2*np.pi*tt/1.4-np.pi/2); ph=2*np.pi*np.cumsum(f)/SR
s=np.sign(np.sin(ph))*0.3+np.sin(ph)+0.3*np.sin(2*ph); s=lp(s,4000)
e=np.minimum(1,tt/0.3)*np.minimum(1,(d-tt)/0.5); save("siren",s*e,0.6)
# yelp siren fast
d=2.0; tt=t(d); f=1000+450*np.sin(2*np.pi*tt*6); ph=2*np.pi*np.cumsum(f)/SR
s=lp(np.sin(ph)+0.4*np.sign(np.sin(ph))*0.5,4000)*np.minimum(1,tt/0.1)*np.minimum(1,(d-tt)/0.3); save("yelp",s,0.55)
# riser 2.5s
d=2.5; tt=t(d); n=len(tt); r=sweep_noise(d,200,8000,0.5)*(tt/d)**2
f=110*2**(tt/d*3); r+=0.4*np.sin(2*np.pi*np.cumsum(f)/SR)*(tt/d)**2; save("riser",r,0.7)
# heartbeat (2 beats)
def beat(d=0.25):
    tt=t(d); return np.sin(2*np.pi*(45+30*np.exp(-tt*25))*tt)*np.exp(-tt*16)
hb=np.zeros(int(SR*0.9)); b1=beat(); hb[:len(b1)]+=b1; o=int(SR*0.24); hb[o:o+len(b1)]+=0.7*b1
save("heartbeat",np.tanh(1.8*lp(hb,300)),0.95)
# ka-ching (bell + coins)
d=1.2; tt=t(d); k=np.zeros(len(tt))
for fr,a in [(2093,1),(2637,.7),(3136,.6),(4186,.4)]:
    o=int(SR*0.08); seg=np.sin(2*np.pi*fr*tt[:len(tt)-o])*np.exp(-tt[:len(tt)-o]*4)*a; k[o:]+=seg
k+=0.5*hp(rng.standard_normal(len(tt)),4000)*np.exp(-tt*30); save("kaching",k,0.6)
# pop (bubble pop for captions) very short
d=0.08; tt=t(d); p=np.sin(2*np.pi*(400+1400*tt/d)*tt)*np.exp(-tt*60); save("pop",p,0.5)
# ding (notification)
d=0.7; tt=t(d); g=(np.sin(2*np.pi*1568*tt)+0.5*np.sin(2*np.pi*2349*tt))*np.exp(-tt*6); save("ding",g,0.5)
# bass drop / braam (cinematic)
d=2.4; tt=t(d); f=48; br=sum(np.sign(np.sin(2*np.pi*f*m*tt+m))/m for m in (1,1.01,2,3))
br=lp(br,700)*np.minimum(1,tt/0.03)*np.exp(-tt*1.3); save("braam",np.tanh(1.5*br),0.9)
# glitch/stutter
d=0.35; n=int(SR*d); g=np.zeros(n)
for i in range(0,n,int(SR*0.03)):
    g[i:i+int(SR*0.015)]=np.sin(2*np.pi*rng.uniform(200,2000)*t(0.015))*rng.uniform(.3,1)
save("glitch",bp(g+0.3*rng.standard_normal(n),150,8000),0.6)
# record scratch / tension sting: tension drone 4s
d=4.0; tt=t(d); dr=(np.sin(2*np.pi*55*tt)+0.6*np.sin(2*np.pi*58.3*tt)+0.3*np.sin(2*np.pi*110.5*tt))
dr=lp(dr,600)*np.minimum(1,tt/1.5)*np.minimum(1,(d-tt)/0.5); save("drone",dr,0.6)
# footstep-ish tick for sneaking (clock tick)
d=0.06; tt=t(d); tk=hp(rng.standard_normal(len(tt)),2500)*np.exp(-tt*120); save("tick",tk,0.5)

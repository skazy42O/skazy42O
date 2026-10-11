import numpy as np, scipy.signal as ss, scipy.io.wavfile as wf, sys
SR=48000; out=sys.argv[1]; rng=np.random.default_rng(11)
def save(n,x,peak=0.9):
    x=x/(np.max(np.abs(x))+1e-9)*peak; wf.write(f"{out}/{n}.wav",SR,(np.stack([x,x],1)*32767).astype(np.int16))
t=np.arange(int(SR*0.6))/SR
f=220+180*np.exp(-t*6)*np.sin(2*np.pi*14*t)+t*120   # boing: vibrato koje se smiruje
save("boing",np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*5)*np.minimum(1,t/0.005),0.7)
t=np.arange(int(SR*0.55))/SR   # record scratch
n=rng.standard_normal(len(t)); y=np.zeros(len(t)); blk=240; zi=None
fc=900+700*np.sin(2*np.pi*9*t[::blk])
for i in range(0,len(t),blk):
    sos=ss.butter(2,[fc[i//blk]*0.6,fc[i//blk]*1.6],'band',fs=SR,output='sos')
    if zi is None: zi=np.zeros((sos.shape[0],2))
    y[i:i+blk],zi=ss.sosfilt(sos,n[i:i+blk],zi=zi)
y*=np.exp(-t*3)*(0.6+0.4*np.sign(np.sin(2*np.pi*9*t)))
save("scratch",y,0.8)

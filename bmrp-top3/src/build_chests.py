# Iseca kovceg sa reference, prebojava ga po temi i pravi rupu za prednji panel.
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
SRC=Image.open('ref-sikatti.png').convert('RGB').crop((640,1320,1460,1880))
W,H=SRC.size
POLY=[(36,72),(52,52),(105,38),(300,30),(520,30),(700,34),(765,42),(788,64),(792,100),(792,472),(786,497),(42,497),(26,474),(22,108)]
PANEL=(108,168,698,468)
def mask(poly,hole=None,S=4):
    m=Image.new('L',(W*S,H*S),0);d=ImageDraw.Draw(m)
    d.polygon([(x*S,y*S) for x,y in poly],fill=255)
    if hole: d.rounded_rectangle([v*S for v in hole],radius=8*S,fill=0)
    return m.resize((W,H),Image.LANCZOS).filter(ImageFilter.GaussianBlur(.7))
def hexc(h):h=h.lstrip('#');return np.array([int(h[i:i+2],16) for i in (0,2,4)],float)
def gmap(L,stops):
    xs=np.array([s[0] for s in stops]);cs=np.array([hexc(s[1]) for s in stops])
    return np.stack([np.interp(L,xs,cs[:,i]) for i in range(3)],-1)
THEMES={
 'boomer': ([(0,'#050505'),(.45,'#17181b'),(.8,'#34373e'),(1,'#7c818c')],[(0,'#140600'),(.45,'#a8380a'),(.75,'#ff7a18'),(1,'#ffe0b0')]),
 'titan':  ([(0,'#04060a'),(.45,'#1a2230'),(.8,'#4a5a72'),(1,'#b8c6da')],[(0,'#020812'),(.45,'#1d5fb8'),(.75,'#5fb0ff'),(1,'#e6f3ff')]),
 'status': ([(0,'#06020c'),(.45,'#2a0f4d'),(.8,'#5a2a99'),(1,'#c9a6ff')],[(0,'#120800'),(.45,'#9a6512'),(.75,'#f2c14e'),(1,'#fff3cf')]),
 'nemacka':([(0,'#040404'),(.45,'#141414'),(.8,'#2c2c2e'),(1,'#6a6a6e')],[(0,'#160002'),(.4,'#a80d14'),(.7,'#ff2a2a'),(.9,'#ffce00'),(1,'#fff3b0')]),
 'klasika':([(0,'#020806'),(.45,'#0c3a2e'),(.8,'#1f7a60'),(1,'#a8e6d2')],[(0,'#120800'),(.45,'#9a6512'),(.75,'#e7c27a'),(1,'#fff6dc')]),
}
a=np.asarray(SRC,float)/255
L=(a*[.299,.587,.114]).sum(-1)
mx,mn=a.max(-1),a.min(-1);S=(mx-mn)/(mx+1e-4)
warm=(a[...,0]>=a[...,2]+.04)&(a[...,0]>=a[...,1]-.02)
sat=np.clip((S-.28)/.17,0,1)*warm
sat=np.asarray(Image.fromarray((sat*255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)),float)/255
alpha=mask(POLY,PANEL)
import sys
for k,(body,acc) in THEMES.items():
    out=gmap(L,body)*(1-sat[...,None])+gmap(L,acc)*sat[...,None]
    im=Image.fromarray(np.clip(out,0,255).astype('uint8'));im.putalpha(alpha)
    im.save(f'chest-{k}.png')
print('panel',PANEL,'size',W,H)

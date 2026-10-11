# ---- BEZANJE SA BANANAMOBILOM: plan montaze (sva vremena su u vremenu ORIGINALA) ----
SRC_DUR=152.661
# Usporeni snimci (od, do, brzina) i zamrznuti kadrovi (vreme, trajanje)
SLOWMO=[(42.20,43.40,0.35),(117.50,119.00,0.30),(142.60,143.80,0.45)]
FREEZE=[(43.40,0.90)]
def _segs():
    ev=[(a,b,s) for a,b,s in SLOWMO]+[(t,t,("F",d)) for t,d in FREEZE]
    return sorted(ev,key=lambda x:(x[0],0 if isinstance(x[2],tuple) else 1))
def src2out(t):
    o=t
    for a,b,s in _segs():
        if isinstance(s,tuple):
            if t>a or (t==a and False): o+=s[1]
        else:
            if t>=b: o+=(b-a)*(1/s-1)
            elif t>a: o+=(t-a)*(1/s-1)
    return o
OUT_DUR=src2out(SRC_DUR)
def out2src(o):
    # vraca (src_t, u_freeze)
    lo,hi=0.0,SRC_DUR
    for t,d in FREEZE:
        st=src2out(t)
        if st<=o<st+d: return t,True
    for _ in range(50):
        m=(lo+hi)/2
        if src2out(m)<o: lo=m
        else: hi=m
    return (lo+hi)/2,False
# Titlovi (start, end, tekst) - svaka grupa reci ima POP-IN animaciju
SUBS=[
(0.10,3.40,"DANAS, LJUDI MOJI, BEŽIMO SA OVOM ČUDNOM NAPRAVOM"),
(4.06,5.40,"NE ZNAM NI JA ŠTA JE"),
(5.70,8.70,"ALI VIDIM DA CURI GORIVO SKROZ"),
(9.38,13.00,"BEŽIMO SA BANANAMOBILOM, BANANAMOTOROM, KAKO GOD"),
(13.66,15.80,"IDEMO DA NAĐEMO NEKOG MILICAJCA"),
(16.30,17.60,"PA DA KRENEMO U AKCIJU"),
(18.24,20.60,"MISLIM DA SAM VIDEO OVDE JEDNOG"),
(21.16,21.80,"AHA, EVO GA!"),
(22.24,23.90,"GLEDA NEŠTO U TELEFON"),
(24.66,25.40,"TREBA TI NEŠTO?"),
(25.64,27.50,"ŠTA GLEDAŠ, TIKTOK GLEDAŠ?"),
(28.00,29.90,"ZAPRATI NAS NA INSTAGRAMU!"),
(33.78,34.70,"POTREBNA PODRŠKA!"),
(35.20,36.90,"OKEJ LJUDI, KRENULI SMO!"),
(37.46,40.50,"UFF, MENI CURI GORIVO, LJUDI MOJI"),
(40.72,42.20,"CURI MI GORIVO!"),
(44.16,44.70,"STANI!"),
(44.78,46.90,"CURI MI GORIVO!"),
(48.56,50.90,"BRZO, BRZO, BRZO!"),
(50.96,52.90,"OVAJ MOTOR NIJE TOLIKO UŽASAN"),
(53.64,54.20,"STANI!"),
(55.92,57.40,"OKEJ, MOTORISTA PAO!"),
(58.00,59.10,"IDEMO VAMO"),
(61.72,63.90,"AKO STANEŠ, DAĆEMO TI DVE BANANE"),
(64.32,67.60,"UH, MOŽDA STANEM AKO SU ZA BANANE"),
(67.80,69.70,"AJOJ, ZEZNUO JE!"),
(72.50,74.50,"ŠTA ĆETE VI SA VAŠIM ŠKODAMA?"),
(80.58,81.60,"LJUDI, IDEMO"),
(93.30,93.90,"NE ČUJEM VAS!"),
(95.58,98.90,"OKEJ, PAO JE MOTORISTA"),
(99.38,100.30,"IDEMO DALJE"),
(100.90,103.60,"PUKLA GUMA!"),
(104.24,106.40,"IDEMO, IDEMO, PRATE ME I DALJE"),
(107.34,107.90,"UFF..."),
(109.68,113.00,"HOP, HOP, HOP!"),
(113.50,115.00,"DOBAR, DOBAR!"),
(119.80,122.80,"STANI! STANI!"),
(126.00,129.20,"ZAPLENITE MU SVE"),
(129.44,130.90,"NE MORAŠ"),
(134.76,137.60,"VEŽI GOVEDO!"),
(138.90,140.50,"PUSTITE ME! PUSTITE ME!"),
(140.90,142.40,"IZGOREO MI MOTOR, BLEJ"),
(144.80,145.40,"MRŠ TAMO!"),
]
GREEN={"BANANAMOBILOM,","BANANAMOTOROM,","BANANE","BANANE,","BANANE!","INSTAGRAMU!","TIKTOK","KRENULI","SMO!","DOBAR,","DOBAR!","HOP,","HOP!","DALJE","AKCIJU","PAO!","PAO","MOTORISTA","TOLIKO","UŽASAN"}
RED={"GORIVO","GORIVO!","GORIVO,","STANI!","PODRŠKA!","BRZO,","BRZO!","PUKLA","GUMA!","ZAPLENITE","GOVEDO!","PUSTITE","MOTOR,","IZGOREO","MRŠ","ŠKODAMA?","MILICAJCA","ČUDNOM"}
PROMO_TEXT="Registrujte se i unesite PROMOKOD: BMRP2026 za besplatna 2 case i bonus novac."
PROMO=[(84.0,90.0)]   # samo jednom
# rezovi -> tranzicije (zoom|whip|spin|glitch)
TRANS=[(9.35,"zoom"),(13.25,"whip"),(18.25,"glitch"),(21.08,"spin"),(24.67,"whip"),(30.58,"zoom"),(32.47,"glitch"),
(37.80,"whip"),(47.53,"spin"),(50.92,"zoom"),(54.72,"whip"),(60.90,"glitch"),(64.28,"zoom"),(67.77,"whip"),(70.97,"spin"),
(75.35,"zoom"),(80.30,"whip"),(85.58,"glitch"),(88.78,"spin"),(100.30,"whip"),(105.45,"zoom"),(119.43,"glitch"),
(123.73,"whip"),(126.65,"zoom"),(136.85,"spin")]
ZOOM=[(0,1.3,0),(0,1.0,0.4),(2.56,1.12,0.08),(3.4,1.0,0.25),(6.88,1.14,0.08),(8.7,1.0,0.25),(10.02,1.12,0.08),(12.9,1.0,0.25),
(21.16,1.16,0.07),(22.0,1.0,0.25),(26.92,1.14,0.07),(27.5,1.0,0.2),(28.0,1.1,1.8),(29.9,1.0,0.25),(37.84,1.12,0.08),(38.5,1.0,0.2),
(40.72,1.15,1.4),(42.2,1.32,1.2),(43.4,1.0,0.0),(44.16,1.18,0.06),(44.7,1.0,0.2),(48.56,1.1,0.08),(50.9,1.0,0.2),(53.64,1.16,0.06),(54.2,1.0,0.2),
(55.92,1.12,0.08),(57.4,1.0,0.2),(61.72,1.08,2.0),(63.62,1.2,0.07),(64.3,1.0,0.25),(66.9,1.15,0.08),(67.6,1.0,0.2),
(72.5,1.06,1.6),(74.3,1.25,0.06),(75.2,1.0,0.25),(93.3,1.14,0.08),(93.9,1.0,0.2),(101.0,1.18,0.07),(102.2,1.0,0.25),
(109.68,1.08,0.06),(110.3,1.0,0.06),(111.5,1.1,0.06),(112.2,1.0,0.06),(112.88,1.12,0.06),(113.4,1.0,0.2),
(117.0,1.2,0.5),(117.6,1.38,1.3),(119.0,1.0,0.3),(119.8,1.14,0.08),(120.6,1.0,0.2),(134.76,1.12,0.08),(137.5,1.0,0.2),
(138.9,1.1,1.5),(140.5,1.0,0.2),(142.6,1.25,1.2),(143.8,1.0,0.3),(144.8,1.15,0.06),(145.4,1.0,0.25),(147.0,1.12,3.0)]
SHAKE=[(0.0,0.3,14,18),(42.4,43.4,18,14),(44.16,44.5,10,18),(53.64,53.95,10,18),(74.3,74.6,10,18),(101.0,101.4,10,18),
(117.85,119.0,22,14),(119.0,119.6,10,14),(142.9,143.4,8,14)]
FLASH=[(0.0,0.25,(255,255,255),0.7),(42.45,0.12,(255,255,255),0.5),(117.9,0.1,(255,255,255),0.6)]
RGB=[(0.0,0.25,12),(42.45,0.4,10),(117.9,0.5,14),(74.3,0.15,8)]
# anime linije brzine (od, do)
SPEED=[(30.6,32.4),(35.5,37.7),(47.6,50.9),(84.2,85.5),(100.4,101.0),(103.7,105.4),(108.0,109.6)]
SFX=[
(0.00,"boom",0.7),(0.00,"whoosh_down",0.4),(2.56,"pop",0.35),(6.88,"pop",0.35),(10.02,"boing",0.45),(21.16,"ding",0.3),
(26.92,"pop",0.35),(28.0,"ding",0.3),(33.78,"impact",0.3),(40.72,"riser",0.3),(42.45,"impact",0.55),(43.40,"scratch",0.6),
(43.40,"boom",0.55),(44.16,"pop",0.35),(53.64,"impact",0.35),(55.92,"ding",0.3),(63.62,"boing",0.5),(66.9,"ding",0.3),
(74.30,"boom",0.6),(93.3,"pop",0.3),(101.0,"impact",0.4),(109.68,"boing",0.35),(111.5,"boing",0.35),(112.88,"boing",0.4),
(116.8,"riser",0.35),(117.90,"braam",0.6),(117.90,"impact",0.55),(119.80,"pop",0.3),(134.76,"boom",0.45),(142.6,"whoosh",0.5),
(144.8,"pop",0.35),(149.0,"boom",0.45),
]
MUSIC_VOL=0.15   # 50% od proslog videa
BED=[(30.5,117.6,"phonk"),(119.6,151.5,"phonk")]
DUCK=[]
FADE_OUT=(149.6,152.661)

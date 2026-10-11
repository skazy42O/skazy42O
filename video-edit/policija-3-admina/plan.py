# ---- POLICIJA 3 ADMINA: plan montaze ----
# Titlovi: (start, end, tekst). Tekst se automatski deli na grupe od 1-3 reci,
# a aktivna rec se pali (karaoke stil). Kljucne reci dobijaju posebnu boju.
SUBS=[
(0.10,2.40,"DANAS ĆEMO ADMINU PONUDITI RANK UP"),
(2.90,5.60,"AKO USPE DA POBEGNE OD POLICIJE DOBIJA RANK UP"),
(6.20,7.50,"IMA DA BIRA IZMEĐU TRI VOZILA"),
(8.00,9.20,"OVAJ ZELENI TENKIĆ"),
(9.80,11.20,"NAJNOVIJI BOGATI MANSORY"),
(11.50,13.90,"I OVAJ AUTO ZA PREVOZ GROBOVA"),
(15.30,17.30,"DOBRO, SAD ĆU POZVATI ADMINA"),
(17.98,20.20,"DA VIDIMO DA LI ĆE PRIHVATITI PONUDU"),
(20.48,23.30,"POZVALI SMO ADMINA, SEDEO JE OVDE NA KLUPI"),
(23.80,24.50,"ADMINE!"),
(26.54,28.20,"EVO, IMAM PITANJE ZA TEBE"),
(29.50,33.60,"IZABRAN SI DA UČESTVUJEŠ U NAGRADNOJ IGRI ZA RANK UP"),
(37.40,38.40,"DOBRO, AJDE"),
(40.50,41.40,"JOJ, GLEDAJ TENK!"),
(42.00,43.86,"ZNAČI, BIRAŠ IZMEĐU TRI VOZILA"),
(44.10,46.80,"AKO USPEŠ DA POBEGNEŠ OD POLICIJE DOBIJAŠ RANK UP"),
(46.82,47.90,"SADA BIRAJ"),
(48.14,48.90,"A AKO NE USPEM?"),
(49.30,52.90,"AKO NE USPEŠ, NAŽALOST RANK DOWN NA MODERATORA"),
(53.32,54.20,"UFFF..."),
(63.10,64.90,"UZEO SI AUTO ZA PREVOZ GROBOVA?"),
(65.56,66.40,"OKEJ, EVO IH"),
(71.10,71.90,"KEROVI?!"),
(75.40,76.50,"KAKVI KEROVI?!"),
(78.70,79.10,"BOGAMI!"),
(82.40,83.80,"ŠTA JE OVO? PET KOLA, BRATE!"),
(85.50,87.40,"BOGAMI, BIĆE JAKO NAPETO"),
(87.80,90.40,"PALE MEGAFONE, DERU SE"),
(91.90,93.80,"IDE, IDE OVA KRNTIJA!"),
(94.18,97.00,"OVO TI JE PREMIJUM, NEMAŠ TO"),
(98.00,99.80,"OVO NIKAD NISTE VIDELI"),
(100.06,101.10,"POGLEDAJ, POGLEDAJ"),
(101.40,102.60,"MERCEDES I BMW"),
(103.16,105.50,"AJDE PO BUREK I JEDAN JOGURT"),
(106.00,107.70,"POGLEDAJ, UFF, DOBRI SU"),
(110.30,112.00,"PUCAJU PO GUMAMA!"),
(120.40,122.00,"E, POGODIĆE GUMU!"),
(122.40,122.90,"OPA!"),
(129.60,130.30,"OKEJ, MERCEDES"),
(131.00,131.60,"OPA!"),
(135.10,136.50,"I ONI PUCAJU PO NAMA!"),
(138.00,139.00,"JOŠ JEDNA PUKLA GUMA"),
(139.40,139.90,"AJMO!"),
(140.10,140.70,"PUKLA GUMA!"),
(142.60,143.20,"BEŽI!"),
(144.00,146.60,"NE, PUKLA GUMA, BRATE!"),
(150.20,150.80,"OPA!"),
(159.90,161.20,"BEŽI, BEŽI!"),
(166.80,167.40,"BEŽI!"),
(168.00,168.90,"BEŽI, BEŽI!"),
(169.50,170.90,"TO JE TO, BEŽI!"),
(171.40,173.60,"SVAKA ČAST, USPELI SMO DA POBEGNEMO!"),
(174.10,175.90,"TO ZNAČI DOBIJAŠ ADMIN RANK!"),
]
GREEN={"RANK","UP","USPELI","POBEGNEMO","PREMIJUM","ADMIN","TO!","USPE","POBEGNE","DOBIJAŠ","DOBIJA","MANSORY","TENKIĆ","TENK!"}
RED={"POLICIJE","KEROVI?!","PET","KOLA,","GUMU!","GUMA","GUMA!","GUMA,","GUMAMA!","DOWN","MODERATORA","PUCAJU","BEŽI!","BEŽI,","OPA!","NE,","GROBOVA","GROBOVA?","KRNTIJA!"}
# Promo tekst - nasumicne pozicije unutar TikTok sigurne zone
PROMO_TEXT="Registrujte se i unesite PROMOKOD: BMRP2026 za besplatna 2 case i bonus novac."
PROMO=[(14.0,19.0),(55.0,60.0),(97.0,102.0),(124.0,129.0),(163.0,168.0)]
# Tranzicije na rezovima: (vreme, tip)  tip: zoom|whip|spin|glitch
TRANS=[(8.03,"zoom"),(9.80,"whip"),(11.90,"glitch"),(20.48,"spin"),(23.75,"whip"),(28.35,"zoom"),(37.37,"glitch"),
(58.02,"whip"),(65.52,"zoom"),(74.00,"spin"),(85.65,"whip"),(94.38,"zoom"),(96.40,"glitch"),(104.23,"whip"),(106.60,"zoom"),
(109.83,"spin"),(138.00,"whip"),(140.93,"glitch"),(147.13,"zoom"),(163.63,"whip"),(166.08,"spin"),(176.52,"zoom")]
# Punch-in zum: (vreme, zum, prelaz)
ZOOM=[(0,1.25,0),(0,1.0,0.35),(1.98,1.12,0.1),(2.9,1.0,0.25),(4.5,1.14,0.1),(5.6,1.0,0.25),(13.0,1.12,0.1),(13.9,1.0,0.2),
(23.8,1.15,0.08),(24.5,1.0,0.2),(31.6,1.12,1.6),(33.6,1.0,0.25),(40.5,1.15,0.08),(41.4,1.0,0.2),(46.82,1.12,0.1),(47.9,1.0,0.2),
(51.0,1.18,1.8),(52.9,1.0,0.25),(63.1,1.1,1.5),(64.9,1.0,0.2),(71.1,1.22,0.06),(72.0,1.0,0.3),(82.86,1.2,0.08),(83.9,1.0,0.25),
(91.9,1.1,0.1),(93.8,1.0,0.2),(110.3,1.15,0.08),(112.0,1.0,0.25),(122.4,1.18,0.06),(123.0,1.0,0.2),(135.1,1.14,0.08),(136.5,1.0,0.2),
(140.1,1.2,0.06),(140.8,1.0,0.2),(144.6,1.15,0.06),(146.6,1.0,0.25),(151.5,1.28,0.9),(152.42,1.42,0.04),(152.5,1.12,0.6),(154.0,1.0,0.5),(171.4,1.1,2.2),(174.1,1.16,0.1),(176.0,1.0,0.3)]
SHAKE=[(0.0,0.3,14,18),(71.1,71.5,12,18),(82.86,83.2,10,18),(122.4,122.7,10,18),(140.1,140.5,14,18),(144.6,145.0,12,18),
(152.42,154.4,26,15),(172.0,172.4,8,16)]
FLASH=[(0.0,0.25,(255,255,255),0.7),(71.1,0.12,(255,255,255),0.35),(152.42,0.3,(255,255,255),0.65)]
RGB=[(0.0,0.25,12),(71.1,0.2,8),(140.1,0.2,8),(152.42,0.4,14)]
SFX=[
(0.00,"boom",0.8),(0.00,"whoosh_down",0.4),(1.98,"pop",0.4),(4.5,"ding",0.3),(13.0,"pop",0.35),(23.8,"impact",0.35),
(31.6,"riser",0.25),(33.5,"ding",0.3),(40.5,"pop",0.4),(51.0,"riser",0.3),(52.9,"boom",0.55),(63.1,"pop",0.35),
(71.10,"boom",0.7),(71.6,"siren",0.32),(72.0,"riser",0.35),(82.86,"impact",0.5),(91.9,"pop",0.3),(103.16,"ding",0.25),
(110.3,"impact",0.4),(122.4,"impact",0.45),(140.1,"boom",0.55),(144.6,"impact",0.45),(150.4,"riser",0.45),(152.42,"braam",0.8),
(152.42,"boom",0.85),(152.42,"impact",0.6),(171.4,"kaching",0.4),(174.1,"ding",0.35),(176.4,"boom",0.5),
]
# podloga: phonk ritam tokom potere
BED=[(74.0,152.3,"phonk",0.30),(155.0,177.0,"phonk",0.26)]
DUCK=[(151.6,152.42)]   # tisina pred sudar
FADE_OUT=(177.6,178.666)

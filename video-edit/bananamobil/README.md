# BEŽANJE SA BANANAMOBILOM – montaža za TikTok

Izvor: release [VIDEO BANANA MOBIL](https://github.com/skazy42O/skazy42O/releases/tag/bananamobil).
Prati pravila iz [`../STIL.md`](../STIL.md).

Šta video ima:

- Karaoke titlove sa **pop-in** animacijom na svakoj grupi reči.
- Tranzicije na 25 rezova: zoom blur, whip pan, spin i glitch.
- **Slow-motion** na oba pada (0:42 i 1:58) i na skoku preko ograde (2:23). Zvuk je tada usporen i dublji, a muzika se stiša.
- **Zamrznut kadar** posle prvog pada: crno-beli kadar, polagani zum i „record scratch” zvuk.
- **Anime linije brzine** dok kvad juri.
- Smešne zvukove: boing na „banane” i „hop hop hop”, boom na „škodama?”.
- Phonk muziku na 50% jačine.
- Promo kod, samo jednom.

Sva vremena su u `plan.py`, u vremenu originalnog snimka. `src2out()` ih preračunava zbog slow-motiona.

```bash
python3 sfx_extra.py sfx/              # boing + scratch (ostali efekti iz ../policija-1/sfx)
ffmpeg -i BEZANJE.SA.BANANAMOBIL.mp4 -vn -ac 2 -ar 48000 orig48.wav
python3 audio.py . . sfx
python3 ass.py . subs.ass fonts
python3 fx.py . BEZANJE.SA.BANANAMOBIL.mp4 subs.ass fonts mix.wav BANANAMOBIL_EDIT.mp4
```

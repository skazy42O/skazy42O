# VIDEO POLICIJA #1 – montaža

Skripte za montažu videa `Timeline.1.mp4` iz release-a
[VIDEO POLICIJA #1](https://github.com/skazy42O/skazy42O/releases/tag/videopolicija).

Šta video dobija:

- **Titlovi u MrBeast stilu**: žuti font Luckiest Guy sa debelom crnom ivicom i pop-in animacijom. Važne reči su crvene ili zelene.
- **Stikeri**: hook na početku, „POLICIJA JE BLIZU!”, „+ KALAŠ”, „POLICAJAC!!”, „PRIMETILI SU NAS!”, „POTERA!” i „DEO 2 USKORO!” na kraju.
- **Pokret**: punch-in zumovi na ključnim rečima, polagani zumovi na napetim delovima, tresenje ekrana, blicevi, RGB razdvajanje na udarcima, crveno-plava policijska svetla tokom potere i fade-out.
- **Zvuk**: whoosh, boom, impact, braam, sirena, otkucaji srca, ka-ching, glitch i riser. Ispod toga ide napeta podloga i bas ritam za poteru.

Sva vremena (titlovi, efekti, zumovi) su u `plan.py`. Promeni ih tamo i pokreni sve ponovo.

## Pokretanje

Potrebno: `ffmpeg` (sa libass), Python 3, `numpy`, `scipy` i `opencv-python-headless`.

```bash
python3 sfx.py sfx/                                   # pravi zvučne efekte
ffmpeg -i Timeline.1.mp4 -vn -ac 2 -ar 48000 orig48.wav
python3 audio.py . .                                  # mix.wav = original + efekti
python3 ass.py . subs.ass                             # titlovi
python3 fx.py . Timeline.1.mp4 subs.ass fonts mix.wav VIDEO_POLICIJA_1_EDIT.mp4
```

Font Luckiest Guy je pod licencom Apache 2.0 (Google Fonts). Zvučni efekti su sintetisani u kodu (`sfx.py`), pa nema problema sa autorskim pravima.

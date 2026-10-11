# POLICIJA 3 ADMINA (bežanje admina) – montaža za TikTok

Skripte za montažu videa `Bezanje.Admina.not.edited.mp4` iz release-a
[POLICIJA 3 ADMINA](https://github.com/skazy42O/skazy42O/releases/tag/policija3admina).

- **Titlovi u karaoke stilu**: reč koja se trenutno izgovara se pali žuto, a ključne reči zeleno ili crveno. Grupe imaju 1–3 reči, a veličina fonta se sama prilagođava tako da tekst ostane u TikTok sigurnoj zoni (levo 70px, desno 880px, gore 180px, dole 1500px). Tako ga ne pokrivaju dugmići sa desne strane ni opis na dnu.
- **Tranzicije na rezovima**: zoom blur, whip pan, spin i glitch, uz whoosh zvuk.
- **Pokret**: punch-in zumovi, tresenje i blic na sudaru, jači kontrast i boje, vinjeta i fade-out.
- **Zvuk**: phonk ritam tokom potere, samo jedna kratka sirena i tišina tik pred sudar.
- **Promo tekst** „Registrujte se i unesite PROMOKOD: BMRP2026 …” se pojavljuje 5 puta na nasumičnim mestima u sigurnoj zoni.

Sva vremena su u `plan.py`. Zvučni efekti dolaze iz `../policija-1/sfx/`.

```bash
ffmpeg -i Bezanje.Admina.not.edited.mp4 -vn -ac 2 -ar 48000 orig48.wav
python3 audio.py . . ../policija-1/sfx
python3 ass.py . subs.ass fonts
python3 fx.py . Bezanje.Admina.not.edited.mp4 subs.ass fonts mix.wav BEZANJE_ADMINA_EDIT.mp4
```

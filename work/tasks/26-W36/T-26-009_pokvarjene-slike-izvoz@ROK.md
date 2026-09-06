---
task: T-26-009
title: Preverba naj pokvarjene slike prijavi, ne pa da izvoz pade
status: notify
cost-usd: 1.82
assignee: [ROK]
requested-by: ROK
week: 26-W36
created: 2026-09-06
completed:
notified:
blocked-by: []
visibility: team
---

# Preverba naj pokvarjene slike prijavi, ne pa da izvoz pade

## Goal

`preveri_ric.py` v razdelku IZVOZ V WORD občasno (opaženo pri T-26-008: 1 od
6 zagonov) pade z `UnrecognizedImageError`, ker naključno vzorčenje kdaj
zadene eno od pokvarjenih slikovnih datotek v `slike/`. Preverba naj take
slike zazna in prijavi kot težavo, izvoz pa naj jih preskoči namesto da pade.

## Scope

In: zaznava neveljavnih/pokvarjenih slikovnih datotek v `slike/` (vsaj tistih,
ki jih `python-docx`/PIL ne zna odpreti); poročanje seznama v `preveri_ric.py`;
izvoz v Word naj tako sliko preskoči namesto da vrže izjemo.
Out: popravljanje/nadomeščanje samih pokvarjenih slik; ponovni uvoz virov, iz
katerih izvirajo.

## Notes

Najdeno pri T-26-008 (glej `## Result` tam): 21 pokvarjenih slikovnih datotek
v mapi `slike/`, od tega ena pri RIC nalogah
(`nukleinske kisline/nukleinske kisline_image56.jpeg`). Napaka obstaja že na
varnostni kopiji izpred posega T-26-008, torej ni z njim povezana.

## Plan

Vzrok: `bionaloga/generator.py:_preveri_slike` (vrstice 15–25) preveri le
obstoj datoteke in podprto pripono, ne pa da jo `python-docx` dejansko zna
odpreti. `_dodaj_besedilo_s_slikami` (vrstica 122) zato pokliče
`doc.add_picture()` na pokvarjeno datoteko in `UnrecognizedImageError` pade
skozi, brez lova (`preveri_ric.py` uvozi `generator.generiraj_test()` brez
try/except okoli klica, vrstica 103).

Potrjeno v tej seji: `docx.image.image.Image.from_file(pot)` na znano
pokvarjeni datoteki (`slike/nukleinske kisline/nukleinske
kisline_image56.jpeg`) vrže `UnrecognizedImageError` — isto pot kot
`add_picture()` uporablja interno, torej zanesljivo napove, ali bo vstavljanje
padlo. Brez dodatne odvisnosti (Pillow ni nameščen).

1. V `bionaloga/generator.py`, `_preveri_slike()`: za vsako sliko, ki obstaja
   in ima podprto pripono, dodatno poskusi `docx.image.image.Image.from_file(pot)`
   znotraj `try/except Exception` (lovi `UnrecognizedImageError` in splošneje
   vsako izjemo pri branju — pokvarjena datoteka lahko odpove na različne
   načine). Ob napaki dodaj v `napake`:
   `f"slika je pokvarjena ({pot.name}): {e}"`.
2. V `_dodaj_besedilo_s_slikami()` (vrstica 121) pusti pogoj kot je — ker
   `_preveri_slike()` zdaj že izloči nalogo prej (`generiraj_test` jo
   `continue`-a na vrstici 182), do `doc.add_picture()` na pokvarjeni sliki
   sploh ne pride več.
3. V `preveri_ric.py` doda se izpis "pokvarjenih slikovnih datotek" v razdelku
   `=== SLIKE ===` (po vzoru `napacen_format`, vrstici 74/81‑88): za vsako
   sliko RIC nalog dodatno poskusi `Image.from_file`, štej in izpiši do 3
   primere — tako se pokvarjene slike vidijo v poročilu preverbe, ne le kot
   "izpuščena naloga" v razdelku izvoza.
4. Preveri:
   - `python3 preveri_ric.py` — razdelek `IZVOZ V WORD` se ne sme več sesuti;
     `napake`/`IZPUŠČENIH nalog` sme vsebovati pokvarjeno RIC nalogo s sliko
     `nukleinske kisline_image56.jpeg`, ne sme pa vreči `UnrecognizedImageError`.
   - Ponovi zagon 10× (`for i in range(10): python3 preveri_ric.py`) — ker
     napaka nastopi naključno (1 od 6 v T-26-008), en sam zagon je ne dokaže
     zanesljivo popravljene.
   - `python3 -c "from bionaloga import generator; ..."` ročno pokliči
     `generiraj_test` s seznamom id-jev, ki vsebuje znano pokvarjeno RIC
     nalogo, in preveri, da je v vrnjenih `napake` omenjena kot izpuščena
     (ne pade).

## Result

Popravljeno in preverjeno. Izvoz v Word ne pade več na pokvarjeni slikovni
datoteki, preverba jo prijavi kot težavo.

**Spremembe**

- `bionaloga/generator.py`
  - nova javna funkcija `je_slika_berljiva(pot)`: poskusi
    `docx.image.image.Image.from_file(pot)` (ista pot, ki jo `add_picture()`
    uporablja interno) v `try/except Exception`; vrne `None` ob uspehu, sicer
    `"<TipNapake>: <sporočilo>"`. Brez nove odvisnosti (Pillow ni potreben).
  - `_preveri_slike()`: za sliko, ki obstaja in ima podprto pripono, dodatno
    preveri berljivost; ob napaki doda
    `slika je pokvarjena (<ime>): <razlog>`. `generiraj_test()` tako nalogo
    izpusti (obstoječi `continue`) in jo navede v `napake`.
  - `_dodaj_besedilo_s_slikami()` nespremenjen — do `add_picture()` na
    pokvarjeni sliki po zgornjem sploh ne pride.
  - dopolnjen docstring `generiraj_test()`.
- `preveri_ric.py`, razdelek `=== SLIKE ===`: nov števec
  `pokvarjenih datotek (bi izpadle iz testa)` (po vzoru `napacen_format`),
  označen z `!!`, z izpisom do 3 primerov skupaj z razlogom.

**Preverjeno**

- `je_slika_berljiva()` na znano pokvarjeni
  `slike/nukleinske kisline/nukleinske kisline_image56.jpeg`
  → `UnrecognizedImageError`; na zdravi datoteki iste mape → `None`.
- `generiraj_test([17933])` (edina RIC naloga s to sliko) vrne dokument in
  napako `Naloga 17933: slika je pokvarjena (…) — izpuščena`; ne vrže izjeme.
- `preveri_ric.py` 10× zapored: nobenega `UnrecognizedImageError` in nobenega
  `Traceback`; razdelek `IZVOZ V WORD` se v vseh 10 zagonih izvede do konca.
- `python3 scripts/check_tasks.py` → `9 tasks, 0 errors`.
- `python3 test_vmesnik.py` → `vsi testi ok (5)`.

**Opombe / odstopanja**

- Za zagone je uporabljen `.venv/bin/python` — sistemski `python3` v tem okolju
  nima `python-docx`/`fastapi`.
- `preveri_ric.py` zdaj konča z izhodno kodo 1 (`1 TEŽAV`), ker je pokvarjena
  slika po zahtevi naloge prijavljena kot težava. Prej je bila koda 0 (v ~5 od
  6 zagonov) ali sesutje. To je pričakovano in ostane, dokler datoteka ni
  popravljena — kar je izrecno izven obsega te naloge.
- Preverba pokvarjenosti bere vseh 5.490 RIC slikovnih zapisov (in vsako sliko
  v izvozu); zagon `preveri_ric.py` je zato nekaj sekund počasnejši. Sprejemljivo.
- Popravljanje same pokvarjene datoteke in preostalih 20 pokvarjenih slik izven
  RIC (najdeno pri T-26-008) ostaja odprto — vredno svoje naloge.

Commit: glej `git log` za `T-26-009`.

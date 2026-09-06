---
task: T-26-011
title: Preverjanje in normalizacija slik ob uvozu
status: notify
cost-usd: 1.78
assignee: [ROK]
requested-by: Rok
week: 26-W36
created: 2026-09-06
completed:
notified:
blocked-by: []
visibility: team
---

# Preverjanje in normalizacija slik ob uvozu

## Goal

Ob vsakem uvozu slike (standardni uvoz, uvoz velikih datotek, ročni upload
učitelja) se sveže zapisana datoteka v `slike/` takoj preveri z že obstoječo
`je_slika_berljiva()` (uvedeno v T-26-009/T-26-010). Če je neberljiva in gre za
JPEG, se prekodira v baseline JPEG (isti postopek kot ročno v T-26-010:
`magick -strip -interlace none -quality 95`) in ponovno preveri. S tem se
težava iz T-26-010 (JPEG z Exif glavo ali progresivnim zapisom, ki ga
`python-docx` zavrne) ne nabira naprej ob vsakem novem uvozu.

## Scope

In:
- Klic preverjanja + po potrebi prekodiranja takoj po vsakem surovem zapisu
  slike v `slike/`, na vseh treh mestih, kjer se to danes zgodi:
  - `klasificiraj.py:279` (standardni uvozni tok)
  - `izvozi_slike.py:~140` (tok za velike datoteke)
  - `bionaloga/main.py` `nalozi_sliko()` (~vrstica 225, ročni upload učitelja)
- Skupna pomožna funkcija (npr. `normaliziraj_sliko(pot)` v `bionaloga/generator.py`,
  poleg `je_slika_berljiva()`), ki jo vsi trije klicatelji uporabijo.

Out:
- Neobstoječih 9 neveznih neberljivih datotek v `slike/` iz T-26-010 (niso
  vezane na nalogo) — ni del te naloge.
- Formati, ki jih ImageMagick ne zna prekodirati v podprt format
  (`.wmf`/`.emf` in podobno) — ostane enako kot danes: obstoječa preverba v
  `_preveri_slike()` jo prijavi ob izvozu, naloga se ne izvozi s to sliko, a
  izvoz ne pade (T-26-009).
- Deploy (push) — ni v obsegu.

## Acceptance criteria

- [x] Nova pomožna funkcija obstaja in jo uporabljajo vsa tri mesta zapisa
      slike ob uvozu (`klasificiraj.py`, `izvozi_slike.py`, `main.py:nalozi_sliko`).
- [x] Ponovljen scenarij iz T-26-010: JPEG s progresivnim zapisom ali Exif
      glavo, prepisan skozi kateri koli od uvoznih poti, je po uvozu berljiv
      za `je_slika_berljiva()` (vrne `None`), medtem ko je pred prekodiranjem
      vračala napako.
- [x] `python test_vmesnik.py` — vse teste zeleno (izhodišče: 5/5).
- [x] `python scripts/check_tasks.py` — 0 napak.
- [x] Slika, ki je berljiva že ob zapisu, ni po nepotrebnem prekodirana
      (funkcija najprej preveri, šele nato po potrebi prekodira).

## Notes

Predlog za to nalogo je zapisan v `## Result` naloge T-26-010 ("Predlog za
ločeno nalogo"): isti postopek prekodiranja, ki je bil takrat izveden ročno za
21 obstoječih datotek, naj teče samodejno ob vsakem novem uvozu. `ImageMagick`
(`magick`) je na strežniku nameščen in dostopen v PATH.

## Plan

1. V `bionaloga/generator.py` dodaj `normaliziraj_sliko(pot: Path) -> None`
   tik pod `je_slika_berljiva()`:
   - Če `je_slika_berljiva(pot)` vrne `None`, ne naredi nič.
   - Če vrne napako in je `pot.suffix.lower()` v `{".jpg", ".jpeg"}`, poženi
     `magick <pot> -strip -interlace none -quality 95 <pot>` (prekodiranje na
     mestu, isti ukaz kot v T-26-010) in ponovno preveri z `je_slika_berljiva()`.
     Izpiši opozorilo (`print`/log), če ostane neberljiva tudi po poskusu.
   - Za druge formate (npr. `.wmf`, `.emf`) ne poskušaj prekodirati — pusti
     obstoječemu preverjanju v `_preveri_slike()`, da to prijavi ob izvozu.
2. V `klasificiraj.py` takoj po `with z.open(...) as src, open(cilj, "wb") as
   dst: ...` (vrstica ~279) dodaj klic `generator.normaliziraj_sliko(cilj)`.
3. V `izvozi_slike.py` na istem mestu (po `shutil.copyfileobj(src, dst)`,
   vrstica ~143) dodaj enak klic na `cilj`.
4. V `bionaloga/main.py` `nalozi_sliko()` po `with open(SLIKE_POT / ime, "wb")
   as f: ...` (vrstica ~225) dodaj enak klic.
5. Preveri:
   - Vzemi eno od znanih pokvarjenih variant iz T-26-010 (progresiven JPEG ali
     JPEG z Exif glavo — reproduciraj z `magick -interlace plane` oz. z
     dodajanjem Exif bloka na veljaven JPEG, ali uporabi eno od 9 neveznih
     neberljivih datotek iz `slike/`, ki niso v tabeli `slika`, kot testni
     vzorec — kopija, ne prepiši izvirnika), jo prepelji skozi
     `normaliziraj_sliko()` in preveri, da `je_slika_berljiva()` po klicu vrne
     `None`.
   - `python test_vmesnik.py` → 5/5 (ali brez novih rdečih).
   - `python scripts/check_tasks.py` → 0 napak.
   - Ročni pregled diffa v vseh treh datotekah — prepričaj se, da klic ne
     podvoji zapisa in ne spremeni imena datoteke (ime mora ostati enako, ker
     `naloga.besedilo` nanj kaže prek `[SLIKA:...]`).
6. Commit brez push (deploy ni v obsegu).

## Result

Vse sprejemne kriterije izpolnjeno; commit brez push (deploy ni v obsegu).

### Kaj je shipano

1. **`bionaloga/generator.py`** — nova funkcija `normaliziraj_sliko(pot)` tik
   pod `je_slika_berljiva()`. Najprej preveri; če je slika berljiva, ne naredi
   nič in ne prekodira. Če ni berljiva in gre za `.jpg`/`.jpeg`, požene
   `magick <pot> -strip -interlace none -quality 95 <pot>` (prekodiranje na
   mestu, ime datoteke ostane isto) in ponovno preveri. Vrne `None` ob uspehu
   oz. opis preostale napake; ob neuspehu izpiše opozorilo in ne vrže izjeme.
   Za druge formate (`.wmf`, `.emf`) ne poskuša ničesar — to ostane pri
   `_preveri_slike()` ob izvozu (T-26-009). Dodan `import subprocess`.

2. **`klasificiraj.py`** (standardni uvoz, ~vrstica 285) — klic
   `normaliziraj_sliko(cilj)` po zapisu slike. Dodan import
   `from bionaloga.generator import normaliziraj_sliko`.

3. **`izvozi_slike.py`** (tok za velike datoteke, ~vrstica 143) — enak klic po
   `shutil.copyfileobj(src, dst)`, enak import.

4. **`bionaloga/main.py` `nalozi_sliko()`** (ročni upload, ~vrstica 227) — klic
   `generator.normaliziraj_sliko(SLIKE_POT / ime)` po zapisu, pred
   `baza.dodaj_sliko()`.

### Odstopanje od načrta (majhno, namerno)

V `klasificiraj.py` se pri `.emf`/`.wmf` po uspešni pretvorbi z LibreOffice
`cilj` prestavi na nastalo `.png` datoteko (`cilj = png`), da se normalizacija
požene nad datoteko, ki dejansko ostane na disku, in ne nad že izbrisanim
izvirnikom. Načrt tega ni omenjal; brez tega bi klic tekel nad neobstoječo potjo.

### Preverjanje

| preverba | izid |
|---|---|
| realni pokvarjeni vzorec `UnexpectedEndOfFileError` (kopija, izvirnik nedotaknjen) | pred: `UnexpectedEndOfFileError` → po `normaliziraj_sliko()`: `None` |
| realni pokvarjeni vzorec `UnrecognizedImageError` (kopija) | pred: `UnrecognizedImageError` → po: `None` |
| berljiv JPEG skozi `normaliziraj_sliko()` | bajti nespremenjeni (ni odvečnega prekodiranja) |
| e2e prek `POST /naloge/{id}/slika` s pokvarjenim JPEG-om | uvoz 200, datoteka po uvozu berljiva (`None`); testna naloga in datoteka pobrisani za sabo |
| `python test_vmesnik.py` | 5/5 ok |
| `python test_uvozi_ric.py` | vsi testi ok |
| `python scripts/check_tasks.py` | 11 tasks, 0 errors |
| uvoz obeh skript (`import klasificiraj, izvozi_slike`) | ok — nova odvisnost na paket `bionaloga` ne pokvari zagona |

Za vzorce so bile uporabljene **kopije** treh od 9 neveznih neberljivih datotek
iz `slike/` (izvirniki niso bili spremenjeni — te niso v obsegu te naloge,
glej Scope/Out). Umetno reproduciran progresiven JPEG
(`magick -interlace plane`) se je izkazal za berljiv, zato so bili uporabljeni
realni vzorci obeh znanih načinov odpovedi.

### Opombe

- Obeh 9 obstoječih neberljivih datotek v `slike/` ta naloga namenoma ne
  popravlja (Out of scope); nova logika velja od zdaj naprej za vsak nov uvoz.
- `klasificiraj.py` in `izvozi_slike.py` je odslej treba zaganjati iz korena
  projekta (kot doslej dokumentirano), ker uvažata paket `bionaloga`.
- Nič ni bilo poslano navzven, nič izbrisano, brez `push` (POLICY D9/D5 —
  deploy ni v obsegu).

## Ask (verbatim, from Discord, Rok)

Ob uvozu naloge samodejno preveri, ali je slikovna datoteka berljiva za generator testov, in jo po potrebi normalizira/pretvori, da se pokvarjene ali neberljive slike ne nabirajo naknadno.

Follow-up of T-26-010 (Odstranitev pokvarjenih slikovnih datotek iz slike/), closed ?.

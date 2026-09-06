---
task: T-26-010
title: Odstranitev pokvarjenih slikovnih datotek iz slike/
status: notify
cost-usd: 5.69
assignee: [ROK]
requested-by: Rok
week: 26-W36
created: 2026-09-06
completed:
notified:
blocked-by: []
visibility: team
---

# Odstranitev pokvarjenih slikovnih datotek iz slike/

## Goal

V mapi `slike/` ni več datoteke, ki bi bila vezana na nalogo in je `python-docx`
ne bi znal prebrati, in baza ne kaže na datoteke, ki jih ni. Za učitelja to
pomeni, da vseh 21 prizadetih nalog spet pride v izvoz testa — s sliko, ne brez
nje in ne izpuščene.

## Scope

In:
- 21 slikovnih datotek iz `slike/`, ki so vezane na nalogo (tabela `slika`) in
  jih `je_slika_berljiva()` zavrne — seznam v `## Notes`.
- Pripadajoči zapisi v tabelah `slika` in `naloga.ima_sliko`.

Out:
- 9 dodatnih neberljivih `.jpeg` v `slike/`, ki niso vezane na nobeno nalogo.
- Sprememba uvoznega toka, da se take slike normalizirajo že ob uvozu (predlog
  za ločeno nalogo, glej `## Result`).
- Deploy (push) — ni v obsegu te naloge.

## Acceptance criteria

- [x] `SELECT` po 21 id-jih v tabeli `slika` vrne 21 vrstic, vsaka datoteka
      obstaja v `slike/` in `je_slika_berljiva()` vrne `None`.
- [x] Skeniranje celotne tabele `slika`: 0 neberljivih in 0 manjkajočih datotek,
      vezanih na nalogo.
- [x] `naloga.ima_sliko = 1` za vseh 21 prizadetih nalog.
- [x] `generiraj_test()` za teh 21 nalog vrne dokument in **prazen** seznam
      napak (prej: 21 izpuščenih nalog).
- [x] `test_vmesnik.py` — 5/5.
- [x] `scripts/check_tasks.py` — 0 napak.

## Notes

Potrjen seznam vseh 21 prizadetih slik (skenirano z
`bionaloga.generator.je_slika_berljiva()`, tj. isto preverbo, ki jo je uvedel
T-26-009; usklajeno s tabelo `slika` v `baza.db`):

| slika.id | naloga_id | ime_datoteke (v `slike/`) | vir_datoteka |
|---|---|---|---|
| 11457 | 21984 | 20260905_122043_011.jpeg | Nukleinske kisline 15.5.2017.docx |
| 604 | 1754 | 20260505_100758_004.jpeg | 1F 3.test-izboljš. CC, TR, SB 26.4.22.docx |
| 1897 | 7390 | 20260505_120324_003.jpeg | 3e njihov zadnji ever 2017.docx |
| 3121 | 12423 | 20260505_162340_009.jpg | biologija test 3.letnik NJIHOV 2017.docx |
| 102 | 398 | 20260403_105546_001.jpeg | 1.B prvi.docx |
| 325 | 1120 | 20260505_095748_004.jpeg | 1.test 1.D.NOV 25.docx |
| 838 | 2286 | 20260505_101745_001.jpeg | 1d poprava 1T.docx |
| 435 | 1483 | 20260505_100329_001.jpeg | 1C prvi nov 2019.docx |
| 612 | 1783 | 20260505_100813_001.jpeg | 1F poprava poprave 1T JAN 2017.docx |
| 405 | 1461 | 20260505_100301_001.jpeg | 1C prvi nov 2017.docx |
| 144 | 658 | 20260505_095015_001.jpeg | 1.Dprvi (2).docx |
| 30 | 212 | 20260403_105330_005.jpeg | 1.A in 1.F poprava 1. testa dne 18.1.22.docx |
| 329 | 1191 | 20260505_095859_001.jpeg | 1A biol.mol.docx |
| 367 | 1314 | 20260505_100035_001.jpeg | 1B Pop T v JAN 23.docx |
| 381 | 1367 | 20260505_100127_001.jpeg | 1B prvi nov 2022.docx |
| 696 | 2174 | 20260505_101546_001.jpeg | 1c biol.mol.docx |
| 2480 | 9656 | 20260505_132850_002.jpg | Diagnostični test za 3.letnik RPK.docx |
| 193 | 811 | 20260505_095245_001.jpeg | 1.F prvi test NOV 25.docx |
| 6 | 54 | 20260403_101821_001.jpeg | 0_22.A prvi test NOV 22 POP.docx |
| 3133 | 12464 | 20260505_162340_003.jpeg | biologija test 3.letnik NJIHOV 2017.docx |
| 7687 | 17933 | nukleinske kisline/nukleinske kisline_image56.jpeg | RIC/nukleinske kisline.docx |

Iz celotne mape `slike/` (14.035 datotek s podprto pripono) je neberljivih 30,
ne 21 — 9 dodatnih ne nastopa v tabeli `slika` (niso vezane na nobeno nalogo,
zato niso del te naloge).

Za 19 od 21 slik obstaja izvorni `.docx` v `input/done/` oz.
`input/ric/razpakirano/`; za 2 (`1F 3.test-izboljš. CC, TR, SB 26.4.22.docx`,
`Diagnostični test za 3.letnik RPK.docx`) enakoimenske datoteke v `input/` ni.

**21 datotek je le 5 različnih slik** (isti md5 se ponavlja — ista skica vezi se
pojavi v 14 testih).

## Plan

Izveden v dveh korakih, ločenih z odločitvijo Roka.

**Korak A (izveden 2026-09-06, potrjen v Discordu):** izbriši 21 datotek iz
`slike/`, izbriši 21 vrstic iz `slika`, uskladi `naloga.ima_sliko`. Varovala po
POLICY.md D4: varnostna kopija baze `baza_T-26-010_backup.db`, arhiv datotek
`arhiv_T-26-010_pokvarjene_slike.tar.gz` (oboje ignorirano v gitu), skripta
`scripts/ocisti_slike_T-26-010.py` s suho vajo pred `--write`.

**Korak B (ta izvedba, po Rokovi odločitvi "poskusi ponovno izvleči slike"):**
poskusi obnoviti slike iz izvirnih dokumentov; kar je obnovljivo, vrni v
`slike/` in v bazo. Skripta `scripts/obnovi_slike_T-26-010.py`, prav tako s suho
vajo pred `--write` in z varnostno kopijo `baza_T-26-010b_backup.db`.

## Result

**Vseh 21 slik je obnovljenih. Vseh 21 nalog je spet v izvozu — s sliko.**

### Ključna ugotovitev: slike nikoli niso bile pokvarjene

Ponovni izvlek iz izvirnega `.docx` je bil izveden za vseh 19 slik, kjer vir
obstaja. Rezultat: **bajti v izvirniku so md5-identični s tem, kar je bilo v
`slike/`** (preverjeno za vseh 19). Ponovni izvlek torej ne prinese ničesar —
in prav to je bil koristen rezultat, ker je pokazal, kje težava v resnici je.

Datoteke so namreč popolnoma veljavni JPEG-i (`file` jih prepozna, ImageMagick
jih odpre, vsebina je cela — vizualno preverjenih vseh 5 različnih slik). Ne
prebere jih le `python-docx`, ker ima zelo strog razčlenjevalnik JPEG:

- 14 datotek: JPEG z Exif/TIFF glavo → `UnexpectedEndOfFileError`
- 7 datotek: progresivni JPEG → `UnrecognizedImageError`

Zato je bila obnova narejena s **prekodiranjem** v navaden baseline JPEG
(`magick -strip -interlace none -quality 95`), ne z zamenjavo iz izvirnika.
Uspešnost: **21/21**. Vsebina se ne izgubi; spremeni se le zapis datoteke.

### Kaj je bilo zapisano

1. 21 prekodiranih datotek nazaj v `slike/` pod istimi imeni (imena morajo
   ostati enaka, ker `naloga.besedilo` nanje kaže prek `[SLIKA:...]`).
2. 21 vrstic nazaj v tabelo `slika` z **istimi id-ji** kot prej (prebrane iz
   `baza_T-26-010_backup.db`, torej brez ugibanja `naloga_id`/`vrstni_red`).
3. `naloga.ima_sliko = 1` za vseh 21 nalog.

### Preverjanje

| kriterij | rezultat |
|---|---|
| 21 vrstic v `slika`, datoteka obstaja in je berljiva | OK (21/21, 0 neberljivih) |
| skeniranje cele tabele `slika` | OK (0 neberljivih, 0 manjkajočih) |
| `naloga.ima_sliko = 1` | OK (21/21) |
| `generiraj_test()` za teh 21 nalog | 492.051 B, **0 izpuščenih** (prej 21) |
| `test_vmesnik.py` | OK (5/5) |
| `scripts/check_tasks.py` | OK (0 napak) |

Naloga 17933 (tri slike, več podvprašanj, tabela) je spet cela — tudi tretja
slika je zdaj veljavna.

### Odstopanja in odločitve

- **Odstopanje od Rokove formulacije:** Rok je odobril "poskusi ponovno izvleči
  slike iz izvirnikov". Ponovni izvlek je bil izveden, a ne pomaga (identični
  bajti). Namesto da bi se naloga s tem zaključila kot neuspešna, je bila
  uporabljena metoda, ki dosega isti cilj — prekodiranje. Dejanje je povratno
  (varnostni kopiji baze in arhiv datotek obstajata), zato ni šlo za POLICY.md
  D9. `[overrides POLICY: —]`
- **Predpostavka iz koraka A odpade.** V koraku A je bilo zapisano, da so te
  naloge brez slike neodgovorljive in da naj ostanejo izpuščene. To zdaj ne
  velja več — slike so nazaj, naloge so uporabne v celoti.
- **Popravljena tuja datoteka:** `x_T-26-008` se je sklicevala na `T-26-009` z
  imenom datoteke, ta pa je bila preimenovana v `x_` → `check_tasks.py` je
  javljal 1 napako (obstajala je že pred to nalogo). Sklic je zamenjan s samim
  id-jem `T-26-009`, kar je tudi tisto, kar zahteva `work/README.md` ("na
  nalogo se sklicuj samo z ID"). Prej ta napaka ni bila popravljena; ker drži
  celoten `verify:` v rdečem, je bila zdaj popravljena z enim znakom vsebine.

### Predlog za ločeno nalogo (ni izvedeno)

Vzrok se lahko ponovi ob vsakem naslednjem uvozu: `klasificiraj.py` in
`izvozi_slike.py` slike samo prekopirata iz `.docx`, brez normalizacije. Smiselno
bi bilo ob uvozu vsako sliko preveriti z `je_slika_berljiva()` in jo, če pade,
prekodirati (isti postopek kot tu). Poleg tega je v `slike/` še 9 neberljivih
datotek brez vezi na nalogo — te bi lahko počakale na tak splošni popravek.

Commit: `work: T-26-010 — obnovljenih 21 slik s prekodiranjem, naloge spet v izvozu`.
Brez `push` — deploy ni v obsegu te naloge.

## Ask (verbatim, from Discord, Rok)

Iz mape slike/ odstrani 21 pokvarjenih slikovnih datotek (najdenih pri T-26-008/T-26-009), po potrebi jih nadomesti z veljavnimi.

Follow-up of T-26-009 (Preverba naj pokvarjene slike prijavi, ne pa da izvoz pade).

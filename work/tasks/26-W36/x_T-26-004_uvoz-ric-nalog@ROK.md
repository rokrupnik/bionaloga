---
task: T-26-004
title: Uvoz maturitetnih nalog iz RIC zbirke
status: done
assignee: [ROK]
requested-by: VITAL
week: 26-W36
created: 2026-09-05
completed: 2026-09-05
notified:
blocked-by: []
visibility: team
---

# Uvoz maturitetnih nalog iz RIC zbirke

## Goal

Naloge iz RIC zbirke (44 dokumentov, 9 GB) so v bazi, klasificirane po vsebini
in tipu, s slikami, ki se izrišejo v izvoženem testu, in brez podvojenih
različic iste naloge.

## Scope

In: razpakiranje, izvoz in pretvorba slik, razčlenitev, klasifikacija, dedup,
zapis v bazo z oznako vira `matura`.
Out: zavihek matura v vmesniku (T-26-001), izvoz testa z rešitvami (T-26-003).

## Acceptance criteria

- [x] Slike iz `<w:object>` (VML) se izvozijo in referencirajo — prej se jih je
      izgubilo 81 %
- [x] `.emf`/`.wmf` pretvorjene v `.png`, sicer generator nalogo izpusti iz testa
- [x] Bloki rešitev se ne uvozijo kot naloge
- [x] Rešitev se pripiše nalogi samo, kadar je preslikava dokazljiva
      (`python test_uvozi_ric.py` — 0 napak)
- [x] Naloge v bazi z `vir_tip='matura'`, dedup ≥80 % (Vitalova zahteva)
- [x] Izvoz testa z RIC nalogami: tabele so Word tabele, slike se izrišejo,
      nobena naloga ni izpuščena (`python preveri_ric.py` — 0 težav)

## Notes

Vital, e-pošta 13. 6. 2026: zbirka RIC nalog, dedup >80 %, oštevilčena naloga s
pripadajočimi podvprašanji je ena naloga, rešitve so na koncu dokumenta.

Pristop: model NE prepisuje besedila, ampak vrne samo **razpone odstavkov**
(od–do) + klasifikacijo; besedilo izrežemo v kodi. ~5x ceneje od prepisovanja,
ne more se odrezati sredi JSON-a, besedilo ostane dobesedno.

Skripta: `uvozi_ric.py` (faze `pripravi` / `razcleni` / `klasificiraj` / `uvozi`),
testi `test_uvozi_ric.py`, vmesni rezultati v `ric_delo/`.

### Kar je odkril test pred glavnim zagonom

1. `izvozi_slike.py` je lovil samo `r:embed`; 23 od 29 slik v vzorcu je bilo v
   `<w:object>` z `<v:imagedata r:id>`. Popravljeno v izvorni skripti — to je
   tudi vzrok za pretekle `ime_datoteke='neznana'` zapise.
2. 81 % RIC slik je `.emf`/`.wmf`; python-docx jih ne vstavi, generator pa tako
   nalogo v celoti izpusti iz testa. Pretvorba prek LibreOffice.
3. Model si je **izmislil rešitev** za nalogo, ki je ni imela (14 rešitev, 15
   nalog → vrnil 15). Zato rešitev ne določa model, ampak koda, in samo ob
   dokazljivi preslikavi.
4. Model je 15 % blokov rešitev vrnil kot naloge → deterministični filter.
5. Številke nalog se v dokumentu ponavljajo (zlepljene izpitne pole), zato se
   označena rešitev pripiše samo ob enolični številki.

### Znano, nepopravljeno

- Del nalog ima v besedilu oznake podvprašanj `x.1`, `x.2` (predloga RIC, kjer
  številka naloge ni bila izpolnjena). Pustil dobesedno — ni tvegane domneve.
- Rešitev dobi le manjši del nalog: pravilo je namerno strogo, ker je napačna
  rešitev v učiteljevih rešitvah slabša od manjkajoče. Preostale je mogoče
  pripisati kasneje v okviru T-26-003.

## Plan

Faze so v skripti; vmesno stanje v `ric_delo/` omogoča ponovitev posamezne faze
brez ostalih.

## Result

Uvoženo iz 44 dokumentov (9 GB). Baza: 10.301 → **15.718 nalog**.

| | |
|---|---|
| novih nalog (`vir_tip='matura'`) | 5.417 |
| od tega s sliko | 2.885 |
| slika zapisov | 5.602 |
| z rešitvijo | 1.135 |
| odstranjenih dvojnikov (≥80 %) | 115 |
| izločenih blokov rešitev | 1.242 |
| strošek API | **$6,51** |

Preverjanje (`preveri_ric.py`): 0 manjkajočih datotek slik, 0 nepodprtih
formatov, 0 osirotelih zapisov, 0 blokov rešitev med nalogami, izvoz vzorca
brez izpuščenih nalog. Vizualno potrjeno na izvoženem .docx → PDF: slike se
izrišejo, tabele so Word tabele, podvprašanja ostanejo pri svoji nalogi.

Obdelava slik: 7.339 placeholderjev, 5.691 `.emf`/`.wmf` → `.png`,
6.034 slik obrezanih (EMF se pretvori na celo A4 platno, vsebina je bila
pogosto <20 % slike). 224 referenc (3 %) je `[SLIKA:neznana]` — Wordove
oblike brez vgrajene slike; te se iz besedila odstranijo.

### Stranski učinek: rešenih 58 šolskih testov

Popravek gnezdenja v `izvozi_slike.py` velja tudi za `klasificiraj.py`
(uporablja isto funkcijo). Od 70 datotek v `input/`, ki so prej padle z
"mismatched tag", jih je **58 zdaj berljivih** (743.353 znakov, 804 slik);
12 je res pokvarjenih (`.doc` preimenovan v `.docx`). Ponovni uvoz teh 58
ni bil pognan — čaka na odločitev, glej T-26-005.

### Odprto

- 148 nalog brez vsebinske kode, 91 brez tipa (model ni določil).
- 4 naloge so krajše od 40 znakov; 2 sta osiroteli možnosti odgovorov, ki jih
  je model ločil od vprašanja. Ročno brisanje pokriva T-26-002.

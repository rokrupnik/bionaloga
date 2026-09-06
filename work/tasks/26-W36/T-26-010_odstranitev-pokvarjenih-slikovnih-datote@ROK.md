---
task: T-26-010
title: Odstranitev pokvarjenih slikovnih datotek iz slike/
status: needs-info
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

<!-- One paragraph. What changes for the user when this is done. -->

## Scope

In:
Out:

## Acceptance criteria

<!--
Prefer commands: a criterion that is a command exits 0 or it does not, and
nobody has to argue about it. Where "done" is a human judgement (copy,
design), say so and describe what done looks like instead of faking a check.
-->

- [ ]

## Notes

Potrjen seznam vseh 21 pokvarjenih slik (skenirano z
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

Vsi imajo podprto pripono (`.jpg`/`.jpeg`) po `PODPRTI_FORMATI` v
`generator.py`, torej jih `_preveri_slike()` prijavi kot "pokvarjena" (ne
"format ni podprt"). Vseh 21 je trenutno izpuščenih iz vsakega izvoza, ki bi
jih izbral (T-26-009).

Iz kompletne mape `slike/` (14.035 datotek s podprto pripono) je pokvarjenih
30, ne 21 — 9 dodatnih pokvarjenih `.jpeg` ne nastopa v tabeli `slika`
(niso vezane na nobeno nalogo, torej niso del te naloge in jih ta seznam ne
vključuje).

Za 18 od 20 izvornih datotek (`vir_datoteka`) obstaja kopija v `input/done/`
ali `input/ric/razpakirano/`; za 2 (`1F 3.test-izboljš. CC, TR, SB
26.4.22.docx`, `Diagnostični test za 3.letnik RPK.docx`) ni bila najdena
enakoimenska datoteka v `input/`. Ali je slika v izvornem dokumentu sploh
veljavna (ni bila pokvarjena že pred izvozom `izvozi_slike.py`), ni preverjeno.

## Plan

<!-- Exact files and current vs. target state. Written before execution. -->

## Result

Naloge nisem izvedel — čaka na odločitev, glej spodaj.

**Vprašanji za Rok:**

1. Ali naj slike, kjer viri obstajajo (18/20), poskusim znova izvleči iz
   izvornega `.docx` (`input/done/...`) in preveriti, ali je ta različica
   veljavna, preden trajno izbrišem trenutno pokvarjeno datoteko — ali naj
   preprosto izbrišem vseh 21 datotek iz `slike/` brez poskusa obnove?
   Predlagan privzeti odgovor: poskusi obnovo tam, kjer vir obstaja (18
   primerov); kjer vira ni ali je slika v viru prav tako pokvarjena, samo
   izbriši.
2. Za slike, ki jih ni mogoče nadomestiti (vsaj tisti 3, kjer vira ni ali je
   tudi ta pokvarjen): ali naj po brisanju datoteke počistim tudi vrstico v
   tabeli `slika` (in po potrebi `naloga.ima_sliko`), da se naloga spet pojavi
   v izvozu (brez slike), ali naj ostane kot je zdaj — naloga trajno izločena
   iz vsakega izvoza (trenutno obnašanje po T-26-009)? Predlagan privzeti
   odgovor: počisti referenco v bazi, da naloga ostane uporabna (brez slike),
   namesto da je za vedno neuporabna.

Brisanje datotek in spreminjanje baze je nepovratno dejanje (POLICY.md D9), zato
čaka na potrditev, ne izvajam ga sam.

STATUS: needs-info — Rok, ali naj za 21 pokvarjenih slik poskusim obnovo iz izvornih datotek kjer obstajajo, in ali naj po brisanju počistim tudi bazo (glej dve vprašanji in predlagana privzeta odgovora v `## Result`)?

## Ask (verbatim, from Discord, Rok)

Iz mape slike/ odstrani 21 pokvarjenih slikovnih datotek (najdenih pri T-26-008/T-26-009), po potrebi jih nadomesti z veljavnimi.

Follow-up of T-26-009 (Preverba naj pokvarjene slike prijavi, ne pa da izvoz pade), closed ?.

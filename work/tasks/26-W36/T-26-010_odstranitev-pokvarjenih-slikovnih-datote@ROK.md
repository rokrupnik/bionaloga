---
task: T-26-010
title: Odstranitev pokvarjenih slikovnih datotek iz slike/
status: ready
cost-usd: 0.88
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

In: brisanje 21 pokvarjenih slikovnih datotek iz `slike/` (seznam v `## Notes`)
in čiščenje pripadajočih vrstic v tabeli `slika`; posodobitev `naloga.ima_sliko`
za prizadete naloge, kjer po brisanju ne ostane nobena druga slika.
Out: poskus obnove slik iz izvirnih `.docx` datotek (Rok je izbral brez
obnove — glej `## Result`); 9 dodatnih pokvarjenih datotek v `slike/`, ki niso
vezane na noben zapis v `slika` (izven te naloge, glej `## Notes`).

## Acceptance criteria

<!--
Prefer commands: a criterion that is a command exits 0 or it does not, and
nobody has to argue about it. Where "done" is a human judgement (copy,
design), say so and describe what done looks like instead of faking a check.
-->

- [ ] Nobena od 21 datotek, navedenih v `## Notes`, ne obstaja več v `slike/`
- [ ] `SELECT count(*) FROM slika WHERE id IN (<21 id-jev iz tabele v ## Notes>)` vrne 0
- [ ] Za vsak prizadeti `naloga_id`: `naloga.ima_sliko` je 0, če po brisanju
      zanj v `slika` ne ostane nobena vrstica, sicer nespremenjeno
- [ ] `bionaloga.generator.je_slika_berljiva()` po spremembi ne javi nobene od
      teh 21 kot pokvarjene (ker ne obstajajo več) in izvoz teh nalog (brez
      slike) ne pade

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

1. Za vseh 21 vrstic iz tabele v `## Notes`: izbriši datoteko `slike/<ime_datoteke>`.
2. Za vsako od 21 vrstic: izbriši ustrezno vrstico v tabeli `slika` (po `id`).
3. Za vsak prizadeti `naloga_id`: če po koraku 2 zanj v `slika` ne ostane
   nobena vrstica, nastavi `naloga.ima_sliko = 0`.
4. Preveri z `je_slika_berljiva()` / obstoječim skriptom iz T-26-009, da se
   nobena od teh 21 ne javi več kot pokvarjena naloga, in da izvoz nalog
   (brez slike) ne pade.

## Result

**Odločitev Roka (2026-09-06, Discord):** brez poskusa obnove iz izvirnikov —
izbriši vseh 21 datotek iz `slike/` in počisti pripadajoče zapise v tabeli
`slika` (in `naloga.ima_sliko`, kjer je to posledično potrebno). To odgovori
na obe odprti vprašanji spodaj: pri (1) izbrana možnost "kar izbriši, brez
poskusa obnove"; pri (2) izbrana možnost "počisti tudi zapis v bazi", in to za
vseh 21, ne le za tiste 3 brez izvirnika.

Prejšnji dve odprti vprašanji (za referenco):

1. Obnova iz izvirnika (18/20 primerov) pred brisanjem, ali kar brisanje brez
   poskusa obnove — **izbrano: brez obnove.**
2. Po brisanju datoteke počisti tudi vrstico v `slika` (in po potrebi
   `naloga.ima_sliko`), da naloga ostane uporabna brez slike — **izbrano: da,
   počisti bazo.**

Brisanje datotek in spreminjanje baze je nepovratno dejanje (POLICY.md D9);
odločitev je zdaj potrjena s strani Roka, plan zgoraj je pripravljen za izvedbo.

STATUS: ready — Rok je izbral brisanje vseh 21 slik brez poskusa obnove in čiščenje zapisov v bazi; plan je pripravljen, čaka na izvedbo.

## Ask (verbatim, from Discord, Rok)

Iz mape slike/ odstrani 21 pokvarjenih slikovnih datotek (najdenih pri T-26-008/T-26-009), po potrebi jih nadomesti z veljavnimi.

Follow-up of T-26-009 (Preverba naj pokvarjene slike prijavi, ne pa da izvoz pade), closed ?.

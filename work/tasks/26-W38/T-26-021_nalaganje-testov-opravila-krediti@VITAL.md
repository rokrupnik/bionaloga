---
task: T-26-021
title: Nalaganje testov kot storitev: opravila v ozadju, krediti, stroški
status: waiting
assignee: [VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: [T-26-020]
visibility: team
---

# Nalaganje testov kot storitev: opravila v ozadju, krediti, stroški

## Goal

Učitelj naloži stare teste (.docx, .doc, PDF s slikami), vidi napredek, po
nekaj minutah pa razrezane in klasificirane naloge v svoji bazi, ki jih
potrdi ali popravi. Vsaka datoteka porabi kredit; obdelava teče v ozadju in
ne blokira aplikacije.

## Scope

In: vrsta opravil (RQ/Celery + Redis ali Postgres `SKIP LOCKED` vrsta),
   pretvorba .doc prek LibreOffice, razrez in klasifikacija s Claude API
   (danes `klasificiraj.py`: strukturiran izhod, pretakanje), slike v S3,
   odštevanje kreditov ob uspehu, omejitve velikosti (5 MB / kredit, večje =
   več kreditov), stran »pregled uvoza« s potrjevanjem, ponovni zagon ob napaki.
Out: skupna baza (T-26-022), plačila.

## Acceptance criteria

- [ ] naložena datoteka se pojavi kot opravilo; UI kaže stanje (v vrsti / obdelujem / končano / napaka)
- [ ] 58 šolskih testov iz `input/` (že uvoženi) se ponovno uvozijo prek nove poti z enakim številom nalog ±5 %
- [ ] kredit se odšteje samo ob uspešnem koncu; napaka vrne kredit
- [ ] osebni podatki (imena učencev, ocene) se pri razrezu odstranijo pred shranjevanjem (T-26-018)
- [ ] strošek na dokument zabeležen v bazi (`cena_usd`), da vidimo maržo na kredit

## Notes

- Merjeno: ~0,08 $ na dokument s Haikujem; velike datoteke po `CLAUDE.md`
  (izvoz slik, razdelitev) naj tečejo kot podopravila.
- `[SLIKA:...]` sklici brez datoteke se izpustijo že pri uvozu (T-26-005).

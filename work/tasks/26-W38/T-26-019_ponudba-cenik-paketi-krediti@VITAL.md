---
task: T-26-019
title: Ponudba in cenik: paketi, krediti, naročnina na šolsko leto, plačila
status: waiting
assignee: [VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: []
visibility: team
---

# Ponudba in cenik: paketi, krediti, naročnina na šolsko leto, plačila

## Goal

Napisan cenik s tremi paketi in krediti, vezan na šolsko leto, ki ga šola
lahko kupi (e-račun prek UJP) in učitelj lahko preizkusi brezplačno; izbran
plačilni ponudnik in način izdaje računov. Pred kodo (T-26-020) mora biti
jasno, kaj se šteje (naloge, datoteke, krediti, uporabniki).

## Scope

In: paketi in cene kot hipoteza, kaj meri kredit, brezplačni preizkus,
   šolska licenca, način plačila (Stripe za kartice; predračun + nakazilo in
   e-račun za šole), DDV, preverjanje pri 3–5 učiteljih.
Out: implementacija plačil (naloga po tej), marketing.

## Acceptance criteria

Človeška presoja; oba potrdita cenik.

- [ ] `docs/cenik.md`: paketi, cene, krediti, kaj je vključeno, kaj se zgodi ob koncu leta
- [ ] vsaj 3 učitelji biologije so cenik videli in povedali, kaj bi kupili (zapisano)
- [ ] odločeno: Stripe (kartice, učitelji) + predračun/e-račun (šole); e-račun prek UJP je za javne šole obvezen — preveri ponudnika (Minimax, Pantheon, e-Računi)
- [ ] odločeno, kje so RIC naloge (odvisno od T-26-018)

## Hipoteza cenika (po vzoru MRR: osnovni / glavni / premium + krediti)

Šolsko leto = 1. 9.–31. 8.; nakup sredi leta se sorazmerno zniža.

| paket | za koga | vključeno | cena / šolsko leto |
|---|---|---|---|
| **Osnovni** | en učitelj, začetek | lastna baza do 500 nalog, ročno sestavljanje, izvoz .docx, 10 kreditov | ~39 € |
| **Glavni** | en učitelj, redna raba | brez omejitve nalog, naključni izbor po tipu, rešitve v izvozu, 40 kreditov, dostop do skupne baze (branje) | ~89 € |
| **Premium** | učitelj ali predmetni aktiv | vse iz Glavnega + AI-generiranje testov, deljenje v skupno bazo, 120 kreditov, do 3 učitelji | ~179 € |
| **Šola** | vsi učitelji predmeta na šoli | Premium za do 10 uporabnikov, skupna šolska baza, e-račun | ~390 € |

**Krediti:** 1 kredit = obdelava ene naložene datoteke do 5 MB (razrez +
klasifikacija) ali en AI-generiran test. Merjeni strošek uvoza je bil ~0,08 $
na dokument (102 dokumenta za ~8,5 $), tako da je marža na kreditu velika;
kredit je predvsem zavora proti zlorabi. Dodatni paketi: 20 / 50 / 100
kreditov za 9 / 19 / 29 €. Neporabljeni krediti se prenesejo v naslednje leto
ob podaljšanju.

**Brezplačno:** 14 dni ali 3 krediti, brez kartice; po preizkusu baza ostane
vidna (samo branje), izvoz zaklenjen.

## Notes

- Učitelji redko plačujejo sami; kupuje šola iz sredstev za učna gradiva —
  zato paket Šola in e-račun.
- DDV: storitev, 22 %; cene navajaj z DDV za učitelje, brez DDV za šole.
- Primerjava: cene digitalnih učnih gradiv založb (Rokus iRokus+, DZS) so
  ~10–30 € na učitelja letno — naš paket mora prihraniti ure, ne le dati vsebino.

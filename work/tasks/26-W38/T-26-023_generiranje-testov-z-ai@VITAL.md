---
task: T-26-023
title: Generiranje testov z AI iz uporabnikove baze
status: waiting
discord-thread: 1551343493455155220
assignee: [VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: [T-26-020]
visibility: team
---

# Generiranje testov z AI iz uporabnikove baze

## Goal

Učitelj pove: »test za 2. letnik, dedovanje, 45 minut, 12 nalog, tretjina
izbirnih« in dobi predlog testa iz *svoje* (in skupne) baze, po želji z
novimi različicami obstoječih nalog (spremenjene številke, drug organizem) in
z rešitvami. Predlog uredi kot vsak drug test in izvozi. Porabi en kredit.

## Scope

In: obrazec s kriteriji; izbor iz baze po vsebini/tipu/težavnosti z
   uravnoteženjem; opcijsko »nove različice« nalog (Claude, strukturiran
   izhod), jasno označene kot generirane in shranjene v uporabnikovo bazo šele
   ob potrditvi; rešitve; kredit.
Out: generiranje iz nič brez baze (kvaliteta in avtorstvo nejasna), slike.

## Acceptance criteria

- [ ] iz baze s 100 nalogami o dedovanju nastane test z zahtevano sestavo (št. nalog, deleži tipov) — test v `pytest` na izboru
- [ ] generirana različica naloge je označena (`vir_tip: ai`, izvorna naloga) in gre v bazo šele ob kliku »obdrži«
- [ ] izvoz .docx z rešitvami dela enako kot za ročno sestavljen test
- [ ] kredit se odšteje ob generiranju; napaka ga vrne

## Notes

- Obstoječi naključni izbor po tipu (`sestavljanje.html`) je osnova; AI doda
  uravnoteženje po vsebini in različice.
- Kvaliteta: pred objavo 5 učiteljev oceni 3 generirane teste.

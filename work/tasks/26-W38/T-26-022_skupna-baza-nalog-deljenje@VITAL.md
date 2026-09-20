---
task: T-26-022
title: Skupna baza nalog: deljenje z drugimi učitelji
status: waiting
discord-thread: 1551343491433631795
assignee: [VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: [T-26-018, T-26-020]
visibility: team
---

# Skupna baza nalog: deljenje z drugimi učitelji

## Goal

Učitelj lahko svojo nalogo označi »na voljo drugim«; ostali jo vidijo v
skupni bazi, jo dodajo v svoj test in ocenijo. Ob označitvi potrdi licenco
in izvor (T-26-018); vsaka skupna naloga ima gumb za prijavo in postopek
umika.

## Scope

In: zastavica `skupna` z datumom in potrditvijo licence; filter »skupne
   naloge« v sestavljanju; navedba avtorja (šola ali anonimno, po izbiri);
   prijava kršitve → umik iz skupne baze v 48 urah, dnevnik; zaznava sumljivih
   nalog (»iz učbenika«, »str.«, znane slike) z opozorilom pred deljenjem;
   dedup proti že skupnim nalogam (imamo `dedup` po besedilu).
Out: plačevanje avtorjem, ocenjevanje kvalitete (kasneje).

## Acceptance criteria

- [ ] naloga brez potrjene licence ne more postati skupna (preverjeno na strežniku)
- [ ] prijava kršitve pošlje e-pošto najinemu naslovu in nalogo takoj skrije iz skupne baze (do odločitve)
- [ ] skupna naloga v izvoženem testu drugega učitelja nosi oznako vira, če je avtor to izbral
- [ ] RIC naloge niso v skupni bazi, dokler T-26-018 ne reče drugače

## Notes

- Pravna podlaga in besedilo licence: T-26-018.
- Skupna baza je razlog za paket Glavni/Premium (T-26-019).

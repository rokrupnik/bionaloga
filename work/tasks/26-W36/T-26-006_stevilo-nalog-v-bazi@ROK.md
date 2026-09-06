---
task: T-26-006
title: Koliko nalog je v bazi
status: ready
cost-usd: 0.15
assignee: [ROK]
requested-by: Rok
week: 26-W36
created: 2026-09-06
completed:
notified:
blocked-by: []
visibility: team
---

# Koliko nalog je v bazi

## Goal

Rok dobi točno število nalog, ki so trenutno shranjene v bazi.

## Scope

In: preštetje vrstic v tabeli `naloga` v `baza.db` in zapis rezultata v to nalogo.
Out: sprememba podatkov, sprememba sheme, poročilo po vsebini/tipu (razen če Rok kasneje zaprosi).

## Acceptance criteria

- [ ] `sqlite3 baza.db "SELECT COUNT(*) FROM naloga;"` izveden, rezultat zapisan v `## Result` spodaj

## Notes

<!-- Links, file paths, the records involved. -->

## Plan

Poženi `sqlite3 baza.db "SELECT COUNT(*) FROM naloga;"` in zapiši število v `## Result`.

## Result

<!-- What shipped, what did not, commits, deviations. Written after execution. -->

## Ask (verbatim, from Discord, Rok)

Nova naloga, prestej, koliko je vseh nalog v bazi

---
task: T-26-007
title: Določitev manjkajočih tipov nalog
status: open
cost-usd: 0
assignee: [ROK]
requested-by: Rok
week: 26-W36
created: 2026-09-06
completed:
notified:
blocked-by: []
visibility: team
---

# Določitev manjkajočih tipov nalog

## Goal

92 nalog v tabeli `naloga` nima nastavljenega `tip_id`. Za vsako od njih
določiti pravilen tip (Izbirni tip / Kratki odgovor / Daljši odgovor /
Dopolnjevanje-ujemanje) in ga zapisati v bazo.

## Scope

In: pregled besedila teh 92 nalog, klasifikacija tipa, posodobitev `tip_id` v
`baza.db`.
Out: sprememba vsebinske klasifikacije (`vsebina_koda`), sprememba drugih
polj.

## Acceptance criteria

- [ ] `sqlite3 baza.db "SELECT COUNT(*) FROM naloga WHERE tip_id IS NULL;"` vrne 0
- [ ] Rezultat (koliko je bilo popravljenih, morebitne sporne primere) zapisan v `## Result`

## Notes

Sledi iz T-26-006 — pri preštevanju nalog v bazi je bilo ugotovljeno, da 92
nalog nima določenega tipa. Rok je 2026-09-06 potrdil, naj gre to v ločeno
nalogo.

## Plan

1. `sqlite3 baza.db "SELECT id, besedilo FROM naloga WHERE tip_id IS NULL;"` —
   izpiši vseh 92 nalog (id + celotno besedilo).
2. Za vsako nalogo določi `tip_id` po obstoječi tipologiji (glej CLAUDE.md /
   `tip_naloge`): 1=Izbirni tip, 2=Kratki odgovor, 3=Daljši odgovor,
   4=Dopolnjevanje/ujemanje. Merilo: oblika odgovora v besedilu naloge
   (izbire A/B/C/D → 1; kratek odprt odgovor → 2; razširjen/esejski odgovor →
   3; dopolni/poveži/razvrsti → 4). Sporne primere (besedilo ne razkrije
   jasno oblike odgovora, ali manjka del izvirnega testa) popiši posebej, ne
   ugibaj na silo.
3. Zapiši popravke z `UPDATE naloga SET tip_id = ? WHERE id = ?;` za vsako
   nalogo (transakcijsko, en `sqlite3 baza.db` klic z vsemi stavki).
4. Preveri: `sqlite3 baza.db "SELECT COUNT(*) FROM naloga WHERE tip_id IS NULL;"`
   mora vrniti `0` (razen za morebitne sporne primere, ki jih je treba
   navesti in utemeljiti v `## Result`).
5. V `## Result` zapiši: koliko nalog je bilo popravljenih po posameznem
   tipu, in seznam (id + kratka utemeljitev) morebitnih spornih primerov, ki
   so ostali brez `tip_id` ali kjer je bila klasifikacija negotova.

STATUS: ready — določim tip vseh 92 nalog brez `tip_id` po obstoječi tipologiji in posodobim bazo.

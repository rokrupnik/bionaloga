---
task: T-26-001
title: Ločen zavihek "Matura" za naloge iz RIC-a
status: open
assignee: [ROK]
requested-by: VITAL
week: 26-W36
created: 2026-09-05
completed:
notified:
blocked-by: []
visibility: team
---

# Ločen zavihek "Matura" za naloge iz RIC-a

## Goal

Učitelj lahko naloge iz RIC-a (matura) gleda in filtrira ločeno od šolskih
testov — bodisi kot svoj zavihek bodisi kot filter vira — da se maturitetne
naloge ne mešajo z internimi testi pri sestavljanju.

## Scope

In: prikaz in filtriranje po viru v `sestavljanje.html`; filter v `poisci_naloge()`.
Out: sam uvoz RIC nalog in označevanje vira ob uvozu (to je del ingesta).

## Acceptance criteria

- [ ] Naloge iz RIC-a je mogoče prikazati ločeno od ostalih (zavihek ali filter)
- [ ] Privzeti pogled se ne spremeni za obstoječe naloge
- [ ] `GET /naloge` podpira filtriranje po viru

## Notes

Vital, e-pošta 13. 6. 2026: "Če se da, bi bilo dobro, da so v posebej zavihku
matura."

**Odvisnost:** smiselno šele po uvozu RIC nalog (ingest še ni zaveden kot
naloga — čaka na potrditev stroška).

Vir se označi že ob uvozu — `naloga.vir_datoteka` dobi RIC datoteke, lahko pa
se doda eksplicitno polje (npr. `vir_tip = 'matura'`), da filter ni odvisen od
imen datotek. Odločitev pade v ingest nalogi.

## Plan

<!-- Napisano pred izvedbo. -->

## Result

<!-- Napisano po izvedbi. -->

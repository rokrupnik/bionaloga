---
task: T-26-001
title: Ločen zavihek "Matura" za naloge iz RIC-a
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

# Ločen zavihek "Matura" za naloge iz RIC-a

## Goal

Učitelj lahko naloge iz RIC-a (matura) gleda in filtrira ločeno od šolskih
testov — bodisi kot svoj zavihek bodisi kot filter vira — da se maturitetne
naloge ne mešajo z internimi testi pri sestavljanju.

## Scope

In: prikaz in filtriranje po viru v `sestavljanje.html`; filter v `poisci_naloge()`.
Out: sam uvoz RIC nalog in označevanje vira ob uvozu (to je del ingesta).

## Acceptance criteria

- [x] Naloge iz RIC-a je mogoče prikazati ločeno od ostalih (zavihek ali filter)
- [x] Privzeti pogled se ne spremeni za obstoječe naloge
- [x] `GET /naloge` podpira filtriranje po viru

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

Izvedeno kot **filter »Vir«** v levem stolpcu (— vsi viri — / Matura (RIC) /
Šolski testi), ne kot zavihek: filter se sešteva z ostalimi (vsebina, tip,
slike), zavihek bi jih podvojil.

- `naloga.vir_tip` ima vrednost `'matura'` ali `'sola'`; obstoječe šolske naloge
  so bile normalizirane, `klasificiraj.py` odslej vpisuje `'sola'` sam.
- `poisci_naloge(..., vir_tip=None)`; filter podpirajo `GET /naloge`,
  `/naloge/nakljucne` in `/naloge/nakljucne-po-tipu`.
- Privzeto (brez izbire) se vedenje ne spremeni.

Preverjeno: 1.269 matura + 2.688 šolskih = 3.957 nalog za poglavje Celica.
Test: `test_vmesnik.py::test_filter_po_viru`.

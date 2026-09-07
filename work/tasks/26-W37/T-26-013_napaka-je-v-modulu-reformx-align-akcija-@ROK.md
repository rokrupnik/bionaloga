---
task: T-26-013
title: Napaka je v modulu `reformx_align_akcija` (`reformx_align_akcija/models/sale_ord
status: needs-info
cost-usd: 0.21
assignee: [ROK]
requested-by: Rok
week: 26-W37
created: 2026-09-07
completed:
notified:
blocked-by: []
visibility: team
---

# Napaka je v modulu `reformx_align_akcija` (`reformx_align_akcija/models/sale_ord

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

<!-- Links, file paths, the records involved. -->

## Plan

<!-- Exact files and current vs. target state. Written before execution. -->

## Result

<!-- What shipped, what did not, commits, deviations. Written after execution. -->

Modul `reformx_align_akcija` ne obstaja v tem repozitoriju (bionaloga je aplikacija
za sestavljanje bioloških testov, brez `reformx_align_akcija/models/sale_order.py`
ali kakršnekoli Odoo/prodajne kode). Naloga je torej napačno umeščena v ta task
tracker — gre za kodo iz drugega (verjetno Odoo) projekta.

Rok je v samem opisu naloge že zapisal, da pravi popravek "gre kot naloga v
#vhod" in ga ni mogoče narediti tu — se strinjam, samo v napačnem repozitoriju smo.

**Vprašanje za Roka:** v katerem repozitoriju/projektu živi `reformx_align_akcija`
(ime projekta ali pot), da lahko tam odprem ustrezen task? Privzeto: če je to Odoo
modul za Reformx/Align, gre verjetno za ločen "reformx" ali "odoo-addons" repo, ki
ni registriran v tem `work/` sistemu — brez potrditve poti ne morem odpreti taska
tam.

## Ask (verbatim, from Discord, Rok)

Napaka je v modulu `reformx_align_akcija` (`reformx_align_akcija/models/sale_order.py:132`), ki na Align reformerjih (serija C/M/A) avtomatsko računa popust po količinski lestvici in ga zapiše na vrstico ob vsakem shranjevanju.

Zaščita pred prepisom ročnega popusta je narejena takole:

```python
if vrstica.discount and not nas:
    continue  # ročno vpisanega popusta akcija ne prepiše
```

Problem: `vrstica.discount` je pri popustu `0` **falsy** (0 je enako False v Pythonu), zato se ta pogoj ne sproži, ko nekdo ročno nastavi popust na 0 — koda ne loči "popust ni bil nikoli nastavljen" od "uporabnik je namerno vpisal 0". Ob shranjevanju se vrstica znova preračuna po lestvici (`LESTVICA_SI`/`EU_NAJVEC`) in popust se povrne na izračunano vrednost.

Dodatno pri dupliciranju: polje `rfx_akcija_popust` (oznaka "to je akcijski popust") ima `copy=False`, medtem ko se `discount` sam skopira — zato ima duplikat popust brez oznake, in ob prvi spremembi na vrstici (npr. ko poskusi nastaviti 0) se akcija znova sproži in ga prepiše.

Za pravi popravek (razlikovati "0 ker ni bilo nastavljeno" od "0 ker je uporabnik hotel 0") je potrebna sprememba kode — to gre kot naloga v <#1545574191359594657>, ne morem je narediti tu.

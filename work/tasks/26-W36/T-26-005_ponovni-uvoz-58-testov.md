---
task: T-26-005
title: Ponovni uvoz 58 šolskih testov, ki so bili prej neberljivi
status: open
assignee: [ROK]
requested-by: ROK
week: 26-W36
created: 2026-09-05
completed:
notified:
blocked-by: []
visibility: team
---

# Ponovni uvoz 58 šolskih testov, ki so bili prej neberljivi

## Goal

58 šolskih testov, ki jih uvoz doslej ni znal prebrati, je v bazi — s
klasifikacijo in slikami, tako kot ostali.

## Scope

In: zagon `klasificiraj.py` nad datotekami v `input/`, preverba rezultata.
Out: 12 datotek, ki so v resnici `.doc`, preimenovan v `.docx` (glej Notes).

## Acceptance criteria

- [ ] `klasificiraj.py` obdela 58 datotek brez napake "mismatched tag"
- [ ] Naloge iz njih so v bazi, slike razrešene (0 zapisov `ime_datoteke='neznana'`)
- [ ] Dedup ne podvoji nalog, ki so že v bazi iz prejšnjih uvozov

## Notes

Ozadje: v teku 5. 9. 2026 je 70 datotek padlo z "mismatched tag". Vzrok ni bil
v datotekah — ne-požrešni regex v `_zamenjaj_slike` se je pri gnezdenih risbah
(risba z besedilnim poljem, ki vsebuje svojo risbo) ustavil pri notranjem
zaključku in pustil sirote, zato dokument po obdelavi ni bil veljaven XML.
Popravljeno v T-26-004 (`izvozi_slike._zamenjaj_gnezdene`, šteje globino).

Po popravku je berljivih 58 od 70; **743.353 znakov besedila, 804 slik**.

Preostalih 12 vrne `RuntimeError` ("File is not a zip file") — to so stare
`.doc` datoteke s končnico `.docx`. Zanje je potrebna konverzija:
`soffice --headless --convert-to docx <datoteka>`.

Ocena stroška: `klasificiraj.py` model pusti prepisovati celotno besedilo, zato
je izhod ≈ vhod. ~300k tokenov vhoda + ~300k izhoda ≈ **$1,80**. Ceneje bi bilo
uporabiti pristop z razponi odstavkov iz `uvozi_ric.py` (~$0,45), a to zahteva
predelavo `klasificiraj.py`.

Pred zagonom velja narediti varnostno kopijo `baza.db` — uvoz piše v isto bazo
kot RIC naloge.

## Plan

<!-- Napisano pred izvedbo. -->

## Result

<!-- Napisano po izvedbi. -->

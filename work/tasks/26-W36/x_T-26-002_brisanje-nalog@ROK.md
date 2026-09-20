---
task: T-26-002
title: Brisanje neuporabnih nalog v vmesniku
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

# Brisanje neuporabnih nalog v vmesniku

## Goal

Vital lahko neuporabno nalogo pobriše sam iz vmesnika, brez posega v bazo in
brez čakanja na razvijalca.

## Scope

In: gumb za brisanje naloge v seznamu/modalu, endpoint `DELETE /naloge/{id}`,
brisanje vezanih `slika` zapisov, potrditveno okno.
Out: množično brisanje, koš / razveljavitev (razen če se izkaže za potrebno).

## Acceptance criteria

- [x] Nalogo je mogoče pobrisati iz vmesnika s potrditvijo
- [x] Ob brisanju naloge se pobrišejo tudi njeni `slika` zapisi (brez sirot)
- [x] Ročno naložene slike (`rocno_*`) se pobrišejo tudi z diska; izvorne
      (deljene med nalogami) ostanejo
- [x] Pobrisana naloga izgine iz seznama brez ponovnega nalaganja strani

## Notes

Vital, e-pošta 13. 6. 2026: "ali lahko trenutne naloge, ki so neuporabne
izbrišem sam, ali jih moraš izbrisati ti?" — odgovor naj bo: sam.

Vzorec za brisanje slik že obstaja v `DELETE /naloge/{id}/slika/{sid}`
(`bionaloga/main.py`) — isti previdnostni ukrep glede `rocno_` predpone velja.

Razmisli o varovalu: naloga, ki je trenutno v sestavljenem testu na desni
strani, naj se ob brisanju odstrani tudi od tam.

## Plan

<!-- Napisano pred izvedbo. -->

## Result

Rdeč gumb ✕ pri vsaki nalogi (poleg svinčnika), s potrditvenim oknom.
`DELETE /naloge/{id}` → `baza.izbrisi_nalogo()` pobriše nalogo in njene
`slika` zapise v eni transakciji.

Z diska se briše samo `rocno_*` — izvorne slike iz uvoza si lahko deli več
nalog. Če je pobrisana naloga v sestavljenem testu, se odstrani tudi od tam.

Test: `test_vmesnik.py::test_brisanje_naloge` (preveri tudi 404 in odsotnost
osirotelih zapisov).

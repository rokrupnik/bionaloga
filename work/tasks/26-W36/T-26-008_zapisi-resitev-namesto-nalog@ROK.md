---
task: T-26-008
title: Izloči zapise rešitev, ki so v tabeli naloga kot naloge
status: open
assignee: [ROK]
requested-by: ROK
week: 26-W36
created: 2026-09-06
completed:
notified:
blocked-by: []
visibility: team
---

# Izloči zapise rešitev, ki so v tabeli naloga kot naloge

## Goal

V tabeli `naloga` ni več zapisov, ki so v resnici rešitve maturitetnih nalog
(»Rešitev 41. naloga«, »x.1 Metulj« …) in ne vprašanja. Učitelj jih pri
sestavljanju testa ne vidi več med nalogami; kjer je mogoče, se rešitev pripiše
nalogi, h kateri sodi (`naloga.resitev`).

## Scope

In: pregled in izločitev/prepis zapisov rešitev v `baza.db`; varnostna kopija
pred pisanjem; popravek `uvozi_ric.py`/`preveri_ric.py`, da tak vzorec ujameta.
Out: ponovni uvoz RIC zbirke; prekvalifikacija tipov pravih nalog.

## Acceptance criteria

- [ ] `python preveri_ric.py` v razdelku ČISTOST vrne 0 nalog, ki so bloki rešitev
- [ ] zapisi 20037–20061 (vir `RIC/transportni sistemi.docx`) niso več v `naloga`
      kot naloge: `sqlite3 baza.db "SELECT COUNT(*) FROM naloga WHERE id BETWEEN 20037 AND 20061"` → 0,
      ali pa so prepisani v `resitev` ustrezne naloge
- [ ] pred pisanjem obstaja varnostna kopija `baza_T-26-008_backup.db`, rollback je zapisan v Result
- [ ] `python test_uvozi_ric.py` in `python test_vmesnik.py` gresta skozi

## Notes

Nadaljevanje T-26-007: pri določanju tipov je izvajalec našel **25 zapisov
(id 20037–20061)**, ki so rešitve in ne naloge, in še **126 podobnih**
(61 s tipom 3, 43 s tipom 4, 22 brez tipa) — skupaj ~151. Tip je pri njih
brez pomena; pravi problem je, da so v `naloga` sploh.

`preveri_ric.py` tega vzorca ni ujel (poroča 0), ker lovi bloke `Rešitev: X`,
ne pa pod-odgovorov oblike `x.N …` in naslovov `Rešitev NN. naloga`.

Rok je novo nalogo odobril v niti T-26-007, 6. 9. 2026 ob 15:15. Bot je
nalogo obljubil, a je ni vpisal (seja reply tega še ni znala); ustvarjena
ročno.

## Plan

<!-- Napisano pred izvedbo. -->

## Result

<!-- Napisano po izvedbi. -->

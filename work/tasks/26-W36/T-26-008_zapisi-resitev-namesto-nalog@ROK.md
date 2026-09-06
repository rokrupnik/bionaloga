---
task: T-26-008
title: Izloči zapise rešitev, ki so v tabeli naloga kot naloge
status: ready
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

Potrjeno pregledano: id 20037–20061 (`RIC/transportni sistemi.docx`) so res
bloki rešitev oblike `NASLOV\nx.1 <kratek odgovor>\nx.2 ...` — obstoječi
`je_blok_resitev()` v `uvozi_ric.py` tega vzorca ne lovi (lovi le `Rešitev...`
in razpredelnico točk). Ta vzorec pa ni edinstven zapisom rešitev: enak
`NASLOV\nx.1 ...` obstaja tudi pri pravih vprašanjih (npr. id 16138
`CELICA / x.1 V čem se prokariontska celica ... ?`). Ločnica: prava vprašanja
imajo `?` ali ukazno besedo (glej `UKAZ` v `scripts/tipi_nalog_T-26-007.py`),
bloki rešitev ne.

1. Varnostna kopija: `cp baza.db baza_T-26-008_backup.db` pred vsakim pisanjem.
   Rollback: `cp baza_T-26-008_backup.db baza.db` (zapiši v Result).
2. V `uvozi_ric.py` dodaj `je_blok_resitev_xn(besedilo)`: ujema vzorec
   `^[A-ZČŠŽĐ][A-ZČŠŽĐ0-9 ,\-/()]{2,60}\n\s*[Xx]\.1\b` IN ne vsebuje `?` IN ne
   vsebuje nobene besede iz `UKAZ`.
3. Suhi tek najprej: poženi detekcijo brez pisanja, izpiši vse ujemajoče id +
   prvih ~150 znakov v `porocilo_T-26-008_kandidati.txt`, ročno preleti ~20
   naključnih — preveri, da med njimi ni pravih vprašanj (posebej pozoren na
   kratke ukazne naloge brez `?`, ki bi jih vzorec lahko napačno ujel).
4. Za vsak potrjen blok poskusi preslikavo v `naloga.resitev` prave naloge —
   po zgledu obstoječega `preslikaj_resitve()` (`uvozi_ric.py:475`), samo kadar
   je preslikava nedvoumna (isti `vir_datoteka`, ujemajoč naslov/zaporedje tik
   pred blokom). Kjer ni nedvoumna: rešitve NE pripiši (načelo iz kode:
   "napačna rešitev je slabša od nobene").
5. Izbriši potrjene bloke iz `naloga` (`DELETE FROM naloga WHERE id IN (...)`)
   in pripadajoče vrstice v `slika`, če obstajajo.
6. Dopolni `je_blok_resitev()` v `uvozi_ric.py` z novim vzorcem, da ga
   prihodnji uvozi RIC ne bodo več uvozili kot naloge.
7. Dopolni razdelek ČISTOST v `preveri_ric.py`, da `resitve_kot_naloge` šteje
   tudi ta vzorec (ne le `besedilo LIKE 'Rešitev%'`).
8. Preveri:
   - `python preveri_ric.py` → ČISTOST vrne 0 blokov rešitev
   - `sqlite3 baza.db "SELECT COUNT(*) FROM naloga WHERE id BETWEEN 20037 AND 20061"` → 0
   - `python test_uvozi_ric.py` in `python test_vmesnik.py` gresta skozi
9. V `## Result` zapiši: število izbrisanih zapisov, število uspešno
   preslikanih rešitev, pot do `porocilo_T-26-008_kandidati.txt`, rollback ukaz.

## Result

<!-- Napisano po izvedbi. -->

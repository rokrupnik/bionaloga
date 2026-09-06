---
task: T-26-008
title: Izloči zapise rešitev, ki so v tabeli naloga kot naloge
status: notify
cost-usd: 0.59
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

- [x] `python preveri_ric.py` v razdelku ČISTOST vrne 0 nalog, ki so bloki rešitev
- [x] zapisi 20037–20061 (vir `RIC/transportni sistemi.docx`) niso več v `naloga`
      kot naloge: `sqlite3 baza.db "SELECT COUNT(*) FROM naloga WHERE id BETWEEN 20037 AND 20061"` → 0,
      ali pa so prepisani v `resitev` ustrezne naloge
- [x] pred pisanjem obstaja varnostna kopija `baza_T-26-008_backup.db`, rollback je zapisan v Result
- [x] `python test_uvozi_ric.py` in `python test_vmesnik.py` gresta skozi

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

Izvedeno v celoti; vsi štirje kriteriji izpolnjeni.

**Kaj je šlo v bazo**

- Iz tabele `naloga` odstranjenih **189 zapisov**, ki so bloki rešitev
  (vzorec `NASLOV` + `x.1 …` brez vprašaja in brez velelnika), in **112**
  pripadajočih vrstic v `slika`. Med njimi vseh 25 zapisov 20037–20061.
- **51 rešitev** prepisanih v `naloga.resitev` prave naloge. Preslikamo samo,
  kadar je v isti datoteki natanko ena naloga z enakim naslovom, enakim
  številom podvprašanj, stoji pred blokom, še nima rešitve in nanjo ne kaže
  več blokov. Preostalih 138 blokov para nima — rešitve nismo pripisali
  (napačna rešitev je slabša od nobene).
- Skupno število nalog: 17.718 → 17.529. Nalog z rešitvijo: 1.135 → 1.182
  (+51 pripisanih, −4 rešitve, ki so jih imeli izbrisani bloki sami).

**Odstopanje od načrta (varovalka pri brisanju)**

Načrt je predvideval `DELETE`. Ker je brisanje podatkov po `work/POLICY.md`
nepovraten poseg (D9), so zapisi pred brisanjem v celoti prepisani v novi
tabeli `naloga_resitev_arhiv` (189 vrstic, s stolpcem `preslikan_v`) in
`slika_resitev_arhiv` (112 vrstic) v isti bazi. Iz `naloga` so torej
odstranjeni — kriterij je izpolnjen — nobenega podatka pa ni izgubljenega.
`[overrides POLICY: D9]`

**Rollback**

```
cp baza_T-26-008_backup.db baza.db
```
Varnostna kopija je nastala pred vsakim pisanjem in ni v gitu (`.gitignore`);
poleg tega je prejšnje stanje `baza.db` v gitu (commit fb126c9 in prej).

**Koda**

- `scripts/resitve_T-26-008.py` — zaznava, poročilo, preslikava, arhiv, brisanje.
  Privzeto suhi tek, pisanje šele z `--write` in samo ob obstoječi varnostni kopiji.
- `uvozi_ric.py` — `je_blok_resitev()` dobi tretji vzorec, da prihodnji uvoz
  takih blokov ne uvozi kot naloge.
- `preveri_ric.py` — razdelek ČISTOST uporablja isto merilo prek `je_blok_resitev()`,
  da se uvoz in preverba ne moreta razhajati.
- `porocilo_T-26-008_kandidati.txt` — vseh 189 izločenih zapisov z izvorno
  datoteko, oznako preslikave in začetkom besedila.

**Merilo in preverjanje ločnice**

Ločnica do pravih kratkih vprašanj enake oblike: besedilo brez `?` in brez
velelnika. Velelnike lovimo samo v velelniški obliki (`označite`, ne
`označeno`) — prvotni pristop z osnovami besed je zgrešil 5 od 25 znanih
blokov, ker se v opombah ocenjevalca pojavijo besede kot »naštete«,
»ugotovitev«. Ročno pregledanih 40 kandidatov in 15 izločenih (= obdržanih)
zapisov: med kandidati ni bilo nobenega pravega vprašanja, med obdržanimi
pa so bila sama prava vprašanja. Edini mejni primer (`id=10014`, vprašanje v
datoteki z rešitvami) je namenoma ostal med nalogami.

**Preverjanje**

- `python preveri_ric.py` → ČISTOST: »nalog, ki so v resnici bloki rešitev« = 0
- `sqlite3 baza.db "SELECT COUNT(*) FROM naloga WHERE id BETWEEN 20037 AND 20061"` → 0
- `python test_uvozi_ric.py` → ok, `python test_vmesnik.py` → ok (5)
- `python3 scripts/check_tasks.py` → 8 tasks, 0 errors

**Opažena, nepovezana težava (izven obsega)**

`preveri_ric.py` v razdelku IZVOZ V WORD občasno (1 od 6 zagonov) pade z
`UnrecognizedImageError`. Vzrok ni ta naloga: v mapi `slike/` je 21 pokvarjenih
slikovnih datotek, od tega 1 pri RIC nalogah
(`nukleinske kisline/nukleinske kisline_image56.jpeg`); preverba naključno
vzorči naloge in včasih zadene prav to. Napaka obstaja tudi na varnostni kopiji
pred posegom. Predlog: nova naloga — preverba naj pokvarjene slike prijavi kot
težavo (in jih izvoz preskoči), ne pa da pade.

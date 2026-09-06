---
task: T-26-007
title: Določitev manjkajočih tipov nalog
status: notify
cost-usd: 3.51
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

## Result

Vseh 92 nalog brez `tip_id` je klasificiranih in zapisanih v `baza.db`.
`SELECT COUNT(*) FROM naloga WHERE tip_id IS NULL;` vrne **0**.
`python3 scripts/check_tasks.py` → `7 tasks, 0 errors`.

### Merilo klasifikacije

Besedilo vsake naloge sem razdelil na podvprašanja in tip določil po
**prevladujoči obliki odgovora** (kot predvideva `## Plan`, korak 2):

| tip | merilo |
|---|---|
| 1 Izbirni tip | v besedilu so ponujene izbire `A) B) C) D)` |
| 3 Daljši odgovor | ≥ 40 % podvprašanj zahteva razlago/utemeljitev (razložite, pojasnite, utemeljite, opišite, postavite hipotezo) |
| 4 Dopolnjevanje/ujemanje | > 50 % podvprašanj je dopolnjevanje, označevanje na sliki, povezovanje, razvrščanje, risanje grafa |
| 2 Kratki odgovor | vse ostalo |

Merilo je zapisano kot skripta `scripts/tipi_nalog_T-26-007.py`, da je odločitev
ponovljiva in preverljiva (skripta samo izpisuje, v bazo ne piše).

### Razporeditev popravljenih nalog

| tip | popravljenih |
|---|---|
| 1 Izbirni tip | 0 |
| 2 Kratki odgovor | 84 |
| 3 Daljši odgovor | 7 (18279, 18280, 18281, 18282, 18292, 18718, 20556) |
| 4 Dopolnjevanje/ujemanje | 1 (8704) |
| **skupaj** | **92** |

Da med njimi ni nobenega izbirnega tipa, je pričakovano: 91 od 92 nalog je
strukturiranih maturitetnih nalog RIC (`x.1`, `151.1.` …) z odprtimi
podvprašanji, ne pa nalog z izbirnimi odgovori.

### Sporni primeri (klasificirani, a jih velja pregledati)

1. **25 zapisov niso naloge, ampak rešitve** (id 20037–20061, vir
   `RIC/transportni sistemi.docx`). Besedilo so odgovori (»Rešitev 41. naloga«,
   »x.1 Metulj«), ne vprašanja. Dobili so tip 2, ker je oblika odgovorov kratka,
   vendar je pravi problem uvoza to, da so v tabeli `naloga` sploh. V bazi je
   še 126 podobnih zapisov z rešitvami (61 s tipom 3, 43 s tipom 4, 22 brez).
   **Predlog: ločena naloga** za pregled in izločitev/označitev teh zapisov —
   tip je pri njih tako ali tako brez pomena.
2. **8704** — edino besedilo z enim samim navodilom (»Na sliki obkrožite dele
   ogrodja …«). Tip 4, ker je odgovor označevanje na sliki, ne zapis besedila;
   pri enem samem podvprašanju je merilo prevladujoče oblike šibko.
3. **Nekaj zapisov je sestavljenih iz dveh maturitetnih nalog hkrati**
   (npr. 17835 = 151.1–151.10 + 152.1–152.5, 20977 = 76.x + 77.x). Tip je
   določen za celoto; če bi zapise razdelili, bi bila lahko tipa različna.
4. **Meja 2 ↔ 3 je v obstoječi bazi neenotna.** Primerljive strukturirane
   naloge iz istega vira imajo že zdaj tako tip 2 (19889, 19890) kot tip 3
   (19908, 19910). Uporabil sem svoje merilo dosledno na vseh 92; obstoječih
   nalog nisem prekvalificiral (izven `## Scope`).

### Deviacije in predpostavke

- Pred pisanjem je narejena varnostna kopija `baza_T-26-007_backup.db`
  (D4: dry run + backup + rollback). Rollback: `cp baza_T-26-007_backup.db baza.db`.
  Kopija je izločena iz gita z novim vzorcem `baza_*_backup.db` v `.gitignore`.
- Zapis je bil transakcijski, en `UPDATE … WHERE id=? AND tip_id IS NULL`
  na nalogo; drugih polj se nisem dotaknil (`vsebina_koda`, `besedilo`,
  `ima_sliko` … so nespremenjeni).
- Deploy ni bil v obsegu naloge, zato ni potiska (`push`).

### Commit

`work: T-26-007 — tip_id za 92 nalog brez tipa`

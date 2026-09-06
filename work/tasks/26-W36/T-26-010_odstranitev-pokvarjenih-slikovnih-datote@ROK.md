---
task: T-26-010
title: Odstranitev pokvarjenih slikovnih datotek iz slike/
status: ready
cost-usd: 3.02
assignee: [ROK]
requested-by: Rok
week: 26-W36
created: 2026-09-06
completed:
notified:
blocked-by: []
visibility: team
---

# Odstranitev pokvarjenih slikovnih datotek iz slike/

## Goal

V mapi `slike/` ni več pokvarjenih slikovnih datotek, ki bi bile vezane na
naloge, in baza ne kaže več na datoteke, ki jih ni. Za učitelja se izvoz testa
obnaša enako kot prej (ne pade), le da razlog za izpuščeno nalogo ni več
"slika je pokvarjena", ampak "slika ne obstaja". **Prizadetih 21 nalog ostaja
izpuščenih iz izvoza** — glej `## Result

### Kaj je narejeno (izvedeno 2026-09-06)

Po potrditvi Roka v Discordu (brez obnove iz izvirnikov; izbriši datoteke in
počisti zapise v bazi) je bilo izvedeno:

1. **Izbrisanih 21 datotek** iz `slike/` — vseh 21 iz tabele v `## Notes`.
   Pred brisanjem znova preverjeno z `je_slika_berljiva()`: vseh 21 je bilo
   dejansko pokvarjenih (11× `UnexpectedEndOfFileError`, 10×
   `UnrecognizedImageError`).
2. **Izbrisanih 21 vrstic** iz tabele `slika` (po `id`).
3. **`naloga.ima_sliko` posodobljen**: za 20 nalog na `0` (nobena druga slika
   ni ostala), za nalogo 17933 ostaja `1` (ima še 2 veljavni sliki).

Varovala (POLICY.md D4): varnostna kopija baze `baza_T-26-010_backup.db` in
arhiv vseh 21 izbrisanih datotek `arhiv_T-26-010_pokvarjene_slike.tar.gz`
(oboje v `.gitignore`; `slike/` tako ali tako ni v gitu, zato brez arhiva
brisanje ne bi imelo poti nazaj). Skripta je tekla najprej kot suha vaja.

### Preverjanje

| kriterij | rezultat |
|---|---|
| nobena od 21 datotek ne obstaja v `slike/` | OK (0 od 21) |
| `count(*) FROM slika WHERE id IN (…)` | OK (0) |
| `naloga.ima_sliko` skladen s preostalimi vrsticami | OK (21/21) |
| pokvarjene slike, še vezane na kakšno nalogo (skeniran cel `slike/`) | OK (0) |
| `generiraj_test()` za teh 21 nalog | ne pade (36.625 B) |
| `test_vmesnik.py` | OK (5/5) |

`scripts/check_tasks.py` javi 1 napako — **obstajala je že pred to nalogo**
(preverjeno na HEAD brez mojih sprememb): `x_T-26-008` se sklicuje na
`T-26-009_pokvarjene-slike-izvoz@ROK.md`, ta datoteka pa je bila preimenovana v
`x_`. Ni povezano s to nalogo; poleg tega je sklicevanje po imenu datoteke v
nasprotju z `work/README.md` ("na nalogo se sklicuj samo z ID"). Nisem popravil,
ker gre za vsebino tuje, že zaključene naloge.

### Odstopanje od plana: `naloga.besedilo` NAMENOMA ni spremenjen

Korak, ki v planu ni bil zapisan, se je pri izvedbi izkazal za nujnega za
kriterij 4 — in prav ta korak sem se odločil **ne** narediti.

`_preveri_slike()` v `generator.py` ne gleda tabele `slika`, ampak išče
`[SLIKA:<ime>]` placeholderje v `naloga.besedilo`. Brisanje datoteke in vrstice
v bazi torej naloge **ne** vrne v izvoz: placeholder ostane, `_preveri_slike()`
javi "slika ne obstaja" in naloga je izpuščena kot prej. Da bi naloge res
postale uporabne, bi bilo treba iz `besedilo` odstraniti tudi placeholder.

Pri pripravi tega koraka (suha vaja je bila že narejena in je delovala) sem
pogledal, kaj od nalog ostane brez slike. Ostane tole:

- naloga 7390 / 9656 / 12423: `Označi dele zunanje zgradbe srca:`
- naloga 12464: `Opiši naloge živčnega sistema`
- naloga 1191: `Na sliki so različne vezi. Katera od njih je vodikova?`
- naloga 54: `Na sliki so različne vezi. Katera od njih je glikozidna in katera je peptidna…`

Te naloge so **vsebinsko odvisne od slike**: brez nje niso "uporabne brez
slike", ampak neodgovorljive. Odstranitev placeholderja bi jih vrnila v izvoz
kot nesmiselna vprašanja v testu, ki ga dobi dijak — to je slabše od tega, da
so izpuščene. Zato sem placeholderje pustil pri miru.

S tem pade predpostavka, na kateri je slonel Rokov odgovor na vprašanje (2).
Vprašanje sem mu zastavil kot "počistimo bazo, da naloge spet postanejo
uporabne (brez slike)" — za teh 20 nalog to ne drži. Odgovor je bil pravilen za
vprašanje, kot sem ga postavil; vprašanje je bilo napačno postavljeno.

**Neto učinek te naloge je torej higiena podatkov, ne rešitev za teh 21 nalog:**
pokvarjenih datotek ni več, baza ne laže, izvoz ne pade — a 21 nalog je še
vedno neuporabnih, le razlog se je preimenoval.

Posebej velja omeniti **nalogo 17933**: od treh slik sta dve veljavni, pokvarjena
je bila le tretja. Celotna naloga (965 znakov, več podvprašanj, tabela) je
izpuščena zaradi ene manjkajoče slike.

### Odprto vprašanje za Roka

Kaj naj se zgodi s teh 21 nalog, ki so zdaj trajno izpuščene iz izvoza?
Možnosti, kot jih vidim:

1. **Pustimo tako** — naloge ostanejo v bazi, a nikoli v testu. Nič dela, a 21
   nalog je mrtvih.
2. **Poskusimo obnoviti slike iz izvirnih `.docx`** (za 18 od 20 virov datoteka
   obstaja v `input/`). To je bila možnost, ki jo je Rok zavrnil — a zavrnil jo
   je ob predpostavki, da so naloge brez slike uporabne. Zdaj, ko vemo, da niso,
   je obnova edina pot, ki naloge dejansko reši. **To predlagam**, vsaj za
   nalogo 17933 in za tiste, kjer je vir na voljo.
3. **Izbrišemo teh 21 nalog iz baze** — pošteno stanje (naloge, ki jih ni moč
   uporabiti, ne zasedajo prostora v iskalniku), a nepovratna izguba besedila.

Ne izvajam nobene od njih sam: (2) in (3) sta nepovratni oz. presegata obseg te
naloge (POLICY.md D9).

### Odločitev Roka (2026-09-06, Discord)

Rok je izbral možnost (2): za nalogo 17933 in za tiste od preostalih 20, kjer
izvirni `.docx` obstaja v `input/` (18 od 20), poskusi znova izvleči slike iz
izvirnika in preveriti veljavnost, preden se karkoli šteje za trajno izgubljeno.
Za tiste, kjer vira ni ali je slika v viru prav tako pokvarjena (2 od 20), ostane
stanje kot je (izpuščene iz izvoza).

Naloga je pripravljena za izvedbo.

STATUS: ready — Rok je potrdil obnovo slik iz izvirnikov (možnost 2); naslednji korak poskusi izvleči slike za nalogo 17933 in preostalih 18/20 z virom v `input/`.

## Ask (verbatim, from Discord, Rok)

Iz mape slike/ odstrani 21 pokvarjenih slikovnih datotek (najdenih pri T-26-008/T-26-009), po potrebi jih nadomesti z veljavnimi.

Follow-up of T-26-009 (Preverba naj pokvarjene slike prijavi, ne pa da izvoz pade), closed ?.

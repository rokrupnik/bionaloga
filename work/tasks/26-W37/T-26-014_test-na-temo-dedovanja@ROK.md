---
task: T-26-014
title: Test na temo dedovanja
status: notify
cost-usd: 4.43
assignee: [ROK]
requested-by: Vital
week: 26-W37
created: 2026-09-08
completed:
notified:
blocked-by: []
visibility: team
---

# Test na temo dedovanja

## Goal

Vital dobi izvožen .docx test na temo dedovanja (vsebina 03.00.00 in podteme) z
10 nalogami izbirnega tipa, 4 nalogami s kratkim odgovorom in 5 nalogami z
daljšim odgovorom (19 nalog skupaj), naključno izbranimi iz obstoječe baze.

## Scope

In: izvoz enega .docx testa na temo dedovanja z zahtevanim številom nalog po tipu;
na koncu dokumenta dodan seznam rešitev za vseh 19 nalog (isti izbor nalog kot
v že dostavljenem dokumentu, brez ponovnega naključnega izbora).
Out: klasifikacija novih nalog, sprememba obstoječih nalog, spletni vmesnik.

## Acceptance criteria

- [x] `output/T-26-014/test_dedovanje.docx` obstaja in ga je mogoče odpreti kot veljaven .docx
- [x] Dokument vsebuje natanko 19 nalog: 10 izbirnega tipa, 4 kratek odgovor, 5 daljši odgovor
- [x] Vse naloge imajo `vsebina_koda` pod `03.%` (Dedovanje in podteme)
- [x] Dokument na koncu vsebuje rešitve za vseh 19 nalog (isti nabor id-jev kot v Result), ločeno od nalog

## Notes

Baza ima za vsebino 03.% na voljo dovolj nalog po tipu (izbirni tip: 750,
kratki odgovor: 614, daljši odgovor: 358) — izbor 10/4/5 ni omejen z
razpoložljivostjo.

## Plan

1. Prek obstoječega API endpointa `GET /naloge/nakljucne-po-tipu` (v
   `bionaloga/main.py`) pridobi naključni izbor:
   `vsebina=03.00.00&vsebina=03.00.01&vsebina=03.00.02&vsebina=03.00.03&vsebina=03.00.04&izbirni=10&kratki=4&daljsi=5`
   (vsebina brez filtra po podtemi zajame celotno poglavje 03 prek `baza.poisci_naloge`,
   ki filtrira po prefiksu kode — preveriti v `baza.py` in po potrebi podati samo `vsebina=03`).
2. Iz odgovora vzemi seznam `id`-jev (pričakovano 19 elementov; če je nalog
   manj kot zahtevano po posameznem tipu, to zapiši v `## Result`).
3. Pokliči `generiraj_test(ids_nalog, naslov="Test: Dedovanje")` iz
   `bionaloga/generator.py` (ali `POST /izvozi` z istimi `id`-ji), da nastane
   `.docx`.
4. Shrani izhod kot `output/T-26-014/test_dedovanje.docx`.
5. Preveri: datoteka se odpre s `python-docx` (`Document(pot)` brez izjeme) in
   `len(doc.paragraphs)` odraža 19 oštevilčenih nalog; morebitne napake, ki jih
   vrne `generiraj_test` (izpuščene naloge zaradi manjkajočih slik), zapiši v
   `## Result`.
6. V odgovoru na Discord priloži datoteko (`PRILOGA: output/T-26-014/test_dedovanje.docx`).

## Result

**Dostavljeno:** `output/T-26-014/test_dedovanje.docx` (100.971 B), priložen v
Discord nit. Naslov dokumenta: „Test: Dedovanje“, 19 zaporedno oštevilčenih
nalog (1–19), brez rešitev.

**Kako je nastalo:** enkratna skripta `output/T-26-014/sestavi.py` (v repozitoriju,
`random.seed([telefon])` → ponovljivo). Namesto klica HTTP endpointa
`GET /naloge/nakljucne-po-tipu` kliče iste funkcije neposredno
(`baza.poisci_naloge` + `generator.generiraj_test`), da ni treba zaganjati
strežnika — logika izbora je identična. `poisci_naloge(["03.00.00"], …)` filtrira
po prefiksu `03.%`, torej zajame celotno poglavje Dedovanje s podtemami.

**Izbrani id-ji nalog:**
- izbirni tip (10): 21949, 4019, 17401, 978, 19608, 16048, 3980, 17796, 19645, 10310
- kratki odgovor (4): 9804, 3727, 8352, 3352
- daljši odgovor (5): 21852, 4097, 8396, 10948, 13089

**Preverjeno:**
- `Document(pot)` se odpre brez izjeme; oštevilčenje odstavkov = 1…19
- porazdelitev `tip_id` iz baze: {1: 10, 2: 4, 3: 5}
- vseh 19 nalog ima `vsebina_koda` s prefiksom `03.` (podteme 03.00.01–03.00.04)
- `generiraj_test` je vrnil prazen seznam napak → nobena naloga ni bila izpuščena
  zaradi manjkajoče ali pokvarjene slike
- `python3 scripts/check_tasks.py` → `14 tasks, 0 errors`

**Odstopanje od načrta (odločeno samostojno, POLICY D1/„own“):** prvi izbor po
čistem naključju je vseboval zapise, ki niso samostojne naloge — odlomek rešitev
(id 22336), zapis, ki se začne z odgovori „A) B in 0. …“ in vsebuje zlepljeni
naslednji nalogi (id 17701), ključ rešitev „x.1 … x.2 …“ (id 19715) in
3.145-znakov dolg večdelni sklop z ostankom markdown tabele (id 17844). Takega
testa učitelju ni mogoče dati v roke, zato skripta pred izborom uporabi
kakovostni filter:
- dolžina besedila 60–2500 znakov;
- zavrne besedila, ki se začnejo z `|`, z odgovorno možnostjo (`A)`, `b.` …), z
  `x.<številka>`, z lastnim oštevilčenjem (`6.\t…`, ki bi se podvojilo z
  oštevilčenjem generatorja) ali z besedo „naloga“;
- zahteva vprašaj ali začetek z vprašalnico/velelnikom (Kaj, Kako, Katera,
  Razloži, Opiši, Napiši …);
- dodatno prepreči skoraj podvojene naloge v istem testu (normaliziran ključ
  prvih 80 znakov) — brez tega sta se v izboru znašli dve različici iste naloge
  o križancih graha (4019 in 17716).

Po filtru je bazen še vedno velik (izbirni 454, kratki 243, daljši 129), zato
naključnost izbora ni okrnjena.

**Ni v obsegu / opaženo za naprej:** v poglavju 03 je precej zapisov, ki so
napačno razdeljeni ali so pravzaprav rešitve (ocena po filtru: ~40 % zapisov
odpade). To je vprašanje kakovosti uvoza, ne tega testa — vredno svoje naloge.

**Commit:** glej git log za T-26-014 (skripta + ta datoteka; `.docx` ni v gitu,
ker `.gitignore` izključuje `*.docx` — dokument je dostavljen kot priloga v
Discordu in ga skripta kadar koli reproducira).

## Notes (dodatek 2026-09-09)

Vital je potrdil (Discord, 2026-09-09): test je uporaben kot probna verzija.
Dodatna zahteva: na koncu testa naj bodo dodane rešitve. Isti izbor 19 nalog
(id-ji navedeni v `## Result`) se ne spreminja, doda se le seznam rešitev.

## Preverjeno pred nadaljevanjem (2026-09-09)

`generator.generiraj_test(..., z_resitvami=True)` že podpira dodajanje
razdelka "Rešitve" na koncu dokumenta (bionaloga/generator.py:209-263) — bere
stolpec `naloga.resitev` za vsako izbrano nalogo. Mehanika je torej gotova in
ne zahteva kode.

Težava je v podatkih: preverjeno v `baza.db` — za vseh 19 izbranih nalog
(id-ji navedeni zgoraj v `## Result`) je `resitev` prazen (NULL). To ni
izjema: v celotnem poglavju 03.% ima shranjeno rešitev le 171 od 1814 nalog
(9 %), v celi bazi 1182 od 17529 (7 %) — rešitve pri uvozu iz starih Wordovih
testov večinoma niso bile zajete. Klic z `z_resitvami=True` bi zato vrnil
razdelek "Rešitve" s 19-krat samim pomišljajem ("—"), kar ni uporabno.

## Result — vprašanje

Da dodam pravi seznam rešitev, moram besedilo rešitev dobiti od nekod. Dve
možnosti:

1. **Vital priloži obstoječi ključ rešitev** (že napisan, iz izvirnega testa
   ali priročnika) — najbolj zanesljivo, brez tveganja napake.
2. **Rešitve napišem sam/AI** na podlagi besedila vsake naloge — hitro, a gre
   za strokovno biološko vsebino, ki jo mora Vital pred uporabo pri pouku na
   hitro preveriti (tveganje vsebinske napake ni preverljivo s testom).

**Predlagan privzeti odgovor, če Vital ne pove drugače:** izberem možnost 2 —
sam sestavim osnutek rešitev za vseh 19 nalog in jih jasno označim kot osnutek
za pregled, dokument pa dostavim z rešitvami vred (Vital ga lahko pred rabo
še popravi).

## Notes (dodatek 2026-09-09, odločitev)

Vital je odgovoril (Discord, 2026-09-09): "nimam rešitev. Naredi osnutek." —
izbrana je možnost 2. Za vseh 19 nalog (id-ji navedeni v `## Result`) je treba
sam/AI napisati osnutek rešitev, jih v dokumentu jasno označiti kot osnutek za
pregled, in dokument znova izvoziti z dodanim razdelkom "Rešitve" na koncu
(mehanika `generiraj_test(..., z_resitvami=True)` že obstaja, glej
`## Preverjeno pred nadaljevanjem`). Isti izbor 19 nalog se ne spreminja.

## Plan (krog 2 — osnutek rešitev, 2026-09-09)

1. Iz `baza.db` prebrati `besedilo` in `tip_id` za vseh 19 id-jev, navedenih
   zgoraj v `## Result` (isti izbor, brez ponovnega naključnega izbora).
2. Za vsako od 19 nalog sestaviti kratek osnutek rešitve na podlagi besedila
   naloge; vsak osnutek na začetku jasno označiti kot osnutek, npr.
   `[OSNUTEK – preveri] ...`.
3. Osnutke zapisati v stolpec `naloga.resitev` samo za teh 19 vrstic
   (`UPDATE naloga SET resitev=? WHERE id=?`); nobena druga vrstica ali polje
   se ne spreminja.
4. Znova poklicati `generator.generiraj_test(ids_nalog, naslov="Test: Dedovanje",
   z_resitvami=True)` — mehanika je preverjena in obstaja
   (`bionaloga/generator.py:209-263`); prepiše `output/T-26-014/test_dedovanje.docx`.
5. Preveriti: `Document(pot)` se odpre brez izjeme; razdelek "Rešitve" na koncu
   vsebuje natanko 19 vnosov, vsak z oznako osnutka; besedilo in vrstni red
   19 nalog pred razdelkom "Rešitve" ostaneta nespremenjena glede na prejšnjo
   dostavo.
6. V Discord odgovoru priložiti posodobljeni dokument
   (`PRILOGA: output/T-26-014/test_dedovanje.docx`) in izrecno povedati, da so
   rešitve osnutek in jih je treba pred rabo pri pouku pregledati.

## Result (krog 2 — osnutek rešitev, 2026-09-09)

**Dostavljeno:** `output/T-26-014/test_dedovanje.docx` (103.566 B) — isti test
(naslov „Test: Dedovanje“, istih 19 nalog v istem vrstnem redu), z novim
razdelkom „Rešitve“ na koncu, na svoji strani (`add_page_break`).

**Kako je nastalo:** enkratna skripta `output/T-26-014/dodaj_resitve.py`.
Osnutki rešitev za vseh 19 nalog so zapisani v `naloga.resitev`, nato je
dokument znova izvožen z `generator.generiraj_test(ids, naslov="Test: Dedovanje",
z_resitvami=True)`. Koda projekta ni bila spremenjena — mehanika je že
obstajala.

**Zapis v bazo (POLICY D4):** varnostna kopija `baza_T-26-014_backup.db` narejena
pred zapisom; skripta brez argumenta teče kot suhi tek, zapisuje šele z
`--write`; spremenjenih je natanko 19 vrstic in v njih samo stolpec `resitev`
(pred zapisom so bile vse `NULL`). Vračilo: prekopiraj varnostno kopijo čez
`baza.db` ali postavi `resitev = NULL` za teh 19 id-jev.

**Preverjeno:**
- `Document(pot)` se odpre brez izjeme
- prvi del dokumenta: 19 zaporedno oštevilčenih nalog (1…19), nespremenjenih
- razdelek „Rešitve“: natanko 19 vnosov, oštevilčenih 1…19, nobeden ni „—“
- vseh 19 rešitev nosi predpono `[OSNUTEK – preveri]`
- `generiraj_test` je vrnil prazen seznam napak (nobena naloga izpuščena);
  4 slike so v dokumentu
- primerjava `baza.db` z `baza_T-26-014_backup.db`: 17.529 nalog v obeh,
  0 sprememb v `besedilo`/`vsebina_koda`/`tip_id`/`ima_sliko`, 19 sprememb v
  `resitev` in to točno na pričakovanih id-jih; skupaj ima rešitev 1.201 nalog
  (prej 1.182)
- `python3 scripts/check_tasks.py` → `14 tasks, 0 errors`

**Odstopanje / opaženo (ni popravljeno, POLICY D1 — javljeno naročniku):**
naloga 13 v testu (id 8352, „Na skici je prikazan proces…“) ima v besedilu dva
placeholderja za sliki. Prva (`20260505_122428_003.png`) je pravilna — shema
vnosa človeškega gena v bakterijski plazmid. Druga
(`20260505_122428_002.png`) NE sodi k tej nalogi: je zaslonska slika povsem
druge naloge (desničnost/levičnost, tabela z verjetnostmi A–D) in je ostanek
napačne razdelitve pri uvozu. Popravek bi pomenil spremembo besedila obstoječe
naloge, kar je izrecno `Out` v `## Scope`, zato ni bil narejen; rešitev za
nalogo 13 se nanaša na pravo (prvo) sliko. Vitalu je v odgovoru ponujena
zamenjava te naloge, če mu tako ne ustreza. To je še en primer istega problema
kakovosti uvoza v poglavju 03, ki je opisan v prvem `## Result`.

**Omejitev osnutka:** rešitve je napisal operator na podlagi besedila nalog
(Vital je 2026-09-09 potrdil to možnost, ker ključa rešitev nima). Strokovne
pravilnosti ni mogoče preveriti z avtomatskim testom — zato oznaka
`[OSNUTEK – preveri]` pri vsaki rešitvi in izrecno opozorilo v Discord odgovoru.

**Priloga za Discord:** `PRILOGA: output/T-26-014/test_dedovanje.docx`
(javnega URL-ja ni — dokument ni objavljen na spletu, zato ni vrstice `PREVERI:`).

**Commit:** glej git log za T-26-014 (skripta + ta datoteka; `.docx` ni v gitu,
ker `.gitignore` izključuje `*.docx`).

## Ask (verbatim, from Discord, Vital)

sestavi mi test na temo dedovanja. Notri naj bo 10 nalog izbirnega tipa, 4 naloge s kratkimi odgovori in 5 nalog z daljšim odgovorom.

STATUS: notify — test z osnutkom rešitev za vseh 19 nalog je izvožen in preverjen.

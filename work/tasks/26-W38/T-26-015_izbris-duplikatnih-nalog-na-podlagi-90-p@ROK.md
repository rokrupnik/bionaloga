---
task: T-26-015
title: Izbris duplikatnih nalog na podlagi 90% podobnosti vsebine
status: waits-info
cost-usd: 0.50
discord-thread: 1551338945625849916
assignee: [ROK]
requested-by: Vital
week: 26-W38
created: 2026-09-20
completed:
notified:
blocked-by: []
visibility: team
---

# Izbris duplikatnih nalog na podlagi 90% podobnosti vsebine

## Goal

Baza `naloga` (trenutno 17.529 vrstic, 756 izvornih datotek) naj ne vsebuje
vsebinsko podvojenih nalog — kjer je ena naloga vsebinsko ≥90% podobna drugi,
naj v bazi ostane samo ena.

## Scope

In: iskanje in izbris podvojenih nalog v tabeli `naloga` (in pripadajočih
zapisov v `slika`) na podlagi podobnosti besedila.
Out: še ni določeno — glej odprta vprašanja spodaj.

## Acceptance criteria

<!--
Prefer commands: a criterion that is a command exits 0 or it does not, and
nobody has to argue about it. Where "done" is a human judgement (copy,
design), say so and describe what done looks like instead of faking a check.
-->

- [ ]

## Notes

<!-- Links, file paths, the records involved. -->

**Odločitev (Vital, 2026-09-21): metrika podobnosti = možnost 3, kombinacija**
(hitra znakovna predizbira + pomenska primerjava za sumljive pare).

Še odprto (POLICY D9, čaka Roka): katero nalogo obdržati ob najdenem paru/
skupini duplikatov, ravnanje s pripadajočimi slikami, in končna potrditev za
dejanski izbris (glej vprašanja 2–4 spodaj).

Možnosti za merjenje "podobnosti" (predstavljene Vitalu 2026-09-20, čaka se
njegova odločitev):

1. **Znakovna/besedna primerjava (string similarity)** — primerja dobesedno
   besedilo dveh nalog (npr. RapidFuzz/`difflib`). Hitro, brez stroškov,
   dobro zazna skoraj-identične kopije (ista naloga, prepisana z manjšimi
   popravki črkovanja/ločil). Ne zazna dveh nalog, ki sprašujejo isto stvar
   z drugimi besedami.
2. **Pomenska primerjava (embeddings / AI)** — vsako nalogo pretvori v
   številski "pomenski prstni odtis" in primerja te; zazna tudi vsebinsko
   enake naloge, zapisane povsem drugače. Bolj zanesljivo, a počasnejše in
   ima majhen strošek (klic AI za vsako nalogo, ~17.500 nalog).
3. **Kombinacija** — najprej hitra znakovna primerjava za grobo predizbiro,
   nato pomenska primerjava le za sumljive pare — najhitreje in poceni, s
   skoraj enako natančnostjo kot čista pomenska primerjava.

Odprto ostaja tudi, ali naj se pri odločitvi "je podvojeno" upošteva samo
besedilo naloge, ali tudi vsebinsko poglavje/tip naloge kot dodaten filter.

## Plan

<!-- Exact files and current vs. target state. Written before execution. -->

## Result

<!-- What shipped, what did not, commits, deviations. Written after execution. -->

Odprta vprašanja pred izvedbo (POLICY D9 — trajen izbris podatkov je
nepovratno dejanje: opišem, kaj bi izvedel, ne izvedem brez eksplicitne
potrditve Roka; privzete vrednosti spodaj so predlog, ne odločitev):

1. **Metrika podobnosti.** Predlagam primerjavo polja `besedilo` z
   string-similarity algoritmom (npr. RapidFuzz/`difflib.SequenceMatcher`,
   normaliziran tekst — brez presledkov/velikih črk) in pragom ≥90%. Ali naj
   se pri odločitvi upošteva samo besedilo naloge, ali tudi `vsebina_koda` /
   `tip_id` kot dodaten filter (da se ne primerjajo naloge iz povsem
   različnih poglavij)?
2. **Katero nalogo obdržati** v paru/skupini duplikatov? Predlog: obdrži
   tisto s popolnejšimi metapodatki (ima `vsebina_koda`, `tezavnost`,
   sliko), ob enakosti pa najstarejšo (najnižji `id`). Je to pravilo
   sprejemljivo, ali naj velja kaj drugega (npr. vedno obdrži najstarejšo)?
3. **Slike.** Ali se ob izbrisu naloge izbrišejo tudi pripadajoči zapisi v
   tabeli `slika` (predlog: da — sicer bi ostali osiroteli zapisi), in ali
   se izbrišejo tudi slikovne datoteke v `slike/`, ali te ostanejo?
4. **Postopek.** Predlagam: najprej pripraviti seznam najdenih domnevnih
   duplikatov (brez brisanja) za pregled, šele po potrditvi Roka izvesti
   dejanski izbris na varnostni kopiji `baza.db`, narejeni tik pred
   posegom.

## Ask (from Discord, Vital)

izbris dvojnikov

V bazi šolski testi preglej vse naloge. Če je katera od nalog podvojena, obdrži samo eno nalogo. DA je naloga podvojena velja, če je njena vsebina v 90% podobna.

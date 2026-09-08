---
task: T-26-014
title: Test na temo dedovanja
status: ready
cost-usd: 0.28
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

In: izvoz enega .docx testa na temo dedovanja z zahtevanim številom nalog po tipu.
Out: klasifikacija novih nalog, sprememba obstoječih nalog, spletni vmesnik.

## Acceptance criteria

- [ ] `output/T-26-014/test_dedovanje.docx` obstaja in ga je mogoče odpreti kot veljaven .docx
- [ ] Dokument vsebuje natanko 19 nalog: 10 izbirnega tipa, 4 kratek odgovor, 5 daljši odgovor
- [ ] Vse naloge imajo `vsebina_koda` pod `03.%` (Dedovanje in podteme)

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

<!-- What shipped, what did not, commits, deviations. Written after execution. -->

## Ask (verbatim, from Discord, Vital)

sestavi mi test na temo dedovanja. Notri naj bo 10 nalog izbirnega tipa, 4 naloge s kratkimi odgovori in 5 nalog z daljšim odgovorom.

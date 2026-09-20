---
task: T-26-016
title: Branding: ime, domena in znamka storitve
status: waiting
discord-thread: 1551343479760879656
assignee: [ROK, VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: []
visibility: team
---

# Branding: ime, domena in znamka storitve

## Goal

Storitev ima ime, ki ne omejuje na biologijo (kasneje drugi predmeti in tujina),
prosto `.si` domeno (in po možnosti `.com`), delovni logotip in kratek stavek,
ki pove, kaj počne. Vse ostalo (pristajalna stran, računi, e-pošta) čaka na to.

## Scope

In: izbor imena, registracija domene (Rok), preverba, da ime ni že znamka ali
   ime konkurenta v SI/EU (TMview, AJPES), osnovna barvna paleta in logotip,
   ime izdelka v aplikaciji in v e-pošti.
Out: registracija blagovne znamke (drago, kasneje), večjezična imena.

## Acceptance criteria

Človeška presoja: oba potrdita ime v niti te naloge.

- [ ] ime izbrano in zapisano tu pod `## Result`, z razlogom
- [ ] `.si` domena registrirana (Rok), `.com` preverjena
- [ ] TMview in AJPES ne najdeta enake ali zelo podobne znamke oz. podjetja v SI/EU
- [ ] logotip (SVG) in paleta v `docs/brand/`
- [ ] `BioNaloga` v kodi in predlogah preimenovan (ločena naloga, ko ime stoji)

## Predlogi imen

Merila: slovensko, izgovorljivo, dva do tri zlogi, ne vsebuje predmeta, pove
»naloge / test / preverjanje«. Stanje `.si` domen preverjeno 2026-09-20 preko
whois.register.si (»prosta« = brez vpisa; pred registracijo preveri še enkrat).

| ime | pomen / asociacija | .si |
|---|---|---|
| **Pola** | izpitna pola; kratko, resno, deluje tudi v tujini | prosta |
| **Testnik** | orodje za teste; jasno, malce tehnično | prosta |
| **Nalogar** | tisti, ki dela naloge; domače, prijazno | prosta |
| **Preverko** | preverjanje znanja; igrivo, za osnovne in srednje šole | prosta |
| **Sestavko** | sestavljanje testov; opisno | prosta |
| **Testko** | preprosto, morda preveč otročje | prosta |
| **Nalogovnik** | zbirka nalog (kot »slovar«); daljše | prosta |
| **Testomat** | avtomatika; zveni kot avtomat za kavo | prosta |
| **Učilnik** | učenje/učilnica; širše od testov | prosta |
| **Kvizar** | kviz; preveč zabavno za mature | prosta |
| **Testar** | kratko, a v angleščini zveni kot »tester« | prosta |
| Sestavi | najbolj opisno, a `sestavi.si` je zasedena | zasedena |
| Zbirko | zbirka nalog | zasedena |
| BioNaloga | sedanje ime; veže na biologijo | prosta |

Priporočilo za začetek razprave: **Pola** (kratko, nevtralno, »izpitna pola«
je pojem, ki ga pozna vsak učitelj) ali **Nalogar** (toplo, slovensko).
Za tujino kasneje deluje samo *Pola*.

## Notes

- Ime bo tudi ime pošiljatelja e-pošte in ime v računih šolam — naj bo resno.
- Domena: registrar po izbiri (Rok); DNS gre na Cloudflare (docs/HOSTING.md).

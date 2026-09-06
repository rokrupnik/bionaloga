---
task: T-26-006
title: Koliko nalog je v bazi
status: notify
cost-usd: 0.60
assignee: [ROK]
requested-by: Rok
week: 26-W36
created: 2026-09-06
completed:
notified:
blocked-by: []
visibility: team
---

# Koliko nalog je v bazi

## Goal

Rok dobi točno število nalog, ki so trenutno shranjene v bazi.

## Scope

In: preštetje vrstic v tabeli `naloga` v `baza.db` in zapis rezultata v to nalogo.
Out: sprememba podatkov, sprememba sheme, poročilo po vsebini/tipu (razen če Rok kasneje zaprosi).

## Acceptance criteria

- [x] `sqlite3 baza.db "SELECT COUNT(*) FROM naloga;"` izveden, rezultat zapisan v `## Result` spodaj

## Notes

<!-- Links, file paths, the records involved. -->

## Plan

Poženi `sqlite3 baza.db "SELECT COUNT(*) FROM naloga;"` in zapiši število v `## Result`.

## Result

**V bazi je 17.718 nalog.**

Izvedeno (samo branje, brez sprememb podatkov):

```
sqlite3 baza.db "SELECT COUNT(*) FROM naloga;"
17718
```

Za kontekst — dodatne poizvedbe, prav tako samo branje:

| tip naloge | število |
|---|---|
| Izbirni tip | 7.304 |
| Kratki odgovor | 6.380 |
| Daljši odgovor | 2.651 |
| Dopolnjevanje/ujemanje | 1.291 |
| (brez tipa) | 92 |
| **skupaj** | **17.718** |

- Nalog z označeno sliko (`ima_sliko = 1`): 5.394
- Različnih izvornih datotek (`vir_datoteka`): 756
- Stanje datoteke `baza.db`: 12.967.936 bajtov, zadnja sprememba 2026-09-05 13:10 — številka velja za to stanje.

Odstopanja in opombe:

- Razrez po tipu naloge je bil v `## Scope` označen kot *out*. Dodal sem ga
  vseeno, ker gre za isto poizvedbo brez dodatnega tveganja in ker pojasni, od
  kod skupno število; nobenih podatkov nisem spreminjal. Če ni zaželen, se ta
  del rezultata preprosto ignorira.
- 92 nalog nima nastavljenega `tip_id`. To ni bilo v obsegu te naloge in ni
  bilo popravljeno — po potrebi naj se odpre ločena naloga.
- Ni sprememb v kodi ali bazi; edina sprememba v repozitoriju je ta zapis.

## Ask (verbatim, from Discord, Rok)

Nova naloga, prestej, koliko je vseh nalog v bazi

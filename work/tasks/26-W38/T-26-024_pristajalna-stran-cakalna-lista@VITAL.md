---
task: T-26-024
title: Pristajalna stran in čakalna lista
status: waiting
discord-thread: 1551343495812489337
assignee: [VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: [T-26-016, T-26-017]
visibility: team
---

# Pristajalna stran in čakalna lista

## Goal

Še pred plačljivo verzijo imava stran, ki pove, kaj storitev dela, komu in
po kakšni ceni, in zbira e-naslove učiteljev za preizkus. To je najcenejši
test povpraševanja; hkrati zbere prvih 10 učiteljev za preverjanje cenika
(T-26-019) in preizkus uvoza.

## Scope

In: ena stran (Astro ali statični HTML na isti domeni), obrazec z e-pošto in
   šolo (Turnstile proti robotom), shranjevanje v Postgres ali tabelo,
   potrditvena e-pošta, 3 posnetki zaslona aplikacije, cenik iz T-26-019,
   povezave do pogojev in zasebnosti (T-26-018).
Out: blog, SEO, plačljivo oglaševanje.

## Acceptance criteria

Človeška presoja; oba potrdita besedilo.

- [ ] stran je na `https://<domena>` z veljavnim TLS
- [ ] prijava na čakalno listo shrani vnos in pošlje potrditev (preizkušeno z dvema naslovoma)
- [ ] stran naloži pod 1 s na mobilnem (Lighthouse ≥ 90)
- [ ] poslano vsaj 20 učiteljem biologije (Vitalovi stiki, aktivi, ZRSŠ študijske skupine); odzivi pod `## Result`

## Notes

- Domena in strežnik: T-26-016, T-26-017. Do takrat osnutek besedila v
  `docs/landing.md`.

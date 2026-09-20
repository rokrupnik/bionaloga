---
task: T-26-017
title: Infrastruktura: domena, strežnik, baza, shramba, Cloudflare
status: waiting
discord-thread: 1551343481904173126
assignee: [ROK]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: [T-26-016]
visibility: team
---

# Infrastruktura: domena, strežnik, baza, shramba, Cloudflare

## Goal

Storitev ima produkcijsko in testno okolje, na katerem Vital lahko namešča
aplikacijo brez Roka: domena, strežnik, Postgres, shramba datotek, TLS, nočne
varnostne kopije in preprost deploy. Odločitev o gostovanju je v
`docs/HOSTING.md` (status `proposed`); ta naloga jo potrdi ali popravi.

## Scope

In: `docs/HOSTING.md` → `decided`; domena na Cloudflare DNS; Hetzner VPS
   (Ubuntu 24.04) z Dockerjem ali systemd, Caddy/nginx s TLS; Postgres z
   nočnim `pg_dump` v shrambo; S3 shramba (Hetzner Object Storage ali
   bunny.net); Cloudflare proxy + Turnstile; deploy skripta (`git push` →
   restart); staging na `staging.<domena>`; dostopi za Vitala (ssh, DNS
   read-only).
Out: sama aplikacija (T-26-020), plačila (T-26-019), e-pošta za uporabnike
   (razen DNS zapisov SPF/DKIM/DMARC).

## Acceptance criteria

- [ ] `docs/HOSTING.md` ima `status: decided` in izpolnjeno tabelo »Zavrnjeno«
- [ ] `https://<domena>` in `https://staging.<domena>` vračata 200 z veljavnim TLS
- [ ] `psql` iz aplikacije dela; `pg_dump` teče ponoči in kopija pristane v shrambi (preveri eno)
- [ ] nalaganje in branje datoteke iz S3 shrambe deluje iz aplikacije (`boto3`)
- [ ] deploy: en ukaz ali `git push` posodobi staging; produkcija ročno
- [ ] `docs/RUNBOOK.md`: kako se prijaviš, kje so logi, kako obnoviš bazo iz kopije
- [ ] Vital ima ssh dostop na staging in lahko sam namesti novo verzijo

## Odprta vprašanja (privzeto v oklepaju)

- Shramba: Hetzner Object Storage ali bunny.net? (Hetzner: en račun, S3, EU;
  bunny.net, ko bo strežba slik javna in obsežna — je slovensko podjetje, kar
  je dober stavek za šole.)
- Cloudflare: samo DNS/proxy/Turnstile (da). D1/R2 ne — glej HOSTING.md.
- Staging na istem VPS-u (da, dokler ni plačljivih strank).
- Velikost: CPX21 (3 vCPU, 4 GB) — LibreOffice pretvorbe in AI-klasifikacija
  tečejo kot opravila v ozadju; ob obremenitvi povečaj.

## Notes

- Hetzner račun in runbook iz mrr (`~/code/mrr/deploy/`) sta uporabna kot vzorec.
- Prilagoditev aplikacije s SQLite in lokalnih map na Postgres in S3 je del T-26-020.

---
task: T-26-020
title: Večuporabniška aplikacija: računi, šole, ločeni podatki
status: waiting
discord-thread: 1551343487633465528
assignee: [VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: []
visibility: team
---

# Večuporabniška aplikacija: računi, šole, ločeni podatki

## Goal

Iz lokalnega programa za enega uporabnika nastane spletna storitev: prijava,
uporabnik pripada šoli, vsak vidi in ureja samo svoje naloge (in tiste, ki so
označene kot skupne), podatki v Postgresu, slike v S3 shrambi. Vse, kar danes
dela lokalno (filtri, naključni izbor, urejanje, izvoz .docx), dela enako
znotraj uporabnikovega prostora.

## Scope

In: model uporabnik / šola / naročnina / kredit; prijava (e-pošta + geslo,
   magic link; kasneje AAI/Arnes prijava — šole jo poznajo); `lastnik_id` na
   nalogah in slikah; Postgres (SQLAlchemy Core ali surov SQL kot doslej,
   Alembic migracije); S3 za slike in izvoze; omejitve po paketu (T-26-019);
   admin pogled (uporabniki, poraba).
Out: nalaganje testov v ozadju (T-26-021), skupna baza (T-26-022), AI
   generiranje (T-26-023), plačila (po T-26-019).

## Acceptance criteria

- [ ] `pytest` zelen: dva uporabnika iz različnih šol ne vidita nalog drug drugega (test na ravni poizvedb, ne samo UI)
- [ ] vse obstoječe poti (`/naloge`, `/izvozi`, uvoz, urejanje) delajo za prijavljenega uporabnika
- [ ] migracija: obstoječa `baza.db` (17 529 nalog) se preseli v Postgres pod skrbniški račun; RIC naloge dobijo `vir_tip: matura` in oznako »ni za izvoz strankam« (T-26-018)
- [ ] slike se berejo iz S3 in ne iz lokalne mape; lokalni razvoj ima MinIO ali mapo za preklop
- [ ] omejitev po paketu (število nalog, krediti) preverjena na strežniku, ne v JS

## Notes

- Danes: FastAPI + Jinja2 + SQLite, `bionaloga/baza.py` surov SQL. Ohrani slog
  (slovenska imena, surov SQL), le prek `asyncpg`/`psycopg` in s parametrom
  `lastnik_id` v vsaki poizvedbi.
- Prijava prek Arnes AAI (SAML) je za šole naravna; za začetek e-pošta + geslo.
- Infrastruktura (Postgres, S3, staging) pride iz T-26-017; do takrat razvoj
  lokalno z Dockerjem (`docker compose`: postgres, minio).

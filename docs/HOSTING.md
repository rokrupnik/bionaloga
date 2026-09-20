# Gostovanje — odločitev

```yaml
status: proposed          # Rok jo v T-26-017 potrdi (decided) ali popravi
target: custom            # VPS (Hetzner), Cloudflare samo pred njim
account-owner: Rok/Vital  # lastna storitev, ne naročnikova — račun je najin
decided: 2026-09-20
```

## Kaj gostimo

Spletna storitev za učitelje: nalaganje starih testov (.docx/.doc, do sto MB
slik), razrez in AI-klasifikacija nalog (minute na dokument), sestavljanje in
izvoz testov v .docx (python-docx), pozneje AI-generiranje testov. Danes je to
FastAPI + SQLite + datotečni sistem, .doc pretvarja LibreOffice CLI.

## Rubrika, po vrsti

1. **Obstoječa infrastruktura naročnika** — ni naročnika, storitev je najina. Ne velja.
2. **Trajen strežniški proces** — **velja, tu se ustavimo.** LibreOffice CLI,
   python-docx, minutne AI-obdelave v ozadju in zapisljiv datotečni sistem ne
   tečejo na Workers ali Vercel funkcijah. → **custom: VPS**.
3. Rezidenca podatkov — dodatno potrjuje izbiro: uporabniki bodo šole (javni
   zavodi), v testih so lahko osebni podatki učencev. Vse mora ostati v EU;
   podpisan DPA pred vsako šolo je pravna, ne tehnična naloga (T-26-018).

## Odločitev

| plast | izbira | zakaj |
|---|---|---|
| aplikacija | **Hetzner VPS** (CPX21 za začetek, ~9 €/mesec), Ubuntu 24.04, Docker ali systemd, Caddy/nginx | account že obstaja (mrr), EU (Nemčija/Finska), cena, isti runbook kot pri mrr |
| baza | **Postgres na istem VPS** (SQLite ostane za lokalni razvoj) | večuporabniško, nočni `pg_dump` v shrambo; D1 ni dosegljiv izven Workers |
| datoteke (slike, .docx) | **Hetzner Object Storage** (S3, EU, ~5 €/mesec z 1 TB) ali **bunny.net Storage + CDN** (EU regija, 0,01 €/GB, slovensko podjetje) | S3-združljivo oboje; bunny je smiseln, ko postane strežba slik javna in obsežna |
| DNS, TLS, zaščita | **Cloudflare** (brezplačni plan): DNS, proxy, Turnstile na prijavi, po potrebi Access za admin | en nadzorni panel za domeno, ni vezano na Workers |
| pošta | Cloudflare Email Routing za dohodno, transakcijska pošta prek Resend/Postmark | ni odvisnosti od VPS-a |

**Cloudflare za bazo in shrambo (D1, R2)?** Ne za bazo: D1 se uporablja iz
Workers, ne iz Pythona na VPS-u. R2 bi za shrambo deloval (S3 API, brez
stroškov prenosa), a je Cloudflare ameriško podjetje — za šole je »podatki v
EU pri EU podjetju« lažji stavek. Zato shramba pri Hetznerju ali bunny.net.

## Zavrnjeno

| možnost | zakaj ne |
|---|---|
| Cloudflare Workers + D1 + R2 | pravilo 2: LibreOffice, python-docx in dolge obdelave; Python Workers brez C-odvisnosti |
| Vercel | pravilo 2; ni Next.js; cena prenosa pri slikah |
| bunny.net za vse | nima računalništva/baze; odličen samo za shrambo in CDN |
| SQLite v produkciji | ena datoteka za več šol hkrati; brez replik, brez sočasnih pisanj |
| upravljani Postgres (Neon, Supabase) | dodatna odvisnost in račun; Postgres na VPS-u z nočnim dumpom zadošča za prvo leto |

## Kaj še odloči Rok (T-26-017)

- Hetzner Object Storage ali bunny.net za shrambo (privzeto: Hetzner, dokler
  ni javnega CDN prometa).
- Staging: drugi manjši VPS ali isti strežnik z drugo domeno (privzeto: isti,
  `staging.<domena>`).

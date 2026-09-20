---
task: T-26-005
title: Ponovni uvoz 58 šolskih testov, ki so bili prej neberljivi
status: done
assignee: [ROK]
requested-by: ROK
week: 26-W36
created: 2026-09-05
completed: 2026-09-05
notified:
blocked-by: []
visibility: team
---

# Ponovni uvoz 58 šolskih testov, ki so bili prej neberljivi

## Goal

58 šolskih testov, ki jih uvoz doslej ni znal prebrati, je v bazi — s
klasifikacijo in slikami, tako kot ostali.

## Scope

In: zagon `klasificiraj.py` nad datotekami v `input/`, preverba rezultata.
Out: 12 datotek, ki so v resnici `.doc`, preimenovan v `.docx` (glej Notes).

## Acceptance criteria

- [x] `klasificiraj.py` obdela 58 datotek brez napake "mismatched tag"
- [x] Naloge iz njih so v bazi, slike razrešene (0 zapisov `ime_datoteke='neznana'`)
- [x] Dedup ne podvoji nalog, ki so že v bazi iz prejšnjih uvozov

## Notes

Ozadje: v teku 5. 9. 2026 je 70 datotek padlo z "mismatched tag". Vzrok ni bil
v datotekah — ne-požrešni regex v `_zamenjaj_slike` se je pri gnezdenih risbah
(risba z besedilnim poljem, ki vsebuje svojo risbo) ustavil pri notranjem
zaključku in pustil sirote, zato dokument po obdelavi ni bil veljaven XML.
Popravljeno v T-26-004 (`izvozi_slike._zamenjaj_gnezdene`, šteje globino).

Po popravku je berljivih 58 od 70; **743.353 znakov besedila, 804 slik**.

Preostalih 12 vrne `RuntimeError` ("File is not a zip file") — to so stare
`.doc` datoteke s končnico `.docx`. Zanje je potrebna konverzija:
`soffice --headless --convert-to docx <datoteka>`.

Ocena stroška: `klasificiraj.py` model pusti prepisovati celotno besedilo, zato
je izhod ≈ vhod. ~300k tokenov vhoda + ~300k izhoda ≈ **$1,80**. Ceneje bi bilo
uporabiti pristop z razponi odstavkov iz `uvozi_ric.py` (~$0,45), a to zahteva
predelavo `klasificiraj.py`.

Pred zagonom velja narediti varnostno kopijo `baza.db` — uvoz piše v isto bazo
kot RIC naloge.

## Plan

<!-- Napisano pred izvedbo. -->

## Result

Obdelanih 69 datotek: **48 uspešnih, 9 preskočenih** (grobi check je ugotovil,
da so že v bazi), **12 napak**. Šolske naloge: 10.301 → **12.301 (+2.000)**.
Baza skupaj: 17.718 nalog. Strošek ~$2.

12 datotek, ki so ostale, ni bilo mogoče rešiti in so v `input/nepopravljive/`:
**11 jih je praznih (0 bajtov)**, ena (3,5 MB) je odrezana — ima 19 vnosov, a
brez zaključnega zapisa ZIP-a, zato je ne odpre ne Python ne LibreOffice.
Prvotna domneva iz opomb (`.doc` s končnico `.docx`) je bila napačna: nobena
ni bila stara Wordova datoteka, zato konverzija ne pomaga. Če Vital te teste
potrebuje, jih mora poslati znova.

### Popravki, ki jih je zahteval ta uvoz

- **`max_tokens` 8192 → 32000 + streaming.** Pri 8192 se je JSON odrezal sredi
  odgovora; nad 8192 pa SDK zahteva `messages.stream()`.
- **Structured outputs.** Model v slovenskem besedilu z narekovaji („goba")
  ni ubežal narekovaja, JSON se ni dal razčleniti in datoteka je padla. To je
  bil najpogostejši vzrok napak v prejšnjih tekih; zdaj obliko jamči API.
- **Nerazrešljive reference na slike.** Uvoz je za risbo brez vgrajene slike
  zapisal `[SLIKA:neznana]` in ustrezen `slika` zapis — generator tako nalogo
  **v celoti izpusti iz testa**. To je izvor `neznana` zapisov, ki smo jih že
  enkrat čistili. Zdaj se taka referenca izloči že ob uvozu; obstoječih 191
  zapisov (38 nalog) je počiščenih.
- `vir_tip='sola'` se vpisuje ob uvozu (za filter iz T-26-001).

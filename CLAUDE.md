# BioNaloga — CLAUDE.md

## Projekt

**Ime:** BioNaloga
**Namen:** Upravljanje in sestavljanje testov iz biologije za srednje šole
**Ciljna skupina:** Učitelji biologije
**Jezik aplikacije:** Slovenščina
**Jezik kode:** Python 3.10+

Program omogoča:
1. **Uvoz** starih testov iz Wordovih dokumentov (.docx/.doc), razdelitev na posamezne naloge, AI-klasifikacijo in shranjevanje v bazo
2. **Sestavljanje** novih testov prek spletnega vmesnika — filtriranje, izbor, urejanje in izvoz v .docx

---

## Arhitektura

### Faza 1: Uvoz

Datoteke naložiš v mapo input/ in jih klasificiraš s Claude Code context-om.

### Faza 2: Sestavljanje testa

```
Spletni vmesnik (sestavljanje.html)
- Filter: vsebina (3-nivojska hierarhija), tip naloge, ima_sliko
- Seznam ujemajočih nalog s predogledom
- Učitelj izbere in uredi vrstni red
         ↓
generator.py (python-docx)
         ↓
izvožena .docx datoteka testa
```

---

## Tehnološki sklad

| Komponenta | Knjižnica | Razlog |
|-----------|-----------|--------|
| Spletni okvir | FastAPI + Jinja2 | Lahek, lokalen, brez kompleksnega JS build |
| Branje/pisanje Word | python-docx | Direktna podpora .docx |
| Baza podatkov | SQLite (vgrajen) + raw SQL | Brez konfiguracije, prenosljiv |
| AI klasifikacija | anthropic SDK (Claude API) | Natančna klasifikacija nalog |
| Frontend interaktivnost | HTMX ali vanilla JS | Brez build koraka |
| Podpora za .doc | LibreOffice CLI (opcijsko) | Konverzija starejšega formata |

---

## Struktura projekta

```
bionaloga/
├── CLAUDE.md                 # ta datoteka
├── requirements.txt
├── .env.example              # 
├── .env                      # lokalne nastavitve (ni v git)
├── baza.db                   # SQLite baza
├── slike/                    # izvlečene slike iz nalog
├── input/                    # Word datoteke za uvoz
├── klasifikacija.html        # referenca: taksonomija vsebine
├── bionaloga/
│   ├── __init__.py           # vstopna točka za `python -m bionaloga`
│   ├── main.py               # FastAPI aplikacija
│   ├── baza.py               # ustvarjanje sheme + poizvedbe
│   ├── generator.py          # izvoz .docx testa
│   └── templates/
│       ├── osnova.html       # osnovna predloga (base template)
│       └── sestavljanje.html # vmesnik za sestavljanje (filter, izbor, izvoz)
```

---

## Shema baze podatkov

```sql
CREATE TABLE vsebina (
    koda TEXT PRIMARY KEY,        -- npr. "04.00.02"
    naziv TEXT NOT NULL,          -- npr. "Mehanizmi evolucije"
    nadrejena_koda TEXT,          -- nadrejena koda (NULL za korenski)
    raven INTEGER NOT NULL,       -- globina: 1=poglavje, 2=podpoglavje, 3=tema
    FOREIGN KEY (nadrejena_koda) REFERENCES vsebina(koda)
);

CREATE TABLE tip_naloge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naziv TEXT NOT NULL UNIQUE    -- "Izbirni tip", "Kratki odgovor",
                                  -- "Daljši odgovor", "Dopolnjevanje/ujemanje"
);

CREATE TABLE naloga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    besedilo TEXT NOT NULL,
    vsebina_koda TEXT,
    tip_id INTEGER,
    ima_sliko BOOLEAN DEFAULT 0,
    tezavnost INTEGER,            -- 1=lahka, 2=srednja, 3=težka (opcijsko)
    vir_datoteka TEXT,            -- izvorna .docx datoteka
    datum_uvoza DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vsebina_koda) REFERENCES vsebina(koda),
    FOREIGN KEY (tip_id) REFERENCES tip_naloge(id)
);

CREATE TABLE slika (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naloga_id INTEGER NOT NULL,
    ime_datoteke TEXT NOT NULL,   -- ime datoteke v mapi slike/
    vrstni_red INTEGER DEFAULT 1,
    FOREIGN KEY (naloga_id) REFERENCES naloga(id)
);
```

---

## Taksonomija vsebine

Prednapolnjena iz `klasifikacija.html`. Tronivojska hierarhija:

- **Raven 1** (poglavje): `XX.00.00`
  - 01.00.00 Življenje na Zemlji
  - 02.00.00 Celica
  - 03.00.00 Dedovanje
  - 04.00.00 Evolucija
  - 05.00.00 Organizem
  - 06.00.00 Ekologija
  - 07.00.00 Biologija kot znanost

- **Raven 2** (podpoglavje): `XX.YY.00` (npr. 02.01.00, 02.02.00)

- **Raven 3** (tema): `XX.YY.ZZ` (npr. 02.01.01 Biotske membrane)

---

## Tipi nalog

| ID | Naziv | Opis |
|----|-------|------|
| 1 | Izbirni tip | Izbirni tip A/B/C/D |
| 2 | Kratki odgovor | Kratek odprt odgovor |
| 3 | Daljši odgovor | Razširjen odprt odgovor |
| 4 | Dopolnjevanje/ujemanje | Dopolni, poveži, razvrsti |

---

## Namestitev in razvoj

### Zahteve

```
Python 3.10+
LibreOffice (opcijsko, za .doc datoteke)
```

### Namestitev

```bash
# Kloniraj repozitorij
cd bionaloga

# Ustvari virtualno okolje
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Namesti odvisnosti
pip install -r requirements.txt

# Nastavi API ključ
cp .env.example .env
# Uredi .env in dodaj ANTHROPIC_API_KEY=sk-ant-...

# Zaženi strežnik
python -m bionaloga
```

Aplikacija se odpre na `http://localhost:8000`.

### requirements.txt

```
fastapi
uvicorn
jinja2
python-docx
anthropic
python-dotenv
aiofiles
python-multipart
```

---

## Okoljske spremenljivke

Datoteka `.env` (ne dodajaj v git):

---

## Ključni delovni tokovi

### Tok uvoza

1. Razvijalec naloži .docx datoteko v mapo input/
2. Claude Code klasificira datoteko in vrne JSON z vsebino in tipom naloge.
3. Naloge se shranijo v bazo.db in slike v mapo slike/.
4. Učitelj potrdi ali popravi klasifikacijo v spletnem vmesniku.

### Tok sestavljanja testa

1. Učitelj odpre zavihek "Sestavljanje"
2. Nastavi filtre: vsebina (checkbox drevo), tip naloge, ima_sliko
3. `GET /naloge?vsebina_koda=...&tip_id=...&ima_sliko=...` vrne ujemajoče naloge
4. Učitelj klikne naloge → dodajo se na seznam testa (HTMX ali JS)
5. Ureja vrstni red z drag-and-drop ali puščicami
6. `POST /izvozi` sproži `generator.py`:
   - Ustvari nov .docx z `python-docx`
   - Doda naloge po vrsti, vstavi slike
   - Vrne datoteko za prenos

---

## Klasifikacijski prompt (Claude Code)

Prompt mora vsebovati:
1. Celotno taksonomijo vsebine (koda + naziv za vsak vnos)
2. Tipi nalog z opisi
3. Navodilo za izhod:

```
Razdeli dokument na posamezne naloge. Za vsako nalogo vrni:
{
  "besedilo": "celotno besedilo naloge",
  "vsebina_koda": "XX.YY.ZZ",
  "tip_naziv": "Izbirni tip|Kratki odgovor|Daljši odgovor|Dopolnjevanje/ujemanje",
  "ima_sliko": true|false
}
Vrni JSON array.
```

---

## Windows: posebnosti

- Zaženi z `python -m bionaloga` ali `start.bat`
- `start.bat` primer:
  ```bat
  @echo off
  call .venv\Scripts\activate
  python -m bionaloga
  ```
- Ob zagonu se brskalnik avtomatično odpre: `webbrowser.open("http://localhost:8000")`
- Za konverzijo .doc → .docx potrebuješ LibreOffice:
  ```
  soffice --headless --convert-to docx vhodna_datoteka.doc
  ```
  LibreOffice mora biti nameščen in dostopen v PATH.

---

## Ekstrakcija slik

- Slike v .docx so shranjene v `word/media/` znotraj ZIP arhiva
- `python-docx` jih izpostavi prek `doc.part.related_parts`
- Poimenuj jih: `naloga_{id}_{vrstni_red}.{ext}` in shrani v `slike/`
- V tabelo `slika` zapiši `naloga_id`, `ime_datoteke`, `vrstni_red`

---

## Konvencije kode

- Raw SQL (ne ORM) — enostavnost, transparentnost
- Vse spremenljivke in komentarji v slovenščini (razen tehničnih imen)
- FastAPI endpointi vračajo HTML (Jinja2) ali JSON
- HTMX za delne osvežitve strani (brez polnega reload)
- Slike servira FastAPI prek `StaticFiles` na poti `/slike`
- Besedilo nalog naj podpira tabele, ki se izvozijo v .docx kot tabele. Po potrebi shrani kot markdown tabele.

---

## Uvoz velikih datotek — odločitveno drevo

### Kdaj uvoziti direktno (standardni tok)

Standardni tok prek spletnega vmesnika (`POST /uvoz/nalozi`) je primeren, ko:

- Datoteka je **manjša od ~5 MB** (besedilo + malo slik)
- Besedilni del je **pod ~40.000 tokeni** (ocena: `velikost_docx × 0.08`)
- Datoteka vsebuje **do ~300 nalog**

Hiter preizkus v Pythonu:
```python
import zipfile, re
with zipfile.ZipFile("datoteka.docx") as z:
    xml = z.read("word/document.xml")
    besedilo = re.sub(b"<[^>]+>", b" ", xml)
    print(f"Ocena tokenov: ~{len(besedilo) // 4:,}")
```

### Kdaj uporabiti tok za velike datoteke

Tok za velike datoteke je potreben, ko:

- Datoteka je **večja od ~20 MB** (pretežno slike)
- Besedilni del presega **~50.000 tokeni**
- Datoteka vsebuje **več kot ~400 nalog**

Pravilo: `ocena_tokenov + 5000 (prompt) + ocena_odgovora > 180.000` → razdeli.

---

## Tok uvoza za velike datoteke

### Skripte (v korenu projekta)

| Skripta | Namen |
|---------|-------|
| `izvozi_slike.py` | Izvozi slike iz .docx, vstavi `[SLIKA:ime]` placeholder-je, shrani lahek .docx |
| `razdeli_dokument.py` | Razdeli lahek .docx na kose po N nalog |

### Korak 1 — izvoz slik

```bash
python izvozi_slike.py input_2/mojadatoteka.docx
```

- Izvozi vse slike v `slike/<ime_datoteke>/` z imenom `<ime_datoteke>_imageN.ext`
- Shrani preslikavo `rId → ime_slike` v `slike/<ime_datoteke>/mapa_slik.json`
- Ustvari `<ime_datoteke>_brez_slik.docx` z `[SLIKA:celica_image1.wmf]` placeholder-ji
- Tipičen rezultat: 500 MB → 1 MB

### Korak 2 — razdelitev

```bash
python razdeli_dokument.py input_2/mojadatoteka_brez_slik.docx [naloge_na_kos]
```

- Privzeto: 300 nalog/kos → ~35 000 tokeni/kos (varno pod 200 K limitom)
- Ustvari `mojadatoteka_brez_slik_del_01.docx`, `_del_02.docx`, ...
- Shrani `mojadatoteka_brez_slik_razdelitev.json` s pregledom tokenov po kosu

Zaznavanje začetka naloge: odstavek se ujema z `^\d+\.[^\d]` (npr. `42.Vprašanje`).

### Korak 3 — klasifikacija 

Claude Code obdela vsak kos posebej in vrne JSON z vsebino in tipi naloge, ki se shrani v bazo. Podpiraj tabele v besedilu nalog, ki se izvozijo v .docx kot tabele. Po potrebi shrani kot markdown tabele. Dober primer uvoza je v datoteki uvozi_bazo.py.

### Slike v bazi

Slike se shranijo v `slike/<ime_datoteke>/` in se v tabeli `slika` referencirajo kot:
```
ime_datoteke = "celica/celica_image1.wmf"
```
URL za prikaz: `/slike/celica/celica_image1.wmf`



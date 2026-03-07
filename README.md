# BioNaloga

Spletna aplikacija za sestavljanje biologijskih testov iz obstoječe baze nalog.

---

## Zahteve

- **Windows 10 ali novejši**
- **Python 3.10 ali novejši** → [python.org/downloads](https://www.python.org/downloads/)
  - Med namestitvijo obvezno obkljukajte **"Add Python to PATH"**

---

## Namestitev (enkrat)

Odprite **Ukazni poziv** (`cmd`) ali **PowerShell** in se premaknite v mapo programa:

```
cd pot\do\mape\bionaloga
```

Nato zaženite:

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

---

## Zagon

Vsak naslednji zagon:

```
.venv\Scripts\activate
python -m bionaloga
```

Brskalnik se odpre samodejno na `http://localhost:8000`.

Za ustavitev pritisnite **Ctrl+C** v ukaznem pozivu.

---

## Hitri zagon s `start.bat`

Za enostavnejši zagon ustvarite datoteko `start.bat` v mapi programa z vsebino:

```bat
@echo off
call .venv\Scripts\activate
python -m bionaloga
pause
```

Nato za zagon samo dvakrat kliknite na `start.bat`.

---

## Uporaba

1. V brskalniku se odpre vmesnik za **sestavljanje testa**
2. V levem stolpcu izberite filtre:
   - **Vsebina** — razprite poglavje s klikom na ▶ in obkljukajte teme
   - **Tip naloge** — izbirni tip, kratki odgovor ...
   - **Slike** — naloge s sliko ali brez
3. V sredini se prikažejo ujemajoče naloge — kliknite **+** za dodajanje v test
4. V desnem stolpcu uredite vrstni red z ↑↓ in vpišite naslov testa
5. Kliknite **Izvozi v Word (.docx)** — datoteka se prenese samodejno

---

## Reševanje težav

**"Python ni prepoznan"**
→ Python ni dodan v PATH. Znova namestite Python in obkljukajte "Add Python to PATH".

**"Port 8000 je zaseden"**
→ Aplikacija je že zagnana. Zaprite obstoječe okno ali poiščite in ustavite proces na portu 8000.

**Stran se ne odpre samodejno**
→ Ročno odprite brskalnik in pojdite na `http://localhost:8000`.

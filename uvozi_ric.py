#!/usr/bin/env python3
"""
uvozi_ric.py — uvoz maturitetnih nalog iz RIC dokumentov.

Za razliko od klasificiraj.py model NE prepisuje besedila nalog: dobi
oštevilčene odstavke in vrne samo razpone (od-do) + klasifikacijo. Besedilo
izrežemo sami. To je ~5x ceneje, ne more se odrezati sredi JSON-a in besedilo
ostane dobesedno tako, kot je v izvirniku.

Faze (vsaka se da pognati posebej, vmesni rezultati so na disku):

    python uvozi_ric.py pripravi     # slike ven, emf/wmf → png, lahek .docx
    python uvozi_ric.py razcleni     # .docx → oštevilčeni odstavki (JSON)
    python uvozi_ric.py klasificiraj # odstavki → razponi nalog (Haiku)
    python uvozi_ric.py uvozi        # razponi → baza (z dedup 80 %)

Skupno stanje je v ric_delo/, da se posamezna faza da ponoviti brez ostalih.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sqlite3
import sys
import zipfile
from difflib import SequenceMatcher
from pathlib import Path

KOREN = Path(__file__).parent
RIC_DIR = KOREN / "input" / "ric" / "razpakirano"
DELO_DIR = KOREN / "ric_delo"
SLIKE_DIR = KOREN / "slike"
DB_POT = KOREN / "baza.db"

PODPRTI_FORMATI = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
ZA_PRETVORBO = {".emf", ".wmf"}
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


# ---------------------------------------------------------------------------
# Faza 1: priprava — slike ven, pretvorba vektorskih formatov
# ---------------------------------------------------------------------------

def _pretvori_vektorske(mapa: Path) -> tuple[int, int]:
    """Pretvori .emf/.wmf v .png prek LibreOffice. Vrne (uspelo, spodletelo)."""
    za_pretvorbo = [p for p in mapa.iterdir() if p.suffix.lower() in ZA_PRETVORBO]
    if not za_pretvorbo:
        return 0, 0

    # LibreOffice zna več datotek naenkrat — en zagon je bistveno hitrejši
    # od enega zagona na sliko.
    ukaz = [SOFFICE, "--headless", "--convert-to", "png", "--outdir", str(mapa)]
    ukaz += [str(p) for p in za_pretvorbo]
    try:
        subprocess.run(ukaz, capture_output=True, timeout=1800, check=False)
    except subprocess.TimeoutExpired:
        pass

    uspelo = spodletelo = 0
    for p in za_pretvorbo:
        png = p.with_suffix(".png")
        if png.exists() and png.stat().st_size > 0:
            p.unlink()  # izvirnik ni uporaben za .docx izvoz
            uspelo += 1
        else:
            spodletelo += 1
    return uspelo, spodletelo


def obrezi_bele_robove(mapa: Path) -> tuple[int, int]:
    """Obreže enobarvni (bel) rob okoli slik. Vrne (obrezanih, preskočenih).

    EMF iz Visia se pretvori na celo A4 platno, zato je vsebina pogosto <20 %
    slike — v testu potem zavzame pol strani belega prostora. Obrez naredimo
    samo, kadar je rezultat videti smiseln; sicer pustimo izvirnik.
    """
    obrezanih = preskocenih = 0
    for p in sorted(mapa.glob("*.png")):
        try:
            izhod = p.with_suffix(".trim.png")
            r = subprocess.run(
                ["magick", str(p), "-fuzz", "2%", "-trim", "+repage", str(izhod)],
                capture_output=True, timeout=60,
            )
            if r.returncode != 0 or not izhod.exists() or izhod.stat().st_size == 0:
                izhod.unlink(missing_ok=True)
                preskocenih += 1
                continue
            # varovalo: obrez ne sme dati degeneriranega izreza
            id_r = subprocess.run(["magick", "identify", "-format", "%w %h", str(izhod)],
                                  capture_output=True, text=True, timeout=30)
            try:
                w, h = (int(x) for x in id_r.stdout.split())
            except ValueError:
                izhod.unlink(missing_ok=True)
                preskocenih += 1
                continue
            if w < 20 or h < 20:
                izhod.unlink(missing_ok=True)
                preskocenih += 1
                continue
            izhod.replace(p)
            obrezanih += 1
        except Exception:
            preskocenih += 1
    return obrezanih, preskocenih


def faza_pripravi(samo: str | None = None):
    DELO_DIR.mkdir(exist_ok=True)
    datoteke = sorted(p for p in RIC_DIR.glob("*.docx")
                      if not p.stem.endswith("_brez_slik"))
    if samo:
        datoteke = [p for p in datoteke if samo.lower() in p.name.lower()]

    povzetek = []
    for i, pot in enumerate(datoteke, 1):
        print(f"[{i:3}/{len(datoteke)}] {pot.name}")
        rezultat = subprocess.run(
            [sys.executable, str(KOREN / "izvozi_slike.py"), str(pot)],
            capture_output=True, text=True, cwd=KOREN,
        )
        if rezultat.returncode != 0:
            print(f"    NAPAKA pri izvozu slik: {rezultat.stderr[:200]}")
            povzetek.append({"datoteka": pot.name, "napaka": rezultat.stderr[:200]})
            continue

        mapa_slik = SLIKE_DIR / pot.stem
        uspelo = spodletelo = obrezanih = 0
        if mapa_slik.exists():
            uspelo, spodletelo = _pretvori_vektorske(mapa_slik)
            obrezanih, _ = obrezi_bele_robove(mapa_slik)

        lahka = pot.parent / f"{pot.stem}_brez_slik.docx"
        vst = re.search(r"Vstavljenih .*?: (\d+)", rezultat.stdout)
        print(f"    placeholderjev: {vst.group(1) if vst else '?'} | "
              f"emf/wmf→png: {uspelo} ok, {spodletelo} spodletelo | "
              f"{lahka.stat().st_size/1e6:.2f} MB")
        povzetek.append({
            "datoteka": pot.name,
            "lahka": lahka.name,
            "placeholderjev": int(vst.group(1)) if vst else 0,
            "pretvorjenih": uspelo,
            "nepretvorjenih": spodletelo,
        })

    (DELO_DIR / "priprava.json").write_text(
        json.dumps(povzetek, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nPovzetek → {DELO_DIR/'priprava.json'}")


# ---------------------------------------------------------------------------
# Faza 2: razčlenitev na oštevilčene odstavke
# ---------------------------------------------------------------------------

def _tabela_v_markdown(tbl) -> str:
    """Pretvori w:tbl element v markdown tabelo."""
    vrstice = []
    for tr in tbl.findall(f"{W}tr"):
        celice = []
        for tc in tr.findall(f"{W}tc"):
            besedilo = " ".join(
                "".join(t.text or "" for t in p.iter(f"{W}t")).strip()
                for p in tc.findall(f"{W}p")
            ).strip()
            celice.append(besedilo.replace("|", "\\|"))
        if celice:
            vrstice.append("| " + " | ".join(celice) + " |")
    if not vrstice:
        return ""
    if len(vrstice) > 1:
        st = vrstice[0].count("|") - 1
        vrstice.insert(1, "|" + "---|" * st)
    return "\n".join(vrstice)


def _odstavek_besedilo(p) -> str:
    """Besedilo odstavka; tabulatorji ostanejo, ker ločujejo oznako od besedila.

    V RIC dokumentih je oznaka odgovora svoj run, za njim tabulator:
    'A' <tab> 'Celično dihanje.' — brez tabulatorja bi se zlepilo v
    'ACelično dihanje.', popravljanje tega z regexom nad zlepljenim besedilom pa
    ni varno ('B' + 'ATP pridobivajo…' izgleda enako kot 'BATP…').
    """
    deli = []
    for el in p.iter():
        if el.tag == f"{W}t":
            deli.append(el.text or "")
        elif el.tag == f"{W}tab":
            deli.append("\t")
    besedilo = "".join(deli).strip()

    # Oznaka odgovora / alineje: 'A<tab>besedilo' → 'A) besedilo'
    m = re.match(r"^([A-Da-dŠČŽ]|\d{1,2})\t+(.+)$", besedilo, re.DOTALL)
    if m:
        besedilo = f"{m.group(1)}) {m.group(2).lstrip()}"
    return besedilo.strip()


def razcleni_docx(pot: Path) -> list[str]:
    """Vrne odstavke v vrstnem redu dokumenta; tabele kot markdown bloke."""
    with zipfile.ZipFile(pot) as z:
        xml = z.read("word/document.xml")
    from xml.etree import ElementTree
    koren = ElementTree.fromstring(xml)
    body = koren.find(f"{W}body")
    if body is None:
        return []

    odstavki = []
    for el in body:
        if el.tag == f"{W}p":
            t = _odstavek_besedilo(el)
            if t:
                odstavki.append(t)
        elif el.tag == f"{W}tbl":
            md = _tabela_v_markdown(el)
            if md:
                odstavki.append(md)
    return odstavki


def faza_razcleni(samo: str | None = None):
    DELO_DIR.mkdir(exist_ok=True)
    (DELO_DIR / "odstavki").mkdir(exist_ok=True)
    datoteke = sorted(RIC_DIR.glob("*_brez_slik.docx"))
    if samo:
        datoteke = [p for p in datoteke if samo.lower() in p.name.lower()]

    skupaj = 0
    for i, pot in enumerate(datoteke, 1):
        ime = pot.stem.replace("_brez_slik", "")
        try:
            odstavki = razcleni_docx(pot)
        except Exception as e:
            print(f"[{i:3}] {ime[:45]:<47} NAPAKA: {e}")
            continue
        (DELO_DIR / "odstavki" / f"{ime}.json").write_text(
            json.dumps(odstavki, ensure_ascii=False, indent=1), encoding="utf-8")
        znakov = sum(len(o) for o in odstavki)
        skupaj += len(odstavki)
        print(f"[{i:3}] {ime[:45]:<47} {len(odstavki):6} odstavkov, {znakov:9,} znakov")
    print(f"\nSkupaj odstavkov: {skupaj:,} → {DELO_DIR/'odstavki'}/")


# ---------------------------------------------------------------------------
# Faza 3: klasifikacija — model vrne razpone odstavkov, ne besedila
# ---------------------------------------------------------------------------

MODEL = "claude-haiku-4-5"
CENA_VHOD = 1.00 / 1_000_000       # $ na token
CENA_IZHOD = 5.00 / 1_000_000
CENA_CACHE_READ = 0.10 / 1_000_000
CENA_CACHE_WRITE = 1.25 / 1_000_000

# Trda varovalka: nikoli ne porabi več od tega (ključ ima 15 USD).
MEJA_USD = 10.00

CILJ_TOKENOV_NA_KOS = 15000   # ~2.5 znaka/token → ~37k znakov
MAX_TOKENS_IZHOD = 8000       # razponi so kratki; 8k je z veliko rezerve


def _sistem_prompt() -> str:
    from klasificiraj import TAKSONOMIJA_BESEDILO
    return f"""Si pomočnik učitelja biologije. Dobiš oštevilčene odstavke iz maturitetne zbirke nalog (RIC) in določiš, kje se posamezna naloga začne in konča.

POMEMBNO: besedila NE prepisuj. Vrni samo številke odstavkov — besedilo izrežemo sami.

TAKSONOMIJA VSEBINE:
{TAKSONOMIJA_BESEDILO}

TIPI NALOG:
  Izbirni tip            — naloga z možnostmi A/B/C/D
  Kratki odgovor         — kratek odprt odgovor (1–3 stavki)
  Daljši odgovor         — razširjen odprt odgovor ali esej
  Dopolnjevanje/ujemanje — dopolni praznine, poveži, razvrsti, tabela

KAJ JE ENA NALOGA:
- Oštevilčena postavka (npr. "12.") skupaj z VSEM, kar spada zraven: uvodnim
  besedilom, sliko [SLIKA:...], virom slike, tabelo, možnostmi A/B/C/D in vsemi
  podvprašanji. Podvprašanja so nerazumljiva iz konteksta, zato NIKOLI ne
  razbijaj naloge s podvprašanji na več nalog.
- "od" je prvi odstavek naloge (vključno z uvodnim besedilom pred številko, če
  očitno spada zraven), "do" je zadnji.

KAJ NI NALOGA (izpusti, ne vračaj):
- naslovi razdelkov in glave (npr. "191. Raziskovanje in poskusi" brez vprašanja)
- vrstice "NAPAKA: datoteka ne obstaja: ..."
- bloki rešitev ("Rešitev: A", "Rešitev8.naloga", "x.1 ...")
- osamljeni viri slik brez pripadajočega vprašanja

REŠITEV NE DOLOČAJ. Bloke rešitev samo izpusti — pripis rešitev nalogam se
naredi posebej v kodi, ker zahteva natančno ujemanje po številu.

Vrni SAMO JSON array, brez razlag:
[{{"od": 12, "do": 18, "vsebina_koda": "XX.YY.ZZ", "tip_naziv": "Izbirni tip"}}]"""


def _kosi(odstavki: list[str], zacetek: int, ciljni_znaki: int) -> tuple[int, str]:
    """Zloži oštevilčene odstavke od 'zacetek' do ~ciljni_znaki. Vrne (konec, besedilo)."""
    kos, znakov, i = [], 0, zacetek
    while i < len(odstavki) and znakov < ciljni_znaki:
        vrstica = f"[{i+1}] {odstavki[i]}"
        kos.append(vrstica)
        znakov += len(vrstica)
        i += 1
    return i, "\n".join(kos)


def _izlusci_json(odgovor: str) -> list[dict]:
    """Izlušči JSON array(e) iz odgovora.

    Model občasno vrne več zaporednih arrayev ali doda besedilo za njimi; rezanje
    od prvega '[' do zadnjega ']' takrat da neveljaven JSON. Zato beremo z
    raw_decode in seštejemo vse arraye, ki jih najdemo.
    """
    t = odgovor.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```\s*$", "", t)

    dekoder = json.JSONDecoder()
    najdeno: list[dict] = []
    videl_array = False
    i = t.find("[")
    while i != -1:
        try:
            vrednost, konec = dekoder.raw_decode(t, i)
        except json.JSONDecodeError:
            i = t.find("[", i + 1)
            continue
        if isinstance(vrednost, list):
            videl_array = True
            najdeno += [x for x in vrednost if isinstance(x, dict)]
        i = t.find("[", max(konec, i + 1))

    # Prazen array je veljaven odgovor: v tem kosu ni nalog (npr. sami bloki
    # rešitev). Napaka je samo, če arraya sploh ni.
    if not videl_array:
        raise ValueError(f"ni JSON arraya v odgovoru: {t[:200]}")
    return najdeno


class Stroskovnik:
    def __init__(self):
        self.vhod = self.izhod = self.cache_r = self.cache_w = 0

    def dodaj(self, u):
        self.vhod += u.input_tokens
        self.izhod += u.output_tokens
        self.cache_r += getattr(u, "cache_read_input_tokens", 0) or 0
        self.cache_w += getattr(u, "cache_creation_input_tokens", 0) or 0

    @property
    def usd(self):
        return (self.vhod * CENA_VHOD + self.izhod * CENA_IZHOD
                + self.cache_r * CENA_CACHE_READ + self.cache_w * CENA_CACHE_WRITE)

    def povzetek(self):
        return (f"vhod {self.vhod:,} | izhod {self.izhod:,} | "
                f"cache r/w {self.cache_r:,}/{self.cache_w:,} | ${self.usd:.3f}")


def faza_klasificiraj(samo: str | None = None, meja: float = MEJA_USD):
    import anthropic
    from dotenv import load_dotenv
    load_dotenv(KOREN / ".env", override=True)
    odjemalec = anthropic.Anthropic()

    (DELO_DIR / "razponi").mkdir(parents=True, exist_ok=True)
    datoteke = sorted((DELO_DIR / "odstavki").glob("*.json"))
    if samo:
        datoteke = [p for p in datoteke if samo.lower() in p.name.lower()]

    sistem = [{"type": "text", "text": _sistem_prompt(),
               "cache_control": {"type": "ephemeral"}}]
    strosek = Stroskovnik()
    ciljni_znaki = CILJ_TOKENOV_NA_KOS * 25 // 10   # ~2.5 znaka/token

    for n, pot in enumerate(datoteke, 1):
        ime = pot.stem
        izhod_pot = DELO_DIR / "razponi" / f"{ime}.json"
        if izhod_pot.exists():
            print(f"[{n:3}/{len(datoteke)}] {ime[:42]:<44} že obdelano, preskok")
            continue

        odstavki = json.loads(pot.read_text(encoding="utf-8"))
        vse_naloge, i, kos_st = [], 0, 0

        while i < len(odstavki):
            if strosek.usd >= meja:
                print(f"\n!! USTAVLJENO: dosežena meja ${meja:.2f} ({strosek.povzetek()})")
                return
            konec, besedilo_kosa = _kosi(odstavki, i, ciljni_znaki)
            zadnji_kos = konec >= len(odstavki)
            kos_st += 1

            try:
                odg = odjemalec.messages.create(
                    model=MODEL,
                    max_tokens=MAX_TOKENS_IZHOD,
                    system=sistem,
                    messages=[{"role": "user", "content": besedilo_kosa}],
                )
            except Exception as e:
                print(f"    kos {kos_st}: NAPAKA API ({e}); preskočim odstavke {i+1}–{konec}")
                i = konec
                continue

            strosek.dodaj(odg.usage)
            try:
                naloge = _izlusci_json(odg.content[0].text)
            except Exception as e:
                print(f"    kos {kos_st}: neveljaven JSON ({e}); preskočim {i+1}–{konec}")
                i = konec
                continue

            naloge = [x for x in naloge if isinstance(x.get("od"), int)
                      and isinstance(x.get("do"), int) and x["do"] >= x["od"]]

            if not naloge:
                i = konec
                continue

            zadnja = naloge[-1]
            if zadnji_kos:
                vse_naloge += naloge
                i = konec
            elif zadnja["do"] < konec - 3:
                # Za zadnjo nalogo je v kosu ostalo še nekaj odstavkov, ki jih
                # model ni vključil (npr. blok rešitev) — torej je videl njen
                # konec in ni odrezana. Obdržimo jo in nadaljujemo za njo.
                vse_naloge += naloge
                i = max(zadnja["do"], i + 1)
            else:
                # Zadnja naloga sega do meje kosa in je lahko odrezana:
                # zavržemo jo in naslednji kos začnemo pri njej.
                vse_naloge += naloge[:-1]
                nov_i = max(zadnja["od"] - 1, i + 1)   # -1: 1-osnovano → 0-osnovano
                i = nov_i if nov_i > i else konec

        izhod_pot.write_text(json.dumps(vse_naloge, ensure_ascii=False, indent=1),
                             encoding="utf-8")
        print(f"[{n:3}/{len(datoteke)}] {ime[:42]:<44} {len(odstavki):5} odst. → "
              f"{len(vse_naloge):4} nalog ({kos_st} kosov) | ${strosek.usd:.3f}")

    print(f"\nSkupaj: {strosek.povzetek()}")


# ---------------------------------------------------------------------------
# Faza 4: uvoz v bazo — rešitve deterministično, dedup 80 %
# ---------------------------------------------------------------------------

PRAG_PODOBNOSTI = 0.80   # Vitalova zahteva: >80 % enako → obdrži eno različico


def _normaliziraj(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())


def _besede(s: str) -> set[str]:
    return set(re.findall(r"\w+", _normaliziraj(s)))


def _odstrani_zaporedno(besedilo: str) -> str:
    """Odstrani vodilno zaporedno številko naloge ('12.' / '12.\\t') — v testu
    številčenje doda generator."""
    return re.sub(r"^\d{1,3}\.\s*", "", besedilo, count=1).strip()


def preslikaj_resitve(odstavki: list[str], naloge: list[dict]) -> dict[int, str]:
    """Pripiše rešitve nalogam SAMO tam, kjer je preslikava dokazljiva.

    Dva varna vzorca:
      1. Označena: 'Rešitev8.naloga' → naloga s številko 8 (številka je v besedilu).
      2. Blok N zaporednih 'Rešitev: X' takoj za skupino N nalog → 1:1 po vrsti.
    Vse drugo pusti prazno — napačna rešitev je slabša od nobene.
    """
    resitve: dict[int, str] = {}          # indeks naloge → rešitev
    je_resitev = [bool(re.match(r"^Rešitev", o)) for o in odstavki]

    # --- vzorec 1: eksplicitno oštevilčene rešitve ---
    # Dokumenti so zlepljeni iz več izpitnih pol, zato se številke nalog
    # ponavljajo. Preslikamo samo, kadar je številka v dokumentu enolična —
    # sicer ne vemo, kateri od nalog z isto številko rešitev pripada.
    pojavitve: dict[int, list[int]] = {}
    for idx, n in enumerate(naloge):
        m = re.match(r"^(\d{1,3})\.", odstavki[n["od"] - 1])
        if m:
            pojavitve.setdefault(int(m.group(1)), []).append(idx)
    st_naloge_v_besedilu = {st: idxs[0] for st, idxs in pojavitve.items()
                            if len(idxs) == 1}

    for i, o in enumerate(odstavki):
        # 'Rešitev13.\tnaloga' in 'Rešitev36. Užitne rastline: koruza' — oboje
        # nedvoumno imenuje številko naloge, ki ji rešitev pripada.
        m = re.match(r"^Rešitev\s*(\d{1,3})\.", o)
        if not m:
            continue
        st = int(m.group(1))
        if st not in st_naloge_v_besedilu:
            continue
        # rešitev so vsi odstavki do naslednjega 'Rešitev' ali konca
        konec = i + 1
        while konec < len(odstavki) and not je_resitev[konec]:
            konec += 1
        telo = "\n".join(odstavki[i + 1:konec]).strip()
        if telo:
            resitve.setdefault(st_naloge_v_besedilu[st], telo)

    # --- vzorec 2: blok 'Rešitev: X' takoj za skupino nalog ---
    # Skupina = naloge med koncem prejšnjega bloka rešitev (ali začetkom
    # dokumenta) in tem blokom. Preslikamo SAMO, če je nalog natanko toliko kot
    # rešitev. Če jih je 15 in rešitev 14, ne vemo, katera naloga je brez —
    # in takrat rajši ne pripišemo nobene.
    meja_skupine = 0            # 1-osnovan indeks zadnjega odstavka prejšnjega bloka
    i = 0
    while i < len(odstavki):
        if not (je_resitev[i] and re.match(r"^Rešitev:\s*\S", odstavki[i])):
            i += 1
            continue
        j, blok = i, []
        while j < len(odstavki) and re.match(r"^Rešitev:\s*\S", odstavki[j]):
            blok.append(re.sub(r"^Rešitev:\s*", "", odstavki[j]).strip())
            j += 1

        skupina = [k for k, n in enumerate(naloge)
                   if n["od"] > meja_skupine and n["do"] < i + 1]
        if len(skupina) == len(blok) and skupina and naloge[skupina[-1]]["do"] == i:
            for idx, r in zip(skupina, blok):
                resitve.setdefault(idx, r)
        meja_skupine = j
        i = j

    return resitve


def je_blok_resitev(besedilo: str) -> bool:
    """Ali je to blok rešitev in ne naloga?

    Model kljub navodilu občasno vrne blok rešitev kot nalogo (v vzorcu 15 %).
    Oba vzorca sta v besedilu nedvoumna, zato ju odfiltriramo v kodi in se ne
    zanašamo na prompt — učitelj v testu ne sme dobiti odgovorov namesto vprašanj.
    """
    t = besedilo.lstrip()
    if t.startswith("Rešitev"):
        return True
    # razpredelnica rešitev iz RIC predloge
    if re.search(r"\|\s*Naloga\s*\|\s*Točke\s*\|", besedilo):
        return True
    return False


def _brez_prekrivanj(naloge: list[dict]) -> list[dict]:
    """Odstrani prekrivajoče razpone (artefakt prenosa čez mejo kosa).

    Naloge se po naravi ne prekrivajo. Ob prekrivanju obdržimo daljši razpon —
    krajši je praviloma odrezan ostanek iste naloge.
    """
    urejene = sorted(naloge, key=lambda n: (n["od"], -(n["do"] - n["od"])))
    rezultat: list[dict] = []
    for n in urejene:
        if rezultat and n["od"] <= rezultat[-1]["do"]:
            if n["do"] > rezultat[-1]["do"] and n["od"] == rezultat[-1]["od"]:
                rezultat[-1] = n      # isti začetek, daljši razpon
            continue
        rezultat.append(n)
    return rezultat


def _resi_sliko(ime: str, mapa: str) -> str | None:
    """Vrne '<mapa>/<datoteka>' za placeholder; upošteva emf/wmf → png pretvorbo."""
    kandidat = SLIKE_DIR / mapa / ime
    if kandidat.exists():
        return f"{mapa}/{ime}"
    p = Path(ime)
    if p.suffix.lower() in ZA_PRETVORBO:
        png = SLIKE_DIR / mapa / f"{p.stem}.png"
        if png.exists():
            return f"{mapa}/{p.stem}.png"
    return None


def faza_uvozi(samo: str | None = None, poskusno: bool = False):
    from klasificiraj import TIPI
    conn = sqlite3.connect(DB_POT)
    conn.row_factory = sqlite3.Row

    # Shema: stolpca za rešitev in vir naloge (matura vs. šolski test)
    stolpci = {r["name"] for r in conn.execute("PRAGMA table_info(naloga)")}
    if "resitev" not in stolpci:
        conn.execute("ALTER TABLE naloga ADD COLUMN resitev TEXT")
        print("shema: dodan stolpec naloga.resitev")
    if "vir_tip" not in stolpci:
        conn.execute("ALTER TABLE naloga ADD COLUMN vir_tip TEXT")
        print("shema: dodan stolpec naloga.vir_tip")
    conn.commit()

    tipi = {n: i for i, n in conn.execute("SELECT id, naziv FROM tip_naloge").fetchall()}
    tipi = {naziv: id_ for id_, naziv in conn.execute("SELECT id, naziv FROM tip_naloge")}
    veljavne_kode = {k for (k,) in conn.execute("SELECT koda FROM vsebina")}

    # Obstoječe RIC naloge (za dedup ob ponovnem zagonu)
    obstojece = [(r["id"], r["besedilo"]) for r in
                 conn.execute("SELECT id, besedilo FROM naloga WHERE vir_tip = 'matura'")]
    indeks: dict[str, set[int]] = {}
    zbirka: list[tuple[set[str], str]] = []
    for _, b in obstojece:
        bes = _besede(b)
        zbirka.append((bes, _normaliziraj(b)))
        for w in bes:
            indeks.setdefault(w, set()).add(len(zbirka) - 1)

    def je_duplikat(besedilo: str) -> bool:
        bes = _besede(besedilo)
        if not bes:
            return False
        norm = _normaliziraj(besedilo)
        # Kandidate iščemo prek obrnjenega indeksa, a samo po najredkejših
        # besedah: pogoste ("je", "in") imajo ogromne sezname in bi iskanje
        # kandidatov spremenile v pregled cele zbirke. Dve ≥80 % podobni
        # besedili si delita tudi redke besede, zato recall s tem ne trpi.
        redke = sorted(bes, key=lambda w: len(indeks.get(w, ())))[:15]
        stevec: dict[int, int] = {}
        for w in redke:
            for k in indeks.get(w, ()):
                stevec[k] = stevec.get(k, 0) + 1
        for k, skupnih in stevec.items():
            druge, dnorm = zbirka[k]
            jac = skupnih / len(bes | druge)
            if jac < 0.5:
                continue
            if SequenceMatcher(None, norm, dnorm).ratio() >= PRAG_PODOBNOSTI:
                return True
        return False

    def zabelezi(besedilo: str):
        bes = _besede(besedilo)
        zbirka.append((bes, _normaliziraj(besedilo)))
        for w in bes:
            indeks.setdefault(w, set()).add(len(zbirka) - 1)

    datoteke = sorted((DELO_DIR / "razponi").glob("*.json"))
    if samo:
        datoteke = [p for p in datoteke if samo.lower() in p.name.lower()]

    sk_vstavljenih = sk_dvojnikov = sk_resitev = sk_slik = sk_brez_slike = 0
    sk_izlocenih_resitev = [0]   # v seznamu, ker se šteje v notranji zanki

    for n, pot in enumerate(datoteke, 1):
        ime = pot.stem
        odstavki = json.loads((DELO_DIR / "odstavki" / f"{ime}.json").read_text(encoding="utf-8"))
        naloge = json.loads(pot.read_text(encoding="utf-8"))
        # Model občasno vrne razpon čez konec dokumenta — odstranimo neveljavne
        # takoj, ker jih uporabi že preslikava rešitev.
        naloge = [n for n in naloge if 1 <= n["od"] <= n["do"] <= len(odstavki)]
        naloge = _brez_prekrivanj(naloge)
        resitve = preslikaj_resitve(odstavki, naloge)

        vstavljenih = dvojnikov = 0
        for idx, nal in enumerate(naloge):
            od, do = nal["od"], nal["do"]
            if not (1 <= od <= do <= len(odstavki)):
                continue
            besedilo = _odstrani_zaporedno("\n".join(odstavki[od - 1:do]))
            if len(besedilo) < 15:
                continue
            if je_blok_resitev(besedilo):
                sk_izlocenih_resitev[0] += 1
                continue
            if je_duplikat(besedilo):
                dvojnikov += 1
                continue

            # slike: preveri obstoj in popravi končnico po pretvorbi
            slike = []
            for ref in re.findall(r"\[SLIKA:([^\]]+)\]", besedilo):
                resena = _resi_sliko(ref.strip(), ime)
                if resena:
                    slike.append((ref.strip(), resena))
                    if not ref.strip().endswith(Path(resena).suffix):
                        besedilo = besedilo.replace(f"[SLIKA:{ref}]",
                                                    f"[SLIKA:{Path(resena).name}]")
                else:
                    besedilo = besedilo.replace(f"[SLIKA:{ref}]", "")
                    sk_brez_slike += 1
            besedilo = re.sub(r"\n{3,}", "\n\n", besedilo).strip()

            koda = nal.get("vsebina_koda")
            koda = koda if koda in veljavne_kode else None
            tip_id = tipi.get(nal.get("tip_naziv") or "")
            resitev = resitve.get(idx)

            if not poskusno:
                cur = conn.execute(
                    """INSERT INTO naloga (besedilo, vsebina_koda, tip_id, ima_sliko,
                                           vir_datoteka, resitev, vir_tip)
                       VALUES (?,?,?,?,?,?,'matura')""",
                    (besedilo, koda, tip_id, 1 if slike else 0, f"RIC/{ime}.docx", resitev),
                )
                for vr, (_, rel) in enumerate(slike, 1):
                    conn.execute(
                        "INSERT INTO slika (naloga_id, ime_datoteke, vrstni_red) VALUES (?,?,?)",
                        (cur.lastrowid, rel, vr))

            zabelezi(besedilo)
            vstavljenih += 1
            sk_slik += len(slike)
            if resitev:
                sk_resitev += 1

        if not poskusno:
            conn.commit()
        sk_vstavljenih += vstavljenih
        sk_dvojnikov += dvojnikov
        print(f"[{n:3}/{len(datoteke)}] {ime[:40]:<42} {len(naloge):4} nalog → "
              f"{vstavljenih:4} vstavljenih, {dvojnikov:3} dvojnikov, "
              f"{sum(1 for i in range(len(naloge)) if i in resitve):3} rešitev")

    print(f"\n{'POSKUSNO — nič ni zapisano' if poskusno else 'ZAPISANO V BAZO'}")
    print(f"  vstavljenih : {sk_vstavljenih:,}")
    print(f"  dvojnikov   : {sk_dvojnikov:,} (≥{PRAG_PODOBNOSTI:.0%} podobnih)")
    print(f"  z rešitvijo : {sk_resitev:,}")
    print(f"  slik        : {sk_slik:,} (manjkajočih referenc: {sk_brez_slike})")
    print(f"  izločenih blokov rešitev: {sk_izlocenih_resitev[0]:,}")
    conn.close()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("faza", choices=["pripravi", "razcleni", "klasificiraj", "uvozi"])
    p.add_argument("--samo", metavar="NIZ", help="obdelaj samo datoteke z NIZ v imenu")
    p.add_argument("--meja", type=float, default=MEJA_USD,
                   help=f"trda meja stroška v USD (privzeto {MEJA_USD})")
    p.add_argument("--poskusno", action="store_true",
                   help="pri uvozu samo poročaj, ne piši v bazo")
    a = p.parse_args()

    if a.faza == "pripravi":
        faza_pripravi(a.samo)
    elif a.faza == "razcleni":
        faza_razcleni(a.samo)
    elif a.faza == "klasificiraj":
        faza_klasificiraj(a.samo, a.meja)
    elif a.faza == "uvozi":
        faza_uvozi(a.samo, a.poskusno)


if __name__ == "__main__":
    main()

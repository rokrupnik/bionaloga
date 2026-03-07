"""
Klasifikacija nalog iz .docx datotek v mapi input/ z modelom claude-haiku-4-5.

Uporaba:
    python klasificiraj.py               # obdela vse nove datoteke
    python klasificiraj.py --vzorec 10   # samo prvih 10 (za preizkus)
    python klasificiraj.py --datoteka "ime.docx"  # samo eno datoteko

Rezultati se sproti shranjujejo v:
    klasifikacije/<ime_datoteke>.json    # surovi JSON odgovor
    baza.db                             # naloge v SQLite bazi
"""

import argparse
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import zipfile
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from xml.etree import ElementTree

import anthropic
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Poti
# ---------------------------------------------------------------------------

KOREN = Path(__file__).parent
DB_POT = KOREN / "baza.db"
INPUT_DIR = KOREN / "input"
DONE_DIR = INPUT_DIR / "done"
KLASIFIKACIJE_DIR = KOREN / "klasifikacije"
SLIKE_DIR = KOREN / "slike"
MODEL = "claude-haiku-4-5-20251001"

# ---------------------------------------------------------------------------
# Shema baze
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS vsebina (
    koda TEXT PRIMARY KEY,
    naziv TEXT NOT NULL,
    nadrejena_koda TEXT,
    raven INTEGER NOT NULL,
    FOREIGN KEY (nadrejena_koda) REFERENCES vsebina(koda)
);

CREATE TABLE IF NOT EXISTS tip_naloge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naziv TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS naloga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    besedilo TEXT NOT NULL,
    vsebina_koda TEXT,
    tip_id INTEGER,
    ima_sliko BOOLEAN DEFAULT 0,
    tezavnost INTEGER,
    vir_datoteka TEXT,
    datum_uvoza DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vsebina_koda) REFERENCES vsebina(koda),
    FOREIGN KEY (tip_id) REFERENCES tip_naloge(id)
);

CREATE TABLE IF NOT EXISTS slika (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naloga_id INTEGER NOT NULL,
    ime_datoteke TEXT NOT NULL,
    vrstni_red INTEGER DEFAULT 1,
    FOREIGN KEY (naloga_id) REFERENCES naloga(id)
);
"""

VSEBINA = [
    ("01.00.00", "Življenje na Zemlji",               None,       1),
    ("02.00.00", "Celica kot živi sistem",             None,       1),
    ("03.00.00", "Dedovanje",                          None,       1),
    ("04.00.00", "Evolucija",                          None,       1),
    ("05.00.00", "Organizem kot živi sistem",          None,       1),
    ("06.00.00", "Ekologija",                          None,       1),
    ("07.00.00", "Biologija kot naravoslovna znanost", None,       1),
    ("01.01.00", "Biologija – veda o življenju",       "01.00.00", 2),
    ("01.02.00", "Temeljne lastnosti živega",          "01.00.00", 2),
    ("02.01.00", "Celica kot osnovna enota organizmov","02.00.00", 2),
    ("02.02.00", "Presnova",                           "02.00.00", 2),
    ("02.01.01", "Biotske membrane",                   "02.01.00", 3),
    ("02.01.02", "Celični organeli",                   "02.01.00", 3),
    ("02.02.01", "Zgradba in delovanje encimov in drugih beljakovin", "02.02.00", 3),
    ("02.02.02", "Energijsko bogate snovi",            "02.02.00", 3),
    ("02.02.03", "Glikoliza in vrenje",                "02.02.00", 3),
    ("02.02.04", "Celično dihanje",                    "02.02.00", 3),
    ("02.02.05", "Fotosinteza",                        "02.02.00", 3),
    ("02.02.06", "Presnovne povezave",                 "02.02.00", 3),
    ("02.02.07", "Celična signalizacija, transport in regulacija celičnih procesov", "02.02.00", 3),
    ("02.02.08", "Nukleinske kisline",                 "02.02.00", 3),
    ("03.00.01", "Celični cikel",                      "03.00.00", 3),
    ("03.00.02", "Gensko uravnavanje",                 "03.00.00", 3),
    ("03.00.03", "Spreminjanje dedne snovi",           "03.00.00", 3),
    ("03.00.04", "Načini dedovanja",                   "03.00.00", 3),
    ("04.00.01", "Nastanek in razvoj življenja",       "04.00.00", 3),
    ("04.00.02", "Mehanizmi evolucije",                "04.00.00", 3),
    ("04.00.03", "Evolucija človeka",                  "04.00.00", 3),
    ("04.00.04", "Razvrščanje organizmov v sisteme",   "04.00.00", 3),
    ("05.01.00", "Bakterije",                          "05.00.00", 2),
    ("05.02.00", "Glive",                              "05.00.00", 2),
    ("05.03.00", "Rastline",                           "05.00.00", 2),
    ("05.04.00", "Živali",                             "05.00.00", 2),
    ("05.01.01", "Zgradba, razmnoževanje in delovanje bakterij", "05.01.00", 3),
    ("05.02.01", "Zgradba in prehranjevanje gliv",     "05.02.00", 3),
    ("05.03.01", "Zgradba in delovanje rastlin",       "05.03.00", 3),
    ("05.03.02", "Rast in razvoj rastlin",             "05.03.00", 3),
    ("05.03.03", "Razmnoževanje rastlin",              "05.03.00", 3),
    ("05.03.04", "Strategije preživetja pri rastlinah","05.03.00", 3),
    ("05.04.01", "Zgradba in delovanje človeka in drugih živali", "05.04.00", 3),
    ("05.04.02", "Transportni sistemi",                "05.04.00", 3),
    ("05.04.03", "Imunski sistem",                     "05.04.00", 3),
    ("05.04.04", "Dihalni sistemi",                    "05.04.00", 3),
    ("05.04.05", "Prebavni sistemi",                   "05.04.00", 3),
    ("05.04.06", "Izločalni sistem",                   "05.04.00", 3),
    ("05.04.07", "Regulacijski sistemi",               "05.04.00", 3),
    ("05.04.08", "Hormonski sistem",                   "05.04.00", 3),
    ("05.04.09", "Živčni sistem",                      "05.04.00", 3),
    ("05.04.10", "Sprejemanje dražljajev – čutila",    "05.04.00", 3),
    ("05.04.11", "Zaščita, opora in gibanje",          "05.04.00", 3),
    ("05.04.12", "Razmnoževanje, rast in razvoj",      "05.04.00", 3),
    ("06.00.01", "Ekologija kot področje biologije",   "06.00.00", 3),
    ("06.00.02", "Osebki in populacije",               "06.00.00", 3),
    ("06.00.03", "Delovanje ekosistema",               "06.00.00", 3),
    ("06.00.04", "Ekosistemi in biosfera",             "06.00.00", 3),
    ("06.00.05", "Človek in narava",                   "06.00.00", 3),
    ("07.00.01", "Raziskovanje in poskusi",            "07.00.00", 3),
]

TIPI = ["Izbirni tip", "Kratki odgovor", "Daljši odgovor", "Dopolnjevanje/ujemanje"]

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

TAKSONOMIJA_BESEDILO = "\n".join(
    f"  {koda} — {naziv}" for koda, naziv, _, _ in VSEBINA
)

SISTEM_PROMPT = f"""Si pomočnik učitelja biologije. Tvoja naloga je razdeliti test biologije na posamezne naloge in vsako klasificirati.

TAKSONOMIJA VSEBINE:
{TAKSONOMIJA_BESEDILO}

TIPI NALOG:
  Izbirni tip          — naloga z možnostmi A/B/C/D
  Kratki odgovor       — kratek odprt odgovor (1–3 stavki)
  Daljši odgovor       — razširjen odprt odgovor ali esej
  Dopolnjevanje/ujemanje — dopolni praznine, poveži, razvrsti, tabela

NAVODILA:
- Razdeli dokument na posamezne naloge. Vsaka oštevilčena postavka je ena naloga.
- Naloge s podtočkami (a, b, c...) obravnavaj kot eno nalogo, razen če so vsebinsko povsem neodvisne.
- Vključi celotno besedilo naloge, vključno z vsemi možnostmi in podvprašanji.
- Če naloga vsebuje tabelo, jo zapiši kot markdown tabelo.
- Besedilo začni takoj z vsebino naloge, brez zaporedne številke.
- Izberi vsebinsko kodo na ravni 3 (XX.YY.ZZ), če je mogoče. Sicer uporabi raven 2 ali 1.
- Če besedilo vsebuje oznake [SLIKA:ime_datoteke], jih OHRANI TOČNO TAKO V BESEDILU naloge — ne briši, ne parafraziraj, ne zamenjaj z opisom.
- ima_sliko nastavi na true, če besedilo vsebuje [SLIKA:...] placeholder ali omenja sliko/graf/shemo.
- Vrni SAMO JSON array, brez dodatnega besedila ali razlag.

FORMAT IZHODA:
[
  {{
    "besedilo": "celotno besedilo naloge",
    "vsebina_koda": "XX.YY.ZZ",
    "tip_naziv": "Izbirni tip|Kratki odgovor|Daljši odgovor|Dopolnjevanje/ujemanje",
    "ima_sliko": true
  }}
]"""

# ---------------------------------------------------------------------------
# Pomožne funkcije
# ---------------------------------------------------------------------------

def inicializiraj_bazo(conn: sqlite3.Connection):
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT OR IGNORE INTO vsebina (koda, naziv, nadrejena_koda, raven) VALUES (?,?,?,?)",
        VSEBINA,
    )
    for tip in TIPI:
        conn.execute("INSERT OR IGNORE INTO tip_naloge (naziv) VALUES (?)", (tip,))
    conn.commit()


def pridobi_ze_obdelane(conn: sqlite3.Connection) -> set[str]:
    # Iz baze
    vrstice = conn.execute("SELECT DISTINCT vir_datoteka FROM naloga WHERE vir_datoteka IS NOT NULL").fetchall()
    v_bazi = {v[0] for v in vrstice}
    # Iz mape done/ (fizično premaknjene datoteke)
    v_done = {p.name for p in DONE_DIR.glob("*.docx")} if DONE_DIR.exists() else set()
    return v_bazi | v_done


SOFFICE = next(
    (p for p in [
        "soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ] if shutil.which(p) or Path(p).exists()),
    None,
)


def _konvertiraj_emf(pot: Path) -> Path | None:
    """Pretvori .emf/.wmf v .png z LibreOffice. Vrne pot do .png ali None ob napaki."""
    if SOFFICE is None:
        return None
    png_pot = pot.with_suffix(".png")
    if png_pot.exists():
        return png_pot
    try:
        subprocess.run(
            [SOFFICE, "--headless", "--convert-to", "png", "--outdir", str(pot.parent), str(pot)],
            check=True, capture_output=True, timeout=30,
        )
        return png_pot if png_pot.exists() else None
    except Exception:
        return None


def _preberi_relacije(rels_xml: str) -> dict:
    """Vrne {rId: originalno_ime} za slike iz relacijske datoteke."""
    rid_to_file = {}
    for m in re.finditer(r'<Relationship\s+Id="(rId\d+)"[^>]*Target="(media/[^"]+)"', rels_xml):
        rid_to_file[m.group(1)] = Path(m.group(2)).name
    return rid_to_file


def _zamenjaj_slike(doc_xml: str, rid_to_ime: dict) -> str:
    """Zamenja w:drawing in w:pict z [SLIKA:ime] placeholder-ji."""

    def placeholder(match):
        blok = match.group(0)
        rid_m = re.search(r'r:embed="(rId\d+)"', blok) or re.search(r'r:link="(rId\d+)"', blok) or re.search(r'r:id="(rId\d+)"', blok)
        if rid_m:
            ime = rid_to_ime.get(rid_m.group(1), f"neznana_{rid_m.group(1)}")
            return f'<w:r><w:t>[SLIKA:{ime}]</w:t></w:r>'
        return '<w:r><w:t>[SLIKA:neznana]</w:t></w:r>'

    doc_xml = re.sub(r'<w:drawing[ >].*?</w:drawing>', placeholder, doc_xml, flags=re.DOTALL)
    doc_xml = re.sub(r'<w:pict>.*?</w:pict>', placeholder, doc_xml, flags=re.DOTALL)
    return doc_xml


def ekstrahiraj_besedilo_in_slike(pot: Path) -> tuple[str, dict]:
    """Izvleče besedilo z [SLIKA:ime] placeholder-ji in shrani slike v slike/ (brez podmap).

    Slike poimenuje kot <timestamp>_<counter>.<ext> — brez presledkov, brez podmap.
    Vrne (besedilo, {ime_v_placeholderju: ime_datoteke_v_slike_dir}).
    """
    ns = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    SLIKE_DIR.mkdir(exist_ok=True)

    try:
        with zipfile.ZipFile(pot) as z:
            try:
                rels_xml = z.read("word/_rels/document.xml.rels").decode("utf-8")
                rid_to_orig = _preberi_relacije(rels_xml)
            except KeyError:
                rid_to_orig = {}

            # Izvozi slike z novimi imeni ts_001.ext, ts_002.ext, ...
            # rid_to_ime: rId → novo ime datoteke (kar bo v placeholderju)
            rid_to_ime = {}
            for counter, (rid, orig_ime) in enumerate(rid_to_orig.items(), 1):
                ext = Path(orig_ime).suffix.lower()
                novo_ime = f"{ts}_{counter:03d}{ext}"
                cilj = SLIKE_DIR / novo_ime
                with z.open(f"word/media/{orig_ime}") as src, open(cilj, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                # Konvertiraj .emf/.wmf → .png takoj
                if ext in {".emf", ".wmf"}:
                    png = _konvertiraj_emf(cilj)
                    if png:
                        cilj.unlink()
                        novo_ime = png.name
                rid_to_ime[rid] = novo_ime

            # Besedilo z [SLIKA:novo_ime] placeholder-ji
            doc_xml = z.read("word/document.xml").decode("utf-8")
            doc_xml = _zamenjaj_slike(doc_xml, rid_to_ime)

            koren = ElementTree.fromstring(doc_xml)
            odstavki = []
            for odst in koren.iter(f"{{{ns}}}p"):
                vrstica = "".join(t.text or "" for t in odst.iter(f"{{{ns}}}t"))
                if vrstica.strip():
                    odstavki.append(vrstica.strip())

    except Exception as e:
        raise RuntimeError(f"Napaka pri branju {pot.name}: {e}") from e

    # slike_map: ime_v_placeholderju → ime_datoteke (enako, ker ni podmap)
    slike_map = {novo: novo for novo in rid_to_ime.values()}
    return "\n".join(odstavki), slike_map


def klici_api(odjemalec: anthropic.Anthropic, besedilo: str) -> list[dict]:
    """Pošlje besedilo v API in vrne seznam nalog kot Python seznam."""
    sporocilo = odjemalec.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SISTEM_PROMPT,
        messages=[{"role": "user", "content": f"Klasificiraj naloge iz tega testa:\n\n{besedilo}"}],
    )
    odgovor = sporocilo.content[0].text.strip()

    # Izvleči JSON (včasih model doda ```json ... ```)
    if odgovor.startswith("```"):
        vrstice = odgovor.splitlines()
        odgovor = "\n".join(vrstice[1:-1] if vrstice[-1].strip() == "```" else vrstice[1:])

    return json.loads(odgovor)


PRAG_PODOBNOSTI = 0.92  # naloge z ujemanjem >= 92 % se štejejo za duplicate


def _normaliziraj(besedilo: str) -> str:
    """Odstrani odvečne presledke in pretvori v male črke za primerjavo."""
    return " ".join(besedilo.split()).lower()


def _ze_obstaja(conn: sqlite3.Connection, besedilo: str) -> bool:
    """Vrne True, če v bazi že obstaja dovolj podobna naloga.

    Segment (ena vrstica) primerjamo samo s PRVO VRSTICO vsakega DB zapisa.
    Pre-filter: LIKE prvih_30_znakov% na prvi vrstici → fuzzy primerjava.
    """
    norm = _normaliziraj(besedilo)
    kljuc = norm[:30].replace("%", "").replace("_", "")
    if not kljuc:
        return False
    kandidati = conn.execute(
        "SELECT substr(besedilo, 1, instr(besedilo || '\n', '\n') - 1) FROM naloga "
        "WHERE lower(substr(besedilo, 1, instr(besedilo || '\n', '\n') - 1)) LIKE ?",
        (kljuc + "%",),
    ).fetchall()
    for (prva_vrstica,) in kandidati:
        razmerje = SequenceMatcher(None, norm, _normaliziraj(prva_vrstica)).ratio()
        if razmerje >= PRAG_PODOBNOSTI:
            return True
    return False


def shrani_naloge(conn: sqlite3.Connection, naloge: list[dict], ime_datoteke: str, slike_map: dict):
    """Vstavi klasificirane naloge v bazo in shrani reference na slike."""
    tipi = {naziv: id_ for id_, naziv in conn.execute("SELECT id, naziv FROM tip_naloge").fetchall()}
    veljavne_kode = {k for k, *_ in conn.execute("SELECT koda FROM vsebina").fetchall()}

    vstavljeno = 0
    preskoceno = 0
    for n in naloge:
        vsebina_koda = n.get("vsebina_koda")
        if vsebina_koda not in veljavne_kode:
            vsebina_koda = None

        tip_naziv = n.get("tip_naziv", "")
        tip_id = tipi.get(tip_naziv)
        besedilo = n.get("besedilo", "").strip()

        if _ze_obstaja(conn, besedilo):
            preskoceno += 1
            continue

        # Poišči slike v besedilu: [SLIKA:ime_datoteke]
        reference_slik = re.findall(r'\[SLIKA:([^\]]+)\]', besedilo)
        ima_sliko = bool(reference_slik) or bool(n.get("ima_sliko"))

        cur = conn.execute(
            """INSERT INTO naloga (besedilo, vsebina_koda, tip_id, ima_sliko, vir_datoteka)
               VALUES (?, ?, ?, ?, ?)""",
            (besedilo, vsebina_koda, tip_id, 1 if ima_sliko else 0, ime_datoteke),
        )
        naloga_id = cur.lastrowid

        # Vstavi zapise za slike
        for vrstni_red, orig_ime in enumerate(reference_slik, 1):
            # orig_ime je originalno ime (npr. image1.png) ali že prefiks (basename_image1.png)
            # Poiščemo v slike_map, sicer vzamemo kot je
            relativna_pot = slike_map.get(orig_ime, orig_ime)
            conn.execute(
                "INSERT INTO slika (naloga_id, ime_datoteke, vrstni_red) VALUES (?, ?, ?)",
                (naloga_id, relativna_pot, vrstni_red),
            )

        vstavljeno += 1

    conn.commit()
    return vstavljeno, preskoceno


# ---------------------------------------------------------------------------
# Glavna zanka
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Klasifikacija nalog z AI")
    parser.add_argument("--vzorec", type=int, default=None, metavar="N",
                        help="Obdelaj samo prvih N datotek (za preizkus)")
    parser.add_argument("--datoteka", type=str, default=None,
                        help="Obdelaj samo to eno datoteko")
    parser.add_argument("--debug", action="store_true",
                        help="Izpiši podrobnosti o segmentih in fuzzy ujemanju")
    args = parser.parse_args()

    KLASIFIKACIJE_DIR.mkdir(exist_ok=True)
    DONE_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_POT)
    inicializiraj_bazo(conn)
    ze_obdelane = pridobi_ze_obdelane(conn)

    odjemalec = anthropic.Anthropic()

    # Izberi datoteke
    if args.datoteka:
        datoteke = [INPUT_DIR / args.datoteka]
        if not datoteke[0].exists():
            print(f"Napaka: datoteka ne obstaja: {datoteke[0]}")
            sys.exit(1)
    else:
        datoteke = sorted(INPUT_DIR.glob("*.docx"))

    # Filtriraj že obdelane
    nove = [d for d in datoteke if d.name not in ze_obdelane]

    if args.vzorec:
        nove = nove[: args.vzorec]

    skupaj = len(nove)
    print(f"Datotek za obdelavo: {skupaj}  (že obdelanih: {len(ze_obdelane)})")

    if skupaj == 0:
        print("Ni novih datotek.")
        conn.close()
        return

    uspesno = 0
    napake = 0

    for i, pot in enumerate(nove, 1):
        print(f"[{i:>4}/{skupaj}] {pot.name}", end=" ", flush=True)

        # Preveri, če JSON že obstaja (delna obdelava brez vpisa v bazo)
        json_pot = KLASIFIKACIJE_DIR / (pot.stem + ".json")

        try:
            besedilo, slike_map = ekstrahiraj_besedilo_in_slike(pot)

            if json_pot.exists():
                naloge = json.loads(json_pot.read_text(encoding="utf-8"))
                print(f"(iz predpomnilnika, {len(naloge)} nalog)", end=" ", flush=True)
            else:
                if not besedilo.strip():
                    print("PRESKOK (prazna datoteka)")
                    continue

                # Poizkusi do 3-krat pri prehodnih napakah API
                for poskus in range(3):
                    try:
                        naloge = klici_api(odjemalec, besedilo)
                        break
                    except (anthropic.RateLimitError, anthropic.APIStatusError) as e:
                        # RateLimitError (429) ali OverloadedError (529)
                        if poskus < 2:
                            cakaj = 30 * (poskus + 1)
                            print(f"(preobremenjen/rate-limit, čakam {cakaj}s...)", end=" ", flush=True)
                            time.sleep(cakaj)
                        else:
                            raise
                    except anthropic.BadRequestError:
                        raise
                    except (anthropic.APIError, json.JSONDecodeError) as e:
                        if poskus < 2:
                            print(f"(napaka {e}, čakam 5s...)", end=" ", flush=True)
                            time.sleep(5)
                        else:
                            raise

                json_pot.write_text(json.dumps(naloge, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"({len(naloge)} nalog, {len(slike_map)} slik)", end=" ", flush=True)

            vstavljeno, preskoceno = shrani_naloge(conn, naloge, pot.name, slike_map)
            pot.rename(DONE_DIR / pot.name)
            dup = f", {preskoceno} duplikatov" if preskoceno else ""
            print(f"-> {vstavljeno} v bazo{dup}, premaknjeno v done/")
            uspesno += 1

        except Exception as e:
            print(f"NAPAKA: {e}")
            napake += 1
            # Nadaljuj z naslednjo datoteko
            continue

    conn.close()
    print(f"\nKonec. Uspesno: {uspesno}, napake: {napake}")
    print(f"Baza: {DB_POT}")
    print(f"JSON predpomnilnik: {KLASIFIKACIJE_DIR}/")


if __name__ == "__main__":
    main()

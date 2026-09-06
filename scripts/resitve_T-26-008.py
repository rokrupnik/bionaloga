"""T-26-008 — izloči zapise, ki so v tabeli `naloga` v resnici bloki rešitev.

Vzorec: NASLOV z velikimi črkami + pod-odgovori `x.1`, `x.2` …, brez vprašaja
in brez velelnika. Prava (kratka) vprašanja imajo enako obliko, zato ju loči
šele odsotnost vprašanja — glej `je_blok_resitev_xn()`.

Zagon:
    python3 scripts/resitve_T-26-008.py            # suhi tek, samo poročilo
    python3 scripts/resitve_T-26-008.py --write    # zapiše v bazo

Pred `--write` naredi varnostno kopijo:
    cp baza.db baza_T-26-008_backup.db
Vrnitev na prejšnje stanje:
    cp baza_T-26-008_backup.db baza.db
"""
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
DB = KOREN / "baza.db"
POROCILO = KOREN / "porocilo_T-26-008_kandidati.txt"

# Naslov v prvi vrstici, takoj za njim pod-odgovor `x.1`.
NASLOV_XN = re.compile(r"^[A-ZČŠŽĐ][A-ZČŠŽĐ0-9 ,\-/()\.]{2,60}\n\s*[Xx]\.1\b")

# Velelniki iz nalog (razširjen seznam iz scripts/tipi_nalog_T-26-007.py).
# Namenoma ujamemo samo velelniško obliko: 'označite' je vprašanje, 'označeno'
# v opombi ocenjevalca pa ne.
VELELNIK = re.compile(
    r"\b(?:navedi|zapiši|izračunaj|imenuj|naštej|poimenuj|določi|razloži|pojasni|"
    r"utemelji|opiši|dopolni|označi|nariši|vpiši|podčrtaj|obkroži|poveži|razvrsti|"
    r"razporedi|prikaži|odčitaj|ugotovi|primerjaj|vriši|osenči|sklepaj|izberi|"
    r"napiši|postavi|presodi|popravi|obrazloži|dokaži|analiziraj|razmisli)(?:te)?\b",
    re.I)


def je_blok_resitev_xn(besedilo: str) -> bool:
    """Blok rešitev oblike 'NASLOV\\nx.1 <odgovor>\\nx.2 …'.

    Isto obliko imajo tudi prava kratka vprašanja, zato blok priznamo šele,
    kadar v besedilu ni ne vprašaja ne velelnika — vprašanje brez obojega ne
    obstaja, seznam odgovorov pa je praviloma tak.
    """
    t = besedilo.lstrip()
    return bool(NASLOV_XN.match(t)) and "?" not in t and not VELELNIK.search(t)


def _naslov(b: str) -> str:
    return b.lstrip().split("\n")[0].strip()


def _st_podvprasanj(b: str) -> int:
    return len(set(re.findall(r"(?:^|\s|\|)[Xx]\.(\d{1,2})\b", b)))


def analiziraj(conn):
    """Vrne (bloki, preslikave): kandidate za izločitev in enolične pare."""
    vrstice = [(r[0], r[1] or "", r[2] or "", r[3]) for r in conn.execute(
        "SELECT id, vir_datoteka, besedilo, resitev FROM naloga ORDER BY id")]
    bloki = [r for r in vrstice if je_blok_resitev_xn(r[2])]
    ids = {r[0] for r in bloki}

    po_datoteki = defaultdict(list)
    for r in vrstice:
        po_datoteki[r[1]].append(r)

    # Preslikamo SAMO, kadar je v isti datoteki natanko ena naloga z enakim
    # naslovom, enakim številom podvprašanj, stoji pred blokom in še nima
    # rešitve. Sicer rešitve ne pripišemo — napačna je slabša od nobene.
    preslikave = {}
    for b in bloki:
        cilji = [r for r in po_datoteki[b[1]]
                 if r[0] not in ids and _naslov(r[2]) == _naslov(b[2])]
        if (len(cilji) == 1 and cilji[0][0] < b[0] and not cilji[0][3]
                and _st_podvprasanj(cilji[0][2]) == _st_podvprasanj(b[2])):
            preslikave[b[0]] = cilji[0][0]
    # Če se na isto nalogo veže več blokov, ne vemo, kateri je njena rešitev —
    # takrat ne pripišemo nobenega.
    veckratni = {c for c in preslikave.values()
                 if list(preslikave.values()).count(c) > 1}
    return bloki, {b: c for b, c in preslikave.items() if c not in veckratni}


def zapisi_porocilo(bloki, preslikave):
    with POROCILO.open("w", encoding="utf-8") as f:
        f.write(f"T-26-008 — bloki rešitev v tabeli naloga: {len(bloki)}\n")
        f.write(f"od tega preslikanih v naloga.resitev: {len(preslikave)}\n\n")
        for nid, vir, bes, _ in bloki:
            cilj = preslikave.get(nid)
            f.write(f"--- id={nid} vir={vir} "
                    f"{'-> resitev naloge ' + str(cilj) if cilj else '(brez preslikave)'}\n")
            f.write(bes.replace("\n", " | ")[:400] + "\n\n")


def izvedi(conn, bloki, preslikave):
    """Arhivira bloke, pripiše rešitve in jih odstrani iz `naloga`."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS naloga_resitev_arhiv (
            id INTEGER PRIMARY KEY, besedilo TEXT, vsebina_koda TEXT,
            tip_id INTEGER, ima_sliko BOOLEAN, tezavnost INTEGER,
            vir_datoteka TEXT, datum_uvoza DATETIME, resitev TEXT, vir_tip TEXT,
            preslikan_v INTEGER, naloga TEXT);
        CREATE TABLE IF NOT EXISTS slika_resitev_arhiv (
            id INTEGER PRIMARY KEY, naloga_id INTEGER, ime_datoteke TEXT,
            vrstni_red INTEGER);
    """)
    ids = [b[0] for b in bloki]
    seznam = ",".join("?" * len(ids))
    conn.execute(f"""INSERT OR REPLACE INTO naloga_resitev_arhiv
        SELECT id, besedilo, vsebina_koda, tip_id, ima_sliko, tezavnost,
               vir_datoteka, datum_uvoza, resitev, vir_tip, NULL, 'T-26-008'
        FROM naloga WHERE id IN ({seznam})""", ids)
    for blok_id, cilj_id in preslikave.items():
        conn.execute("UPDATE naloga_resitev_arhiv SET preslikan_v=? WHERE id=?",
                     (cilj_id, blok_id))
    for blok_id, cilj_id in preslikave.items():
        besedilo = conn.execute("SELECT besedilo FROM naloga WHERE id=?",
                                (blok_id,)).fetchone()[0]
        conn.execute("UPDATE naloga SET resitev=? WHERE id=? AND resitev IS NULL",
                     (besedilo, cilj_id))
    conn.execute(f"""INSERT OR REPLACE INTO slika_resitev_arhiv
        SELECT id, naloga_id, ime_datoteke, vrstni_red FROM slika
        WHERE naloga_id IN ({seznam})""", ids)
    slik = conn.execute(f"SELECT COUNT(*) FROM slika WHERE naloga_id IN ({seznam})",
                        ids).fetchone()[0]
    conn.execute(f"DELETE FROM slika WHERE naloga_id IN ({seznam})", ids)
    conn.execute(f"DELETE FROM naloga WHERE id IN ({seznam})", ids)
    conn.commit()
    return slik


def main():
    conn = sqlite3.connect(DB)
    bloki, preslikave = analiziraj(conn)
    zapisi_porocilo(bloki, preslikave)
    print(f"blokov rešitev v tabeli naloga : {len(bloki)}")
    print(f"  od tega preslikanih v resitev: {len(preslikave)}")
    print(f"poročilo: {POROCILO}")
    if "--write" not in sys.argv:
        print("suhi tek — v bazo ni bilo zapisano nič (dodaj --write)")
        return
    if not (KOREN / "baza_T-26-008_backup.db").exists():
        raise SystemExit("manjka baza_T-26-008_backup.db — najprej naredi kopijo")
    slik = izvedi(conn, bloki, preslikave)
    print(f"izbrisano iz naloga: {len(bloki)} (arhiv: naloga_resitev_arhiv)")
    print(f"izbrisano iz slika : {slik} (arhiv: slika_resitev_arhiv)")


if __name__ == "__main__":
    main()

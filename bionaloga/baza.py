import sqlite3
from pathlib import Path

BAZA_POT = Path(__file__).parent.parent / "baza.db"


def povezava():
    conn = sqlite3.connect(BAZA_POT)
    conn.row_factory = sqlite3.Row
    return conn


def pridobi_vsebino():
    """Vrne celotno hierarhijo vsebine."""
    with povezava() as conn:
        return conn.execute(
            "SELECT koda, naziv, nadrejena_koda, raven FROM vsebina ORDER BY koda"
        ).fetchall()


def pridobi_tipe_nalog():
    with povezava() as conn:
        return conn.execute("SELECT id, naziv FROM tip_naloge ORDER BY id").fetchall()


def poisci_naloge(vsebina_kode: list[str] | None, tip_id: int | None, ima_sliko: bool | None):
    """Vrne naloge po izbranih filtrih. Koda poglavja (raven 1) ujame tudi vse podkode."""
    pogoji = []
    parametri = []

    if vsebina_kode:
        # Za vsako kodo: če je raven 1 (XX.00.00) ali raven 2 (XX.YY.00),
        # poišči tudi naloge v podkodah z LIKE prefixom.
        sub_pogoji = []
        for koda in vsebina_kode:
            deli = koda.split(".")
            if deli[1] == "00" and deli[2] == "00":
                # Raven 1 → vse kode z enakim poglavjem (XX.*)
                sub_pogoji.append("n.vsebina_koda LIKE ?")
                parametri.append(deli[0] + ".%")
            elif deli[2] == "00":
                # Raven 2 → vse kode z enakim podpoglavjem (XX.YY.*)
                sub_pogoji.append("n.vsebina_koda LIKE ?")
                parametri.append(deli[0] + "." + deli[1] + ".%")
            else:
                # Raven 3 → točna koda
                sub_pogoji.append("n.vsebina_koda = ?")
                parametri.append(koda)
        pogoji.append("(" + " OR ".join(sub_pogoji) + ")")

    if tip_id is not None:
        pogoji.append("n.tip_id = ?")
        parametri.append(tip_id)

    if ima_sliko is not None:
        pogoji.append("n.ima_sliko = ?")
        parametri.append(1 if ima_sliko else 0)

    where = ("WHERE " + " AND ".join(pogoji)) if pogoji else ""

    sql = f"""
        SELECT n.id, n.besedilo, n.vsebina_koda, n.tip_id, n.ima_sliko,
               v.naziv AS vsebina_naziv, t.naziv AS tip_naziv
        FROM naloga n
        LEFT JOIN vsebina v ON n.vsebina_koda = v.koda
        LEFT JOIN tip_naloge t ON n.tip_id = t.id
        {where}
        ORDER BY n.vsebina_koda, n.id
    """

    with povezava() as conn:
        return conn.execute(sql, parametri).fetchall()


def pridobi_naloge_po_ids(ids: list[int]):
    """Vrne naloge v točno takem vrstnem redu kot ids."""
    if not ids:
        return []
    placeholders = ",".join("?" * len(ids))
    sql = f"""
        SELECT n.id, n.besedilo, n.vsebina_koda, n.tip_id, n.ima_sliko,
               v.naziv AS vsebina_naziv, t.naziv AS tip_naziv
        FROM naloga n
        LEFT JOIN vsebina v ON n.vsebina_koda = v.koda
        LEFT JOIN tip_naloge t ON n.tip_id = t.id
        WHERE n.id IN ({placeholders})
    """
    with povezava() as conn:
        vrstice = conn.execute(sql, ids).fetchall()

    # Ohrani vrstni red ids
    po_id = {v["id"]: v for v in vrstice}
    return [po_id[i] for i in ids if i in po_id]


def pridobi_nalogo(naloga_id: int):
    with povezava() as conn:
        return conn.execute(
            """SELECT n.id, n.besedilo, n.vsebina_koda, n.tip_id, n.ima_sliko,
                      v.naziv AS vsebina_naziv, t.naziv AS tip_naziv
               FROM naloga n
               LEFT JOIN vsebina v ON n.vsebina_koda = v.koda
               LEFT JOIN tip_naloge t ON n.tip_id = t.id
               WHERE n.id = ?""",
            (naloga_id,),
        ).fetchone()


def posodobi_nalogo(naloga_id: int, besedilo: str, vsebina_koda: str | None, tip_id: int | None):
    with povezava() as conn:
        conn.execute(
            "UPDATE naloga SET besedilo = ?, vsebina_koda = ?, tip_id = ? WHERE id = ?",
            (besedilo, vsebina_koda or None, tip_id or None, naloga_id),
        )


def pridobi_slike_naloge(naloga_id: int):
    with povezava() as conn:
        return conn.execute(
            "SELECT ime_datoteke FROM slika WHERE naloga_id = ? ORDER BY vrstni_red",
            (naloga_id,),
        ).fetchall()

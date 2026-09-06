"""T-26-010 — obnovi 21 "pokvarjenih" slik s prekodiranjem in vrni zapise v bazo.

Ozadje: datoteke niso pokvarjene v smislu izgubljenih podatkov — vsebina je
cela, le python-docx je ne zna prebrati (Exif/progressive JPEG). Ponovni izvlek
iz izvornega .docx ne pomaga (bajti so identični, preverjeno z md5), zato slike
prekodiramo v navaden baseline JPEG, ki ga python-docx sprejme.

Vir bajtov: arhiv arhiv_T-26-010_pokvarjene_slike.tar.gz (iste datoteke, kot so
bile prej v slike/; za 19 od 21 preverjeno md5-identične s sliko v izvornem
.docx).

Zagon:  .venv/bin/python scripts/obnovi_slike_T-26-010.py [--write]
Brez --write je suha vaja (nič se ne spremeni).
"""

import os
import shutil
import sqlite3
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KOREN))
from bionaloga.generator import je_slika_berljiva  # noqa: E402

ARHIV = KOREN / "arhiv_T-26-010_pokvarjene_slike.tar.gz"
BACKUP_BAZA = KOREN / "baza_T-26-010_backup.db"   # stanje pred brisanjem (ima 21 vrstic)
BAZA = KOREN / "baza.db"
SLIKE = KOREN / "slike"

# id-ji vrstic v tabeli `slika`, ki so bile izbrisane v prvem delu T-26-010
IDS = [11457, 604, 1897, 3121, 102, 325, 838, 435, 612, 405, 144, 30, 329,
       367, 381, 696, 2480, 193, 6, 3133, 7687]


def prekodiraj(vhod: Path, izhod: Path) -> str | None:
    """Prekodira sliko v baseline JPEG. Vrne opis napake ali None."""
    r = subprocess.run(
        ["magick", str(vhod), "-strip", "-interlace", "none", "-quality", "95", str(izhod)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        return f"magick: {r.stderr.strip()[:200]}"
    return je_slika_berljiva(izhod)


def main() -> int:
    pisi = "--write" in sys.argv
    print(f"{'PISANJE' if pisi else 'SUHA VAJA'}\n")

    vrstice = {}
    with sqlite3.connect(BACKUP_BAZA) as bk:
        bk.row_factory = sqlite3.Row
        for r in bk.execute(
            f"SELECT id, naloga_id, ime_datoteke, vrstni_red FROM slika "
            f"WHERE id IN ({','.join('?' * len(IDS))})", IDS
        ):
            vrstice[r["id"]] = dict(r)
    manjka = set(IDS) - set(vrstice)
    if manjka:
        print(f"NAPAKA: v varnostni kopiji ni vrstic {sorted(manjka)}")
        return 1

    tmp = Path(tempfile.mkdtemp(prefix="t26010_"))
    with tarfile.open(ARHIV) as t:
        t.extractall(tmp)

    obnovljene, neuspele = [], []
    for sid in IDS:
        v = vrstice[sid]
        ime = v["ime_datoteke"]
        vir = tmp / ime
        if not vir.exists():
            neuspele.append((sid, ime, "ni v arhivu"))
            continue
        cilj_tmp = tmp / f"obnovljena_{sid}{Path(ime).suffix}"
        napaka = prekodiraj(vir, cilj_tmp)
        if napaka:
            neuspele.append((sid, ime, napaka))
            continue
        obnovljene.append((sid, v, cilj_tmp))
        print(f"OK   {sid:>6}  naloga {v['naloga_id']:>6}  {ime}"
              f"  ({vir.stat().st_size} -> {cilj_tmp.stat().st_size} B)")

    for sid, ime, zakaj in neuspele:
        print(f"NE   {sid:>6}  {ime}: {zakaj}")

    print(f"\nObnovljivih: {len(obnovljene)}/{len(IDS)}")
    if not pisi:
        print("\n(suha vaja — nič zapisanega; zaženi z --write)")
        return 0

    # 1) datoteke v slike/
    for sid, v, cilj_tmp in obnovljene:
        cilj = SLIKE / v["ime_datoteke"]
        cilj.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(cilj_tmp, cilj)

    # 2) vrstice v tabeli slika + naloga.ima_sliko
    with sqlite3.connect(BAZA) as con:
        for sid, v, _ in obnovljene:
            con.execute(
                "INSERT OR REPLACE INTO slika (id, naloga_id, ime_datoteke, vrstni_red) "
                "VALUES (?,?,?,?)",
                (sid, v["naloga_id"], v["ime_datoteke"], v["vrstni_red"]),
            )
            con.execute("UPDATE naloga SET ima_sliko = 1 WHERE id = ?", (v["naloga_id"],))
        con.commit()

    print(f"\nZapisano: {len(obnovljene)} datotek v slike/, "
          f"{len(obnovljene)} vrstic v tabelo slika.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

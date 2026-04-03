"""
Reset skripta za BioNaloga projekt.

Zbriše baza.db, premakne datoteke iz input/done/ nazaj v input/,
in zbriše JSON datoteke v klasifikacije/.

Uporaba:
    python scripts/reset.py
"""

import shutil
from pathlib import Path

KOREN = Path(__file__).parent.parent
DB_POT = KOREN / "baza.db"
INPUT_DIR = KOREN / "input"
DONE_DIR = INPUT_DIR / "done"
KLASIFIKACIJE_DIR = KOREN / "klasifikacije"


def main():
    # 1. Zbriši baza.db
    if DB_POT.exists():
        DB_POT.unlink()
        print(f"Zbrisano: {DB_POT}")
    else:
        print(f"Baza ne obstaja: {DB_POT}")

    # 2. Premakni datoteke iz done/ nazaj v input/
    if DONE_DIR.exists():
        premaknjeno = 0
        for dat in DONE_DIR.iterdir():
            if dat.is_file():
                cilj = INPUT_DIR / dat.name
                shutil.move(str(dat), str(cilj))
                premaknjeno += 1
        print(f"Premaknjeno iz done/ nazaj v input/: {premaknjeno} datotek")
    else:
        print("Mapa done/ ne obstaja.")

    # 3. Zbriši JSON datoteke v klasifikacije/
    if KLASIFIKACIJE_DIR.exists():
        zbrisano = 0
        for dat in KLASIFIKACIJE_DIR.glob("*.json"):
            dat.unlink()
            zbrisano += 1
        print(f"Zbrisano JSON datotek v klasifikacije/: {zbrisano}")
    else:
        print("Mapa klasifikacije/ ne obstaja.")

    print("\nReset končan.")


if __name__ == "__main__":
    main()

"""T-26-010 — odstrani 21 pokvarjenih slik iz slike/ in počisti bazo.

Zagon:  .venv/bin/python /tmp/t26010/ocisti.py [--write]
Brez --write je suha vaja (nič se ne spremeni).
"""
import os, re, sqlite3, sys

PISI = "--write" in sys.argv

IDS = [11457, 604, 1897, 3121, 102, 325, 838, 435, 612, 405, 144,
       30, 329, 367, 381, 696, 2480, 193, 6, 3133, 7687]

c = sqlite3.connect("baza.db")
c.row_factory = sqlite3.Row
q = ",".join("?" * len(IDS))
vrstice = c.execute(
    f"SELECT id, naloga_id, ime_datoteke FROM slika WHERE id IN ({q})", IDS
).fetchall()
assert len(vrstice) == len(IDS), f"pricakovanih {len(IDS)} vrstic, dobljenih {len(vrstice)}"

print(f"{'PISEM' if PISI else 'SUHA VAJA'} — {len(vrstice)} slik\n")

naloge = sorted({v["naloga_id"] for v in vrstice})

# 1. datoteke
for v in vrstice:
    pot = os.path.join("slike", v["ime_datoteke"])
    print(f"  brisem datoteko: {pot}  (obstaja={os.path.exists(pot)})")
    if PISI and os.path.exists(pot):
        os.remove(pot)

# 2. vrstice v `slika`
print(f"\n  brisem {len(vrstice)} vrstic iz tabele slika")
if PISI:
    c.execute(f"DELETE FROM slika WHERE id IN ({q})", IDS)

# 3. placeholderji v naloga.besedilo + ima_sliko
print()
for nid in naloge:
    n = c.execute("SELECT besedilo, ima_sliko FROM naloga WHERE id=?", (nid,)).fetchone()
    # besedilo NAMENOMA ostane nespremenjeno: naloge so odvisne od slike
    # (npr. "Označi dele zunanje zgradbe srca:"), zato bi odstranitev
    # placeholderja ustvarila neodgovorljivo nalogo v izvozu. Glej ## Result.
    preostale = c.execute(
        f"SELECT count(*) FROM slika WHERE naloga_id=? AND id NOT IN ({q})",
        [nid] + IDS,
    ).fetchone()[0]
    nova_ima_sliko = 1 if preostale else 0
    print(f"  naloga {nid}: preostale slike={preostale} "
          f"ima_sliko {n['ima_sliko']} -> {nova_ima_sliko} "
          f"| besedilo nespremenjeno ({len(n['besedilo'])} znakov)")
    if PISI:
        c.execute("UPDATE naloga SET ima_sliko=? WHERE id=?", (nova_ima_sliko, nid))

if PISI:
    c.commit()
    print("\nSHRANJENO.")
else:
    c.rollback()
    print("\nNic ni bilo spremenjeno (suha vaja).")

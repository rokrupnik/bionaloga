#!/usr/bin/env python3
"""Preveri stanje uvoženih RIC nalog v bazi in izvoz v Word.

    python preveri_ric.py
"""

import io
import re
import sqlite3
import sys
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).parent))

KOREN = Path(__file__).parent
SLIKE = KOREN / "slike"

conn = sqlite3.connect(KOREN / "baza.db")
conn.row_factory = sqlite3.Row
tezav = 0


def zapis(oznaka, vrednost, tezava=False):
    global tezav
    if tezava:
        tezav += 1
    print(f"  {'!!' if tezava else '  '} {oznaka:<44} {vrednost}")


print("\n=== OBSEG ===")
vse = conn.execute("SELECT COUNT(*) FROM naloga").fetchone()[0]
ric = conn.execute("SELECT COUNT(*) FROM naloga WHERE vir_tip='matura'").fetchone()[0]
sole = vse - ric
zapis("nalog skupaj", f"{vse:,}")
zapis("  od tega matura (RIC)", f"{ric:,}")
zapis("  od tega šolski testi", f"{sole:,}")
zapis("RIC s sliko", conn.execute(
    "SELECT COUNT(*) FROM naloga WHERE vir_tip='matura' AND ima_sliko=1").fetchone()[0])
zapis("RIC z rešitvijo", conn.execute(
    "SELECT COUNT(*) FROM naloga WHERE vir_tip='matura' AND resitev IS NOT NULL").fetchone()[0])
zapis("RIC brez klasifikacije vsebine", conn.execute(
    "SELECT COUNT(*) FROM naloga WHERE vir_tip='matura' AND vsebina_koda IS NULL").fetchone()[0])
zapis("RIC brez tipa", conn.execute(
    "SELECT COUNT(*) FROM naloga WHERE vir_tip='matura' AND tip_id IS NULL").fetchone()[0])

print("\n=== ČISTOST ===")
resitve_kot_naloge = conn.execute(
    "SELECT COUNT(*) FROM naloga WHERE vir_tip='matura' AND besedilo LIKE 'Rešitev%'"
).fetchone()[0]
zapis("nalog, ki so v resnici bloki rešitev", resitve_kot_naloge, resitve_kot_naloge > 0)
tabele_resitev = sum(1 for (b,) in conn.execute(
    "SELECT besedilo FROM naloga WHERE vir_tip='matura'")
    if re.search(r"\|\s*Naloga\s*\|\s*Točke\s*\|", b))
zapis("nalog z razpredelnico rešitev", tabele_resitev, tabele_resitev > 0)
kratke = conn.execute(
    "SELECT COUNT(*) FROM naloga WHERE vir_tip='matura' AND length(besedilo) < 40").fetchone()[0]
zapis("sumljivo kratkih (<40 znakov)", kratke)
prazni_ph = sum(1 for (b,) in conn.execute(
    "SELECT besedilo FROM naloga WHERE vir_tip='matura'") if "[SLIKA:neznana" in b)
zapis("besedil z '[SLIKA:neznana'", prazni_ph, prazni_ph > 0)

print("\n=== SLIKE ===")
slik = conn.execute("""SELECT COUNT(*) FROM slika s JOIN naloga n ON n.id=s.naloga_id
                       WHERE n.vir_tip='matura'""").fetchone()[0]
zapis("slika zapisov (RIC)", f"{slik:,}")
manjka = []
napacen_format = []
PODPRTI = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}
for r in conn.execute("""SELECT s.ime_datoteke FROM slika s JOIN naloga n ON n.id=s.naloga_id
                         WHERE n.vir_tip='matura'"""):
    p = SLIKE / r["ime_datoteke"]
    if not p.exists():
        manjka.append(r["ime_datoteke"])
    elif p.suffix.lower() not in PODPRTI:
        napacen_format.append(r["ime_datoteke"])
zapis("manjkajočih datotek", len(manjka), bool(manjka))
for m in manjka[:3]:
    print(f"       {m}")
zapis("nepodprtih formatov (bi izpadle iz testa)", len(napacen_format), bool(napacen_format))
for m in napacen_format[:3]:
    print(f"       {m}")
osirotele = conn.execute("""SELECT COUNT(*) FROM slika s LEFT JOIN naloga n ON n.id=s.naloga_id
                            WHERE n.id IS NULL""").fetchone()[0]
zapis("osirotelih slika zapisov", osirotele, osirotele > 0)

print("\n=== IZVOZ V WORD (vzorec 25 nalog) ===")
from bionaloga import generator                                   # noqa: E402
from docx import Document                                         # noqa: E402

ids = [r["id"] for r in conn.execute(
    "SELECT id FROM naloga WHERE vir_tip='matura' AND ima_sliko=1 ORDER BY RANDOM() LIMIT 12")]
ids += [r["id"] for r in conn.execute(
    "SELECT id FROM naloga WHERE vir_tip='matura' AND besedilo LIKE '%|---%' ORDER BY RANDOM() LIMIT 8")]
ids += [r["id"] for r in conn.execute(
    "SELECT id FROM naloga WHERE vir_tip='matura' ORDER BY RANDOM() LIMIT 5")]
vsebina, napake = generator.generiraj_test(ids, "Preverjanje RIC")
(KOREN / "ric_vzorec_test.docx").write_bytes(vsebina)
d = Document(io.BytesIO(vsebina))
zapis("nalog v vzorcu", len(ids))
zapis("Word tabel", len(d.tables))
zapis("slik v dokumentu", len(d.inline_shapes))
zapis("IZPUŠČENIH nalog", len(napake), bool(napake))
for n in napake[:3]:
    print(f"       {n}")

print("\n=== DVOJNIKI (vzorec 300 parov) ===")
from difflib import SequenceMatcher                               # noqa: E402
vzorec = [r["besedilo"] for r in conn.execute(
    "SELECT besedilo FROM naloga WHERE vir_tip='matura' ORDER BY RANDOM() LIMIT 300")]
rnd = Random(7)
nad_pragom = 0
for _ in range(300):
    if len(vzorec) < 2:
        break
    a, b = rnd.sample(vzorec, 2)
    na = re.sub(r"\s+", " ", a.strip().lower())
    nb = re.sub(r"\s+", " ", b.strip().lower())
    if SequenceMatcher(None, na, nb).ratio() >= 0.80:
        nad_pragom += 1
zapis("naključnih parov ≥80 % podobnih", nad_pragom, nad_pragom > 0)

print()
if tezav:
    print(f"{tezav} TEŽAV — poglej vrstice z '!!'")
    raise SystemExit(1)
print("vse v redu")

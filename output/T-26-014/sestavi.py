"""Enkratna skripta za T-26-014: sestavi test na temo dedovanja (03.%).

10 nalog izbirnega tipa, 4 kratki odgovor, 5 daljši odgovor.

Poleg naključnega izbora velja kakovostni filter: baza vsebuje nekaj zapisov,
ki niso samostojne naloge (odlomki rešitev, ostanki oštevilčenja, zlepljeni
deli več nalog). Taki kandidati se preskočijo, prav tako naloge, ki jih
generator izpusti zaradi pokvarjenih slik.
"""
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bionaloga import baza, generator

random.seed(20260908)

ZAHTEVE = [(1, 10), (2, 4), (3, 5)]
VSEBINA = ["03.00.00"]

# Zapisi, ki niso samostojna naloga
ZAVRNI_ZACETEK = re.compile(
    r"^(\s*[|]|\s*[A-Da-d][)\.]\s|\s*x\.\d|\s*\d+[\.\)]\s*[\t ]|\s*naloga\b)", re.I
)
ZACETEK_VPRASANJA = re.compile(
    r"^(kaj|kako|zakaj|kater|kje|kdaj|koliko|napiši|razloži|pojasni|opiši|utemelji|"
    r"skiciraj|naštej|določi|izračunaj|navedi|dopolni|poimenuj|primerjaj|obkroži|"
    r"poveži|razvrsti|označi|ugotovi|zapiši|predstavi|pri |na sliki|v )", re.I
)


def je_uporabna(besedilo: str) -> bool:
    b = besedilo.strip()
    if not (60 <= len(b) <= 2500):
        return False
    if ZAVRNI_ZACETEK.match(b):
        return False
    if "?" not in b and not ZACETEK_VPRASANJA.match(b):
        return False
    return True


def kljuc(besedilo: str) -> str:
    """Ključ za prepoznavo (skoraj) podvojenih nalog."""
    b = re.sub(r"[^a-zčšž ]", " ", besedilo.lower())
    return " ".join(b.split())[:80]


videni_kljuci = set()
izbrani_po_tipu = {}
for tip_id, koliko in ZAHTEVE:
    bazen = [n for n in baza.poisci_naloge(VSEBINA, tip_id, None) if je_uporabna(n["besedilo"])]
    random.shuffle(bazen)
    izbrani, i = [], 0
    while len(izbrani) < koliko and i < len(bazen):
        kandidat = bazen[i]
        i += 1
        k = kljuc(kandidat["besedilo"])
        if k in videni_kljuci:
            continue
        _, napake = generator.generiraj_test([kandidat["id"]])
        if napake:
            continue
        videni_kljuci.add(k)
        izbrani.append(kandidat["id"])
    if len(izbrani) < koliko:
        print(f"OPOZORILO: tip {tip_id} — samo {len(izbrani)} od {koliko}")
    print(f"tip {tip_id}: bazen po filtru = {len(bazen)}")
    izbrani_po_tipu[tip_id] = izbrani

ids = [i for tip_id, _ in ZAHTEVE for i in izbrani_po_tipu[tip_id]]
vsebina_docx, napake = generator.generiraj_test(ids, naslov="Test: Dedovanje")

pot = Path(__file__).parent / "test_dedovanje.docx"
pot.write_bytes(vsebina_docx)
print("IDS:", ids)
print("NAPAKE:", napake)
print("Shranjeno:", pot)

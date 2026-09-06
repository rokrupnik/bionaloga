"""T-26-007 — merilo za dolocitev tip_id nalogam brez tipa.

Skripta samo IZPISE predlagano klasifikacijo (ne pise v bazo).
Merilo: naloga se razdeli na podvprasanja; odloca prevladujoca oblika odgovora.
  4 = vec kot polovica podvprasanj je dopolnjevanje/oznacevanje/povezovanje
  3 = vsaj 40 % podvprasanj zahteva razlago/utemeljitev
  1 = v besedilu so izbire A) B) ...
  2 = sicer (kratki odprti odgovor)

Zagon: python3 scripts/tipi_nalog_T-26-007.py
"""
import sqlite3, re
from collections import Counter

DB='baza.db'
con = sqlite3.connect(DB)
import sys
# privzeto: samo naloge brez tipa; z "--vse" ponovi merilo na vseh nalogah
kje = "1=1" if "--vse" in sys.argv else "tip_id IS NULL"
rows = con.execute(f"SELECT id, besedilo FROM naloga WHERE {kje} ORDER BY id").fetchall()

SPLIT = re.compile(r'(?:(?<=\s)|(?<=\|)|^)(?:x|\d{1,3})\.\d{1,2}\.?(?=\s*[A-ZČŠŽĐ])')

UKAZ = r'naved|zapiš|izračunaj|imenuj|našte|poimenuj|določi|razlož|pojasn|utemelj|opiši|dopolni|označi|nariši|vpiši|podčrta|obkroži|poveži|razvrsti|razporedi|prikaži|odčitaj|ugotovi|primerjaj|vriši|osenči|sklepaj|izberi|napiši|postavite hipotezo'
JE_VPR = re.compile(r'\?|' + UKAZ, re.I)

DALJ   = re.compile(r'razlož|pojasn|utemelj|opiši|postavite hipotezo|primerjaj', re.I)
DOPOLN = re.compile(r'dopolni|v preglednic\w* (?:vpiš|zapiš|označ)|vpišite v preglednic|označite s [\+x]|poveži|razvrsti|razporedi|podčrta|obkroži|nariši (?:graf|linijski|stolpčni|preglednic)|vriši|osenči|označite in poimenujte|s puščico označite|označite s puščico|na (?:sliki|skici|shemi|grafu|preglednici)[^.?]{0,40}označite', re.I)
IZBIRNI = re.compile(r'\bA\)\s.{0,400}\bB\)\s', re.S)

res = []
for nid, bes in rows:
    frags = [p.strip() for p in SPLIT.split(bes) if p.strip()]
    q = [p for p in frags if JE_VPR.search(p)] or [bes]
    n = len(q)
    d = sum(1 for p in q if DALJ.search(p))
    o = sum(1 for p in q if DOPOLN.search(p))
    if IZBIRNI.search(bes):                tip = 1
    elif o > d and o/n > 0.5:            tip = 4
    elif d/n >= 0.40:                      tip = 3
    else:                                  tip = 2
    res.append((nid, tip, n, d, o))

print(Counter(t for _,t,*_ in res))
for r in res: print("id=%-6d tip=%d  vpr=%-3d dalj=%-3d dopoln=%d" % r)

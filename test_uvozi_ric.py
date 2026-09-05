#!/usr/bin/env python3
"""Testi za preslikavo rešitev in razrez besedila pri uvozu RIC nalog.

Preslikava rešitev je najbolj tvegan del uvoza: napačno pripisana rešitev
pomeni napačen odgovor v učiteljevih rešitvah, kar je slabše od manjkajoče
rešitve. Zato so testi predvsem o tem, kdaj se preslikava NE sme zgoditi.

    python test_uvozi_ric.py
"""

from uvozi_ric import preslikaj_resitve, _odstrani_zaporedno, _normaliziraj

napak = 0


def preveri(opis, dobljeno, pricakovano):
    global napak
    if dobljeno == pricakovano:
        print(f"  ok   {opis}")
    else:
        napak += 1
        print(f"  NAPAKA {opis}\n         dobljeno:    {dobljeno}\n         pričakovano: {pricakovano}")


def n(od, do):
    return {"od": od, "do": do}


print("preslikaj_resitve — blok 'Rešitev: X'")

# 3 naloge, 3 rešitve → preslika 1:1
odstavki = [
    "1.\tPrvo vprašanje?", "A) a", "B) b",
    "2.\tDrugo vprašanje?", "A) a", "B) b",
    "3.\tTretje vprašanje?", "A) a", "B) b",
    "Rešitev: A", "Rešitev: B", "Rešitev: C",
]
preveri("ujemajoče število (3/3) → preslika",
        preslikaj_resitve(odstavki, [n(1, 3), n(4, 6), n(7, 9)]),
        {0: "A", 1: "B", 2: "C"})

# 3 naloge, 2 rešitvi → ne vemo, katera je brez → nič
odstavki2 = odstavki[:9] + ["Rešitev: A", "Rešitev: B"]
preveri("neujemajoče število (3 naloge/2 rešitvi) → nič",
        preslikaj_resitve(odstavki2, [n(1, 3), n(4, 6), n(7, 9)]),
        {})

# 2 skupini, vsaka se ujema sama zase
odstavki3 = [
    "1.\tA?", "A) a",
    "2.\tB?", "A) a",
    "Rešitev: X", "Rešitev: Y",
    "3.\tC?", "A) a",
    "Rešitev: Z",
]
preveri("dve skupini, obe ujemajoči → obe preslikani",
        preslikaj_resitve(odstavki3, [n(1, 2), n(3, 4), n(7, 8)]),
        {0: "X", 1: "Y", 2: "Z"})

# druga skupina se ne ujema → preslika se samo prva
odstavki4 = [
    "1.\tA?", "A) a",
    "2.\tB?", "A) a",
    "Rešitev: X", "Rešitev: Y",
    "3.\tC?", "A) a",
    "4.\tD?", "A) a",
    "Rešitev: Z",
]
preveri("druga skupina neujemajoča → samo prva preslikana",
        preslikaj_resitve(odstavki4, [n(1, 2), n(3, 4), n(7, 8), n(9, 10)]),
        {0: "X", 1: "Y"})

# blok, ki ne sledi neposredno nalogi (vmes je nekaj drugega) → nič
odstavki5 = [
    "1.\tA?", "A) a",
    "Neki vmesni naslov",
    "Rešitev: X",
]
preveri("blok ne sledi neposredno nalogi → nič",
        preslikaj_resitve(odstavki5, [n(1, 2)]),
        {})

print("\npreslikaj_resitve — označena 'RešitevN.naloga'")

odstavki6 = [
    "7.\tSedmo vprašanje?", "A) a",
    "8.\tOsmo vprašanje?", "A) a",
    "Rešitev8.naloga", "x.1 prvi del", "x.2 drugi del",
]
preveri("označena rešitev gre na nalogo s to številko",
        preslikaj_resitve(odstavki6, [n(1, 2), n(3, 4)]),
        {1: "x.1 prvi del\nx.2 drugi del"})

odstavki7 = ["5.\tPeto?", "A) a", "Rešitev9.naloga", "x.1 nekaj"]
preveri("označena rešitev za nalogo, ki je ni → nič",
        preslikaj_resitve(odstavki7, [n(1, 2)]),
        {})

# oznaka brez besede 'naloga' (RIC uporablja tudi 'Rešitev36. Naslov')
odstavki8 = ["36.\tVprašanje?", "A) a", "Rešitev36. Užitne rastline", "| Naloga | Točke |"]
preveri("oznaka z naslovom namesto 'naloga' → preslika",
        preslikaj_resitve(odstavki8, [n(1, 2)]),
        {0: "| Naloga | Točke |"})

# ista številka naloge dvakrat (zlepljeni izpitni poli) → ne vemo, kateri pripada
odstavki9 = [
    "8.\tPrva osma?", "A) a",
    "8.\tDruga osma?", "A) a",
    "Rešitev8. Nekaj", "x.1 odgovor",
]
preveri("podvojena številka naloge → nič (ne ugibaj)",
        preslikaj_resitve(odstavki9, [n(1, 2), n(3, 4)]),
        {})

print("\n_odstrani_zaporedno")
preveri("'12.\\tBesedilo' → 'Besedilo'", _odstrani_zaporedno("12.\tBesedilo"), "Besedilo")
preveri("'3. Besedilo' → 'Besedilo'", _odstrani_zaporedno("3. Besedilo"), "Besedilo")
preveri("brez številke ostane isto", _odstrani_zaporedno("Kaj je celica?"), "Kaj je celica?")
preveri("ne odstrani decimalke v besedilu",
        _odstrani_zaporedno("pH 7.4 je nevtralen"), "pH 7.4 je nevtralen")

print("\n_normaliziraj")
preveri("skrči presledke in male črke",
        _normaliziraj("  Kaj  JE\ncelica? "), "kaj je celica?")

print()
if napak:
    print(f"{napak} NAPAK")
    raise SystemExit(1)
print("vsi testi ok")

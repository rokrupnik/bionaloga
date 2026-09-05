#!/usr/bin/env python3
"""
test_vmesnik.py — testi za vmesnik: filter po viru, brisanje nalog, rešitve.

Piše v pravo bazo, a za sabo počisti: vse testne naloge nastanejo prek API-ja
in se na koncu pobrišejo. Zaženi: python test_vmesnik.py
"""

import io
import sqlite3
import sys
from pathlib import Path
from urllib.parse import unquote

from docx import Document
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent))
from bionaloga.main import app, SLIKE_POT   # noqa: E402
from bionaloga import baza                   # noqa: E402

odjemalec = TestClient(app)
nastale_naloge = []


def ustvari(besedilo, resitev="", tip_id="2"):
    r = odjemalec.post("/naloge", data={
        "besedilo": besedilo, "tip_id": tip_id, "resitev": resitev})
    assert r.status_code == 200, r.text
    nid = r.json()["id"]
    nastale_naloge.append(nid)
    return nid


def test_filter_po_viru():
    """vir_tip omeji nabor; vsota delov = celota."""
    vse = len(baza.poisci_naloge([], None, None))
    matura = len(baza.poisci_naloge([], None, None, "matura"))
    sola = len(baza.poisci_naloge([], None, None, "sola"))
    assert matura > 0 and sola > 0, "oba vira morata imeti naloge"
    assert matura + sola == vse, f"{matura}+{sola} != {vse}"

    r = odjemalec.get("/naloge/nakljucne-po-tipu?izbirni=3&vir_tip=matura")
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_brisanje_naloge():
    """Naloga in njeni slika zapisi izginejo; ročna slika gre tudi z diska."""
    nid = ustvari("Testna naloga za brisanje")
    izvor = next(SLIKE_POT.glob("*.png"))
    with open(izvor, "rb") as f:
        r = odjemalec.post(f"/naloge/{nid}/slika",
                           files={"slika": ("t.png", f.read(), "image/png")})
    assert r.json()["ok"], r.text
    ime = r.json()["ime"]
    assert (SLIKE_POT / ime).exists()

    r = odjemalec.delete(f"/naloge/{nid}")
    assert r.json()["ok"], r.text
    nastale_naloge.remove(nid)

    assert odjemalec.get(f"/naloge/{nid}").status_code == 404
    with sqlite3.connect(baza.BAZA_POT) as c:
        preostale = c.execute("SELECT COUNT(*) FROM slika WHERE naloga_id=?", (nid,)).fetchone()[0]
    assert preostale == 0, "slika zapisi so ostali"
    assert not (SLIKE_POT / ime).exists(), "datoteka slike je ostala"

    assert odjemalec.delete("/naloge/99999999").status_code == 404


def test_resitev_prezivi_slike():
    """Nalaganje in brisanje slike ne sme pobrisati rešitve."""
    nid = ustvari("Naloga z rešitvijo", resitev="B")
    izvor = next(SLIKE_POT.glob("*.png"))
    with open(izvor, "rb") as f:
        r = odjemalec.post(f"/naloge/{nid}/slika",
                           files={"slika": ("t.png", f.read(), "image/png")})
    sid = odjemalec.get(f"/naloge/{nid}").json()["slike"][0]["id"]
    assert odjemalec.get(f"/naloge/{nid}").json()["resitev"] == "B", "rešitev izgubljena ob nalaganju"

    odjemalec.delete(f"/naloge/{nid}/slika/{sid}")
    assert odjemalec.get(f"/naloge/{nid}").json()["resitev"] == "B", "rešitev izgubljena ob brisanju slike"


def test_izvoz_z_resitvami():
    """Razdelek Rešitve samo z zastavico; oštevilčenje sledi nalogam."""
    a = ustvari("Prva testna naloga za izvoz", resitev="A")
    b = ustvari("Druga testna naloga za izvoz", resitev="C")
    ids = f"{a},{b}"

    def odstavki(z):
        r = odjemalec.post("/izvozi", data={"ids": ids, "naslov": "T", "z_resitvami": z})
        assert r.status_code == 200, r.text
        d = Document(io.BytesIO(r.content))
        return [p.text.strip() for p in d.paragraphs if p.text.strip()]

    brez = odstavki("0")
    assert "Rešitve" not in brez

    z_res = odstavki("1")
    assert "Rešitve" in z_res
    i = z_res.index("Rešitve")
    assert z_res[i + 1] == "1. A", z_res[i + 1]
    assert z_res[i + 2] == "2. C", z_res[i + 2]


def test_ime_datoteke_s_sumniki():
    """Šumniki v naslovu ne smejo vreči latin-1 napake v HTTP glavi."""
    nid = ustvari("Naloga za ime datoteke")
    r = odjemalec.post("/izvozi", data={
        "ids": str(nid), "naslov": "Test čebele — šumniki", "z_resitvami": "1"})
    assert r.status_code == 200, r.text
    glava = r.headers["content-disposition"]
    assert "filename*=UTF-8''" in glava
    pravo = unquote(glava.split("filename*=UTF-8''")[1])
    assert "čebele" in pravo and "šumniki" in pravo, pravo


def pocisti():
    for nid in list(nastale_naloge):
        odjemalec.delete(f"/naloge/{nid}")


if __name__ == "__main__":
    testi = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    try:
        for t in testi:
            t()
            print(f"  ok  {t.__name__}")
    finally:
        pocisti()
    print(f"\nvsi testi ok ({len(testi)})")

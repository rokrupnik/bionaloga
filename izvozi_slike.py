#!/usr/bin/env python3
"""
izvozi_slike.py — Izvozi slike iz .docx datoteke in vstavi besedilne placeholder-je.

Uporaba:
    python izvozi_slike.py <pot_do_docx>

Izhod:
    slike/<ime_datoteke>/          — mapa z izvoženimi slikami (prefiks: <ime_datoteke>_)
    slike/<ime_datoteke>/mapa_slik.json — preslikava rId → ime slike
    <ime_datoteke>_brez_slik.docx  — lahek dokument z [SLIKA:...] placeholder-ji
"""

import sys
import os
import re
import zipfile
import json
import shutil
from pathlib import Path

from bionaloga.generator import normaliziraj_sliko


def preberi_relacije(rels_xml: str) -> dict:
    """Vrne preslikavo {rId: ime_datoteke} za vse slike v relacijski datoteki."""
    rid_to_file = {}
    for m in re.finditer(r'<Relationship\s+Id="(rId\d+)"[^>]*Target="(media/[^"]+)"', rels_xml):
        rid = m.group(1)
        target = m.group(2)
        rid_to_file[rid] = os.path.basename(target)
    return rid_to_file


def zamenjaj_slike_v_xml(doc_xml: str, rid_to_ime: dict) -> str:
    """Zamenja w:drawing, w:pict in w:object elemente z besedilnimi placeholder-ji [SLIKA:ime]."""

    def _placeholder(rid: str | None) -> str:
        if not rid:
            return '<w:r><w:t>[SLIKA:neznana]</w:t></w:r>'
        ime = rid_to_ime.get(rid, f"neznana_{rid}")
        return f'<w:r><w:t>[SLIKA:{ime}]</w:t></w:r>'

    def placeholder_drawing(match):
        blok = match.group(0)
        # Poiščemo r:embed="rIdXX" ali r:link="rIdXX"
        rid_m = re.search(r'r:embed="(rId\d+)"', blok) or re.search(r'r:link="(rId\d+)"', blok)
        return _placeholder(rid_m.group(1) if rid_m else None)

    def placeholder_vml(match):
        """w:pict in w:object: sliko nosi <v:imagedata r:id>.

        V w:object je poleg nje še <o:OLEObject r:id>, ki kaže na vgrajeni objekt
        (npr. Visio) in ne na sliko — zato imagedata iščemo eksplicitno in šele
        nato pademo na splošni r:id.
        """
        blok = match.group(0)
        rid_m = (
            re.search(r'<v:imagedata[^>]*r:id="(rId\d+)"', blok)
            or re.search(r'<v:imagedata[^>]*r:href="(rId\d+)"', blok)
            or re.search(r'r:id="(rId\d+)"', blok)
        )
        return _placeholder(rid_m.group(1) if rid_m else None)

    xml = _zamenjaj_gnezdene(doc_xml, "w:drawing", placeholder_drawing)
    xml = _zamenjaj_gnezdene(xml, "w:pict", placeholder_vml)
    xml = _zamenjaj_gnezdene(xml, "w:object", placeholder_vml)
    return xml


def _zamenjaj_gnezdene(xml: str, oznaka: str, zamenjava) -> str:
    """Zamenja vsak NAJBOLJ ZUNANJI <oznaka>…</oznaka> z rezultatom zamenjave().

    Ne-požrešni regex tu ne deluje: risbe so lahko gnezdene (npr. <w:drawing> z
    besedilnim poljem, ki vsebuje svoj <w:drawing>). Regex bi se ustavil pri
    prvem zaključku in pustil notranje zaključne oznake sirote — dokument potem
    ni več veljaven XML. Zato štejemo globino.
    """
    odpri = re.compile(rf'<{re.escape(oznaka)}[ >]')
    zapri = f'</{oznaka}>'
    rezultat = []
    i = 0
    while True:
        m = odpri.search(xml, i)
        if not m:
            rezultat.append(xml[i:])
            break
        rezultat.append(xml[i:m.start()])

        globina, j = 0, m.start()
        while j < len(xml):
            mo = odpri.search(xml, j)
            mz = xml.find(zapri, j)
            if mz == -1:
                break                      # ni zaključka — pustimo pri miru
            if mo and mo.start() < mz:
                globina += 1
                j = mo.end()
            else:
                globina -= 1
                j = mz + len(zapri)
                if globina == 0:
                    break
        if globina != 0:
            rezultat.append(xml[m.start():])   # neuravnoteženo: ne diramo
            break

        class _M:
            def __init__(self, s): self._s = s
            def group(self, n=0): return self._s
        rezultat.append(zamenjava(_M(xml[m.start():j])))
        i = j
    return "".join(rezultat)


def izvozi_slike(vhodna_pot: str):
    vhodna_pot = Path(vhodna_pot).resolve()
    if not vhodna_pot.exists():
        print(f"Napaka: datoteka '{vhodna_pot}' ne obstaja.")
        sys.exit(1)

    basename = vhodna_pot.stem
    mapa_slik = Path("slike") / basename
    mapa_slik.mkdir(parents=True, exist_ok=True)
    izhodna_pot = vhodna_pot.parent / f"{basename}_brez_slik.docx"

    with zipfile.ZipFile(vhodna_pot, 'r') as z:
        # 1. Relacije: rId → originalno ime datoteke
        rels_xml = z.read('word/_rels/document.xml.rels').decode('utf-8')
        rid_to_orig = preberi_relacije(rels_xml)
        print(f"Najdeno relacij slik: {len(rid_to_orig)}")

        # 2. Izvoz slik z novim imenom (prefiks: basename_)
        rid_to_ime = {}
        for rid, orig_ime in rid_to_orig.items():
            novo_ime = f"{basename}_{orig_ime}"
            rid_to_ime[rid] = novo_ime

        stevec = 0
        for ime_v_zipu in z.namelist():
            if ime_v_zipu.startswith('word/media/'):
                orig_ime = os.path.basename(ime_v_zipu)
                novo_ime = f"{basename}_{orig_ime}"
                cilj = mapa_slik / novo_ime
                with z.open(ime_v_zipu) as src, open(cilj, 'wb') as dst:
                    shutil.copyfileobj(src, dst)
                normaliziraj_sliko(cilj)   # T-26-011: preveri in po potrebi prekodiraj
                stevec += 1

        print(f"Izvoženih slik: {stevec} → {mapa_slik}/")

        # 3. Sprememba document.xml
        doc_xml = z.read('word/document.xml').decode('utf-8')
        doc_xml_nov = zamenjaj_slike_v_xml(doc_xml, rid_to_ime)

        st_drawing = len(re.findall(r'\[SLIKA:', doc_xml_nov))
        print(f"Vstavljenih [SLIKA:...] referenc: {st_drawing}")

        # 4. Zapis novega docx brez medijev in vgrajevanj
        with zipfile.ZipFile(izhodna_pot, 'w', zipfile.ZIP_DEFLATED) as out_z:
            for item in z.infolist():
                # Izpustimo slike in OLE objekte (ni jih več v dokumentu)
                if item.filename.startswith('word/media/'):
                    continue
                if item.filename.startswith('word/embeddings/'):
                    continue
                if item.filename == 'word/document.xml':
                    out_z.writestr(item, doc_xml_nov.encode('utf-8'))
                else:
                    out_z.writestr(item, z.read(item.filename))

    # 5. Shrani JSON preslikavo
    mapa_json = mapa_slik / 'mapa_slik.json'
    with open(mapa_json, 'w', encoding='utf-8') as f:
        json.dump(rid_to_ime, f, ensure_ascii=False, indent=2)

    velikost_mb = izhodna_pot.stat().st_size / 1024 / 1024
    print(f"\nShranjen dokument brez slik: {izhodna_pot} ({velikost_mb:.1f} MB)")
    print(f"Preslikava slik (JSON): {mapa_json}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uporaba: python izvozi_slike.py <pot_do_docx>")
        sys.exit(1)
    izvozi_slike(sys.argv[1])

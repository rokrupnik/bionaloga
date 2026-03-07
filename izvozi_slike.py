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


def preberi_relacije(rels_xml: str) -> dict:
    """Vrne preslikavo {rId: ime_datoteke} za vse slike v relacijski datoteki."""
    rid_to_file = {}
    for m in re.finditer(r'<Relationship\s+Id="(rId\d+)"[^>]*Target="(media/[^"]+)"', rels_xml):
        rid = m.group(1)
        target = m.group(2)
        rid_to_file[rid] = os.path.basename(target)
    return rid_to_file


def zamenjaj_slike_v_xml(doc_xml: str, rid_to_ime: dict) -> str:
    """Zamenja w:drawing in w:pict elemente z besedilnimi placeholder-ji [SLIKA:ime]."""

    def placeholder_drawing(match):
        blok = match.group(0)
        # Poiščemo r:embed="rIdXX" ali r:link="rIdXX"
        rid_m = re.search(r'r:embed="(rId\d+)"', blok)
        if not rid_m:
            rid_m = re.search(r'r:link="(rId\d+)"', blok)
        if rid_m:
            rid = rid_m.group(1)
            ime = rid_to_ime.get(rid, f"neznana_{rid}")
            return f'<w:r><w:t>[SLIKA:{ime}]</w:t></w:r>'
        return '<w:r><w:t>[SLIKA:neznana]</w:t></w:r>'

    def placeholder_pict(match):
        blok = match.group(0)
        rid_m = re.search(r'r:id="(rId\d+)"', blok)
        if rid_m:
            rid = rid_m.group(1)
            ime = rid_to_ime.get(rid, f"neznana_{rid}")
            return f'<w:r><w:t>[SLIKA:{ime}]</w:t></w:r>'
        return '<w:r><w:t>[SLIKA:neznana]</w:t></w:r>'

    xml = re.sub(r'<w:drawing[ >].*?</w:drawing>', placeholder_drawing, doc_xml, flags=re.DOTALL)
    xml = re.sub(r'<w:pict>.*?</w:pict>', placeholder_pict, xml, flags=re.DOTALL)
    return xml


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

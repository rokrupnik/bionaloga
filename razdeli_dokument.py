#!/usr/bin/env python3
"""
razdeli_dokument.py — Razdeli lahek docx (po izvozi_slike.py) na manjše kose.

Uporaba:
    python razdeli_dokument.py <pot_do_docx> [naloge_na_kos]

    naloge_na_kos: število nalog v vsakem kosu (privzeto: 300)

Izhod:
    <ime>_del_01.docx, <ime>_del_02.docx, ... — kosi v isti mapi kot vhodna datoteka
    <ime>_razdelitev.json — podatki o razdelitvi (katera naloga je v katerem kosu)

Zazna začetek naloge: odstavek, ki se začne z "N." kjer N je celo število.
"""

import sys
import re
import zipfile
import json
from pathlib import Path


# Vzorec za prepoznavo začetka naloge (npr. "1.Besedilo", "42.Besedilo")
# Zahtevamo, da za številko in piko sledi ne-številka (da ne ujamemo "1.2" ipd.)
VZOREC_NALOGE = re.compile(r'^\d+\.[^\d]')

# Minimalni tekst za štetje znakov (groba ocena tokenov)
ZNAKI_NA_TOKEN = 4


def izvleci_besedilo_odstavka(p_xml: str) -> str:
    """Iz XML odstavka izvleče surovo besedilo."""
    return re.sub(r'<[^>]+>', '', p_xml).strip()


def razdeli_odstavke_po_nalogah(odstavki: list) -> list:
    """
    Grupira odstavke v naloge. Vsaka naloga začne z odstavkom, ki ustreza vzorcu.
    Vrne seznam skupin: [(stevilka_naloge, [odstavek_xml, ...]), ...]
    Odstavki pred prvo nalogo so v skupini z stevilko 0 (uvod).
    """
    naloge = []
    trenutna_skupina = []
    trenutna_stevilka = 0

    for p in odstavki:
        besedilo = izvleci_besedilo_odstavka(p)
        m = VZOREC_NALOGE.match(besedilo)
        if m:
            if trenutna_skupina:
                naloge.append((trenutna_stevilka, trenutna_skupina))
            trenutna_stevilka = int(besedilo.split('.')[0])
            trenutna_skupina = [p]
        else:
            trenutna_skupina.append(p)

    if trenutna_skupina:
        naloge.append((trenutna_stevilka, trenutna_skupina))

    return naloge


def sestavi_body_xml(odstavki: list, konec_sekcije: str) -> str:
    """Sestavi <w:body>...</w:body> iz odstavkov in ohrani sekcijsko definicijo."""
    vsebina = '\n'.join(odstavki)
    return f'<w:body>{vsebina}{konec_sekcije}</w:body>'


def izloci_body_in_odstavke(doc_xml: str):
    """
    Iz document.xml vrne:
    - pred_body: besedilo pred <w:body>
    - odstavke: seznam XML stringov odstavkov (brez zadnje <w:sectPr>)
    - konec_sekcije: <w:sectPr>...</w:sectPr> (zadnji element v body)
    - po_body: besedilo po </w:body>
    """
    body_m = re.search(r'(<w:body>)(.*)(</w:body>)', doc_xml, re.DOTALL)
    if not body_m:
        raise ValueError("Nisem našel <w:body> v document.xml")

    pred_body = doc_xml[:body_m.start()] + body_m.group(1)
    po_body = body_m.group(3) + doc_xml[body_m.end():]
    body_vsebina = body_m.group(2)

    # Izloci odstavke (<w:p ...>...</w:p>)
    odstavki = re.findall(r'<w:p[ >].*?</w:p>', body_vsebina, re.DOTALL)

    # Zadnji <w:sectPr> (definicija strani) - ohranimo ga v vsakem kosu
    konec_m = re.search(r'<w:sectPr[ >].*?</w:sectPr>', body_vsebina, re.DOTALL)
    konec_sekcije = konec_m.group(0) if konec_m else ''

    return pred_body, odstavki, konec_sekcije, po_body


def zapisi_kos_docx(
    vhodna_pot: Path,
    izhodna_pot: Path,
    pred_body: str,
    odstavki_kosa: list,
    konec_sekcije: str,
    po_body: str,
):
    """Ustvari nov docx s podmnožico odstavkov."""
    nov_body = pred_body + '\n'.join(odstavki_kosa) + konec_sekcije + po_body
    with zipfile.ZipFile(vhodna_pot, 'r') as vhod:
        with zipfile.ZipFile(izhodna_pot, 'w', zipfile.ZIP_DEFLATED) as izhod:
            for item in vhod.infolist():
                if item.filename == 'word/document.xml':
                    izhod.writestr(item, nov_body.encode('utf-8'))
                else:
                    izhod.writestr(item, vhod.read(item.filename))


def razdeli_dokument(vhodna_pot: str, naloge_na_kos: int = 300):
    vhodna_pot = Path(vhodna_pot).resolve()
    if not vhodna_pot.exists():
        print(f"Napaka: datoteka '{vhodna_pot}' ne obstaja.")
        sys.exit(1)

    basename = vhodna_pot.stem
    mapa = vhodna_pot.parent

    print(f"Berem: {vhodna_pot}")
    with zipfile.ZipFile(vhodna_pot, 'r') as z:
        doc_xml = z.read('word/document.xml').decode('utf-8')

    pred_body, vsi_odstavki, konec_sekcije, po_body = izloci_body_in_odstavke(doc_xml)

    print(f"Skupaj odstavkov: {len(vsi_odstavki)}")

    naloge = razdeli_odstavke_po_nalogah(vsi_odstavki)
    print(f"Zaznanih nalog: {len(naloge)}")

    # Ocena tokenov
    skupni_znaki = sum(len(izvleci_besedilo_odstavka(p)) for p in vsi_odstavki)
    ocena_tokenov = skupni_znaki // ZNAKI_NA_TOKEN
    print(f"Ocena tokenov celotnega dokumenta: ~{ocena_tokenov:,}")

    # Razdelitev nalog v kose
    kosi_nalog = [naloge[i:i + naloge_na_kos] for i in range(0, len(naloge), naloge_na_kos)]
    print(f"Razdelitev: {len(kosi_nalog)} kosov po ~{naloge_na_kos} nalog")

    razdelitev_json = {}

    for idx, kos in enumerate(kosi_nalog, 1):
        # Združimo odstavke vseh nalog v tem kosu
        odstavki_kosa = []
        stevilke = []
        for st_naloge, odst in kos:
            odstavki_kosa.extend(odst)
            stevilke.append(st_naloge)

        ime_kosa = f"{basename}_del_{idx:02d}.docx"
        izhodna_pot_kosa = mapa / ime_kosa

        znaki_kosa = sum(len(izvleci_besedilo_odstavka(p)) for p in odstavki_kosa)
        ocena_tok = znaki_kosa // ZNAKI_NA_TOKEN

        zapisi_kos_docx(vhodna_pot, izhodna_pot_kosa, pred_body, odstavki_kosa, konec_sekcije, po_body)

        razdelitev_json[ime_kosa] = {
            'kos': idx,
            'st_nalog': len(kos),
            'naloge_od': stevilke[0] if stevilke else None,
            'naloge_do': stevilke[-1] if stevilke else None,
            'ocena_tokenov': ocena_tok,
        }

        print(f"  [{idx:02d}] {ime_kosa}: naloge {stevilke[0]}–{stevilke[-1]}, ~{ocena_tok:,} tok")

    # Shrani JSON razdelitve
    json_pot = mapa / f"{basename}_razdelitev.json"
    with open(json_pot, 'w', encoding='utf-8') as f:
        json.dump(razdelitev_json, f, ensure_ascii=False, indent=2)

    print(f"\nRazdelitev shranjena: {json_pot}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uporaba: python razdeli_dokument.py <pot_do_docx> [naloge_na_kos]")
        sys.exit(1)
    naloge_na_kos = int(sys.argv[2]) if len(sys.argv) >= 3 else 300
    razdeli_dokument(sys.argv[1], naloge_na_kos)

import io
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from . import baza

SLIKE_POT = Path(__file__).parent.parent / "slike"

PODPRTI_FORMATI = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff"}


def _preveri_slike(besedilo: str, slike_po_imenu: dict) -> list[str]:
    """Vrne seznam manjkajočih ali nepodprtih slik za nalogo."""
    napake = []
    for m in re.finditer(r'\[SLIKA:([^\]]+)\]', besedilo):
        ime = m.group(1).strip()
        pot = slike_po_imenu.get(ime)
        if not pot or not pot.exists():
            napake.append(f"slika ne obstaja: {ime}")
        elif pot.suffix.lower() not in PODPRTI_FORMATI:
            napake.append(f"format ni podprt ({pot.suffix}): {ime}")
    return napake


def _dodaj_besedilo_s_slikami(doc: Document, besedilo: str, slike_po_imenu: dict, stevilka: int):
    """Razbije besedilo na segmente pri [SLIKA:...] in vstavi slike na pravo mesto.
    Placeholder-ji se ne izpišejo — bodisi se vstavi slika, bodisi se segment preskoči.
    """
    segmenti = re.split(r'(\[SLIKA:[^\]]+\])', besedilo)

    prvi = True
    for segment in segmenti:
        m = re.match(r'\[SLIKA:([^\]]+)\]', segment)
        if m:
            ime = m.group(1).strip()
            pot = slike_po_imenu.get(ime)
            if pot and pot.exists() and pot.suffix.lower() in PODPRTI_FORMATI:
                doc.add_picture(str(pot), width=Inches(4))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            # Manjkajoče / nepodprte slike tiho preskočimo (napaka je bila javljena prej)
        else:
            tekst = segment.strip()
            if not tekst:
                continue
            if prvi:
                odst = doc.add_paragraph()
                odst.paragraph_format.space_before = Pt(6)
                odst.add_run(f"{stevilka}. ").bold = True
                odst.add_run(tekst)
                prvi = False
            else:
                doc.add_paragraph(tekst)

    if prvi:
        odst = doc.add_paragraph()
        odst.paragraph_format.space_before = Pt(6)
        odst.add_run(f"{stevilka}. ").bold = True


def generiraj_test(ids_nalog: list[int], naslov: str = "Test iz biologije") -> tuple[bytes, list[str]]:
    """Ustvari .docx test z izbranimi nalogami.

    Vrne (vsebina_docx, seznam_napak).
    Naloge z manjkajočimi/nepodprtimi slikami so izpuščene iz dokumenta.
    """
    naloge = baza.pridobi_naloge_po_ids(ids_nalog)

    doc = Document()
    naslov_odst = doc.add_heading(naslov, level=0)
    naslov_odst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("")

    napake = []
    stevilka = 1
    for naloga in naloge:
        slike_po_imenu = {}
        if naloga["ima_sliko"]:
            for slika in baza.pridobi_slike_naloge(naloga["id"]):
                pot = SLIKE_POT / slika["ime_datoteke"]
                slike_po_imenu[pot.name] = pot

        napake_naloge = _preveri_slike(naloga["besedilo"], slike_po_imenu)
        if napake_naloge:
            napake.append(f"Naloga {naloga['id']}: {'; '.join(napake_naloge)} — izpuščena")
            continue

        _dodaj_besedilo_s_slikami(doc, naloga["besedilo"], slike_po_imenu, stevilka)
        stevilka += 1

    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.read(), napake

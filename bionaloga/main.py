import random
import webbrowser
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Annotated

from . import baza, generator

POT = Path(__file__).parent
SLIKE_POT = POT.parent / "slike"

app = FastAPI(title="BioNaloga")

app.mount("/slike", StaticFiles(directory=SLIKE_POT), name="slike")

predloge = Jinja2Templates(directory=POT / "templates")


def zgradi_drevo_vsebine(vse_vsebine):
    """Pretvori ploščat seznam vsebine v gnezdeno drevo."""
    po_kodi = {v["koda"]: dict(v) for v in vse_vsebine}
    koreni = []
    for koda, vozlisce in po_kodi.items():
        vozlisce["otroci"] = []
        nadrejena = vozlisce.get("nadrejena_koda")
        if nadrejena and nadrejena in po_kodi:
            po_kodi[nadrejena]["otroci"].append(vozlisce)
        else:
            koreni.append(vozlisce)
    koreni.sort(key=lambda x: x["koda"])
    for v in po_kodi.values():
        v["otroci"].sort(key=lambda x: x["koda"])
    return koreni


@app.get("/", response_class=HTMLResponse)
async def domov(request: Request):
    return predloge.TemplateResponse("sestavljanje.html", {
        "request": request,
        "drevo_vsebine": zgradi_drevo_vsebine(baza.pridobi_vsebino()),
        "tipi_nalog": baza.pridobi_tipe_nalog(),
    })


@app.get("/naloge", response_class=HTMLResponse)
async def seznam_nalog(
    request: Request,
    vsebina: Annotated[list[str] | None, Query()] = None,
    tip_id: int | None = None,
    ima_sliko: str | None = None,
):
    ima_sliko_bool = None
    if ima_sliko == "da":
        ima_sliko_bool = True
    elif ima_sliko == "ne":
        ima_sliko_bool = False

    naloge = baza.poisci_naloge(vsebina or [], tip_id, ima_sliko_bool)

    return predloge.TemplateResponse("_seznam_nalog.html", {
        "request": request,
        "naloge": naloge,
    })


@app.get("/naloge/nakljucne-po-tipu")
async def nakljucne_po_tipu(
    vsebina: Annotated[list[str] | None, Query()] = None,
    izbirni: int = 0,
    kratki: int = 0,
    daljsi: int = 0,
    dopolnjevanje: int = 0,
):
    # tip_id: 1=Izbirni, 2=Kratki, 3=Daljši, 4=Dopolnjevanje
    tipi = [(1, izbirni), (2, kratki), (3, daljsi), (4, dopolnjevanje)]
    rezultat = []
    for tip_id, stevilo in tipi:
        if stevilo <= 0:
            continue
        vse = baza.poisci_naloge(vsebina or [], tip_id, None)
        vzorec = random.sample(list(vse), min(stevilo, len(vse)))
        rezultat.extend(vzorec)
    return JSONResponse([
        {
            "id": n["id"],
            "besedilo": n["besedilo"],
            "vsebina_naziv": n["vsebina_naziv"] or "",
            "tip_naziv": n["tip_naziv"] or "",
        }
        for n in rezultat
    ])


@app.get("/naloge/{naloga_id}")
async def pridobi_nalogo(naloga_id: int):
    naloga = baza.pridobi_nalogo(naloga_id)
    if not naloga:
        return Response("Naloga ne obstaja.", status_code=404)
    return JSONResponse({
        "id": naloga["id"],
        "besedilo": naloga["besedilo"],
        "vsebina_koda": naloga["vsebina_koda"] or "",
        "tip_id": naloga["tip_id"] or "",
    })


@app.post("/naloge/{naloga_id}/uredi")
async def uredi_nalogo(
    naloga_id: int,
    besedilo: Annotated[str, Form()],
    vsebina_koda: Annotated[str, Form()] = "",
    tip_id: Annotated[str, Form()] = "",
):
    baza.posodobi_nalogo(
        naloga_id,
        besedilo,
        vsebina_koda or None,
        int(tip_id) if tip_id.isdigit() else None,
    )
    return Response(status_code=204)


@app.post("/izvozi")
async def izvozi_test(
    ids: Annotated[str, Form()],
    naslov: Annotated[str, Form()] = "Test iz biologije",
):
    id_seznam = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    if not id_seznam:
        return Response("Ni izbranih nalog.", status_code=400)

    vsebina, napake = generator.generiraj_test(id_seznam, naslov)

    if napake:
        import logging
        for n in napake:
            logging.warning(n)

    headers = {"Content-Disposition": f'attachment; filename="{naslov}.docx"'}
    if napake:
        headers["X-Izpuscene-Naloge"] = str(len(napake))

    return Response(
        content=vsebina,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers=headers,
    )


def zazeni():
    webbrowser.open("http://localhost:8000")
    import uvicorn
    uvicorn.run("bionaloga.main:app", host="0.0.0.0", port=8000, reload=False)

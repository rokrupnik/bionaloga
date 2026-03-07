"""
Ustvari bazo baza.db in vanjo uvozi vse klasificirane naloge iz map input/.
Slike se shranijo v mapo slike/.

Klasifikacija nalog je opravljena ročno na podlagi vsebine dokumentov.
"""

import sqlite3
import zipfile
import os
import shutil

DB_PATH = "baza.db"
SLIKE_DIR = "slike"
INPUT_DIR = "input"

# ---------------------------------------------------------------------------
# Shema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS vsebina (
    koda TEXT PRIMARY KEY,
    naziv TEXT NOT NULL,
    nadrejena_koda TEXT,
    raven INTEGER NOT NULL,
    FOREIGN KEY (nadrejena_koda) REFERENCES vsebina(koda)
);

CREATE TABLE IF NOT EXISTS tip_naloge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naziv TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS naloga (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    besedilo TEXT NOT NULL,
    vsebina_koda TEXT,
    tip_id INTEGER,
    ima_sliko BOOLEAN DEFAULT 0,
    tezavnost INTEGER,
    vir_datoteka TEXT,
    datum_uvoza DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vsebina_koda) REFERENCES vsebina(koda),
    FOREIGN KEY (tip_id) REFERENCES tip_naloge(id)
);

CREATE TABLE IF NOT EXISTS slika (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    naloga_id INTEGER NOT NULL,
    ime_datoteke TEXT NOT NULL,
    vrstni_red INTEGER DEFAULT 1,
    FOREIGN KEY (naloga_id) REFERENCES naloga(id)
);
"""

# ---------------------------------------------------------------------------
# Vsebina taksonomija (iz klasifikacija.html)
# ---------------------------------------------------------------------------

VSEBINA = [
    # raven 1
    ("01.00.00", "Življenje na Zemlji",               None,       1),
    ("02.00.00", "Celica kot živi sistem",             None,       1),
    ("03.00.00", "Dedovanje",                          None,       1),
    ("04.00.00", "Evolucija",                          None,       1),
    ("05.00.00", "Organizem kot živi sistem",          None,       1),
    ("06.00.00", "Ekologija",                          None,       1),
    ("07.00.00", "Biologija kot naravoslovna znanost", None,       1),

    # raven 2 — Življenje na Zemlji
    ("01.01.00", "Biologija – veda o življenju",       "01.00.00", 2),
    ("01.02.00", "Temeljne lastnosti živega",          "01.00.00", 2),

    # raven 2 — Celica
    ("02.01.00", "Celica kot osnovna enota organizmov","02.00.00", 2),
    ("02.02.00", "Presnova",                           "02.00.00", 2),

    # raven 3 — Celica > enota
    ("02.01.01", "Biotske membrane",                   "02.01.00", 3),
    ("02.01.02", "Celični organeli",                   "02.01.00", 3),

    # raven 3 — Celica > Presnova
    ("02.02.01", "Zgradba in delovanje encimov in drugih beljakovin", "02.02.00", 3),
    ("02.02.02", "Energijsko bogate snovi",            "02.02.00", 3),
    ("02.02.03", "Glikoliza in vrenje",                "02.02.00", 3),
    ("02.02.04", "Celično dihanje",                    "02.02.00", 3),
    ("02.02.05", "Fotosinteza",                        "02.02.00", 3),
    ("02.02.06", "Presnovne povezave",                 "02.02.00", 3),
    ("02.02.07", "Celična signalizacija, transport in regulacija celičnih procesov", "02.02.00", 3),
    ("02.02.08", "Nukleinske kisline",                 "02.02.00", 3),

    # raven 3 — Dedovanje
    ("03.00.01", "Celični cikel",                      "03.00.00", 3),
    ("03.00.02", "Gensko uravnavanje",                 "03.00.00", 3),
    ("03.00.03", "Spreminjanje dedne snovi",           "03.00.00", 3),
    ("03.00.04", "Načini dedovanja",                   "03.00.00", 3),

    # raven 3 — Evolucija
    ("04.00.01", "Nastanek in razvoj življenja",       "04.00.00", 3),
    ("04.00.02", "Mehanizmi evolucije",                "04.00.00", 3),
    ("04.00.03", "Evolucija človeka",                  "04.00.00", 3),
    ("04.00.04", "Razvrščanje organizmov v sisteme",   "04.00.00", 3),

    # raven 2 — Organizem
    ("05.01.00", "Bakterije",                          "05.00.00", 2),
    ("05.02.00", "Glive",                              "05.00.00", 2),
    ("05.03.00", "Rastline",                           "05.00.00", 2),
    ("05.04.00", "Živali",                             "05.00.00", 2),

    # raven 3 — Bakterije
    ("05.01.01", "Zgradba, razmnoževanje in delovanje bakterij", "05.01.00", 3),

    # raven 3 — Glive
    ("05.02.01", "Zgradba in prehranjevanje gliv",     "05.02.00", 3),

    # raven 3 — Rastline
    ("05.03.01", "Zgradba in delovanje rastlin",       "05.03.00", 3),
    ("05.03.02", "Rast in razvoj rastlin",             "05.03.00", 3),
    ("05.03.03", "Razmnoževanje rastlin",              "05.03.00", 3),
    ("05.03.04", "Strategije preživetja pri rastlinah","05.03.00", 3),

    # raven 3 — Živali
    ("05.04.01", "Zgradba in delovanje človeka in drugih živali", "05.04.00", 3),
    ("05.04.02", "Transportni sistemi",                "05.04.00", 3),
    ("05.04.03", "Imunski sistem",                     "05.04.00", 3),
    ("05.04.04", "Dihalni sistemi",                    "05.04.00", 3),
    ("05.04.05", "Prebavni sistemi",                   "05.04.00", 3),
    ("05.04.06", "Izločalni sistem",                   "05.04.00", 3),
    ("05.04.07", "Regulacijski sistemi",               "05.04.00", 3),
    ("05.04.08", "Hormonski sistem",                   "05.04.00", 3),
    ("05.04.09", "Živčni sistem",                      "05.04.00", 3),
    ("05.04.10", "Sprejemanje dražljajev – čutila",    "05.04.00", 3),
    ("05.04.11", "Zaščita, opora in gibanje",          "05.04.00", 3),
    ("05.04.12", "Razmnoževanje, rast in razvoj",      "05.04.00", 3),

    # raven 3 — Ekologija
    ("06.00.01", "Ekologija kot področje biologije",   "06.00.00", 3),
    ("06.00.02", "Osebki in populacije",               "06.00.00", 3),
    ("06.00.03", "Delovanje ekosistema",               "06.00.00", 3),
    ("06.00.04", "Ekosistemi in biosfera",             "06.00.00", 3),
    ("06.00.05", "Človek in narava",                   "06.00.00", 3),

    # raven 3 — Biologija kot zn.
    ("07.00.01", "Raziskovanje in poskusi",            "07.00.00", 3),
]

# ---------------------------------------------------------------------------
# Tipi nalog
# ---------------------------------------------------------------------------

TIPI = [
    "Izbirni tip",
    "Kratki odgovor",
    "Daljši odgovor",
    "Dopolnjevanje/ujemanje",
]

# ---------------------------------------------------------------------------
# Naloge — ročno klasificirane
# Format: (besedilo, vsebina_koda, tip_naziv, ima_sliko, tezavnost, vir)
# ---------------------------------------------------------------------------

NALOGE = [

    # ========================================================================
    # 2a EVO maj 2016.docx — EVOLUCIJA 2.del: sistem, virusi
    # ========================================================================

    # --- Nastanek in razvoj življenja ---
    (
        "Navedi glavne hipoteze o nastanku prvih celic!",
        "04.00.01", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Predstavi razvoj mnogoceličarjev iz bičkastih enoceličarjev!",
        "04.00.01", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Kakšne oblike metabolizma so se razvijale od prvih celic dalje?",
        "04.00.01", "Kratki odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Kaj je rastlinam omogočilo prehod na kopno?\n"
        "A Razvitost krovnih in opornih tkiv.\n"
        "B Tvorba semen.\n"
        "C Odsotnost plenilcev.\n"
        "D Razvoj klorofila.",
        "04.00.01", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Katere večje oblike življenja so se prve pojavile na kopnem?",
        "04.00.01", "Kratki odgovor", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "V čem je bila prednost žuželk, da so se tako hitro razvijale?",
        "04.00.01", "Kratki odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Naštej glavna izumrtja in vzroke zanje!",
        "04.00.01", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Kaj nam dokazujejo stromatoliti?",
        "04.00.01", "Kratki odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),

    # --- Evolucija človeka ---
    (
        "Do kakšnih sprememb na lobanji je prišlo ob razvoju človeka od najstarejših prednikov dalje?",
        "04.00.03", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "V evoluciji človekovih prednikov je prišlo do premika zatilne odprtine (mesta, kjer se lobanja "
        "povezuje s hrbtenico) z zadnjega na spodnji del lobanje. To je bila prilagoditev na:\n"
        "A drevesni način življenja,\n"
        "B pokončno hojo,\n"
        "C večje intelektualne sposobnosti,\n"
        "D tridimenzionalno gledanje.",
        "04.00.03", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Pri katerih hominidih se pojavijo grobovi? Kaj nam to dejanje sporoča?",
        "04.00.03", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Primati so se verjetno razvili iz prednikov, ki so prešli na drevesno življenje. "
        "Katere lastnosti je človeška vrsta v svojem razvoju pridobila pozneje, ko je že prešla v življenje v savanah?",
        "04.00.03", "Kratki odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "V čem je bila prednost modernega človeka (Homo sapiens) pred neandertalcem?",
        "04.00.03", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Homo habilis! (Opiši: kdo so bili, kdaj so živeli, katere sposobnosti so imeli.)",
        "04.00.03", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),

    # --- Razvrščanje organizmov ---
    (
        "Sodobne evolucijske raziskave ugotavljajo sorodnost med organizmi na osnovi:\n"
        "A uvrstitve organizmov v sistem;\n"
        "B primerjave fenotipov;\n"
        "C primerjave genomov;\n"
        "D primerjave poteka presnovnih procesov.",
        "04.00.04", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Predstavi dvočlensko poimenovanje!",
        "04.00.04", "Kratki odgovor", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Pravilni razpored sistematskih kategorij od najvišje do najnižje je:\n"
        "a) vrsta, rod, razred, družina, deblo, red, kraljestvo\n"
        "b) vrsta, rod, družina, red, razred, deblo, kraljestvo\n"
        "c) kraljestvo, deblo, razred, red, družina, rod, vrsta\n"
        "d) kraljestvo, deblo, razred, rod, družina, red, vrsta",
        "04.00.04", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Katera od navedenih sistematskih kategorij vključuje vse preostale?\n"
        "a) red\nb) razred\nc) družina\nd) rod",
        "04.00.04", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Kako si je Ernst Haeckel zamislil sistematsko razvrstitev organizmov?",
        "04.00.04", "Kratki odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Za rastlini, ki ju strokovno imenujemo Hacquetia epipactis in Epipactis heleborine, lahko trdimo da:\n"
        "a) spadata v isti rod, a različni vrsti;\n"
        "b) spadata v isto vrsto;\n"
        "c) spadata v različna rodova;\n"
        "d) nimata skupnih prednikov.",
        "04.00.04", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Z določevalnimi ključi:\n"
        "a) poimenujemo osebke\n"
        "b) dajemo osebkom latinska imena\n"
        "c) ugotovimo, kateri sistematski skupini pripada določen organizem\n"
        "d) določamo starost osebkov",
        "04.00.04", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),

    # --- Virusi (uvrščeno pod Organizem kot živi sistem) ---
    (
        "Skiciraj in označi virus!",
        "05.00.00", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Kako poteka lizogeni razmnoževalni ciklus virusov?",
        "05.00.00", "Daljši odgovor", False, 3,
        "2a EVO maj 2016.docx",
    ),
    (
        "Kaj je cepljenje? Kaj dosežemo z njim?",
        "05.00.00", "Daljši odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Osebe, ki so okužene z virusom HIV, so zelo občutljive za različne virusne in bakterijske infekcije. Zakaj?",
        "05.00.00", "Kratki odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Včasih z virusom okužene celice dolgo normalno delujejo, nenadoma pa se virus v njih aktivira. "
        "Kje je bil virus med normalnim delovanjem celice?",
        "05.00.00", "Kratki odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Kdo vse je tarča virusnih infekcij?",
        "05.00.00", "Kratki odgovor", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Retrovirusi so RNA virusi, ki imajo encim reverzno transkriptazo. Kaj je vloga tega encima?",
        "05.00.00", "Kratki odgovor", False, 2,
        "2a EVO maj 2016.docx",
    ),
    (
        "Kaj je fag?\n"
        "A Prednik današnjih virusov.\n"
        "B V gostiteljevo DNA vgrajeni virus.\n"
        "C Vsaka virusna nukleinska kislina.\n"
        "D Prvi odkriti virus.",
        "05.00.00", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),
    (
        "Katera trditev ne velja za viruse?\n"
        "A Virusi imajo celično steno.\n"
        "B Nekateri virusi vsebujejo DNA.\n"
        "C Virusi se razmnožujejo v gostiteljskih celicah.\n"
        "D Beljakovine virusa se sintetizirajo na ribosomih.",
        "05.00.00", "Izbirni tip", False, 1,
        "2a EVO maj 2016.docx",
    ),

    # ========================================================================
    # 79406_7. 03. 2026.docx — mešani evolucijski test
    # ========================================================================

    (
        "V populacijah številnih vrst rastlin s prevladujočimi obarvanimi cvetovi se pojavljajo belocvetni primerki. "
        "Pojav imenujemo albinizem, lastnost pa je recesivna. V neki populaciji spomladanskega žafrana "
        "(Crocus neapolitanus) so med 200 primerki našli 2 belocvetna. "
        "Kolikšna je v tej populaciji pogostost alela za belo barvo cvetov?\n"
        "A 1 %\nB 2 %\nC 10 %\nD 20 %\n[Rešitev: C]",
        "04.00.02", "Izbirni tip", False, 3,
        "79406_7. 03. 2026.docx",
    ),
    (
        "Znanstveniki domnevajo, da je bil razvoj neživega v živo postopen, številnih stopenj v tem razvoju pa si "
        "še vedno ne znajo predstavljati prav dobro. Pri kateri od naštetih stopenj razvoja nedvomno že lahko "
        "govorimo o živih bitjih?\n"
        "A Nastanejo beljakovine.\n"
        "B Z membrano se loči prostor od okolja.\n"
        "C Pojavijo se molekule, ki so sposobne podvojevanja.\n"
        "D Beljakovine in nukleinske kisline postanejo medsebojno odvisne.\n[Rešitev: D]",
        "04.00.01", "Izbirni tip", False, 2,
        "79406_7. 03. 2026.docx",
    ),
    (
        "V zadnjih desetletjih se je pojavilo vedno več bakterij, ki so odporne proti antibiotikom. "
        "Pojav odpornosti je potekal vzporedno z vedno bolj razširjeno rabo teh zdravil v medicini in veterinarstvu. "
        "Katera razlaga je v skladu z moderno teorijo evolucije in današnjim znanjem o antibiotikih?\n"
        "A Zaradi antibiotikov so propadle neodporne bakterije, odporne pa so se namnožile in prenesle to lastnost na potomce.\n"
        "B Antibiotiki v okolju so pospeševali takšne mutacije, da so nastajali aleli, ki so zapisovali odpornost.\n"
        "C Z rabo encimov, s katerimi so skušale bakterije razgraditi antibiotike, so se encimi tako spremenili.\n"
        "D Antibiotiki so hrana za nekatere bakterije, za druge pa so strupeni.\n[Rešitev: A]",
        "04.00.02", "Izbirni tip", False, 2,
        "79406_7. 03. 2026.docx",
    ),
    (
        "Katera značilnost človeške vrste ni prilagoditev na drevesni način življenja?\n"
        "A Praviloma se rodi samo en potomec naenkrat.\n"
        "B Palec je postavljen nasproti preostalim prstom.\n"
        "C Slab voh in dobro razvit globinski vid.\n"
        "D Hrbtenica ima dve krivini.\n[Rešitev: D]",
        "04.00.03", "Izbirni tip", False, 2,
        "79406_7. 03. 2026.docx",
    ),
    (
        "Kateri od naštetih načinov razmnoževanja omogoča največjo raznolikost znotraj vrste?\n"
        "A Razmnoževanje goveje trakulje v človeku.\n"
        "B Razmnoževanje krompirja z gomolji.\n"
        "C Prečna delitev paramecija.\n"
        "D Konjugacija bakterij.\n[Rešitev: D]",
        "04.00.02", "Izbirni tip", False, 2,
        "79406_7. 03. 2026.docx",
    ),
    (
        "Rastlini Ranunculus repens in Ranunculus acris, ki smo ju našli na istem travniku, sta:\n"
        "a) pripadnici iste vrste;\n"
        "b) pripadnici istega rodu;\n"
        "c) pripadnici iste populacije;\n"
        "d) nesorodni rastlini.\n[Rešitev: B]",
        "04.00.04", "Izbirni tip", False, 1,
        "79406_7. 03. 2026.docx",
    ),
    (
        "Na sliki so predstavniki: [slika]\n"
        "a) brstnic\nb) semenk\nc) dvokaličnic\nd) golosemenk\n[Rešitev: A]",
        "04.00.04", "Izbirni tip", True, 1,
        "79406_7. 03. 2026.docx",
    ),
    (
        "Kateri od prikazanih živali sta žuželki? [slika]\n"
        "a) a in c\nb) b in a\nc) e in f\nd) e in a\n[Rešitev: C]",
        "04.00.04", "Izbirni tip", True, 1,
        "79406_7. 03. 2026.docx",
    ),

    # ========================================================================
    # EVO   rezerva.docx — Evolucija celice + Ekologija
    # ========================================================================

    # — Neandertalci / evolucija človeka —
    (
        "Pred 120.000 leti so Evropo poseljevali človečnjaki, ki jih danes imenujemo neandertalci. "
        "Primerjava neandertalcev in današnjih ljudi kaže, da je bilo razmerje med telesno površino "
        "in prostornino telesa neandertalcev manjše. Kaj je bil pomen takšnega razmerja za neandertalce?\n"
        "A Omogočalo jim je lažje skrivanje pred plenilci.\n"
        "B Zmanjševalo je njihovo potrebo po hrani.\n"
        "C Omogočalo jim je lažje premikanje po globokem snegu.\n"
        "D Omogočalo jim je več prostora v votlinah, kjer so bivali.",
        "04.00.03", "Izbirni tip", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Katera značilnost človeške vrste ni prilagoditev na drevesni način življenja?\n"
        "A Praviloma se rodi samo en potomec naenkrat.\n"
        "B Palec je postavljen nasproti preostalim prstom.\n"
        "C Slab voh in dobro razvit globinski vid.\n"
        "D Hrbtenica ima dve krivini.",
        "04.00.03", "Izbirni tip", False, 2,
        "EVO   rezerva.docx",
    ),

    # — Evolucija celice (del x) —
    (
        "Našteti so nekateri dogodki iz evolucije življenja na Zemlji:\n"
        "A pojav živalskih vrst, B pojav prvih evkariontskih celic, C pojav prvih človečnjakov,\n"
        "D pojav kopenskih rastlin, E pojav prokariontov, F pojav kopenskih živali, G pojav večceličnih organizmov.\n"
        "Naštete dogodke razvrstite v pravilnem vrstnem redu, od evolucijsko starejšega do evolucijsko mlajšega.",
        "04.00.01", "Dopolnjevanje/ujemanje", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Pojav preprostih monomerov organskih molekul in povezovanje le-teh v polimere ter združevanje polimerov "
        "naj bi omogočilo nastanek prvih organizmov. Ti organizmi so bili anaerobni. Zakaj?",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Slika prikazuje evolucijski razvoj celic. S številkama 1 in 4 sta označena dva različna organizacijska "
        "tipa celic. Poimenujte ju. [slika]\nCelica številka 1:\nCelica številka 4:",
        "04.00.01", "Kratki odgovor", True, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Navedite tri skupne gradbene strukture ali organele, značilne za vse danes živeče celice.",
        "04.00.01", "Kratki odgovor", False, 1,
        "EVO   rezerva.docx",
    ),
    (
        "Celici, označeni s številkama 5 in 7 (na sliki evolucijskega razvoja celic), pripadata različnim "
        "prehranjevalnim tipom. Katerim?\nCelica številka 5:\nCelica številka 7:",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Kopičenje kisika v zemeljski atmosferi je posledica presnovnih procesov v celicah. Na sliki so "
        "obdobja razvoja različnih tipov celic označena na puščicah s črkami od A do F. "
        "V katerem od označenih obdobij je začel nastajati atmosferski molekularni kisik?",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Domnevo, da sta bila mitohondrij in kloroplast nekoč samostojni celici, potrjuje tudi to, "
        "da oba proizvajata lastne beljakovine. Kaj omogoča mitohondriju in kloroplastu sintezo lastnih beljakovin?",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Kaj potrjuje hipotezo, da so se mitohondriji razvili pred kloroplasti?",
        "04.00.01", "Kratki odgovor", False, 3,
        "EVO   rezerva.docx",
    ),

    # — Evolucija celice (del xx) —
    (
        "Katere presnovne procese so opravljali prvotni heterotrofni organizmi in kateri način presnove "
        "so razvile cianobakterije?\nHeterotrofi:\nCianobakterije:",
        "04.00.01", "Daljši odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Če se pri cianobakterijah in nekaterih drugih prokariontih ne bi razvili avtotrofni procesi, "
        "bi to kmalu omejilo razvoj in rast heterotrofnih organizmov ali celo povzročilo njihovo izumrtje. "
        "Razložite zakaj.",
        "04.00.01", "Daljši odgovor", False, 3,
        "EVO   rezerva.docx",
    ),
    (
        "Katera oblika energije in katere molekule so najpogosteje potrebne za avtotrofne procese primarnih producentov?\n"
        "Oblika energije:\nMolekule:",
        "04.00.01", "Kratki odgovor", False, 1,
        "EVO   rezerva.docx",
    ),
    (
        "Kot stranski produkt se v presnovnih procesih avtotrofov pogosto sprošča kisik. "
        "V evoluciji heterotrofov je bil kisik za organizme, ki so ga lahko uporabljali v presnovnih procesih, prednost. Zakaj?",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Kljub pomembnosti kisika lahko tudi danes številne bakterije živijo brez njega. "
        "Tiste, ki sodelujejo pri kroženju dušika, namesto kisika pri celičnem dihanju uporabijo nitrat. "
        "Kaj je vloga nitrata v tem procesu?",
        "04.00.01", "Kratki odgovor", False, 3,
        "EVO   rezerva.docx",
    ),
    (
        "Brez kisika lahko živijo tudi nekateri mikroorganizmi, ki sicer opravljajo aerobno celično dihanje. "
        "Taki organizmi so na primer glive kvasovke. Kje v celicah kvasovk poteka presnovni proces "
        "za pridobivanje energije, kadar nimajo kisika?",
        "02.02.03", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Kako se imenuje proces, ki ga kvasovke opravljajo, kadar nimajo na voljo kisika?",
        "02.02.03", "Kratki odgovor", False, 1,
        "EVO   rezerva.docx",
    ),

    # — Ekologija (del) —
    (
        "Slovenija je znana po izredni biotski raznovrstnosti. Kaj to pomeni?",
        "06.00.04", "Kratki odgovor", False, 1,
        "EVO   rezerva.docx",
    ),
    (
        "Na sliki je prometni znak. Na katerih delih cestišč je smiselna njegova namestitev? [slika]",
        "06.00.05", "Kratki odgovor", True, 1,
        "EVO   rezerva.docx",
    ),
    (
        "Dvoživke sodijo med bolj ogrožene živalske skupine pri nas. Kakšne so posledice upadanja "
        "njihovega števila v ekosistemih?",
        "06.00.03", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Napišite še dva vzroka zmanjševanja populacij dvoživk pri nas.",
        "06.00.05", "Kratki odgovor", False, 1,
        "EVO   rezerva.docx",
    ),
    (
        "Uporaba insekticidov v kmetijstvu ogroža ptice. Zakaj so v pticah koncentracije insekticidov "
        "tudi 10-krat večje kakor v žuželkah, proti katerim se insekticidi uporabljajo?",
        "06.00.03", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Rimljani so pred skoraj 2000 leti iz Azije v Evropo prinesli fazane. Naselitev fazanov je "
        "povzročila zmanjšanje števila prepelic in jerebic. Zakaj lahko vnos tuje vrste iztrebi ali "
        "ogrozi domače (avtohtone) vrste živali?",
        "06.00.05", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Koloradski hrošči so tuja vrsta, ki je bila prinesena iz Amerike skupaj s krompirjem. "
        "V našem okolju so izjemno uspešni. Zakaj so koloradski hrošči pri nas mnogo bolj uspešni kakor v Ameriki?",
        "06.00.05", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),
    (
        "Kljub temu da je gorništvo in pohodništvo ena najbolj priljubljenih oblik rekreacije in sprostitve, "
        "je gorskemu okolju škodljiva. Utemeljite zakaj.",
        "06.00.05", "Kratki odgovor", False, 2,
        "EVO   rezerva.docx",
    ),

    # — Samostojna naloga (Miller-Urey) —
    (
        "Miller-Ureyev poskus je pokazal možnost, da so prve:\n"
        "A beljakovine omogočile nastanek prvih pracelic.\n"
        "B beljakovine lahko nastale iz anorganskih snovi brez sodelovanja organizmov.\n"
        "C aminokisline lahko nastale iz anorganskih snovi brez sodelovanja organizmov.\n"
        "D anorganske molekule nastale v vodnem okolju brez sodelovanja organizmov.",
        "04.00.01", "Izbirni tip", False, 1,
        "EVO   rezerva.docx",
    ),

    # ========================================================================
    # EVO 2016 2a.docx — EVOLUCIJA 1.del
    # ========================================================================

    (
        "Kratko predstavi Lamarckov prispevek k evoluciji!",
        "04.00.02", "Kratki odgovor", False, 1,
        "EVO 2016 2a.docx",
    ),
    (
        "Kako so si nastanek življenja razlagali stari Grki?",
        "04.00.01", "Kratki odgovor", False, 1,
        "EVO 2016 2a.docx",
    ),
    (
        "Prikazana aparatura je bila uporabljena za preverjanje teorije o spontanem nastanku življenja. "
        "Kaj so z njo dokazali? [slika]",
        "04.00.01", "Izbirni tip", True, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Katera ugotovitev je skupna Lamarckovi in Darwinovi hipotezi o razvoju živega?\n"
        "A V življenju pridobljene lastnosti se prenašajo na potomce.\n"
        "B Živa bitja so prilagojena okolju, v katerem živijo.\n"
        "C Med osebki iste vrste poteka boj za obstanek.\n"
        "D Vsi osebki v populaciji so enaki.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2016 2a.docx",
    ),
    (
        "Kaj razlaga darvinistična teorija?",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "V zadnjih desetletjih se je pojavilo vedno več bakterij, ki so odporne na antibiotike. "
        "Katera razlaga je v skladu z moderno teorijo evolucije in današnjim znanjem o antibiotikih?\n"
        "A Zaradi antibiotikov so propadle neodporne bakterije, odporne pa so se namnožile in prenesle lastnost na potomce.\n"
        "B Antibiotiki v okolju so pospeševali mutacije za odpornost.\n"
        "C Z rabo encimov so se encimi spremenili in bolje razgrajevali antibiotike.\n"
        "D Antibiotiki so hrana za nekatere bakterije, za druge pa strup.",
        "04.00.02", "Izbirni tip", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Darwinovi ščinkavci in evolucijska teorija! "
        "(Opiši, kaj nam Darwinovi ščinkavci sporočajo o naravni selekciji in speciaciji.)",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Rast populacije je eksponentna, če:\n"
        "a) se osebki razmnožujejo samo nespolno\n"
        "b) se osebki razmnožujejo samo spolno\n"
        "c) ni upora okolja\n"
        "d) je nosilnost okolja stalna",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2016 2a.docx",
    ),
    (
        "Kakšni organizmi se ohranjajo med naravno selekcijo?\n"
        "A Boljši samo v reprodukcijskih sposobnostih.\n"
        "B Uspešnejši in bolj prilagojeni življenjskim razmeram v primerjavi z drugimi organizmi.\n"
        "C Organizmi, ki jih je izbral človek.\n"
        "D Vzdržljivejši, vendar z nesposobnostjo reprodukcije.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2016 2a.docx",
    ),
    (
        "Razloži pomen spolnega izbora!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Pri enem od poskusov so uporabili majhne ribe-gambuzije. Znani sta dve podvrsti, svetla in temna. "
        "V svetlo obarvan bazen so dali enako število rib obeh podvrst, nato so spustili pingvine. "
        "Ti so ulovili 70 % temnih in 30 % svetlih rib. Katera trditev velja?\n"
        "A Pingvini se raje hranijo s temnimi ribami.\n"
        "B Rezultati so slučajni.\n"
        "C Pingvini so ulovili več temnih, ker so manj prilagojene okolici, vendar bi v temnem bazenu dobili enak rezultat.\n"
        "D Ujeli so več temnih rib, ker so bile v svetlo obarvanem bazenu bolj opazne.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2016 2a.docx",
    ),
    (
        "Rastline na sliki so si po obliki podobne, čeprav spadajo v različne, sorodstveno zelo oddaljene "
        "družine. Bližnji sorodniki teh rastlin imajo večinoma neomesenela stebla. "
        "Kaj je pri rastlinah na sliki povzročilo razvoj podobnih morfoloških značilnosti? [slika]\n"
        "A Podobne življenjske razmere.\n"
        "B Zasedanje iste ekološke niše.\n"
        "C Podoben genotip.\n"
        "D Skupni plenilec.",
        "04.00.02", "Izbirni tip", True, 1,
        "EVO 2016 2a.docx",
    ),
    (
        "Prsne plavuti morskega psa in delfina:\n"
        "A imajo skupen izvor in opravljajo enako nalogo;\n"
        "B imajo skupen izvor in opravljajo različno nalogo;\n"
        "C imajo različen izvor in opravljajo enako nalogo;\n"
        "D imajo različen izvor in opravljajo različno nalogo.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2016 2a.docx",
    ),
    (
        "Predstavi umetni izbor! Navedi nekaj primerov!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "V skupini glavonožcev (npr.: lignji), ki so živeli v istem okolju, se je ena vrsta razvila v dve novi. "
        "Kaj se je zgodilo?",
        "04.00.02", "Kratki odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Kako utemeljuje vrsto ekološki koncept?",
        "04.00.02", "Kratki odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Kako pride do simpatrične speciacije? Navedi primer!",
        "04.00.02", "Daljši odgovor", False, 3,
        "EVO 2016 2a.docx",
    ),
    (
        "Kakšne so lahko predoploditvene pregrade med dvema vrstama?",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Kako se je odvijala evolucija konjev? Kakšen tip speciacije predstavlja?",
        "04.00.02", "Daljši odgovor", False, 3,
        "EVO 2016 2a.docx",
    ),
    (
        "Navedi primer adaptivne radiacije! Kdaj je tak način razvoja možen?",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Navedi:\n"
        "- štiri anorganske molekule v sekundarni atmosferi:\n"
        "- dva dejavnika, ki sta omogočila kemoevolucijo:",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Prve biološke molekule iz katerih so se kasneje razvili prvi organizmi, so nastale v vodi "
        "in ne v atmosferi. Zakaj?",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO 2016 2a.docx",
    ),
    (
        "Prikazana aparatura je znanstvenikom potrdila domnevo (Miller-Ureyev poskus). "
        "Kaj so z njo dokazali? [slika]",
        "04.00.01", "Izbirni tip", True, 1,
        "EVO 2016 2a.docx",
    ),

    # ========================================================================
    # EVO 2a 12.10.docx — EVOLUCIJA (splošni test, razred 2A)
    # ========================================================================

    (
        "Kaj razlaga evolucijska teorija?",
        "04.00.02", "Kratki odgovor", False, 1,
        "EVO 2a 12.10.docx",
    ),
    (
        "Kratko predstavi Lamarckov prispevek k evoluciji!",
        "04.00.02", "Kratki odgovor", False, 1,
        "EVO 2a 12.10.docx",
    ),
    (
        "Razloži temeljne principe evolucije z naravnim izborom!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Na kakšen način mutacije in spolno razmnoževanje prispevajo k evoluciji?",
        "04.00.02", "Kratki odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Kakšne so posledice:\n"
        "a) konvergentnega razvoja\n"
        "b) sukcesivnega razvoja\n"
        "c) divergentnega razvoja",
        "04.00.02", "Dopolnjevanje/ujemanje", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Rast populacije je eksponentna, če:\n"
        "a) se osebki razmnožujejo samo nespolno\n"
        "b) se osebki razmnožujejo samo spolno\n"
        "c) ni upora okolja\n"
        "d) je nosilnost okolja stalna",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2a 12.10.docx",
    ),
    (
        "Kakšni organizmi se ohranjajo med naravno selekcijo?\n"
        "A Boljši samo v reprodukcijskih sposobnostih.\n"
        "B Uspešnejši in bolj prilagojeni življenjskim razmeram v primerjavi z drugimi organizmi.\n"
        "C Organizmi, ki jih je izbral človek.\n"
        "D Vzdržljivejši, vendar z nesposobnostjo reprodukcije.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2a 12.10.docx",
    ),
    (
        "V prostoru, ki ga je naseljevala populacija, se je pojavila pregrada, ki je razmejila populacijo "
        "na dva dela in onemogočila komunikacijo med osebki. Kateri proces je potekel na vsaki strani pregrade?\n"
        "a) makroevolucija\nb) speciacija\nc) konvergenca\nd) vrsti ostajata nespremenjeni",
        "04.00.02", "Izbirni tip", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Pri enem od poskusov so uporabili majhne ribe-gambuzije. Znani sta dve podvrsti, svetla in temna. "
        "V svetlo obarvan bazen so dali enako število rib obeh podvrst, nato spustili pingvine, ki so ulovili "
        "70 % temnih in 30 % svetlih rib. Katera trditev velja?\n"
        "A Pingvini se raje hranijo s temnimi ribami.\n"
        "B Rezultati so slučajni.\n"
        "C Pingvini so ulovili več temnih, ker so manj prilagojene okolici, vendar bi v temnem bazenu dobili enak rezultat.\n"
        "D Ujeli so več temnih rib, ker so bile v svetlo obarvanem bazenu bolj opazne.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2a 12.10.docx",
    ),
    (
        "V zadnjih desetletjih se je pojavilo vedno več bakterij, ki so odporne na antibiotike. "
        "Katera razlaga je v skladu z moderno teorijo evolucije?\n"
        "A Zaradi antibiotikov so propadle neodporne bakterije, odporne pa so se namnožile.\n"
        "B Antibiotiki so pospeševali mutacije za odpornost.\n"
        "C Z rabo encimov so se encimi spremenili in bolje razgrajevali antibiotike.\n"
        "D Antibiotiki so hrana za nekatere bakterije, za druge pa strup.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2a 12.10.docx",
    ),
    (
        "Kdaj se v evoluciji telesna zgradba nekega organizma poenostavi?",
        "04.00.02", "Kratki odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "V skupini glavonožcev, ki so živeli v istem okolju, se je ena vrsta razvila v dve novi. Kaj se je zgodilo?\n"
        "a) mutacije in selekcija\n"
        "b) modifikacije in variacije\n"
        "c) modifikacije in usmerjena izolacija\n"
        "d) migracije in geografska izolacija",
        "04.00.02", "Izbirni tip", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Pojasni izraze:\n"
        "mimikrija:\n"
        "mimeza:\n"
        "aposemija:\n"
        "koacervat:",
        "04.00.02", "Dopolnjevanje/ujemanje", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Opiši primer naravne selekcije na primeru brezovega pedica!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Predstavi primer umetnega izbora na primeru!",
        "04.00.02", "Daljši odgovor", False, 1,
        "EVO 2a 12.10.docx",
    ),
    (
        "V kakšnih pogojih nastopi adaptivna radiacija? Primer!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Kako so nastale prve prokariontske celice?",
        "04.00.01", "Daljši odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Na katerih dejstvih temeljijo domneve, da je življenje prišlo na Zemljo iz drugih planetov?",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Predstavi nastajanje kisika v vodi in ozračju v procesu nastajanja življenja!",
        "04.00.01", "Daljši odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Katere možne poti nastanka mnogoceličnosti poznaš?",
        "04.00.01", "Daljši odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Kdo so bili prvi kopenski organizmi in katere probleme so morali reševati?",
        "04.00.01", "Daljši odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),
    (
        "Zakaj pravimo, da imamo današnji organizmi enako dolgo evolucijsko zgodovino?",
        "04.00.01", "Kratki odgovor", False, 2,
        "EVO 2a 12.10.docx",
    ),

    # ========================================================================
    # EVO 2e 10.docx — EVOLUCIJA (razred 2.E)
    # ========================================================================

    (
        "Katera ugotovitev je skupna Lamarckovi in Darwinovi hipotezi o razvoju živega?\n"
        "A V življenju pridobljene lastnosti se prenašajo na potomce.\n"
        "B Živa bitja so prilagojena okolju, v katerem živijo.\n"
        "C Med osebki iste vrste poteka boj za obstanek.\n"
        "D Vsi osebki v populaciji so enaki.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "Kakšni organizmi se ohranjajo med naravno selekcijo?\n"
        "A Boljši samo v reprodukcijskih sposobnostih.\n"
        "B Uspešnejši in bolj prilagojeni življenjskim razmeram v primerjavi z drugimi organizmi.\n"
        "C Organizmi, ki jih je izbral človek.\n"
        "D Vzdržljivejši, vendar z nesposobnostjo reprodukcije.",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "V prostoru, ki ga je naseljevala populacija, se je pojavila pregrada, ki je razmejila populacijo "
        "na dva dela. Kateri proces je potekel na vsaki strani pregrade?\n"
        "a) makroevolucija\nb) speciacija\nc) konvergenca\nd) vrsti ostajata nespremenjeni",
        "04.00.02", "Izbirni tip", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Katera oblika razvoja / kateri procesi v evoluciji privedejo do večje raznolikosti med osebki?",
        "04.00.02", "Kratki odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Katera od trditev je veljala v preteklosti, danes pa ni več veljavna?\n"
        "A Morfološka podobnost med vrstami še ni nujno znak sorodnosti.\n"
        "B Vrste se razlikujejo.\n"
        "C Organizmi so prilagojeni okolju, v katerem živijo.\n"
        "D Lastnosti, ki so se razvile pri posamezniku kot prilagoditev na okolje, se dedujejo.",
        "04.00.02", "Izbirni tip", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Speciacija je bistven proces evolucije. Pogosto je vzrok izolacija. Naštej vzroke za izolacijo!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Rast populacije je eksponentna, če:\n"
        "a) se osebki razmnožujejo samo nespolno\n"
        "b) se osebki razmnožujejo samo spolno\n"
        "c) ni upora okolja\n"
        "d) je nosilnost okolja stalna",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "Kako vplivajo drugi plenilci (lisice, sove) na nosilnost okolja za zajce?\n"
        "a) jo povečujejo\nb) jo zmanjšujejo\nc) ne vplivajo nanjo",
        "06.00.02", "Izbirni tip", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "Kdaj se v evoluciji telesna zgradba nekega organizma poenostavi? Primer:",
        "04.00.02", "Kratki odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Pojasni izraze:\n"
        "mimikrija:\n"
        "mimeza:\n"
        "aposemija:\n"
        "variabilnost:",
        "04.00.02", "Dopolnjevanje/ujemanje", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Razloži pojem iz evolucije: PRILAGOJENOST! Predstavi na konkretnem primeru!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Naravni izbor deluje na:\n"
        "a) fenotip\nb) genotip\nc) na najbolj prilagojene\nd) na najmanj prilagojene",
        "04.00.02", "Izbirni tip", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "Čemu služi čezmerno potomstvo in kako je s preživetjem? Primer!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Kateri so glavni principi Darwinove evolucijske teorije?",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Katera komponenta populacije je pomembna za naravni izbor?",
        "04.00.02", "Kratki odgovor", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "Kako je s fenotipskimi spremembami na populaciji? Kaj jih določa? Predstavi na primeru.",
        "04.00.02", "Daljši odgovor", False, 3,
        "EVO 2e 10.docx",
    ),
    (
        "Opiši primer brezovega pedica z vidika evolucije!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Kako poteka umetni izbor? Predstavi na primeru!",
        "04.00.02", "Daljši odgovor", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "Kakšne so prednosti in slabosti spolnega in nespolnega razmnoževanja?",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Zakaj različni pesticidi v začetku dokaj uspešno pobijejo večino nezaželenih žuželk, "
        "z večkratno uporabo pa postajajo vse manj učinkoviti?",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Kako poteka sukcesivni razvoj?",
        "04.00.02", "Kratki odgovor", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "Kako se razvijejo analogne lastnosti? Posledica kakšnega razvoja so?",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Ali je regresiven razvoj škodljiv za organizme? Utemelji!",
        "04.00.02", "Kratki odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Posledica česa je adaptivna radiacija? Primer!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Kaj je vrsta?",
        "04.00.02", "Kratki odgovor", False, 1,
        "EVO 2e 10.docx",
    ),
    (
        "Naštej 6 vrst različnih dokazov za evolucijo!",
        "04.00.02", "Daljši odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
    (
        "Kaj pomeni »nepovratnost« evolucije?",
        "04.00.02", "Kratki odgovor", False, 2,
        "EVO 2e 10.docx",
    ),
]

# ---------------------------------------------------------------------------
# Slike: kateri nalogi pripada katera slika v kateri datoteki
# Format: (vir_datoteka, media_ime_v_docx, naloga_besedilo_fragment, vrstni_red)
# ---------------------------------------------------------------------------

SLIKE_MAPIRANJE = [
    # 79406_7. 03. 2026.docx
    ("79406_7. 03. 2026.docx", "word/media/image1.wmf", "Na sliki so predstavniki:", 1),
    ("79406_7. 03. 2026.docx", "word/media/image2.wmf", "Kateri od prikazanih živali sta žuželki", 1),

    # EVO rezerva.docx
    ("EVO   rezerva.docx", "word/media/image1.emf", "Slika prikazuje evolucijski razvoj celic", 1),
    ("EVO   rezerva.docx", "word/media/image2.png", "Na sliki je prometni znak", 1),

    # EVO 2016 2a.docx — image3 je pri vprašanju o aparaturi (Miller-Urey, zadnje vprašanje)
    # image1 in image2 sta verjetno pri vprašanjih sredi dokumenta
    ("EVO 2016 2a.docx", "word/media/image1.png",  "Prikazana aparatura je bila uporabljena", 1),
    ("EVO 2016 2a.docx", "word/media/image2.emf",  "Rastline na sliki so si po obliki podobne", 1),
    ("EVO 2016 2a.docx", "word/media/image3.png",  "Prikazana aparatura je znanstvenikom potrdila", 1),
]


# ---------------------------------------------------------------------------
# Pomožne funkcije
# ---------------------------------------------------------------------------

def izvleci_slike(vir: str, media_pot: str, ciljno_ime: str) -> None:
    """Izvleče sliko iz docx v mapo slike/."""
    src = os.path.join(INPUT_DIR, vir)
    dst = os.path.join(SLIKE_DIR, ciljno_ime)
    with zipfile.ZipFile(src) as z:
        with z.open(media_pot) as src_f, open(dst, "wb") as dst_f:
            shutil.copyfileobj(src_f, dst_f)


def poisci_naloga_id(cur, fragment: str) -> int | None:
    """Poišče naloga.id po delčku besedila."""
    cur.execute(
        "SELECT id FROM naloga WHERE besedilo LIKE ? LIMIT 1",
        (f"%{fragment}%",),
    )
    row = cur.fetchone()
    return row[0] if row else None


# ---------------------------------------------------------------------------
# Glavni uvoz
# ---------------------------------------------------------------------------

def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"Obstoječa baza {DB_PATH} izbrisana.")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # shema
    cur.executescript(SCHEMA)
    con.commit()
    print("Shema ustvarjena.")

    # vsebina
    cur.executemany(
        "INSERT INTO vsebina (koda, naziv, nadrejena_koda, raven) VALUES (?, ?, ?, ?)",
        VSEBINA,
    )
    con.commit()
    print(f"Vsebina: {len(VSEBINA)} vnosov.")

    # tipi nalog
    cur.executemany("INSERT INTO tip_naloge (naziv) VALUES (?)", [(t,) for t in TIPI])
    con.commit()

    # tip_id lookup
    cur.execute("SELECT id, naziv FROM tip_naloge")
    tip_map = {naziv: id_ for id_, naziv in cur.fetchall()}

    # naloge
    vstavili = 0
    for besedilo, vsebina_koda, tip_naziv, ima_sliko, tezavnost, vir in NALOGE:
        tip_id = tip_map.get(tip_naziv)
        cur.execute(
            "INSERT INTO naloga (besedilo, vsebina_koda, tip_id, ima_sliko, tezavnost, vir_datoteka) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (besedilo, vsebina_koda, tip_id, int(ima_sliko), tezavnost, vir),
        )
        vstavili += 1
    con.commit()
    print(f"Naloge: {vstavili} vstavljena.")

    # slike
    os.makedirs(SLIKE_DIR, exist_ok=True)
    for vir, media_pot, fragment, vrstni_red in SLIKE_MAPIRANJE:
        naloga_id = poisci_naloga_id(cur, fragment)
        if naloga_id is None:
            print(f"  OPOZORILO: naloga z besedilom '{fragment[:40]}' ni najdena.")
            continue

        ext = os.path.splitext(media_pot)[1]
        ime_datoteke = f"naloga_{naloga_id}_{vrstni_red}{ext}"

        try:
            izvleci_slike(vir, media_pot, ime_datoteke)
            cur.execute(
                "INSERT INTO slika (naloga_id, ime_datoteke, vrstni_red) VALUES (?, ?, ?)",
                (naloga_id, ime_datoteke, vrstni_red),
            )
            print(f"  Slika {ime_datoteke} → naloga {naloga_id}")
        except Exception as e:
            print(f"  NAPAKA pri sliki {media_pot}: {e}")

    con.commit()
    con.close()
    print("\nUvoz zaključen.")


if __name__ == "__main__":
    main()

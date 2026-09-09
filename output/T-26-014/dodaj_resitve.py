"""Enkratna skripta za T-26-014 (krog 2): osnutek rešitev za 19 izbranih nalog.

Za vseh 19 nalog testa „Test: Dedovanje“ zapiše osnutek rešitve v stolpec
`naloga.resitev` in znova izvozi dokument z razdelkom „Rešitve“ na koncu.

Rešitve so OSNUTEK (avtor: operator, ne učitelj) — vsaka je zato označena s
predpono `[OSNUTEK – preveri]`.

Brez argumenta teče kot suhi tek (nič se ne zapiše). Za zapis v bazo:

    python3 output/T-26-014/dodaj_resitve.py --write
"""
import sqlite3
import sys
from pathlib import Path

KOREN = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(KOREN))

from bionaloga import generator  # noqa: E402

OZNAKA = "[OSNUTEK – preveri] "

# Isti izbor kot v prvem krogu (glej ## Result v nalogi) — brez ponovnega izbora.
RESITVE = [
    (21949, "C) Nekateri geni pri moškem. Moški ima spolna kromosoma X in Y, ki "
            "nista homologna. Geni na X, ki jih na Y ni (in obratno), zato pri "
            "moškem nastopajo samo v enem izvodu — niso v parih."),
    (4019, "D) monohibridno dominantno recesivno. Razmerje v F2 je 211 : 69, "
           "torej približno 3 : 1, kar je značilno za monohibridno križanje z "
           "dominantno-recesivnim dedovanjem (zelena barva je dominantna, "
           "rumena recesivna)."),
    (17401, "D) Konjugacija paramecijev. To je edini našteti primer, pri katerem "
            "si dva osebka izmenjata dedni material in nastanejo nove "
            "kombinacije genov. Ostali trije načini (razmnoževanje trakulje s "
            "samooprašitvijo oz. samooploditvijo, gomolji krompirja, vzdolžna "
            "delitev evglene) dajo potomce, ki so dedno (skoraj) enaki staršu."),
    (978, "d) praspolna celica v modih. Mejoza poteka samo pri nastanku spolnih "
          "celic. Jajčna celica je končni produkt mejoze in se ne deli več, "
          "celica plute je odmrla, celice meristema pa se delijo z mitozo."),
    (19608, "B) Prekrižanje homolognih kromosomov. Skica prikazuje izmenjavo "
            "odsekov med kromatidama homolognih kromosomov (crossing over): "
            "kromosoma po dogodku nosita drugačno kombinacijo alelov kot pred "
            "njim. Dogodek poteče v profazi prve mejotske delitve."),
    (16048, "D) Podvojevanje molekul DNA. DNA se podvoji v interfazi, torej še "
            "pred začetkom mejoze. Prekrižanje kromatid in ločevanje homolognih "
            "kromosomov potekata med prvo mejotsko delitvijo, ločevanje "
            "kromatid pa šele med drugo."),
    (3980, "D) 3/16. Križanje BbDd × BbDd: delež črnih (B_) je 3/4, delež "
           "kratkodlakavih (dd) je 1/4. Ker gena nista vezana, se verjetnosti "
           "množita: 3/4 × 1/4 = 3/16."),
    (17796, "B) Kadar sta gena na različnih kromosomih. Le takrat se para alelov "
            "med mejozo razporejata neodvisno drug od drugega, zato nastanejo "
            "vse štiri vrste gamet v enakem razmerju. Če sta gena na istem "
            "kromosomu (vezana), prevladujeta starševski kombinaciji."),
    (19645, "D) Zaporedje 2 in zaporedje 3. Podvojevanje DNA je "
            "polkonzervativno: po dveh delitvah v gojišču z neradioaktivnim "
            "timinom sta od štirih molekul DNA dve sestavljeni iz ene "
            "označene in ene neoznačene verige (zaporedje 2), dve pa sta "
            "povsem neoznačeni (zaporedje 3). Molekula z obema označenima "
            "verigama (zaporedje 1) ne more nastati."),
    (10310, "B) Ker v njih odpove nadzor nad delovanjem nekaterih genov, ki "
            "urejajo celični cikel. Rak je posledica mutacij v genih za nadzor "
            "celičnega cikla; celica se zato deli, tudi ko za to ni signala."),
    (9804, "1920 vinskih mušic. Frekvenca recesivnega alela je q = 0,2, zato je "
           "delež recesivnih homozigotov (zakrnela krila) q² = 0,04, torej "
           "0,04 × 2000 = 80 mušic. Normalno razvita krila ima "
           "2000 − 80 = 1920 mušic."),
    (3727, "Dominanten alel: alel za rdeče oči. Recesivni alel: alel za bele "
           "oči. Križanje belookega samca z rdečeoko samico je dalo samo "
           "rdečeoko potomstvo, torej alel za bele oči v potomcih ni prišel do "
           "izraza."),
    (8352, "Skica prikazuje pripravo rekombinantne DNA in vnos v bakterijo: "
           "izbrani človeški gen vstavijo v bakterijski plazmid, ta pa gen "
           "prenese v bakterijsko celico. Postopek omogoča, da se človeški gen "
           "v bakteriji pomnožuje in izraža, tako da bakterija izdeluje "
           "človeško beljakovino (npr. inzulin ali rastni hormon) v velikih "
           "količinah."),
    (3352, "Pričakujemo krvni skupini B in 0 v razmerju 3 : 1. Starša sta "
           "heterozigota, torej I(B)i × I(B)i. Punnettov kvadrat:\n"
           "         I(B)      i\n"
           "  I(B)   I(B)I(B)  I(B)i\n"
           "  i      I(B)i     ii\n"
           "Trije od štirih potomcev imajo krvno skupino B (I(B)I(B) ali "
           "I(B)i), eden od štirih pa krvno skupino 0 (ii)."),
    (21852,
     "x.1 Vitamin D omogoča vsrkavanje kalcija in fosfata iz prebavil. Ob "
     "pomanjkanju se teh mineralov vsrka premalo, zato jih je v krvi in v "
     "kostnem tkivu manj; kost se slabše mineralizira, ostane mehkejša in se "
     "deformira.\n"
     "x.2 Fosfati, ki se ne vsrkajo nazaj iz ledvičnih cevk, ostanejo v "
     "primarnem seču in se izločijo s sečem iz telesa.\n"
     "x.3 Bolezen povzroča dominantni alel na kromosomu X. Oseba A je zdrava "
     "ženska, torej X(a)X(a); oseba B je bolan moški, torej X(A)Y (A = "
     "dominantni bolezenski alel, a = zdravi alel).\n"
     "x.4 Bolan oče X(A)Y da vsem hčeram svoj edini kromosom X, na katerem je "
     "dominantni bolezenski alel; mati jim da X(a). Vse hčere so torej "
     "X(A)X(a) in ker je alel dominanten, vse zbolijo.\n"
     "x.5 Sin C je od očeta dobil kromosom Y (ne X) in od zdrave matere "
     "kromosom X(a). Njegov genotip je X(a)Y, zato je zdrav.\n"
     "x.6 Oseba C je X(a)Y, oseba T pa je zdrava ženska X(a)X(a). Noben od "
     "staršev nima bolezenskega alela, zato bodo vsi otroci zdravi — "
     "verjetnost je 1 (100 %).\n"
     "x.7 Oseba G je X(A)X(a), oseba U pa zdrav moški X(a)Y. Polovica otrok "
     "dobi od matere X(A) in zboli, polovica dobi X(a) in je zdrava — "
     "verjetnost za zdravega otroka je 1/2 (50 %).\n"
     "x.8 Pri hipofosfatnem rahitisu okvara ni v vsrkavanju iz prebavil, ampak "
     "v ledvicah. Tudi če z vitaminom D povečamo vsrkavanje fosfatov iz "
     "črevesa, se ti v ledvicah ne vsrkajo nazaj in se izločijo s sečem, zato "
     "količina fosfatov v krvi in v kosteh ne naraste."),
    (4097, "Oče je kratkorep in homozigot za recesivni alel, torej dd "
           "(fenotip: kratek rep). Shema križanja: Dd (dolgorepa mati) × dd "
           "(kratkorep oče) → gamete D, d × d, d → potomci 1/2 Dd (dolgorepi) "
           "in 1/2 dd (kratkorepi), kar se ujema z opisanim razmerjem "
           "1 : 1."),
    (8396, "Da, rogate živali se lahko še pojavijo. Brezrožnost je dominantna "
           "lastnost, zato so med brezrogimi živalmi tudi heterozigoti (Bb), ki "
           "so prenašalci recesivnega alela za rogove. Če se parita dva "
           "heterozigota, je pričakovana četrtina potomcev bb — torej rogatih."),
    (10948, "Raznolikost živih bitij je posledica mutacij, ki so izvor novih "
            "alelov, in spolnega razmnoževanja, ki te alele prerazporeja v nove "
            "kombinacije. Primer: med mejozo pri človeku se homologni "
            "kromosomi prekrižajo (crossing over) in se v gamete razporedijo "
            "naključno, pri oploditvi pa se naključno združita dve od milijonov "
            "možnih gamet — zato ima vsak otrok drugačno kombinacijo alelov kot "
            "starša in kot bratje in sestre. Na to raznolikost nato deluje "
            "naravni izbor."),
    (13089, "Operon omogoča, da se skupina genov za isto presnovno pot vklopi ali "
            "izklopi hkrati, in sicer takrat, ko je to potrebno. Bakterija tako "
            "izdeluje encime samo takrat, ko je v okolju ustrezen substrat "
            "(npr. laktozni operon se vklopi šele ob prisotnosti laktoze). "
            "Biološki pomen je varčevanje z energijo in gradniki ter hitro "
            "prilagajanje spremembam v okolju."),
]


def main() -> None:
    zapisi = "--write" in sys.argv
    ids = [i for i, _ in RESITVE]
    assert len(ids) == 19 and len(set(ids)) == 19, "pričakovanih 19 različnih id-jev"

    conn = sqlite3.connect(KOREN / "baza.db")
    try:
        obstojece = {
            r[0]: r[1]
            for r in conn.execute(
                f"SELECT id, resitev FROM naloga WHERE id IN ({','.join('?' * len(ids))})",
                ids,
            )
        }
        manjka = [i for i in ids if i not in obstojece]
        assert not manjka, f"v bazi ni nalog: {manjka}"
        prepisi = [i for i in ids if (obstojece[i] or "").strip()]
        if prepisi:
            print(f"OPOZORILO: te naloge že imajo rešitev, prepisal bi jih: {prepisi}")

        for i, r in RESITVE:
            besedilo = OZNAKA + r
            print(f"id {i}: {len(besedilo)} znakov")
            if zapisi:
                conn.execute("UPDATE naloga SET resitev = ? WHERE id = ?", (besedilo, i))
        if zapisi:
            conn.commit()
            print("Zapisano v bazo.")
        else:
            print("SUHI TEK — nič ni zapisano. Za zapis dodaj --write.")
            return
    finally:
        conn.close()

    vsebina_docx, napake = generator.generiraj_test(
        ids, naslov="Test: Dedovanje", z_resitvami=True
    )
    pot = Path(__file__).parent / "test_dedovanje.docx"
    pot.write_bytes(vsebina_docx)
    print("NAPAKE:", napake)
    print("Shranjeno:", pot, pot.stat().st_size, "B")


if __name__ == "__main__":
    main()

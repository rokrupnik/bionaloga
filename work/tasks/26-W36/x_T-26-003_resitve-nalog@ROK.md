---
task: T-26-003
title: Rešitve nalog — hramba in izvoz testa z rešitvami
status: done
assignee: [ROK]
requested-by: VITAL
week: 26-W36
created: 2026-09-05
completed: 2026-09-05
notified:
blocked-by: []
visibility: team
---

# Rešitve nalog — hramba in izvoz testa z rešitvami

## Goal

Učitelj lahko isti test izvozi v dveh različicah: brez rešitev (za dijake) in
z rešitvami (zase), ker so v RIC dokumentih rešitve navedene na koncu vsakega
dokumenta.

## Scope

In: stolpec `resitev` v tabeli `naloga`, prikaz/urejanje rešitve v modalu,
izbira "izvozi z rešitvami" ob izvozu, izris rešitev v `generator.py`.
Out: samodejno ocenjevanje, točkovnik.

## Acceptance criteria

- [x] Naloga lahko hrani rešitev (prazno, kjer je ni)
- [x] Rešitev je vidna in urejljiva v modalu za urejanje naloge
- [x] `POST /izvozi` sprejme zastavico za rešitve; brez nje se izvoz ne
      spremeni glede na sedanjega
- [x] Z zastavico so rešitve v .docx izpisane pri vsaki nalogi (ali na koncu)

## Notes

Vital, e-pošta 13. 6. 2026: "Na koncu dokumenta so rešitve za posamezno
nalogo. Če bi se lahko tudi to dalo zraven označit, če bi želel naredit test
z rešitvami..."

**Odvisnost od ingesta — pomembno:** rešitve so v RIC dokumentih na koncu, kar
pomeni, da jih je treba **zajeti med uvozom**. Če se uvoz izvede brez njih, jih
kasneje ni mogoče dodati brez ponovnega klasificiranja (in ponovnega stroška
API-ja). Zato naj ingest RIC nalog rešitve zajame in shrani že v prvem prehodu,
tudi če se ta naloga (vmesnik + izvoz) izvede kasneje.

Za obstoječe (šolske) naloge rešitev večinoma ni — stolpec ostane prazen.

## Plan

<!-- Napisano pred izvedbo. -->

## Result

Stolpec `naloga.resitev` je nastal že ob uvozu RIC nalog (1.135 jih ima
rešitev). Modal ima polje »Rešitev (neobvezno)«, izvoz pa izbiro
»Dodaj rešitve na konec«.

Rešitve gredo na novo stran pod naslov »Rešitve«, oštevilčene po nalogah v
testu — izpuščene naloge ne premaknejo številk. Naloga brez rešitve dobi »—«,
izvoz pa v opozorilih pove, koliko takih je.

**Popravljena obstoječa napaka:** ime datoteke gre v HTTP glavo, ki je latin-1,
zato bi vsak naslov s šumniki (»Test čebele«) vrgel `UnicodeEncodeError` in
izvoz bi padel s 500. Zdaj ASCII različica + RFC 5987 `filename*`.

**Ujeta regresija:** nalaganje/brisanje slike je klicalo `posodobi_nalogo()`
brez rešitve in bi jo tiho prepisalo s prazno. Pokrito s testom.

Testi: `test_vmesnik.py::test_izvoz_z_resitvami`, `::test_resitev_prezivi_slike`,
`::test_ime_datoteke_s_sumniki`.

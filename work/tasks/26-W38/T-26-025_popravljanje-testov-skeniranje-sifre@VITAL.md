---
task: T-26-025
title: Popravljanje testov: skeniranje, AI ocenjevanje, šifre namesto imen
status: waiting
discord-thread: 1551347534369132675
assignee: [VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: [T-26-020]
visibility: team
---

# Popravljanje testov: skeniranje, AI ocenjevanje, šifre namesto imen

## Goal

Učitelj natisne test iz aplikacije, učenci ga rešijo na papir, učitelj
rešene teste skenira ali fotografira, aplikacija prebere odgovore, jih
primerja z rešitvami in predlaga točke po nalogah; učitelj predloge potrdi ali
popravi in dobi tabelo rezultatov. Učenci na testu niso z imenom, ampak s
**šifro**, tako da v aplikacijo nikoli ne pride ime otroka.

## Scope

In: tisk testa s šifro in QR kodo na vsaki strani; zajem (glej možnosti);
   branje odgovorov (Claude z vidom: izbirni tip in kratki odgovori
   zanesljivo, daljši odgovori kot predlog točk z utemeljitvijo); pregled po
   nalogah z gumbi potrdi/popravi; izvoz rezultatov (CSV/xlsx po šifrah);
   kredit na popravljen test; besedilo za splošne pogoje (T-26-018).
Out: digitalno reševanje na napravah učencev; samodejno pošiljanje ocen v
   eAsistent (kasneje, po povpraševanju).

## Acceptance criteria

- [ ] test, izvožen iz aplikacije, ima na vsaki strani šifro učenca in QR kodo (id testa, šifra, stran)
- [ ] 30 skeniranih testov (en PDF s kopirnega stroja) se pravilno razdeli po učencih in straneh; napačno razpoznane strani gredo v »neuvrščene« in se ročno dodelijo
- [ ] pri izbirnih nalogah je ujemanje z učiteljevim popravkom ≥ 95 % na vzorcu 10 testov; pri kratkih odgovorih učitelj vsak predlog vidi in potrdi
- [ ] v bazi, dnevnikih in poslanih zahtevkih Claude API ni imena učenca; preverjeno s testom, ki v skene podtakne ime in ga aplikacija zamaže/zavrne
- [ ] rezultat je tabela šifra → točke po nalogah → skupaj; preslikava šifra → ime ostane pri učitelju (natisnjen seznam ali lokalno, glej spodaj)

## Možnosti izvedbe (Vital izbere, predlog v oklepaju)

**Zajem**
1. **Skeni vseh testov skupaj** na šolskem kopirnem stroju v en PDF, aplikacija
   razdeli po QR kodah. Najmanj dela za učitelja, kopirni stroj ima vsaka
   šola. *(privzeto za začetek)*
2. **Kamera telefona**, fotografija vsakega testa (PWA, odprta kamera,
   samodejna zaznava roba lista in izravnava perspektive, npr. OpenCV.js ali
   `jscanify`). Dobro za hitre kratke preverjanja, slabše pri 30 testih po
   4 strani.
3. **Brez zajema**: učitelj popravi na papir in v aplikacijo samo vpiše točke
   po nalogah na matriko šifra × naloga. Ničelni strošek, dela že s prvim
   dnem, statistika po nalogah pride zraven. Smiselno kot **prva stopnja**
   funkcije in kot rezerva, ko razpoznava odpove.
4. Optični odgovorni list (»bubble sheet«) za izbirne naloge: učenec zapolni
   krogce na posebni strani; branje je deterministično (OpenCV), brez AI.
   Dopolnilo možnosti 1.

**Razpoznava**
- Claude z vidom na sliki strani: dobi sliko, besedilo naloge in rešitev, vrne
  strukturirano (naloga, prebran odgovor, predlog točk, zaupanje). Nizko
  zaupanje → učitelj vidi izrez slike ob predlogu.
- Daljši odgovori: model predlaga točke po rubriki iz rešitve; učitelj vedno
  potrdi. Nikoli samodejna končna ocena.

**Šifre in anonimnost**
- Šifra = kratka koda (npr. `7B-14`), ki jo aplikacija dodeli ob tisku;
  preslikava na ime nastane in ostane **pri učitelju**: natisnjen seznam ob
  tisku testa ali shranjeno samo lokalno v brskalniku (šifrirano z geslom
  učitelja), nikoli na strežniku.
- Splošni pogoji (T-26-018): uporabnik na teste ne piše imen učencev, uporablja
  šifre; aplikacija imena, ki jih vseeno zazna, zamaže pred shranjevanjem in
  jih ne pošilja v AI obdelavo; skeni se izbrišejo po X dneh (privzeto 30) po
  potrditvi rezultatov.
- Za šole to pomeni: v aplikaciji ni osebnih podatkov učencev, pogodba o
  obdelavi ostane preprosta.

## Notes

- Kredit: 1 kredit na popravljen test (vse strani), ker je vid dražji kot
  klasifikacija besedila; strošek izmeri na 10 testih in zapiši v T-26-019.
- Rešitve v izvozu že obstajajo (T-26-003, T-26-008); rubrike za daljše
  odgovore bo treba dopisati k nalogam.

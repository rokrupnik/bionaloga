---
task: T-26-018
title: Pravni okvir: pogoji uporabe, avtorske pravice, GDPR, RIC
status: waiting
assignee: [ROK, VITAL]
requested-by: Rok
week: 26-W38
created: 2026-09-20
completed:
blocked-by: []
visibility: team
---

# Pravni okvir: pogoji uporabe, avtorske pravice, GDPR, RIC

## Goal

Pred prvo plačljivo šolo imamo splošne pogoje, politiko zasebnosti in
pogodbo o obdelavi podatkov, ki jih lahko podpiše javna šola, ter jasen
odgovor, kaj smemo ponuditi sami (RIC-ove maturitetne naloge) in kaj samo
gostimo za uporabnika. Kar je spodaj, je najina delovna ocena, ne pravni
nasvet — dokumente pred objavo pregleda odvetnik (ena ura, znan strošek).

## Scope

In: splošni pogoji (SI), politika zasebnosti, pogodba o obdelavi (DPA) za
   šole, postopek prijave in odstranitve sporne vsebine (notice-and-action),
   dopis RIC-u za dovoljenje, pregled pri odvetniku.
Out: registracija znamke (T-26-016), davčna obravnava naročnin (T-26-019).

## Acceptance criteria

Človeška presoja; »narejeno« pomeni, da dokumenti stojijo v `docs/pravno/` in
jih je pregledal odvetnik.

- [ ] `docs/pravno/pogoji.md`, `zasebnost.md`, `dpa.md` napisani po točkah spodaj
- [ ] v aplikaciji je postopek prijave kršitve (obrazec/e-naslov) in odstranitve v 48 urah
- [ ] RIC-u poslan dopis (Vital), odgovor zabeležen pod `## Result`
- [ ] odvetnik pregledal; pripombe vgrajene
- [ ] odločitev, na katerem paketu (če sploh) so RIC naloge, zapisana v T-26-019

## Kaj vemo o avtorskih pravicah (delovna ocena, 2026-09-20)

**1. Testi, ki jih naložijo učitelji.** Test je avtorsko delo učitelja; ker
nastane pri delu, sme šola kot delodajalec deset let izključno upravljati
pravice (ZASP, delo iz delovnega razmerja). Učitelj, ki naloži svoj test za
*lastno* rabo v orodju, je v praksi brez tveganja; pri **deljenju z drugimi**
šola načeloma lahko ugovarja. Večja past: v šolskih testih so pogosto naloge
in slike, prepisane iz učbenikov in delovnih zvezkov (Rokus Klett, DZS, MK) ali
z interneta. Teh pravic učitelj nima in nam jih ne more dati.

**2. »Roke stran« v pogojih — ali gre skozi?** Delno, in samo ob dejanjih:
- Za vsebino za *lastno rabo uporabnika* smo ponudnik gostovanja. Po ZEPT
  (e-poslovanje) in evropskem aktu o digitalnih storitvah (DSA) ponudnik ne
  odgovarja za vsebino uporabnikov, dokler zanjo ne ve in ob prijavi hitro
  ukrepa. Za to potrebujemo: jasno izjavo uporabnika, da ima pravice; postopek
  prijave in odstranitve; kontaktno točko; dnevnik ukrepov.
- Ko nalogo **označiš kot »na voljo drugim učiteljem«**, jo mi razširjamo
  naprej in zaslužimo s tem. Tu »roke stran« ne zadošča: v pogojih mora
  uporabnik dati **licenco** nam in drugim uporabnikom (neizključna, za
  uporabo v aplikaciji in v izvoženih testih), potrditi, da naloga ni prepis
  iz učbenika, in mi moramo ob prijavi nalogo umakniti iz skupne baze. AI
  klasifikacija lahko pomaga: označi naloge z besedami »iz učbenika«,
  »str. 42«, znanimi slikami.
- Filtriranje vnaprej ni obvezno (DSA ne zahteva splošnega nadzora), a
  učbeniške založbe so v SI aktivne; postopek odstranitve mora res delovati.

**3. RIC-ove maturitetne naloge.** Izpitne pole in navodila za ocenjevanje so
na ric.si prosto dostopne, spletna stran pa nosi »© Državni izpitni center.
Vse pravice pridržane.« brez licence za nadaljnjo uporabo. Izjema za uradna
besedila (ZASP 9. člen: zakoni, uradna besedila zakonodajne, upravne in sodne
narave) za izpitne pole ni zanesljiva — nanjo se ne opiramo. Zato:
- **Ne** ponujava RIC nalog kot lastne baze na plačljivem paketu **brez
  pisnega dovoljenja RIC-a**. Vital pošlje dopis: kdo sva, kaj je storitev,
  da bi naloge prikazovala z navedbo vira (»RIC, matura 2019, jesenski rok«)
  in povezavo na izvorno polo; prosiva za neizključno licenco za izobraževalno
  rabo v plačljivi storitvi. RIC je javni zavod — verjetni izidi: dovoljenje z
  navedbo vira, dovoljenje s plačilom, ali zavrnitev.
- Do odgovora: RIC naloge so na voljo samo kot **uvoz, ki ga naredi uporabnik
  sam za svojo rabo** (enako kot lastni testi), in v aplikaciji ponudiva
  »uvozi maturitetno polo z ric.si« kot vodeni uvoz uporabnikove datoteke.
  Alternativa: naloge kaževa samo kot povezave na RIC-ov PDF s stranjo.
- Obstoječih 5 229 RIC nalog v najini bazi ne izvažava strankam, dokler ni
  dovoljenja.

**4. Osebni podatki.** Testi vsebujejo imena učencev, ocene, včasih rojstne
datume. Šola je upravljavec, mi obdelovalec → pogodba o obdelavi (GDPR 28.
člen), podatki v EU (docs/HOSTING.md), izbris ob koncu naročnine, samodejno
brisanje imen pri razrezu (že imamo redakcijo za `work/`; enako pri uvozu).
Za AI-obdelavo pri Anthropicu: navesti kot podobdelovalca; API-ja ne uporablja
podatkov za učenje; regija obdelave ZDA — šolam povedati. Če bo to ovira,
možnost obdelave v EU regiji (Anthropic ponuja »inference in EU«; preveri
pogoje ob podpisu).

## Notes

- Vzorci pogojev za SaaS v SI: preveri, kaj uporabljajo Znam za več, Astra,
  eAsistent (kako naslavljajo vsebino uporabnikov).
- Odvetnik: ena ura pregleda; vprašanja s seznama zgoraj.

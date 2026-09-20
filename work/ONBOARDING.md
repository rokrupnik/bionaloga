# Onboarding

What the bot posts to a person on arrival (`on_member_join`) and on
`!navodila`. Sections are picked by role: `Vsi` for everyone, then `Ekipa`,
then `Admin` for team members in the admin group. Placeholders used here:
`{name}`, `{qa}`, `{board}`, `{status}`. Gendered forms are written as
`{masculine|feminine}` and resolved from `gender:` in policy.yml (unmarked
reads as masculine). The bot reads this file at the moment it posts, so it
can be edited freely.

This instance has no intake channel (`channels.names.intake: ""`), so nothing
here may point at one: a task starts as a post on the forum, or as a proposal
out of the questions channel.

## Vsi

Živjo {name}, jaz sem Moss. Skrbim za BioNaloga — program za sestavljanje
testov iz biologije — in dosežeš me samo tukaj.

**Kje pišeš.** Dvoje in nič tretjega:

- **Nalogo** odpreš kot **novo objavo** (New Post) v {board}. Naslov, besedilo,
  priloge in povezave daš v objavo, in ta je od tega trenutka nit naloge: tam
  se pogovarjava naprej. Naslova si ni treba izmišljati — če napišeš le nekaj
  kratkega, ga določim sam.
- **Vprašanje** napišeš v {qa}: tam odgovarjam iz repozitorija, baze nalog in
  dokumentacije in ničesar ne spremenim. Če iz odgovora pade kaj, kar je v
  resnici naloga, ti jo predlagam — napišeš **da** in jo odprem, ali pa
  popravke in predlog ponovim.

Vse o eni stvari napiši v **eno** objavo ali sporočilo: vsako vzamem v obdelavo
takoj in ne čakam na nadaljevanje.

**Kaj se zgodi z nalogo.** Najprej jo preverim in pripravim načrt. Če mi kaj
manjka, vprašam v niti in nalogo označim `needs-info`; takrat čakam nate. Ko je
narejeno, ti v niti napišem, kaj se je spremenilo in kaj naj preveriš. Naloge
tečejo ena za drugo, nikoli dve hkrati.

**Kaj gledati na forumu.** Zgoraj klikni ikono za filtriranje po oznakah in
izberi `needs-info`, `waits-info` in `notify`: to so edine oznake, pri katerih
je poteza tvoja. Vse ostalo je v delu ali čaka name. Filter je tvoj, Discord ga
ne nastavi vnaprej.

**Obvestila.** V nit naloge te dodam, kadar te zadeva. {status} je moj dnevnik
in ga lahko mirno utišaš — kar potrebujem od tebe, vedno pride z omembo.

**Kje me moraš omeniti.** V {qa} in v nitih nalog se odzovem na vsako sporočilo;
omemba ni potrebna. V drugih kanalih sporočil ne berem: tam me omeni
(`@Moss navodila`). Ukazi delujejo v obeh oblikah, `!close` ali `@Moss close`.

**Česa ne delam.** Nalog in slik iz baze ne brišem in ničesar ne spreminjam
nepovratno brez izrecnega naročila v niti; pred vsakim pisanjem v bazo naredim
varnostno kopijo. E-pošte ne pošiljam, pripravim samo osnutek. Spomina izven
naloge in njene niti nimam.

## Ekipa

Naloge so v {board}, oznaka na objavi je stanje. Nalogo, ki si jo naročil{|a}
ti, zaključiš z `!close` v njeni niti. Nalogo, ki naj počaka, odložiš z
`!odlozi T-26-NNN 26-W40` ali `!odlozi T-26-NNN 2026-10-15 [razlog]`; ko pride
čas, jo sam vrnem v vrsto.

**Kill switch.** `!stop` ustavi vse, kar se še ni začelo; `!go` spet spusti.

## Admin

`!assign T-26-NNN VITAL` dodeli nalogo, `!close` zapre katerokoli,
`!link Ime handle` poveže človeka z Discord računom, `!doctor` izpiše, kaj od
dostopov manjka, `!dnevnik` pokaže današnji dnevnik, `!cost` porabo.
Pravila, po katerih se odločam, so v `work/POLICY.md` v repozitoriju; ureja
jih Rok.

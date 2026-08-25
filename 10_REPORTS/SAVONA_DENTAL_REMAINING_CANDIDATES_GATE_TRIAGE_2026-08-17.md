---
type: pilot-triage-report
market: Savona
category: dentale
gate: RRT_DENTAL_SAVONA_DISCOVERY_TO_FIRST_VISIT_GATE_V1
status: completed
updated: 2026-08-17
---

# Savona Dental Pilot — Remaining Candidates Gate Triage

## Scope

Applicazione del gate [[03_RULES/RRT_DENTAL_SAVONA_DISCOVERY_TO_FIRST_VISIT_GATE_V1]] ai candidati dentali Savona rimasti dopo la chiusura del primo Signal confermato:

- [[04_PROSPECTS/SAV-DENT-01 - Studio Odontoiatrico Zecca-Cohen]]

Zecca-Cohen non viene riaperto; viene usato solo come caso di riferimento metodologico.

## Product North Star

Questo triage non deve generare una lista lunga di pseudo-finding.

Obiettivo: promuovere solo nuovi Opportunity Signal che sopravvivono davvero a:

- entity resolution;
- evidenza pubblica diretta;
- confronto locale;
- Red Team;
- formulazione senza overclaim clinici/economici.

## Executive outcome

**Nessun nuovo Opportunity Signal viene certificato in questa passata.**

Esito corretto:

- 0 nuovi `OPPORTUNITY_SIGNAL`;
- 0 nuovi mini-audit cliente;
- 3 casi tenuti come `WATCHLIST` o `BENCHMARK/REFERENCE`;
- resto `NO_SIGNAL`, `DEFERRED`, `ENTITY_UNRESOLVED` o `OUT_OF_SCOPE`.

Questo e un buon risultato di prodotto: il gate ha evitato di trasformare normali differenze di sito/contatto in Signal deboli.

## Triage matrix

| Candidate | Entity | Public site / path evidence | Gate result | Reason |
|---|---|---|---|---|
| Studio Mantovani | RESOLVED | Sito con promessa chiara, CTA `Chiedici informazioni` e CTA finale `INIZIA DA QUI`; gia usato come comparator. | BENCHMARK_REFERENCE | Non promuovere a Signal: percorso di prima azione forte, utile come benchmark per altri. |
| Studio Vesalici | RESOLVED | Sito ufficiale con orari, servizi, telefono, cellulare, email, indirizzo e blocco `Contattaci per ricevere informazioni`. | WATCHLIST_WEAK | Potenziale attrito se il profilo Google non linkasse il sito o se mancasse form visibile, ma dal sito emergono contatti forti. Non basta per Signal senza Google profile evidence e mobile-path screenshot. |
| Studio Soana Martinengo | RESOLVED | Sito con telefono, WhatsApp, CTA `Fissa un appuntamento`, `Fissa una visita`, `Contattaci per un consulto`, contenuto prima visita e form richiesta prenotazione. | NO_SIGNAL | Percorso first-visit gia esplicito; finding discovery-to-first-visit non sopravvive. |
| Studio Faucci | RESOLVED | Sito con indirizzo, telefono, email, orari e form contatto. | NO_SIGNAL | Gia noto come non prioritario; clear contact path e specialist positioning. |
| Studio Bianco | ENTITY_UNRESOLVED | `studio-bianco.it` risulta under construction; altra fonte `studiobiancosc.it/odontoiatria` non basta a risolvere con sicurezza il candidato Savona. | DEFERRED_ENTITY | Non promuovere: rischio di analizzare entita sbagliata. Serve risoluzione entita prima del gate. |
| Studio Roberto Cristiano Martinengo | RESOLVED_AS_BENCHMARK | Profilo online booking con 187 recensioni pubbliche e action di booking/messaggio gia usate come comparator. | BENCHMARK_REFERENCE | Non riaprire come prospect in questa fase: e un percorso benchmark forte, non un Signal target. |
| Studio Bellini | RESOLVED | Sito ufficiale con telefono, indirizzo, orari e form `Scrivici ora`; pagina indica intervento di digitalizzazione. | NO_SIGNAL | Percorso first-contact sufficientemente guidato. Eventuali altri gap non sono questo gate. |
| Studio San Giovanni | ENTITY_CONFLICT_OR_OUT_OF_SCOPE | Ricerche pubbliche restituiscono risultati non coerenti con Savona dentale indipendente: Chioggia, Loano, convenzioni CNA e fonti ambulatoriali non allineate. | DEFERRED_ENTITY / OUT_OF_SCOPE | Non analizzare finche l'entita Savona dental corretta non e risolta. |
| Studio Blasi | RESOLVED | Sito con `Richiedi un appuntamento`, WhatsApp, telefono, email, indirizzo, team, servizi e FAQ. | NO_SIGNAL | First-visit path gia esplicito; non sopravvive come continuity gap. |
| Studio Orengo | RESOLVED_WITH_ADDRESS_VARIANCE | Sito con contatti, telefoni, email, dati societari e pagine `Dove siamo`; fonte agency descrive micro-CTA call/WhatsApp e sito mobile-first. | NO_SIGNAL / MONITOR_ADDRESS_VARIANCE | Percorso contatto sufficiente; annotare varianza indirizzi/sedi ma non Signal sul gate. |
| Studio Garbasso | RESOLVED | Sito con specializzazione ortodonzia, telefono, email, indirizzo e form con nome/email/telefono; directory conferma sito e telefono. | NO_SIGNAL | First-contact path presente; non promuovere. |

## Strongest cases reviewed

### 1. Studio Vesalici — WATCHLIST_WEAK

Why it was considered:

- sito reale e coerente;
- molte informazioni utili per paziente;
- telefono fisso, cellulare, email e indirizzo;
- blocco `Contattaci per ricevere informazioni`;
- offre tecnologie, costi competitivi, prevenzione, implantologia, filler, ortodonzia e altri servizi.

Why it does not clear the gate:

- il sito espone gia contatti forti;
- manca evidenza diretta del profilo Google e della presenza/assenza del link ufficiale;
- senza screenshot mobile e Google profile state si rischia di inferire assenza da evidence incompleta;
- non c'e ancora comparatore che dimostri un gap decisionale abbastanza specifico.

Verdict: **WATCHLIST, non Signal.**

### 2. Studio Bianco — DEFERRED_ENTITY

Why it was considered:

- `studio-bianco.it` appare under construction, elemento potenzialmente rilevante per discovery-to-first-visit;
- altro risultato pubblico parla di odontoiatria su `studiobiancosc.it`.

Why it does not clear the gate:

- entity resolution non solida;
- rischio alto di confondere entita, sede o specializzazione;
- nessun Signal puo nascere da un'entita non risolta.

Verdict: **DEFERRED_ENTITY.**

### 3. Studio Orengo — NO_SIGNAL / MONITOR_ADDRESS_VARIANCE

Why it was considered:

- sito con piu indirizzi/sedi e dati societari;
- possibile varianza tra `Corso Ricci`, `Corso Italia` e riferimenti del Dott. Orengo.

Why it does not clear the gate:

- il sito espone telefoni, email e pagine `Dove siamo`;
- una fonte pubblica dell'agenzia web descrive micro-CTA call/WhatsApp e mobile-first;
- la varianza indirizzi e da monitorare come entity hygiene, non come discovery-to-first-visit Signal.

Verdict: **NO_SIGNAL sul gate; monitor entity hygiene.**

## Red Team summary

Finding generic rejected:

> Alcuni studi potrebbero avere siti meno moderni o meno performanti.

Rejected because:

- e SEO/digital hygiene generica;
- non prova un gap decisionale;
- non dimostra che il paziente non possa chiedere una visita;
- non rispetta la North Star.

Finding only allowed if evidence shows:

> Il paziente che parte da Google non trova continuita verso sito ufficiale e richiesta prima visita, mentre un comparator locale rende quel passaggio piu chiaro.

In questa passata, nessun nuovo candidato oltre Zecca-Cohen soddisfa tutti i requisiti.

## Source notes

Public sources checked, non-exhaustive:

- Studio Mantovani: https://www.mantovanisavona.com/
- Studio Vesalici: https://www.studiovesalici.it/
- Studio Soana Martinengo: https://www.dentistamartinengosoana.it/
- Studio Soana Martinengo pedodonzia/ortodonzia: https://www.dentistamartinengosoana.it/pedodonzia-e-ortodonzia/
- Studio Faucci: https://www.studiofaucci.it/dove-siamo-e-contatti/
- Studio Bianco: https://www.studio-bianco.it/
- Studio Bianco / odontoiatria source: https://www.studiobiancosc.it/odontoiatria
- Studio Bellini: https://www.studiodentisticobellinisv.it/contatti/
- Studio Blasi: https://www.studiodentisticoblasi.it/
- Studio Orengo: https://orengodentista.it/
- Studio Orengo dove siamo: https://orengodentista.it/dovesiamo.html
- Studio Garbasso: https://www.studiodentisticogarbasso.it/

## Decision

No new full Signal artifact set is created in this phase.

The correct operational output is:

- documented deferral/no-signal outcome;
- refined checklist rule against website-only false positives;
- preserve Zecca-Cohen as the only certified Signal for now.

## Next recommended phase

For any candidate to be promoted next, collect:

1. fresh Google profile screenshot/state;
2. mobile official-site path screenshot;
3. explicit yes/no on site link from Google profile;
4. explicit yes/no on first-visit CTA/form/booking/WhatsApp;
5. comparator screenshot;
6. Red Team review before any client-facing report.


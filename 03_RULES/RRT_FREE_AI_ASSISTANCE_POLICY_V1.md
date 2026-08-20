---
type: rule
status: active
version: v1
created: 2026-08-12
---

# RRT Free AI Assistance Policy V1

## Intento

AI gratuite esterne possono essere usate solo quando aumentano velocita, controllo incrociato o qualita operativa senza generare costi, senza violare termini d'uso e senza sostituire fonti primarie.

## Stato default

- `FREE_AI_ASSISTANCE_OPTIONAL`
- `AGENT_TEAM_LOCKED`
- costo consentito: `EUR 0.0000`
- nessun dato sensibile, privato o non pubblico deve essere inviato a strumenti esterni gratuiti;
- nessun output AI gratuito e considerato fonte primaria.

## Usi ammessi

1. Brainstorming categorie e nicchie.
2. Generazione di query pubbliche da verificare.
3. Normalizzazione non sensibile di liste gia pubbliche.
4. Secondo parere su layout dashboard, report, checklist e runbook.
5. Controllo incrociato di testi metodologici.

## Usi vietati

1. Inventare aziende, recensioni, rating, contatti o bilanci.
2. Dichiarare Opportunity Signal.
3. Sostituire Google, Registro Imprese, siti ufficiali, portali review o documenti pubblici.
4. Processare dati personali non gia pubblici o dati riservati dell'utente.
5. Aggirare login, paywall, CAPTCHA, rate limit o termini d'uso.
6. Attivare agent team A1-A9 o operazioni a pagamento.

## Regola di provenance

Ogni contributo AI gratuito deve essere marcato come:
- `source_type = FREE_AI_ASSISTANCE`
- `cost_eur = EUR 0.0000`
- `evidence_role = NON_AUTHORITATIVE`
- `requires_human_or_primary_source_verification = YES`

Non puo essere promosso a evidenza finche non e confermato da fonte primaria o manual review.

## Decisione operativa

Usare AI gratuite solo se riduce tempi senza aumentare rischio. Se il lavoro e deterministico, locale o verificabile con script, preferire codice e fonti primarie.

## Interazione con A1-A9

Questa policy non sblocca gli agent team. A1-A9 restano bloccati finche l'utente non autorizza esplicitamente run e budget EUR.

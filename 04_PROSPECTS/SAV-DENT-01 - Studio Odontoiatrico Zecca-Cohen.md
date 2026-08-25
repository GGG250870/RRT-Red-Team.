---
type: prospect
id: SAV-DENT-01
company: Studio Odontoiatrico Zecca-Cohen
city: Savona
official_domain: cohenorthodontic.wixsite.com
entity_status: RESOLVED_PUBLIC_PROFILE_AND_OFFICIAL_SITE
saturation_state: SATURATED_FOR_SIGNAL_SCOPE
target_match_state: PASS_DISCOVERY_TO_FIRST_VISIT_CONTINUITY
benchmark_state: PASS_LOCAL_COMPARATORS
red_team_state: SURVIVES
signal_state: OPPORTUNITY_SIGNAL
qa_state: PASS_CONSERVATIVE_SCOPE
human_review: approved_by_user
updated: 2026-08-17
---

# SAV-DENT-01 — Studio Odontoiatrico Zecca-Cohen

## Stato sintetico

**OPPORTUNITY_SIGNAL confermato sul gate "Google profile -> sito ufficiale -> prima visita".**

Il finding non riguarda qualita clinica, seniority professionale o adeguatezza terapeutica. Riguarda esclusivamente la continuita esterna di scoperta e conversione per un potenziale paziente che parte dal profilo Google pubblico.

## Identita e scope

- Nome pubblico: Studio Odontoiatrico Zecca Cohen.
- Indirizzo pubblico Google: Via Bartolomeo Guidobono 18/Int 1, Savona.
- Sito ufficiale osservato: `https://cohenorthodontic.wixsite.com/odontoiatriasavona`.
- Categoria RRT: `dentale`.
- Target specifico: continuita del percorso prima visita / prenotazione dopo scoperta locale.

## Evidence

- [[05_EVIDENCE/SAV-DENT-01 - Zecca-Cohen Evidence Pack]]

Evidence rilevante:
- sito ufficiale mobile con numeri telefonici e due email per prenotazione;
- nessun form richiesta visita o booking online visibile nel percorso osservato;
- profilo Google con rating pubblico 4.6/5 da 14 recensioni, telefono, indirizzo e Instagram;
- profilo Google mostra `Aggiungi sito web`, quindi il sito ufficiale non risulta collegato al profilo pubblico;
- sito ufficiale con branding Wix visibile e footer `©2014`.

## Target match

- D1 Discoverability locale: PASS, profilo Google pubblico presente.
- D2 Continuita profilo -> sito: GAP, sito ufficiale non linkato dal profilo Google osservato.
- D3 Continuita sito -> prima visita: GAP, call/email presenti ma nessun flusso guidato osservato.
- D4 Fiducia pubblica: PASS, rating pubblico positivo ma volume limitato.
- D5 Competitor path comparabile: PASS, competitor locali hanno CTA o booking/message action piu guidati.

## Benchmark

Comparatori usati solo per percorso decisionale esterno, non per superiorita clinica:

1. Studio Mantovani
   - comparatore locale;
   - CTA Typeform prominente `Inizia da qui`;
   - rende piu guidata l'azione iniziale del paziente.

2. Dr. Roberto Cristiano Martinengo
   - profilo con 187 recensioni pubbliche;
   - online booking/message action presenti;
   - rende piu immediata la richiesta di appuntamento/contatto.

## Red Team

Falsificazione principale considerata:

> Un workflow phone-first potrebbe essere intenzionale e coerente con uno studio specialistico/referral-led.

Esito:

**SURVIVES.**

Il finding sopravvive perche:
- il sito ufficiale non e collegato nel profilo Google osservato;
- dal mobile site emergono call/email, ma non un percorso guidato di lead capture o booking;
- comparator locali mostrano percorsi di prima azione piu chiari;
- il finding non richiede di affermare che lo studio perda pazienti o che la qualita clinica sia inferiore.

## Commercial Gate / Signal

Signal sicuro:

> Lo studio possiede segnali professionali e reputazionali pubblici gia buoni, ma nel percorso esterno osservato un potenziale paziente che parte da Google non trova continuita immediata verso sito ufficiale e richiesta guidata di prima visita. Comparatori locali rendono invece piu chiara la prima azione. Esiste quindi un'opportunita verificabile di ridurre attrito nel passaggio scoperta -> primo contatto, senza implicare alcuna carenza clinica.

Confidenza calibrata: **98% sul fatto osservabile e sul gap di continuita; non su conversioni o impatto economico.**

## QA / Validation

Claim vietati:
- lo studio perde pazienti;
- lo studio converte meno;
- il sito vecchio causa perdita economica;
- i competitor sono clinicamente superiori;
- rating Google dimostra qualita clinica.

Claim consentiti:
- continuita Google profile -> sito ufficiale non completa nel profilo osservato;
- sito mobile offre call/email ma non percorso guidato di booking/request form osservato;
- comparator locali offrono CTA o booking/message action piu esplicite;
- opportunita pratica di migliorare il percorso di primo contatto.

## Human review

Finding approvato dall'utente come primo Opportunity Signal confermato del pilot dentale Savona.

## Decisione / prossimo passo

Usare il mini-audit cliente e lo script di primo contatto:

- [[10_REPORTS/SAV-DENT-01 - Zecca-Cohen Client Mini-Audit]]
- [[10_REPORTS/SAV-DENT-01 - Zecca-Cohen First Contact Script]]

Applicare la checklist agli altri candidati Savona:

- [[03_RULES/RRT_DENTAL_SAVONA_DISCOVERY_TO_FIRST_VISIT_GATE_V1]]

## Lezioni di sistema

Il finding forte non e "sito vecchio".

Il finding forte e la frizione specifica nel percorso decisionale esterno: Google profile senza sito collegato + sito mobile senza lead capture guidata, mentre competitor comparabili mostrano CTA/booking piu chiari.

## Collegamenti

- [[00_HOME/SECOND_BRAIN]]
- [[04_PROSPECTS/Prospects Index]]
- [[05_EVIDENCE/SAV-DENT-01 - Zecca-Cohen Evidence Pack]]
- [[07_SIGNALS/SAV-DENT-01 - Zecca-Cohen Opportunity Signal Dossier]]
- [[08_RED_TEAM/SAV-DENT-01 - Zecca-Cohen Red Team Review]]

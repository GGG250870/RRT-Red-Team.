---
type: product-spec
status: active
version: v1
created: 2026-08-12
---

# RRT Final Dashboard Product Spec V1

Research companion: [[01_ARCHITECTURE/RRT_DASHBOARD_ONLINE_RESEARCH_NOTES_V1]]
Delivery roadmap: [[01_ARCHITECTURE/RRT_DASHBOARD_DELIVERY_ROADMAP_V1]]
Product North Star: [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]]

## Intento

La dashboard finale deve essere il centro operativo per identificare opportunita commerciali per categoria, citta e singolo imprenditore, mantenendo il principio cheap-first e impedendo l'uso degli agent team finche l'utente non lo autorizza esplicitamente.

La dashboard non e il prodotto vendibile finale. E la superficie di controllo che porta da mercato/lista prospect a pochi Opportunity Signal forti, falsificati e auditabili.

Una lista prospect, un PDF consulente o un report rapido sono output intermedi. Il prodotto finale RRT e il Signal che sopravvive a entity resolution, benchmark comparabile, Red Team, commercial gate e human review.

## Regola aurea

Eseguire sempre prima tutto cio che e gratuito, legalmente accessibile e realisticamente utile, massimizzandone il potenziale prima di proporre operazioni a costo.

Regole operative:
- non inventare mai dati, fonti, recensioni, bilanci, metriche o conclusioni;
- non attendere run lunghi se un triage gratuito puo gia restringere il campo;
- non usare agent team, API a pagamento o fonti documentali a pagamento senza consenso esplicito;
- accedere online alle informazioni gratuite e legalmente estraibili quando aumentano copertura e precisione;
- mostrare cosa e stato controllato, cosa manca e quale sarebbe il costo/beneficio del passo successivo;
- preferire output immediatamente utilizzabili anche se parziali, marcando gli stati `UNRESOLVED` e `COLLECTION_RESTRICTED`.

## Regola di consenso agent team

Gli agent team A1-A9 non devono essere usati automaticamente da dashboard, CLI, batch o scorciatoie operative.

Stato default:
- `AGENT_TEAM_LOCKED`
- nessuna chiamata live A1-A9;
- nessun report avanzato agentico;
- nessun costo LLM generato dagli agenti.

Sblocco richiesto:
- consenso esplicito dell'utente per il caso o batch selezionato;
- stima costo in EUR mostrata prima dell'avvio;
- budget massimo per operazione confermato;
- audit log con `user_approval_ref`, timestamp, case/batch e costo stimato.

Guard tecnico runtime:
- ogni run live richiede `RRT_AGENT_TEAM_APPROVAL=I_APPROVE_AGENT_TEAM_LIVE_RUN`;
- in assenza della variabile il runtime deve restituire `AGENT_TEAM_REQUIRES_EXPLICIT_USER_APPROVAL`.

## Selezioni principali dashboard

La dashboard deve permettere di scegliere:

1. Categoria
   - `dentale`
   - `ristorazione`
   - `pmi`
   - `hospitality`
   - `benessere_estetica`
   - `servizi_casa`
   - `formazione`
   - `generic`

2. Citta o area
   - citta singola;
   - lista citta;
   - regione o provincia solo se esiste una sorgente validata;
   - nessun allargamento geografico silenzioso.

3. Modalita identificazione opportunita
   - `manual_csv`: input ufficiale a basso rischio;
   - `validated_primary_discovery`: solo sorgenti gia validate;
   - `review_only_context`: portali usati come contesto, mai come dominio ufficiale;
   - `primary_intelligence_review`: Google, recensioni, social e bilanci pubblici come sorgenti primarie di segnali;
   - `agent_team_deep_run`: bloccato finche non autorizzato.

4. Output
   - lista prospect;
   - shortlist;
   - report batch;
   - report singolo imprenditore;
   - export machine-readable.

Ogni output deve dichiarare chiaramente se e:
- `PROSPECT_LIST`: utile per primo contatto, non Signal;
- `RAPID_CONTEXT`: contesto operativo, non Signal;
- `OPPORTUNITY_HYPOTHESIS`: ipotesi da falsificare;
- `OPPORTUNITY_SIGNAL_CANDIDATE`: finding sopravvissuto ai gate automatici ma non ancora validato;
- `OPPORTUNITY_SIGNAL`: finding falsificato, auditabile e human-reviewed.

Ogni lista e report per imprenditore deve includere sempre un blocco contatti con:
- telefono;
- cellulare/WhatsApp quando disponibile o distinguibile;
- email;
- indirizzo.

Se il dato non e disponibile da input o fonti pubbliche gratuite, deve restare vuoto o `NON_TROVATO`. Non e ammesso completarlo per inferenza.

## Cosa e piu opportuno per identificare opportunita

La dashboard deve raccomandare il percorso in base a categoria, qualita fonti e costo atteso.

Ordine consigliato:

1. `manual_csv` con domini ufficiali
   - piu affidabile per categorie non ancora validate;
   - costo LLM zero;
   - riduce contaminazione da portali.

2. `validated_primary_discovery`
   - solo quando il parser di categoria e il resolver dominio ufficiale hanno test di regressione;
   - al momento validato solo per `dentale` con MioDottore.

3. `primary_intelligence_review`
   - Google Business Profile, Google Reviews e Google Maps;
   - portali recensioni verticali e generalisti;
   - social ufficiali e profili pubblici;
   - bilanci pubblici e informazioni societarie disponibili da Registro Imprese, Telemaco/InfoCamere o documenti ufficiali pubblicati dall'azienda;
   - fonti usate per reputazione, presenza locale, affidabilita e solidita, non per sostituire il dominio ufficiale.

4. `zero_llm_prescreen`
   - filtra per segnali pubblici e gap operativi;
   - produce `REJECT`, `COLLECTION_RESTRICTED`, `SHORTLIST`, `ESCALATE`;
   - non produce Opportunity Signal.

   Lo scopo del pre-screen e ridurre costo e rumore, non sostituire il Red Team commerciale.

5. `human_selection`
   - l'utente seleziona imprenditori o aziende su cui vale la pena spendere.

6. `agent_team_deep_run`
   - solo dopo consenso esplicito;
   - costo in EUR stimato prima e consuntivato dopo;
   - produce solo stati coerenti con A1-A9, QA e Human Review.

## SLA operativa attesa

La dashboard deve privilegiare tempi brevi. Una singola analisi non deve richiedere giorni salvo fonti esterne indisponibili, acquisto bilanci, credenziali mancanti o richiesta esplicita di dossier completo.

Target per batch gia dotati di domini ufficiali:

- `single_zero_llm_triage`: 30-90 secondi per imprenditore.
- `single_rapid_report`: 2-5 minuti per imprenditore.
- `city_category_batch_50`: 5-15 minuti per pre-screen zero-LLM, dipendente da rete e siti lenti.
- `city_category_batch_200`: 15-45 minuti per pre-screen zero-LLM, con output progressivo.
- `shortlist_export`: meno di 2 minuti dopo completamento batch.
- `source_coverage_matrix`: 2-10 minuti per batch piccolo se usa solo fonti gratuite/pubbliche gia accessibili.
- `guided_opportunity_report`: 5-15 minuti per imprenditore se non usa A1-A9.
- `full_rrt_a1_a9_report`: 10-30 minuti per imprenditore dopo consenso e budget, salvo blocchi fonte.

Target per costruzione prodotto:

- dashboard V1 locale/manuale: 1-2 giorni di sviluppo.
- export XLSX/DOCX/PDF: 0.5-1 giorno aggiuntivo.
- integrazione API Google/Registro Imprese con costo e credenziali: 1-3 giorni per connettore, dopo accessi disponibili.

Output progressivo:
- dopo 60 secondi mostrare almeno stato parziale e fonti gia coperte;
- dopo 5 minuti mostrare batch parziale utilizzabile;
- ogni blocco deve indicare motivo, fonte e prossimo passo gratuito possibile.

## Fonti primarie dashboard

Ogni categoria deve poter usare queste famiglie di fonti:

- `official_website`: fonte primaria per identita, offerta, contatti e claim propri.
- `google_business_profile`: fonte primaria per presenza locale, recensioni, rating, orari e indirizzo.
- `review_portals`: fonte primaria per reputazione pubblica e segnali di fiducia, con portali diversi per categoria.
- `social_profiles`: fonte primaria per attivita, prova sociale, community e aggiornamenti.
- `public_financials`: fonte primaria per solidita societaria quando legalmente/pubblicamente disponibile.

Per l'Italia, `public_financials` include:
- Registro Imprese / Camera di Commercio;
- Telemaco / InfoCamere;
- bilanci o documenti societari pubblicati sul sito ufficiale;
- altre fonti pubbliche o autorizzate solo se tracciate con provenance.

Google, portali, social e bilanci pubblici possono alzare la priorita di analisi, ma non bastano da soli a certificare un Opportunity Signal.

## Target segment per ristorazione

La categoria `ristorazione` non deve essere trattata come un unico mercato. La dashboard deve permettere segmentazione target e ranking separato.

Segmenti V1:
- `ristorazione_generic`;
- `fine_dining`;
- `pizzeria`;
- `trattoria_osteria`;
- `sushi_etnico`;
- `delivery_asporto`;
- `eventi_catering`;
- `enoteca_wine_bar`;
- `bar_cafe`.

Fonti review prioritarie:
- TripAdvisor e Google per tutti i segmenti;
- TheFork per prenotazione, ristoranti, fine dining e discovery consumer;
- RestaurantGuru per copertura generalista/local;
- Michelin e Gambero Rosso per `fine_dining` ed enogastronomia;
- PagineGialle come fonte generalista locale.

I portali recensioni sono usati come intelligence e provenance. Non devono sostituire sito ufficiale, ragione sociale o bilanci pubblici.

## Enrichment online gratuito/legal-safe

La dashboard deve poter accedere online alle informazioni pubbliche, gratuite e legalmente estraibili.

Fonti ammesse in V1:
- sito ufficiale e pagine interne pubbliche;
- link social pubblici esposti dal sito ufficiale;
- link a portali recensioni esposti dal sito ufficiale o gia forniti nel CSV;
- documenti di bilancio o trasparenza pubblicati sul sito ufficiale;
- URL di ricerca manuale per Google/Maps e Registro Imprese.

Limiti:
- non aggirare login, paywall, CAPTCHA, blocchi tecnici o termini evidenti;
- non usare scraping Google come sostituto di API ufficiali;
- non inventare rating, recensioni, P.IVA, ricavi o bilanci;
- se una fonte non e estraibile gratis, segnare `COLLECTION_RESTRICTED`, `NOT_CHECKED`, `API_REQUIRED` o `PAID_SOURCE_REQUIRED`;
- ogni dato estratto deve salvare URL, stato fetch e timestamp/provenance.

## Moduli funzionali richiesti

La dashboard V1 deve essere progettata attorno a questi moduli:

1. `Opportunity Cockpit`
   - filtri per categoria, citta, stato, score, rating, recensioni, social, bilanci, costo prossimo step.

2. `Source Coverage Matrix`
   - copertura fonti per sito ufficiale, Google, recensioni, social, bilanci e documenti ufficiali.

3. `Explainable Opportunity Score`
   - scomposizione in category fit, commercial gap, reputation, social, financial capacity, contactability, data quality e costo validazione.

4. `Map & City View`
   - cluster geografici, densita opportunita, categorie, stati e copertura fonti per area.

5. `Entity Resolution Workbench`
   - ragione sociale, P.IVA/codice fiscale, dominio, Google place ID, indirizzo, social, bilancio, conflitti.

6. `Review Intelligence`
   - rating, volume, frequenza recensioni recenti, temi, attriti, segnali positivi e risposte pubbliche quando accessibili.

7. `Public Financial Snapshot`
   - ultimo bilancio/visura disponibile, ricavi, utile/perdita, patrimonio netto, addetti/size band, eventi critici, costo fonte e freshness.

8. `Report Builder`
   - lista, shortlist, batch report, report imprenditore rapido, report opportunita guidato, dossier RRT completo.

9. `Cost & Consent Panel`
   - costo stimato/consuntivo in EUR, budget massimo, costo cumulativo e blocco agent team.

10. `Calibration & Outcome Loop`
    - contatti, risposte, appuntamenti, clienti, falsi positivi/negativi e costo per opportunita reale.

## Export richiesti

La dashboard deve produrre formati utilizzabili ed editabili:

- `.csv`: liste prospect, shortlist, batch results;
- `.xlsx`: liste editabili per lavoro commerciale;
- `.json`: output standardizzato per automazioni e audit;
- `.md`: report Obsidian/GitHub human-readable;
- `.docx`: report editabile cliente o interno;
- `.pdf`: report standardizzato non editabile per invio finale.

V1 locale:
- `.xlsx` e `.docx` devono essere generati localmente senza costi o dipendenze esterne;
- `.pdf` puo essere prodotto da `print_report.html` tramite stampa browser finche non e disponibile un renderer gratuito affidabile e verificato.

Ogni export deve includere:
- categoria;
- citta/area;
- telefono;
- cellulare/WhatsApp quando disponibile;
- email;
- indirizzo;
- sorgente;
- Google/review/social/public financial source refs quando disponibili;
- dominio ufficiale;
- stato acquisizione;
- score preliminare quando applicabile;
- decisione;
- costo EUR dell'operazione che lo ha prodotto;
- timestamp;
- avvertenza metodologica.

## Tre report per singolo imprenditore

Dopo selezione di un singolo imprenditore, la dashboard deve offrire tre passaggi crescenti.

### 1. Passaggio 1 - Report rapido zero-LLM

Scopo: lettura operativa economica.

Contenuto:
- profilo categoria;
- telefono, cellulare/WhatsApp, email e indirizzo;
- sito live/non live;
- dimensioni D1-D5;
- gap osservabili;
- presenza social/review;
- decisione pre-screen;
- costo EUR: normalmente `0.0000` salvo costi di strumenti esterni.

Non usa agent team.

### 2. Passaggio 2 - Report opportunita guidato

Scopo: analisi piu ricca ma ancora controllata.

Contenuto:
- telefono, cellulare/WhatsApp, email e indirizzo;
- sintesi sito ufficiale;
- ipotesi di gap;
- domande commerciali da verificare;
- materiali pronti per revisione umana;
- costo EUR stimato prima di ogni operazione.

Puo usare strumenti non-agentici solo se approvati e conteggiati. Non produce Opportunity Signal certificato.

### 3. Passaggio 3 - Report RRT completo A1-A9

Scopo: dossier ad alta affidabilita.

Contenuto:
- telefono, cellulare/WhatsApp, email e indirizzo;
- evidence atomica;
- target-specific deep scan;
- saturation;
- benchmark;
- red team;
- commercial gate;
- QA;
- stato finale.

Richiede consenso esplicito dell'utente, budget EUR massimo e conferma prima dell'avvio. Senza consenso resta `AGENT_TEAM_LOCKED`.

## Contatore costi in EUR

La dashboard deve mostrare sempre:

- costo stimato prima dell'operazione;
- costo consuntivo dopo l'operazione;
- costo cumulativo sessione;
- costo cumulativo batch;
- costo per prospect;
- costo per imprenditore selezionato;
- costo per report;
- costo per agent/stage quando A1-A9 e autorizzato.

Regole:
- valuta UI: EUR;
- i prezzi modello possono restare registrati in USD se la fonte primaria e in USD;
- conversione deterministica tramite `RRT_USD_EUR_RATE`;
- ogni record deve salvare anche il cambio usato;
- se il cambio non e aggiornato, mostrare `FX_RATE_STALE` e bloccare report economici finali.

## Stati UI minimi

- `READY_ZERO_COST`: operazione zero-LLM disponibile.
- `NEEDS_OFFICIAL_DOMAIN`: manca dominio ufficiale.
- `DISCOVERY_EMPTY`: nessuna fonte validata ha restituito prospect.
- `COLLECTION_RESTRICTED`: sito non acquisibile o accesso limitato.
- `SHORTLIST`: puo essere valutato manualmente.
- `ESCALATE`: candidato per possibile run avanzato.
- `AGENT_TEAM_LOCKED`: agent team non autorizzato.
- `COST_APPROVAL_REQUIRED`: serve conferma budget.
- `RUNNING_WITH_BUDGET`: operazione autorizzata entro budget.
- `BUDGET_EXCEEDED`: operazione bloccata.

## Non-obiettivi V1

- Nessun scraping aggressivo o aggiramento di protezioni.
- Nessun uso di domini portale come domini ufficiali.
- Nessuna promessa di perdita economica.
- Nessun Opportunity Signal senza pipeline completa, QA e Human Review.
- Nessun run agentico automatico da batch o dashboard.

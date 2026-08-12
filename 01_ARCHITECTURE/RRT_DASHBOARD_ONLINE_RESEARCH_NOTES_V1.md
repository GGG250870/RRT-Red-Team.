---
type: research-notes
status: active
version: v1
created: 2026-08-12
---

# RRT Dashboard Online Research Notes V1

## Scopo

Questa nota raccoglie ricerca online e autoanalisi per progettare la dashboard finale RRT. Non introduce metriche validate: definisce cosa conviene rendere visibile, quali sorgenti sono utili e quali controlli servono prima di automatizzare.

## Fonti consultate

- Google Places API Place Details: ritorna dettagli come indirizzo, telefono, rating e recensioni tramite place ID. Fonte: https://developers.google.com/maps/documentation/places/web-service/place-details
- Google Places API Text Search: consente ricerca testuale con bias/restrizioni geografiche, filtri e field mask per controllare costo e payload. Fonte: https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places/searchText
- Google Business Profile review data: API per listare, leggere e gestire recensioni dei profili gestiti/autorizzati. Fonte: https://developers.google.com/my-business/content/review-data
- Registro Imprese / Telemaco: accesso a visure, fascicoli, bilanci, atti, soci, amministratori e dati legali/economici/amministrativi. Fonte: https://registroimprese.infocamere.it/web/guest/telemaco
- Registro Imprese deposito bilanci: bilanci depositati, XBRL e formato elaborabile. Fonte: https://registroimprese.infocamere.it/web/guest/deposito-bilanci
- Registro Imprese API banche dati: web service per dati ufficiali, ricerca anagrafica, visure, amministratori e Bilancio XBRL. Fonte: https://accessoallebanchedati.registroimprese.it/abdo/api
- Unioncamere Registro Imprese: il Registro garantisce pubblicita legale delle imprese italiane e include atti e bilanci. Fonte: https://unioncamere.gov.it/registro-imprese-e-semplificazione/registro-delle-imprese-e-anagrafi-camerali
- HubSpot lead scoring: distingue fit score, engagement score e combined score per contatti/aziende/deal. Fonte: https://knowledge.hubspot.com/scoring/understand-the-lead-scoring-tool
- Salesforce lead scoring dashboard: esempi utili di dashboard includono score medio per fonte, distribuzione score e conversion rate per score. Fonte: https://help.salesforce.com/s/articleView?id=005314324&language=en_US&type=1
- Pipedrive Scores: criteri spiegabili con fattori positivi/negativi e trasparenza dei contributi allo score. Fonte: https://support.pipedrive.com/en/article/scores

## Autoanalisi: cosa serve davvero a RRT

RRT non deve diventare solo una lista lead. Deve aiutare a decidere dove spendere tempo e costo agentico. La dashboard quindi deve separare cinque domande:

1. Esiste ed e identificata correttamente l'impresa?
2. Ha segnali pubblici sufficienti per essere valutata?
3. Ci sono gap commerciali osservabili rispetto alla categoria?
4. Ha reputazione, presenza e solidita sufficienti per meritare attenzione?
5. Vale la pena autorizzare un report agentico costoso?

Regola aurea applicata: la dashboard deve produrre il massimo valore gratuito nel minor tempo possibile. Il risultato ideale non e "analisi completa sempre", ma "decisione utile subito, con incertezza dichiarata".

## Tempi realistici corretti

Per l'utente, aspettare molti giorni per una analisi e inaccettabile. La distinzione corretta e:

- analisi singola: minuti;
- batch cittadino: minuti/decine di minuti;
- dashboard V1 o connettori nuovi: giorni di sviluppo;
- calibrazione statistica multi-categoria: iterativa, non bloccante.

SLA consigliate:

- imprenditore singolo, dominio ufficiale disponibile: 30-90 secondi per triage zero-LLM.
- imprenditore singolo, report rapido gratuito: 2-5 minuti.
- report opportunita guidato non-agentico: 5-15 minuti.
- dossier A1-A9 completo: 10-30 minuti dopo consenso esplicito e budget.
- batch 50 prospect con domini: 5-15 minuti.
- batch 200 prospect con domini: 15-45 minuti con output progressivo.

La dashboard deve mostrare risultati parziali appena disponibili. Un batch non deve trattenere una shortlist gia utile mentre altri siti sono lenti o bloccati.

## Moduli dashboard raccomandati

### 1. Opportunity Cockpit

Vista principale con filtri:
- categoria;
- citta/area;
- stato: `NEEDS_OFFICIAL_DOMAIN`, `COLLECTION_RESTRICTED`, `SHORTLIST`, `ESCALATE`;
- score preliminare;
- rating Google;
- numero recensioni;
- presenza social;
- disponibilita bilanci pubblici;
- employee/size band quando disponibile;
- costo stimato per prossimo step.

Razionale: prima si decide il segmento, poi si decide il costo.

### 2. Source Coverage Matrix

Per ogni prospect mostra copertura fonti:
- sito ufficiale;
- Google Business Profile / Maps / Reviews;
- portali recensioni;
- social;
- Registro Imprese / bilanci;
- documenti ufficiali aziendali;
- note manuali.

Ogni cella deve avere stato:
- `FOUND`;
- `NOT_CHECKED`;
- `COLLECTION_RESTRICTED`;
- `CONFLICT`;
- `STALE`;
- `NOT_APPLICABLE`.

Razionale: senza copertura fonti, lo score rischia di sembrare piu certo di quanto sia.

### 3. Explainable Opportunity Score

Lo score dashboard deve essere scomposto, non solo numerico:
- `category_fit_score`: quanto il target appartiene bene alla categoria scelta;
- `commercial_gap_score`: gap osservabili sul sito ufficiale;
- `reputation_score`: rating, volume recensioni, qualita segnali review;
- `social_presence_score`: social presenti, aggiornati, coerenti;
- `financial_capacity_score`: bilanci, dimensione, continuita, solidita pubblica;
- `contactability_score`: telefono, email, form, prenotazione, WhatsApp;
- `data_quality_score`: completezza e contraddizioni;
- `cost_to_validate_eur`: costo stimato per passare allo step successivo.

Razionale: HubSpot separa fit/engagement, Pipedrive rende spiegabili i contributi, Salesforce usa dashboard per distribuzione e conversione. RRT deve fare lo stesso, ma con provenance e guardrail metodologici.

### 4. Map & City View

Vista geografica:
- cluster per citta;
- densita opportunita;
- categorie attive;
- rating medio;
- numero prospect per stato;
- coverage Google/review/social/bilanci per area.

Razionale: il progetto lavora per citta e categorie; una vista mappa aiuta a decidere dove fare batch e dove no.

### 5. Entity Resolution Workbench

Pannello per evitare contaminazione:
- nome trovato;
- ragione sociale;
- P.IVA/codice fiscale quando disponibile;
- dominio ufficiale;
- Google place ID;
- indirizzo;
- social ufficiali;
- bilancio/visura collegata;
- conflitti e duplicati.

Razionale: Google, portali e social possono riferirsi a sedi, brand o franchising; prima del report bisogna sapere quale entita si sta analizzando.

### 6. Review Intelligence

Analisi reputazionale:
- rating;
- volume recensioni;
- frequenza recensioni recenti;
- temi ricorrenti;
- recensioni senza risposta quando accessibili;
- segnali di fiducia;
- segnali di attrito;
- rischio recensioni basse o polarizzate.

Razionale: le recensioni non sono solo prova sociale; spesso rivelano promesse mancate, frizioni e differenziatori non comunicati dal sito.

### 7. Public Financial Snapshot

Modulo bilanci pubblici:
- disponibilita visura/bilancio;
- ultimo anno disponibile;
- ricavi quando disponibili;
- utile/perdita;
- patrimonio netto;
- addetti o size band quando disponibile;
- procedure, liquidazioni o eventi critici se presenti;
- costo fonte;
- freshness.

Razionale: per PMI fino a 200 persone e categorie locali, la capacita economica e la stabilita contano prima di spendere in A1-A9.

### 8. Report Builder

Output selezionabili:
- lista operativa CSV/XLSX;
- shortlist per commerciale;
- report batch categoria/citta;
- report imprenditore rapido;
- report opportunita guidato;
- dossier RRT completo.

Ogni report deve avere:
- versione template;
- fonti usate;
- costo EUR;
- limiti;
- stato validazione.

### 9. Cost & Consent Panel

Sempre visibile:
- operazione selezionata;
- costo stimato EUR;
- costo massimo autorizzabile;
- costo consuntivo;
- costo cumulativo batch;
- blocco agent team;
- pulsante/azione di consenso esplicito.

Razionale: l'utente ha richiesto controllo puntuale dei costi e nessun uso agentico non autorizzato.

### 10. Calibration & Outcome Loop

Pannello per imparare dai risultati:
- prospect contattati;
- risposte;
- appuntamenti;
- clienti acquisiti;
- falsi positivi;
- falsi negativi;
- costo per shortlist;
- costo per report;
- costo per opportunita reale;
- score distribution per categoria/citta.

Razionale: senza feedback commerciale, lo score resta euristico.

## Priorita implementativa

1. Dashboard shell con categorie, citta, stato, export e cost panel.
2. Source Coverage Matrix.
3. Import/export CSV/XLSX/JSON/MD.
4. Google Places connector design con field mask e costo stimato.
5. Bilanci pubblici connector design con Registro Imprese/Telemaco/API banche dati.
6. Entity Resolution Workbench.
7. Review Intelligence.
8. Report Builder tre livelli.
9. Agent-team unlock flow con consenso e budget.
10. Calibration loop con outcome commerciali.

## Rischi e guardrail

- Google Business Profile API completa per recensioni richiede autorizzazione del profilo gestito; per prospect terzi usare Places/risultati pubblici dove consentito.
- Le API Google hanno costo per campo richiesto: usare field mask minime e stimare costo prima della chiamata.
- Registro Imprese/Telemaco puo richiedere acquisto o credenziali; ogni documento deve registrare costo e provenance.
- I portali recensioni non devono essere scraperati se termini o protezioni lo vietano.
- Social e portali possono contenere duplicati, sedi o brand non equivalenti alla ragione sociale.
- Bilancio pubblico non equivale automaticamente a disponibilita commerciale.
- Nessun dato finanziario deve generare claim economici senza A1-A9, QA e Human Review.

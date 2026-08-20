---
type: delivery-roadmap
status: active
version: v1
created: 2026-08-12
---

# RRT Dashboard Delivery Roadmap V1

## Stato attuale

La dashboard V1 locale e pronta come motore operativo gratuito:
- categorie e target segment;
- enrichment pubblico legal-safe;
- contatti telefono, cellulare/WhatsApp, email e indirizzo;
- tre passaggi report crescenti;
- export CSV, XLSX, JSON, Markdown, DOCX e HTML stampa;
- Cost & Consent Panel;
- agent team A1-A9 bloccato fino a consenso esplicito.

Non e ancora un sistema produzione su dati reali finche non vengono validati batch e fonti per categoria.

## Tempi realistici

### Fase 0 - PR e baseline

Durata: 0.5 giornata.

Output:
- merge PR dashboard V1;
- riesecuzione test;
- generazione demo locale con CSV esempio;
- checklist operativa per uso manuale.

Dipendenze:
- nessuna API;
- nessun agent team.

### Fase 1 - Pilot gratuito ristorazione

Durata: 1 giornata per una citta e un target.

Target consigliato:
- `ristorazione`;
- `pizzeria` o `fine_dining`;
- 30-50 prospect iniziali da CSV/manual input.

Output:
- dashboard reale;
- shortlist;
- tre passaggi report per selezionati;
- cost ledger a `EUR 0.0000`;
- misurazione domini risolti, contatti trovati, coverage Google/review/social/bilanci.

Dipendenze:
- CSV con nomi/domini o lista prospect verificabile;
- fonti pubbliche gratuite accessibili.

### Fase 2 - Pilot PMI e nicchie

Durata: 1-2 giornate per due categorie aggiuntive.

Target consigliati:
- `pmi` fino a 200 persone;
- `benessere_estetica`;
- `servizi_casa`;
- `formazione`.

Output:
- profili categoria rifiniti sui dati reali;
- falsi positivi e falsi negativi annotati;
- ranking comparabile per citta/categoria;
- shortlist esportabile.

Dipendenze:
- CSV o fonti gratuite gia consultabili;
- nessuna promessa di bilanci completi senza fonte autorizzata.

### Fase 3 - Calibrazione batch

Durata: 2-3 giornate.

Volume:
- 50-200 imprese per categoria prioritaria;
- almeno 2 citta;
- almeno 2 target ristorazione.

Output:
- metriche reali su precisione e tempi;
- soglie score da correggere;
- categorie da promuovere o sospendere;
- report finale di validazione V1.

Metriche minime:
- dominio ufficiale risolto;
- telefono trovato;
- cellulare/WhatsApp trovato;
- email trovata;
- indirizzo trovato;
- review/social/bilanci coverage;
- `SHORTLIST` confermate manualmente;
- falsi positivi.

### Fase 4 - Connettori ufficiali opzionali

Durata: 2-5 giornate dopo accessi disponibili.

Connettori possibili:
- Google Places/Profile API;
- fonte autorizzata bilanci/visure;
- export/API portali review quando consentiti.

Output:
- costi stimati/consuntivi in EUR;
- budget guard;
- provenance fonte;
- blocco automatico se manca consenso.

Dipendenze:
- chiavi API;
- pricing noto;
- termini d'uso compatibili.

### Fase 5 - Dashboard prodotto

Durata: 3-5 giornate dopo calibrazione V1.

Output:
- UI web piu comoda;
- caricamento CSV;
- salvataggio sessioni;
- confronto citta/categorie;
- storico costi;
- download guidato dei tre passaggi report.

Dipendenze:
- decisione su hosting;
- modello dati finale;
- risultati Fase 3.

## Timeline consigliata

Sequenza minima senza attese lunghe:

1. Giorno 0: merge PR e demo locale.
2. Giorno 1: pilot ristorazione su una citta e un target.
3. Giorno 2: pilot PMI/nicchia con 30-50 prospect.
4. Giorni 3-5: calibrazione batch su 50-200 imprese.
5. Giorni 6-10: solo se servono, connettori ufficiali e dashboard prodotto.

La prima dashboard utile deve arrivare entro 24 ore dal dataset reale, non dopo dieci giorni.

## Livello di precisione atteso

Prima della calibrazione:
- precisione metodologica: alta;
- precisione opportunita commerciale: provvisoria;
- rischio falsi positivi: medio;
- claim consentiti: shortlist e priorita di verifica, non Opportunity Signal.

Dopo Fase 3:
- precisione operativa stimabile su categoria/citta;
- soglie score piu affidabili;
- categorie non performanti sospese;
- report pronti per uso commerciale controllato.

Dopo connettori ufficiali:
- migliore copertura su Google, contatti e bilanci;
- costi tracciati in EUR;
- ancora nessun Opportunity Signal senza A1-A9, QA e Human Review.

## Definition of Done V1

La V1 e completa quando:
- PR dashboard mergiata;
- almeno un pilot ristorazione eseguito;
- almeno un pilot PMI o nicchia eseguito;
- almeno 50 prospect reali processati;
- export aperti e verificati;
- cost ledger verificato;
- falsi positivi annotati;
- nessun dato inventato;
- nessun agent team usato senza consenso.

---
type: reusable-gate-checklist
version: v1
status: active
category: pmi
target_segment: climatizzazione_impianti
market: Savona
updated: 2026-08-18
---

# RRT PMI Climatizzazione Savona Lead-Trust Gate V1

## Purpose

Applicare a PMI e imprese tecniche di climatizzazione un gate diverso da dentale e ristorazione.

Il percorso da valutare non e "prenoto una visita" ma:

> ricerca locale -> fiducia tecnica -> richiesta sopralluogo/preventivo/intervento.

Il gate non valuta qualita tecnica, conformita reale degli impianti o bilanci interni. Valuta solo segnali pubblici esterni utili a capire se un potenziale cliente puo scegliere e contattare l'impresa con fiducia.

## Required inputs

Per ogni impresa:

- nome pubblico;
- ragione sociale se reperibile;
- indirizzo operativo;
- sito ufficiale;
- telefono, cellulare o WhatsApp;
- email;
- profilo Google/Maps pubblico;
- portali recensioni o directory pertinenti;
- social ufficiali;
- certificazioni dichiarate pubblicamente;
- link Registro Imprese o altre fonti societarie pubbliche;
- 1-3 comparator locali o provinciali.

## Evidence checklist

### A. Entity resolution

- [ ] Nome, indirizzo e sito ufficiale sono coerenti.
- [ ] La provincia/comune rientra nello scope Savona o provincia.
- [ ] La ragione sociale/P.IVA e tracciata se esposta.
- [ ] Duplicati, sedi multiple o brand collegati sono annotati.
- [ ] Se l'entita non e chiara, stato `ENTITY_UNRESOLVED`.

### B. Lead path

- [ ] Il sito espone richiesta preventivo, sopralluogo, consulenza o assistenza.
- [ ] Telefono cliccabile o comunque evidente.
- [ ] Cellulare/WhatsApp presente se dichiarato.
- [ ] Email presente.
- [ ] Form presente e coerente con il servizio richiesto.
- [ ] Se il servizio e urgente o manutentivo, il percorso di assistenza e distinto dal preventivo commerciale.

### C. Trust path tecnico

- [ ] Certificazioni dichiarate pubblicamente: es. FGAS, ISO, SOA, MEPA, FER.
- [ ] Marchi/centri assistenza/partner indicati.
- [ ] Realizzazioni, cantieri, portfolio o referenze visibili.
- [ ] Settori serviti chiari: residenziale, aziende, PA, industriale, condomini.
- [ ] Garanzia, conformita, libretto impianto, incentivi o detrazioni spiegati solo se pubblicamente presenti.

### D. Review and local presence

- [ ] Profilo Google/Maps verificato manualmente o tramite link di ricerca.
- [ ] Rating/review count annotati come segnali pubblici, non giudizio tecnico.
- [ ] Portali review/directory controllati senza scraping massivo.
- [ ] Social ufficiali controllati per coerenza e attivita pubblica.

### E. Public financial / company layer

- [ ] Registro Imprese o fonte societaria pubblica aperta come link di verifica.
- [ ] Bilanci/documenti pubblici usati solo se gratuitamente disponibili.
- [ ] Nessuna stima di fatturato, utile o numero dipendenti se non verificata.
- [ ] Target PMI fino a 200 persone resta `UNVERIFIED_SIZE` finche non c'e fonte pubblica.

## Finding decision rules

### NO_SIGNAL

Usare se:

- il sito ha gia contatti chiari;
- il servizio e comprensibile;
- il percorso preventivo/sopralluogo e sufficiente;
- la differenza con comparator e solo estetica o generica.

### WATCHLIST

Usare se:

- il pre-screen indica buona complessita commerciale;
- manca ancora Google/review/bilanci;
- il potenziale gap riguarda un percorso specifico ma non e falsificato;
- serve screenshot o verifica manuale prima di promuovere.

### OPPORTUNITY_SIGNAL_CANDIDATE

Usare se:

- esiste un gap specifico nel percorso richiesta preventivo/sopralluogo/intervento;
- almeno un comparator locale rende quel passaggio piu chiaro;
- il gap e rilevante per clienti B2B, condomini, PA o residenziale ad alto valore;
- Red Team non lo falsifica;
- non servono claim economici.

### OPPORTUNITY_SIGNAL

Usare solo se:

- entity resolution e solida;
- Google/review/local presence sono verificati;
- fonti societarie pubbliche sono almeno tracciate;
- evidence pack completo;
- comparator fit difendibile;
- Red Team `SURVIVES`;
- messaggio cliente non critica qualita tecnica;
- human review approva.

## Unsafe wording

Non usare:

- "state perdendo clienti";
- "non siete affidabili";
- "non avete certificazioni";
- "i competitor sono migliori";
- "il sito e brutto/vecchio";
- "avete poche recensioni";
- "manca il cellulare" se il telefono/email sono gia chiari.

## Safe client wording

> Abbiamo osservato il percorso pubblico con cui un cliente trova l'impresa, capisce se puo fidarsi tecnicamente e prova a chiedere un sopralluogo o un preventivo. Ci sono gia segnali positivi; il punto e rendere piu guidato e verificabile il passaggio tra fiducia tecnica e primo contatto.

## Related

- [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]]
- [[10_REPORTS/SAVONA_PMI_CLIMATIZZAZIONE_GATE_TRIAGE_2026-08-18]]

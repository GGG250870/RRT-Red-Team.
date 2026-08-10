---
type: architecture-extension
version: v1.1
status: active
updated: 2026-08-10
---

# Integrated Knowledge Model

## Scopo
Integrare il framework operativo persistito nel repository con le librerie metodologiche consolidate durante il lavoro in chat, mantenendo GitHub come fonte autorevole e Obsidian come interfaccia umana.

## Principio di integrazione
Il repository prevale in caso di conflitto. Il lavoro conversazionale viene integrato solo quando:
- non contraddice lo stato persistito;
- aggiunge una tassonomia o una libreria utile;
- è espresso come framework/metodologia e non come fatto empirico non verificato;
- mantiene separati fatto, ipotesi, stato non risolto e validazione.

## Modello unificato
PUNTO ZERO / PROBLEMA PERCEPITO
→ PATTERN
→ BLIND SPOT
→ EVIDENCE
→ TARGET
→ SATURATION
→ TARGET MATCH
→ BENCHMARK
→ FINDING
→ RED TEAM
→ COMMERCIAL GATE
→ SIGNAL
→ HUMAN REVIEW
→ VALIDATION

## Granularità canonica
Lo standard operativo di dettaglio è [[01_ARCHITECTURE/RRT_GRANULAR_TRACEABILITY_STANDARD_V1]].

Ogni oggetto rilevante deve essere atomico, identificabile, versionabile e ricostruibile a ritroso. In particolare:
- ogni evidence sostiene un solo claim materiale;
- source, observation, interpretation e claim restano separati;
- ogni target conserva evidence accettate/rifiutate, unresolved e search trace;
- ogni benchmark viene congelato prima del gap;
- ogni finding separa factual difference, interpretation e commercial hypothesis;
- ogni Red Team packet conserva controevidenza e alternative explanations;
- ogni promozione di Signal richiede catena completa di refs;
- ogni decisione materiale entra nell'audit trail.

## Librerie metodologiche consolidate

### Problem Library
100 problemi percepiti ricorrenti dell'imprenditore, usati come layer di ingresso e non come diagnosi.

### Pattern Library
46 pattern organizzativi/commerciali ricorrenti. I pattern sono ipotesi di lavoro e richiedono evidenze prima di diventare finding.

### Blind Spot Atlas
240 blind spot strutturati, organizzati per leadership, persone, marketing, vendite, organizzazione, controllo, cliente, innovazione, strategia, finanza, governance, execution e performance.

### Question Library
Domande organizzate per apertura, consapevolezza, diagnosi, quantificazione, priorità, transizione e verifica.

### Evidence Library
Fonti pubbliche/consensuali e loro uso consentito. Ogni evidenza deve mantenere provenance, observed_at, scope e stato.

### Revenue Trigger / Insight Layer
Gli insight e i “Sapevi che…” sono output commerciali derivati da evidenza e non possono introdurre claim non dimostrati.

## Evidence Levels
### Level A — OBSERVABLE
Fatto direttamente osservabile da fonte pubblica o consensuale. Può essere affermato se verificato e tracciato.

### Level B — DEDUCIBLE
Ipotesi motivata da più evidenze concordanti. Deve essere esplicitamente formulata come ipotesi e sottoposta a Red Team.

### Level C — INTERNAL ONLY
Informazione interna non inferibile in modo affidabile dall’esterno, inclusi leadership reale, clima, delega effettiva, marginalità per linea, cultura e processi decisionali interni. Stato predefinito: `UNRESOLVED` fino a verifica.

## Stati ammessi per dati mancanti o problematici
- `UNRESOLVED`
- `NOT_FOUND_AFTER_PROTOCOL`
- `COLLECTION_RESTRICTED`
- `CONTRADICTORY`
- `BLOCKED`
- `STALE`
- `REJECTED_BY_AUDIT`

Un dato mancante non viene mai trasformato automaticamente in zero.

## Scoring
Gli score conversazionali precedenti sono da considerare euristiche non validate fino a calibrazione empirica.

Ogni score futuro deve distinguere:
- evidence confidence;
- commercial consequence level;
- validation state;
- eventuale priorità euristica.

Nessun punteggio euristico equivale a probabilità statistica o perdita economica dimostrata.

## Tracciabilità minima
Ogni risultato importante deve poter essere ricostruito come:

[[04_PROSPECTS/Prospects Index|prospect]]
→ [[05_EVIDENCE/Evidence Index|evidence]]
→ target
→ [[06_BENCHMARKS/Benchmarks Index|benchmark]]
→ finding
→ [[08_RED_TEAM/Red Team Index|red-team]]
→ commercial gate
→ signal
→ human review
→ [[09_VALIDATION/Validation Dashboard|validation]]

## Regole operative ChatGPT ↔ GitHub ↔ Obsidian
1. Prima di modificare, leggere il file rilevante e recuperare lo SHA corrente.
2. GitHub è la fonte persistente e auditabile.
3. Obsidian legge i file Markdown e i backlink dal repository sincronizzato localmente.
4. Salvare solo avanzamenti consolidati.
5. Appunti temporanei e ragionamenti intermedi non vanno persistiti.
6. In caso di conflitto tra conversazione e repository, prevale lo stato persistito verificabile.
7. Ogni nuovo blocco operativo deve rispettare il Granular Traceability Standard prima di essere considerato consolidato.

## Related
- [[00_HOME/HOME]]
- [[01_ARCHITECTURE/Architecture Overview]]
- [[01_ARCHITECTURE/RRT_GRANULAR_TRACEABILITY_STANDARD_V1]]
- [[03_RULES/Rules Index]]
- [[05_EVIDENCE/Evidence Index]]
- [[09_VALIDATION/Validation Dashboard]]

---
type: architecture-audit
version: v1.0
status: active
updated: 2026-08-10
---

# RRT Architecture & Economic Sustainability Audit v1

## Executive verdict
L'architettura metodologica è coerente con il progetto originale e con l'obiettivo di produrre Opportunity Signal difendibili da evidenza esterna. L'architettura runtime non è ancora pronta per un run multi-agent completo: manca `02_AGENTS/runtime/worker.py` e mancano controlli espliciti di budget, stop conditions, retry/idempotenza e cost accounting per case/agent.

Stato complessivo: `GO_WITH_BLOCKERS`.

Non avviare una wave multi-agent live completa finché i blocker runtime/economici non sono chiusi.

## Coerenza con il progetto originale
### Coerente
- Punto Zero / problema percepito resta il layer umano di ingresso.
- Evidence-first e separazione fatto/ipotesi preservano il principio di non inventare.
- Benchmark freeze prima del gap riduce cherry-picking.
- Red Team avversariale preserva la funzione originale di rivelare punti ciechi senza trasformarsi in critica arbitraria.
- Commercial Gate mantiene il dossier orientato all'appuntamento senza fingere perdite economiche non dimostrate.
- Human Review mantiene le persone al centro e impedisce l'automazione cieca di decisioni commerciali.
- GitHub come source of truth e Obsidian come human interface sono compatibili con auditabilità e knowledge reuse.

### Evoluzioni compatibili
- Granular Traceability Standard.
- Prominence & Discoverability Gate P1-P8.
- Loop di granularità/re-audit.
- Multi-agent independence.

Queste evoluzioni migliorano il progetto originale purché siano governate da stop conditions e budget.

## Divergenze da correggere
### D1 — Pipeline documentale non perfettamente allineata
`Architecture Overview.md` contiene ancora `GENERAL EVIDENCE → TARGET DISCOVERY → ... → BUYER SCORING`, mentre il modello integrato usa `PUNTO ZERO → PROBLEM → PATTERN → BLIND SPOT → EVIDENCE...`.

Decisione: mantenere due viste esplicite:
1. **Human/Commercial Intake Layer**: Punto Zero → Problem → Pattern → Blind Spot.
2. **Evidence Validation Pipeline**: Entity/Scope → Discovery → Deep Scan → Saturation → Target Match → Benchmark → Finding → Red Team → Commercial Gate → Signal → Human Review → Validation.

`BUYER SCORING` non deve essere un gate autonomo finché non è calibrato empiricamente; gli score restano euristiche.

### D2 — Loop senza stop condition
Il principio di granularità iterativa è corretto, ma un loop aperto crea rischio di:
- ricerca infinita;
- costi API non controllati;
- diminishing returns;
- overfitting del finding;
- bias da ricerca successiva al risultato.

Decisione: ogni loop deve avere `loop_reason`, `max_iterations`, `query_budget`, `token_budget`, `stop_condition`, `marginal_information_gain`, `final_state`.

## Audit runtime
### BLOCKER R1 — worker.py mancante
`orchestrator.py` invoca `02_AGENTS/runtime/worker.py`; il file non è presente nel repository.

Impatto: il provider live funziona individualmente, ma l'orchestratore non può eseguire realmente le wave multi-agent.

### BLOCKER R2 — nessun cost ledger
Il provider registra token per singola risposta, ma lo state store non conserva ancora in forma strutturata:
- model;
- input_tokens;
- output_tokens;
- cached_tokens;
- estimated_cost_usd;
- cost_per_case;
- cost_per_stage;
- cumulative_cost.

Impatto: impossibile dimostrare economicità del sistema a scala.

### HIGH R3 — nessun hard budget guard
Non esiste un blocco automatico per:
- max API cost/case;
- max API cost/batch;
- max calls/agent;
- max retries;
- max tokens/task.

### HIGH R4 — retry/idempotenza incompleti
`INSERT OR REPLACE` e task UUID riducono collisioni ma non definiscono una policy robusta per retry, duplicate execution e crash recovery.

### HIGH R5 — structured output non imposto a livello API
I prompt chiedono JSON-only, ma il provider fa parsing post-hoc. Un output non JSON diventa `FAIL_JSON` dopo aver consumato token.

Decisione futura: usare Structured Outputs/schema quando possibile.

### MEDIUM R6 — state store locale non condiviso
SQLite locale è appropriato per il prototipo, ma GitHub non contiene lo stato live del DB. Serve una policy di export/snapshot machine-readable per audit condiviso senza committare un database volatile ad ogni task.

### MEDIUM R7 — secrets management
La chiave API è correttamente fuori dal repository. Va mantenuta solo in environment/secret store; mai loggare header, chiavi o traceback contenenti credenziali.

## Audit economico
Prezzi standard verificati il 2026-08-10:
- GPT-5.6 Sol: $5/M input, $30/M output.
- GPT-5.6 Terra: $2.50/M input, $15/M output.
- GPT-5.6 Luna: $1/M input, $6/M output.

### Problema del mapping attuale
Mapping attuale:
- Terra: A1, A2, A3, A5, A6, A8.
- Sol: A4, A7, A9.

È qualitativamente prudente, ma costoso per attività ad alto volume come discovery, entity normalization e scansione.

### Routing economico raccomandato
**Luna**
- A1 Discovery: crawling plan, extraction normalization, deduplication.
- prima passata A2 Entity/Scope su casi semplici.
- task meccanici di classificazione/provenance.

**Terra**
- A2 escalation su identità/scope non banali.
- A3 Deep Scan.
- A5 Target Match.
- A6 Benchmark.
- A8 Commercial Gate preliminare.

**Sol**
- A4 Evidence Auditor su casi materialmente rilevanti.
- A7 Red Team.
- A9 QA finale.
- escalation di casi `CONTRADICTORY`, `BLOCKED` o ad alto valore.

Principio: `cheap-first, escalate-on-uncertainty`, non `frontier-everywhere`.

### Prompt caching
Le istruzioni di sistema e le tassonomie sono largamente ripetitive. Devono essere progettate per massimizzare input caching e ridurre costo unitario.

### Batch processing
Per lavorazioni non interattive di calibrazione, valutare Batch API quando compatibile con il workflow; il pricing ufficiale indica una riduzione rispetto allo standard processing.

## Unit economics da misurare
Prima di parlare di profittabilità commerciale vanno misurati almeno:
- API cost per prospect screened;
- API cost per saturated prospect;
- API cost per Opportunity Signal Candidate;
- analyst/human minutes per prospect;
- conversion dossier → appointment;
- appointment → paid engagement;
- gross margin per engagement;
- false positive cost;
- false negative sampling rate.

### Formule operative
`Cost_per_prospect = API + search/tool fees + allocated human review cost`

`Cost_per_candidate = total_batch_cost / Opportunity_Signal_Candidates`

`CAC_RRT = total_prospecting_cost / new_paid_clients`

`Contribution_margin = client_revenue - variable_delivery_cost - RRT_acquisition_cost`

Nessuna affermazione di “profittevole” è ammessa prima di misurare questi denominator su campioni reali.

## Guardrail economici iniziali
Da calibrare con dati reali, non trattare come benchmark empirici:
- definire un `soft_budget_usd_per_prospect` prima del live batch;
- definire un `hard_budget_usd_per_prospect` che blocca nuove iterazioni;
- Sol solo su escalation/gate ad alto valore;
- interrompere la ricerca quando l'information gain marginale non modifica stato/gate;
- nessun loop può modificare retroattivamente query frozen o benchmark frozen.

## Compatibilità Obsidian/GitHub
PASS.

Condizioni:
- Markdown per viste umane e decision notes;
- JSON per ledger/schema;
- niente DB SQLite volatile come unica fonte condivisa;
- snapshot/export consolidati del runtime in GitHub;
- backlink coerenti tra Prospect → Evidence → Target → Benchmark → Finding → Red Team → Signal → Validation.

## Profitability verdict
`UNRESOLVED — MEASURABLE`.

L'architettura può essere economicamente sostenibile e presenta una logica favorevole alla marginalità perché filtra prospect prima dell'intervento umano e riserva i modelli più costosi ai gate ad alto valore. Tuttavia non esistono ancora dati persistiti sufficienti per dichiarare profittabilità reale.

La profittabilità deve essere validata come ipotesi attraverso il Batch Calibration e successivi test commerciali.

## Priorità prima del primo multi-agent live run
1. Creare `worker.py` con structured task lifecycle e error handling.
2. Aggiungere cost ledger per task/case/stage.
3. Aggiungere budget guard e max iteration guard.
4. Formalizzare Granularity Loop Controller.
5. Allineare Architecture Overview alle due pipeline (human intake + evidence validation).
6. Aggiornare HOME: provider live verificato, runtime multi-agent ancora BLOCKED finché R1-R4 non sono chiusi.
7. Solo dopo: canary run A1+A2 su un singolo caso già noto.

## Decisione finale
**NON lanciare ancora i 9 agenti live.**

Architettura metodologica: `PASS`.
Compatibilità GitHub/Obsidian: `PASS`.
Provider API singolo: `PASS`.
Runtime orchestrato: `BLOCKED`.
Sostenibilità economica potenziale: `PASS_WITH_MEASUREMENT_REQUIRED`.
Profittabilità dimostrata: `UNRESOLVED`.

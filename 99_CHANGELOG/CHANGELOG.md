---
type: changelog
status: active
---

# CHANGELOG

## 2026-08-12
- Rafforzata PR #7 `agent/prescreen-batch-generator`: il batch builder portal-first scarta link di navigazione/generici e non usa più domini di portale come domini ufficiali del prospect.
- `build_batch.py` lascia `domain` vuoto e imposta `official_domain_state = UNRESOLVED` quando scopre solo una scheda portale.
- `pre_screen.py` preserva `source_url` e ferma i record senza dominio ufficiale come `COLLECTION_RESTRICTED` con `fetch_state = NO_OFFICIAL_DOMAIN`.
- Test live Savona: 5 profili reali MioDottore, 0 righe navigazionali, 0 `ESCALATE`, 5 `COLLECTION_RESTRICTED`; la shortlist resta vuota finché manca `OFFICIAL_DOMAIN_RESOLUTION`.
- PR #7 resta non merge-safe finché non viene implementata e validata la risoluzione del dominio ufficiale.

## 2026-08-10
- Integrato il framework persistito del repository con le librerie metodologiche consolidate emerse nel lavoro conversazionale.
- Creato [[01_ARCHITECTURE/Integrated Knowledge Model]].
- Formalizzato il modello unificato: Punto Zero → Pattern → Blind Spot → Evidence → Target → Saturation → Target Match → Benchmark → Red Team → Commercial Gate → Signal → Human Review → Validation.
- Registrate come librerie metodologiche consolidate: Problem Library (100), Pattern Library (46), Blind Spot Atlas (240), Question Library, Evidence Library e Revenue Trigger/Insight Layer.
- Formalizzati Evidence Level A `OBSERVABLE`, B `DEDUCIBLE`, C `INTERNAL ONLY`.
- Confermato che score e pesi conversazionali precedenti sono euristiche non validate finché non calibrate empiricamente.
- Formalizzati gli stati `UNRESOLVED`, `NOT_FOUND_AFTER_PROTOCOL`, `COLLECTION_RESTRICTED`, `CONTRADICTORY`, `BLOCKED`; un dato mancante non viene trasformato automaticamente in zero.
- Aggiornata HOME con il nuovo knowledge model integrato.
- Stabilita la regola operativa ChatGPT ↔ GitHub ↔ Obsidian: GitHub è fonte persistente; prima di sovrascrivere si legge file+SHA; vengono persistiti solo avanzamenti consolidati.
- Creato [[01_ARCHITECTURE/RRT_GRANULAR_TRACEABILITY_STANDARD_V1]] per introdurre granularità atomica e tracciabilità end-to-end su prospect, evidence, target, search trace, benchmark, finding, Red Team, Commercial Gate, Signal, Human Review e Validation.
- Definiti identificatori canonici, state machine estesa, temporal integrity, contradiction ledger, audit trail e Definition of Done per ogni blocco.
- Aggiornato [[01_ARCHITECTURE/Integrated Knowledge Model]] alla v1.1 per rendere il Granular Traceability Standard parte ufficiale dell'architettura.
- Creato `05_EVIDENCE/B04_TRANCHE_D_ATOMIC_EVIDENCE_PACK_V1.json`: evidence pack atomico per B04-34 Centro Odontoiatrico Gioia, B04-37 Studio Dentistico Dott. Pietro Leone e B04-48 Savasta & Partners, con evidence_id per D1-D5 e provenance su dominio ufficiale.
- Creato `09_VALIDATION/RRT_BATCH_04_SATURATION_REAUDIT_TRANCHE_D_V1.json`: Saturation Evidence Re-Audit completato sui tre candidati; 3 PASS, 0 downgrade, 0 reject. I tre casi avanzano a Target Match e Benchmark Selection Freeze. Il PASS certifica la saturazione evidenziale, non una perdita economica.
- Creato `06_BENCHMARKS/RRT_BATCH_04_TARGET_MATCH_BENCHMARK_FREEZE_TRANCHE_D_V1.json`: Target Match PASS per B04-34, B04-37 e B04-48 sui decision job D1-D5. Congelato un benchmark set verificato di due comparabili ad alto fit per ciascun prospect; il terzo benchmark resta esplicitamente `UNRESOLVED` e non viene inventato o sostituito dopo il gap.
- Creato `08_RED_TEAM/RRT_BATCH_04_DECISION_LOSS_RED_TEAM_COMMERCIAL_GATE_TRANCHE_D_V1.json`: Decision Loss comparativo e Red Team conservativo sui tre casi. Stato commerciale mantenuto provvisorio finché Prominence & Discoverability P1-P8 non sono completati; nessun claim economico o causale introdotto.
- Creato `02_AGENTS/runtime/agent_registry.json`: registro runtime dei 9 agenti con stage, system prompt, vincoli e output JSON-only, coerente con `RRT_MULTI_AGENT_ROLES_V1.json`.
- Provider OpenAI live verificato con chiamata reale `LIVE_OPENAI_RESPONSES` e parse PASS.
- Creato [[01_ARCHITECTURE/RRT_ARCHITECTURE_ECONOMIC_SUSTAINABILITY_AUDIT_V1]]: audit completo di coerenza col progetto originale, robustezza runtime, compatibilità GitHub/Obsidian e sostenibilità economica.
- Audit verdict: metodologia `PASS`, GitHub/Obsidian `PASS`, provider singolo `PASS`, runtime orchestrato `BLOCKED` prima del canary live perché manca `worker.py` e non esistono ancora cost ledger, budget guard, retry/idempotency policy e stop conditions dei loop.
- Formalizzato il principio economico `cheap-first, escalate-on-uncertainty`: Luna per discovery/normalizzazione, Terra per analisi intermedie, Sol per Evidence Audit, Red Team, QA ed escalation ad alto valore.
- Confermato che la profittabilità reale resta `UNRESOLVED` finché non vengono misurate unit economics: cost/prospect, cost/candidate, human minutes, dossier→appointment, appointment→paid, contribution margin e false positive/negative costs.
- Aggiornata HOME con lo stato reale del provider live e i blocker da chiudere prima del primo run multi-agent orchestrato.

## 2026-08-09
- Repository GitHub inizializzato come vault Obsidian RRT.
- Creata struttura base `00_HOME` → `99_CHANGELOG`.
- Documentati principi core, pipeline, multi-agent system e framework di validazione.
- Migrati i 9 ruoli multi-agent e l'orchestrazione a wave indipendenti.
- Migrati runtime `orchestrator.py`, `state_store.py` e provider LLM.
- Migrato il framework di validazione 98% e la External-Only Commercial Signal Policy.
- Migrata la specifica Target-Specific Deep Scan v1.1.
- Creato il case note U03 Oberholtzer & Martini come Opportunity Signal Candidate in attesa di blind human review.
- Creato lo stato Obsidian del Batch 04 National Calibration.
- Aggiornata HOME con stato corrente, caso di riferimento e regole di integrità.

## Regola di manutenzione
Le modifiche metodologiche future devono essere registrate qui con versione e motivazione. Una nota conversazionale non sostituisce un file persistito.

---
type: changelog
status: active
---

# CHANGELOG

## 2026-08-12
- Rafforzata PR #7 `agent/prescreen-batch-generator`: il batch builder portal-first scarta link di navigazione/generici e non usa più domini di portale come domini ufficiali del prospect.
- `build_batch.py` risolve domini ufficiali solo da link espliciti `Sito web`/`website` nella scheda portale; altrimenti lascia `domain` vuoto e imposta `official_domain_state = UNRESOLVED`.
- `pre_screen.py` preserva `source_url` e ferma i record senza dominio ufficiale come `COLLECTION_RESTRICTED` con `fetch_state = NO_OFFICIAL_DOMAIN`.
- Dentisti-Italia e DocDental sono stati disabilitati come primary discovery finché il parser profili non è validato contro righe di navigazione.
- Test live Savona: 5 profili reali MioDottore, 0 righe navigazionali, 2 domini ufficiali risolti, 1 `ESCALATE`, 1 `SHORTLIST`, 3 `COLLECTION_RESTRICTED`.
- Default `rrt_build_and_prescreen.sh` riportati a città (`Milano,Roma,Torino,Genova,Bologna`); il targeting quartiere resta best effort e non ancora validato.
- PR #7 resta da validare su più aree perché MioDottore non copre necessariamente il livello quartiere e le fonti secondarie sono disabilitate.
- Declassate le note pilota Genova/Itri a ipotesi manuali non validate: nessun Opportunity Signal o claim economico senza A1→A9, QA e Human Review.
- Rafforzato `02_AGENTS/runtime/qa_scoring_engine_v2.py`: un target bloccato non può esporre `status = PASS` né `normalized_0_100`.
- Estesa `09_VALIDATION/test_scoring_integrity_v2.py` da 5 a 11 regression check, includendo stati bloccanti (`UNRESOLVED`, `COLLECTION_RESTRICTED`, `CONTRADICTORY`), dimensioni inattese, scoring bloccato con output numerico e guard `SATURATED_MULTI_TARGET`.
- Aggiunto in `02_AGENTS/runtime/motore_multi_target_v2.py` il guard `validate_saturated_multi_target`: `SATURATED_MULTI_TARGET` è valido solo se tutti i target attesi sono terminali.
- Riallineate le note Obsidian di Tranche D al ledger machine-readable `09_VALIDATION/RRT_BATCH_04_SATURATION_REAUDIT_TRANCHE_D_V1.json`: B04-34, B04-37 e B04-48 risultano re-audit PASS 3/3.
- Aggiornate le schede B04-34 e B04-48: benchmark freeze parziale e `NO_SIGNAL_PROVISIONAL`; P1-P8 prominence/discoverability resta il gate aperto prima di qualunque conclusione commerciale.
- La Legacy Zero Repair Queue resta aperta con 15 item: nessuno zero legacy è stato convertito automaticamente.
- Reso il pre-screen adattabile per categoria: profili `dentale`, `ristorazione`, `pmi`, `hospitality`, `benessere_estetica`, `servizi_casa`, `formazione` e `generic` con dimensioni, page hints, pattern high-value e gap separati. La discovery automatica resta validata solo per `dentale`/MioDottore; le altre categorie usano CSV manuali finché fonti category-safe non sono validate.
- Creato `01_ARCHITECTURE/RRT_FINAL_DASHBOARD_PRODUCT_SPEC_V1.md`: specifica dashboard finale con scelta categoria/citta, raccomandazione percorso opportunita, export CSV/XLSX/JSON/MD/DOCX/PDF, tre report per imprenditore e contatore costi in EUR.
- Aggiunto guard runtime: i run live degli agent team A1-A9 restano bloccati senza consenso esplicito via `RRT_AGENT_TEAM_APPROVAL=I_APPROVE_AGENT_TEAM_LIVE_RUN`.
- Formalizzate le primary intelligence sources per tutte le categorie: Google Business/Profile Reviews/Maps, portali recensioni, social e bilanci pubblici/Registro Imprese, separandole dalla risoluzione del dominio ufficiale e dagli Opportunity Signal.
- Creato `01_ARCHITECTURE/RRT_DASHBOARD_ONLINE_RESEARCH_NOTES_V1.md` con ricerca online e autoanalisi su moduli utili per la dashboard: Opportunity Cockpit, Source Coverage Matrix, Explainable Score, Map View, Entity Resolution, Review Intelligence, Public Financial Snapshot, Report Builder, Cost & Consent e Calibration Loop.
- Formalizzata la regola aurea dashboard: massimizzare prima tutto cio che e gratuito, legalmente accessibile e realisticamente utile; mai inventare e mai usare agent/API/fonti a pagamento senza consenso. Aggiunte SLA operative: triage singolo in 30-90s, report rapido 2-5m, batch 50 in 5-15m, batch 200 in 15-45m con output progressivo.
- Implementata `11_DASHBOARD/dashboard.py`: dashboard HTML locale zero-LLM da CSV pre-screen, con Opportunity Cockpit, Source Coverage Matrix, shortlist CSV, payload JSON, report batch Markdown, report rapidi singoli e stato `AGENT_TEAM_LOCKED`.
- Estesi gli export dashboard: `prospects.xlsx`, `batch_report.docx` e `print_report.html` generati localmente senza dipendenze esterne e con costo `EUR 0.0000`.
- Aggiunti tre report per prospect selezionato: rapido zero-LLM (`reports/`), opportunita guidato non-agentico (`guided_reports/`) e template A1-A9 bloccato (`full_rrt_locked/`) con consenso/budget richiesti.
- Implementato `11_DASHBOARD/enrich_public_sources.py`: enrichment online gratuito/legal-safe da sito ufficiale e URL pubblici forniti, con estrazione social/review/bilanci linkati, `robots.txt` check, provenance `source_refs_json`, nessun aggiramento e costo `EUR 0.0000`.
- Aggiunta segmentazione target per `ristorazione`: `fine_dining`, `pizzeria`, `trattoria_osteria`, `sushi_etnico`, `delivery_asporto`, `eventi_catering`, `enoteca_wine_bar`, `bar_cafe` e `ristorazione_generic`, con TripAdvisor e altri portali review come intelligence/provenance per segmento.

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

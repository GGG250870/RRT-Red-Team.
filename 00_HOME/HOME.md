---
type: dashboard
project: RRT Red Team
status: active
updated: 2026-08-12
---

# RRT Red Team — Home

## Navigazione
- [[00_HOME/SECOND_BRAIN]]
- [[01_ARCHITECTURE/Architecture Overview]]
- [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]]
- [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]]
- [[01_ARCHITECTURE/RRT_DASHBOARD_VERTICAL_DATA_CONTRACT_V1]]
- [[01_ARCHITECTURE/Integrated Knowledge Model]]
- [[01_ARCHITECTURE/Knowledge Graph Flow]]
- [[01_ARCHITECTURE/RRT_FINAL_DASHBOARD_PRODUCT_SPEC_V1]]
- [[01_ARCHITECTURE/RRT_DASHBOARD_DELIVERY_ROADMAP_V1]]
- [[01_ARCHITECTURE/RRT_DASHBOARD_ONLINE_RESEARCH_NOTES_V1]]
- [[01_ARCHITECTURE/RRT_ARCHITECTURE_ECONOMIC_SUSTAINABILITY_AUDIT_V1]]
- [[02_AGENTS/Multi-Agent System]]
- [[02_AGENTS/RRT_AGENT_OPERATING_MODEL_V1]]
- [[03_RULES/Rules Index]]
- [[03_RULES/RRT_FREE_AI_ASSISTANCE_POLICY_V1]]
- [[04_PROSPECTS/Prospects Index]]
- [[05_EVIDENCE/Evidence Index]]
- [[06_BENCHMARKS/Benchmarks Index]]
- [[07_SIGNALS/Signals Index]]
- [[08_RED_TEAM/Red Team Index]]
- [[09_VALIDATION/Validation Dashboard]]
- [[09_VALIDATION/Batch 04 National Calibration]]
- [[09_VALIDATION/Scoring Integrity V2]]
- [[09_VALIDATION/Legacy Zero Repair Queue]]
- [[10_REPORTS/Reports Index]]
- [[11_DASHBOARD/README]]
- [[99_CHANGELOG/CHANGELOG]]

## Stato progetto
- North Star prodotto: RRT non e uno scraper, un SEO audit o un report marketing generico; e un Red Team commerciale esterno che deve produrre pochi Opportunity Signal forti, falsificati, auditabili e commercialmente sorprendenti. Vedi [[01_ARCHITECTURE/RRT_PRODUCT_NORTH_STAR_V1]].
- Runtime A1→A9: **VALIDATO** su B04-37; nuovo stato release-safe finale `READY_FOR_HUMAN_REVIEW`, non approvazione automatica.
- Runner end-to-end: `rrt_e2e.sh` + `02_AGENTS/runtime/end_to_end_runner.py` presenti in `main`.
- Auto-repair: **VALIDATO**. Se A4 blocca con `COLLECTION_RESTRICTED`, il runner esegue una sola volta A3 repair e A4/A5 re-audit.
- Isolation guard: i worker reclamano task per `case_id`; eliminata contaminazione tra prospect.
- Caso B04-37: pipeline completa PASS; A8 `WATCHLIST`; A9 `READY`.
- Caso ICO-01: auto-repair eseguito correttamente; esito finale `COLLECTION_RESTRICTED` su D1-D5 per insufficiente acquisizione ufficiale. Questo è uno stato valido, non un errore tecnico.
- Scoring Integrity V2: regression suite 11/11 PASS; individuati 15 zeri legacy da ri-validare.
- Human review: obbligatorio per ogni Opportunity Signal.
- Agent operating model: [[02_AGENTS/RRT_AGENT_OPERATING_MODEL_V1]] autorizza agenti integrati per discovery, entity, comparatori, Red Team e preparazione dossier, ma blocca contatti, evidenze inventate, outreach e Signal senza human gate.
- GitHub: fonte persistente e auditabile.
- Obsidian: interfaccia umana del second brain e knowledge graph.
- Dashboard finale: specificata in [[01_ARCHITECTURE/RRT_FINAL_DASHBOARD_PRODUCT_SPEC_V1]], con categorie/citta/export/report e contatore costi in EUR.
- Vertical configuration: [[01_ARCHITECTURE/RRT_VERTICAL_CONFIGURATION_MODEL_V1]] separa core comune e regole di verticale; dentale e il primo profilo attivo, non il confine del prodotto.
- Dashboard V1 locale: [[11_DASHBOARD/README]], generabile da CSV pre-screen senza API, costi o agent team.
- Roadmap tempi dashboard: [[01_ARCHITECTURE/RRT_DASHBOARD_DELIVERY_ROADMAP_V1]], con pilot in 24 ore dal dataset reale e calibrazione batch in 3-5 giorni.

## Knowledge flow
PUNTO ZERO / PROBLEMA PERCEPITO → PATTERN → BLIND SPOT → EVIDENCE → TARGET → SATURATION → TARGET MATCH → BENCHMARK → FINDING → RED TEAM → COMMERCIAL GATE → SIGNAL → HUMAN REVIEW → VALIDATION.

Vedi [[01_ARCHITECTURE/Knowledge Graph Flow]] per la mappa navigabile.

## Regole chiave
0. Ogni sviluppo deve essere giudicato rispetto alla North Star: aumentare la probabilita di produrre 3-7 Opportunity Signal forti, non ovvi, falsificati e auditabili.
1. Nessun dato inventato.
2. Nessun `NOT_FOUND` senza Target-Specific Deep Scan.
3. Identità e scope prima dello scoring.
4. A4 audita prima di A5.
5. Benchmark congelato prima del gap.
6. Red Team può falsificare il finding.
7. Opportunity Signal ≠ perdita economica dimostrata.
8. Missing ≠ zero.
9. `COLLECTION_RESTRICTED` è uno stato valido e non va forzato.
10. Ogni loop ha stop condition e budget.
11. Cheap-first, escalate-on-uncertainty.
12. Ogni finding deve mantenere la catena prospect → evidence → target → benchmark → red-team → commercial gate → validation.
13. `level = 0` è valido solo con `NOT_FOUND_AFTER_PROTOCOL`.
14. Gli agent team A1→A9 restano `AGENT_TEAM_LOCKED` finche l'utente non autorizza esplicitamente il run e il budget in EUR.
15. Regola aurea: eseguire prima tutto cio che e gratuito, legalmente accessibile e realisticamente utile; mai inventare, mai spendere senza consenso.
16. AI gratuite esterne sono ammesse solo come assistenza non autoritativa su dati pubblici/non sensibili; non sono fonti primarie e non sbloccano A1→A9.
17. La dashboard e una superficie di controllo, non il prodotto: il prodotto e il Signal che sopravvive a entity resolution, benchmark, Red Team e human review.
18. Ogni nuovo verticale deve avere un profilo esplicito; se il profilo e `draft`, puo produrre solo template/pianificazione, non Signal.
19. Gli agenti integrati possono preparare e sfidare evidenze, ma `OPPORTUNITY_SIGNAL`, `VALIDATED_SIGNAL` e outreach approvato sono output human-approved.

## Casi runtime di riferimento
- [[04_PROSPECTS/B04-37 - Studio Dentistico Pietro Leone]]
- [[04_PROSPECTS/ICO-01 - ICO Dental]]

## Obiettivo operativo
Usare [[00_HOME/SECOND_BRAIN]] come pannello quotidiano. Le note prospect diventano l'unità principale di navigazione umana; il runtime continua a vivere in `02_AGENTS/runtime/` senza dipendere da Obsidian.

## Obiettivo prodotto
Dato un nome azienda o una lista prospect, RRT deve ricostruire l'entita reale, osservare cio che il mercato vede online, confrontarlo con competitor comparabili, individuare gap decisionali, falsificarli e consegnare pochi Opportunity Signal che l'imprenditore probabilmente non stava vedendo.

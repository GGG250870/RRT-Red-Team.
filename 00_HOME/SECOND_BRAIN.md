---
type: second-brain-dashboard
project: RRT Red Team
status: active
updated: 2026-08-10
---

# RRT Second Brain

## Come usarlo
Questa nota è il pannello operativo umano. GitHub resta la fonte persistente; Obsidian serve per orientarsi, collegare casi e prendere decisioni.

## Oggi
- Runtime A1→A9: validato.
- B04-37: `READY` dopo A9.
- ICO-01: `COLLECTION_RESTRICTED` dopo auto-repair; non forzare conclusioni.
- Prossimo obiettivo: aumentare il numero di prospect puliti e misurare costo/prospect, reliability e distribuzione degli stati finali.

## Pipeline
[[04_PROSPECTS/Prospects Index]] → [[05_EVIDENCE/Evidence Index]] → [[06_BENCHMARKS/Benchmarks Index]] → [[08_RED_TEAM/Red Team Index]] → [[07_SIGNALS/Signals Index]] → [[09_VALIDATION/Validation Dashboard]] → [[10_REPORTS/Reports Index]]

## Prospect attivi
- [[04_PROSPECTS/B04-37 - Studio Dentistico Pietro Leone]] — pipeline completa, A9 READY.
- [[04_PROSPECTS/ICO-01 - ICO Dental]] — raccolta ufficiale limitata, auto-repair eseguito, stop corretto.

## Stati da leggere subito
- `READY`: QA finale superata.
- `WATCHLIST`: asimmetria debole o non ancora sufficiente per Opportunity Signal Candidate.
- `COLLECTION_RESTRICTED`: la raccolta non consente conclusione affidabile; non equivale ad assenza.
- `UNRESOLVED`: informazione non determinata.
- `NOT_FOUND_AFTER_PROTOCOL`: assenza osservata solo dopo protocollo completo.
- `CONTRADICTORY`: fonti o stati incompatibili.

## Principio operativo
Nessuna nota deve trasformare una limitazione di raccolta in una conclusione commerciale.

## Traccia obbligatoria
Prospect → Evidence → Target → Benchmark → Red Team → Commercial Gate → Validation.

## Runtime
- `rrt_e2e.sh`: launcher umano.
- `02_AGENTS/runtime/end_to_end_runner.py`: orchestrazione A1→A9.
- `02_AGENTS/runtime/state/`: stato locale runtime, non knowledge base.

## Decisioni consolidate
- A4 prima di A5.
- Worker isolati per `case_id`.
- A3 deve persistere `execution_trace` per certificare saturation.
- A5 usa output compatto per evitare truncation.
- A4 block può attivare una sola volta A3 repair → A4/A5 re-run.
- Se dopo repair resta `COLLECTION_RESTRICTED`, il caso si ferma senza forcing.

## Link rapidi
- [[00_HOME/HOME]]
- [[01_ARCHITECTURE/Integrated Knowledge Model]]
- [[01_ARCHITECTURE/RRT_ARCHITECTURE_ECONOMIC_SUSTAINABILITY_AUDIT_V1]]
- [[99_CHANGELOG/CHANGELOG]]

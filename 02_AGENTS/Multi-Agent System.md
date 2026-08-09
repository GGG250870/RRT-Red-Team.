---
type: agents
version: v1
status: active
---

# Multi-Agent System

## Ruoli
- A1 Discovery
- A2 Entity & Scope
- A3 Deep Scan
- A4 Evidence Auditor
- A5 Target Match
- A6 Benchmark
- A7 Red Team
- A8 Commercial Gate
- A9 QA Orchestrator

## Regole di indipendenza
- Nessun agente crea e certifica lo stesso finding.
- Benchmark congelato prima del gap.
- Red Team deve poter falsificare il finding.
- Conflict su entity/scope = hard block.
- In caso di conflitto commerciale prevale lo stato più conservativo.

## Runtime
Il progetto dispone di orchestratore, worker separati, code, SQLite state store e audit log. Il provider LLM live deve essere collegato per avere 9 agenti AI autonomi effettivamente in esecuzione.

## Related
- [[01_ARCHITECTURE/Architecture Overview]]
- [[03_RULES/Rules Index]]

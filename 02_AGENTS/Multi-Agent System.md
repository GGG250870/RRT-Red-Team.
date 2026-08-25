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

## Operating model
Gli agenti sono autorizzati come worker integrati RRT, ma restano vincolati da [[02_AGENTS/RRT_AGENT_OPERATING_MODEL_V1]].

Cluster operativi:
- Discovery / Evidence Collection: A1, A3.
- Entity Resolution: A2.
- Comparator Research: A5, A6.
- Red-Team Challenger: A7.
- Dossier / Report Preparation: A8.
- Human Approval / Release: A9 prepara QA; la certificazione finale resta umana.

## Regole di indipendenza
- Nessun agente crea e certifica lo stesso finding.
- Benchmark congelato prima del gap.
- Red Team deve poter falsificare il finding.
- Conflict su entity/scope = hard block.
- In caso di conflitto commerciale prevale lo stato più conservativo.
- Nessun agente puo contattare aziende, inviare form, aggirare login/paywall/captcha o inventare evidenze.
- Nessun outreach artifact diventa usabile senza human gate esplicito.
- `OPPORTUNITY_SIGNAL` e `VALIDATED_SIGNAL` sono stati human-approved, non output autonomi degli agenti.

## Runtime
Il progetto dispone di orchestratore, worker separati, code, SQLite state store e audit log. Il provider LLM live deve essere collegato per avere 9 agenti AI autonomi effettivamente in esecuzione.

## Related
- [[01_ARCHITECTURE/Architecture Overview]]
- [[02_AGENTS/RRT_AGENT_OPERATING_MODEL_V1]]
- [[03_RULES/Rules Index]]

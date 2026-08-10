---
type: prospect
id: ICO-01
company: ICO Dental
official_domain: https://www.icodental.it/
entity_status: UNRESOLVED
saturation_state: BLOCKED
target_match_state: NOT_RUN
benchmark_state: NOT_RUN
red_team_state: NOT_RUN
signal_state: COLLECTION_RESTRICTED
qa_state: NOT_RUN
human_review: not_applicable
updated: 2026-08-10
---

# ICO-01 — ICO Dental

## Stato sintetico
La pipeline si ferma correttamente a Wave 3 dopo un auto-repair A3 e un re-audit A4.

Esito: `COLLECTION_RESTRICTED` su D1-D5.

## Cosa è successo
1. A1/A2 avviati.
2. A3 Deep Scan non ha acquisito contenuto ufficiale sufficiente.
3. A4 ha certificato `COLLECTION_RESTRICTED` senza inventare assenze.
4. Il runner ha attivato automaticamente `Wave 2R: automatic A3 repair`.
5. Il repair ha tentato D1-D5 con ricerca adattiva sul dominio ufficiale.
6. `Wave 3R` ha confermato che la raccolta restava insufficiente.
7. A5 non è stato forzato.

## Interpretazione corretta
`COLLECTION_RESTRICTED` non significa che ICO non possieda o non comunichi i target cercati. Significa soltanto che il materiale ufficiale non è stato acquisito in misura sufficiente per una conclusione affidabile.

## Lezione di sistema
ICO-01 ha validato il percorso automatico:
A4 BLOCK → A3 REPAIR → A4/A5 RE-AUDIT → STOP se la restrizione persiste.

Il caso dimostra che il runtime sa fermarsi senza trasformare un limite tecnico di raccolta in un finding commerciale.

## Prossima strategia possibile
Usare una modalità di raccolta alternativa solo se coerente con le regole etiche e di provenance. Fino ad allora il caso resta chiuso come `COLLECTION_RESTRICTED`.

## Collegamenti
- [[00_HOME/SECOND_BRAIN]]
- [[04_PROSPECTS/Prospects Index]]
- [[05_EVIDENCE/Evidence Index]]
- [[09_VALIDATION/Validation Dashboard]]

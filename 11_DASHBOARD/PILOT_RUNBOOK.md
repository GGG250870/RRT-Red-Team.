# RRT Dashboard Pilot Runbook

## Obiettivo

Eseguire un pilot gratuito e legal-safe entro 24 ore dal dataset reale, senza agent team e senza dati inventati.

## Input minimo

Usare uno dei template:
- `11_DASHBOARD/templates/ristorazione_pilot_template.csv`
- `11_DASHBOARD/templates/pmi_pilot_template.csv`

Colonne prioritarie:
- `company`
- `domain`
- `city`
- `vertical`
- `target_segment`
- `phone`
- `mobile_phone`
- `email`
- `address`
- `google_url`
- `review_portal_url`
- `vat_id`

## Sequenza

1. Controllare readiness del CSV.

```bash
python3 11_DASHBOARD/pilot_readiness.py INPUT.csv --min-rows 30 --output-json 11_DASHBOARD/out/pilot_readiness.json
```

2. Eseguire pre-screen deterministico.

```bash
python3 00_PRE_SCREEN/pre_screen.py INPUT.csv 11_DASHBOARD/out/pilot_prescreen.csv
```

3. Generare dashboard con enrichment pubblico gratuito.

```bash
zsh rrt_dashboard.sh 11_DASHBOARD/out/pilot_prescreen.csv 11_DASHBOARD/out/pilot
```

4. Aprire `11_DASHBOARD/out/pilot/index.html`.

5. Verificare:
- `cost_ledger.csv`;
- `prospects.xlsx`;
- `shortlist.csv`;
- `reports/`;
- `guided_reports/`;
- `full_rrt_locked/`.

## SLA

- Readiness CSV: meno di 1 minuto.
- Pre-screen 30-50 prospect: 5-15 minuti, dipendente da rete e siti.
- Dashboard/export: meno di 2 minuti dopo input arricchito.
- Prima shortlist utile: entro 24 ore dal dataset reale.

## Stati

- `READY`: pilot avviabile.
- `USABLE_WITH_GAPS`: dashboard avviabile, ma interpretare shortlist con cautela.
- `NOT_READY`: correggere blockers prima di usare l'output.

## Guardrail

- Nessun agent team.
- Nessun dato inventato.
- Nessun portale usato come dominio ufficiale.
- Nessun costo senza consenso.
- Nessun Opportunity Signal senza A1-A9, QA e Human Review.

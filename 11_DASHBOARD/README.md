# RRT Dashboard V1

Dashboard locale zero-LLM per trasformare un CSV di pre-screen in output immediatamente utilizzabili.

## Regola aurea

Prima usa tutto cio che e gratuito, legalmente accessibile e realisticamente utile. Non inventa dati e non avvia gli agent team.

## Uso

```bash
python3 11_DASHBOARD/dashboard.py 00_PRE_SCREEN/batch_dentale_results.csv 11_DASHBOARD/out/dentale
```

Con enrichment online gratuito/legal-safe prima della dashboard:

```bash
python3 11_DASHBOARD/enrich_public_sources.py 00_PRE_SCREEN/batch_dentale_results.csv 11_DASHBOARD/out/dentale/enriched_input.csv
python3 11_DASHBOARD/dashboard.py 11_DASHBOARD/out/dentale/enriched_input.csv 11_DASHBOARD/out/dentale
```

Oppure wrapper:

```bash
zsh rrt_dashboard.sh 00_PRE_SCREEN/batch_dentale_results.csv 11_DASHBOARD/out/dentale
```

## Pilot reale

Prima di lanciare un pilot su dataset reale, usa il readiness check:

```bash
python3 11_DASHBOARD/pilot_readiness.py INPUT.csv --min-rows 30 --output-json 11_DASHBOARD/out/pilot_readiness.json
```

Template disponibili:
- `11_DASHBOARD/templates/ristorazione_pilot_template.csv`
- `11_DASHBOARD/templates/pmi_pilot_template.csv`

Runbook: `11_DASHBOARD/PILOT_RUNBOOK.md`.

## Review intelligence

Google Maps e TripAdvisor possono essere usati come fonti primarie di reputazione solo tramite:
- link di verifica/search generati dalla dashboard;
- API ufficiali con consenso, chiavi e cost ledger;
- export autorizzati/import manuali.

Non viene fatto scraping massivo di nomi, indirizzi o recensioni.

Per aggregare export autorizzati:

```bash
python3 11_DASHBOARD/review_intelligence.py reviews_export.csv review_summary.csv --output-json review_summary.json
```

Per verificare che i link review letti manualmente appartengano davvero alla stessa azienda/citta:

```bash
python3 11_DASHBOARD/entity_resolution.py seed.csv resolved.csv --manual-links-csv verified_links.csv
```

Stati prodotti: `MATCH_CONFIRMED`, `AMBIGUOUS_REVIEW_LINK`, `OUT_OF_AREA_OR_ENTITY_CONFLICT`, `ENTITY_CONFLICT`, `NEEDS_REVIEW_LINKS`. Il costo resta `EUR 0.0000` e il team agent resta bloccato.

Output:
- `index.html`: dashboard apribile nel browser;
- `dashboard_payload.json`: payload standardizzato;
- `cost_ledger.json`: ledger costi e consenso machine-readable;
- `cost_ledger.csv`: ledger costi editabile;
- `shortlist.csv`: soli `SHORTLIST` ed `ESCALATE`;
- `prospects.xlsx`: workbook editabile con prospect, summary e cost ledger;
- `batch_report.md`: report batch editabile;
- `batch_report.docx`: report batch editabile in Word;
- `print_report.html`: versione stampabile/esportabile PDF dal browser;
- `reports/*.md`: Passaggio 1, report rapidi per singolo imprenditore selezionabile;
- `guided_reports/*.md`: Passaggio 2, report opportunita guidati, non-agentici;
- `full_rrt_locked/*.md`: Passaggio 3, template report completo A1-A9 bloccato fino a consenso e budget.

CSV, XLSX e report singoli includono sempre il blocco contatti: telefono, cellulare/WhatsApp quando disponibile, email e indirizzo. I campi non trovati restano marcati come `NON_TROVATO`/vuoti: non vengono mai inventati.

La lista operativa HTML mostra i contatti principali e, per ogni prospect in `SHORTLIST` o `ESCALATE`, i link diretti ai tre passaggi report.
Il `Cost & Consent Panel` mostra operazioni gratuite completate, operazioni bloccate, costo consuntivo e consenso richiesto prima di qualunque report A1-A9.

## Stato costi

La dashboard V1 usa input gia disponibili, fonti pubbliche gratuite quando accessibili e genera output locali:

- costo operativo: `EUR 0.0000`;
- ledger costi esportato in `cost_ledger.json`, `cost_ledger.csv` e foglio `Cost Ledger` nell'XLSX;
- agent team: `AGENT_TEAM_LOCKED`;
- nessuna chiamata API a pagamento;
- nessun report A1-A9.

## Tre passaggi crescenti per imprenditore

Per ogni prospect in `SHORTLIST` o `ESCALATE` la dashboard produce:

1. Passaggio 1 - Report rapido
   - lettura zero-LLM;
   - telefono, cellulare/WhatsApp, email e indirizzo;
   - coverage fonti;
   - score spiegabili;
   - prossima azione.

2. Passaggio 2 - Report opportunita guidato
   - ipotesi di lavoro non-agentica;
   - telefono, cellulare/WhatsApp, email e indirizzo;
   - controlli gratuiti mancanti;
   - domande da verificare prima di spendere;
   - nessun Opportunity Signal certificato.

3. Passaggio 3 - Report A1-A9 locked
   - template di richiesta dossier completo;
   - telefono, cellulare/WhatsApp, email e indirizzo;
   - stato `AGENT_TEAM_LOCKED`;
   - richiede consenso esplicito e budget EUR prima del run.

## Enrichment pubblico gratuito

`enrich_public_sources.py` puo accedere online a informazioni disponibili, gratuite e legalmente estraibili:

- sito ufficiale;
- telefono, cellulare/WhatsApp, email e indirizzo esposti su sito ufficiale o dati strutturati pubblici;
- link social pubblici esposti dal sito;
- link a portali recensioni esposti dal sito;
- link a bilanci/documenti finanziari pubblici esposti dal sito;
- URL di ricerca manuale per Google/Maps e Registro Imprese.
- per ristorazione, URL di ricerca manuale su TripAdvisor e altri portali review rilevanti per target.

Guardrail:
- non aggira login, paywall, CAPTCHA o blocchi;
- rispetta `robots.txt` quando disponibile;
- non usa Google scraping come sostituto di API ufficiali;
- non inventa rating, recensioni o dati di bilancio;
- salva `source_refs_json` con provenance e stati di accesso.

## Target ristorazione

La dashboard supporta `target_segment` per separare la ristorazione in mercati operativi diversi:

- `fine_dining`
- `pizzeria`
- `trattoria_osteria`
- `sushi_etnico`
- `delivery_asporto`
- `eventi_catering`
- `enoteca_wine_bar`
- `bar_cafe`
- `ristorazione_generic`

Esempio:

```bash
zsh rrt_build_and_prescreen.sh 50 "Milano,Roma" ristorazione pizzeria
zsh rrt_dashboard.sh 00_PRE_SCREEN/batch_ristorazione_pizzeria_results.csv 11_DASHBOARD/out/ristorazione_pizzeria
```

## Flusso consigliato

1. Genera o importa un CSV con domini ufficiali.
2. Esegui `00_PRE_SCREEN/pre_screen.py`.
3. Verifica entita e link review con `entity_resolution.py` quando lavori su liste generate per citta/categoria.
4. Genera la dashboard.
5. Esegui enrichment pubblico gratuito se vuoi massimizzare le fonti online.
6. Usa filtri categoria/citta/decisione per selezionare prospect.
7. Completa manualmente Google, recensioni, social e bilanci pubblici dove mancanti o non estraibili.
8. Solo dopo selezione umana valuta un report guidato o A1-A9 con consenso e budget.

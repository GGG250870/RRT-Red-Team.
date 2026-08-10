# RRT PRE-SCREEN ENGINE

Obiettivo: scremare grandi gruppi di prospect prima di usare gli agenti A1→A9.

## Principio
Nessuna chiamata OpenAI in questa fase.

Pipeline:

`MARKET LIST → HARD FILTER → WEB SIGNAL FILTER → CHEAP SCORE → REJECT / SHORTLIST / ESCALATE → A1→A9`

## Input CSV
Colonne consigliate:

- `company`
- `domain`
- `city`
- `vertical`

Sono accettati anche `name`, `website`, `official_domain` come alias.

## Output CSV

- company
- domain
- city
- vertical
- website_live
- fetch_state
- pages_found
- D1_hits
- D2_hits
- D3_hits
- D4_hits
- D5_hits
- contactability
- observed_dimensions
- preliminary_score
- decision

## Dimensioni dentale v1

- D1: paura / ansia / sedazione / dolore / anestesia
- D2: prezzo / costo / finanziamento / rate / pagamenti
- D3: implantologia / TAC / 3D / scanner / chirurgia guidata / team / garanzia
- D4: carico immediato / 24h / un giorno / stessa giornata / All-on-4
- D5: perché scegliere / vantaggi / testimonianze / recensioni / FAQ / esperienza

## Decisione v1

- `REJECT`: sito non acquisibile oppure score insufficiente
- `SHORTLIST`: score >= 45 e almeno 2 dimensioni osservate
- `ESCALATE`: score >= 70 e almeno 3 dimensioni osservate

Lo score è solo un filtro operativo. Non rappresenta un Opportunity Signal e non sostituisce A1→A9.

## Uso

```bash
python3 00_PRE_SCREEN/pre_screen.py 00_PRE_SCREEN/prospects_example.csv 00_PRE_SCREEN/output.csv
```

Poi filtrare `decision` su `SHORTLIST` e `ESCALATE`.

Solo questi prospect devono entrare, salvo eccezione manuale, nel runtime costoso:

```bash
zsh rrt_e2e.sh CASE-ID "Company" https://domain.it/
```

## Guardrail

1. Missing non significa zero.
2. `REJECT` è solo esclusione dal batch costoso, non giudizio commerciale definitivo.
3. `fetch_state != OK` non autorizza a concludere che un target non esista.
4. Il pre-screen non produce benchmark, finding, signal o claim economici.
5. Le soglie sono euristiche iniziali e vanno calibrate sui batch reali.
6. Il motore usa solo librerie Python standard e HTTP pubblico; nessuna API LLM.

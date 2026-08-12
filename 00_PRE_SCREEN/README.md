# RRT PRE-SCREEN ENGINE

Obiettivo: scremare grandi gruppi di prospect prima di usare gli agenti A1→A9.

## Principio
Nessuna chiamata OpenAI in questa fase.

Pipeline:

`PUBLIC DISCOVERY → HARD FILTER → WEB SIGNAL FILTER → CHEAP SCORE → REJECT / COLLECTION_RESTRICTED / SHORTLIST / ESCALATE → A1→A9`

## Modalità batch gratuita

Per creare e scremare un batch dentale in un solo comando:

```bash
zsh rrt_build_and_prescreen.sh 100
```

Il comando:
1. usa ricerche web pubbliche senza API key per costruire un CSV di prospect;
2. deduplica i record-source per profilo/entity del portale;
3. esegue il pre-screen deterministico zero-LLM;
4. produce i risultati completi;
5. crea un CSV separato con soli `SHORTLIST` e `ESCALATE`.

File predefiniti:
- `00_PRE_SCREEN/batch_dentale.csv`
- `00_PRE_SCREEN/batch_dentale_results.csv`
- `00_PRE_SCREEN/batch_dentale_shortlist.csv`

La discovery gratuita è volutamente sostituibile: `build_batch.py` è separato da `pre_screen.py`. Se una fonte pubblica cambia o limita l'accesso, il motore di scoring non va modificato.

Nota: i profili di portale non sono domini ufficiali. Quando `build_batch.py` scopre una scheda su MioDottore/Dentisti-Italia/DocDental ma non risolve un dominio ufficiale, lascia `domain` vuoto e imposta `official_domain_state = UNRESOLVED`. Il pre-screen deve fermare questi record come `COLLECTION_RESTRICTED`, non calcolare lo score sul dominio del portale.

Primary discovery release-safe corrente: MioDottore. Dentisti-Italia e DocDental restano nella backlog sorgenti ma sono disabilitati come primary discovery finché il parser profili non è validato contro righe di navigazione.

Il targeting geografico resta city-first nella sorgente validata corrente. Quartieri o zone sono accettati come input, ma se il portale non li supporta il builder deve restituire `DISCOVERY_EMPTY` invece di allargare silenziosamente o usare fonti sporche.

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
- source_url
- official_domain_state
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
- `COLLECTION_RESTRICTED`: dominio presente ma sito non acquisibile; non equivale a prospect debole.
- `REJECT`: score insufficiente o assenza di dominio utile.
- `SHORTLIST`: score >= 45 e almeno 2 dimensioni osservate.
- `ESCALATE`: score >= 70 e almeno 3 dimensioni osservate.

Lo score è solo un filtro operativo. Non rappresenta un Opportunity Signal e non sostituisce A1→A9.

## Uso manuale

```bash
python3 00_PRE_SCREEN/pre_screen.py 00_PRE_SCREEN/prospects_example.csv 00_PRE_SCREEN/output.csv
```

Solo `SHORTLIST` e `ESCALATE` devono entrare normalmente nel runtime costoso:

```bash
zsh rrt_e2e.sh CASE-ID "Company" https://domain.it/
```

## Guardrail
1. Missing non significa zero.
2. `REJECT` è solo esclusione dal batch costoso, non giudizio commerciale definitivo.
3. `fetch_state != OK` non autorizza a concludere che un target non esista.
4. `COLLECTION_RESTRICTED` resta separato da `REJECT`.
5. Il pre-screen non produce benchmark, finding, signal o claim economici.
6. Le soglie sono euristiche iniziali e vanno calibrate sui batch reali.
7. Il motore usa solo librerie Python standard e HTTP pubblico; nessuna API LLM.
8. Nessuna chiamata A1→A9 viene eseguita automaticamente dal batch gratuito.
9. Un dominio di portale non può essere usato come dominio ufficiale del prospect.

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

Per una categoria esplicita:

```bash
zsh rrt_build_and_prescreen.sh 20 "Milano,Roma" dentale
zsh rrt_build_and_prescreen.sh 20 "Milano,Roma" ristorazione
zsh rrt_build_and_prescreen.sh 20 "Milano,Roma" ristorazione pizzeria
zsh rrt_build_and_prescreen.sh 20 "Milano,Roma" pmi
```

Il comando:
1. usa ricerche web pubbliche senza API key per costruire un CSV di prospect;
2. deduplica i record-source per profilo/entity del portale;
3. esegue il pre-screen deterministico zero-LLM;
4. produce i risultati completi;
5. crea un CSV separato con soli `SHORTLIST` e `ESCALATE`.

File predefiniti:
- `00_PRE_SCREEN/batch_<vertical>.csv`
- `00_PRE_SCREEN/batch_<vertical>_results.csv`
- `00_PRE_SCREEN/batch_<vertical>_shortlist.csv`
- `00_PRE_SCREEN/batch_<vertical>_<target_segment>.csv` quando viene passato un target segment.

La discovery gratuita è volutamente sostituibile: `build_batch.py` è separato da `pre_screen.py`. Se una fonte pubblica cambia o limita l'accesso, il motore di scoring non va modificato.

Nota: i profili di portale non sono domini ufficiali. Quando `build_batch.py` scopre una scheda su MioDottore/Dentisti-Italia/DocDental ma non risolve un dominio ufficiale, lascia `domain` vuoto e imposta `official_domain_state = UNRESOLVED`. Il pre-screen deve fermare questi record come `COLLECTION_RESTRICTED`, non calcolare lo score sul dominio del portale.

Primary discovery release-safe corrente:
- `dentale`: MioDottore.
- `ristorazione`: OpenStreetMap/Overpass open data per estrazione city-first; TripAdvisor/TheFork/Google restano intelligence/provenance, non scraping.
- `pmi`: OpenStreetMap/Overpass best effort per aziende/craft/office/industrial; dimensione fino a 200 persone resta da validare con fonti esterne.
- `hospitality`: OpenStreetMap/Overpass open data per strutture ricettive.
- `benessere_estetica`: OpenStreetMap/Overpass open data per beauty, hairdresser, spa, massage.
- `servizi_casa`: OpenStreetMap/Overpass open data per shop/craft rilevanti.
- `formazione`: OpenStreetMap/Overpass open data per scuole, corsi e istituzioni formative.
- `generic`: nessuna fonte automatica; usare CSV manuale con domini ufficiali.

OpenStreetMap/Overpass viene usato con limiti piccoli, User-Agent identificativo e provenance. Nominatim viene usato solo per risolvere la bounding box della citta indicata, rispettando il limite di richiesta. Non e una fonte completa di mercato: se mancano sito, telefono o email, il record resta parziale.
Gli endpoint Overpass pubblici possono essere lenti o temporaneamente indisponibili. In quel caso il builder restituisce `DISCOVERY_EMPTY` o batch parziale: riprovare piu tardi o usare CSV/manual seed senza forzare risultati.

Primary intelligence per tutte le categorie:
- Google Business Profile, Google Reviews e Google Maps come fonte primaria di reputazione/local presence.
- Portali recensioni verticali e generalisti rilevanti per categoria.
- Social ufficiali e profili pubblici: Facebook, Instagram, LinkedIn, TikTok dove pertinenti.
- Bilanci pubblici e informazioni societarie: Registro Imprese, Telemaco/InfoCamere e documenti economico-finanziari pubblicati sul sito ufficiale dell'azienda.

Queste fonti sono primarie per segnali, reputazione, contesto e solidita dell'impresa. Non sono automaticamente domini ufficiali del prospect e non autorizzano claim economici senza pipeline RRT completa.

Per `ristorazione`, TripAdvisor e altri portali recensioni sono previsti come fonti di intelligence per target:
- `fine_dining`: TripAdvisor, TheFork, Michelin, Gambero Rosso.
- `pizzeria`: TripAdvisor, TheFork, RestaurantGuru, PagineGialle.
- `trattoria_osteria`: TripAdvisor, RestaurantGuru, TheFork, PagineGialle.
- `sushi_etnico`: TripAdvisor, TheFork, RestaurantGuru.
- `delivery_asporto`: TripAdvisor, TheFork, RestaurantGuru.
- `eventi_catering`: TripAdvisor, TheFork, PagineGialle.
- `enoteca_wine_bar`: TripAdvisor, TheFork, Gambero Rosso.
- `bar_cafe`: TripAdvisor, RestaurantGuru, PagineGialle.

Questi portali possono essere usati come review intelligence e URL di ricerca/provenance. Non vengono usati come dominio ufficiale e non vengono scraperati aggirando blocchi o API ufficiali.

Dentisti-Italia, DocDental, TheFork, TripAdvisor, Booking, Treatwell, ProntoPro e Habitissimo restano nella backlog sorgenti ma sono disabilitati come primary discovery finché il parser profili e la risoluzione dominio ufficiale non sono validati contro righe di navigazione.

Il targeting geografico resta city-first nella sorgente validata corrente. Quartieri o zone sono accettati come input, ma se il portale non li supporta il builder deve restituire `DISCOVERY_EMPTY` invece di allargare silenziosamente o usare fonti sporche.

## Input CSV
Colonne consigliate:
- `company`
- `domain`
- `city`
- `vertical`
- `target_segment`

Sono accettati anche `name`, `website`, `official_domain` come alias.

## Output CSV
- company
- domain
- source_url
- official_domain_state
- city
- vertical
- target_segment
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

## Dimensioni ristorazione v1
- D1: prenotazione / contatto / tavolo
- D2: menu / prezzi / degustazione / asporto / delivery
- D3: cucina / chef / ingredienti / territorio / cantina
- D4: orari / pranzo / cena / giorni di apertura
- D5: recensioni / guide / storia / esperienza / gallery

## Dimensioni PMI v1
Target: piccole e medie imprese fino a circa 200 persone, con uso consigliato su CSV manuali che riportano domini ufficiali.

- D1: contatto / preventivo / consulenza
- D2: servizi / soluzioni / prodotti / catalogo
- D3: certificazioni / referenze / clienti / case study
- D4: team / sede / produzione / laboratorio / stabilimento
- D5: innovazione / digitale / sostenibilità / export / assistenza

## Nicchie interessanti v1
Queste categorie sono utili perché hanno segnali pubblici leggibili, valore commerciale potenziale e frequenti gap di comunicazione sul sito:

- `hospitality`: hotel, B&B, agriturismi e strutture ricettive.
- `benessere_estetica`: centri estetici, spa, wellness, beauty, parrucchieri/barber.
- `servizi_casa`: impianti, serramenti, fotovoltaico, edilizia e ristrutturazioni.
- `formazione`: corsi, academy, scuole professionali e training.
- `pmi`: aziende B2B/locali fino a circa 200 persone.

Le dimensioni sono profili zero-LLM per filtro operativo. Non sono confrontabili tra categorie come metriche statistiche e non producono Opportunity Signal.

## Decisione v1
- `COLLECTION_RESTRICTED`: dominio presente ma sito non acquisibile; non equivale a prospect debole.
- `REJECT`: score insufficiente o assenza di dominio utile.
- `SHORTLIST`: score >= 45 e almeno 2 dimensioni osservate, oppure almeno 1 indicatore high-value.
- `ESCALATE`: score >= 70 e almeno 3 dimensioni osservate, con eventuale gate high-value definito dal profilo categoria.

Lo score è solo un filtro operativo. Non rappresenta un Opportunity Signal e non sostituisce A1→A9.

## Uso manuale

Per estrarre una lista iniziale dalla citta indicata:

```bash
zsh rrt_build_and_prescreen.sh 50 "Milano" ristorazione pizzeria
zsh rrt_dashboard.sh 00_PRE_SCREEN/batch_ristorazione_pizzeria_results.csv 11_DASHBOARD/out/milano_pizzeria
```

```bash
python3 00_PRE_SCREEN/pre_screen.py 00_PRE_SCREEN/prospects_example.csv 00_PRE_SCREEN/output.csv
python3 00_PRE_SCREEN/pre_screen.py 00_PRE_SCREEN/prospects_ristorazione_example.csv 00_PRE_SCREEN/output_ristorazione.csv
python3 00_PRE_SCREEN/pre_screen.py 00_PRE_SCREEN/prospects_pmi_example.csv 00_PRE_SCREEN/output_pmi.csv
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
10. Ogni categoria deve avere profilo esplicito o fallback `generic`; nuovi verticali vanno calibrati prima di essere dichiarati release-safe.

---
type: reusable-gate-checklist
version: v1
status: active
category: dentale
market: Savona
updated: 2026-08-17
---

# RRT Dental Savona Discovery-To-First-Visit Gate V1

## Purpose

Applicare agli altri candidati dentali Savona lo stesso gate che ha prodotto il Signal Zecca-Cohen:

> Google profile -> sito ufficiale -> richiesta prima visita.

Questo gate non valuta qualita clinica. Valuta continuita decisionale esterna per un potenziale paziente.

## Required inputs

Per ogni studio:

- nome pubblico;
- ragione sociale se reperibile;
- indirizzo;
- profilo Google pubblico;
- sito ufficiale;
- telefono/email;
- social pubblici;
- eventuale booking/form/request CTA;
- 1-3 comparator locali comparabili.

## Evidence checklist

### A. Entity resolution

- [ ] Il nome pubblico corrisponde allo studio giusto.
- [ ] L'indirizzo e coerente tra Google, sito e directory.
- [ ] Il sito ufficiale e identificato senza ambiguita.
- [ ] Eventuali societa collegate o domini alternativi sono tracciati.
- [ ] Conflitti marcati come `ENTITY_CONFLICT`, non ignorati.

### B. Google profile

- [ ] Profilo Google presente.
- [ ] Telefono visibile.
- [ ] Indirizzo visibile.
- [ ] Rating/review count registrati come segnali pubblici, non qualita clinica.
- [ ] Sito web collegato nel profilo.
- [ ] Se assente, annotare label osservata: es. `Aggiungi sito web`.
- [ ] Instagram/social o altri link presenti.
- [ ] Screenshot o data osservazione.

### C. Official site mobile path

- [ ] Il sito si apre da mobile.
- [ ] CTA primaria visibile above/before long scroll.
- [ ] Telefono cliccabile.
- [ ] Email cliccabile.
- [ ] Form richiesta visita presente.
- [ ] Online booking presente.
- [ ] Messaggio WhatsApp o canale guidato presente.
- [ ] Footer/branding/piattaforma annotati solo come contesto, non finding principale.

### D. First-visit continuity

- [ ] Da Google si arriva al sito ufficiale in un click.
- [ ] Dal sito si capisce cosa fare per chiedere una prima visita.
- [ ] Il percorso non richiede interpretazioni eccessive.
- [ ] Esiste una CTA esplicita per nuovo paziente o appuntamento.
- [ ] Se workflow phone-first, verificare se la scelta e coerente e ben segnalata.

### E. Comparator path

Per ogni comparator:

- [ ] Nome e indirizzo.
- [ ] Perche e comparabile.
- [ ] CTA/booking/form/message action osservata.
- [ ] Review count/rating solo come segnale pubblico.
- [ ] Nessun claim clinico comparativo.

## Finding decision rules

### NO_SIGNAL

Usare se:

- profilo Google linka sito ufficiale;
- sito mobile ha CTA chiara;
- booking/form/call flow e comparabile o migliore;
- gap non e decisionale.

### WATCHLIST

Usare se:

- c'e attrito, ma non e chiaro se incida su una scelta;
- comparator non sono abbastanza comparabili;
- dati temporali incompleti;
- possibile workflow referral-led intenzionale non falsificato.

### OPPORTUNITY_SIGNAL_CANDIDATE

Usare se:

- il gap Google -> sito -> prima visita e osservabile;
- almeno un comparator locale rende la prima azione piu chiara;
- il Red Team non falsifica il finding;
- mancano ancora screenshot completi, secondo controllo o human review.

### OPPORTUNITY_SIGNAL

Usare solo se:

- entity resolution e solida;
- evidence pack completo;
- comparator fit difendibile;
- Red Team `SURVIVES`;
- claim formulato senza overclaim clinici/economici;
- human review approva;
- confidenza claim attribution >= 98%.

## Red Team questions

Ogni candidate deve rispondere:

1. Il sito o booking esiste ma e stato perso nella scansione?
2. Il workflow phone-first e intenzionale e ben comunicato?
3. Il competitor e davvero comparabile o solo digitalmente piu maturo?
4. Il gap puo influenzare una decisione o e solo estetico?
5. Stiamo confondendo assenza di evidenza con evidenza di assenza?
6. Il finding richiede claim economici non dimostrabili?
7. Il messaggio al cliente resta rispettoso e non clinico?

## Safe client wording

> Abbiamo osservato il percorso pubblico con cui un potenziale paziente trova lo studio e prova a chiedere una prima visita. Ci sono gia segnali positivi; il punto e rendere piu continuo e guidato il passaggio da Google al primo contatto.

## Unsafe wording

Non usare:

- "state perdendo pazienti";
- "il sito e vecchio";
- "i competitor sono migliori";
- "la vostra qualita clinica non emerge";
- "avete poche recensioni";
- "dovete usare booking online".

## Output required per candidate

- Evidence pack.
- Signal candidate note or NO_SIGNAL note.
- Red Team review.
- Client-facing mini-audit only if candidate survives.
- First-contact script only if human-approved for outreach.

## Related

- [[04_PROSPECTS/SAV-DENT-01 - Studio Odontoiatrico Zecca-Cohen]]
- [[07_SIGNALS/SAV-DENT-01 - Zecca-Cohen Opportunity Signal Dossier]]
- [[08_RED_TEAM/SAV-DENT-01 - Zecca-Cohen Red Team Review]]

---
type: red-team-review
case: SAV-DENT-01
prospect: Studio Odontoiatrico Zecca-Cohen
finding: Google profile -> official site -> first visit continuity gap
status: SURVIVES
updated: 2026-08-17
---

# SAV-DENT-01 — Zecca-Cohen Red Team Review

## Finding attacked

> Nel percorso pubblico osservato, un potenziale paziente che parte dal profilo Google non trova continuita immediata verso il sito ufficiale e, sul sito mobile, non trova un percorso guidato di richiesta prima visita o booking online.

## Attack 1 — "Il telefono basta"

Obiezione:

Lo studio espone telefono e email; per uno studio odontoiatrico il contatto telefonico puo essere sufficiente.

Esito:

**PARTIAL.**

Il telefono e una forma valida di conversione. Tuttavia il Signal non sostiene che il telefono sia sbagliato. Sostiene che il percorso Google -> sito -> prima visita e meno guidato di comparator locali con CTA/booking.

## Attack 2 — "Workflow referral-led intenzionale"

Obiezione:

Lo studio potrebbe lavorare prevalentemente su referral, passaparola o pazienti specialistici, quindi un booking online potrebbe non essere desiderato.

Esito:

**PARTIAL.**

Possibile. Il finding viene ristretto: non "manca booking quindi e sbagliato", ma "manca continuita guidata per il paziente che scopre lo studio esternamente".

## Attack 3 — "Sito vecchio non significa gap commerciale"

Obiezione:

Il branding Wix e il footer `©2014` non dimostrano un problema commerciale.

Esito:

**ACCEPTED.**

Questo non e il finding. Il sito datato e solo contesto secondario. Il Signal certificato e la continuita di scoperta e primo contatto.

## Attack 4 — "Comparatori non clinicamente comparabili"

Obiezione:

Studio Mantovani e Dr. Martinengo non dimostrano superiorita clinica o stessa specializzazione.

Esito:

**ACCEPTED WITH SCOPE.**

I comparator sono usati solo come percorsi pubblici locali di prima azione. Non sono usati per claim clinici.

## Attack 5 — "Google profile potrebbe cambiare"

Obiezione:

Il profilo Google puo essere aggiornato in qualsiasi momento.

Esito:

**ACCEPTED AS TEMPORAL CAVEAT.**

Il Signal resta valido alla data osservata `2026-08-17`. Prima del contatto commerciale va riaperto il profilo e verificato se `Aggiungi sito web` e ancora presente.

## Verdict

**SURVIVES**

## Surviving formulation

Lo studio ha segnali pubblici positivi e canali di contatto diretti, ma alla data osservata il percorso Google profile -> sito ufficiale -> richiesta guidata di prima visita presenta una discontinuita pratica rispetto a comparator locali con CTA/booking piu espliciti. Questa e un'opportunita di riduzione attrito nel primo contatto, non una critica clinica.

## Residual caveats

- Verificare di nuovo profilo Google prima dell'outreach.
- Non usare il finding per dichiarare perdita pazienti.
- Non suggerire booking online come obbligatorio se lo studio preferisce workflow telefonico.
- Non trasformare branding Wix/footer in claim principale.

## Related

- [[07_SIGNALS/SAV-DENT-01 - Zecca-Cohen Opportunity Signal Dossier]]
- [[05_EVIDENCE/SAV-DENT-01 - Zecca-Cohen Evidence Pack]]

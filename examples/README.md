# DrumAPP · Examples

Set di esempio importabili nell'app via il bottone **IMPORT**. Ognuno è pensato per dimostrare un **genere diverso** e le feature Pro che lo caratterizzano.

---

## 📀 Demo disponibili

### Generi moderni
| File | Genere | BPM | Feel |
|---|---|---|---|
| [`demo-house.json`](demo-house.json)     | House / Techno      | 124 | 4/4 dritto, build + drop |
| [`demo-trap.json`](demo-trap.json)       | Trap / Hip-Hop      | 140 | 808 profondo + ratchet hats |
| [`demo-boombap.json`](demo-boombap.json) | Boom Bap '90s       |  90 | Swing alto, feel "lazy" Dilla |
| [`demo-dnb.json`](demo-dnb.json)         | DNB / Amen Break    | 170 | Breakbeat jungle, ghost snare |
| [`demo-makesomenoise.json`](demo-makesomenoise.json) | NYC Hip-Hop 2011 style | 105 | Kick doppio + rim shaker + cowbell |
| [`demo-ukhardcore.json`](demo-ukhardcore.json) | UK Breakbeat Hardcore '92-'93 | 140 | Pre-jungle, 4/4 rave + Amen choppato |
| [`demo-onedrop.json`](demo-onedrop.json) | Dub / Reggae One-Drop | 80  | ★ Beat sul 3, filosofia invertita |

### Break storici (ricostruzioni ritmiche)
| File | Ispirato a | Anno | BPM | Perché è iconico |
|---|---|---|---|---|
| [`demo-billiejean.json`](demo-billiejean.json)     | Billie Jean (MJ)            | 1982 | 117 | Linn LM-1 metronomica, kick sincopato |
| [`demo-funkydrummer.json`](demo-funkydrummer.json) | Funky Drummer (J. Brown)    | 1970 | 103 | Break più campionato della storia — ghost + open hat |
| [`demo-levee.json`](demo-levee.json)               | When the Levee Breaks (LZ)  | 1971 |  72 | Bonham massiccio, half-time, decay lunghi |
| [`demo-apache.json`](demo-apache.json)             | Apache (Incredible Bongo B.)| 1973 | 112 | Il break che Kool Herc mixava al Bronx = genesi hip-hop |
| [`demo-impeach.json`](demo-impeach.json)           | Impeach the President (Honey Drippers) | 1973 | 100 | Intro drum-solo iconica, pulizia chirurgica |
| [`demo-ashleysroachclip.json`](demo-ashleysroachclip.json) | Ashley's Roachclip (Soul Searchers) | 1974 | 100 | Funky con open hat signature |
| [`demo-synthsub.json`](demo-synthsub.json)         | Synthetic Substitution (Melvin Bliss) | 1973 | 91 | Break sparso che lascia spazio alla voce |

> ⚠️ **Disclaimer per i break storici**: questi file ricostruiscono lo *scheletro ritmico* (kick/snare/percussion placement) dei brani indicati. **Non** riproducono le melodie, voci, basso, arrangement, sample o timbri specifici, che restano protetti dal copyright dei rispettivi autori/editori. La drum programming è grammatica musicale generale.

Tutte usano gli stessi 8 suoni sintetizzati di DrumAPP — cambia solo come vengono **programmati** (pattern, velocity, ratchet, pan, pitch). Sono la dimostrazione migliore di quanto il *programming* conti più del *sample* in una drum machine.

---

## 🎛 Come ogni genere sfrutta feature diverse

| Feature             | House | Trap  | Boom Bap | DNB |
|---------------------|:-----:|:-----:|:--------:|:---:|
| BPM                 | 124   | 140   | **90**   | **170** |
| Swing               | 8%    | 0     | **52%** ★ | 0   |
| Humanize            | on    | off   | **on** ★  | off |
| Kick four-on-floor  | ✅    | ❌    | ❌       | ❌  |
| Kick 808 profondo   | -2 st | **-5 st** ★ | -2 st | -3 st |
| Ratchet hi-hat      | fill  | **ovunque** ★ | -      | -   |
| Ghost snare         | -     | -     | -        | **★ firma Amen** |
| Snare roll 4×       | -     | drop  | -        | **drop** ★ |
| Clap layered snare  | -     | ✅    | muted    | muted |
| Cowbell             | ✅ R60 | muted | muted    | muted |
| Pan stereo          | largo | medio | medio    | medio |

★ = feature caratterizzante del genere

---

## 📀 `demo-house.json` · House / Techno 124 BPM

Mini-traccia dance a 124 BPM. 4 pattern: **Intro Minimal** → **Verse Groove** → **Build-up** → **Drop Full**. Sequence `A A B B A B C D D B`.

Punti di forza: pan stereo ampio (clap L40, cowbell R60), velocity alternata sugli hi-hat ottavi, build-up con probability decrescente sul kick, snare roll nel fill.

## 📀 `demo-trap.json` · Trap 140 BPM (half-time)

Beat trap moderno. Kick 808 pitchato -5 con pattern sincopato (non 4/4). Hi-hat con ratchet 2×/3×/4× ovunque — **l'essenza del trap moderno**.

Punti di forza: ghost kick con probability, rim shot come accent, snare roll 4× esplosivo nel Pattern D. Sequence `A A B B C B B C C D`.

## 📀 `demo-boombap.json` · Boom Bap 90s (J Dilla / Pete Rock)

**SWING 52%** + **Humanize ON**: è tutto qui. Il classico feel "lazy dietro il beat" che ha fatto la storia dell'hip-hop anni '90.

Caratteristiche distintive:
- Kick sincopato (step 1 e 7) — non 4/4, alla Dilla
- **Ghost snare** al 7 e 11 con probability 55-80% (variazioni jazz)
- **Rim shot** al posto del click (Pete Rock style)
- **Hi-hat pitch -2 e decay 0.7** — vibe vintage lo-fi
- Clap muted, si usa solo snare puro

Prova il trucco: porta lo swing a 0 e senti tutto diventare robotico. Poi rimettilo a 52% → magia.

Sequence `A A B B A B C D`.

## 📀 `demo-dnb.json` · DNB / Amen Break 170 BPM

Ispirato all'**Amen Break** dei The Winstons (1969), il drum solo di 4 secondi più campionato della storia. Ha fatto nascere jungle, DNB, breakbeat.

Firma classica Amen:
- Kick solo su step **1 e 11** (mai 4/4)
- Snare backbeat (5, 13) + **ghost snare al 7** ← dettaglio magico
- Hi-hat/ride 8th con accenti

Pattern A/B alternano le due bar dell'Amen originale (il kick si sposta tra le due). Pattern C aggiunge roll e tensione. Pattern D è il **big break**: snare roll 4× + tom fill ascendente.

Trucco per capire l'Amen: dopo l'import, seleziona la traccia SNARE (click sul nome), poi premi `S` (solo) → senti isolato il pattern Amen classico col ghost che "fa tutto".

Sequence `A B A B A B C A B D`.

## 📀 `demo-makesomenoise.json` · NYC Hip-Hop 105 BPM

Pattern **nello stile** di "Make Some Noise" dei Beastie Boys (2011) — NYC hip-hop punchy, feel quasi dritto (swing 12%, non boom-bap pesante).

> ⚠️ **Chiarimento**: è un pattern originale *ispirato* al brano, non una cover né una riproduzione. La drum programming (kick/snare placement) è grammatica musicale generale; il brano reale con voci, sample, synth e arrangement resta dei Beastie Boys.

Firma sonora:
- **Kick doppio** su step 1+3 e 9+11 (non four-on-the-floor) — il "boom-BOOM ... ta" caratteristico
- Snare backbeat punchy, pitch +2 per lo "snap" da drum machine vintage
- **Rim shot sugli off-beat 16th** = shaker/tamburello del verso
- **Cowbell HP-filtered** (cutoff 30%) per la timbrica metallica NYC
- Double snare al step 13 nel hook = "crack-crack" del ritornello
- Tom fill "live" nel Pattern D — stile Beastie, niente trap roll aggressivi
- Humanize on leggero per feel umano

Pattern A (intro/skeleton) → B (verse con shaker+cowbell) → C (hook punchy con clap layer) → D (break con tom fill). Sequence `A B B C B C C D`.

Trucchi interessanti:
- Porta lo **swing a 45%** → stesso pattern diventa boom-bap classico (capisci quanto lo swing cambi tutto)
- **PITCH cowbell +4** → vibe ancora più NYC-80s
- Togli **HUMANIZE** → diventa più "tight/compressed" come le registrazioni del 2011 reali

---

## 🏛 Break storici

I 4 file seguenti ricostruiscono lo *scheletro ritmico* di break leggendari. Sono un piccolo museo interattivo: puoi ascoltare in 60 secondi la differenza fondamentale fra una drum machine del 1982 (metronomica), un batterista funk del 1970 (pieno di ghost), un hard rock del 1971 (massiccio e half-time) e una band di session tropicale del 1973 (bongos e claves).

### 📀 `demo-billiejean.json` · 117 BPM, stile Linn LM-1

Ispirato a *Billie Jean* (Michael Jackson, 1982). La drum machine era una Linn LM-1, strumento che ha cambiato la produzione pop: precisione **assolutamente metronomica**, niente humanize, niente ghost. Il groove nasce da ciò che è **presente** (kick sincopato su 1 e 7, snare pulito, hi-hat 16th con accento) e da ciò che è **assente** (nessuna sottigliezza ritmica).

**Trucco**: prova ad attivare HUMANIZE → senti come il feel si rovina subito. È una delle rare demo dove il robot è l'obiettivo.

### 📀 `demo-funkydrummer.json` · 103 BPM, stile Clyde Stubblefield

Ispirato a *Funky Drummer* (James Brown, 1970), eseguito da Clyde Stubblefield. Il break più campionato della storia dell'hip-hop (Public Enemy, N.W.A, LL Cool J, Prince e migliaia di altri). L'anima del pattern sta in due cose:

1. **Ghost snare** fittissimi (step 7, 8, 11, 14) con velocity 0.3-0.35 e probability 80-90% — creano il "conversational" feel del funk
2. **Open hat al step 6** — un singolo colpo che è IL momento magico del break

Test da manuale: metti la traccia OPEN HH a volume 0 durante la riproduzione. Senti il groove che si affloscia. Rimetti su → torna il funk. Tutto il mito sta lì.

### 📀 `demo-levee.json` · 72 BPM, stile John Bonham

Ispirato a *When the Levee Breaks* (Led Zeppelin IV, 1971). Bonham registrò il drum break nella tromba delle scale di Headley Grange, con due microfoni lontani — da qui il sound enorme. Il pattern è **semplicissimo** (kick su 1 e 7, snare sul backbeat, hi-hat 8th), ma i parametri lo fanno diventare monumentale:

- Kick **pitch -3 e decay 2.0×**
- Snare **pitch -1 e decay 1.5×**
- Tom **pitch -4 e decay 1.8×** (il "bombo-tom" signature)
- Humanize **off** — Bonham era tight, non lazy

Campionato da Beastie Boys (*Rhymin' & Stealin'*), Eminem (*Kim*), Dr. Dre, Enigma e molti altri. Prova ad alzare il decay del kick a 2.5 e del snare a 2.0 per amplificare l'effetto "stairwell".

### 📀 `demo-apache.json` · 112 BPM, il break originario dell'hip-hop

Ispirato ad *Apache* (Incredible Bongo Band, 1973). Questo è il break che **DJ Kool Herc** isolava e loopava ai block party del Bronx nel 1973-75 — l'atto di nascita materiale dell'hip-hop. La band era una session tropicale e la drum programming riflette il mix: batteria funk + bongos + claves + cowbell.

Ho mappato i timbri come fa tipicamente chi "interpreta" Apache in una drum machine moderna:
- **TOM** con pitch +5 = bongos (pan R40)
- **RIM** con pitch +1 = claves (pan L40, stereo largo anni '70)
- **COWBELL** = cowbell latina (pan R25)
- **HI-HAT** solo 8th, non protagonista
- Kick doppio sincopato (1+3, 9+11) per il feel latino-funk

Il Pattern C è il "break di Kool Herc": kick ridotto, percussioni in roll. È il momento in cui i DJ abbassavano la batteria principale e facevano rappare sopra le congas. Per sentirlo: durante il Pattern C, muta il kick (premi `M` con la traccia KICK attiva) → hai ricostruito l'esperienza di un block party 1975.

### 📀 `demo-impeach.json` · 100 BPM, "Impeach the President"-style

Ispirato al break di apertura di *Impeach the President* (The Honey Drippers, 1973). La lezione di questo break è la **pulizia**: kick sparse (1 e "and of 2"), snare backbeat "crack", hi-hat 16th steady. Niente ghost, niente fill. Proprio la semplicità l'ha reso uno dei break più campionati nel golden age hip-hop.

**Prova**: suona benissimo anche a tempo diverso — porta il BPM a 88 e diventa boom bap West Coast.

### 📀 `demo-ashleysroachclip.json` · 100 BPM, "Ashley's Roachclip"-style

Ispirato a *Ashley's Roachclip* (The Soul Searchers, 1974). A parità di BPM con Impeach, ha un groove più funky: kick più ricco (1, "and of 1", 11), ghost snare in mezzo, e soprattutto **open hat al step 6** come Funky Drummer. È il "cugino più movimentato" di Impeach.

**Prova**: porta volume OPEN HH a 0. Il groove diventa più piatto — l'open hat al 6 è il trucco che si porta dal 1970 al 2020.

### 📀 `demo-synthsub.json` · 91 BPM, "Synthetic Substitution"-style

Ispirato a *Synthetic Substitution* (Melvin Bliss, 1973). Il punto di forza è lo **spazio**: kick sincopato su 0, 3, 8, 11, ma hi-hat solo in 8th (non 16th come gli altri break). Questo respiro è il motivo per cui i rapper golden age lo hanno scelto così tanto — c'è aria dentro cui mettere parole.

**Prova**: imposta lo stesso pattern passando il BPM a 85 e aggiungi un po' di swing (20%) → diventa un loop boom-bap perfetto per un verso lungo.

### 📀 `demo-onedrop.json` · 80 BPM · ★ filosofia ritmica invertita

Questa non è una ricostruzione di un brano specifico ma del **principio ritmico** del reggae classico (Studio One, Marley, Sly & Robbie). È la demo più interessante per capire quanto una drum machine pro sia flessibile: se sposti il "centro di gravità" ritmico, cambi genere.

Il colpo di genio del reggae è **mettere kick e snare insieme sul beat 3**, non sull'1. Nel sequencer: solo step 8 è forte. Il resto del pattern è hi-hat skank (step 4 e 12) + rim shot come cross-stick. Tutto ciò che vedi *assente* è il groove.

**Test che spacca la testa**: ascolta Pattern A. Poi cliccando Pattern C passi a "rockers" (aggiunge kick sull'1 in stile Sly & Robbie anni '70). Stesso BPM, stessa strumentazione, due epoche reggae diverse.

### 📀 `demo-ukhardcore.json` · 140 BPM, rave UK 1992-93 (pre-jungle)

L'era dell'**hardcore UK** (The Prodigy primi EP, SL2, Shut Up & Dance, Acen, Rufige Kru) dove il breakbeat incontrava la 4/4 rave. Qui **Pattern A è 4/4 rave dritto** (stile hardcore), **Pattern B è Amen choppato** con ghost snare (stile jungle nascente), **Pattern C li fonde con ratchet aggressivi**, **Pattern D è un fill pre-drop esplosivo** (snare roll 4× + tom fill). Nel 1992-93 questi due mondi coesistevano nello stesso brano — ascolti la transizione da hardcore a jungle in un singolo loop.

**Trucco mind-blowing**: finito l'ascolto, alza il BPM a 170 e muta il kick durante il Pattern B. Hai appena ricostruito la transizione storica hardcore → drum & bass che è avvenuta tra il 1993 e il 1995. Un cambio di velocità + un kick muto = nuovo genere.

---

## 🚀 Come usare

1. Scarica il file `.json` dal repo (click sui link sopra)
2. Apri la PWA DrumAPP
3. Clicca **IMPORT** → seleziona il file
4. ⚠️ **Attiva SONG** nella modebar (altrimenti loopa solo il Pattern A)
5. Premi **PLAY** (o `SPACE`)

💡 **Prima di cliccare DEMO** (che sovrascrive Pattern A e B), salva il set importato in uno SLOT: *hold 500 ms* su A/B/C/D. Così puoi smanettare liberamente e recuperarlo con un tap.

---

## 🛠 Creare le tue demo

Gli script Python `_build_*.py` sono i generatori. Usali come template:

```bash
cd examples
python3 _build_house.py     # ↦ demo-house.json
python3 _build_trap.py      # ↦ demo-trap.json
python3 _build_boombap.py   # ↦ demo-boombap.json
python3 _build_dnb.py       # ↦ demo-dnb.json
```

La struttura è sempre la stessa — API minimale:

```python
from copy import copy

def cell(vel=0.9, prob=100, ratch=1, nudge=0):
    """Una cella accesa del sequencer"""
    return {"vel": vel, "prob": prob, "ratch": ratch, "nudge": nudge}

def set_steps(pattern, track, steps, **kwargs):
    """Attiva gli step (indici 0-based) sulla traccia"""
    for s in steps:
        pattern[track][s] = cell(**kwargs)

# Esempio: kick four-on-the-floor
set_steps(A, KICK, [0, 4, 8, 12], vel=1.0)

# Esempio: hi-hat trap con ratchet
for s in range(16):
    A[HIHAT][s] = cell(vel=0.6)
A[HIHAT][14] = cell(vel=0.8, ratch=3)  # tripletta
A[HIHAT][15] = cell(vel=0.9, ratch=4)  # roll
```

Indici tracce: `KICK=0, SNARE=1, HIHAT=2, OPENHAT=3, CLAP=4, TOM=5, RIM=6, COW=7`.

## 📋 Formato

Vedi il [README principale](../README.md#-formato-dati) per lo schema completo JSON v2.

## 💡 Idee per altre demo

Se ne vuoi altre, i generi che si prestano bene a questa drum machine:

- **Techno minimal** (130 BPM, kick 4/4, clap offbeat, molti spazi vuoti)
- **Afrobeat** (115 BPM, cowbell + conga-style tom, pan stereo molto ampio)
- **Garage UK** (130 BPM, shuffle 60%+ con snare su 3 anziché 4/13)
- **Footwork/Juke** (160 BPM, kick pattern folli con probability alta)
- **Half-time metal** (80 BPM, kick doppio, snare lento, hi-hat 16th aggressivi)

Chiedi pure il prossimo.

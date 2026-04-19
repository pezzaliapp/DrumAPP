# DrumAPP · Examples

Set di esempio importabili nell'app via il bottone **IMPORT**. Ognuno è pensato per dimostrare un **genere diverso** e le feature Pro che lo caratterizzano.

---

## 📀 Demo disponibili

| File | Genere | BPM | Durata | Feel |
|---|---|---|---|---|
| [`demo-house.json`](demo-house.json)     | House / Techno      | 124 | ~20s | 4/4 dritto, build + drop |
| [`demo-trap.json`](demo-trap.json)       | Trap / Hip-Hop      | 140 | ~17s | 808 profondo + ratchet hats |
| [`demo-boombap.json`](demo-boombap.json) | Boom Bap '90s       |  90 | ~21s | Swing alto, feel "lazy" Dilla |
| [`demo-dnb.json`](demo-dnb.json)         | DNB / Amen Break    | 170 | ~14s | Breakbeat jungle, ghost snare |

Tutte usano gli stessi 8 suoni sintetizzati di DrumAPP — cambia solo come vengono **programmati** (pattern, velocity, ratchet, pan, pitch). È la dimostrazione migliore di quanto il *programming* conti più del *sample* in una drum machine.

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

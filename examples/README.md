# DrumAPP · Examples

Set di esempio importabili nell'app via il bottone **IMPORT**.

## 📀 Demo disponibili

| File | Stile | BPM | Durata | Caratteristica distintiva |
|---|---|---|---|---|
| [`demo-house.json`](demo-house.json) | House / Techno | 124 | ~20s | Pattern 4/4, pan stereo, build-up + drop |
| [`demo-trap.json`](demo-trap.json)   | Trap / Hip-Hop  | 140 | ~17s | Kick 808 sincopato, hi-hat ratchet (triplette), snare roll finale |

---

## 📀 `demo-house.json`

Mini-traccia house/techno a 124 BPM. Dimostra velocity alternate, probability, ratchet, nudge, pan stereo, pitch kick profondo, filter high-pass sulla cowbell.

**Pattern:** A (Intro Minimal · 12 hit) → B (Verse Groove · 28) → C (Build-up · 26) → D (Drop Full · 35)
**Sequence:** A A B B A B C D D B

## 📀 `demo-trap.json`

Trap beat moderno a 140 BPM (half-time feel = suona come 70). La firma sonora del trap sta nei **ratchet** degli hi-hat: l'orecchio sente le triplette velocissime che gli altri generi non hanno.

**Pattern:** A (Intro · 14 hit) → B (Verse · 26) → C (Hype · 29) → D (Fill · 33)
**Sequence:** A A B B C B B C C D
**Signature moves:**
- Kick sincopato su step 1-7-9-11 (non four-on-the-floor come house)
- 808 pitchato -5 semitoni con decay 1.8× (sub profondo)
- Hi-hat 16th con ratchet 2×/3×/4× (le famose triplette trap)
- Snare roll finale 4× sullo step 15 del Pattern D
- Clap layered col snare, pan L30 per creare larghezza stereo
- Cowbell muted (non si usa nel trap)

---

## 🎛 Feature coperte dalle demo

| Feature             | In quale demo |
|---------------------|---------------|
| Velocity variabile  | house, trap (hi-hat alternato) |
| Probability         | house (rim 65%, kick prob), trap (ghost kick) |
| Ratchet             | house (snare roll + hi-hat fill), **trap (ovunque)** |
| Nudge               | house (hi-hat +5ms), trap (no, trap sta sul grid) |
| Swing               | house (8%), trap (0%) |
| Humanize            | house (on), trap (off) |
| Pan stereo          | entrambi |
| Pitch estremo       | trap (-5 su kick) |
| Filter high-pass    | house (cowbell) |
| Song mode           | entrambi |

## Come usare

1. Scarica il JSON
2. Apri la PWA DrumAPP
3. Clicca **IMPORT** → seleziona il file
4. Attiva **SONG** nella modebar (altrimenti suona solo il Pattern A in loop)
5. Premi **PLAY** (o `SPACE`)

💡 Prima di cliccare DEMO, **salva** il set importato in uno SLOT (hold 500ms su A/B/C/D) per non perderlo.

---

## 🛠 Generatori

Gli script Python `_build_demo.py` e `_build_trap.py` hanno generato i JSON. Usali come template:

```bash
cd examples
python3 _build_demo.py   # rigenera demo-house.json
python3 _build_trap.py   # rigenera demo-trap.json
```

Modifica le chiamate `set_steps(pattern, track, [steps], vel=X, ratch=Y)` per creare le tue demo (dnb, techno minimal, ambient…).

## 📋 Formato

Vedi il [README principale](../README.md#-formato-dati) per lo schema completo JSON v2.


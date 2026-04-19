# DrumAPP · Examples

Set di esempio importabili nell'app via il bottone **IMPORT**.

## 📀 `demo-house.json`

Mini-traccia house/techno di ~20 secondi a 124 BPM che dimostra **tutte** le feature Pro:

| Feature             | Dove la trovi |
|---------------------|-----------------------------------------------------|
| Velocity variabile  | Pattern B/D: hi-hat con accenti sui pari            |
| Probability         | Pattern B: rim al 65% · Pattern C: kick che "si rompe" |
| Ratchet             | Pattern C: hi-hat 2x/3x nel fill · snare roll 4x    |
| Nudge               | Pattern D: hi-hat off con +5ms (groove umano)       |
| Swing               | 8% globale                                          |
| Humanize            | On (± 12 ms timing, ± 15% velocity)                 |
| Pan stereo          | Clap L40 · Hi-hat/Open HH R30 · Rim L50 · Cowbell R60 |
| Pitch               | Kick -2 semitoni (profondo) · Tom +3 (acuto)        |
| Decay               | Kick 1.5× lungo · Hi-hat 0.7× corto                 |
| Filter              | Cowbell in high-pass 35% (più "metallico")          |
| Song mode           | Sequenza: A A B B A B C D D B (intro · verse · build · drop · outro) |

### Come usare
1. Scarica `demo-house.json`
2. Apri la PWA DrumAPP
3. Clicca **IMPORT** → seleziona il file
4. Attiva **SONG** nella modebar (altrimenti suona solo il pattern corrente in loop)
5. Premi **PLAY** (o `SPACE`)

### Struttura dei 4 pattern

**A — Intro Minimal** · 12 hits
Kick 4/4, clap back-beat (step 5/13), hi-hat off-beat (3/7/11/15), open hat su 7/15.

**B — Verse Groove** · 28 hits
Come A + hi-hat ottavi con dinamica (forte sui pari, debole sui dispari), cowbell in layer col clap, rim con probability 65% e 50% per variazioni.

**C — Build-up** · 26 hits
Tensione: kick con probability decrescente (100/100/85/60), hi-hat 16th con ratchet 2× e 3× nei fill finali, snare roll 4× sul 15, tom ascendente (10/12/14 con nudge e velocity crescenti).

**D — Drop Full** · 35 hits
Groove completo: kick+snare+clap layered, hi-hat 16th con velocity alternate e nudge +5ms sugli off, open hat off-beat, cowbell 16esimi dispari (feel latino-house), rim con probability, tom occasionale.

---

## 🛠 Generatore

Il file `_build_demo.py` è lo script Python che ha generato il JSON.
Usalo come template per creare le tue demo:

```bash
cd examples
python3 _build_demo.py
```

Modifica la funzione `cell(vel, prob, ratch, nudge)` e le chiamate `set_steps()` per costruire i tuoi pattern, poi re-importa in DrumAPP.

## 📋 Formato

Vedi il [README principale](../README.md#-formato-dati) per lo schema completo JSON v2.

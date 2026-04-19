# DrumAPP — Pro Drum Machine

Una drum machine **professionale a 8 voci** nel browser. 16 step (8/12/16/24/32), swing, velocity per step, probability, ratchet, nudge, filter/pitch/decay per traccia, 4 pattern live con song mode, export WAV, Web MIDI out, undo/redo. Tutto **Web Audio sintetizzato**, niente sample, niente dipendenze esterne, funziona offline come PWA.

**Demo live:** [pezzaliapp.github.io/DrumAPP](https://pezzaliapp.github.io/DrumAPP/)

---

## ✨ Feature Pro

### Sequencer
- **16 step di default**, lunghezza variabile (8 / 12 / 16 / 24 / 32)
- **8 voci sintetiche**: Kick · Snare · Hi-Hat · Open HH · Clap · Tom · Rimshot · Cowbell
- **4 pattern live A/B/C/D** con switch istantaneo durante il play
- **Song mode**: concatena i pattern in una sequenza (default A-A-B-A)

### Timing & Groove
- **BPM 60–200** con slider
- **Swing 0–75%** (ritarda gli step dispari — fa la differenza tra "robot" e "groove")
- **Tap tempo** (bottone TAP o tasto `T`, almeno 2 tap)
- **Humanize** (±12 ms di timing, ±15% velocity per ogni hit)
- **Metronomo** on/off (click accento sul downbeat)

### Per ogni traccia
Click sul **nome** della traccia per selezionarla. In alto appaiono i parametri:
- **Volume** 0–100%
- **Mute / Solo** (inline, M/S)
- **Pitch** ±12 semitoni
- **Decay** 0.4x – 2.5x (corto / lungo)
- **Filter** Off / Low-pass / High-pass con **Cutoff** 50 Hz – 18 kHz

### Per ogni step (drag verticale in edit mode)
Cambia modalità con i bottoni `TRIG / VEL / PROB / RATCH / NUDGE`:
- **TRIG**: click = toggle on/off
- **VEL**: drag su/giù per velocity (0.05–1.0) — visualizzata come barra colorata che sale dal basso
- **PROB**: drag su/giù per probabilità trigger (0–100%) — lo step suona solo con quella probabilità (generative)
- **RATCH**: drag per ratchet (1× / 2× / 3× / 4×) — ripetizioni dentro un singolo step (essenziale per hi-hat trap)
- **NUDGE**: drag per micro-timing (±50 ms) — sposta lo step off-grid

### Output
- **Export WAV**: renderizza 2 loop del pattern corrente via `OfflineAudioContext`, scarica `.wav` 44.1 kHz 16-bit stereo
- **Export / Import JSON**: salva/carica l'intero "set" (tutti i pattern + parametri tracce + swing)
- **Share link**: URL compatto col pattern corrente (hex encoding)
- **Web MIDI out**: invia note General MIDI sulla prima porta disponibile (kick=36, snare=38, hihat=42, ecc.)

### Storage & Edit
- **4 slot locali A/B/C/D** su `localStorage` — *tap* carica, *hold 500 ms* salva l'intero set
- **Undo / Redo** (max 40 step di storia) — `Cmd/Ctrl+Z` e `Cmd/Ctrl+Shift+Z`
- **Demo** ricarica pattern di esempio · **Clear** svuota pattern corrente

---

## ⌨️ Scorciatoie tastiera

| Tasto | Azione |
|---|---|
| `SPACE` | Play / Stop |
| `T` | Tap tempo |
| `1` – `4` | Switch pattern A/B/C/D |
| `C` | Clear pattern corrente |
| `D` | Load demo |
| `Cmd/Ctrl + Z` | Undo |
| `Cmd/Ctrl + Shift + Z` | Redo |

---

## 🏗 Architettura tecnica

**Sintesi sonora** — ogni voce costruita con `OscillatorNode` + `GainNode` + `BiquadFilterNode`, niente sample. Il kick è un sine sweep 165→45 Hz con click 1200 Hz, lo snare è triangle + noise passato in high-pass 1 kHz, l'hi-hat è noise bianco high-pass 7 kHz, la cowbell è due square a 540/800 Hz in bandpass 2 kHz (stile TR-808).

**Catena audio per traccia**: `voice` → `trackFilter[i]` (BiquadFilter) → `trackGain[i]` (volume + mute/solo logic) → `masterGain` → `destination`. I parametri si aggiornano con `setTargetAtTime` per evitare click di discontinuità.

**Scheduler** — pattern di Chris Wilson: `setInterval` ogni 25 ms programma gli step nei 100 ms successivi via `AudioContext.currentTime`, timing solido anche sotto load. Gestisce in un unico pass: swing, probability (Math.random), ratchet (loop interno con gap calcolato), nudge (offset ms), humanize (random ±), metronomo.

**Pattern** — matrice `[track][step]` dove ogni cella è `null` (off) o `{ vel, prob, ratch, nudge }`. Tutti e 4 i pattern A/B/C/D coesistono in memoria, lo switch cambia solo il puntatore `currentPattern`.

**PWA** — `service-worker.js` (cache `drumapp-v3`) serve tutti gli asset offline dopo la prima visita.

---

## 📦 Struttura del progetto

```
DrumAPP/
├── index.html          # markup (top, atrack panel, sequencer, modebar, storage, footer)
├── style.css           # Studio Press palette + tutti i componenti Pro
├── app.js              # Web Audio, sintesi 8 voci, scheduler, UI, export WAV, MIDI
├── manifest.json       # PWA manifest
├── service-worker.js   # offline cache (drumapp-v3)
├── icons/              # 192/512/maskable PNG
├── python/
│   └── drum_machine.py # versione desktop legacy (pygame+numpy)
└── generate_icons.py   # script generazione icone da SVG
```

---

## 🚀 Installazione & deploy

**Locale (test):**
```bash
git clone https://github.com/pezzaliapp/DrumAPP.git
cd DrumAPP
python3 -m http.server 8000
# apri http://localhost:8000
```

**Aggiornamento su GitHub Pages:**
```bash
cd DrumAPP
git add .
git commit -m "Pro Edition: 8 voices, swing, velocity, WAV export, MIDI"
git push origin main
```

**Importante**: dopo il push, per vedere la nuova versione serve un **hard reload** per bypassare il service worker:
- Desktop Chrome/Safari: `Cmd+Shift+R` (Mac) o `Ctrl+Shift+R` (Win/Linux)
- iOS: chiudi e riapri la PWA **due volte**

---

## 📋 Formato dati

Export JSON versione 2:
```json
{
  "version": 2,
  "bpm": 120,
  "swing": 25,
  "patternLength": 16,
  "humanize": false,
  "trackParams": [{ "volume": 0.85, "pitch": 0, "decay": 1.0, ... }, ...],
  "patterns": {
    "A": [[{"vel":0.9,"prob":100,"ratch":1,"nudge":0}, null, ...], ...],
    "B": [...], "C": [...], "D": [...]
  }
}
```

---

## 🎯 Scelte di design

- **Niente sample**: ogni suono è sintetizzato con Web Audio. Dimensione totale < 60 KB, zero dipendenze, funziona anche su iPhone 8.
- **Estetica Studio Press**: palette carta avorio `#eae3d2` + inchiostro `#1a1a22` + accento arancione `#f77f00`. Typography Anton (display) + VT323 (mono per BPM) + IBM Plex Sans (UI). Noise overlay SVG per texture carta.
- **Active track pattern**: invece di stipare tutti i controlli per traccia nel sequencer, si seleziona una traccia (click sul nome) e si modificano i suoi parametri nel panel superiore. Workflow Elektron-style.
- **Pattern multipli come live slot**: i 4 pattern A/B/C/D sono *sempre* in memoria, lo switch è istantaneo. Gli slot su `localStorage` servono per persistere interi "set" tra sessioni.

---

## 👤 Autore

**Alessandro Pezzali** — [pezzaliapp.github.io](https://pezzaliapp.github.io)

## 📄 Licenza

MIT — vedi [LICENSE](LICENSE)

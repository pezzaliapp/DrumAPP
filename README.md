# DrumAPP — Pro Drum Machine

Una drum machine **professionale a 8 voci** nel browser. 16 step (8/12/16/24/32), swing, velocity/probability/ratchet/nudge per step, pan/pitch/decay/filter per traccia, 4 pattern live con song editor, bounce WAV + rec live, Web MIDI out, undo/redo, guida integrata. Tutto **Web Audio sintetizzato**, niente sample, niente dipendenze esterne, funziona offline come PWA.

**Demo live:** [pezzaliapp.github.io/DrumAPP](https://pezzaliapp.github.io/DrumAPP/)

> Prima volta qui? Premi il bottone **?** nel footer (o il tasto `?`) per aprire la guida integrata con tutte le istruzioni passo-passo.

---

## ✨ Feature Pro

### Sequencer
- **16 step di default**, lunghezza variabile (8 / 12 / 16 / 24 / 32)
- **8 voci sintetiche**: Kick · Snare · Hi-Hat · Open HH · Clap · Tom · Rimshot · Cowbell
- **4 pattern live A/B/C/D** con switch istantaneo durante il play (tasti `1-4` o `[` / `]`)
- **Copy/Paste pattern** — duplica il pattern corrente per ritoccarlo in un altro slot
- **Song editor visuale** — riga `SEQUENCE: [A][A][B][A]` con click-to-cycle, bottoni `+`/`−` per allungare/accorciare (1–16 slot). Lo slot corrente si illumina di arancione durante la playback quando SONG è attivo.

### Timing & Groove
- **BPM 60–200** con slider
- **Swing 0–75%** (ritarda gli step dispari — fa la differenza tra "robot" e "groove")
- **Tap tempo** (bottone TAP o tasto `T`, almeno 2 tap)
- **Humanize** (±12 ms di timing, ±15% velocity per ogni hit)
- **Metronomo** on/off (click accento sul downbeat)

### Per ogni traccia
Click sul **nome** della traccia per selezionarla. In alto appaiono 6 controlli:
- **Volume** 0–100%
- **Pan** stereo L100 ← C → R100 (doppio click per centrare)
- **Pitch** ±12 semitoni
- **Decay** 0.4× – 2.5× (corto / lungo)
- **Filter** Off / Low-pass / High-pass con **Cutoff** 50 Hz – 18 kHz
- **Mute / Solo** (inline, M/S)

### Per ogni step (drag verticale in edit mode)
Cambia modalità con i bottoni `TRIG / VEL / PROB / RATCH / NUDGE`. Sotto la modebar appare un **hint contestuale** che spiega cosa fa ogni modalità:
- **TRIG**: click = toggle on/off
- **VEL**: drag su/giù per velocity (0.05–1.0) — visualizzata come barra colorata che sale dal basso
- **PROB**: drag per probabilità trigger (0–100%) — a 50% lo step suona metà delle volte (generative)
- **RATCH**: drag per ratchet (1× / 2× / 3× / 4×) — ripetizioni dentro un singolo step (essenziale per hi-hat trap)
- **NUDGE**: drag per micro-timing (±50 ms) — sposta lo step off-grid

### Output
- **BOUNCE WAV**: render deterministico offline via `OfflineAudioContext`. Apre un dialog dove scegli 2 / 4 / 8 loop o "intera song" (se SONG è attivo, renderizza tutta la sequence). Veloce, file `.wav` 44.1 kHz 16-bit stereo, pulito come uno studio.
- **REC LIVE**: registra *in tempo reale* tutto ciò che esce dalle casse — knob twist, cambi di pattern, modifiche di volume, mute/solo. Premi una volta per iniziare (bottone rosso pulsante con timer), premi di nuovo per fermare e scaricare. File `.webm` (Opus) ~8× più piccolo del WAV a qualità equivalente. Utile per catturare performance improvvisate.
- **Export / Import JSON**: salva/carica l'intero "set" (tutti i pattern + parametri tracce + song sequence + swing)
- **Share link**: URL compatto col pattern corrente (hex encoding)
- **Web MIDI out**: invia note General MIDI sulla prima porta disponibile (kick=36, snare=38, hihat=42, openhat=46, clap=39, tom=45, rim=37, cow=56)

### Storage & Edit
- **4 slot locali A/B/C/D** su `localStorage` — *tap* carica, *hold 500 ms* salva l'intero set
- **Copy / Paste** — clipboard in memoria, il bottone PASTE si illumina quando ha contenuto
- **Undo / Redo** (max 40 step di storia) — `⌘Z` / `⌘⇧Z`
- **Demo** ricarica pattern di esempio · **Clear** svuota pattern corrente

### Guida integrata
- **Hint contestuale**: sotto la modebar compare sempre un suggerimento che spiega la modalità edit selezionata
- **Modal HELP** (bottone `?` nel footer o tasto `?`): guida completa con 6 sezioni (play & transport, sequencer & edit mode, pattern & song, parametri traccia, save & export, shortcuts + tip rapidi). Chiusura con `ESC`.

---

## ⌨️ Scorciatoie tastiera

| Tasto | Azione |
|---|---|
| `SPACE` | Play / Stop |
| `T` | Tap tempo |
| `1` – `4` | Switch pattern A/B/C/D |
| `[` / `]` | Pattern precedente / successivo |
| `↑` / `↓` | Traccia attiva precedente / successiva |
| `M` / `S` | Mute / Solo sulla traccia attiva |
| `C` | Clear pattern corrente |
| `D` | Load demo |
| `⌘Z` / `Ctrl+Z` | Undo |
| `⌘⇧Z` / `Ctrl+Shift+Z` | Redo |
| `?` | Apri guida |
| `ESC` | Chiudi modali |

---

## 🏗 Architettura tecnica

**Sintesi sonora** — ogni voce costruita con `OscillatorNode` + `GainNode` + `BiquadFilterNode`, niente sample. Il kick è un sine sweep 165→45 Hz con click 1200 Hz, lo snare è triangle + noise passato in high-pass 1 kHz, l'hi-hat è noise bianco high-pass 7 kHz, la cowbell è due square a 540/800 Hz in bandpass 2 kHz (stile TR-808).

**Catena audio per traccia**: `voice` → `trackPanner[i]` (StereoPannerNode) → `trackFilter[i]` (BiquadFilter) → `trackGain[i]` (volume + mute/solo) → `masterGain` → `destination`. In parallelo il masterGain è connesso anche a un `MediaStreamDestination` usato da `MediaRecorder` per il REC live. I parametri si aggiornano con `setTargetAtTime` per evitare click di discontinuità.

**Scheduler** — pattern di Chris Wilson: `setInterval` ogni 25 ms programma gli step nei 100 ms successivi via `AudioContext.currentTime`, timing solido anche sotto load. Gestisce in un unico pass: swing, probability (Math.random), ratchet (loop interno con gap calcolato), nudge (offset ms), humanize (random ±), metronomo, song mode (avanza `songStep` al wrap).

**Pattern** — matrice `[track][step]` dove ogni cella è `null` (off) o `{ vel, prob, ratch, nudge }`. Tutti e 4 i pattern A/B/C/D coesistono in memoria, lo switch cambia solo il puntatore `currentPattern`.

**Bounce WAV** — `OfflineAudioContext` ricostruisce l'intera catena audio (panner/filter/gain) e schedula tutti gli step della sequenza scelta (loop del pattern corrente o intera song). `AudioBuffer` → PCM 16-bit stereo → WAV RIFF header scritto a mano in `DataView`.

**REC live** — `MediaStreamDestination` in parallelo a `destination`, passato a `MediaRecorder`. Formato auto-negoziato (`audio/webm;codecs=opus` preferito, fallback `audio/mp4` su Safari). I chunks si accumulano via `ondataavailable`, al `stop` vengono uniti in Blob e scaricati.

**PWA** — `service-worker.js` (cache `drumapp-v6`) serve tutti gli asset offline dopo la prima visita. Cache-first per gli asset locali, runtime caching per i font di Google.

---

## 📦 Struttura del progetto

```
DrumAPP/
├── index.html          # markup (top, atrack panel, sequencer, modebar, songbar, storage, footer, modal)
├── style.css           # Studio Press palette + tutti i componenti Pro + modal help
├── app.js              # Web Audio, sintesi 8 voci, scheduler, UI, bounce, rec live, MIDI
├── manifest.json       # PWA manifest
├── service-worker.js   # offline cache (drumapp-v6)
├── icons/              # 192/512/maskable PNG
├── examples/           # set JSON importabili (demo-house.json)
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
git commit -m "Pro Edition: 8 voices + pan + song editor + help"
git push origin main
```

**Importante**: dopo il push, per vedere la nuova versione serve un **hard reload** per bypassare il service worker:
- Desktop Chrome/Safari: `Cmd+Shift+R` (Mac) o `Ctrl+Shift+R` (Win/Linux)
- iOS: chiudi e riapri la PWA **due volte** (la prima scarica la v6, la seconda la attiva)

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
  "trackParams": [
    {
      "volume": 0.85, "mute": false, "solo": false,
      "pitch": 0, "decay": 1.0,
      "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0,
      "pan": 0
    }
  ],
  "patterns": {
    "A": [[{"vel":0.9,"prob":100,"ratch":1,"nudge":0}, null, ...], ...],
    "B": [...], "C": [...], "D": [...]
  },
  "songSequence": ["A", "A", "B", "A"]
}
```

**Backward compatibility**: i file v1/v2 senza `pan` o `songSequence` vengono caricati con valori di default (pan=0, sequence=["A","A","B","A"]).

---

## 🎁 Esempi (import pronti)

Nella cartella [`examples/`](examples/) trovi **14 set completi** importabili col bottone **IMPORT** — una piccola enciclopedia della drum programming popolare.

**Generi moderni** (7 file):
- `demo-house.json` · 124 BPM · house/techno con build+drop
- `demo-trap.json` · 140 BPM · trap con ratchet hats
- `demo-boombap.json` · 90 BPM · swing 52% stile Dilla
- `demo-dnb.json` · 170 BPM · Amen-ispirato
- `demo-makesomenoise.json` · 105 BPM · NYC hip-hop
- `demo-ukhardcore.json` · 140 BPM · UK rave/breakbeat '92-'93
- `demo-onedrop.json` · 80 BPM · ★ reggae one-drop (beat sul 3)

**Break storici** (7 file, ricostruzioni ritmiche):
- `demo-billiejean.json` · 117 BPM · Linn LM-1 1982
- `demo-funkydrummer.json` · 103 BPM · Clyde Stubblefield 1970
- `demo-levee.json` · 72 BPM · Bonham 1971
- `demo-apache.json` · 112 BPM · break originario hip-hop 1973
- `demo-impeach.json` · 100 BPM · Honey Drippers 1973
- `demo-ashleysroachclip.json` · 100 BPM · Soul Searchers 1974
- `demo-synthsub.json` · 91 BPM · Melvin Bliss 1973

> ⚠️ I "break storici" ricostruiscono solo lo *scheletro ritmico* (kick/snare/percussion placement), che è grammatica musicale generale. Non riproducono melodie, voci, basso, arrangement o timbri specifici delle registrazioni originali, che restano protetti.

Tutti usano le stesse 8 voci sintetizzate — cambia solo il *programming*. Vedi il [README degli esempi](examples/README.md) per dettagli e tip d'uso per ogni demo.

---

## 🎯 Scelte di design

- **Niente sample**: ogni suono è sintetizzato con Web Audio. Dimensione totale ~55 KB minificabile, zero dipendenze runtime, funziona anche su iPhone 8 e Android entry-level.
- **Estetica Studio Press**: palette carta avorio `#eae3d2` + inchiostro `#1a1a22` + accento arancione `#f77f00`. Typography Anton (display) + VT323 (mono per BPM) + IBM Plex Sans (UI). Noise overlay SVG per texture carta.
- **Active track pattern**: invece di stipare tutti i controlli per traccia nel sequencer (che diventerebbe illeggibile), si seleziona una traccia (click sul nome) e si modificano i suoi parametri nel panel superiore. Workflow Elektron-style.
- **Pattern multipli come live slot**: i 4 pattern A/B/C/D sono *sempre* in memoria, lo switch è istantaneo. Gli slot su `localStorage` servono per persistere interi "set" tra sessioni.
- **Bounce vs REC**: due paradigmi distinti, come nelle DAW serie. Bounce = render offline deterministico (veloce, pulito, stesso risultato ogni volta). REC = cattura live (cattura l'espressività delle variazioni in tempo reale).
- **Guida integrata**: la densità di feature richiede onboarding. Hint contestuale su ogni edit mode + modal HELP completo accessibile da `?`.

---

## 👤 Autore

**Alessandro Pezzali** — [pezzaliapp.github.io](https://pezzaliapp.github.io)

## 📄 Licenza

MIT — vedi [LICENSE](LICENSE)

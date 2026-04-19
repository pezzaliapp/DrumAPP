# DrumAPP

**Drum Machine a 16 step** funzionante interamente nel browser, installabile come **PWA** (Progressive Web App) su mobile e desktop. Nessun file audio esterno: i suoni sono sintetizzati in tempo reale con la **Web Audio API**.

> Disponibile anche come versione desktop Python (pygame + numpy) nella cartella [`python/`](python/).

---

## Caratteristiche

- **4 tracce** sintetizzate: Kick, Snare, Hi-Hat, Clap
- **16 step** per traccia, cliccabili/toccabili
- **Zero samples**: tutti i suoni generati via `OscillatorNode`, `BufferSource` di rumore, filtri e `GainNode` per gli inviluppi
- **Scheduler lookahead** con precisione campione-accurata (pattern di Chris Wilson)
- **Slider BPM** 60–200 regolabile durante il playback
- **3 modalità di salvataggio**:
  - **4 slot locali** (A/B/C/D) — tap = carica, tieni premuto = salva
  - **Export/Import `.json`** — per archiviazione e backup
  - **Share link** — pattern codificato nell'URL, condivisibile su WhatsApp/Telegram/email
- **Installabile** come app standalone (service worker + manifest)
- **Funziona offline** dopo il primo caricamento
- **Responsive**: si adatta a desktop, tablet e smartphone (scroll orizzontale del sequencer sui telefoni piccoli)
- **Scorciatoie da tastiera**: `SPACE` play/stop, `C` clear, `D` demo

---

## Demo live

Dopo aver pubblicato il progetto su GitHub Pages sarà accessibile come:

```
https://pezzaliapp.github.io/DrumAPP/
```

---

## Installazione come PWA

### Su iPhone / iPad (Safari)
1. Apri il sito in Safari
2. Tocca l'icona **Condividi** (quadrato con freccia)
3. Scorri e tocca **Aggiungi alla schermata Home**

### Su Android (Chrome)
1. Apri il sito in Chrome
2. Tocca il menu a tre puntini
3. Tocca **Installa app** (o **Aggiungi a schermata Home**)

### Su Desktop (Chrome / Edge)
1. Apri il sito
2. Clicca sull'icona **Installa** che appare nella barra degli indirizzi

---

## Pubblicazione su GitHub Pages

La PWA si serve direttamente dalla root del repo, quindi basta abilitare GitHub Pages:

1. Vai nelle **Settings** del repo `DrumAPP`
2. Sezione **Pages**
3. **Source**: `Deploy from a branch`
4. **Branch**: `main` / `/ (root)`
5. Salva

Dopo un paio di minuti l'app è live su `https://pezzaliapp.github.io/DrumAPP/`.

---

## Sviluppo locale

Per testare in locale (il service worker richiede un server, non funziona con `file://`):

```bash
# Da dentro la cartella DrumAPP
python3 -m http.server 8080
# poi apri http://localhost:8080
```

Oppure con Node:

```bash
npx serve .
```

---

## Salvare e condividere i pattern

### Slot locali (A / B / C / D)
Quattro slot memorizzati nel browser (`localStorage`).

- **Tap breve** su uno slot vuoto → salva il pattern corrente lì dentro
- **Tap breve** su uno slot pieno → carica quel pattern
- **Tieni premuto** (mezzo secondo) su qualsiasi slot → salva il pattern corrente (sovrascrive se già pieno)

Gli slot pieni sono scuri con un puntino arancione in alto a destra. I pattern restano sul dispositivo corrente.

### Export / Import `.json`
- **EXPORT** scarica un file `drumapp-<timestamp>.json` contenente pattern e BPM.
- **IMPORT** apre un file picker e carica un `.json` precedentemente esportato.

Formato del file:
```json
{
  "version": 1,
  "bpm": 120,
  "pattern": {
    "kick":  [1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
    "snare": [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
    "hihat": [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
    "clap":  [0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0]
  }
}
```

### Share link
**SHARE** copia negli appunti un URL tipo:

```
https://pezzaliapp.github.io/DrumAPP/#8888-0808-aaaa-0800-78
```

Chi apre quel link vede partire la PWA con il pattern e il BPM già caricati. L'hash codifica ogni traccia in 4 caratteri esadecimali (16 bit = 16 step, 1 = attivo), seguiti dal BPM in hex.

---

## Architettura dei suoni

Tutti i suoni sono costruiti con nodi Web Audio standard. Nessun sample.

### Kick (cassa)
Oscillatore sinusoidale la cui **frequenza crolla** esponenzialmente da 165 Hz a 45 Hz in 120 ms. Un secondo oscillatore a 1200 Hz produce un **click** di attacco molto breve (25 ms). Ogni voce ha il proprio `GainNode` con inviluppo `exponentialRampToValueAtTime`.

### Snare (rullante)
Somma di due sorgenti:
- un oscillatore **triangolare a 220 Hz** (risonanza della pelle)
- un `AudioBufferSource` di **rumore bianco** filtrato passa-alto a 1 kHz (cordiera)

Entrambi con inviluppo di decadimento rapido.

### Hi-Hat (chiuso)
`AudioBufferSource` di rumore bianco → filtro **passa-alto a 7 kHz** → `GainNode` con decay in 55 ms.

### Clap (battito di mani)
Rumore bianco → filtro **passa-banda a 1.5 kHz** → `GainNode` con inviluppo **multi-burst** (tre impulsi ravvicinati a 0, 16 e 30 ms) + coda che scende a zero in 320 ms.

---

## Scheduler

Il motore del sequencer usa il pattern classico di Chris Wilson: un `setInterval` a 25 ms osserva l'`audioCtx.currentTime` e schedula tutti gli eventi audio che cadono nei successivi 100 ms. Questo garantisce timing stabile anche se la tab viene messa in background o il main thread è occupato.

L'intervallo di uno step è:

```
secondi_per_step = (60 / BPM) / 4
```

quindi a 120 BPM → 125 ms/step → 2 secondi per l'intero giro di 16.

---

## Struttura del progetto

```
DrumAPP/
├── index.html              ← markup PWA
├── style.css               ← estetica "Studio Press"
├── app.js                  ← sintesi + scheduler + UI
├── manifest.json           ← metadati PWA
├── service-worker.js       ← cache offline
├── icons/
│   ├── icon-192.png
│   ├── icon-512.png
│   ├── icon-192-maskable.png
│   └── icon-512-maskable.png
├── generate_icons.py       ← script Pillow per rigenerare le icone
├── python/                 ← versione desktop legacy
│   ├── drum_machine.py
│   └── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

---

## Design

L'interfaccia adotta un'estetica **"Studio Press"**: carta avorio, tipografia editoriale (Anton + IBM Plex Sans + VT323), pulsanti tattili con shadow di profondità, accento arancione. Evita di proposito i cliché del dark-mode neon delle app audio.

Font utilizzati via Google Fonts:
- **Anton** — display / label
- **VT323** — readout BPM (feel da display CRT)
- **IBM Plex Sans** — UI e micro-text

---

## Possibili estensioni future

- Swap pattern A/B/C/D in playback (song mode)
- Volume per traccia
- Tracce aggiuntive (Tom, Cowbell, Open Hi-Hat)
- Export del loop in `.wav` via `OfflineAudioContext`
- MIDI in/out tramite Web MIDI API
- Step "accent" (step con volume maggiore)
- Swing / shuffle regolabile

---

## Licenza

MIT — vedi [`LICENSE`](LICENSE).

© pezzaliapp

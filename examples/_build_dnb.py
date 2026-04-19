#!/usr/bin/env python3
"""
Genera examples/demo-dnb.json — Drum & Bass / Jungle a 170 BPM,
ispirato all'Amen Break (The Winstons, 1969) — il breakbeat più
campionato della storia.

Firma sonora del DNB / Amen:
  - BPM 170 (half-time feel = si conta come 85)
  - Swing 0 (il DNB sta sul grid; il feel viene dai pattern sincopati)
  - Humanize off (precisione chirurgica)
  - Kick SPARSO su step 1 e 11 (non four-on-the-floor, MAI)
  - Snare main su 5 e 13 + GHOST SNARE su step 7 = firma Amen
  - Hi-hat/ride 8th con velocity alternata
  - Decay breve ovunque (aggressività)
  - Roll finali al fill

Struttura (2 "bar" dell'Amen + variazioni):
  A "Amen Bar 1"    — pattern base classico
  B "Amen Bar 2"    — variazione con snare ghost + kick spostato (chop)
  C "Rollout"       — hi-hat con ratchet + ghost snare fitti (tensione)
  D "Big Break"     — roll 4x esplosivo + tom fill (drop)

Sequence: A B A B A B C A B D  (il classico loop-and-break del jungle)
"""

import json

MAX_STEPS = 32
NUM_TRACKS = 8
KICK, SNARE, HIHAT, OPENHAT, CLAP, TOM, RIM, COW = range(8)

def cell(vel=0.9, prob=100, ratch=1, nudge=0):
    return {"vel": vel, "prob": prob, "ratch": ratch, "nudge": nudge}

def empty_pattern():
    return [[None] * MAX_STEPS for _ in range(NUM_TRACKS)]

def set_steps(pattern, track, steps, **kwargs):
    for s in steps:
        pattern[track][s] = cell(**kwargs)

# =======================================================
# PATTERN A — "Amen Bar 1" (il pattern storico, prima misura)
#   Kick: 1 e 11  (indici 0 e 10)  — firma Amen
#   Snare: 5 e 13 (indici 4 e 12)  — back-beat classico
#   Ghost snare: 7 (indice 6)      — ★ la firma segreta dell'Amen
#   Hi-hat/ride: ogni 8vo con accenti alternati
# =======================================================
A = empty_pattern()
set_steps(A, KICK, [0, 10], vel=1.0)
set_steps(A, SNARE, [4, 12], vel=0.9)
# Ghost snare — la firma dell'Amen
A[SNARE][6] = cell(vel=0.4, prob=95)  # leggero per sentirlo come "tic"
# Hi-hat 8th (ride jazz) con accenti sui pari
for s in range(0, 16, 2):
    A[HIHAT][s] = cell(vel=0.75 if s % 4 == 0 else 0.55)

# =======================================================
# PATTERN B — "Amen Bar 2" (variazione della seconda misura)
#   Nel vero Amen la seconda bar sposta il kick e aggiunge ghost extra
# =======================================================
B = empty_pattern()
# Kick spostato — tipico "chopped" amen
set_steps(B, KICK, [0, 4], vel=1.0)  # primo + anticipo il secondo
# Snare: main sul 13 e un "crash" sul 9 invece del classico 5
B[SNARE][4]  = cell(vel=0.85)
B[SNARE][12] = cell(vel=0.9)
# Ghost snare multipli (caos controllato)
B[SNARE][6]  = cell(vel=0.4, prob=90)
B[SNARE][14] = cell(vel=0.45, prob=80)  # ghost prima del loop
# Hi-hat 8th + extra sui 16th per densità
for s in range(0, 16, 2):
    B[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)
# Accenti 16th sporadici
B[HIHAT][11] = cell(vel=0.65, prob=70)
B[HIHAT][15] = cell(vel=0.7, prob=80)
# Rimshot accent
B[RIM][2] = cell(vel=0.55, prob=60)

# =======================================================
# PATTERN C — "Rollout" (tensione: ratchet hi-hat, ghost fitti)
#   Usato tipicamente prima del drop del bass
# =======================================================
C = empty_pattern()
# Kick: pattern classico ma con ghost extra
set_steps(C, KICK, [0, 10], vel=1.0)
C[KICK][6] = cell(vel=0.7, prob=65)  # sub extra
# Snare main + ghost NOTES DENSI (dnb classic)
set_steps(C, SNARE, [4, 12], vel=0.9)
C[SNARE][6]  = cell(vel=0.4, prob=90)
C[SNARE][7]  = cell(vel=0.35, prob=55)  # ghost doppia
C[SNARE][10] = cell(vel=0.35, prob=60)
C[SNARE][14] = cell(vel=0.4, prob=75)
# Hi-hat con RATCHET (triplette in mezzo al ride)
for s in range(0, 16, 2):
    C[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)
C[HIHAT][11] = cell(vel=0.7, ratch=2)   # tripletta
C[HIHAT][13] = cell(vel=0.75, ratch=2)
C[HIHAT][15] = cell(vel=0.8, ratch=3)   # roll pre-drop
# Open hat accento
C[OPENHAT][10] = cell(vel=0.6)

# =======================================================
# PATTERN D — "Big Break" (drop / fill esplosivo)
#   Il momento Amen classico: snare roll 4x + tom fill ascendente
# =======================================================
D = empty_pattern()
set_steps(D, KICK, [0], vel=1.0)
D[KICK][8] = cell(vel=0.9)  # sub al centro
# Snare roll 4x sullo step 15 = classico Amen fill
set_steps(D, SNARE, [4, 12], vel=0.9)
D[SNARE][13] = cell(vel=0.7, ratch=2)
D[SNARE][14] = cell(vel=0.85, ratch=3)
D[SNARE][15] = cell(vel=1.0, ratch=4)  # ★ esplosione finale
# Hi-hat denso con ratchet crescenti
for s in range(0, 16, 2):
    D[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.45)
D[HIHAT][5]  = cell(vel=0.7, ratch=2)
D[HIHAT][9]  = cell(vel=0.75, ratch=2)
D[HIHAT][11] = cell(vel=0.8, ratch=3)
# Tom fill ASCENDENTE (crescendo di tensione)
D[TOM][6]  = cell(vel=0.7, nudge=-5)
D[TOM][7]  = cell(vel=0.8)
D[TOM][10] = cell(vel=0.85)
D[TOM][11] = cell(vel=0.95)
# Rim accent
D[RIM][2] = cell(vel=0.6, prob=70)

# =======================================================
# TRACK PARAMS — mix stile DNB/jungle
#   Kick: sub profondo ma non 808 (decay medio, non lunghissimo)
#   Snare: aggressivo, pitch leggermente alto per "snap"
#   Hi-hat: brillante e CORTO (il DNB è preciso, no sbavature)
# =======================================================
track_params = [
    # KICK — sub, pitch basso ma non estremo, decay medio
    {"volume": 0.9,  "mute": False, "solo": False, "pitch": -3, "decay": 1.2,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # SNARE — "snap" aggressivo, pitch leggermente alto
    {"volume": 0.82, "mute": False, "solo": False, "pitch": 1, "decay": 0.9,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # HI-HAT — brillante, decay molto corto (precisione)
    {"volume": 0.65, "mute": False, "solo": False, "pitch": 1, "decay": 0.55,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.3},
    # OPEN HH — stesso lato del chiuso
    {"volume": 0.55, "mute": False, "solo": False, "pitch": 1, "decay": 1.1,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.3},
    # CLAP — mute (l'Amen usa solo snare, niente clap)
    {"volume": 0.6,  "mute": True,  "solo": False, "pitch": 0, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.3},
    # TOM — pitch alto per fill ascendenti (tensione)
    {"volume": 0.75, "mute": False, "solo": False, "pitch": 3, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # RIMSHOT — sinistra, accenti
    {"volume": 0.65, "mute": False, "solo": False, "pitch": 0, "decay": 0.7,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.4},
    # COWBELL — mute
    {"volume": 0.5,  "mute": True,  "solo": False, "pitch": 0, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
]

# =======================================================
# SONG SEQUENCE — struttura jungle/DNB classica
#   2 bar Amen × 3 volte (A B A B A B) · Rollout (C) · Amen (A B) · BREAK (D)
# =======================================================
song = ["A", "B", "A", "B", "A", "B", "C", "A", "B", "D"]

demo = {
    "version": 2,
    "exportedAt": "2026-04-19T18:58:00Z",
    "bpm": 170,
    "swing": 0,         # DNB sta sul grid
    "patternLength": 16,
    "humanize": False,  # precisione chirurgica
    "trackParams": track_params,
    "patterns": {"A": A, "B": B, "C": C, "D": D},
    "songSequence": song,
    "_meta": {
        "title": "DNB / Amen Break — DrumAPP Pro",
        "genre": "Drum & Bass / Jungle (Amen Break-ispirato)",
        "history": "L'Amen Break è un drum solo di 4 secondi da 'Amen, Brother' dei The Winstons (1969). E' stato campionato in migliaia di brani jungle/DNB/hip-hop. La sua firma: kick sparso, snare backbeat + GHOST NOTE sul 7, ride 8th.",
        "key_features": [
            "Ghost snare al step 7 (firma Amen): barra velocity molto bassa, quasi invisibile ma fondamentale al feel",
            "Kick solo su 1 e 11 — mai four-on-the-floor in DNB",
            "Snare roll 4x sullo step 15 di Pattern D — il momento iconico del fill",
            "Tom fill ascendente con nudge e velocity crescenti (pattern C+D)",
            "Hi-hat decay 0.55x — precisione massima, niente risonanze",
        ],
        "instructions": [
            "1) IMPORT questo file",
            "2) Attiva SONG (fondamentale per sentire la variazione A↔B dell'Amen)",
            "3) PLAY",
            "4) Focus sull'ascolto: il ghost snare al 7 è il dettaglio che fa tutto",
            "5) Prova: seleziona traccia SNARE, click su SOLO. Senti isolato il pattern Amen classico",
        ],
    },
}

out_path = "/home/claude/DrumAPP/examples/demo-dnb.json"
with open(out_path, "w") as f:
    json.dump(demo, f, indent=2)

hits = {name: sum(1 for t in p for s in t if s) for name, p in [("A",A),("B",B),("C",C),("D",D)]}
print(f"DNB/Amen generato: {out_path}")
print(f"  Patterns: A={hits['A']} B={hits['B']} C={hits['C']} D={hits['D']} hits")
print(f"  Sequence: {' → '.join(song)}")
print(f"  BPM 170 (half-time 85) · No swing · No humanize · Clap+Cow mute")
total_sec = len(song) * 16 / (170 / 60 * 4)
print(f"  Durata: {total_sec:.1f}s")

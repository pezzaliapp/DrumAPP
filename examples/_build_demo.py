#!/usr/bin/env python3
"""
Genera examples/demo-house.json — una mini-traccia house/techno
che dimostra tutte le feature Pro di DrumAPP: velocity, probability,
ratchet, nudge, pan, pitch, decay, filter, song mode.

Struttura:
  - 124 BPM, swing 8%, humanize on
  - Pattern A "Intro Minimal": kick + clap + hi-hat off
  - Pattern B "Verse Groove":  + cowbell + open hat + rim (prob)
  - Pattern C "Build-up":      hi-hat 16th con ratchet, snare roll
  - Pattern D "Drop Full":     tutto + cowbell R60, rim L40, tom
  - Sequence: A A B B A B C D D B  (~40 sec)
"""

import json

MAX_STEPS = 32
NUM_TRACKS = 8

# Indici tracce (come in TRACK_DEFS)
KICK, SNARE, HIHAT, OPENHAT, CLAP, TOM, RIM, COW = range(8)

def cell(vel=0.9, prob=100, ratch=1, nudge=0):
    """Crea una cella attiva del sequencer"""
    return {"vel": vel, "prob": prob, "ratch": ratch, "nudge": nudge}

def empty_pattern():
    return [[None] * MAX_STEPS for _ in range(NUM_TRACKS)]

def set_steps(pattern, track, steps, **kwargs):
    """Attiva `steps` (indici 0-based) sulla `track`"""
    for s in steps:
        pattern[track][s] = cell(**kwargs)

# =======================================================
# PATTERN A — "Intro Minimal"
#   Partenza pulita: kick 4/4, clap back-beat, hi-hat off-beat
# =======================================================
A = empty_pattern()
set_steps(A, KICK,  [0, 4, 8, 12], vel=1.0)
set_steps(A, CLAP,  [4, 12], vel=0.85)
set_steps(A, HIHAT, [2, 6, 10, 14], vel=0.65)  # off-beat
set_steps(A, OPENHAT, [6, 14], vel=0.7)

# =======================================================
# PATTERN B — "Verse Groove"
#   Aggiunge hi-hat ottavi con dinamica, cowbell, rim (probability)
# =======================================================
B = empty_pattern()
set_steps(B, KICK,  [0, 4, 8, 12], vel=1.0)
set_steps(B, CLAP,  [4, 12], vel=0.85)
# Hi-hat ottavi con velocity alternata (accenti sui pari)
for s in range(0, 16, 2):
    B[HIHAT][s] = cell(vel=0.9)
for s in range(1, 16, 2):
    B[HIHAT][s] = cell(vel=0.55)
set_steps(B, OPENHAT, [6, 14], vel=0.7)
# Cowbell in back-beat (layer col clap)
set_steps(B, COW, [4, 12], vel=0.7)
# Rim sporadico, probability 65%
B[RIM][10] = cell(vel=0.75, prob=65)
B[RIM][14] = cell(vel=0.7, prob=50)

# =======================================================
# PATTERN C — "Build-up"
#   Tensione: hi-hat 16th, ratchet sui fill, snare roll finale,
#   kick "rotto" con probability negli ultimi step
# =======================================================
C = empty_pattern()
# Kick: primi due solidi, poi probability che scende
C[KICK][0]  = cell(vel=1.0)
C[KICK][4]  = cell(vel=1.0)
C[KICK][8]  = cell(vel=1.0, prob=85)
C[KICK][12] = cell(vel=1.0, prob=60)
set_steps(C, CLAP, [4, 12], vel=0.85)
# Hi-hat: tutti e 16 i step, ratchet 2x sugli ultimi 2 (fill)
for s in range(16):
    C[HIHAT][s] = cell(vel=0.6 + (0.3 if s % 2 == 0 else 0))
C[HIHAT][14] = cell(vel=0.7, ratch=2)
C[HIHAT][15] = cell(vel=0.8, ratch=3)
# Snare roll finale (ratchet 4x sul 15)
C[SNARE][15] = cell(vel=0.9, ratch=4)
# Tom ascendente come tensione
C[TOM][10] = cell(vel=0.75, nudge=-10)
C[TOM][12] = cell(vel=0.85)
C[TOM][14] = cell(vel=0.95)

# =======================================================
# PATTERN D — "Drop Full"
#   Groove completo con pan spaziale, nudge per sentire umano
# =======================================================
D = empty_pattern()
set_steps(D, KICK, [0, 4, 8, 12], vel=1.0)
set_steps(D, SNARE, [4, 12], vel=0.85)
set_steps(D, CLAP, [4, 12], vel=0.7)  # layer col snare
# Hi-hat 16th con velocity alternata e un nudge leggero sugli off
for s in range(0, 16, 2):
    D[HIHAT][s] = cell(vel=0.85)
for s in range(1, 16, 2):
    D[HIHAT][s] = cell(vel=0.55, nudge=5)  # leggero ritardo
# Open hat sugli off-beat principali
set_steps(D, OPENHAT, [2, 6, 10, 14], vel=0.7)
# Cowbell in 16esimi dispari (feel latino-house)
set_steps(D, COW, [2, 6, 10, 14], vel=0.7)
# Rimshot su syncopation
D[RIM][3] = cell(vel=0.75, prob=80)
D[RIM][11] = cell(vel=0.7, prob=80)
# Tom occasionale
D[TOM][14] = cell(vel=0.8, prob=50)

# =======================================================
# TRACK PARAMS — pan / pitch / decay per ogni voce
#   Simula un mix drum-kit reale con spatializzazione stereo
# =======================================================
track_params = [
    # Kick: centro, pitch basso per profondità, decay lungo
    {"volume": 0.9,  "mute": False, "solo": False, "pitch": -2, "decay": 1.5,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # Snare: centro, decay medio
    {"volume": 0.82, "mute": False, "solo": False, "pitch": 0,  "decay": 0.9,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # Hi-hat: leggermente a destra, decay corto
    {"volume": 0.65, "mute": False, "solo": False, "pitch": 0,  "decay": 0.7,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.3},
    # Open HH: destra (stesso lato del chiuso)
    {"volume": 0.6,  "mute": False, "solo": False, "pitch": 0,  "decay": 1.1,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.3},
    # Clap: sinistra
    {"volume": 0.75, "mute": False, "solo": False, "pitch": 0,  "decay": 1.1,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.4},
    # Tom: centro, pitch leggermente alto (tensione)
    {"volume": 0.7,  "mute": False, "solo": False, "pitch": 3,  "decay": 1.2,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # Rimshot: sinistra
    {"volume": 0.7,  "mute": False, "solo": False, "pitch": 0,  "decay": 0.8,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.5},
    # Cowbell: destra, pan marcato
    {"volume": 0.55, "mute": False, "solo": False, "pitch": 0,  "decay": 1.0,
     "filterType": "highpass", "filterCutoff": 0.35, "filterQ": 1.0, "pan": 0.6},
]

# =======================================================
# SONG SEQUENCE — struttura della mini-traccia (~40 sec a 124 BPM)
#   Intro (A A) · Verse (B B) · Ritorno (A) · Groove (B) ·
#   Build (C) · Drop (D D) · Outro (B)
# =======================================================
song = ["A", "A", "B", "B", "A", "B", "C", "D", "D", "B"]

# =======================================================
# ASSEMBLA IL SET COMPLETO
# =======================================================
demo = {
    "version": 2,
    "exportedAt": "2026-04-19T15:30:00Z",
    "bpm": 124,
    "swing": 8,
    "patternLength": 16,
    "humanize": True,
    "trackParams": track_params,
    "patterns": {"A": A, "B": B, "C": C, "D": D},
    "songSequence": song,
    "_meta": {
        "title": "House Demo — DrumAPP Pro",
        "description": "Mini-traccia di ~40 secondi che mostra velocity, probability, ratchet, nudge, pan e song mode.",
        "instructions": [
            "1) Clicca IMPORT e seleziona questo file",
            "2) Attiva SONG nella modebar",
            "3) Premi PLAY (o SPACE) e ascolta i 10 pattern in sequenza",
            "4) Prova a variare: cambia pitch del kick, aggiungi ratchet agli hi-hat, smanetta",
        ],
    },
}

# Salva JSON
out_path = "/home/claude/DrumAPP/examples/demo-house.json"
with open(out_path, "w") as f:
    json.dump(demo, f, indent=2)

print(f"Demo generata: {out_path}")
print(f"  Patterns: A={sum(1 for t in A for s in t if s)} hits, "
      f"B={sum(1 for t in B for s in t if s)} hits, "
      f"C={sum(1 for t in C for s in t if s)} hits, "
      f"D={sum(1 for t in D for s in t if s)} hits")
print(f"  Song sequence: {' → '.join(song)}")
print(f"  BPM: 124 · Swing: 8% · Humanize: ON · Filter HP su cowbell")

# Calcola durata stimata
steps_per_sec = 124 / 60 * 4  # 16esimi per secondo
total_steps = len(song) * 16
total_sec = total_steps / steps_per_sec
print(f"  Durata: {total_sec:.1f}s")

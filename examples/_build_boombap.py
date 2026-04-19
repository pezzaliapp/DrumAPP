#!/usr/bin/env python3
"""
Genera examples/demo-boombap.json — boom bap anni '90 stile J Dilla / Pete Rock.

Firma sonora del boom bap:
  - BPM 90 (a volte 86-92)
  - SWING ALTO (~50-55%) — questa è la killer feature del genere
  - HUMANIZE ON — il feel "lazy" dietro il beat è la firma di Dilla
  - Kick + snare classici su backbeat, ma con sincopazioni MPC-style
  - Hi-hat vintage (decay corto, pitch basso per il vibe lo-fi)
  - Rim shot per accenti al posto di click digitali
  - Ghost notes per il feel jazzy

Struttura:
  A "Lay Back"     — pattern base, kick sincopato alla Dilla
  B "Ghost Groove" — + ghost snare + open hat sporadico
  C "Breakdown"    — respiro, rim shot al posto di alcune snare, tom fill
  D "Outro"        — variazione con snare ratchet leggero, risoluzione

Sequence: A A B B A B C D (8 bar · ~21 sec a 90 BPM con swing)
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
# PATTERN A — "Lay Back"
#   Kick sincopato (step 1 e 7, non 4/4) = feel alla Dilla
#   Snare classico backbeat (5/13)
#   Hi-hat ottavi — lo swing sul groove globale fa il resto
# =======================================================
A = empty_pattern()
# Kick: step 1 e 7 (indici 0 e 6) — sincopato
set_steps(A, KICK, [0, 6], vel=1.0)
# Snare backbeat
set_steps(A, SNARE, [4, 12], vel=0.85)
# Hi-hat ottavi (il vero groove lo fa lo swing globale 50%)
for s in range(0, 16, 2):
    A[HIHAT][s] = cell(vel=0.75 if s % 4 == 0 else 0.55)

# =======================================================
# PATTERN B — "Ghost Groove"
#   Base + ghost notes sul snare + kick extra con probability + open hat
# =======================================================
B = empty_pattern()
set_steps(B, KICK, [0, 6], vel=1.0)
# Kick ghost al 10 (prob 60 = variazione casuale)
B[KICK][10] = cell(vel=0.75, prob=60)
# Snare backbeat + ghost al 7 e 11 (classico del boom bap)
set_steps(B, SNARE, [4, 12], vel=0.85)
B[SNARE][7]  = cell(vel=0.35, prob=75)  # ghost
B[SNARE][11] = cell(vel=0.3,  prob=55)  # ghost ancora più sporadica
# Hi-hat ottavi con velocity alternata
for s in range(0, 16, 2):
    B[HIHAT][s] = cell(vel=0.75 if s % 4 == 0 else 0.55)
# Open hat sporadico sull'ultimo off-beat
B[OPENHAT][14] = cell(vel=0.6)

# =======================================================
# PATTERN C — "Breakdown"
#   Respiro: meno elementi, rim shot al posto di qualche snare,
#   tom fill leggero per transizione
# =======================================================
C = empty_pattern()
set_steps(C, KICK, [0, 6], vel=1.0)
# Snare solo sul primo backbeat, rim shot sul secondo (variazione)
C[SNARE][4] = cell(vel=0.85)
C[RIM][12]  = cell(vel=0.75)
# Ghost snare
C[SNARE][7] = cell(vel=0.35, prob=60)
# Hi-hat più sparso (solo sui 4 beat principali)
for s in [0, 4, 8, 12]:
    C[HIHAT][s] = cell(vel=0.75)
# Tom fill leggero (transition)
C[TOM][14] = cell(vel=0.7, nudge=-8)  # leggermente prima del beat

# =======================================================
# PATTERN D — "Outro Variation"
#   Snare roll leggero (ratchet 2x, non aggressivo come trap/dnb)
#   Risoluzione classica con tutti gli elementi insieme
# =======================================================
D = empty_pattern()
set_steps(D, KICK, [0, 6], vel=1.0)
D[KICK][13] = cell(vel=0.8, prob=70)  # kick extra per risoluzione
set_steps(D, SNARE, [4, 12], vel=0.85)
# Ghost snare denso + roll leggero finale
D[SNARE][7]  = cell(vel=0.4, prob=80)
D[SNARE][11] = cell(vel=0.4, prob=70)
D[SNARE][15] = cell(vel=0.8, ratch=2)  # roll leggero boom bap (non 4x aggressivo)
# Hi-hat ottavi + open hat sui finali
for s in range(0, 16, 2):
    D[HIHAT][s] = cell(vel=0.75 if s % 4 == 0 else 0.55)
set_steps(D, OPENHAT, [6, 14], vel=0.6)
# Rim per accenti jazz
D[RIM][3]  = cell(vel=0.55, prob=60)
D[RIM][11] = cell(vel=0.55, prob=60)

# =======================================================
# TRACK PARAMS — mix vintage boom bap
#   Kick: decay medio-lungo (non 808 profondo)
#   Hi-hat: pitch basso, decay corto (vibe lo-fi vintage)
#   Rim: accentato per il feel jazz
# =======================================================
track_params = [
    # KICK — lievemente grave, decay medio
    {"volume": 0.9,  "mute": False, "solo": False, "pitch": -2, "decay": 1.3,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # SNARE — centro, "polposo"
    {"volume": 0.8,  "mute": False, "solo": False, "pitch": 0, "decay": 1.1,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # HI-HAT — pitch basso, decay CORTO per feel vintage lo-fi
    {"volume": 0.6,  "mute": False, "solo": False, "pitch": -2, "decay": 0.7,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.2},
    # OPEN HH — stessa cifra stilistica
    {"volume": 0.55, "mute": False, "solo": False, "pitch": -2, "decay": 1.2,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.2},
    # CLAP — mute (il boom bap usa più snare puro, non clap layered)
    {"volume": 0.6,  "mute": True,  "solo": False, "pitch": 0, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.3},
    # TOM — centro, pitch leggermente alto per fill
    {"volume": 0.7,  "mute": False, "solo": False, "pitch": 2, "decay": 1.1,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # RIMSHOT — sinistra, accenti jazz
    {"volume": 0.7,  "mute": False, "solo": False, "pitch": 0, "decay": 0.8,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.4},
    # COWBELL — mute (fuori contesto)
    {"volume": 0.5,  "mute": True,  "solo": False, "pitch": 0, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
]

# =======================================================
# SONG SEQUENCE — struttura boom bap classica
#   Layback (A A) · Groove (B B) · Ritorno (A B) · Breakdown (C) · Outro (D)
# =======================================================
song = ["A", "A", "B", "B", "A", "B", "C", "D"]

demo = {
    "version": 2,
    "exportedAt": "2026-04-19T18:55:00Z",
    "bpm": 90,
    "swing": 52,       # ★ KILLER FEATURE del boom bap
    "patternLength": 16,
    "humanize": True,  # ★ feel "lazy" alla Dilla
    "trackParams": track_params,
    "patterns": {"A": A, "B": B, "C": C, "D": D},
    "songSequence": song,
    "_meta": {
        "title": "Boom Bap — DrumAPP Pro",
        "genre": "Hip-Hop anni '90 (J Dilla / Pete Rock / DJ Premier)",
        "key_features": [
            "Swing 52% — il groove del genere nasce tutto qui",
            "Humanize ON — piccole variazioni di timing/velocity per feel 'lazy'",
            "Hi-hat pitch -2 e decay corto — timbrica vintage lo-fi",
            "Ghost snare con probability 55-80% — variazioni jazz sulla ripetizione",
            "Rim shot al posto del click — accenti alla Pete Rock",
            "Clap muted — nel boom bap si usa solo snare puro",
        ],
        "instructions": [
            "1) IMPORT questo file",
            "2) Attiva SONG nella modebar",
            "3) PLAY",
            "4) Prova: togli lo swing (porta a 0) e senti che tutto diventa subito robotico",
            "5) Per feel ancora più vintage: PITCH del kick a -4 e DECAY del hi-hat a 0.5",
        ],
    },
}

out_path = "/home/claude/DrumAPP/examples/demo-boombap.json"
with open(out_path, "w") as f:
    json.dump(demo, f, indent=2)

hits = {name: sum(1 for t in p for s in t if s) for name, p in [("A",A),("B",B),("C",C),("D",D)]}
print(f"Boom bap generato: {out_path}")
print(f"  Patterns: A={hits['A']} B={hits['B']} C={hits['C']} D={hits['D']} hits")
print(f"  Sequence: {' → '.join(song)}")
print(f"  BPM 90 · Swing 52% · Humanize ON · Clap+Cowbell mute")
total_sec = len(song) * 16 / (90 / 60 * 4)
print(f"  Durata: {total_sec:.1f}s")

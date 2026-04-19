#!/usr/bin/env python3
"""
Genera examples/demo-trap.json — trap beat a 140 BPM in stile moderno.

Firma sonora del trap:
  - Kick 808 pitchato basso, pattern sincopato (non four-on-the-floor)
  - Snare + clap layered su step 5 e 13 (back-beat)
  - Hi-hat ottavi con RATCHET 2x/3x/4x per le classiche triplette
  - Open hat sporadico per respiro
  - Humanize off (trap è quantizzato, il feel viene dalle ratchet)
  - Swing 0 (no shuffle, si sta sul grid)

Struttura (4 pattern):
  A "Intro" — solo base scarna
  B "Verse" — base + triplette hi-hat
  C "Hype" — roll aggressivi + rim + ghost kick
  D "Fill"  — tutto al massimo, snare roll finale

Sequence: A A B B C B B C C D (17 sec)
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
# PATTERN A — "Intro" (skeleton: 808 kick + snare + hi-hat 8th)
# =======================================================
A = empty_pattern()
# Classico pattern 808 sincopato: 1 - - - - - 7 - 9 - - - - - - -
# In indici 0-based: 0, 6, 8 (poi replica sulla seconda metà con variazione)
set_steps(A, KICK, [0, 6, 8, 10], vel=1.0)
# Snare back-beat (step 5 e 13 umani, quindi indici 4 e 12)
set_steps(A, SNARE, [4, 12], vel=0.9)
# Hi-hat ottavi (ogni 2 step) con velocity alternata
for s in range(0, 16, 2):
    A[HIHAT][s] = cell(vel=0.85 if s % 4 == 0 else 0.7)

# =======================================================
# PATTERN B — "Verse" (+ clap layer, triplette hi-hat, open hat)
# =======================================================
B = empty_pattern()
set_steps(B, KICK, [0, 6, 8, 10], vel=1.0)
set_steps(B, SNARE, [4, 12], vel=0.9)
# Clap layered col snare (classica cosa trap)
set_steps(B, CLAP, [4, 12], vel=0.7)
# Hi-hat 16th con ratchet su alcuni step (triplette)
for s in range(16):
    B[HIHAT][s] = cell(vel=0.55 + (0.25 if s % 2 == 0 else 0))
# Ratchet 2x qui e là (il "ta-ta" veloce del trap)
B[HIHAT][6]  = cell(vel=0.75, ratch=2)
B[HIHAT][10] = cell(vel=0.75, ratch=2)
B[HIHAT][14] = cell(vel=0.8, ratch=3)  # fine misura, tripletta
# Open hat respiri
set_steps(B, OPENHAT, [2, 14], vel=0.6)

# =======================================================
# PATTERN C — "Hype" (ghost kick, rim, hi-hat roll aggressivo)
# =======================================================
C = empty_pattern()
# Kick classico + ghost notes (step 3 e 11 con probability)
set_steps(C, KICK, [0, 6, 8, 10], vel=1.0)
C[KICK][3]  = cell(vel=0.7, prob=60)  # ghost note
C[KICK][11] = cell(vel=0.7, prob=70)
set_steps(C, SNARE, [4, 12], vel=0.9)
set_steps(C, CLAP, [4, 12], vel=0.75)
# Hi-hat: alterna ratchet 2x e 3x per un groove trap caratteristico
for s in range(16):
    C[HIHAT][s] = cell(vel=0.55 + (0.2 if s % 2 == 0 else 0))
C[HIHAT][2]  = cell(vel=0.75, ratch=2)
C[HIHAT][6]  = cell(vel=0.8,  ratch=3)  # tripletta
C[HIHAT][10] = cell(vel=0.75, ratch=2)
C[HIHAT][14] = cell(vel=0.85, ratch=3)
C[HIHAT][15] = cell(vel=0.9,  ratch=4)  # roll finale
# Rim shot per accent
set_steps(C, RIM, [2, 11], vel=0.7)
set_steps(C, OPENHAT, [14], vel=0.65)

# =======================================================
# PATTERN D — "Fill" (roll massimi, snare 4x, drop)
# =======================================================
D = empty_pattern()
# Kick meno denso, crea spazio per il fill
C_kick = [0, 6, 8]
set_steps(D, KICK, C_kick, vel=1.0)
D[KICK][13] = cell(vel=0.8, prob=75)  # ghost prima del fill
set_steps(D, SNARE, [4, 12], vel=0.9)
# Snare ROLL finale (4x ratchet) — signature del trap fill
D[SNARE][14] = cell(vel=0.9, ratch=3)
D[SNARE][15] = cell(vel=1.0, ratch=4)  # roll esplosivo
set_steps(D, CLAP, [4, 12], vel=0.75)
# Hi-hat: quasi tutto ratchet, piena tensione
for s in range(16):
    D[HIHAT][s] = cell(vel=0.55 + (0.2 if s % 2 == 0 else 0))
D[HIHAT][4]  = cell(vel=0.75, ratch=2)
D[HIHAT][6]  = cell(vel=0.8,  ratch=3)
D[HIHAT][8]  = cell(vel=0.8,  ratch=2)
D[HIHAT][10] = cell(vel=0.85, ratch=3)
D[HIHAT][12] = cell(vel=0.85, ratch=2)
D[HIHAT][14] = cell(vel=0.9,  ratch=4)  # fill pre-drop
D[HIHAT][15] = cell(vel=0.95, ratch=4)
# Open hat e rim per texture
set_steps(D, OPENHAT, [6, 10], vel=0.65)
set_steps(D, RIM, [7, 9, 11], vel=0.6, prob=70)
# Tom per tensione tipo "kick sub" nel fill
set_steps(D, TOM, [14, 15], vel=0.8)

# =======================================================
# TRACK PARAMS — mix typicamente trap
#   Kick 808: pitch -5 (profondo), decay 1.8x (lungo sub),
#   Hi-hat: corto e brillante,
#   Cowbell: muted (non si usa nel trap moderno)
# =======================================================
track_params = [
    # KICK — 808 profondo, decay lungo, centro
    {"volume": 0.95, "mute": False, "solo": False, "pitch": -5, "decay": 1.8,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # SNARE — centro, decay corto per il "crack"
    {"volume": 0.8,  "mute": False, "solo": False, "pitch": 1, "decay": 0.85,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # HI-HAT — leggermente a destra, decay corto
    {"volume": 0.65, "mute": False, "solo": False, "pitch": 2, "decay": 0.6,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.25},
    # OPEN HH — destra (stesso asse)
    {"volume": 0.55, "mute": False, "solo": False, "pitch": 2, "decay": 1.3,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.25},
    # CLAP — sinistra leggero (crea larghezza stereo col snare)
    {"volume": 0.7,  "mute": False, "solo": False, "pitch": 0, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.3},
    # TOM — centro, pitch alto per il fill
    {"volume": 0.7,  "mute": False, "solo": False, "pitch": 2, "decay": 1.1,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # RIMSHOT — sinistra, secco
    {"volume": 0.6,  "mute": False, "solo": False, "pitch": 0, "decay": 0.7,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.4},
    # COWBELL — mute (non usata)
    {"volume": 0.5,  "mute": True,  "solo": False, "pitch": 0, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
]

# =======================================================
# SONG SEQUENCE — struttura di una strofa trap
#   Intro sparsa · verse pocket · hype · drop con fill
# =======================================================
song = ["A", "A", "B", "B", "C", "B", "B", "C", "C", "D"]

# =======================================================
# ASSEMBLA
# =======================================================
demo = {
    "version": 2,
    "exportedAt": "2026-04-19T18:45:00Z",
    "bpm": 140,
    "swing": 0,        # trap non swinga
    "patternLength": 16,
    "humanize": False, # trap è quantizzato, il feel viene dai ratchet
    "trackParams": track_params,
    "patterns": {"A": A, "B": B, "C": C, "D": D},
    "songSequence": song,
    "_meta": {
        "title": "Trap Beat — DrumAPP Pro",
        "genre": "Trap / Hip-Hop moderno",
        "bpm_note": "140 BPM si sente come 70 (half-time feel tipico del trap)",
        "instructions": [
            "1) IMPORT di questo file",
            "2) Attiva SONG nella modebar (altrimenti loopa solo A)",
            "3) PLAY",
            "4) Il kick è -5 semitoni: per un 808 ancora piu' profondo, abbassa PITCH del kick a -8",
            "5) Prova: disattiva HI-HAT mute, metti SOLO, senti la tripletta (ratchet) che fa tutto il groove",
        ],
    },
}

out_path = "/home/claude/DrumAPP/examples/demo-trap.json"
with open(out_path, "w") as f:
    json.dump(demo, f, indent=2)

# Stats
hits = {name: sum(1 for t in p for s in t if s) for name, p in [("A",A),("B",B),("C",C),("D",D)]}
print(f"Demo trap generata: {out_path}")
print(f"  Patterns: A={hits['A']} B={hits['B']} C={hits['C']} D={hits['D']} hits")
print(f"  Song sequence: {' → '.join(song)}")
print(f"  BPM: 140 (half-time = 70 feel) · Kick pitch -5 (808) · Cowbell mute")
steps_per_sec = 140 / 60 * 4
total_sec = len(song) * 16 / steps_per_sec
print(f"  Durata: {total_sec:.1f}s")

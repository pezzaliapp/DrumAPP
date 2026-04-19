#!/usr/bin/env python3
"""
Genera examples/demo-makesomenoise.json — beat NYC hip-hop ispirato
a "Make Some Noise" (Beastie Boys, 2011).

⚠️ Chiarimento: questo è un pattern ORIGINALE nello STILE del brano,
non una cover né una riproduzione. Il brano reale è coperto da
copyright (lyrics, sample, synth, arrangement). Una drum pattern
(kick su 1, snare sul backbeat) è grammatica musicale generale
e non costituisce riproduzione della composizione.

Firma sonora del pattern:
  - BPM 105 (territorio Make Some Noise)
  - Swing 12% (leggero, non boom bap pesante — la track ha feel quasi dritto)
  - Humanize on leggero (feel umano ma la track è pulita/compressa)
  - Kick DOPPIO (1 + "1-and" feel) — firma del brano
  - Snare backbeat PUNCHY con ghost notes
  - Rim shot come "shaker" sui 16th off-beat — vibe vintage Beastie
  - Cowbell per gli accenti signature NYC
  - Tom per i fill "live" (loro registravano drum fill veri)

Struttura:
  A "Intro Kick"    — skeleton, il kick doppio che apre il pezzo
  B "Verse Pocket"  — pieno: rim shot shaker, cowbell, open hat
  C "Hook Punchy"   — doppio snare, cowbell piu' denso, energia alta
  D "Break Fill"    — tom fill + drop per transizione

Sequence: A B B C B C C D  (~20 sec a 105 BPM)
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
# PATTERN A — "Intro Kick"
#   Il KICK DOPPIO alla Beastie: 1 + subito dopo
#   Feel: "boom-BOOM ... ta ... boom-BOOM ... ta"
# =======================================================
A = empty_pattern()
# Kick pattern: step 0 + 2 (doppio iniziale), step 8 + 10 (doppio a metà)
set_steps(A, KICK, [0, 2, 8, 10], vel=1.0)
# Snare backbeat classico
set_steps(A, SNARE, [4, 12], vel=0.9)
# Hi-hat 8th con accento sui downbeat
for s in range(0, 16, 2):
    A[HIHAT][s] = cell(vel=0.8 if s % 4 == 0 else 0.6)

# =======================================================
# PATTERN B — "Verse Pocket" (il groove del verso)
#   Aggiunge rim shot come shaker sui 16th off + cowbell + open hat
# =======================================================
B = empty_pattern()
set_steps(B, KICK, [0, 2, 8, 10], vel=1.0)
set_steps(B, SNARE, [4, 12], vel=0.9)
# Ghost snare leggera
B[SNARE][11] = cell(vel=0.35, prob=65)
# Hi-hat 8th
for s in range(0, 16, 2):
    B[HIHAT][s] = cell(vel=0.8 if s % 4 == 0 else 0.6)
# Rim shot come shaker: step dispari (off-beat 16th) — simula il tamburello
set_steps(B, RIM, [1, 3, 5, 7, 9, 11, 13, 15], vel=0.35)
# Cowbell su 1 e 9 (downbeat accent signature)
set_steps(B, COW, [0, 8], vel=0.55)
# Open hat sporadico per respiro
B[OPENHAT][14] = cell(vel=0.65)

# =======================================================
# PATTERN C — "Hook Punchy" (il ritornello spingente)
#   Double snare + cowbell piu' denso + kick extra
# =======================================================
C = empty_pattern()
# Kick extra per energia
set_steps(C, KICK, [0, 2, 8, 10], vel=1.0)
C[KICK][6] = cell(vel=0.85, prob=75)  # kick extra prima del backbeat
# Snare backbeat + double snare al 13 (caratteristico del ritornello punchy)
set_steps(C, SNARE, [4, 12], vel=0.95)
C[SNARE][13] = cell(vel=0.7)  # "crack-crack" tipo Beastie
# Clap layered col snare per energia (nel hook)
set_steps(C, CLAP, [4, 12], vel=0.65)
# Hi-hat 8th piu' aggressivo
for s in range(0, 16, 2):
    C[HIHAT][s] = cell(vel=0.85 if s % 4 == 0 else 0.7)
# Cowbell anche sugli off-beat (densita' piena)
set_steps(C, COW, [0, 4, 8, 12], vel=0.6)
# Rim shot sparso
set_steps(C, RIM, [3, 7, 11, 15], vel=0.4)
# Open hat
set_steps(C, OPENHAT, [6, 14], vel=0.7)

# =======================================================
# PATTERN D — "Break Fill" (transizione / fine ritornello)
#   Tom fill "live" stile Beastie + drop momentaneo
# =======================================================
D = empty_pattern()
# Kick solo sui 3 primi beat, lascia spazio al fill finale
set_steps(D, KICK, [0, 2, 8], vel=1.0)
# Snare: backbeat + roll leggero finale (ratchet 2x, no trap da 4x qui)
set_steps(D, SNARE, [4, 12], vel=0.9)
D[SNARE][14] = cell(vel=0.75, ratch=2)
D[SNARE][15] = cell(vel=0.85, ratch=2)
# Tom fill ascendente (questo e' il momento "rockista" dei Beastie)
D[TOM][10] = cell(vel=0.75)
D[TOM][11] = cell(vel=0.8)
D[TOM][12] = cell(vel=0.85)  # raddoppio col snare per forza
D[TOM][13] = cell(vel=0.9)
# Hi-hat presente ma meno denso nel fill
for s in [0, 2, 4, 6, 8]:
    D[HIHAT][s] = cell(vel=0.75 if s % 4 == 0 else 0.55)
# Cowbell 1 e 8
set_steps(D, COW, [0, 8], vel=0.6)

# =======================================================
# TRACK PARAMS — mix stile Beastie 2011 (punchy, compressed)
#   Kick: pitch medio (non 808), decay medio-corto, punchy
#   Snare: pitch alto (+2) per "snap" vintage drum machine
#   Hi-hat: brillante
#   Cowbell: HP filter per essere piu' "metallica"
#   Rim: usato come shaker — pan leggero
# =======================================================
track_params = [
    # KICK — punchy, non sub 808
    {"volume": 0.92, "mute": False, "solo": False, "pitch": -1, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # SNARE — "snap" drum machine vintage, pitch un po' alto
    {"volume": 0.85, "mute": False, "solo": False, "pitch": 2, "decay": 0.95,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # HI-HAT — brillante, leggermente a destra
    {"volume": 0.6,  "mute": False, "solo": False, "pitch": 1, "decay": 0.65,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.2},
    # OPEN HH — stessa cifra
    {"volume": 0.55, "mute": False, "solo": False, "pitch": 1, "decay": 1.2,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.2},
    # CLAP — un filo a sinistra (layering col snare -> larghezza)
    {"volume": 0.65, "mute": False, "solo": False, "pitch": 0, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.25},
    # TOM — centro, pitch medio-alto per fill "live"
    {"volume": 0.75, "mute": False, "solo": False, "pitch": 2, "decay": 1.0,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": 0.0},
    # RIMSHOT — usato come shaker, piu' a sinistra, vel gia' bassa nei pattern
    {"volume": 0.6,  "mute": False, "solo": False, "pitch": 0, "decay": 0.6,
     "filterType": "off", "filterCutoff": 0.7, "filterQ": 1.0, "pan": -0.35},
    # COWBELL — HP filter per essere piu' metallica/vintage, pan R
    {"volume": 0.55, "mute": False, "solo": False, "pitch": 1, "decay": 0.9,
     "filterType": "highpass", "filterCutoff": 0.3, "filterQ": 1.0, "pan": 0.35},
]

# =======================================================
# SONG SEQUENCE
# =======================================================
song = ["A", "B", "B", "C", "B", "C", "C", "D"]

demo = {
    "version": 2,
    "exportedAt": "2026-04-19T19:00:00Z",
    "bpm": 105,
    "swing": 12,
    "patternLength": 16,
    "humanize": True,
    "trackParams": track_params,
    "patterns": {"A": A, "B": B, "C": C, "D": D},
    "songSequence": song,
    "_meta": {
        "title": "NYC Hip-Hop — in the style of 'Make Some Noise'",
        "inspired_by": "Make Some Noise — Beastie Boys (Hot Sauce Committee Pt. Two, 2011)",
        "disclaimer": "Pattern originale nello stile del brano, NON una cover ne' una riproduzione. La drum programming (kick/snare/hihat placement) e' grammatica musicale generale. Il brano originale con le sue voci, sample, synth e arrangement resta dei Beastie Boys / Capitol Records.",
        "signature_moves": [
            "Kick DOPPIO su step 1+3 e 9+11 (non 4/4) — tipico del pezzo",
            "Snare backbeat punchy, pitch +2 per lo 'snap' drum-machine vintage",
            "Rim shot sugli off-beat 16th = shaker/tamburello del verso",
            "Cowbell HP-filtered per timbrica metallica NYC hip-hop",
            "Double snare al step 13 nel hook = il 'crack-crack' del ritornello",
            "Tom fill 'live' nel Pattern D = stile registrazioni analog dei Beastie",
        ],
        "instructions": [
            "1) IMPORT questo file",
            "2) Attiva SONG nella modebar",
            "3) PLAY",
            "4) Trucco: seleziona COWBELL, alza il PITCH a +4 per un vibe ancora piu' NYC-80s",
            "5) Se vuoi sentirlo piu' 'rock': togli HUMANIZE, i Beastie erano molto compressed e tight",
            "6) Per feel Dilla/boom-bap: alza lo SWING a 45% e cambi completamente vibe con lo stesso pattern",
        ],
    },
}

out_path = "/home/claude/DrumAPP/examples/demo-makesomenoise.json"
with open(out_path, "w") as f:
    json.dump(demo, f, indent=2)

hits = {name: sum(1 for t in p for s in t if s) for name, p in [("A",A),("B",B),("C",C),("D",D)]}
print(f"Beat NYC hip-hop generato: {out_path}")
print(f"  Patterns: A={hits['A']} B={hits['B']} C={hits['C']} D={hits['D']} hits")
print(f"  Sequence: {' → '.join(song)}")
print(f"  BPM 105 · Swing 12% · Humanize ON · Cowbell HP-filter")
total_sec = len(song) * 16 / (105 / 60 * 4)
print(f"  Durata: {total_sec:.1f}s")

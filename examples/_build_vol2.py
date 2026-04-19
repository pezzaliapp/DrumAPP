#!/usr/bin/env python3
"""
Genera 5 nuove demo per DrumAPP:

BREAK STORICI CAMPIONATI (ricostruzione dello scheletro ritmico):
  demo-impeach.json            · Honey Drippers 1973 — il break più campionato dopo l'Amen
  demo-ashleysroachclip.json   · Soul Searchers 1974 — usato da PM Dawn, Eric B & Rakim, MJ
  demo-synthsub.json           · Melvin Bliss 1973  — la base di "O.P.P." e mille altri

GENERI A FILOSOFIA OPPOSTA:
  demo-onedrop.json            · Dub Reggae — il beat che aspetta il 3 (one-drop)
  demo-ukhardcore.json         · UK Breakbeat Hardcore 1992-93 — pre-jungle, denso e sporco

⚠️ I "break storici" ricostruiscono SOLO la griglia ritmica (grammatica
musicale generale), non le registrazioni, le melodie, il basso o gli
arrangement originali.
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

def tp(volume=0.8, pitch=0, decay=1.0, pan=0.0, mute=False,
       ftype='off', fcutoff=0.7, fq=1.0):
    return {"volume": volume, "mute": mute, "solo": False,
            "pitch": pitch, "decay": decay,
            "filterType": ftype, "filterCutoff": fcutoff, "filterQ": fq,
            "pan": pan}

def save(name, data):
    out = f"/home/claude/DrumAPP/examples/demo-{name}.json"
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    return out

# =========================================================================
# 1) IMPEACH THE PRESIDENT — 100 BPM (Honey Drippers, 1973)
# =========================================================================
# Firma: l'intro di drum-solo pulita e iconica. Kick molto semplice
# (1 e "and of 2"), snare potente sul backbeat, hi-hat 16th con accenti.
# Il groove e' nella PULIZIA — niente ghost, niente fill, solo perfezione
# di 2 bar che si ripete e si fa ricordare.

def build_impeach():
    # A — intro skeleton (i primi 6 secondi di drum solo del brano)
    A = empty_pattern()
    set_steps(A, KICK, [0, 6], vel=1.0)
    set_steps(A, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        A[HIHAT][s] = cell(vel=0.75 if s % 4 == 0 else 0.55)

    # B — pattern con open hat su off-beat (respiro)
    B = empty_pattern()
    set_steps(B, KICK, [0, 6], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        B[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)
    B[OPENHAT][14] = cell(vel=0.7)

    # C — variazione con kick extra e cross-stick rim
    C = empty_pattern()
    set_steps(C, KICK, [0, 6, 10], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    C[SNARE][11] = cell(vel=0.4, prob=70)  # ghost sporadico
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)
    set_steps(C, RIM, [3, 7], vel=0.5)

    # D — tom fill di transizione
    D = empty_pattern()
    set_steps(D, KICK, [0, 6], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        D[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)
    D[TOM][13] = cell(vel=0.8)
    D[TOM][14] = cell(vel=0.85)
    D[TOM][15] = cell(vel=0.9)

    params = [
        tp(0.9,  pitch=-1, decay=1.1),                # Kick
        tp(0.9,  pitch=0,  decay=1.0),                # Snare — potente "crack"
        tp(0.6,  pitch=0,  decay=0.7, pan=0.15),      # Hi-hat
        tp(0.6,  pitch=0,  decay=1.2, pan=0.15),      # Open HH
        tp(0.6,  mute=True),                          # Clap muted
        tp(0.75, pitch=1,  decay=1.0),                # Tom
        tp(0.65, pitch=0,  decay=0.7, pan=-0.25),     # Rim
        tp(0.5,  mute=True),                          # Cow muted
    ]

    return {
        "version": 2, "bpm": 100, "swing": 8, "patternLength": 16,
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "B", "B", "A", "C", "B", "D"],
        "_meta": {
            "title": "Impeach-style · 100 BPM",
            "inspired_by": "Impeach the President — The Honey Drippers (1973)",
            "disclaimer": "Ricostruzione del solo scheletro ritmico. Non riproduce composizione, voci, basso, chitarre o arrangement del brano originale.",
            "signature": [
                "La magia sta nella pulizia: no ghost, no fill barocchi",
                "Kick semplicissimo (1 e 'and-of-2') ma riconoscibile",
                "Snare backbeat 'crack' pieno",
                "Hi-hat 16th steady con accenti sui downbeat",
            ],
            "sampled_in_selection": "Tra i sample più usati nella storia del hip-hop (centinaia di brani, tra cui produzioni Bad Boy e West Coast 90s).",
        },
    }

# =========================================================================
# 2) ASHLEY'S ROACHCLIP — 100 BPM (The Soul Searchers, 1974)
# =========================================================================
# Firma: funky con kick sincopato più ricco, ghost snare, open hat
# "flick" che ricorda Funky Drummer ma a 100 BPM.

def build_ashley():
    A = empty_pattern()
    set_steps(A, KICK, [0, 3, 10], vel=1.0)
    set_steps(A, SNARE, [4, 12], vel=0.92)
    for s in range(16):
        A[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)

    # B — con ghost snare + open hat signature
    B = empty_pattern()
    set_steps(B, KICK, [0, 3, 10], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.92)
    B[SNARE][7] = cell(vel=0.4, prob=85)
    B[SNARE][11] = cell(vel=0.35, prob=80)
    for s in range(16):
        B[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)
    B[OPENHAT][6] = cell(vel=0.8)
    B[OPENHAT][14] = cell(vel=0.7)

    # C — piena densità funky con rim
    C = empty_pattern()
    set_steps(C, KICK, [0, 3, 10], vel=1.0)
    C[KICK][13] = cell(vel=0.75, prob=60)
    set_steps(C, SNARE, [4, 12], vel=0.92)
    C[SNARE][7] = cell(vel=0.4, prob=85)
    C[SNARE][11] = cell(vel=0.35, prob=80)
    C[SNARE][14] = cell(vel=0.35, prob=75)
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)
    set_steps(C, OPENHAT, [6, 14], vel=0.75)
    set_steps(C, RIM, [1, 5, 9, 13], vel=0.4)  # shaker-like

    # D — break variazione
    D = empty_pattern()
    set_steps(D, KICK, [0, 3, 6, 10], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.92)
    D[SNARE][15] = cell(vel=0.7, ratch=2)
    for s in range(16):
        D[HIHAT][s] = cell(vel=0.7 if s % 4 == 0 else 0.5)
    D[OPENHAT][6] = cell(vel=0.8)

    params = [
        tp(0.88, pitch=-1, decay=1.1),
        tp(0.85, pitch=0,  decay=1.0),
        tp(0.6,  pitch=-1, decay=0.7, pan=0.15),
        tp(0.7,  pitch=-1, decay=1.3, pan=0.15),       # Open HH protagonista
        tp(0.6,  mute=True),
        tp(0.7,  pitch=1,  decay=1.0),
        tp(0.55, pitch=0,  decay=0.6, pan=-0.3),
        tp(0.5,  mute=True),
    ]

    return {
        "version": 2, "bpm": 100, "swing": 12, "patternLength": 16,
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "C", "B", "C", "B", "D"],
        "_meta": {
            "title": "Ashley's Roachclip-style · 100 BPM",
            "inspired_by": "Ashley's Roachclip — The Soul Searchers (1974)",
            "disclaimer": "Ricostruzione del solo scheletro ritmico. Non riproduce la composizione, le linee di chitarra/basso o gli arrangement originali.",
            "signature": [
                "Kick sincopato (1, 'and-of-1', 11) — più ricco di Impeach",
                "Ghost snare + open hat al 6 ricordano Funky Drummer, ma più rilassato (100 BPM)",
                "Rim shot sugli off-beat = simula shaker/tamburello",
            ],
            "sampled_in_selection": "Ampiamente campionato: spunti in brani golden age hip-hop e produzioni new jack swing.",
        },
    }

# =========================================================================
# 3) SYNTHETIC SUBSTITUTION — 91 BPM (Melvin Bliss, 1973)
# =========================================================================
# Firma: sparso ma cattivo. Kick molto sincopato, snare potentissimo,
# hi-hat con open hat puntuale. Il groove lascia tanto spazio, per questo
# i rapper ci mettono parole dentro.

def build_synthsub():
    # A — base scarna
    A = empty_pattern()
    set_steps(A, KICK, [0, 8], vel=1.0)
    set_steps(A, SNARE, [4, 12], vel=0.95)
    for s in range(0, 16, 2):
        A[HIHAT][s] = cell(vel=0.65)

    # B — il break iconico con kick sincopato (step 3) + open hat
    B = empty_pattern()
    set_steps(B, KICK, [0, 3, 8, 11], vel=1.0)  # kick "and of 1" + "and of 3"
    set_steps(B, SNARE, [4, 12], vel=0.95)
    for s in range(0, 16, 2):
        B[HIHAT][s] = cell(vel=0.65)
    B[OPENHAT][6] = cell(vel=0.8)

    # C — piena con ghost e variazioni
    C = empty_pattern()
    set_steps(C, KICK, [0, 3, 8, 11], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    C[SNARE][7] = cell(vel=0.35, prob=75)
    for s in range(0, 16, 2):
        C[HIHAT][s] = cell(vel=0.65)
    set_steps(C, OPENHAT, [6, 14], vel=0.75)

    # D — drop/variazione con rim
    D = empty_pattern()
    set_steps(D, KICK, [0, 3, 8], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.95)
    for s in range(0, 16, 2):
        D[HIHAT][s] = cell(vel=0.65)
    D[OPENHAT][6] = cell(vel=0.8)
    set_steps(D, RIM, [10, 14], vel=0.55)

    params = [
        tp(0.92, pitch=-2, decay=1.2),  # Kick vintage 70s
        tp(0.92, pitch=0,  decay=1.1),  # Snare potente
        tp(0.6,  pitch=-1, decay=0.7, pan=0.15),
        tp(0.7,  pitch=-1, decay=1.3, pan=0.15),
        tp(0.6,  mute=True),
        tp(0.7,  pitch=1,  decay=1.0),
        tp(0.6,  pitch=0,  decay=0.7, pan=-0.25),
        tp(0.5,  mute=True),
    ]

    return {
        "version": 2, "bpm": 91, "swing": 5, "patternLength": 16,
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "B", "B", "C", "B", "D", "B"],
        "_meta": {
            "title": "Synthetic Substitution-style · 91 BPM",
            "inspired_by": "Synthetic Substitution — Melvin Bliss (1973)",
            "disclaimer": "Ricostruzione del solo scheletro ritmico. Il brano originale resta di Melvin Bliss e relativi editori.",
            "signature": [
                "Kick SINCOPATO (0, 3, 8, 11) — la firma del break",
                "Snare 'crack' potente sul backbeat",
                "Hi-hat 8th non 16th = respira, lascia spazio al rapper",
                "Open hat al step 6 (come Funky Drummer)",
            ],
            "sampled_in_selection": "Sample ricorrente in molte produzioni golden age (est coast, west coast e europee).",
        },
    }

# =========================================================================
# 4) DUB ONE-DROP — 80 BPM (reggae filosofia opposta)
# =========================================================================
# ★ FILOSOFIA INVERSA: in quasi tutta la musica occidentale il beat forte
# è su 1. Nel reggae ONE-DROP il beat cade sul 3 (step 8 di un 16-step).
# Kick E snare SUONANO INSIEME al 3, non sull'1.
# Il resto è spazio, silenzio, skank di hi-hat, cross-stick rim.

def build_onedrop():
    # A — pattern one-drop puro (il cuore del reggae)
    A = empty_pattern()
    # ★ SOLO step 8 per kick E snare (insieme) — questo è il "one drop"
    A[KICK][8] = cell(vel=1.0)
    A[SNARE][8] = cell(vel=0.9)
    # Hi-hat skank sugli off-beat (2 e 4, cioè step 4 e 12 oltre al 8)
    set_steps(A, HIHAT, [4, 12], vel=0.8)
    # Cross-stick (rim) su 4 e 12 come layer col hi-hat skank
    set_steps(A, RIM, [4, 12], vel=0.55)

    # B — con "rim click" classico e sporadico kick ghost
    B = empty_pattern()
    B[KICK][8] = cell(vel=1.0)
    B[SNARE][8] = cell(vel=0.9)
    set_steps(B, HIHAT, [4, 12], vel=0.8)
    # Rim ("skank") classico reggae su TUTTI gli off-beat 8th
    set_steps(B, RIM, [4, 12], vel=0.65)
    # Ghost kick molto sporadico per variazione
    B[KICK][15] = cell(vel=0.55, prob=40)

    # C — rockers variation (kick anche al 1, ma snare sempre al 3)
    C = empty_pattern()
    C[KICK][0] = cell(vel=0.9)  # Rockers style
    C[KICK][8] = cell(vel=1.0)
    C[SNARE][8] = cell(vel=0.9)
    set_steps(C, HIHAT, [4, 12], vel=0.8)
    set_steps(C, RIM, [4, 12], vel=0.65)
    # Open hat "bubble" occasionale
    C[OPENHAT][14] = cell(vel=0.55, prob=60)

    # D — dub break con tom e reverb feel
    D = empty_pattern()
    D[KICK][8] = cell(vel=1.0)
    D[SNARE][8] = cell(vel=0.9)
    set_steps(D, HIHAT, [4, 12], vel=0.7)
    set_steps(D, RIM, [4, 12], vel=0.6)
    # Tom fill molto sparso, reggae-dub
    D[TOM][11] = cell(vel=0.75, prob=70)
    D[TOM][15] = cell(vel=0.8, prob=80)

    params = [
        # KICK — profondo, decay medio-lungo per sub roots
        tp(0.88, pitch=-3, decay=1.5),
        # SNARE — pitch leggermente alto, decay medio (il "pop" reggae)
        tp(0.85, pitch=1,  decay=1.0),
        # HI-HAT — skank molto "chiuso" e corto
        tp(0.7,  pitch=0,  decay=0.5, pan=0.2),
        # OPEN HH — uso sporadico, decay medio
        tp(0.5,  pitch=0,  decay=1.0, pan=0.2),
        tp(0.6,  mute=True),   # Clap muted
        # TOM — roots/dub, pitch medio-basso, decay lungo
        tp(0.7,  pitch=-2, decay=1.4),
        # RIM (cross-stick) — SUONO PRINCIPALE del reggae, pan centro
        tp(0.75, pitch=1,  decay=0.4, pan=0.0),
        tp(0.5,  mute=True),   # Cow muted
    ]

    return {
        "version": 2, "bpm": 80, "swing": 0, "patternLength": 16,
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "B", "B", "B", "C", "B", "D"],
        "_meta": {
            "title": "One-Drop Reggae · 80 BPM",
            "inspired_by": "Filosofia ritmica del reggae classico (Studio One, Bob Marley 'One Drop', Horace Andy, etc.)",
            "disclaimer": "Pattern generico in stile one-drop. Non riproduce nessun brano specifico.",
            "signature": [
                "★ IL KICK E IL SNARE SUONANO INSIEME AL BEAT 3 (step 8) — NON sull'1!",
                "Questo è il 'drop': tutto aspetta, poi CADE insieme",
                "Hi-hat skank su 2 e 4 (step 4 e 12) — l'unica cosa che riempie",
                "Rim (cross-stick) al posto del snare tradizionale — tipico reggae",
                "Pattern A, B, C, D quasi identici: nel reggae le variazioni sono microscopiche",
            ],
            "try": [
                "Ascolta con attenzione: per 7/8 della misura non succede NIENTE. Poi al 3 cade tutto. È questa sospensione che crea il groove reggae.",
                "Prova: il Pattern C è 'rockers' (kick al 1 E al 3, stile Sly & Robbie anni 70). Il Pattern A/B è 'one-drop puro' (kick solo al 3, stile Bob Marley/Carlton Barrett).",
                "Per dub più scuro: alza PITCH del kick a -5 e DECAY del kick a 2.2",
            ],
        },
    }

# =========================================================================
# 5) UK BREAKBEAT HARDCORE — 140 BPM (1992-93, pre-jungle)
# =========================================================================
# Era pre-DNB: breakbeats tagliati, pitched-up, pieni di ratchet.
# Produzione sporca, densa, energica. The Prodigy, Shut Up & Dance,
# SL2, Acen. L'Amen veniva tritato e riassemblato a velocità folle.

def build_ukhardcore():
    # A — kick "hoover" pattern 4/4 con snare chopped
    A = empty_pattern()
    # Kick 4/4 dritto (stile rave) ma con ghost extra
    set_steps(A, KICK, [0, 4, 8, 12], vel=1.0)
    A[KICK][6] = cell(vel=0.75, prob=70)
    # Snare chopped: backbeat + extra off
    set_steps(A, SNARE, [4, 12], vel=0.9)
    # Hi-hat fitti
    for s in range(16):
        A[HIHAT][s] = cell(vel=0.6 if s % 2 == 0 else 0.4)

    # B — amen-style chopped (kick sparso, più breakbeat)
    B = empty_pattern()
    set_steps(B, KICK, [0, 10], vel=1.0)  # Amen-like
    B[KICK][3] = cell(vel=0.7, prob=65)
    B[KICK][6] = cell(vel=0.8, prob=75)
    set_steps(B, SNARE, [4, 12], vel=0.9)
    B[SNARE][6] = cell(vel=0.45, prob=80)  # ghost Amen
    B[SNARE][14] = cell(vel=0.5, prob=70)
    for s in range(16):
        B[HIHAT][s] = cell(vel=0.6 if s % 2 == 0 else 0.4)
    # Ratchet 2x sporadici (chopping feel)
    B[HIHAT][11] = cell(vel=0.7, ratch=2)
    B[HIHAT][15] = cell(vel=0.8, ratch=3)

    # C — hardcore piena tensione con ratchet aggressivi
    C = empty_pattern()
    set_steps(C, KICK, [0, 4, 6, 8, 12], vel=1.0)  # 4/4 + ghost
    set_steps(C, SNARE, [4, 12], vel=0.95)
    C[SNARE][11] = cell(vel=0.5, prob=80)
    C[SNARE][14] = cell(vel=0.55, prob=85)
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.6 if s % 2 == 0 else 0.4)
    C[HIHAT][5]  = cell(vel=0.7, ratch=2)
    C[HIHAT][9]  = cell(vel=0.75, ratch=2)
    C[HIHAT][13] = cell(vel=0.8, ratch=3)
    C[HIHAT][15] = cell(vel=0.85, ratch=4)  # fill rave
    # Clap layer (rave typical)
    set_steps(C, CLAP, [4, 12], vel=0.65)

    # D — BREAKDOWN / big fill pre-drop (snare roll + tom fill)
    D = empty_pattern()
    set_steps(D, KICK, [0, 4, 8], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.9)
    # Snare roll 4x esplosivo finale (tipico hardcore)
    D[SNARE][13] = cell(vel=0.7, ratch=2)
    D[SNARE][14] = cell(vel=0.85, ratch=3)
    D[SNARE][15] = cell(vel=1.0, ratch=4)
    for s in range(16):
        D[HIHAT][s] = cell(vel=0.55 if s % 2 == 0 else 0.35)
    # Tom fill ascendente
    D[TOM][9]  = cell(vel=0.75)
    D[TOM][10] = cell(vel=0.85)
    D[TOM][11] = cell(vel=0.95)

    params = [
        # KICK — pitch alto per "hoover" rave, decay corto aggressivo
        tp(0.92, pitch=1,  decay=0.85),
        # SNARE — pitch alto "chop", decay corto
        tp(0.88, pitch=2,  decay=0.8),
        # HI-HAT — brillante rave
        tp(0.65, pitch=2,  decay=0.5, pan=0.2),
        tp(0.55, pitch=2,  decay=1.0, pan=0.2),
        # CLAP — rave classic, pan L
        tp(0.7,  pitch=1,  decay=0.9, pan=-0.3),
        tp(0.75, pitch=2,  decay=0.9),
        tp(0.6,  mute=True),
        tp(0.5,  mute=True),
    ]

    return {
        "version": 2, "bpm": 140, "swing": 0, "patternLength": 16,
        "humanize": False,  # hardcore è quantizzato
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "B", "B", "C", "A", "B", "D"],
        "_meta": {
            "title": "UK Breakbeat Hardcore · 140 BPM",
            "inspired_by": "Era pre-jungle UK 1992-93 (Prodigy, SL2, Acen, Shut Up & Dance, Rufige Kru)",
            "disclaimer": "Pattern originale in stile hardcore UK. Non riproduce nessun brano specifico.",
            "signature": [
                "140 BPM = territorio pre-jungle (prima che i break diventassero a 170 del DNB)",
                "Pattern A: kick 4/4 rave (il 'hoover' kick), stile Prodigy prima era",
                "Pattern B: breakbeat Amen-style con ghost snare (la base del futuro jungle)",
                "Ratchet 2×/3×/4× sugli hi-hat = il 'chopping' dei sample",
                "Clap layered sul snare (classica cosa rave)",
                "Kick pitch +1 e decay 0.85 = il suono compresso dei campionatori Akai S950",
            ],
            "try": [
                "Il Pattern A è hardcore rave dritto, il Pattern B è il futuro jungle che sta nascendo. Nel 1992-93 coesistevano nello stesso brano.",
                "Per feel Shut Up & Dance: aumenta PITCH del snare a +4 (quel suono chopped brutto e bellissimo)",
                "Per far diventare il tutto DNB: porta BPM a 170 e muta il kick durante il Pattern B → hai ricostruito la transizione hardcore→jungle",
            ],
        },
    }

# =========================================================================
# GENERA TUTTO
# =========================================================================

if __name__ == "__main__":
    demos = [
        ("impeach",          build_impeach()),
        ("ashleysroachclip", build_ashley()),
        ("synthsub",         build_synthsub()),
        ("onedrop",          build_onedrop()),
        ("ukhardcore",       build_ukhardcore()),
    ]
    for name, data in demos:
        save(name, data)
        hits = sum(1 for p in data["patterns"].values() for t in p for s in t if s)
        bpm = data["bpm"]
        song_len = len(data["songSequence"])
        total_sec = song_len * 16 / (bpm / 60 * 4)
        print(f"  ✓ demo-{name}.json  ·  {bpm} BPM  ·  {hits} hits  ·  {total_sec:.1f}s")
    print("\n5 demo generate in examples/")

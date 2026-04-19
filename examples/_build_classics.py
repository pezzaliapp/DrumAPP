#!/usr/bin/env python3
"""
Genera 4 demo storiche per DrumAPP, ricostruendo lo scheletro ritmico
di break iconici della musica popolare.

⚠️ DISCLAIMER (identico per tutti i 4 file):
Questi sono pattern originali nello STILE dei brani indicati, NON cover
né riproduzioni. Una drum pattern (kick su 1, snare sul backbeat) è
grammatica musicale generale, non composizione protetta. I brani reali
con voci, melodie, basso, arrangement restano dei rispettivi autori/editori.

File generati:
  - demo-billiejean.json    · Michael Jackson 1982 (117 BPM, Linn LM-1)
  - demo-funkydrummer.json  · James Brown 1970    (103 BPM, Clyde Stubblefield)
  - demo-levee.json         · Led Zeppelin 1971   ( 72 BPM, John Bonham)
  - demo-apache.json        · Incredible Bongo Band 1973 (112 BPM, DJ Kool Herc's break)
"""

import json
import os

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

def default_tp(volume=0.8, pitch=0, decay=1.0, pan=0.0, mute=False,
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
# 1) BILLIE JEAN — 117 BPM, Linn LM-1, precisione metronomica
# =========================================================================
# Firma: metronomico perfetto (macchina, non umano), kick sincopato,
# snare backbeat "centered", hi-hat 16th steady con accento sui pari.
# NESSUN ghost note — e' tutto pulito, e' il suono della drum machine 1982.

def build_billiejean():
    # A — pattern base solitario (i primi 2 bar del brano, scarni)
    A = empty_pattern()
    set_steps(A, KICK, [0, 6], vel=1.0)
    set_steps(A, SNARE, [4, 12], vel=0.95)

    # B — pattern pieno del brano: + hi-hat 16th
    B = empty_pattern()
    set_steps(B, KICK, [0, 6], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.95)
    # Hi-hat 16th con accento sui pari (downbeat e-and-a)
    for s in range(16):
        B[HIHAT][s] = cell(vel=0.8 if s % 2 == 0 else 0.5)

    # C — variazione con rim shot (simula le "click" percussion del brano)
    C = empty_pattern()
    set_steps(C, KICK, [0, 6], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.8 if s % 2 == 0 else 0.5)
    # Rim shot su step 3 e 11 (percussioni precise alla Linn)
    set_steps(C, RIM, [3, 11], vel=0.6)

    # D — accumulo con tom fill (transizione verso il bridge)
    D = empty_pattern()
    set_steps(D, KICK, [0, 6], vel=1.0)
    D[KICK][14] = cell(vel=0.85)  # extra kick prima del loop
    set_steps(D, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        D[HIHAT][s] = cell(vel=0.8 if s % 2 == 0 else 0.5)
    # Tom fill leggero finale (dopo il kick extra)
    D[TOM][15] = cell(vel=0.75)

    tp = [
        default_tp(0.92, pitch=-1, decay=1.0),                  # Kick
        default_tp(0.88, pitch=1, decay=0.85),                  # Snare — centro, snap pulito
        default_tp(0.6,  pitch=0, decay=0.5, pan=0.15),         # Hi-hat — precisione LM-1
        default_tp(0.55, pitch=0, decay=1.0, pan=0.15),         # Open HH
        default_tp(0.65, mute=True),                            # Clap — muted
        default_tp(0.7,  pitch=2, decay=0.9),                   # Tom
        default_tp(0.65, pitch=0, decay=0.6, pan=-0.2),         # Rim — percussion click
        default_tp(0.5, mute=True),                             # Cow — muted
    ]

    return {
        "version": 2, "bpm": 117, "swing": 0, "patternLength": 16,
        "humanize": False,  # Linn LM-1 era macchina pura
        "trackParams": tp,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "C", "B", "B", "C", "D"],
        "_meta": {
            "title": "Billie Jean-style · 117 BPM",
            "inspired_by": "Billie Jean — Michael Jackson / Quincy Jones (1982)",
            "disclaimer": "Pattern originale nello stile del brano. NON riproduce la composizione, il basso iconico, le voci o gli arrangement di Quincy Jones, che restano protetti.",
            "signature": [
                "Linn LM-1 = precisione metronomica, ZERO humanize",
                "Kick sincopato (step 1 e 7) invece del 4/4 dance",
                "Snare backbeat pulitissimo, nessun ghost",
                "Hi-hat 16th steady con accento 8th (pari)",
                "Rim shot come click percussivo (no conga, no shaker)",
            ],
            "try": [
                "Attiva SONG",
                "Prova: alza HUMANIZE → rovina immediatamente il feel (la bellezza e' che NON e' umano)",
                "Alza pitch SNARE a +3 per quel suono ancora piu' crack-80s",
            ],
        },
    }

# =========================================================================
# 2) FUNKY DRUMMER — 103 BPM, Clyde Stubblefield, 1970
# =========================================================================
# Il break piu' campionato nella storia dell'hip-hop. Firma:
# ghost notes FITTI sul snare, hi-hat 16th steady, e il famoso OPEN HAT
# in mezzo al pattern (step 6) che fa tutto il "funk".

def build_funkydrummer():
    # A — skeleton (kick + snare main + hi-hat 16th)
    A = empty_pattern()
    set_steps(A, KICK, [0, 2, 10], vel=1.0)
    set_steps(A, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        A[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.5)

    # B — pattern "Funky Drummer" classico: + ghost notes + OPEN HAT sul 6
    B = empty_pattern()
    set_steps(B, KICK, [0, 2, 10], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.95)
    # GHOST notes (la firma del pattern di Clyde)
    B[SNARE][7]  = cell(vel=0.35, prob=90)
    B[SNARE][8]  = cell(vel=0.3,  prob=80)
    B[SNARE][11] = cell(vel=0.32, prob=85)
    B[SNARE][14] = cell(vel=0.35, prob=85)
    for s in range(16):
        B[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.5)
    # ★ OPEN HAT al step 6 — IL momento magico del break
    B[OPENHAT][6] = cell(vel=0.85)

    # C — variazione con piu' ghost e open hat raddoppiato
    C = empty_pattern()
    set_steps(C, KICK, [0, 2, 10], vel=1.0)
    C[KICK][11] = cell(vel=0.7, prob=60)  # kick ghost
    set_steps(C, SNARE, [4, 12], vel=0.95)
    C[SNARE][3]  = cell(vel=0.3,  prob=70)
    C[SNARE][7]  = cell(vel=0.35, prob=90)
    C[SNARE][11] = cell(vel=0.32, prob=85)
    C[SNARE][14] = cell(vel=0.35, prob=85)
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.5)
    set_steps(C, OPENHAT, [6, 14], vel=0.8)

    # D — break style (il momento "drum solo" dove tutto va in funk puro)
    D = empty_pattern()
    set_steps(D, KICK, [0, 2, 6, 10], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.95)
    # Ghost roll sparato
    for s in [3, 7, 8, 11, 14, 15]:
        D[SNARE][s] = cell(vel=0.35, prob=85)
    D[SNARE][15] = cell(vel=0.7, ratch=2)  # mini roll
    for s in range(16):
        D[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.5)
    set_steps(D, OPENHAT, [6], vel=0.9)

    tp = [
        default_tp(0.85, pitch=-2, decay=1.1),                  # Kick — vintage funk
        default_tp(0.82, pitch=0, decay=1.0),                   # Snare — polposo anni 70
        default_tp(0.6,  pitch=-1, decay=0.7, pan=0.15),        # Hi-hat — vintage
        default_tp(0.7,  pitch=-1, decay=1.3, pan=0.15),        # Open HH — ★ protagonista
        default_tp(0.65, mute=True),                            # Clap — muted (no nel funk 70s)
        default_tp(0.7,  pitch=1, decay=1.0),                   # Tom
        default_tp(0.6,  pitch=0, decay=0.7, pan=-0.25),        # Rim
        default_tp(0.5, mute=True),                             # Cow — muted
    ]

    return {
        "version": 2, "bpm": 103, "swing": 10, "patternLength": 16,
        "humanize": True,
        "trackParams": tp,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "B", "C", "B", "D", "B"],
        "_meta": {
            "title": "Funky Drummer-style · 103 BPM",
            "inspired_by": "Funky Drummer — James Brown, perf. Clyde Stubblefield (1970)",
            "disclaimer": "Pattern originale nello stile del break. NON riproduce la composizione di James Brown, la sezione fiati o il basso, che restano protetti.",
            "signature": [
                "GHOST NOTES sul snare (step 7, 8, 11, 14) — l'anima del funk",
                "OPEN HAT al step 6 — 'IL' momento del break, il trigger di migliaia di sample hip-hop",
                "Hi-hat 16th steady — niente trap-ratchet, tutto suonato umano",
                "Swing leggero 10% + humanize = feel umano vero, non macchina",
            ],
            "try": [
                "Attiva SONG",
                "Per sentire quanto conta il ghost: seleziona SNARE e premi S (solo)",
                "Per sentire quanto conta l'open hat al 6: porta volume OPEN HH a 0, poi rimettilo. Tutto il funk sta li'.",
                "Questo break e' stato campionato in: Public Enemy 'Fight the Power', N.W.A 'Fuck tha Police', LL Cool J 'Mama Said Knock You Out', Prince 'Gett Off'... e altri 2000 brani.",
            ],
        },
    }

# =========================================================================
# 3) WHEN THE LEVEE BREAKS — 72 BPM, John Bonham, 1971
# =========================================================================
# Il drum break piu' "massiccio" mai registrato. Bonham suonava in
# una tromba delle scale a Headley Grange, con 2 microfoni lontani.
# Firma: LENTO, PESANTE, ENORME. Half-time feel.
# Nessun ghost, nessuna sottigliezza: solo potenza.

def build_levee():
    # A — il pattern iconico nudo: kick + snare massicci
    A = empty_pattern()
    set_steps(A, KICK, [0, 6], vel=1.0)
    set_steps(A, SNARE, [4, 12], vel=1.0)

    # B — + hi-hat 8th
    B = empty_pattern()
    set_steps(B, KICK, [0, 6], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=1.0)
    # Hi-hat 8th SENZA accenti forti (Bonham teneva tutto pesante ma uniforme)
    for s in range(0, 16, 2):
        B[HIHAT][s] = cell(vel=0.7)

    # C — variazione con kick double (Bonham era famoso per il "triplet kick")
    C = empty_pattern()
    set_steps(C, KICK, [0, 6], vel=1.0)
    C[KICK][7] = cell(vel=0.8)  # doppio kick rapido (Bonham trick)
    set_steps(C, SNARE, [4, 12], vel=1.0)
    for s in range(0, 16, 2):
        C[HIHAT][s] = cell(vel=0.7)

    # D — tom fill pre-loop (Bonham era famoso per i fill aperti)
    D = empty_pattern()
    set_steps(D, KICK, [0, 6], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=1.0)
    for s in range(0, 16, 2):
        D[HIHAT][s] = cell(vel=0.7)
    # Tom fill "tribale" finale (simula i floor tom di Bonham)
    D[TOM][13] = cell(vel=0.85)
    D[TOM][14] = cell(vel=0.9)
    D[TOM][15] = cell(vel=0.95)

    tp = [
        # KICK — pitch basso, decay LUNGO per simulare il room sound enorme
        default_tp(0.95, pitch=-3, decay=2.0),
        # SNARE — pitch basso (anche il snare Bonham era grosso), decay lungo
        default_tp(0.9,  pitch=-1, decay=1.5),
        # HI-HAT — decay un po' piu' lungo del solito (room sound)
        default_tp(0.55, pitch=-1, decay=0.9, pan=0.1),
        default_tp(0.5,  mute=True),  # Open HH muted (il brano non la usa)
        default_tp(0.6,  mute=True),  # Clap muted
        # TOM — pitch BASSO per il "bombo-tom" signature di Bonham, decay lungo
        default_tp(0.9,  pitch=-4, decay=1.8),
        default_tp(0.6,  mute=True),  # Rim muted
        default_tp(0.5,  mute=True),  # Cow muted
    ]

    return {
        "version": 2, "bpm": 72, "swing": 0, "patternLength": 16,
        "humanize": False,  # Bonham era tight, non lazy
        "trackParams": tp,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "B", "B", "B", "C", "B", "D"],
        "_meta": {
            "title": "Levee-style · 72 BPM (half-time massiccio)",
            "inspired_by": "When the Levee Breaks — Led Zeppelin IV (1971), drum: John Bonham",
            "disclaimer": "Pattern originale nello stile del break. NON riproduce la composizione dei Led Zeppelin ne' il sound del brano (registrato in modo unico a Headley Grange), che restano protetti.",
            "signature": [
                "72 BPM = half-time, feel lentissimo e pesante",
                "Decay LUNGHI su tutto (kick 2.0×, snare 1.5×, tom 1.8×) per simulare il room sound enorme",
                "Pitch BASSI (kick -3, snare -1, tom -4) = quel 'cavernoso'",
                "NESSUN ghost note, nessun fill ornato: Bonham era pura potenza",
                "Hi-hat 8th (non 16th come nel funk) — i battiti sono larghi",
            ],
            "try": [
                "Attiva SONG",
                "Per l'effetto 'stairwell at Headley Grange': aumenta il DECAY del kick a 2.5× e del snare a 2.0×",
                "Campionato in: Beastie Boys 'Rhymin' & Stealin'', Eminem 'Kim', Dr. Dre 'Lyrical Gangbang', Enigma 'Return to Innocence'...",
            ],
        },
    }

# =========================================================================
# 4) APACHE — 112 BPM, Incredible Bongo Band 1973
# =========================================================================
# Il break che DJ Kool Herc mixava al Bronx party del 1973 inventando
# di fatto l'hip-hop. Firma: BONGOS e CONGAS protagonisti, batteria
# che fa da base ma le percussioni tribali sono l'anima.
# Usiamo TOM (come bongos) e RIM (come claves) intensivamente.

def build_apache():
    # A — skeleton: kick + snare (la base su cui ballare al block party)
    A = empty_pattern()
    set_steps(A, KICK, [0, 2, 8, 10], vel=1.0)  # kick doppio sincopato
    set_steps(A, SNARE, [4, 12], vel=0.9)
    # Hi-hat 8th leggero
    for s in range(0, 16, 2):
        A[HIHAT][s] = cell(vel=0.55)

    # B — + BONGOS (tom) che fanno il pattern latino
    B = empty_pattern()
    set_steps(B, KICK, [0, 2, 8, 10], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.9)
    for s in range(0, 16, 2):
        B[HIHAT][s] = cell(vel=0.55)
    # BONGOS: pattern tribale tipico (1-e-a feel)
    # Alterno tom con pitch alto e basso (simulato con velocity + pitch track)
    set_steps(B, TOM, [3, 6, 11, 14], vel=0.75)
    set_steps(B, TOM, [7, 15], vel=0.55)  # ghost bongo
    # CLAVES (rim) — shuffle latino
    set_steps(B, RIM, [1, 5, 9, 13], vel=0.5)

    # C — il "break" del brano: solo percussioni (il momento Kool Herc)
    C = empty_pattern()
    # Kick ridotto, lasciare respirare le perc
    set_steps(C, KICK, [0, 8], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.85)
    # BONGOS in roll (il climax del break)
    set_steps(C, TOM, [2, 3, 6, 7, 10, 11, 14, 15], vel=0.7)
    C[TOM][15] = cell(vel=0.9, ratch=2)  # fill
    # Claves fitti
    set_steps(C, RIM, [1, 5, 9, 13], vel=0.55)
    # Cowbell (il "ting" latino)
    set_steps(C, COW, [0, 8], vel=0.6)

    # D — outro / ritorno al groove con shaker denso
    D = empty_pattern()
    set_steps(D, KICK, [0, 2, 8, 10], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.9)
    for s in range(0, 16, 2):
        D[HIHAT][s] = cell(vel=0.55)
    set_steps(D, TOM, [3, 6, 11, 14], vel=0.75)
    set_steps(D, RIM, [1, 3, 5, 7, 9, 11, 13, 15], vel=0.45)  # shaker denso
    set_steps(D, COW, [0, 4, 8, 12], vel=0.55)

    tp = [
        default_tp(0.88, pitch=-1, decay=1.1),                  # Kick funk anni 70
        default_tp(0.82, pitch=0, decay=1.0),                   # Snare
        default_tp(0.55, pitch=0, decay=0.6, pan=0.15),         # Hi-hat
        default_tp(0.5, mute=True),                             # Open HH muted
        default_tp(0.6, mute=True),                             # Clap muted
        # TOM = bongos: pitch ALTO (bongos acuti), decay corto, pan R (stereo latino)
        default_tp(0.75, pitch=5, decay=0.7, pan=0.4),
        # RIM = claves: pan a sinistra (stereo classico)
        default_tp(0.65, pitch=1, decay=0.5, pan=-0.4),
        # COW = cowbell latina, decay medio, pan R
        default_tp(0.6, pitch=0, decay=0.8, pan=0.25),
    ]

    return {
        "version": 2, "bpm": 112, "swing": 0, "patternLength": 16,
        "humanize": True,  # feel umano (erano musicisti veri)
        "trackParams": tp,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "C", "B", "C", "D", "B"],
        "_meta": {
            "title": "Apache-style · 112 BPM (break originale dell'hip-hop)",
            "inspired_by": "Apache — Incredible Bongo Band (1973) · breakbeat usato da DJ Kool Herc ai Bronx block party del 1973-75, inventando di fatto l'hip-hop",
            "disclaimer": "Pattern originale nello stile del brano. NON riproduce la melodia surf, il synth o le chitarre dell'Apache originale, che restano protette.",
            "signature": [
                "BONGOS protagonisti (simulati con TOM pitch +5) — pattern tribale",
                "CLAVES / shaker (simulati con RIM pitch +1) — shuffle latino",
                "Cowbell latina — accenti sui downbeat",
                "Kick doppio sincopato (1+3, 9+11) — feel latino/funk",
                "Stereo largo: tom R40, rim L40, cowbell R25 → effetto 'block party'",
            ],
            "try": [
                "Attiva SONG",
                "Il Pattern C e' il 'break di Kool Herc' — il momento dove i DJ tagliavano e mettevano la voce",
                "Per sentire il 'mixing' del DJ: muta KICK durante il Pattern C (premi M sulla traccia KICK)",
                "Questo break ha generato: Sugarhill Gang 'Apache', Sir Mix-a-Lot, LL Cool J, Nas... e l'intera cultura hip-hop di NYC anni 70-80.",
            ],
        },
    }

# =========================================================================
# GENERA TUTTO
# =========================================================================

if __name__ == "__main__":
    demos = [
        ("billiejean",   build_billiejean()),
        ("funkydrummer", build_funkydrummer()),
        ("levee",        build_levee()),
        ("apache",       build_apache()),
    ]
    for name, data in demos:
        path = save(name, data)
        hits = sum(
            1 for p in data["patterns"].values() for t in p for s in t if s
        )
        bpm = data["bpm"]
        song_len = len(data["songSequence"])
        total_sec = song_len * 16 / (bpm / 60 * 4)
        print(f"  ✓ demo-{name}.json  ·  {bpm} BPM  ·  {hits} hits tot  ·  {total_sec:.1f}s")
    print("\nTutte le 4 demo generate in examples/")

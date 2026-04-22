#!/usr/bin/env python3
"""
VOLUME 3 — 9 nuove demo iconiche per DrumAPP.

Categoria "DA DA DA / da stadio":
  - demo-dadada.json          Trio, 1982 · il minimalismo tedesco Casio VL-Tone
  - demo-wewillrockyou.json   Queen, 1977 · stomp-stomp-clap universale
  - demo-sevennation.json     White Stripes, 2003 · DA-da-DA-DA-da-DA-da stadi
  - demo-anotherone.json      Queen, 1980 · boom-boom-BAH disco-rock

Categoria "Funk-riff":
  - demo-superstition.json    Stevie Wonder, 1972 · funk 16th + ghost notes
  - demo-rosanna.json         Toto, 1982 · half-time shuffle Jeff Porcaro
  - demo-stayinalive.json     Bee Gees, 1977 · disco 103 BPM (ritmo RCP!)

Categoria "Cinematografici":
  - demo-takefive.json        Brubeck, 1959 · jazz in 5/4 (pattern 20 step!)
  - demo-wipeout.json         Surfaris, 1963 · surf drum solo 16th

⚠️ Tutti ricostruiscono solo scheletri ritmici. Niente melodie/voci/basso.
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
# 1) DA DA DA — 120 BPM (Trio, 1982)
# =========================================================================
# Casio VL-Tone preset rock #2. Minimalismo assoluto:
# kick 4/4 dritto, snare backbeat, SEMPRE uguale. È il pattern del
# preset che fa "bish-bash-bosh" nei giocattoli giapponesi.
# Nessun swing, nessun humanize, niente — proprio come sembrava.

def build_dadada():
    # A — il preset Casio VL-Tone PURO (come arriva dalla fabbrica)
    A = empty_pattern()
    set_steps(A, KICK, [0, 4, 8, 12], vel=1.0)         # 4/4 dritto
    set_steps(A, SNARE, [4, 12], vel=0.95)             # backbeat
    # Hi-hat 8th (VL-Tone ne aveva uno semplicissimo)
    for s in range(0, 16, 2):
        A[HIHAT][s] = cell(vel=0.6)

    # B — con rim click al posto del snare (variazione preset)
    B = empty_pattern()
    set_steps(B, KICK, [0, 4, 8, 12], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.95)
    for s in range(0, 16, 2):
        B[HIHAT][s] = cell(vel=0.6)
    # Rim "tick" sugli off-beat (quello è il suono giocattolo)
    set_steps(B, RIM, [2, 6, 10, 14], vel=0.45)

    # C — variazione con cowbell tocco anni 80
    C = empty_pattern()
    set_steps(C, KICK, [0, 4, 8, 12], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    for s in range(0, 16, 2):
        C[HIHAT][s] = cell(vel=0.6)
    set_steps(C, RIM, [2, 6, 10, 14], vel=0.45)
    set_steps(C, COW, [0, 8], vel=0.5)

    # D — stacco: solo kick e clap (stile ponte del pezzo)
    D = empty_pattern()
    set_steps(D, KICK, [0, 4, 8, 12], vel=1.0)
    set_steps(D, CLAP, [4, 12], vel=0.85)              # clap invece di snare!
    for s in range(0, 16, 2):
        D[HIHAT][s] = cell(vel=0.6)

    params = [
        # KICK — pitch ALTO e decay CORTO: quel suono "pong" giocattolo
        tp(0.8, pitch=3, decay=0.55),
        # SNARE — pitch alto e decay corto, "tck" VL-Tone
        tp(0.75, pitch=4, decay=0.5),
        # HI-HAT — pitch alto, decay minuscolo: "tic tic"
        tp(0.55, pitch=3, decay=0.35, pan=0.0),
        tp(0.4, mute=True),   # Open HH muted (il giocattolo non ce l'aveva!)
        # CLAP — solo pattern D
        tp(0.7, pitch=2, decay=0.7),
        tp(0.5, mute=True),   # Tom muted
        # RIM — "tick" giocattolo, pitch alto
        tp(0.6, pitch=3, decay=0.25, pan=0.0),
        # COW — tocco 80s, leggerissima
        tp(0.5, pitch=2, decay=0.5, pan=0.1),
    ]

    return {
        "version": 2, "bpm": 120, "swing": 0, "patternLength": 16,
        "humanize": False,      # ★ il punto è che NON è umano
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "B", "B", "C", "B", "A", "D"],
        "_meta": {
            "title": "Da Da Da-style · 120 BPM (Casio VL-Tone preset)",
            "inspired_by": "Da Da Da — Trio (1982, Germania, Neue Deutsche Welle)",
            "disclaimer": "Pattern originale in stile VL-Tone preset anni 80. Non riproduce la linea melodica, il testo o la chitarra del brano originale dei Trio.",
            "signature": [
                "★ ZERO HUMANIZE, ZERO SWING — è un giocattolo, non un musicista",
                "Kick 4/4 dritto + snare backbeat = preset di fabbrica",
                "Pitch alto su tutto (kick +3, snare +4, hihat +3) = timbro Casio giocattolo",
                "Decay cortissimi = suoni 'pong', non organici",
                "Il messaggio della canzone: la musica pop si puo' fare con niente",
            ],
            "try": [
                "Ascolta: senti come il groove funziona comunque, nonostante sia brutale nella sua semplicita'",
                "Prova a togliere KICK: resta solo il 'tic tic tic' e capisci cosa facevano in concerto",
                "Alza SWING al 30% → lo distruggi, il bello e' che NON swinga",
                "Campionato/coverizzato da: Elastica (2000), cover italiana 'Da Da Da Mundial '82' per la vittoria azzurra, Volkswagen Golf spot 1997, Citroen spot 2012",
            ],
        },
    }


# =========================================================================
# 2) WE WILL ROCK YOU — 81 BPM (Queen, 1977)
# =========================================================================
# STOMP-STOMP-CLAP. Il drum pattern piu' riconoscibile del pianeta.
# Nessuna batteria vera, tutto stomp+clap overdubbato. Tempo: 81 BPM.

def build_wewillrockyou():
    # A — lo stomp-stomp-clap PURO (i primi secondi del pezzo)
    A = empty_pattern()
    # "STOMP-STOMP-CLAP-(pausa)" in 4/4 = step 0, 2, 4 poi pausa lunga
    # Interpretiamo 1 bar = 16 step, il pattern originale e' 2 bar nel pezzo
    # ma basta 1 bar per catturarlo
    set_steps(A, KICK, [0, 2], vel=1.0)    # stomp-stomp
    A[CLAP][4] = cell(vel=1.0)             # CLAP!
    set_steps(A, KICK, [8, 10], vel=1.0)   # stomp-stomp (bar 2)
    A[CLAP][12] = cell(vel=1.0)            # CLAP!

    # B — pieno con il tipico "stadio": clap raddoppiato + snare layer
    B = empty_pattern()
    set_steps(B, KICK, [0, 2, 8, 10], vel=1.0)
    set_steps(B, CLAP, [4, 12], vel=1.0)
    # Snare layered sul clap (come nel pezzo quando la band entra)
    set_steps(B, SNARE, [4, 12], vel=0.7)

    # C — variazione con doppio clap ("we WILL we WILL rock you")
    C = empty_pattern()
    set_steps(C, KICK, [0, 2, 8, 10], vel=1.0)
    set_steps(C, CLAP, [4, 12], vel=1.0)
    C[CLAP][5] = cell(vel=0.6)   # doppio clap
    C[CLAP][13] = cell(vel=0.6)
    set_steps(C, SNARE, [4, 12], vel=0.7)

    # D — il grande finale (tutto insieme, ratchet sul clap per "urla")
    D = empty_pattern()
    set_steps(D, KICK, [0, 2, 8, 10], vel=1.0)
    set_steps(D, CLAP, [4, 12], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.8)
    D[CLAP][15] = cell(vel=0.8, ratch=2)  # clap roll finale

    params = [
        # KICK — qui e' uno STOMP (piede su tavolato), pitch basso e decay medio-lungo
        tp(0.95, pitch=-2, decay=1.3),
        # SNARE — usato come layer, non protagonista
        tp(0.7, pitch=0, decay=0.8),
        tp(0.5, mute=True),   # Hi-hat MUTED (non c'e' nel pezzo!)
        tp(0.5, mute=True),
        # CLAP — il protagonista! Volume pieno, decay lunghetto per il reverb overdub
        tp(0.95, pitch=0, decay=1.5),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
    ]

    return {
        "version": 2, "bpm": 81, "swing": 0, "patternLength": 16,
        "humanize": False,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "A", "B", "A", "B", "C", "D"],
        "_meta": {
            "title": "We Will Rock You-style · 81 BPM (stomp-stomp-CLAP)",
            "inspired_by": "We Will Rock You — Queen (News of the World, 1977)",
            "disclaimer": "Pattern originale. Non riproduce la melodia, il testo, la chitarra di Brian May o la voce di Freddie Mercury.",
            "signature": [
                "★ NON C'E' BATTERIA VERA — Brian May voleva un ritmo che il pubblico potesse fare dal vivo",
                "Stomp-stomp-CLAP: 4 dita bastano per riconoscerlo in mezzo mondo",
                "Kick = STOMP (piede sul palco), non kick drum",
                "Clap = applauso, non snare",
                "Hi-hat MUTED: nel brano originale non c'e' proprio",
                "Registrato overdubbando 4 membri della band che battevano piedi e mani",
            ],
            "try": [
                "Ascolta senza toccare niente — poi chiediti dove senti l'hi-hat che ti aspetti. Non c'e'.",
                "Pattern B aggiunge il snare: e' il momento in cui la band entra nel pezzo.",
                "Prova a portare BPM a 120 → diventa un'altra canzone",
                "Lo stomp-stomp-clap e' diventato lo standard degli stadi sportivi in tutto il mondo",
            ],
        },
    }


# =========================================================================
# 3) SEVEN NATION ARMY — 124 BPM (White Stripes, 2003)
# =========================================================================
# Il "DA-da-DA-DA-da-DA-da" degli stadi. Nel brano e' un riff di BASSO,
# ma e' diventato l'inno degli stadi sportivi cantato dalla gente, e
# funziona benissimo come pattern ritmico.
# Meg White suonava un groove minimal: kick + snare + niente hi-hat nel verso.

def build_sevennation():
    # A — skeleton Meg White: kick + snare con feel MINIMAL
    A = empty_pattern()
    set_steps(A, KICK, [0, 6, 8, 14], vel=1.0)  # kick che segue il riff di basso
    set_steps(A, SNARE, [4, 12], vel=0.95)      # backbeat solido

    # B — pieno con floor tom che fa il "DA-da-DA-DA-da-DA-da"
    B = empty_pattern()
    set_steps(B, KICK, [0, 6, 8, 14], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.95)
    # TOM come il "riff da stadio" — usando floor tom con pitch basso
    # Pattern: DA(0) -- da(2) DA(4) DA(5) da(7) DA(8) da(10) DA(12)
    # Semplifico: tom sui passaggi forti del riff
    B[TOM][2] = cell(vel=0.7)
    B[TOM][5] = cell(vel=0.75)
    B[TOM][10] = cell(vel=0.7)

    # C — quando entra l'hi-hat (seconda meta' del pezzo)
    C = empty_pattern()
    set_steps(C, KICK, [0, 6, 8, 14], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    # Hi-hat 8th quarter-feel (Meg non andava mai troppo fitta)
    for s in [0, 4, 8, 12]:
        C[HIHAT][s] = cell(vel=0.65)
    B_tom_steps = [2, 5, 10]
    for s in B_tom_steps:
        C[TOM][s] = cell(vel=0.7)

    # D — grande finale con kick+snare insieme (il drop piu' pesante)
    D = empty_pattern()
    set_steps(D, KICK, [0, 4, 6, 8, 12, 14], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.95)
    # Snare roll finale
    D[SNARE][14] = cell(vel=0.8, ratch=2)
    D[SNARE][15] = cell(vel=0.95, ratch=3)

    params = [
        # KICK — pitch basso, decay medio, Meg aveva un kick grosso
        tp(0.9, pitch=-2, decay=1.2),
        # SNARE — pitch medio, decay medio, "crack" garage rock
        tp(0.9, pitch=0, decay=0.95),
        # HI-HAT — usata minimalmente nel pezzo
        tp(0.55, pitch=0, decay=0.6, pan=0.15),
        tp(0.5, mute=True),
        tp(0.5, mute=True),  # Clap muted
        # TOM — floor tom GROSSO (il "DA-da-DA-DA" del riff)
        tp(0.85, pitch=-4, decay=1.5),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
    ]

    return {
        "version": 2, "bpm": 124, "swing": 0, "patternLength": 16,
        "humanize": False,  # Meg era minimal e tight
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "B", "B", "C", "B", "C", "D"],
        "_meta": {
            "title": "Seven Nation Army-style · 124 BPM",
            "inspired_by": "Seven Nation Army — The White Stripes (2003)",
            "disclaimer": "Pattern originale. Non riproduce il famoso riff di basso di Jack White (suonato con chitarra + ottavatore) ne' la voce.",
            "signature": [
                "Kick che segue il riff di basso: 0, 6, 8, 14 (non 4/4)",
                "Snare BACKBEAT solidissimo di Meg White",
                "TOM come eco del riff melodico — pitch -4, floor tom grosso",
                "Hi-hat entra solo nella seconda meta' (Pattern C)",
                "Zero humanize: The White Stripes erano tight quasi come una drum machine",
            ],
            "try": [
                "Pattern A = verso (solo kick+snare)",
                "Pattern B = aggiungi il 'riff di tom' che fa da controcanto al basso",
                "Pattern C = ritornello con hi-hat",
                "Pattern D = il drop finale con snare roll",
                "Diventato l'inno degli stadi sportivi globali (Italia 2006, Euro, NFL...)",
            ],
        },
    }


# =========================================================================
# 4) ANOTHER ONE BITES THE DUST — 110 BPM (Queen, 1980)
# =========================================================================
# "boom-boom-BAH boom-boom-BAH". Groove disco-rock di Roger Taylor,
# basso funky di John Deacon. Uno dei primi rock-disco crossover.

def build_anotherone():
    # A — skeleton funky: kick "and of 1" + snare backbeat
    A = empty_pattern()
    # boom(0) boom(3) BAH(4) / boom(8) boom(11) BAH(12)
    set_steps(A, KICK, [0, 3, 8, 11], vel=1.0)
    set_steps(A, SNARE, [4, 12], vel=0.95)
    # Hi-hat 8th
    for s in range(0, 16, 2):
        A[HIHAT][s] = cell(vel=0.6 if s % 4 == 0 else 0.5)

    # B — pattern pieno con groove funky Roger Taylor
    B = empty_pattern()
    set_steps(B, KICK, [0, 3, 8, 11], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.95)
    # Hi-hat 16th per il feel disco
    for s in range(16):
        B[HIHAT][s] = cell(vel=0.6 if s % 4 == 0 else 0.45)
    # Open hat sincopato (firma del pezzo)
    B[OPENHAT][6] = cell(vel=0.7)
    B[OPENHAT][14] = cell(vel=0.7)

    # C — variazione con clap disco layerato
    C = empty_pattern()
    set_steps(C, KICK, [0, 3, 8, 11], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.6 if s % 4 == 0 else 0.45)
    set_steps(C, OPENHAT, [6, 14], vel=0.7)
    # Clap disco (il "tsuck" anni 80)
    set_steps(C, CLAP, [4, 12], vel=0.6)

    # D — break con cowbell funky (Roger Taylor amava il cowbell)
    D = empty_pattern()
    set_steps(D, KICK, [0, 3, 8, 11], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        D[HIHAT][s] = cell(vel=0.6 if s % 4 == 0 else 0.45)
    set_steps(D, COW, [0, 4, 8, 12], vel=0.55)

    params = [
        tp(0.9, pitch=-1, decay=1.0),
        tp(0.9, pitch=0, decay=0.95),
        tp(0.6, pitch=1, decay=0.6, pan=0.15),
        tp(0.7, pitch=1, decay=1.1, pan=0.15),
        tp(0.65, pitch=0, decay=0.85, pan=-0.2),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
        tp(0.55, pitch=1, decay=0.8, pan=0.25, ftype='highpass', fcutoff=0.3),
    ]

    return {
        "version": 2, "bpm": 110, "swing": 5, "patternLength": 16,
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "C", "B", "C", "D", "B"],
        "_meta": {
            "title": "Another One Bites the Dust-style · 110 BPM",
            "inspired_by": "Another One Bites the Dust — Queen (The Game, 1980)",
            "disclaimer": "Pattern originale. Non riproduce il celebre riff di basso di John Deacon.",
            "signature": [
                "Kick 'boom-boom-BAH' (step 0, 3, 4): il groove rock-disco che ha cambiato Queen",
                "Hi-hat 16th disco (non 8th rock) = la firma della svolta discografica",
                "Open hat su step 6 e 14 = il 'respiro' funky",
                "Roger Taylor qui si dimostra drummer funky, non solo rock",
            ],
            "try": [
                "Senti come funziona anche solo Pattern A (skeleton)",
                "Pattern C aggiunge il clap disco = 1980 completo",
                "Uno dei primi incroci rock-disco-funk che ha fatto scuola",
            ],
        },
    }


# =========================================================================
# 5) SUPERSTITION — 100 BPM (Stevie Wonder, 1972)
# =========================================================================
# Stevie Wonder suonava LUI la batteria su questo pezzo. Groove funky
# 16th con GHOST NOTES sulla snare e hi-hat molto danzante.

def build_superstition():
    # A — skeleton funky
    A = empty_pattern()
    set_steps(A, KICK, [0, 6, 10], vel=1.0)
    set_steps(A, SNARE, [4, 12], vel=0.95)
    # Hi-hat 16th
    for s in range(16):
        A[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.45)

    # B — GHOST NOTES (il cuore del pezzo)
    B = empty_pattern()
    set_steps(B, KICK, [0, 6, 10], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.95)
    # Ghost notes sparse sulla snare — tipico di Stevie
    B[SNARE][3] = cell(vel=0.3, prob=80)
    B[SNARE][7] = cell(vel=0.35, prob=90)
    B[SNARE][11] = cell(vel=0.3, prob=75)
    B[SNARE][14] = cell(vel=0.4, prob=85)
    for s in range(16):
        B[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.45)
    # Open hat (firma del brano — quello "swung" al 6)
    B[OPENHAT][6] = cell(vel=0.8)

    # C — break con piu' ghost e tensione
    C = empty_pattern()
    set_steps(C, KICK, [0, 6, 10], vel=1.0)
    C[KICK][13] = cell(vel=0.7, prob=60)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    for g_s in [3, 7, 11, 14, 15]:
        C[SNARE][g_s] = cell(vel=0.35, prob=80)
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.45)
    set_steps(C, OPENHAT, [6, 14], vel=0.75)

    # D — stacco con fill
    D = empty_pattern()
    set_steps(D, KICK, [0, 6], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.95)
    D[SNARE][14] = cell(vel=0.7, ratch=2)
    D[SNARE][15] = cell(vel=0.85, ratch=2)
    for s in range(16):
        D[HIHAT][s] = cell(vel=0.6 if s % 4 == 0 else 0.4)
    D[TOM][13] = cell(vel=0.75)

    params = [
        tp(0.88, pitch=-2, decay=1.1),
        tp(0.85, pitch=0, decay=1.0),
        tp(0.6, pitch=-1, decay=0.65, pan=0.15),
        tp(0.7, pitch=-1, decay=1.2, pan=0.15),
        tp(0.5, mute=True),
        tp(0.7, pitch=1, decay=1.0),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
    ]

    return {
        "version": 2, "bpm": 100, "swing": 15, "patternLength": 16,
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "B", "C", "B", "D", "B"],
        "_meta": {
            "title": "Superstition-style · 100 BPM",
            "inspired_by": "Superstition — Stevie Wonder (Talking Book, 1972)",
            "disclaimer": "Pattern originale. Non riproduce il clavinet, la sezione fiati o la voce di Stevie Wonder.",
            "signature": [
                "Ghost notes sulla snare (step 3, 7, 11, 14) = IL motore del funk",
                "Swing 15% + humanize = feel umano ma non boom-bap lento",
                "Open hat al 6 (come Funky Drummer) = trigger del groove",
                "Stevie Wonder suonava TUTTI gli strumenti in questo pezzo — drum compresa",
            ],
            "try": [
                "Seleziona SNARE e premi S (solo) per isolare il ghost pattern",
                "E' il groove che ha reinventato il funk: ha messo il ghost note nella musica pop mainstream",
            ],
        },
    }


# =========================================================================
# 6) ROSANNA SHUFFLE — 87 BPM (Toto, 1982, Jeff Porcaro)
# =========================================================================
# Half-time shuffle. Uno dei groove piu' studiati al mondo. Terzine swing
# con ghost notes sulle parti deboli della terzina.

def build_rosanna():
    # Il Rosanna shuffle si basa su terzine in half-time.
    # In 16 step approximiamo con: beat 1, mid, beat 3 come accenti principali
    # e ghost tra mezzo.

    A = empty_pattern()
    # Kick su 1, snare su 9 (half-time = backbeat sul 3)
    A[KICK][0] = cell(vel=1.0)
    A[SNARE][8] = cell(vel=0.95)
    # Ride/hi-hat: terzine approssimate con accenti ogni 2-3 step
    # Semplifichiamo: hi-hat su ogni step ma con velocity che simula terzina
    # Pattern terzine "shuffle": DAH-da-da DAH-da-da = 1 (forte), 2-3 (deboli/ghost)
    # In 12 step: 0, 1, 2 | 3, 4, 5 | 6, 7, 8 | 9, 10, 11
    for s in range(16):
        # accento forte ogni "3 step" (approssimazione 16-step di una terzina)
        if s % 3 == 0:
            A[HIHAT][s] = cell(vel=0.75)
        else:
            A[HIHAT][s] = cell(vel=0.4)

    # B — il vero Rosanna shuffle con GHOST SNARE e ride pattern
    B = empty_pattern()
    B[KICK][0] = cell(vel=1.0)
    B[KICK][10] = cell(vel=0.8)  # kick "and of 3"
    B[SNARE][8] = cell(vel=0.95)
    # Ghost snare (la firma del pezzo!)
    B[SNARE][2] = cell(vel=0.3, prob=90)
    B[SNARE][4] = cell(vel=0.32, prob=85)
    B[SNARE][6] = cell(vel=0.3, prob=85)
    B[SNARE][11] = cell(vel=0.32, prob=85)
    B[SNARE][13] = cell(vel=0.3, prob=85)
    # Hi-hat shuffle pattern
    for s in range(16):
        if s % 3 == 0:
            B[HIHAT][s] = cell(vel=0.75)
        elif s % 3 == 1:
            B[HIHAT][s] = cell(vel=0.35, prob=50)
        else:
            B[HIHAT][s] = cell(vel=0.5)

    # C — pattern con piu' tensione, kick doppio
    C = empty_pattern()
    C[KICK][0] = cell(vel=1.0)
    C[KICK][3] = cell(vel=0.75)
    C[KICK][10] = cell(vel=0.85)
    C[SNARE][8] = cell(vel=0.95)
    for g_s in [2, 4, 6, 11, 13, 14]:
        C[SNARE][g_s] = cell(vel=0.32, prob=85)
    for s in range(16):
        if s % 3 == 0:
            C[HIHAT][s] = cell(vel=0.75)
        else:
            C[HIHAT][s] = cell(vel=0.4)

    # D — fill transizione con tom
    D = empty_pattern()
    D[KICK][0] = cell(vel=1.0)
    D[SNARE][8] = cell(vel=0.95)
    for g_s in [2, 4, 6, 11]:
        D[SNARE][g_s] = cell(vel=0.32, prob=85)
    for s in range(16):
        if s % 3 == 0:
            D[HIHAT][s] = cell(vel=0.75)
        else:
            D[HIHAT][s] = cell(vel=0.4)
    # Tom fill (Porcaro lo faceva sempre)
    D[TOM][12] = cell(vel=0.7)
    D[TOM][13] = cell(vel=0.8)
    D[TOM][14] = cell(vel=0.85)
    D[TOM][15] = cell(vel=0.9)

    params = [
        tp(0.88, pitch=-1, decay=1.1),
        tp(0.82, pitch=0, decay=1.0),
        tp(0.65, pitch=0, decay=0.7, pan=0.2),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
        tp(0.75, pitch=0, decay=1.0),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
    ]

    return {
        "version": 2, "bpm": 87, "swing": 62, "patternLength": 16,
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "C", "B", "C", "B", "D"],
        "_meta": {
            "title": "Rosanna Shuffle-style · 87 BPM (Half-time shuffle)",
            "inspired_by": "Rosanna — Toto (Toto IV, 1982), drum: Jeff Porcaro",
            "disclaimer": "Pattern originale. Non riproduce la melodia, la tastiera o la voce del brano.",
            "signature": [
                "★ SWING 62% — il massimo possibile, questo e' half-time shuffle",
                "Ghost notes FITTE sulla snare (step 2, 4, 6, 11, 13) = l'anima dello shuffle",
                "Kick su 1 + kick fantasma 'and of 3' = pattern 'bouncy' complesso",
                "Jeff Porcaro si ispirava al Purdie Shuffle (Bernard Purdie) e al Bonham Fool in the Rain",
                "Uno dei groove piu' studiati al mondo dai batteristi professionisti",
            ],
            "try": [
                "Abbassa SWING a 0% → perdi completamente il groove (capisci quanto conta)",
                "Isolatevi SNARE (S) per sentire il ghost pattern",
                "Porcaro diceva che il pattern era una combo di Bonham + Purdie + lui stesso",
            ],
        },
    }


# =========================================================================
# 7) STAYIN' ALIVE — 103 BPM (Bee Gees, 1977)
# =========================================================================
# Il prototipo del disco. 103 BPM = il ritmo IDEALE per le compressioni
# toraciche nella rianimazione cardiopolmonare (lo insegnano ai corsi).
# Kick 4/4 dritto + snare backbeat + hi-hat 16th + clap disco.

def build_stayinalive():
    A = empty_pattern()
    set_steps(A, KICK, [0, 4, 8, 12], vel=1.0)     # 4/4 dritto (disco)
    set_steps(A, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        A[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.45)

    B = empty_pattern()
    set_steps(B, KICK, [0, 4, 8, 12], vel=1.0)
    set_steps(B, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        B[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.45)
    # Clap disco (layer col snare) + open hat sincopato
    set_steps(B, CLAP, [4, 12], vel=0.7)
    set_steps(B, OPENHAT, [2, 6, 10, 14], vel=0.6)

    # C — pattern pieno disco con cowbell
    C = empty_pattern()
    set_steps(C, KICK, [0, 4, 8, 12], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.65 if s % 4 == 0 else 0.45)
    set_steps(C, CLAP, [4, 12], vel=0.7)
    set_steps(C, OPENHAT, [2, 6, 10, 14], vel=0.65)
    # Cowbell disco (firma anni 70)
    set_steps(C, COW, [0, 8], vel=0.5)

    # D — break con snare roll classico disco
    D = empty_pattern()
    set_steps(D, KICK, [0, 4, 8, 12], vel=1.0)
    set_steps(D, SNARE, [4, 12], vel=0.95)
    D[SNARE][14] = cell(vel=0.75, ratch=2)
    D[SNARE][15] = cell(vel=0.9, ratch=3)
    for s in range(16):
        D[HIHAT][s] = cell(vel=0.6 if s % 4 == 0 else 0.4)
    set_steps(D, CLAP, [4, 12], vel=0.7)

    params = [
        tp(0.9, pitch=-1, decay=1.0),
        tp(0.85, pitch=0, decay=0.95),
        tp(0.6, pitch=1, decay=0.5, pan=0.15),
        tp(0.7, pitch=1, decay=1.1, pan=0.15),
        tp(0.7, pitch=0, decay=0.9, pan=-0.2),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
        tp(0.55, pitch=1, decay=0.8, pan=0.25),
    ]

    return {
        "version": 2, "bpm": 103, "swing": 0, "patternLength": 16,
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "C", "B", "C", "D", "B"],
        "_meta": {
            "title": "Stayin' Alive-style · 103 BPM (RCP-ready!)",
            "inspired_by": "Stayin' Alive — Bee Gees (Saturday Night Fever, 1977)",
            "disclaimer": "Pattern originale. Non riproduce le voci dei Bee Gees, la chitarra o gli archi.",
            "signature": [
                "103 BPM = il ritmo ideale per le compressioni toraciche RCP",
                "L'American Heart Association lo raccomanda per la rianimazione cardiopolmonare dal 2008",
                "Kick 4/4 dritto (il 'four on the floor' disco classico)",
                "Clap layered sul snare = la firma sonora disco",
                "Open hat sugli off-beat (2, 6, 10, 14) = il 'tis-tis' dance",
            ],
            "try": [
                "Lo puoi letteralmente usare per esercitarti con le compressioni RCP (se hai fatto il corso)",
                "Pattern D ha lo snare roll disco alla fine = transizione da strofa a ritornello",
                "Prototipo del disco anni 70: kick dritto + snare forte + hi-hat 16th + clap",
            ],
        },
    }


# =========================================================================
# 8) TAKE FIVE — 172 BPM (Brubeck/Morello, 1959) — 5/4!
# =========================================================================
# ★ JAZZ IN 5/4. Usiamo patternLength=20 step (5 quarti x 4 subdivisions).
# Joe Morello suonava il ride pattern jazz con kick sul 1 e comping jazz.

def build_takefive():
    # patternLength 20 = 5 quarti in 16th
    # Step: 0,1,2,3 = beat 1 | 4,5,6,7 = beat 2 | 8,9,10,11 = beat 3
    # 12,13,14,15 = beat 4 | 16,17,18,19 = beat 5

    # A — skeleton minimale: kick su 1, snare comp sul 2 "and"
    A = empty_pattern()
    A[KICK][0] = cell(vel=1.0)               # beat 1
    A[SNARE][6] = cell(vel=0.65)             # beat 2 "and" (classico Morello)
    A[SNARE][14] = cell(vel=0.55, prob=80)   # beat 4 "and" comp
    # Ride jazz pattern (approssimo su hihat): swing 8th con accento sulla pulsazione
    for beat_start in [0, 4, 8, 12, 16]:
        A[HIHAT][beat_start] = cell(vel=0.7)     # ding
        A[HIHAT][beat_start + 2] = cell(vel=0.5) # ding-a
        if beat_start + 3 < 20:
            A[HIHAT][beat_start + 3] = cell(vel=0.4)  # ding-a-ling (swing)

    # B — jazz comping piu' denso (stile Morello nel verso)
    B = empty_pattern()
    B[KICK][0] = cell(vel=1.0)
    B[KICK][10] = cell(vel=0.6, prob=60)     # comping kick
    B[SNARE][6] = cell(vel=0.65)
    B[SNARE][10] = cell(vel=0.4, prob=70)    # ghost comp
    B[SNARE][14] = cell(vel=0.55)
    B[SNARE][18] = cell(vel=0.4, prob=60)
    for beat_start in [0, 4, 8, 12, 16]:
        B[HIHAT][beat_start] = cell(vel=0.7)
        B[HIHAT][beat_start + 2] = cell(vel=0.5)
        if beat_start + 3 < 20:
            B[HIHAT][beat_start + 3] = cell(vel=0.4)

    # C — il celebre drum SOLO (Morello faceva il solo in 5/4)
    C = empty_pattern()
    C[KICK][0] = cell(vel=1.0)
    # Snare solo pattern con accenti jazz
    set_steps(C, SNARE, [2, 6, 10, 14, 18], vel=0.7)
    C[SNARE][7] = cell(vel=0.4, prob=80)
    C[SNARE][11] = cell(vel=0.4, prob=80)
    C[SNARE][15] = cell(vel=0.45, prob=80)
    # Tom fills occasionali
    C[TOM][9] = cell(vel=0.65, prob=70)
    C[TOM][17] = cell(vel=0.7, prob=75)
    # Ride continua
    for beat_start in [0, 4, 8, 12, 16]:
        C[HIHAT][beat_start] = cell(vel=0.65)
        C[HIHAT][beat_start + 2] = cell(vel=0.5)

    # D — ritorno al tema dopo il solo
    D = empty_pattern()
    D[KICK][0] = cell(vel=1.0)
    D[SNARE][6] = cell(vel=0.7)
    D[SNARE][14] = cell(vel=0.6)
    # Ride swing pattern
    for beat_start in [0, 4, 8, 12, 16]:
        D[HIHAT][beat_start] = cell(vel=0.75)
        D[HIHAT][beat_start + 2] = cell(vel=0.55)
        if beat_start + 3 < 20:
            D[HIHAT][beat_start + 3] = cell(vel=0.45)

    params = [
        tp(0.75, pitch=-2, decay=1.2),
        tp(0.7, pitch=-1, decay=1.1),
        # HI-HAT = RIDE jazz: pitch basso per timbro ride, decay lungo
        tp(0.65, pitch=-5, decay=1.4, pan=0.15),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
        tp(0.65, pitch=-1, decay=1.2),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
    ]

    return {
        "version": 2, "bpm": 172, "swing": 55, "patternLength": 20,  # ★ 5/4!
        "humanize": True,
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "B", "B", "C", "B", "D", "B", "A"],
        "_meta": {
            "title": "Take Five-style · 172 BPM · 5/4",
            "inspired_by": "Take Five — Dave Brubeck Quartet (Time Out, 1959), drum: Joe Morello",
            "disclaimer": "Pattern originale. Non riproduce il tema di sax alto di Paul Desmond o il pianoforte di Brubeck.",
            "signature": [
                "★ METRO 5/4 — patternLength 20 step (non 16!) = 5 quarti di 4 sixteenth",
                "Swing 55% = feel jazz 'triplet' classico",
                "HI-HAT pitch -5 = simula RIDE CYMBAL jazz (non il closed hi-hat)",
                "Kick sul beat 1, snare comping sul 2-and e 4-and (Morello style)",
                "Pattern C = il celebre drum solo di Morello (l'uno dei piu' famosi jazz)",
            ],
            "try": [
                "Conta: 1-2-3-4-5, 1-2-3-4-5. Non conta piu' in 4.",
                "★ Questo e' l'UNICO pattern della libreria in 5/4 — prima esplorazione del 'compound time' nel jazz pop",
                "'Take Five' ha venduto piu' di un milione di copie, primo jazz single di successo",
                "Era 1959: prima di questo pezzo nessuno pensava che il pubblico pop potesse ballare in 5",
            ],
        },
    }


# =========================================================================
# 9) WIPE OUT — 162 BPM (The Surfaris, 1963)
# =========================================================================
# Il drum solo di surf rock piu' famoso. Single stroke 16th costante,
# accenti alternati, tom roll. Era un rullo di tamburo continuo.

def build_wipeout():
    # A — il drum solo classico: single stroke 16th su snare
    A = empty_pattern()
    # 16th continui per tutta la misura con accenti "da-DA-da-da DA-da-da-da"
    for s in range(16):
        # accenti sul 1, 5, 9, 13 (downbeat di ogni beat)
        A[SNARE][s] = cell(vel=0.85 if s % 4 == 0 else 0.5)
    # Kick appena sul 1 e 9 per tenere il tempo
    A[KICK][0] = cell(vel=1.0)
    A[KICK][8] = cell(vel=1.0)

    # B — pattern con tom roll (il momento tom del brano)
    B = empty_pattern()
    # Meta' snare, meta' tom (alternanza)
    for s in [0, 1, 2, 3, 8, 9, 10, 11]:
        B[SNARE][s] = cell(vel=0.85 if s % 4 == 0 else 0.55)
    for s in [4, 5, 6, 7, 12, 13, 14, 15]:
        B[TOM][s] = cell(vel=0.8 if s % 4 == 0 else 0.55)
    A[KICK][0] = cell(vel=1.0)
    B[KICK][0] = cell(vel=1.0)
    B[KICK][8] = cell(vel=1.0)

    # C — band groove surf rock (kick+snare backbeat + hi-hat 16th)
    C = empty_pattern()
    set_steps(C, KICK, [0, 8], vel=1.0)
    set_steps(C, SNARE, [4, 12], vel=0.95)
    for s in range(16):
        C[HIHAT][s] = cell(vel=0.65 if s % 2 == 0 else 0.45)

    # D — il GRAN fill con tom roll crescente (il finale celebre)
    D = empty_pattern()
    D[KICK][0] = cell(vel=1.0)
    D[KICK][8] = cell(vel=1.0)
    # Tom roll ascendente: tom basso → tom alto (simulato con velocity)
    for s in range(8):
        D[TOM][s] = cell(vel=0.55 + s * 0.05)  # crescendo
    for s in range(8, 16):
        D[SNARE][s] = cell(vel=0.7 + (s - 8) * 0.04, ratch=2 if s >= 12 else 1)

    params = [
        tp(0.85, pitch=-1, decay=1.0),
        tp(0.9, pitch=1, decay=0.8),  # snare surf: pitch alto, "crack"
        tp(0.6, pitch=1, decay=0.55, pan=0.15),
        tp(0.5, mute=True),
        tp(0.5, mute=True),
        tp(0.85, pitch=-2, decay=1.0),  # tom: pitch basso, "thud"
        tp(0.5, mute=True),
        tp(0.5, mute=True),
    ]

    return {
        "version": 2, "bpm": 162, "swing": 0, "patternLength": 16,
        "humanize": False,  # Wipe Out e' meccanico, tight
        "trackParams": params,
        "patterns": {"A": A, "B": B, "C": C, "D": D},
        "songSequence": ["A", "A", "B", "A", "B", "C", "A", "D"],
        "_meta": {
            "title": "Wipe Out-style · 162 BPM (surf drum solo)",
            "inspired_by": "Wipe Out — The Surfaris (1963)",
            "disclaimer": "Pattern originale. Non riproduce la chitarra surf o la celebre risata iniziale del brano.",
            "signature": [
                "Single stroke 16th continui sulla snare = IL riff del pezzo",
                "Accenti sui downbeat (0, 4, 8, 12) = 'da-DA-da-da'",
                "Pattern B = sezione con tom (meta' pezzo)",
                "Pattern D = tom roll crescente finale",
                "Il primo drum solo che i bambini americani hanno imparato — prima di 'Tom Sawyer' (1981)",
            ],
            "try": [
                "Porta BPM a 180 → diventa un'esercitazione da drummer vero",
                "Porta BPM a 140 → senti il surf rock 'rilassato'",
                "162 BPM = velocita' originale del disco (1963)",
            ],
        },
    }


# =========================================================================
# GENERA TUTTO
# =========================================================================

if __name__ == "__main__":
    demos = [
        ("dadada",          build_dadada()),
        ("wewillrockyou",   build_wewillrockyou()),
        ("sevennation",     build_sevennation()),
        ("anotherone",      build_anotherone()),
        ("superstition",    build_superstition()),
        ("rosanna",         build_rosanna()),
        ("stayinalive",     build_stayinalive()),
        ("takefive",        build_takefive()),
        ("wipeout",         build_wipeout()),
    ]
    for name, data in demos:
        save(name, data)
        hits = sum(1 for p in data["patterns"].values() for t in p for s in t if s)
        bpm = data["bpm"]
        song_len = len(data["songSequence"])
        pat_len = data["patternLength"]
        total_sec = song_len * pat_len / (bpm / 60 * 4)
        print(f"  ✓ demo-{name}.json  ·  {bpm} BPM  ·  {pat_len} step  ·  {hits} hits  ·  {total_sec:.1f}s")
    print(f"\n{len(demos)} demo generate in examples/")

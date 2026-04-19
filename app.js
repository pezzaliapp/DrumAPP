/* ==============================================================
   DrumAPP · PRO Edition
   Drum machine 8 voci, 16-step con swing/velocity/probability/ratchet,
   filter+pitch+decay per traccia, 4 pattern live + song mode,
   export WAV, Web MIDI, undo/redo.

   Tutto Web Audio, niente samples, niente dipendenze esterne.
   ============================================================== */

(() => {
  'use strict';

  // ============================================================
  // 1) COSTANTI
  // ============================================================
  const NUM_STEPS_DEFAULT = 16;
  const MIN_STEPS = 8;
  const MAX_STEPS = 32;
  const LOOKAHEAD_MS = 25;
  const SCHEDULE_AHEAD = 0.1; // secondi
  const HOLD_MS = 500;
  const MAX_HISTORY = 40;

  // ============================================================
  // 2) DEFINIZIONE TRACCE (8 voci)
  // ============================================================
  const TRACK_DEFS = [
    { id: 'kick',    name: 'KICK',    color: 'var(--track-kick)' },
    { id: 'snare',   name: 'SNARE',   color: 'var(--track-snare)' },
    { id: 'hihat',   name: 'HI-HAT',  color: 'var(--track-hihat)' },
    { id: 'openhat', name: 'OPEN HH', color: 'var(--track-openhat)' },
    { id: 'clap',    name: 'CLAP',    color: 'var(--track-clap)' },
    { id: 'tom',     name: 'TOM',     color: 'var(--track-tom)' },
    { id: 'rim',     name: 'RIMSHOT', color: 'var(--track-rim)' },
    { id: 'cow',     name: 'COWBELL', color: 'var(--track-cow)' },
  ];
  const NUM_TRACKS = TRACK_DEFS.length;

  // ============================================================
  // 3) STATO
  // ============================================================

  /**
   * Ogni "cella" del sequencer è:
   *   null  -> step spento
   *   { vel, prob, ratch, nudge }  -> step attivo
   *
   *   vel:   0.05-1.0   (velocity 0=silenzio, 1=max)
   *   prob:  0-100      (% di probabilità di triggerare)
   *   ratch: 1-4        (ripetizioni dentro lo step)
   *   nudge: -50..+50   (millisecondi di sposto dal grid)
   */
  function makeEmptyPattern() {
    const p = [];
    for (let t = 0; t < NUM_TRACKS; t++) {
      p.push(new Array(MAX_STEPS).fill(null));
    }
    return p;
  }

  let patterns = {
    A: makeEmptyPattern(),
    B: makeEmptyPattern(),
    C: makeEmptyPattern(),
    D: makeEmptyPattern(),
  };
  let currentPattern = 'A';

  /** Parametri per traccia (condivisi tra tutti i pattern) */
  let trackParams = TRACK_DEFS.map(() => ({
    volume: 0.85,
    mute: false,
    solo: false,
    pitch: 0,            // semitoni ±12
    decay: 1.0,          // moltiplicatore (0.4 - 2.5)
    filterType: 'off',   // off / lowpass / highpass
    filterCutoff: 0.7,   // 0-1 (mappato 20Hz-20kHz esponenziale)
    filterQ: 1.0,        // 0.5-10
    pan: 0,              // -1 (full L) .. +1 (full R)
  }));

  // Globals
  let bpm = 120;
  let swing = 0;           // 0-75 (%)
  let humanize = false;
  let metronome = false;
  let patternLength = 16;

  let editMode = 'trig';   // trig / vel / prob / ratch / nudge
  let activeTrack = 0;     // traccia selezionata (per panel di editing)

  // Song mode
  let songMode = false;
  let songSequence = ['A', 'A', 'B', 'A'];
  let songStep = 0;

  // Undo/redo
  let history = [];
  let historyIndex = -1;

  // Audio
  let audioCtx = null;
  let masterGain = null;
  let noiseBuffer = null;

  // Catena audio per traccia
  let trackFilters = [];
  let trackGains = [];
  let trackPanners = [];

  // Pattern clipboard (copy/paste)
  let patternClipboard = null;

  // Scheduler
  let nextStepTime = 0;
  let schedulerTimer = null;
  let currentStep = 0;
  let uiQueue = [];
  let playing = false;

  // DOM cache
  let stepElements = []; // [track][step] -> button

  // MIDI
  let midiAccess = null;
  let midiOut = null;

  // REC live (MediaRecorder su MediaStreamDestination)
  let mediaRecDest = null;
  let mediaRecorder = null;
  let recChunks = [];
  let isRecording = false;
  let recStartTime = 0;
  let recTimerHandle = null;

  // Tap tempo state
  let tapTimes = [];

  // ============================================================
  // 4) INIZIALIZZAZIONE AUDIO
  // ============================================================
  function initAudio() {
    if (audioCtx) return;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    audioCtx = new Ctx();
    masterGain = audioCtx.createGain();
    masterGain.gain.value = 0.75;
    masterGain.connect(audioCtx.destination);

    // Destination parallelo per il REC live (MediaRecorder)
    try {
      mediaRecDest = audioCtx.createMediaStreamDestination();
      masterGain.connect(mediaRecDest);
    } catch (e) {
      mediaRecDest = null;
    }

    // Rumore bianco pregenerato, condiviso
    const len = audioCtx.sampleRate * 2;
    noiseBuffer = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
    const data = noiseBuffer.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;

    // Catena per traccia: voice -> trackPanner[i] -> trackFilter[i] -> trackGain[i] -> masterGain
    for (let i = 0; i < NUM_TRACKS; i++) {
      const pan = audioCtx.createStereoPanner
        ? audioCtx.createStereoPanner()
        : null;

      const f = audioCtx.createBiquadFilter();
      f.type = 'lowpass';
      f.frequency.value = 20000;
      f.Q.value = 1.0;

      const g = audioCtx.createGain();
      g.gain.value = trackParams[i].volume;

      if (pan) {
        pan.pan.value = trackParams[i].pan || 0;
        pan.connect(f).connect(g).connect(masterGain);
      } else {
        f.connect(g).connect(masterGain);
      }

      trackPanners.push(pan); // può essere null su browser vintage
      trackFilters.push(f);
      trackGains.push(g);
    }
    applyTrackParams();
  }

  function unlockAudio() {
    initAudio();
    if (audioCtx.state === 'suspended') audioCtx.resume();
  }

  /** Aggiorna ogni filter/gain/pan in base a trackParams e mute/solo */
  function applyTrackParams() {
    if (!audioCtx) return;
    const anySolo = trackParams.some(p => p.solo);
    for (let i = 0; i < NUM_TRACKS; i++) {
      const p = trackParams[i];
      // Gain (mute/solo)
      let vol = p.volume;
      if (p.mute) vol = 0;
      else if (anySolo && !p.solo) vol = 0;
      trackGains[i].gain.setTargetAtTime(vol, audioCtx.currentTime, 0.01);

      // Pan
      if (trackPanners[i]) {
        trackPanners[i].pan.setTargetAtTime(p.pan || 0, audioCtx.currentTime, 0.01);
      }

      // Filter
      const f = trackFilters[i];
      if (p.filterType === 'off') {
        f.type = 'lowpass';
        f.frequency.setTargetAtTime(20000, audioCtx.currentTime, 0.01);
        f.Q.setTargetAtTime(0.707, audioCtx.currentTime, 0.01);
      } else {
        f.type = p.filterType;
        // Mapping esponenziale 0-1 -> 50Hz-18kHz
        const hz = 50 * Math.pow(360, p.filterCutoff);
        f.frequency.setTargetAtTime(hz, audioCtx.currentTime, 0.01);
        f.Q.setTargetAtTime(p.filterQ, audioCtx.currentTime, 0.01);
      }
    }
  }

  // ============================================================
  // 5) SINTESI DELLE 8 VOCI
  //    Ogni voce accetta (time, params) dove params include:
  //      - trackIdx (per connettersi al filter/gain corretto)
  //      - pitch (semitoni)
  //      - decayMul (moltiplicatore decay)
  //      - vel (0-1 velocity per lo step)
  // ============================================================

  /** Utility: fattore di pitch da semitoni */
  const semi = s => Math.pow(2, s / 12);

  /** Ritorna il nodo di uscita della traccia i (dove connettere le voci) */
  function trackOut(i) {
    return trackPanners[i] || trackFilters[i];
  }

  function playKick(time, p) {
    const out = trackOut(p.trackIdx);
    const pitch = semi(p.pitch);
    const dMul = p.decayMul;
    const vel = p.vel;

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(165 * pitch, time);
    osc.frequency.exponentialRampToValueAtTime(45 * pitch, time + 0.12 * dMul);
    gain.gain.setValueAtTime(vel, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.45 * dMul);
    osc.connect(gain).connect(out);
    osc.start(time);
    osc.stop(time + 0.5 * dMul + 0.02);

    // Click
    const click = audioCtx.createOscillator();
    const cGain = audioCtx.createGain();
    click.type = 'sine';
    click.frequency.setValueAtTime(1200 * pitch, time);
    cGain.gain.setValueAtTime(0.35 * vel, time);
    cGain.gain.exponentialRampToValueAtTime(0.001, time + 0.025);
    click.connect(cGain).connect(out);
    click.start(time);
    click.stop(time + 0.05);
  }

  function playSnare(time, p) {
    const out = trackOut(p.trackIdx);
    const pitch = semi(p.pitch);
    const dMul = p.decayMul;
    const vel = p.vel;

    const osc = audioCtx.createOscillator();
    const oGain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(220 * pitch, time);
    oGain.gain.setValueAtTime(0.5 * vel, time);
    oGain.gain.exponentialRampToValueAtTime(0.001, time + 0.11 * dMul);
    osc.connect(oGain).connect(out);
    osc.start(time);
    osc.stop(time + 0.2 * dMul);

    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    const hp = audioCtx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.value = 1000;
    const nGain = audioCtx.createGain();
    nGain.gain.setValueAtTime(0.7 * vel, time);
    nGain.gain.exponentialRampToValueAtTime(0.001, time + 0.17 * dMul);
    noise.connect(hp).connect(nGain).connect(out);
    noise.start(time);
    noise.stop(time + 0.22 * dMul);
  }

  function playHihat(time, p) {
    const out = trackOut(p.trackIdx);
    const dMul = p.decayMul;
    const vel = p.vel;

    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    const hp = audioCtx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.value = 7000 * semi(p.pitch * 0.5);
    const gain = audioCtx.createGain();
    gain.gain.setValueAtTime(0.45 * vel, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.055 * dMul);
    noise.connect(hp).connect(gain).connect(out);
    noise.start(time);
    noise.stop(time + 0.1 * dMul);
  }

  function playOpenhat(time, p) {
    const out = trackOut(p.trackIdx);
    const dMul = p.decayMul;
    const vel = p.vel;

    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    const hp = audioCtx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.value = 6500 * semi(p.pitch * 0.5);
    const gain = audioCtx.createGain();
    gain.gain.setValueAtTime(0.0001, time);
    gain.gain.linearRampToValueAtTime(0.4 * vel, time + 0.003);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.45 * dMul);
    noise.connect(hp).connect(gain).connect(out);
    noise.start(time);
    noise.stop(time + 0.5 * dMul);
  }

  function playClap(time, p) {
    const out = trackOut(p.trackIdx);
    const dMul = p.decayMul;
    const vel = p.vel;

    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    const bp = audioCtx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 1500 * semi(p.pitch);
    bp.Q.value = 0.9;
    const gain = audioCtx.createGain();

    gain.gain.setValueAtTime(0.0001, time);
    gain.gain.linearRampToValueAtTime(0.85 * vel, time + 0.002);
    gain.gain.exponentialRampToValueAtTime(0.15, time + 0.013);
    gain.gain.linearRampToValueAtTime(0.85 * vel, time + 0.016);
    gain.gain.exponentialRampToValueAtTime(0.15, time + 0.027);
    gain.gain.linearRampToValueAtTime(0.85 * vel, time + 0.030);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.32 * dMul);

    noise.connect(bp).connect(gain).connect(out);
    noise.start(time);
    noise.stop(time + 0.35 * dMul);
  }

  function playTom(time, p) {
    const out = trackOut(p.trackIdx);
    const pitch = semi(p.pitch);
    const dMul = p.decayMul;
    const vel = p.vel;

    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(180 * pitch, time);
    osc.frequency.exponentialRampToValueAtTime(90 * pitch, time + 0.15 * dMul);
    gain.gain.setValueAtTime(0.8 * vel, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.6 * dMul);
    osc.connect(gain).connect(out);
    osc.start(time);
    osc.stop(time + 0.65 * dMul);

    // piccolo noise transient
    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    const bp = audioCtx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 400;
    bp.Q.value = 1.2;
    const nGain = audioCtx.createGain();
    nGain.gain.setValueAtTime(0.2 * vel, time);
    nGain.gain.exponentialRampToValueAtTime(0.001, time + 0.03);
    noise.connect(bp).connect(nGain).connect(out);
    noise.start(time);
    noise.stop(time + 0.05);
  }

  function playRim(time, p) {
    const out = trackOut(p.trackIdx);
    const pitch = semi(p.pitch);
    const vel = p.vel;

    // Due oscillatori stretti con attacco brutale
    const o1 = audioCtx.createOscillator();
    const o2 = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o1.type = 'square';
    o2.type = 'triangle';
    o1.frequency.setValueAtTime(800 * pitch, time);
    o2.frequency.setValueAtTime(380 * pitch, time);
    g.gain.setValueAtTime(0.5 * vel, time);
    g.gain.exponentialRampToValueAtTime(0.001, time + 0.05 * p.decayMul);
    const bp = audioCtx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 1800 * pitch;
    bp.Q.value = 3;
    o1.connect(bp);
    o2.connect(bp);
    bp.connect(g).connect(out);
    o1.start(time); o2.start(time);
    o1.stop(time + 0.08); o2.stop(time + 0.08);
  }

  function playCow(time, p) {
    const out = trackOut(p.trackIdx);
    const pitch = semi(p.pitch);
    const dMul = p.decayMul;
    const vel = p.vel;

    // Cowbell TR-808 classica: due square a 540Hz e 800Hz
    const o1 = audioCtx.createOscillator();
    const o2 = audioCtx.createOscillator();
    o1.type = 'square';
    o2.type = 'square';
    o1.frequency.setValueAtTime(540 * pitch, time);
    o2.frequency.setValueAtTime(800 * pitch, time);

    const mix = audioCtx.createGain();
    mix.gain.value = 0.5;
    const bp = audioCtx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 2000 * pitch;
    bp.Q.value = 1.5;

    const env = audioCtx.createGain();
    env.gain.setValueAtTime(0.0001, time);
    env.gain.linearRampToValueAtTime(0.35 * vel, time + 0.004);
    env.gain.exponentialRampToValueAtTime(0.001, time + 0.3 * dMul);

    o1.connect(mix); o2.connect(mix);
    mix.connect(bp).connect(env).connect(out);
    o1.start(time); o2.start(time);
    o1.stop(time + 0.35 * dMul);
    o2.stop(time + 0.35 * dMul);
  }

  const VOICES = {
    kick:    playKick,
    snare:   playSnare,
    hihat:   playHihat,
    openhat: playOpenhat,
    clap:    playClap,
    tom:     playTom,
    rim:     playRim,
    cow:     playCow,
  };

  // ============================================================
  // 6) METRONOMO (click alto sul primo beat, basso sugli altri)
  // ============================================================
  function playMetronome(time, isDownbeat) {
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(isDownbeat ? 1600 : 1000, time);
    gain.gain.setValueAtTime(0.15, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.04);
    osc.connect(gain).connect(masterGain);
    osc.start(time);
    osc.stop(time + 0.05);
  }

  // ============================================================
  // 7) SCHEDULER
  // ============================================================

  /** Calcola il tempo di inizio di uno step considerando swing */
  function stepTimeOffset(stepIdx, secondsPerStep) {
    // Swing: ritarda gli step dispari (off-beat) di una frazione
    if (stepIdx % 2 === 1 && swing > 0) {
      return (swing / 100) * secondsPerStep * 0.5;
    }
    return 0;
  }

  function playTrackStep(trackIdx, stepIdx, time) {
    const pattern = patterns[currentPattern][trackIdx];
    const cell = pattern[stepIdx];
    if (!cell) return;

    // Probability (dado)
    if (cell.prob < 100 && Math.random() * 100 >= cell.prob) return;

    const tp = trackParams[trackIdx];
    // Se in mute o non in solo mentre qualcuno solo -> skip (il gain e' gia' 0 ma evitiamo sprechi)
    const anySolo = trackParams.some(p => p.solo);
    if (tp.mute || (anySolo && !tp.solo)) return;

    // Humanize: piccola variazione di timing/velocity
    const hTime = humanize ? (Math.random() - 0.5) * 0.012 : 0;
    const hVel  = humanize ? (Math.random() - 0.5) * 0.15 : 0;

    // Nudge manuale (ms)
    const nudgeSec = (cell.nudge || 0) / 1000;

    // Ratchet: N hit in un singolo step
    const ratch = cell.ratch || 1;
    const secondsPerStep = (60.0 / bpm) / 4;
    const ratchGap = (secondsPerStep * 0.9) / ratch;

    for (let r = 0; r < ratch; r++) {
      const t = time + nudgeSec + hTime + r * ratchGap;
      if (t < audioCtx.currentTime) continue;
      const vel = Math.max(0.05, Math.min(1, cell.vel + hVel));
      const voice = VOICES[TRACK_DEFS[trackIdx].id];
      voice(t, {
        trackIdx,
        pitch: tp.pitch,
        decayMul: tp.decay,
        vel: vel * (r === 0 ? 1.0 : 0.7), // i ratchet successivi più deboli
      });
    }

    // MIDI out (note on/off)
    sendMidiForTrack(trackIdx, cell.vel, time);
  }

  function scheduleStep(stepIdx, baseTime) {
    const secondsPerStep = (60.0 / bpm) / 4;
    const stepTime = baseTime + stepTimeOffset(stepIdx, secondsPerStep);

    for (let t = 0; t < NUM_TRACKS; t++) {
      playTrackStep(t, stepIdx, stepTime);
    }

    // Metronome (un click ogni quarto = ogni 4 step)
    if (metronome && stepIdx % 4 === 0) {
      playMetronome(baseTime, stepIdx === 0);
    }

    uiQueue.push({ step: stepIdx, time: stepTime });
  }

  function advance() {
    const secondsPerBeat = 60.0 / bpm;
    nextStepTime += 0.25 * secondsPerBeat;
    currentStep++;
    if (currentStep >= patternLength) {
      currentStep = 0;
      // Song mode: avanza al prossimo pattern
      if (songMode && songSequence.length > 0) {
        songStep = (songStep + 1) % songSequence.length;
        const nextName = songSequence[songStep];
        if (patterns[nextName]) {
          currentPattern = nextName;
          refreshPatternUI();
          updatePatternButtons();
          updateSongCurrentSlot();
        }
      }
    }
  }

  function scheduler() {
    while (nextStepTime < audioCtx.currentTime + SCHEDULE_AHEAD) {
      scheduleStep(currentStep, nextStepTime);
      advance();
    }
  }

  // ============================================================
  // 8) PLAY / STOP
  // ============================================================
  function start() {
    unlockAudio();
    playing = true;
    currentStep = 0;
    songStep = 0;
    nextStepTime = audioCtx.currentTime + 0.08;
    uiQueue = [];
    schedulerTimer = setInterval(scheduler, LOOKAHEAD_MS);
    updateTransportUI();
    requestAnimationFrame(tickUI);
  }

  function stop() {
    playing = false;
    if (schedulerTimer) { clearInterval(schedulerTimer); schedulerTimer = null; }
    uiQueue = [];
    clearPlayingHighlights();
    updateTransportUI();
    // All notes off MIDI
    if (midiOut) {
      for (let n = 35; n < 82; n++) midiOut.send([0x80, n, 0]);
    }
  }

  function toggleTransport() {
    playing ? stop() : start();
  }

  // ============================================================
  // 9) UNDO / REDO
  // ============================================================
  function snapshot() {
    // Salva pattern + trackParams
    return JSON.stringify({
      patterns,
      trackParams,
      bpm, swing, patternLength, songSequence,
    });
  }

  function pushHistory() {
    // Tronca il "futuro" se siamo in mezzo a una sequenza di undo
    history = history.slice(0, historyIndex + 1);
    history.push(snapshot());
    if (history.length > MAX_HISTORY) history.shift();
    historyIndex = history.length - 1;
  }

  function restoreFrom(jsonStr) {
    try {
      const s = JSON.parse(jsonStr);
      patterns = s.patterns;
      trackParams = s.trackParams;
      bpm = s.bpm; swing = s.swing;
      patternLength = s.patternLength;
      songSequence = s.songSequence;
      refreshAllUI();
      applyTrackParams();
    } catch (e) {
      showToast('Undo fallito', true);
    }
  }

  function undo() {
    if (historyIndex <= 0) { showToast('Niente da annullare'); return; }
    historyIndex--;
    restoreFrom(history[historyIndex]);
    showToast('Annullato');
  }

  function redo() {
    if (historyIndex >= history.length - 1) { showToast('Niente da ripetere'); return; }
    historyIndex++;
    restoreFrom(history[historyIndex]);
    showToast('Ripetuto');
  }

  // ============================================================
  // 10) COSTRUZIONE SEQUENCER UI
  // ============================================================
  function buildSequencer() {
    const root = document.getElementById('sequencer');
    root.innerHTML = '';
    stepElements = TRACK_DEFS.map(() => new Array(MAX_STEPS));

    // Riga numeri step
    const numRow = document.createElement('div');
    numRow.className = 'seq__row seq__row--numbers';
    numRow.appendChild(makeTrackLabelPlaceholder());
    numRow.appendChild(makeStepGrid((s) => {
      const el = document.createElement('div');
      el.className = 'step-number' + (s % 4 === 0 ? ' step-number--downbeat' : '');
      el.textContent = String(s + 1).padStart(2, '0');
      return el;
    }));
    root.appendChild(numRow);

    // Righe tracce
    TRACK_DEFS.forEach((track, trackIdx) => {
      const row = document.createElement('div');
      row.className = 'seq__row';
      row.dataset.track = String(trackIdx);
      row.style.setProperty('--track-color', track.color);

      // Etichetta traccia (con mute/solo)
      row.appendChild(makeTrackLabel(track, trackIdx));

      // Griglia degli step
      row.appendChild(makeStepGrid((s) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'step';
        btn.dataset.track = String(trackIdx);
        btn.dataset.step = String(s);
        btn.setAttribute('aria-label', `${track.name} step ${s + 1}`);

        // Inner: barra velocity
        const bar = document.createElement('span');
        bar.className = 'step__bar';
        btn.appendChild(bar);

        // Indicatori (prob / ratch / nudge)
        const ind = document.createElement('span');
        ind.className = 'step__ind';
        btn.appendChild(ind);

        attachStepHandlers(btn, trackIdx, s);
        stepElements[trackIdx][s] = btn;
        return btn;
      }));

      root.appendChild(row);
    });
  }

  function makeStepGrid(cellFactory) {
    const wrap = document.createElement('div');
    wrap.className = 'beats';
    // Le celle sono generate come grid CSS. Numero visibile dipende da patternLength.
    for (let s = 0; s < MAX_STEPS; s++) {
      const cell = cellFactory(s);
      cell.classList.add('beat-cell');
      if (s >= patternLength) cell.classList.add('beat-cell--hidden');
      if (s % 4 === 0) cell.classList.add('beat-cell--downbeat');
      wrap.appendChild(cell);
    }
    return wrap;
  }

  function makeTrackLabel(track, idx) {
    const label = document.createElement('div');
    label.className = 'seq__label';
    label.dataset.track = String(idx);

    const dot = document.createElement('span');
    dot.className = 'seq__dot';
    label.appendChild(dot);

    const name = document.createElement('button');
    name.type = 'button';
    name.className = 'seq__name';
    name.textContent = track.name;
    name.addEventListener('click', () => setActiveTrack(idx));
    label.appendChild(name);

    const mute = document.createElement('button');
    mute.type = 'button';
    mute.className = 'ts-btn ts-btn--mute';
    mute.textContent = 'M';
    mute.title = 'Mute';
    mute.addEventListener('click', () => {
      trackParams[idx].mute = !trackParams[idx].mute;
      applyTrackParams();
      updateTrackControls();
    });
    label.appendChild(mute);

    const solo = document.createElement('button');
    solo.type = 'button';
    solo.className = 'ts-btn ts-btn--solo';
    solo.textContent = 'S';
    solo.title = 'Solo';
    solo.addEventListener('click', () => {
      trackParams[idx].solo = !trackParams[idx].solo;
      applyTrackParams();
      updateTrackControls();
    });
    label.appendChild(solo);

    return label;
  }

  function makeTrackLabelPlaceholder() {
    const label = document.createElement('div');
    label.className = 'seq__label seq__label--placeholder';
    return label;
  }

  // ============================================================
  // 11) GESTORI STEP (click / drag per edit mode)
  // ============================================================
  function attachStepHandlers(btn, trackIdx, stepIdx) {
    let dragStartY = null;
    let dragStartValue = null;
    let didDrag = false;

    btn.addEventListener('pointerdown', (e) => {
      unlockAudio();
      btn.setPointerCapture(e.pointerId);
      didDrag = false;
      const cell = patterns[currentPattern][trackIdx][stepIdx];

      if (editMode === 'trig') {
        // Toggle
        if (cell) {
          patterns[currentPattern][trackIdx][stepIdx] = null;
        } else {
          patterns[currentPattern][trackIdx][stepIdx] = newCell();
          // preview
          if (audioCtx) {
            VOICES[TRACK_DEFS[trackIdx].id](audioCtx.currentTime, {
              trackIdx, pitch: trackParams[trackIdx].pitch,
              decayMul: trackParams[trackIdx].decay, vel: 0.9,
            });
          }
        }
        refreshStep(trackIdx, stepIdx);
        pushHistory();
      } else {
        // Modalità drag-to-edit
        if (!cell) {
          patterns[currentPattern][trackIdx][stepIdx] = newCell();
        }
        dragStartY = e.clientY;
        const c = patterns[currentPattern][trackIdx][stepIdx];
        dragStartValue = {
          vel: c.vel, prob: c.prob, ratch: c.ratch, nudge: c.nudge
        };
        refreshStep(trackIdx, stepIdx);
      }
    });

    btn.addEventListener('pointermove', (e) => {
      if (dragStartY === null) return;
      const dy = dragStartY - e.clientY; // verso l'alto = positivo
      if (Math.abs(dy) > 3) didDrag = true;
      const cell = patterns[currentPattern][trackIdx][stepIdx];
      if (!cell) return;

      if (editMode === 'vel') {
        cell.vel = clamp(dragStartValue.vel + dy / 120, 0.05, 1);
      } else if (editMode === 'prob') {
        cell.prob = clamp(dragStartValue.prob + dy * 2, 0, 100);
      } else if (editMode === 'ratch') {
        cell.ratch = Math.round(clamp(dragStartValue.ratch + dy / 20, 1, 4));
      } else if (editMode === 'nudge') {
        cell.nudge = clamp(dragStartValue.nudge + dy, -50, 50);
      }
      refreshStep(trackIdx, stepIdx);
      updateStepReadout(trackIdx, stepIdx);
    });

    btn.addEventListener('pointerup', () => {
      if (dragStartY !== null) {
        dragStartY = null;
        dragStartValue = null;
        if (didDrag) pushHistory();
      }
    });

    btn.addEventListener('pointercancel', () => {
      dragStartY = null; dragStartValue = null;
    });
  }

  function newCell() {
    return { vel: 0.9, prob: 100, ratch: 1, nudge: 0 };
  }

  function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

  // ============================================================
  // 12) REFRESH UI
  // ============================================================
  function refreshStep(trackIdx, stepIdx) {
    const btn = stepElements[trackIdx][stepIdx];
    if (!btn) return;
    const cell = patterns[currentPattern][trackIdx][stepIdx];
    btn.classList.toggle('step--active', !!cell);
    btn.classList.toggle('step--prob-partial', !!cell && cell.prob < 100);
    btn.classList.toggle('step--ratch', !!cell && cell.ratch > 1);
    btn.classList.toggle('step--nudged', !!cell && Math.abs(cell.nudge) > 3);

    const bar = btn.querySelector('.step__bar');
    if (cell) {
      bar.style.height = `${cell.vel * 100}%`;
    } else {
      bar.style.height = '0%';
    }

    const ind = btn.querySelector('.step__ind');
    if (cell && cell.ratch > 1) {
      ind.textContent = 'x' + cell.ratch;
    } else if (cell && cell.prob < 100) {
      ind.textContent = cell.prob + '%';
    } else {
      ind.textContent = '';
    }
  }

  function refreshPatternUI() {
    for (let t = 0; t < NUM_TRACKS; t++) {
      for (let s = 0; s < MAX_STEPS; s++) {
        refreshStep(t, s);
      }
    }
  }

  function refreshStepVisibility() {
    document.querySelectorAll('.beat-cell').forEach(el => {
      const s = parseInt(el.dataset.step || el.textContent, 10) - 1;
      // Sulla riga numeri non ha dataset.step
    });
    // Piuttosto mostriamo/nascondiamo via grid-template in CSS variable
    document.documentElement.style.setProperty('--pattern-length', patternLength);
    document.querySelectorAll('.beats').forEach(wrap => {
      [...wrap.children].forEach((el, i) => {
        el.classList.toggle('beat-cell--hidden', i >= patternLength);
      });
    });
  }

  function refreshAllUI() {
    refreshPatternUI();
    refreshStepVisibility();
    document.getElementById('bpmValue').textContent = bpm;
    document.getElementById('bpmSlider').value = bpm;
    document.getElementById('swingValue').textContent = swing + '%';
    document.getElementById('swingSlider').value = swing;
    document.getElementById('lengthSelect').value = patternLength;
    updateTrackControls();
    updatePatternButtons();
    updateActiveTrackPanel();
    renderSongBar();
    updateClipboardUI();
  }

  function updateTransportUI() {
    const btn = document.getElementById('playButton');
    const icon = document.getElementById('playIcon');
    const label = document.getElementById('playLabel');
    if (playing) {
      btn.classList.add('transport--playing');
      icon.textContent = '■';
      label.textContent = 'STOP';
    } else {
      btn.classList.remove('transport--playing');
      icon.textContent = '▶';
      label.textContent = 'PLAY';
    }
  }

  function tickUI() {
    if (!playing) return;
    const now = audioCtx.currentTime;
    while (uiQueue.length && uiQueue[0].time <= now) {
      const ev = uiQueue.shift();
      flashColumn(ev.step);
    }
    requestAnimationFrame(tickUI);
  }

  function flashColumn(step) {
    for (let t = 0; t < NUM_TRACKS; t++) {
      for (let s = 0; s < MAX_STEPS; s++) {
        const el = stepElements[t][s];
        if (!el) continue;
        el.classList.remove('step--current-column');
        el.classList.remove('step--playing');
      }
    }
    for (let t = 0; t < NUM_TRACKS; t++) {
      const el = stepElements[t][step];
      if (!el) continue;
      el.classList.add('step--current-column');
      void el.offsetWidth;
      el.classList.add('step--playing');
    }
  }

  function clearPlayingHighlights() {
    for (let t = 0; t < NUM_TRACKS; t++) {
      for (let s = 0; s < MAX_STEPS; s++) {
        const el = stepElements[t][s];
        if (!el) continue;
        el.classList.remove('step--current-column');
        el.classList.remove('step--playing');
      }
    }
  }

  // ============================================================
  // 13) ACTIVE TRACK PANEL (pitch, decay, volume, filter per traccia)
  // ============================================================
  function setActiveTrack(idx) {
    activeTrack = idx;
    updateActiveTrackPanel();
    // evidenzia la riga
    document.querySelectorAll('.seq__row').forEach(r => {
      r.classList.toggle('seq__row--active', r.dataset.track === String(idx));
    });
  }

  function updateActiveTrackPanel() {
    const i = activeTrack;
    const p = trackParams[i];
    const def = TRACK_DEFS[i];
    document.getElementById('atName').textContent = def.name;
    const dot = document.getElementById('atDot');
    if (dot) dot.style.background = def.color;

    document.getElementById('atVol').value = Math.round(p.volume * 100);
    document.getElementById('atVolV').textContent = Math.round(p.volume * 100);
    document.getElementById('atPitch').value = p.pitch;
    document.getElementById('atPitchV').textContent = (p.pitch >= 0 ? '+' : '') + p.pitch;
    document.getElementById('atDecay').value = Math.round(p.decay * 100);
    document.getElementById('atDecayV').textContent = p.decay.toFixed(2);
    document.getElementById('atFilter').value = p.filterType;
    document.getElementById('atCutoff').value = Math.round(p.filterCutoff * 100);
    document.getElementById('atCutoffV').textContent = Math.round(p.filterCutoff * 100);

    const atPan = document.getElementById('atPan');
    if (atPan) {
      const panVal = Math.round((p.pan || 0) * 100);
      atPan.value = panVal;
      const atPanV = document.getElementById('atPanV');
      if (atPanV) atPanV.textContent = panToLabel(p.pan || 0);
    }

    document.querySelectorAll('.seq__row').forEach(r => {
      r.classList.toggle('seq__row--active', r.dataset.track === String(i));
    });
  }

  function panToLabel(v) {
    if (Math.abs(v) < 0.02) return 'C';
    const pct = Math.round(Math.abs(v) * 100);
    return (v < 0 ? 'L' : 'R') + pct;
  }

  function updateTrackControls() {
    // Aggiorna classi mute/solo
    document.querySelectorAll('.seq__row').forEach(row => {
      const idx = parseInt(row.dataset.track, 10);
      if (isNaN(idx)) return;
      const p = trackParams[idx];
      const mute = row.querySelector('.ts-btn--mute');
      const solo = row.querySelector('.ts-btn--solo');
      if (mute) mute.classList.toggle('ts-btn--on', p.mute);
      if (solo) solo.classList.toggle('ts-btn--on', p.solo);
    });
  }

  // ============================================================
  // 14) STEP READOUT (parametri del "step corrente" per edit mode)
  // ============================================================
  let lastReadoutStep = null;

  function updateStepReadout(trackIdx, stepIdx) {
    const el = document.getElementById('stepReadout');
    if (!el) return;
    const cell = patterns[currentPattern][trackIdx][stepIdx];
    if (!cell) {
      el.textContent = '—';
      return;
    }
    const track = TRACK_DEFS[trackIdx].name;
    const parts = [
      `${track} • step ${stepIdx + 1}`,
      `vel ${Math.round(cell.vel * 100)}%`,
      `prob ${cell.prob}%`,
      `x${cell.ratch}`,
      `nudge ${cell.nudge > 0 ? '+' : ''}${cell.nudge}ms`,
    ];
    el.textContent = parts.join('  ·  ');
  }

  // ============================================================
  // 15) PATTERN A/B/C/D (live switch) + CLEAR / DEMO
  // ============================================================
  function switchPattern(name) {
    if (!patterns[name]) return;
    currentPattern = name;
    refreshPatternUI();
    updatePatternButtons();
    showToast(`Pattern ${name}`);
  }

  function updatePatternButtons() {
    ['A','B','C','D'].forEach(n => {
      const b = document.querySelector(`[data-pattern="${n}"]`);
      if (!b) return;
      b.classList.toggle('pat-btn--active', n === currentPattern);
      b.classList.toggle('pat-btn--has-content', patternHasContent(n));
    });
  }

  function patternHasContent(name) {
    const p = patterns[name];
    if (!p) return false;
    for (let t = 0; t < NUM_TRACKS; t++) {
      for (let s = 0; s < patternLength; s++) {
        if (p[t][s]) return true;
      }
    }
    return false;
  }

  function clearCurrentPattern() {
    patterns[currentPattern] = makeEmptyPattern();
    refreshPatternUI();
    updatePatternButtons();
    pushHistory();
    showToast(`Pattern ${currentPattern} pulito`);
  }

  // ============================================================
  // 15b) COPY / PASTE pattern
  // ============================================================
  function copyPattern() {
    patternClipboard = JSON.parse(JSON.stringify(patterns[currentPattern]));
    showToast(`Pattern ${currentPattern} copiato`);
    updateClipboardUI();
  }

  function pastePattern() {
    if (!patternClipboard) {
      showToast('Clipboard vuota', true);
      return;
    }
    patterns[currentPattern] = JSON.parse(JSON.stringify(patternClipboard));
    refreshPatternUI();
    updatePatternButtons();
    pushHistory();
    showToast(`Incollato in ${currentPattern}`);
  }

  function updateClipboardUI() {
    const pb = document.getElementById('pasteBtn');
    if (pb) pb.classList.toggle('chip--armed', !!patternClipboard);
  }

  // ============================================================
  // 15c) SONG EDITOR (sequence A/B/C/D con click-to-cycle)
  // ============================================================
  const SONG_ORDER = ['A','B','C','D'];

  function renderSongBar() {
    const wrap = document.getElementById('songSlots');
    if (!wrap) return;
    wrap.innerHTML = '';
    songSequence.forEach((name, i) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'song-slot';
      btn.dataset.songIdx = String(i);
      btn.textContent = name;
      btn.classList.toggle('song-slot--current', playing && songMode && i === songStep);
      btn.setAttribute('aria-label', `Slot ${i + 1}: pattern ${name}`);
      btn.addEventListener('click', () => cycleSongSlot(i));
      wrap.appendChild(btn);
    });
    const len = document.getElementById('songLenVal');
    if (len) len.textContent = String(songSequence.length);
  }

  function cycleSongSlot(i) {
    const cur = songSequence[i];
    const idx = SONG_ORDER.indexOf(cur);
    songSequence[i] = SONG_ORDER[(idx + 1) % SONG_ORDER.length];
    renderSongBar();
    pushHistory();
  }

  function songAddSlot() {
    if (songSequence.length >= 16) { showToast('Max 16 slot'); return; }
    songSequence.push(songSequence[songSequence.length - 1] || 'A');
    renderSongBar();
    pushHistory();
  }

  function songRemoveSlot() {
    if (songSequence.length <= 1) { showToast('Minimo 1 slot'); return; }
    songSequence.pop();
    renderSongBar();
    pushHistory();
  }

  function updateSongCurrentSlot() {
    // Aggiorna solo l'evidenziazione (performance-friendly)
    const slots = document.querySelectorAll('.song-slot');
    slots.forEach((el, i) => {
      el.classList.toggle('song-slot--current', playing && songMode && i === songStep);
    });
  }

  function loadDemo() {
    // Demo principale in A: classico four-on-the-floor + hi-hat ottavi + clap
    const demoA = makeEmptyPattern();
    // kick 1,5,9,13
    [0,4,8,12].forEach(s => demoA[0][s] = newCell());
    // snare 5,13
    [4,12].forEach(s => demoA[1][s] = newCell());
    // hi-hat ottavi
    for (let s = 0; s < 16; s += 2) demoA[2][s] = newCell();
    // clap 13
    demoA[4][12] = newCell();
    patterns.A = demoA;

    // B: variazione con open hat
    const demoB = makeEmptyPattern();
    [0,4,8,12].forEach(s => demoB[0][s] = newCell());
    [4,12].forEach(s => demoB[1][s] = newCell());
    for (let s = 0; s < 16; s += 2) demoB[2][s] = newCell();
    [2,6,10,14].forEach(s => demoB[3][s] = newCell());
    patterns.B = demoB;

    currentPattern = 'A';
    refreshPatternUI();
    updatePatternButtons();
    pushHistory();
  }

  // ============================================================
  // 16) STORAGE: slot localStorage (legacy A/B/C/D)
  //     Manteniamo la vecchia API ma ora salviamo l'intero "set"
  //     (tutti e 4 i pattern + trackParams + swing).
  // ============================================================
  const STORAGE_PREFIX = 'drumapp.slot.';
  const SLOTS = ['A','B','C','D'];

  function serializeFull() {
    return {
      version: 2,
      bpm, swing, patternLength, humanize,
      trackParams,
      patterns,
      songSequence,
    };
  }

  function applyFull(data) {
    if (!data) return false;
    if (typeof data.bpm === 'number') bpm = data.bpm;
    if (typeof data.swing === 'number') swing = data.swing;
    if (typeof data.patternLength === 'number') patternLength = data.patternLength;
    if (typeof data.humanize === 'boolean') humanize = data.humanize;
    if (Array.isArray(data.trackParams) && data.trackParams.length === NUM_TRACKS) {
      // Merge con default per backward compatibility (pan è recente)
      trackParams = data.trackParams.map(p => ({
        volume: 0.85, mute: false, solo: false,
        pitch: 0, decay: 1.0,
        filterType: 'off', filterCutoff: 0.7, filterQ: 1.0,
        pan: 0,
        ...p,
      }));
    }
    if (data.patterns && typeof data.patterns === 'object') {
      patterns = data.patterns;
    }
    if (Array.isArray(data.songSequence) && data.songSequence.length > 0) {
      songSequence = data.songSequence;
    }
    refreshAllUI();
    applyTrackParams();
    return true;
  }

  function hasSlot(slot) {
    try { return !!localStorage.getItem(STORAGE_PREFIX + slot); }
    catch (e) { return false; }
  }

  function saveToSlot(slot) {
    try {
      localStorage.setItem(STORAGE_PREFIX + slot, JSON.stringify(serializeFull()));
      updateSlotButtons();
      flashSlot(slot, 'saving');
      showToast(`Set salvato in slot ${slot}`);
    } catch (e) { showToast('Salvataggio fallito', true); }
  }

  function loadFromSlot(slot) {
    let raw; try { raw = localStorage.getItem(STORAGE_PREFIX + slot); } catch(e) { raw = null; }
    if (!raw) { showToast(`Slot ${slot} vuoto — hold per salvare`); return; }
    try {
      const data = JSON.parse(raw);
      if (applyFull(data)) {
        flashSlot(slot, 'loading');
        showToast(`Set caricato da slot ${slot}`);
        pushHistory();
      } else showToast('Slot non valido', true);
    } catch (e) { showToast('Errore slot', true); }
  }

  function updateSlotButtons() {
    SLOTS.forEach(slot => {
      const btn = document.querySelector(`[data-slot="${slot}"]`);
      if (btn) btn.classList.toggle('slot--filled', hasSlot(slot));
    });
  }

  function flashSlot(slot, type) {
    const btn = document.querySelector(`[data-slot="${slot}"]`);
    if (!btn) return;
    const cls = 'slot--' + type;
    btn.classList.remove(cls);
    void btn.offsetWidth;
    btn.classList.add(cls);
    setTimeout(() => btn.classList.remove(cls), 600);
  }

  function attachSlotGestures(btn, slot) {
    let timer = null, fired = false;
    const down = (e) => {
      e.preventDefault(); fired = false;
      btn.classList.add('slot--holding');
      timer = setTimeout(() => {
        fired = true;
        btn.classList.remove('slot--holding');
        saveToSlot(slot);
      }, HOLD_MS);
    };
    const up = () => {
      btn.classList.remove('slot--holding');
      if (timer) { clearTimeout(timer); timer = null; }
      if (!fired) {
        if (hasSlot(slot)) loadFromSlot(slot);
        else saveToSlot(slot);
      }
    };
    const cancel = () => {
      btn.classList.remove('slot--holding');
      if (timer) { clearTimeout(timer); timer = null; }
    };
    btn.addEventListener('pointerdown', down);
    btn.addEventListener('pointerup', up);
    btn.addEventListener('pointerleave', cancel);
    btn.addEventListener('pointercancel', cancel);
  }

  // ============================================================
  // 17) EXPORT / IMPORT JSON
  // ============================================================
  function exportJSON() {
    const data = serializeFull();
    data.exportedAt = new Date().toISOString();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const ts = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    a.download = `drumapp-${ts}.json`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    showToast('Set esportato');
  }

  function importJSONFromFile(file) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        if (applyFull(data)) {
          showToast(`Importato: ${file.name}`);
          pushHistory();
        } else showToast('File non valido', true);
      } catch (err) { showToast('JSON non leggibile', true); }
    };
    reader.onerror = () => showToast('Errore lettura', true);
    reader.readAsText(file);
  }

  // ============================================================
  // 18) SHARE LINK (solo pattern corrente, hex compatto)
  // ============================================================
  function packToHex() {
    const parts = [];
    for (let t = 0; t < NUM_TRACKS; t++) {
      let bits = 0;
      const row = patterns[currentPattern][t];
      for (let s = 0; s < 16; s++) {
        if (row[s]) bits |= (1 << (15 - s));
      }
      parts.push(bits.toString(16).padStart(4, '0'));
    }
    return parts.join('-') + '-' + bpm.toString(16);
  }

  function unpackFromHex(hex) {
    const segs = hex.split('-');
    if (segs.length !== NUM_TRACKS + 1) return false;
    const newBpm = parseInt(segs[NUM_TRACKS], 16);
    if (isNaN(newBpm) || newBpm < 60 || newBpm > 200) return false;

    const newPattern = makeEmptyPattern();
    for (let t = 0; t < NUM_TRACKS; t++) {
      const bits = parseInt(segs[t], 16);
      if (isNaN(bits)) return false;
      for (let s = 0; s < 16; s++) {
        if (bits & (1 << (15 - s))) newPattern[t][s] = newCell();
      }
    }
    bpm = newBpm;
    patterns[currentPattern] = newPattern;
    refreshAllUI();
    return true;
  }

  function shareLink() {
    const hex = packToHex();
    const url = `${location.origin}${location.pathname}#${hex}`;
    history.replaceState(null, '', '#' + hex);
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url)
        .then(() => showToast('Link copiato'))
        .catch(() => fallbackCopy(url));
    } else fallbackCopy(url);
  }

  function fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'absolute'; ta.style.left = '-9999px';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); showToast('Link copiato'); }
    catch (e) { showToast('Copia manuale'); }
    document.body.removeChild(ta);
  }

  function loadFromURLHash() {
    const hash = location.hash.replace(/^#/, '');
    if (!hash) return false;
    if (unpackFromHex(hash)) {
      showToast('Pattern caricato dal link');
      return true;
    }
    return false;
  }

  // ============================================================
  // 19) BOUNCE WAV (OfflineAudioContext - render deterministic)
  //     Opzioni: numero di loop oppure intera song sequence
  // ============================================================

  /**
   * Apre il modal di selezione loops/song.
   */
  function openBounceDialog() {
    unlockAudio();
    const modal = document.getElementById('bounceModal');
    if (!modal) return;
    // Mostra/nascondi opzione song in base a sequence presente
    const songOpt = document.getElementById('bounceSongOpt');
    if (songOpt) {
      songOpt.style.display = (songSequence && songSequence.length > 0) ? '' : 'none';
    }
    // Default: ultima scelta o 2 loops
    updateBounceDuration();
    modal.classList.add('modal--open');
  }

  function closeBounceDialog() {
    const modal = document.getElementById('bounceModal');
    if (modal) modal.classList.remove('modal--open');
  }

  function updateBounceDuration() {
    const choice = document.querySelector('input[name="bloops"]:checked');
    if (!choice) return;
    const secondsPerStep = (60 / bpm) / 4;
    let totalSec = 0;
    if (choice.value === 'song') {
      totalSec = songSequence.length * patternLength * secondsPerStep;
    } else {
      const n = parseInt(choice.value, 10);
      totalSec = n * patternLength * secondsPerStep;
    }
    const el = document.getElementById('bounceDuration');
    if (el) el.textContent = totalSec.toFixed(1) + 's';
  }

  async function doBounce() {
    const choice = document.querySelector('input[name="bloops"]:checked');
    if (!choice) return;

    // Costruisci la sequenza di pattern da renderizzare
    let sequence;
    if (choice.value === 'song') {
      sequence = songSequence.slice();
    } else {
      const n = parseInt(choice.value, 10);
      sequence = new Array(n).fill(currentPattern);
    }

    closeBounceDialog();
    showToast('Bounce in corso…');

    try {
      const secondsPerStep = (60 / bpm) / 4;
      const totalSteps = sequence.length * patternLength;
      const totalSec = totalSteps * secondsPerStep + 0.6; // tail
      const sr = 44100;
      const OfflineCtx = window.OfflineAudioContext || window.webkitOfflineAudioContext;
      const ctx = new OfflineCtx(2, Math.ceil(sr * totalSec), sr);

      const master = ctx.createGain();
      master.gain.value = 0.75;
      master.connect(ctx.destination);

      const len = sr;
      const noise = ctx.createBuffer(1, len, sr);
      const nd = noise.getChannelData(0);
      for (let i = 0; i < len; i++) nd[i] = Math.random() * 2 - 1;

      const oFilters = [];
      const oPanners = [];
      for (let i = 0; i < NUM_TRACKS; i++) {
        const f = ctx.createBiquadFilter();
        const p = trackParams[i];
        if (p.filterType === 'off') { f.type = 'lowpass'; f.frequency.value = 20000; f.Q.value = 0.707; }
        else { f.type = p.filterType; f.frequency.value = 50 * Math.pow(360, p.filterCutoff); f.Q.value = p.filterQ; }

        const g = ctx.createGain();
        const anySolo = trackParams.some(pp => pp.solo);
        g.gain.value = p.mute ? 0 : (anySolo && !p.solo ? 0 : p.volume);

        const pan = ctx.createStereoPanner ? ctx.createStereoPanner() : null;
        if (pan) {
          pan.pan.value = p.pan || 0;
          pan.connect(f).connect(g).connect(master);
        } else {
          f.connect(g).connect(master);
        }
        oFilters.push(f);
        oPanners.push(pan);
      }

      const ofVoices = buildOfflineVoices(ctx, noise, oPanners.map((p, i) => p || oFilters[i]));

      // Schedula ogni pattern della sequenza, uno dopo l'altro
      sequence.forEach((patName, idxInSeq) => {
        const pat = patterns[patName];
        if (!pat) return;
        const seqOffset = idxInSeq * patternLength * secondsPerStep;

        for (let s = 0; s < patternLength; s++) {
          const baseTime = seqOffset + s * secondsPerStep + stepTimeOffset(s, secondsPerStep);
          for (let t = 0; t < NUM_TRACKS; t++) {
            const cell = pat[t][s];
            if (!cell) continue;
            if (cell.prob < 100 && Math.random() * 100 >= cell.prob) continue;
            const tp = trackParams[t];
            const ratch = cell.ratch || 1;
            const ratchGap = (secondsPerStep * 0.9) / ratch;
            const nudgeSec = (cell.nudge || 0) / 1000;
            for (let r = 0; r < ratch; r++) {
              const tt = baseTime + nudgeSec + r * ratchGap;
              if (tt < 0) continue;
              ofVoices[TRACK_DEFS[t].id](tt, {
                trackIdx: t,
                pitch: tp.pitch,
                decayMul: tp.decay,
                vel: cell.vel * (r === 0 ? 1 : 0.7),
              });
            }
          }
        }
      });

      const buffer = await ctx.startRendering();
      const wav = bufferToWav(buffer);
      const blob = new Blob([wav], { type: 'audio/wav' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const ts = new Date().toISOString().replace(/[:.]/g,'-').slice(0,19);
      const tag = choice.value === 'song' ? 'song' : `${choice.value}loops`;
      a.download = `drumapp-bounce-${tag}-${ts}.wav`;
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      setTimeout(() => URL.revokeObjectURL(url), 2000);
      showToast('Bounce pronto');
    } catch (e) {
      console.error(e);
      showToast('Errore bounce', true);
    }
  }

  /** Costruisce voci identiche per un OfflineAudioContext */
  function buildOfflineVoices(ctx, noise, filters) {
    const out = i => filters[i];
    const semi = s => Math.pow(2, s / 12);
    return {
      kick: (time, p) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type = 'sine';
        o.frequency.setValueAtTime(165 * semi(p.pitch), time);
        o.frequency.exponentialRampToValueAtTime(45 * semi(p.pitch), time + 0.12 * p.decayMul);
        g.gain.setValueAtTime(p.vel, time);
        g.gain.exponentialRampToValueAtTime(0.001, time + 0.45 * p.decayMul);
        o.connect(g).connect(out(p.trackIdx));
        o.start(time); o.stop(time + 0.5 * p.decayMul + 0.02);
        const c = ctx.createOscillator(), cg = ctx.createGain();
        c.type='sine'; c.frequency.setValueAtTime(1200*semi(p.pitch),time);
        cg.gain.setValueAtTime(0.35*p.vel,time);
        cg.gain.exponentialRampToValueAtTime(0.001,time+0.025);
        c.connect(cg).connect(out(p.trackIdx));
        c.start(time); c.stop(time+0.05);
      },
      snare: (time, p) => {
        const o = ctx.createOscillator(), og = ctx.createGain();
        o.type='triangle'; o.frequency.setValueAtTime(220*semi(p.pitch),time);
        og.gain.setValueAtTime(0.5*p.vel,time);
        og.gain.exponentialRampToValueAtTime(0.001,time+0.11*p.decayMul);
        o.connect(og).connect(out(p.trackIdx));
        o.start(time); o.stop(time+0.2*p.decayMul);
        const n = ctx.createBufferSource(); n.buffer = noise;
        const hp = ctx.createBiquadFilter(); hp.type='highpass'; hp.frequency.value=1000;
        const ng = ctx.createGain();
        ng.gain.setValueAtTime(0.7*p.vel,time);
        ng.gain.exponentialRampToValueAtTime(0.001,time+0.17*p.decayMul);
        n.connect(hp).connect(ng).connect(out(p.trackIdx));
        n.start(time); n.stop(time+0.22*p.decayMul);
      },
      hihat: (time, p) => {
        const n = ctx.createBufferSource(); n.buffer = noise;
        const hp = ctx.createBiquadFilter(); hp.type='highpass';
        hp.frequency.value=7000*semi(p.pitch*0.5);
        const g = ctx.createGain();
        g.gain.setValueAtTime(0.45*p.vel,time);
        g.gain.exponentialRampToValueAtTime(0.001,time+0.055*p.decayMul);
        n.connect(hp).connect(g).connect(out(p.trackIdx));
        n.start(time); n.stop(time+0.1*p.decayMul);
      },
      openhat: (time, p) => {
        const n = ctx.createBufferSource(); n.buffer = noise;
        const hp = ctx.createBiquadFilter(); hp.type='highpass';
        hp.frequency.value=6500*semi(p.pitch*0.5);
        const g = ctx.createGain();
        g.gain.setValueAtTime(0.0001,time);
        g.gain.linearRampToValueAtTime(0.4*p.vel,time+0.003);
        g.gain.exponentialRampToValueAtTime(0.001,time+0.45*p.decayMul);
        n.connect(hp).connect(g).connect(out(p.trackIdx));
        n.start(time); n.stop(time+0.5*p.decayMul);
      },
      clap: (time, p) => {
        const n = ctx.createBufferSource(); n.buffer = noise;
        const bp = ctx.createBiquadFilter(); bp.type='bandpass';
        bp.frequency.value=1500*semi(p.pitch); bp.Q.value=0.9;
        const g = ctx.createGain();
        g.gain.setValueAtTime(0.0001,time);
        g.gain.linearRampToValueAtTime(0.85*p.vel,time+0.002);
        g.gain.exponentialRampToValueAtTime(0.15,time+0.013);
        g.gain.linearRampToValueAtTime(0.85*p.vel,time+0.016);
        g.gain.exponentialRampToValueAtTime(0.15,time+0.027);
        g.gain.linearRampToValueAtTime(0.85*p.vel,time+0.030);
        g.gain.exponentialRampToValueAtTime(0.001,time+0.32*p.decayMul);
        n.connect(bp).connect(g).connect(out(p.trackIdx));
        n.start(time); n.stop(time+0.35*p.decayMul);
      },
      tom: (time, p) => {
        const o = ctx.createOscillator(), g = ctx.createGain();
        o.type='sine'; o.frequency.setValueAtTime(180*semi(p.pitch),time);
        o.frequency.exponentialRampToValueAtTime(90*semi(p.pitch),time+0.15*p.decayMul);
        g.gain.setValueAtTime(0.8*p.vel,time);
        g.gain.exponentialRampToValueAtTime(0.001,time+0.6*p.decayMul);
        o.connect(g).connect(out(p.trackIdx));
        o.start(time); o.stop(time+0.65*p.decayMul);
      },
      rim: (time, p) => {
        const o1=ctx.createOscillator(),o2=ctx.createOscillator(),g=ctx.createGain();
        o1.type='square'; o2.type='triangle';
        o1.frequency.setValueAtTime(800*semi(p.pitch),time);
        o2.frequency.setValueAtTime(380*semi(p.pitch),time);
        g.gain.setValueAtTime(0.5*p.vel,time);
        g.gain.exponentialRampToValueAtTime(0.001,time+0.05*p.decayMul);
        const bp=ctx.createBiquadFilter(); bp.type='bandpass';
        bp.frequency.value=1800*semi(p.pitch); bp.Q.value=3;
        o1.connect(bp); o2.connect(bp);
        bp.connect(g).connect(out(p.trackIdx));
        o1.start(time); o2.start(time);
        o1.stop(time+0.08); o2.stop(time+0.08);
      },
      cow: (time, p) => {
        const o1=ctx.createOscillator(),o2=ctx.createOscillator();
        o1.type='square'; o2.type='square';
        o1.frequency.setValueAtTime(540*semi(p.pitch),time);
        o2.frequency.setValueAtTime(800*semi(p.pitch),time);
        const mix=ctx.createGain(); mix.gain.value=0.5;
        const bp=ctx.createBiquadFilter(); bp.type='bandpass';
        bp.frequency.value=2000*semi(p.pitch); bp.Q.value=1.5;
        const env=ctx.createGain();
        env.gain.setValueAtTime(0.0001,time);
        env.gain.linearRampToValueAtTime(0.35*p.vel,time+0.004);
        env.gain.exponentialRampToValueAtTime(0.001,time+0.3*p.decayMul);
        o1.connect(mix); o2.connect(mix);
        mix.connect(bp).connect(env).connect(out(p.trackIdx));
        o1.start(time); o2.start(time);
        o1.stop(time+0.35*p.decayMul); o2.stop(time+0.35*p.decayMul);
      },
    };
  }

  /** AudioBuffer -> WAV 16-bit PCM */
  function bufferToWav(buffer) {
    const nCh = buffer.numberOfChannels;
    const sr = buffer.sampleRate;
    const nFrames = buffer.length;
    const blockAlign = nCh * 2;
    const dataSize = nFrames * blockAlign;
    const ab = new ArrayBuffer(44 + dataSize);
    const dv = new DataView(ab);
    let o = 0;
    const wStr = s => { for (let i=0;i<s.length;i++) dv.setUint8(o++, s.charCodeAt(i)); };
    wStr('RIFF');
    dv.setUint32(o, 36 + dataSize, true); o += 4;
    wStr('WAVE');
    wStr('fmt ');
    dv.setUint32(o, 16, true); o += 4;
    dv.setUint16(o, 1, true); o += 2;           // PCM
    dv.setUint16(o, nCh, true); o += 2;
    dv.setUint32(o, sr, true); o += 4;
    dv.setUint32(o, sr * blockAlign, true); o += 4;
    dv.setUint16(o, blockAlign, true); o += 2;
    dv.setUint16(o, 16, true); o += 2;
    wStr('data');
    dv.setUint32(o, dataSize, true); o += 4;

    const channels = [];
    for (let c = 0; c < nCh; c++) channels.push(buffer.getChannelData(c));
    for (let i = 0; i < nFrames; i++) {
      for (let c = 0; c < nCh; c++) {
        let s = Math.max(-1, Math.min(1, channels[c][i]));
        dv.setInt16(o, s < 0 ? s * 0x8000 : s * 0x7fff, true);
        o += 2;
      }
    }
    return ab;
  }

  // ============================================================
  // 20) WEB MIDI
  // ============================================================
  // Mapping General MIDI standard drum notes
  const MIDI_NOTES = {
    kick: 36, snare: 38, hihat: 42, openhat: 46,
    clap: 39, tom: 45, rim: 37, cow: 56,
  };

  async function initMIDI() {
    if (!navigator.requestMIDIAccess) {
      showToast('Web MIDI non supportato', true);
      return;
    }
    try {
      midiAccess = await navigator.requestMIDIAccess();
      // prima uscita disponibile
      const outs = [...midiAccess.outputs.values()];
      if (outs.length === 0) {
        showToast('Nessuna porta MIDI trovata', true);
        document.getElementById('midiBtn').classList.remove('chip--on');
        return;
      }
      midiOut = outs[0];
      document.getElementById('midiBtn').classList.add('chip--on');
      document.getElementById('midiBtn').textContent = 'MIDI: ' + midiOut.name.slice(0, 14);
      showToast('MIDI: ' + midiOut.name);
    } catch (e) {
      showToast('Accesso MIDI negato', true);
    }
  }

  function sendMidiForTrack(trackIdx, vel, time) {
    if (!midiOut) return;
    const note = MIDI_NOTES[TRACK_DEFS[trackIdx].id];
    if (!note) return;
    const v = Math.round(vel * 127);
    const delayMs = Math.max(0, (time - audioCtx.currentTime) * 1000);
    try {
      midiOut.send([0x99, note, v], performance.now() + delayMs);
      midiOut.send([0x89, note, 0], performance.now() + delayMs + 80);
    } catch (e) { /* ignore */ }
  }

  // ============================================================
  // 20b) REC LIVE (MediaRecorder -> cattura tutto cio' che suona)
  // ============================================================

  /** Cerca il miglior MIME type supportato dal browser */
  function getRecMime() {
    if (!window.MediaRecorder) return null;
    const candidates = [
      'audio/webm;codecs=opus',
      'audio/webm',
      'audio/mp4',
      'audio/ogg;codecs=opus',
    ];
    for (const t of candidates) {
      try { if (MediaRecorder.isTypeSupported(t)) return t; }
      catch (e) { /* ignore */ }
    }
    return '';
  }

  function recExtension(mime) {
    if (!mime) return 'webm';
    if (mime.includes('webm')) return 'webm';
    if (mime.includes('ogg'))  return 'ogg';
    if (mime.includes('mp4'))  return 'm4a';
    return 'webm';
  }

  function toggleRec() {
    unlockAudio();
    if (!window.MediaRecorder) {
      showToast('MediaRecorder non supportato qui', true);
      return;
    }
    if (!mediaRecDest) {
      showToast('Destination audio non disponibile', true);
      return;
    }
    if (isRecording) stopRec();
    else startRec();
  }

  function startRec() {
    try {
      const mime = getRecMime();
      const opts = mime ? { mimeType: mime } : {};
      mediaRecorder = new MediaRecorder(mediaRecDest.stream, opts);
      recChunks = [];
      mediaRecorder.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) recChunks.push(e.data);
      };
      mediaRecorder.onstop = () => finalizeRec(mime);
      mediaRecorder.onerror = (e) => {
        console.error('MediaRecorder error:', e);
        showToast('Errore REC', true);
        isRecording = false; updateRecButton();
      };
      mediaRecorder.start(200);
      isRecording = true;
      recStartTime = performance.now();
      updateRecButton();
      showToast('REC avviato — premi di nuovo per fermare');
      // Timer visivo per il tempo di registrazione
      tickRecTimer();
    } catch (e) {
      console.error(e);
      showToast('REC fallita: ' + e.message, true);
      isRecording = false; updateRecButton();
    }
  }

  function stopRec() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      try { mediaRecorder.stop(); } catch (e) { /* ignore */ }
    }
    isRecording = false;
    if (recTimerHandle) { clearInterval(recTimerHandle); recTimerHandle = null; }
    updateRecButton();
  }

  function finalizeRec(mime) {
    const blob = new Blob(recChunks, { type: mime || 'audio/webm' });
    const ext = recExtension(mime);
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    const ts = new Date().toISOString().replace(/[:.]/g,'-').slice(0,19);
    a.download = `drumapp-live-${ts}.${ext}`;
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(() => URL.revokeObjectURL(url), 2000);
    showToast(`REC salvato (${(blob.size / 1024).toFixed(0)} kB)`);
    recChunks = [];
  }

  function tickRecTimer() {
    if (recTimerHandle) clearInterval(recTimerHandle);
    const btn = document.getElementById('recBtn');
    if (!btn) return;
    recTimerHandle = setInterval(() => {
      if (!isRecording) { clearInterval(recTimerHandle); recTimerHandle = null; return; }
      const sec = (performance.now() - recStartTime) / 1000;
      const m = Math.floor(sec / 60);
      const s = Math.floor(sec % 60);
      btn.textContent = `REC ${m}:${String(s).padStart(2,'0')}`;
    }, 250);
  }

  function updateRecButton() {
    const btn = document.getElementById('recBtn');
    if (!btn) return;
    btn.classList.toggle('chip--rec', isRecording);
    btn.classList.toggle('chip--on', isRecording);
    if (!isRecording) btn.textContent = 'REC';
  }

  // ============================================================
  // 21) TAP TEMPO
  // ============================================================
  function tapTempo() {
    const now = performance.now();
    tapTimes.push(now);
    if (tapTimes.length > 4) tapTimes.shift();
    // Scarta le tap piu' vecchie di 3 secondi
    tapTimes = tapTimes.filter(t => now - t < 3000);

    if (tapTimes.length >= 2) {
      const deltas = [];
      for (let i = 1; i < tapTimes.length; i++) deltas.push(tapTimes[i] - tapTimes[i-1]);
      const avg = deltas.reduce((a,b)=>a+b, 0) / deltas.length;
      const newBpm = Math.round(60000 / avg);
      if (newBpm >= 60 && newBpm <= 200) {
        bpm = newBpm;
        document.getElementById('bpmValue').textContent = bpm;
        document.getElementById('bpmSlider').value = bpm;
      }
    }
    // Piccolo flash visivo
    const el = document.getElementById('tapBtn');
    if (el) { el.classList.add('tap--flash'); setTimeout(() => el.classList.remove('tap--flash'), 120); }
  }

  // ============================================================
  // 22) TOAST
  // ============================================================
  let toastTimer = null;
  function showToast(msg, isError = false) {
    const el = document.getElementById('toast');
    if (!el) return;
    el.textContent = msg;
    el.classList.toggle('toast--error', !!isError);
    el.classList.add('toast--show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove('toast--show'), 2000);
  }

  // ============================================================
  // 23) BOOTSTRAP
  // ============================================================
  document.addEventListener('DOMContentLoaded', () => {
    buildSequencer();

    // Stato iniziale: demo o URL hash
    if (!loadFromURLHash()) {
      loadDemo();
    }
    refreshAllUI();
    pushHistory(); // stato iniziale nella cronologia

    // --- Transport ---
    document.getElementById('playButton').addEventListener('click', toggleTransport);
    document.getElementById('tapBtn').addEventListener('click', () => { unlockAudio(); tapTempo(); });

    // --- BPM ---
    const bpmSlider = document.getElementById('bpmSlider');
    bpmSlider.addEventListener('input', e => {
      bpm = parseInt(e.target.value, 10);
      document.getElementById('bpmValue').textContent = bpm;
    });

    // --- Swing ---
    const swingSlider = document.getElementById('swingSlider');
    swingSlider.addEventListener('input', e => {
      swing = parseInt(e.target.value, 10);
      document.getElementById('swingValue').textContent = swing + '%';
    });

    // --- Pattern length ---
    document.getElementById('lengthSelect').addEventListener('change', e => {
      patternLength = parseInt(e.target.value, 10);
      refreshStepVisibility();
      pushHistory();
    });

    // --- Checkbox globali ---
    document.getElementById('humanizeChk').addEventListener('change', e => { humanize = e.target.checked; });
    document.getElementById('metroChk').addEventListener('change', e => { metronome = e.target.checked; });

    // --- Active track panel ---
    document.getElementById('atVol').addEventListener('input', e => {
      trackParams[activeTrack].volume = parseInt(e.target.value,10) / 100;
      document.getElementById('atVolV').textContent = e.target.value;
      applyTrackParams();
    });
    document.getElementById('atPitch').addEventListener('input', e => {
      const v = parseInt(e.target.value, 10);
      trackParams[activeTrack].pitch = v;
      document.getElementById('atPitchV').textContent = (v >= 0 ? '+' : '') + v;
    });
    document.getElementById('atDecay').addEventListener('input', e => {
      const v = parseInt(e.target.value,10) / 100;
      trackParams[activeTrack].decay = v;
      document.getElementById('atDecayV').textContent = v.toFixed(2);
    });
    document.getElementById('atFilter').addEventListener('change', e => {
      trackParams[activeTrack].filterType = e.target.value;
      applyTrackParams();
    });
    document.getElementById('atCutoff').addEventListener('input', e => {
      trackParams[activeTrack].filterCutoff = parseInt(e.target.value,10) / 100;
      document.getElementById('atCutoffV').textContent = e.target.value;
      applyTrackParams();
    });

    const atPanEl = document.getElementById('atPan');
    if (atPanEl) {
      atPanEl.addEventListener('input', e => {
        const v = parseInt(e.target.value, 10) / 100;
        trackParams[activeTrack].pan = v;
        const lbl = document.getElementById('atPanV');
        if (lbl) lbl.textContent = panToLabel(v);
        applyTrackParams();
      });
      atPanEl.addEventListener('change', pushHistory);
      // Double-click to reset to center
      atPanEl.addEventListener('dblclick', () => {
        trackParams[activeTrack].pan = 0;
        atPanEl.value = 0;
        document.getElementById('atPanV').textContent = 'C';
        applyTrackParams();
        pushHistory();
      });
    }

    // Snapshot su "change" finale (non su input per evitare history gigante)
    ['atVol','atPitch','atDecay','atCutoff'].forEach(id => {
      document.getElementById(id).addEventListener('change', pushHistory);
    });
    document.getElementById('atFilter').addEventListener('change', pushHistory);

    // --- Copy / Paste pattern ---
    const copyBtn = document.getElementById('copyBtn');
    const pasteBtn = document.getElementById('pasteBtn');
    if (copyBtn) copyBtn.addEventListener('click', copyPattern);
    if (pasteBtn) pasteBtn.addEventListener('click', pastePattern);

    // --- Song editor ---
    const songAddBtn = document.getElementById('songAddBtn');
    const songRemoveBtn = document.getElementById('songRemoveBtn');
    if (songAddBtn) songAddBtn.addEventListener('click', songAddSlot);
    if (songRemoveBtn) songRemoveBtn.addEventListener('click', songRemoveSlot);

    // --- Edit mode ---
    document.querySelectorAll('[data-edit-mode]').forEach(btn => {
      btn.addEventListener('click', () => {
        editMode = btn.dataset.editMode;
        document.querySelectorAll('[data-edit-mode]').forEach(b => b.classList.toggle('mode-btn--on', b === btn));
      });
    });

    // --- Pattern A/B/C/D (live switch) ---
    ['A','B','C','D'].forEach(n => {
      const btn = document.querySelector(`[data-pattern="${n}"]`);
      if (btn) btn.addEventListener('click', () => switchPattern(n));
    });

    // --- Slot A/B/C/D (localStorage) ---
    SLOTS.forEach(slot => {
      const btn = document.querySelector(`[data-slot="${slot}"]`);
      if (btn) attachSlotGestures(btn, slot);
    });
    updateSlotButtons();

    // --- Demo / Clear ---
    document.getElementById('demoBtn').addEventListener('click', () => { loadDemo(); pushHistory(); });
    document.getElementById('clearBtn').addEventListener('click', clearCurrentPattern);

    // --- File ---
    document.getElementById('exportBtn').addEventListener('click', exportJSON);
    const importBtn = document.getElementById('importBtn');
    const importFile = document.getElementById('importFile');
    importBtn.addEventListener('click', () => importFile.click());
    importFile.addEventListener('change', (e) => {
      const f = e.target.files && e.target.files[0];
      if (f) importJSONFromFile(f);
      importFile.value = '';
    });

    // --- Share / Bounce / REC / MIDI ---
    document.getElementById('shareBtn').addEventListener('click', shareLink);
    document.getElementById('wavBtn').addEventListener('click', openBounceDialog);
    document.getElementById('recBtn').addEventListener('click', toggleRec);
    document.getElementById('midiBtn').addEventListener('click', initMIDI);

    // --- Bounce modal handlers ---
    document.querySelectorAll('input[name="bloops"]').forEach(r => {
      r.addEventListener('change', updateBounceDuration);
    });
    const bConfirm = document.getElementById('bounceConfirm');
    if (bConfirm) bConfirm.addEventListener('click', doBounce);
    const bCancel = document.getElementById('bounceCancel');
    if (bCancel) bCancel.addEventListener('click', closeBounceDialog);
    const bBackdrop = document.getElementById('bounceBackdrop');
    if (bBackdrop) bBackdrop.addEventListener('click', closeBounceDialog);

    // --- Undo / Redo ---
    document.getElementById('undoBtn').addEventListener('click', undo);
    document.getElementById('redoBtn').addEventListener('click', redo);

    // --- Song mode ---
    document.getElementById('songChk').addEventListener('change', e => { songMode = e.target.checked; });

    // --- Keyboard ---
    document.addEventListener('keydown', e => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLSelectElement) return;
      if (e.code === 'Space') { e.preventDefault(); toggleTransport(); return; }
      if ((e.metaKey || e.ctrlKey) && e.key === 'z' && !e.shiftKey) { e.preventDefault(); undo(); return; }
      if ((e.metaKey || e.ctrlKey) && (e.key === 'Z' || (e.shiftKey && e.key === 'z'))) { e.preventDefault(); redo(); return; }
      if (e.key === 't' || e.key === 'T') { unlockAudio(); tapTempo(); return; }
      if (e.key === 'c' || e.key === 'C') { clearCurrentPattern(); return; }
      if (e.key === 'd' || e.key === 'D') { loadDemo(); pushHistory(); return; }
      if (e.key === 'm' || e.key === 'M') {
        trackParams[activeTrack].mute = !trackParams[activeTrack].mute;
        applyTrackParams(); updateTrackControls();
        showToast(`${TRACK_DEFS[activeTrack].name} ${trackParams[activeTrack].mute ? 'muted' : 'unmuted'}`);
        return;
      }
      if (e.key === 's' || e.key === 'S') {
        trackParams[activeTrack].solo = !trackParams[activeTrack].solo;
        applyTrackParams(); updateTrackControls();
        showToast(`${TRACK_DEFS[activeTrack].name} solo ${trackParams[activeTrack].solo ? 'on' : 'off'}`);
        return;
      }
      if (e.key === '[') {
        const i = SONG_ORDER.indexOf(currentPattern);
        switchPattern(SONG_ORDER[(i - 1 + 4) % 4]);
        return;
      }
      if (e.key === ']') {
        const i = SONG_ORDER.indexOf(currentPattern);
        switchPattern(SONG_ORDER[(i + 1) % 4]);
        return;
      }
      if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
        e.preventDefault();
        const dir = e.key === 'ArrowUp' ? -1 : 1;
        const newT = (activeTrack + dir + NUM_TRACKS) % NUM_TRACKS;
        setActiveTrack(newT);
        return;
      }
      if (e.key >= '1' && e.key <= '4') {
        const idx = parseInt(e.key, 10) - 1;
        switchPattern(['A','B','C','D'][idx]);
      }
    });

    // Unlock audio al primo tap
    const firstTouch = () => {
      unlockAudio();
      window.removeEventListener('touchstart', firstTouch);
      window.removeEventListener('mousedown', firstTouch);
    };
    window.addEventListener('touchstart', firstTouch, { once: true, passive: true });
    window.addEventListener('mousedown', firstTouch, { once: true });

    // Active track iniziale
    setActiveTrack(0);
  });

})();

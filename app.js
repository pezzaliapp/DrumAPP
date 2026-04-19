/* ==============================================================
   DrumAPP · app.js
   Sintesi audio via Web Audio API + sequencer a 16 step
   Commenti in italiano, nessuna dipendenza esterna.
   ============================================================== */

(() => {
  'use strict';

  // ============================================================
  // 1) CONFIGURAZIONE
  // ============================================================
  const NUM_STEPS = 16;

  // Ogni "traccia" definisce il suo nome visibile, la variabile CSS
  // che contiene il suo colore e la funzione di sintesi.
  const TRACKS = [
    { id: 'kick',  name: 'KICK',   color: 'var(--track-kick)',  play: playKick  },
    { id: 'snare', name: 'SNARE',  color: 'var(--track-snare)', play: playSnare },
    { id: 'hihat', name: 'HI-HAT', color: 'var(--track-hihat)', play: playHihat },
    { id: 'clap',  name: 'CLAP',   color: 'var(--track-clap)',  play: playClap  },
  ];

  // Pattern: matrice [traccia][step] di booleani
  let pattern = TRACKS.map(() => new Array(NUM_STEPS).fill(false));

  // Stato del sequencer
  let bpm = 120;
  let playing = false;
  let currentStep = 0;

  // Web Audio
  let audioCtx = null;
  let masterGain = null;
  let noiseBuffer = null;

  // Scheduler "lookahead" (pattern di Chris Wilson):
  // ogni 25ms controlliamo cosa va schedulato nei prossimi 100ms di clock audio.
  const LOOKAHEAD_MS = 25;
  const SCHEDULE_AHEAD = 0.1; // secondi
  let nextStepTime = 0;
  let schedulerTimer = null;

  // Coda di eventi UI sincronizzati con l'audio clock
  let uiQueue = [];

  // Cache dei riferimenti alle celle per aggiornamenti rapidi
  let stepElements = [];

  // ============================================================
  // 2) INIT AUDIO
  // ============================================================
  function initAudio() {
    if (audioCtx) return;
    const Ctx = window.AudioContext || window.webkitAudioContext;
    audioCtx = new Ctx();
    masterGain = audioCtx.createGain();
    masterGain.gain.value = 0.75;
    masterGain.connect(audioCtx.destination);

    // Pre-genera 1 secondo di rumore bianco, riutilizzato da snare/hihat/clap
    const len = audioCtx.sampleRate;
    noiseBuffer = audioCtx.createBuffer(1, len, audioCtx.sampleRate);
    const data = noiseBuffer.getChannelData(0);
    for (let i = 0; i < len; i++) data[i] = Math.random() * 2 - 1;
  }

  function unlockAudio() {
    // Su iOS/Safari l'AudioContext parte sospeso: lo riattiviamo al primo tap
    initAudio();
    if (audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  // ============================================================
  // 3) SINTESI SONORA
  // ============================================================

  /** KICK: sinusoide con pitch che crolla da 165Hz a 45Hz + click iniziale */
  function playKick(time) {
    // Corpo
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.type = 'sine';
    osc.frequency.setValueAtTime(165, time);
    osc.frequency.exponentialRampToValueAtTime(45, time + 0.12);
    gain.gain.setValueAtTime(1.0, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.45);
    osc.connect(gain).connect(masterGain);
    osc.start(time);
    osc.stop(time + 0.5);

    // Click di attacco
    const click = audioCtx.createOscillator();
    const cGain = audioCtx.createGain();
    click.type = 'sine';
    click.frequency.setValueAtTime(1200, time);
    cGain.gain.setValueAtTime(0.35, time);
    cGain.gain.exponentialRampToValueAtTime(0.001, time + 0.025);
    click.connect(cGain).connect(masterGain);
    click.start(time);
    click.stop(time + 0.05);
  }

  /** SNARE: componente tonale (220Hz triangolo) + rumore bianco filtrato passa-alto */
  function playSnare(time) {
    // Tono (pelle del rullante)
    const osc = audioCtx.createOscillator();
    const oGain = audioCtx.createGain();
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(220, time);
    oGain.gain.setValueAtTime(0.5, time);
    oGain.gain.exponentialRampToValueAtTime(0.001, time + 0.11);
    osc.connect(oGain).connect(masterGain);
    osc.start(time);
    osc.stop(time + 0.2);

    // Rumore (cordiera)
    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    const hp = audioCtx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.value = 1000;
    const nGain = audioCtx.createGain();
    nGain.gain.setValueAtTime(0.7, time);
    nGain.gain.exponentialRampToValueAtTime(0.001, time + 0.17);
    noise.connect(hp).connect(nGain).connect(masterGain);
    noise.start(time);
    noise.stop(time + 0.22);
  }

  /** HI-HAT: rumore passa-alto a 7kHz con decadimento velocissimo */
  function playHihat(time) {
    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    const hp = audioCtx.createBiquadFilter();
    hp.type = 'highpass';
    hp.frequency.value = 7000;
    const gain = audioCtx.createGain();
    gain.gain.setValueAtTime(0.45, time);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.055);
    noise.connect(hp).connect(gain).connect(masterGain);
    noise.start(time);
    noise.stop(time + 0.1);
  }

  /** CLAP: rumore passa-banda con inviluppo multi-burst (3 impulsi ravvicinati) */
  function playClap(time) {
    const noise = audioCtx.createBufferSource();
    noise.buffer = noiseBuffer;
    const bp = audioCtx.createBiquadFilter();
    bp.type = 'bandpass';
    bp.frequency.value = 1500;
    bp.Q.value = 0.9;
    const gain = audioCtx.createGain();

    // Inviluppo a tre "botte" consecutive + coda
    gain.gain.setValueAtTime(0.0001, time);
    gain.gain.linearRampToValueAtTime(0.85, time + 0.002);
    gain.gain.exponentialRampToValueAtTime(0.15, time + 0.013);
    gain.gain.linearRampToValueAtTime(0.85, time + 0.016);
    gain.gain.exponentialRampToValueAtTime(0.15, time + 0.027);
    gain.gain.linearRampToValueAtTime(0.85, time + 0.030);
    gain.gain.exponentialRampToValueAtTime(0.001, time + 0.32);

    noise.connect(bp).connect(gain).connect(masterGain);
    noise.start(time);
    noise.stop(time + 0.35);
  }

  // ============================================================
  // 4) SCHEDULER (lookahead)
  // ============================================================
  function scheduleStep(step, time) {
    for (let t = 0; t < TRACKS.length; t++) {
      if (pattern[t][step]) {
        TRACKS[t].play(time);
      }
    }
    uiQueue.push({ step, time });
  }

  function advance() {
    const secondsPerBeat = 60.0 / bpm;
    // Ogni step = 1/16 = 1/4 di quarto
    nextStepTime += 0.25 * secondsPerBeat;
    currentStep = (currentStep + 1) % NUM_STEPS;
  }

  function scheduler() {
    while (nextStepTime < audioCtx.currentTime + SCHEDULE_AHEAD) {
      scheduleStep(currentStep, nextStepTime);
      advance();
    }
  }

  // ============================================================
  // 5) CONTROLLI PLAY/STOP
  // ============================================================
  function start() {
    unlockAudio();
    playing = true;
    currentStep = 0;
    nextStepTime = audioCtx.currentTime + 0.08;
    uiQueue = [];
    schedulerTimer = setInterval(scheduler, LOOKAHEAD_MS);
    updateTransportUI();
    requestAnimationFrame(tickUI);
  }

  function stop() {
    playing = false;
    if (schedulerTimer) {
      clearInterval(schedulerTimer);
      schedulerTimer = null;
    }
    uiQueue = [];
    clearPlayingHighlights();
    updateTransportUI();
  }

  function toggleTransport() {
    playing ? stop() : start();
  }

  // ============================================================
  // 6) UI (costruzione, aggiornamento, input)
  // ============================================================
  function buildSequencer() {
    const root = document.getElementById('sequencer');
    root.innerHTML = '';
    stepElements = TRACKS.map(() => new Array(NUM_STEPS));

    // --- Riga numeri degli step ---
    const numRow = document.createElement('div');
    numRow.className = 'seq__row seq__row--numbers';
    numRow.appendChild(makeLabel('', null));
    numRow.appendChild(makeBeats((b, i) => {
      const stepIdx = b * 4 + i;
      const el = document.createElement('div');
      el.className = 'step-number' + (i === 0 ? ' step-number--downbeat' : '');
      el.textContent = String(stepIdx + 1).padStart(2, '0');
      return el;
    }));
    root.appendChild(numRow);

    // --- Righe tracce ---
    TRACKS.forEach((track, trackIdx) => {
      const row = document.createElement('div');
      row.className = 'seq__row';
      row.style.setProperty('--track-color', track.color);
      row.appendChild(makeLabel(track.name, track.color));

      row.appendChild(makeBeats((b, i) => {
        const stepIdx = b * 4 + i;
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'step';
        btn.dataset.track = String(trackIdx);
        btn.dataset.step = String(stepIdx);
        btn.setAttribute('aria-label', `${track.name} step ${stepIdx + 1}`);
        btn.addEventListener('click', () => toggleCell(trackIdx, stepIdx));
        stepElements[trackIdx][stepIdx] = btn;
        return btn;
      }));

      root.appendChild(row);
    });
  }

  function makeLabel(text, color) {
    const label = document.createElement('div');
    label.className = 'seq__label';
    const dot = document.createElement('span');
    dot.className = 'seq__dot';
    label.appendChild(dot);
    const name = document.createElement('span');
    name.className = 'seq__name';
    name.textContent = text;
    label.appendChild(name);
    return label;
  }

  function makeBeats(cellFactory) {
    const beats = document.createElement('div');
    beats.className = 'beats';
    for (let b = 0; b < 4; b++) {
      const beat = document.createElement('div');
      beat.className = 'beat';
      for (let i = 0; i < 4; i++) {
        beat.appendChild(cellFactory(b, i));
      }
      beats.appendChild(beat);
    }
    return beats;
  }

  function toggleCell(trackIdx, stepIdx) {
    unlockAudio();
    pattern[trackIdx][stepIdx] = !pattern[trackIdx][stepIdx];
    const el = stepElements[trackIdx][stepIdx];
    el.classList.toggle('step--active', pattern[trackIdx][stepIdx]);
    // Preview sonora quando si accende una cella
    if (pattern[trackIdx][stepIdx]) {
      TRACKS[trackIdx].play(audioCtx.currentTime);
    }
  }

  function refreshPatternUI() {
    for (let t = 0; t < TRACKS.length; t++) {
      for (let s = 0; s < NUM_STEPS; s++) {
        stepElements[t][s].classList.toggle('step--active', pattern[t][s]);
      }
    }
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
    // Processa tutti gli eventi il cui "time" e' gia' passato
    while (uiQueue.length && uiQueue[0].time <= now) {
      const ev = uiQueue.shift();
      flashColumn(ev.step);
    }
    requestAnimationFrame(tickUI);
  }

  function flashColumn(step) {
    // Rimuove le highlight precedenti
    for (let t = 0; t < TRACKS.length; t++) {
      for (let s = 0; s < NUM_STEPS; s++) {
        const el = stepElements[t][s];
        el.classList.remove('step--current-column');
        el.classList.remove('step--playing');
      }
    }
    // Aggiunge la highlight sulla colonna corrente
    for (let t = 0; t < TRACKS.length; t++) {
      const el = stepElements[t][step];
      el.classList.add('step--current-column');
      // triggera l'animazione "flash"
      void el.offsetWidth; // reflow: resetta l'animazione
      el.classList.add('step--playing');
    }
  }

  function clearPlayingHighlights() {
    for (let t = 0; t < TRACKS.length; t++) {
      for (let s = 0; s < NUM_STEPS; s++) {
        stepElements[t][s].classList.remove('step--current-column');
        stepElements[t][s].classList.remove('step--playing');
      }
    }
  }

  // ============================================================
  // 7) PATTERN DEMO / CLEAR
  // ============================================================
  function loadDemo() {
    // Four-on-the-floor classico
    pattern = [
      // Kick su 1, 5, 9, 13
      [true,false,false,false, true,false,false,false, true,false,false,false, true,false,false,false],
      // Snare sul backbeat (5, 13)
      [false,false,false,false, true,false,false,false, false,false,false,false, true,false,false,false],
      // Hi-hat su tutti gli ottavi
      [true,false,true,false, true,false,true,false, true,false,true,false, true,false,true,false],
      // Clap di rinforzo sul 13
      [false,false,false,false, false,false,false,false, false,false,false,false, true,false,false,false],
    ];
    refreshPatternUI();
  }

  function clearPattern() {
    pattern = TRACKS.map(() => new Array(NUM_STEPS).fill(false));
    refreshPatternUI();
  }

  // ============================================================
  // 8) BOOTSTRAP
  // ============================================================
  document.addEventListener('DOMContentLoaded', () => {
    buildSequencer();
    loadDemo();

    // Play / Stop
    document.getElementById('playButton').addEventListener('click', toggleTransport);

    // Slider BPM
    const slider = document.getElementById('bpmSlider');
    const readout = document.getElementById('bpmValue');
    slider.addEventListener('input', e => {
      bpm = parseInt(e.target.value, 10);
      readout.textContent = bpm;
    });

    // Pulsanti chip
    document.getElementById('demoBtn').addEventListener('click', () => {
      loadDemo();
    });
    document.getElementById('clearBtn').addEventListener('click', clearPattern);

    // Scorciatoie da tastiera
    document.addEventListener('keydown', e => {
      if (e.target instanceof HTMLInputElement) return;
      if (e.code === 'Space') {
        e.preventDefault();
        toggleTransport();
      } else if (e.key === 'c' || e.key === 'C') {
        clearPattern();
      } else if (e.key === 'd' || e.key === 'D') {
        loadDemo();
      }
    });

    // Sblocca l'audio al primo tap/click ovunque (per iOS)
    const firstTouch = () => {
      unlockAudio();
      window.removeEventListener('touchstart', firstTouch);
      window.removeEventListener('mousedown', firstTouch);
    };
    window.addEventListener('touchstart', firstTouch, { once: true, passive: true });
    window.addEventListener('mousedown', firstTouch, { once: true });
  });

})();

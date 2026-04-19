#!/usr/bin/env python3
"""
render_json_to_wav.py — renderer offline dei JSON di DrumAPP.

Replica in numpy la sintesi Web Audio di DrumAPP (8 voci sintetizzate,
scheduler con swing/ratchet/probability/nudge/humanize, pan/filter/pitch/decay
per traccia). Produce WAV 44.1 kHz 16-bit stereo identico (a meno di
differenze di floating point) a quello che esce dal BOUNCE del browser.

Uso:
    python3 render_json_to_wav.py input.json output.wav [--loops N]
    python3 render_json_to_wav.py input.json output.wav --song  # usa songSequence

Se ffmpeg è disponibile, puoi convertire in MP3 con:
    ffmpeg -y -i out.wav -codec:a libmp3lame -qscale:a 2 out.mp3
"""

import sys
import json
import argparse
import numpy as np
from scipy.signal import lfilter, butter
from pathlib import Path

SR = 44100  # sample rate fisso

# Indici tracce
KICK, SNARE, HIHAT, OPENHAT, CLAP, TOM, RIM, COW = range(8)
TRACK_IDS = ['kick', 'snare', 'hihat', 'openhat', 'clap', 'tom', 'rim', 'cow']


# =======================================================
# UTILITÀ DSP
# =======================================================

def semi(s):
    """Fattore di pitch da semitoni"""
    return 2.0 ** (s / 12.0)


def env_exp(n_samples, attack, peak, end=1e-3):
    """Envelope lineare attacco + esponenziale decay (mimica gain.setValueAtTime + exponentialRampToValueAtTime)"""
    env = np.zeros(n_samples)
    a = max(1, int(attack * SR))
    if a > 0:
        env[:a] = np.linspace(0, peak, a)
    if n_samples > a:
        # decay esponenziale da peak a end
        n_d = n_samples - a
        tau = n_d / 5  # 5 tau = decay a fine
        env[a:] = peak * np.exp(-np.arange(n_d) / max(1, tau))
    return env


def exp_decay(n_samples, peak, tau_samples):
    """Decay esponenziale puro"""
    if tau_samples <= 0:
        return np.zeros(n_samples)
    t = np.arange(n_samples)
    return peak * np.exp(-t / tau_samples)


def freq_sweep(n_samples, f_start, f_end, t_sweep_s):
    """Frequenza esponenziale da f_start a f_end in t_sweep_s"""
    n_sweep = min(n_samples, int(t_sweep_s * SR))
    freqs = np.zeros(n_samples)
    if n_sweep > 0:
        # sweep esponenziale
        ratio = f_end / f_start
        freqs[:n_sweep] = f_start * (ratio ** (np.arange(n_sweep) / n_sweep))
    if n_samples > n_sweep:
        freqs[n_sweep:] = f_end
    return freqs


def osc_sine_sweep(n_samples, f_start, f_end, t_sweep_s):
    """Oscillatore sine con sweep di frequenza"""
    freqs = freq_sweep(n_samples, f_start, f_end, t_sweep_s)
    phase = np.cumsum(2 * np.pi * freqs / SR)
    return np.sin(phase)


def osc_triangle(n_samples, freq):
    t = np.arange(n_samples) / SR
    # triangle come 2/pi * asin(sin(2*pi*f*t))
    return (2.0 / np.pi) * np.arcsin(np.sin(2 * np.pi * freq * t))


def osc_square(n_samples, freq):
    t = np.arange(n_samples) / SR
    return np.sign(np.sin(2 * np.pi * freq * t))


def noise(n_samples, seed=None):
    """Rumore bianco"""
    if seed is not None:
        rng = np.random.RandomState(seed)
        return rng.uniform(-1, 1, n_samples)
    return np.random.uniform(-1, 1, n_samples)


def biquad(sig, btype, cutoff_hz, q=0.707):
    """Filtro biquad Butterworth (approssima BiquadFilter di Web Audio)"""
    if btype == 'off' or sig is None or len(sig) == 0:
        return sig
    nyq = SR / 2
    cutoff = min(max(cutoff_hz, 20), nyq - 100)
    # scipy butter usa ordine 2 per comportamento simile a biquad base
    b, a = butter(2, cutoff / nyq, btype=('low' if btype == 'lowpass'
                                          else 'high' if btype == 'highpass'
                                          else 'band'))
    return lfilter(b, a, sig)


# =======================================================
# SINTESI DELLE 8 VOCI (replica app.js)
# =======================================================

def voice_kick(pitch=0, decay_mul=1.0, vel=0.9):
    """Kick: sine sweep 165→45 Hz + click 1200 Hz"""
    p = semi(pitch)
    dur = int(SR * (0.5 * decay_mul + 0.05))
    out = np.zeros(dur)

    # sweep
    osc = osc_sine_sweep(dur, 165 * p, 45 * p, 0.12 * decay_mul)
    env = exp_decay(dur, vel, int(SR * 0.45 * decay_mul / 5))
    out += osc * env

    # click 1200 Hz
    click_dur = int(SR * 0.05)
    click_t = np.arange(click_dur) / SR
    click_osc = np.sin(2 * np.pi * 1200 * p * click_t)
    click_env = exp_decay(click_dur, 0.35 * vel, int(SR * 0.025 / 5))
    out[:click_dur] += click_osc * click_env

    return out


def voice_snare(pitch=0, decay_mul=1.0, vel=0.9, noise_seed=None):
    """Snare: triangle 220 Hz + white noise HP 1 kHz"""
    p = semi(pitch)
    dur = int(SR * (0.22 * decay_mul + 0.02))
    out = np.zeros(dur)

    # tono
    tone = osc_triangle(dur, 220 * p)
    tone_env = exp_decay(dur, 0.5 * vel, int(SR * 0.11 * decay_mul / 5))
    out += tone * tone_env

    # noise HP filtered
    n = noise(dur, noise_seed)
    n_filt = biquad(n, 'highpass', 1000)
    n_env = exp_decay(dur, 0.7 * vel, int(SR * 0.17 * decay_mul / 5))
    out += n_filt * n_env

    return out


def voice_hihat(pitch=0, decay_mul=1.0, vel=0.9, noise_seed=None):
    """Hi-hat chiuso: noise HP 7 kHz"""
    p = semi(pitch * 0.5)
    dur = int(SR * (0.1 * decay_mul + 0.01))
    n = noise(dur, noise_seed)
    n_filt = biquad(n, 'highpass', 7000 * p)
    env = exp_decay(dur, 0.45 * vel, int(SR * 0.055 * decay_mul / 5))
    return n_filt * env


def voice_openhat(pitch=0, decay_mul=1.0, vel=0.9, noise_seed=None):
    """Open hi-hat: noise HP 6.5 kHz, decay lungo"""
    p = semi(pitch * 0.5)
    dur = int(SR * (0.5 * decay_mul + 0.02))
    n = noise(dur, noise_seed)
    n_filt = biquad(n, 'highpass', 6500 * p)
    # attack + decay
    env = env_exp(dur, attack=0.003, peak=0.4 * vel)
    # sostituisco con exp decay dopo attack
    a = int(0.003 * SR)
    env[a:] = 0.4 * vel * np.exp(-np.arange(dur - a) / max(1, int(SR * 0.45 * decay_mul / 5)))
    return n_filt * env


def voice_clap(pitch=0, decay_mul=1.0, vel=0.9, noise_seed=None):
    """Clap: noise bandpass 1500 Hz con triplo attacco + decay"""
    p = semi(pitch)
    dur = int(SR * (0.35 * decay_mul + 0.02))
    n = noise(dur, noise_seed)
    # bandpass via HP + LP (approssimazione)
    n_bp = biquad(biquad(n, 'highpass', 1000 * p), 'lowpass', 2500 * p)

    # envelope triplo (tipico clap 808)
    env = np.zeros(dur)
    peaks_t = [0.002, 0.013, 0.027, 0.030]
    dips_t = [0.013, 0.027, 0.030, 0.035]
    # semplificazione: exp decay da step 0.030s
    attack_end = int(0.030 * SR)
    env[:attack_end] = 0.85 * vel
    if dur > attack_end:
        env[attack_end:] = 0.85 * vel * np.exp(-np.arange(dur - attack_end)
                                                / max(1, int(SR * 0.32 * decay_mul / 5)))
    return n_bp * env


def voice_tom(pitch=0, decay_mul=1.0, vel=0.9, noise_seed=None):
    """Tom: sine sweep 180→90 Hz + noise transient"""
    p = semi(pitch)
    dur = int(SR * (0.65 * decay_mul + 0.02))
    out = np.zeros(dur)

    sweep = osc_sine_sweep(dur, 180 * p, 90 * p, 0.15 * decay_mul)
    env = exp_decay(dur, 0.8 * vel, int(SR * 0.6 * decay_mul / 5))
    out += sweep * env

    # noise transient
    tr_dur = int(SR * 0.05)
    tr_n = noise(tr_dur, noise_seed)
    tr_filt = biquad(biquad(tr_n, 'highpass', 200), 'lowpass', 800)
    tr_env = exp_decay(tr_dur, 0.2 * vel, int(SR * 0.03 / 5))
    out[:tr_dur] += tr_filt * tr_env

    return out


def voice_rim(pitch=0, decay_mul=1.0, vel=0.9):
    """Rimshot: square 800 + triangle 380 in bandpass 1800 Hz"""
    p = semi(pitch)
    dur = int(SR * 0.08)
    o1 = osc_square(dur, 800 * p)
    o2 = osc_triangle(dur, 380 * p)
    mix = o1 + o2
    filt = biquad(biquad(mix, 'highpass', 1000 * p), 'lowpass', 3000 * p)
    env = exp_decay(dur, 0.5 * vel, int(SR * 0.05 * decay_mul / 5))
    return filt * env


def voice_cow(pitch=0, decay_mul=1.0, vel=0.9):
    """Cowbell TR-808: due square 540/800 Hz in bandpass 2000 Hz"""
    p = semi(pitch)
    dur = int(SR * (0.35 * decay_mul + 0.02))
    o1 = osc_square(dur, 540 * p)
    o2 = osc_square(dur, 800 * p)
    mix = 0.5 * (o1 + o2)
    filt = biquad(biquad(mix, 'highpass', 1200 * p), 'lowpass', 3500 * p)

    env = np.zeros(dur)
    a = int(0.004 * SR)
    env[:a] = np.linspace(0, 0.35 * vel, a)
    if dur > a:
        env[a:] = 0.35 * vel * np.exp(-np.arange(dur - a) / max(1, int(SR * 0.3 * decay_mul / 5)))
    return mix * env * filt / (np.max(np.abs(filt)) + 1e-9)


VOICES = {
    'kick': voice_kick,
    'snare': voice_snare,
    'hihat': voice_hihat,
    'openhat': voice_openhat,
    'clap': voice_clap,
    'tom': voice_tom,
    'rim': voice_rim,
    'cow': voice_cow,
}


# =======================================================
# RENDERER (applica catena audio per traccia)
# =======================================================

def render_voice(track_idx, vel, pitch, decay_mul):
    """Genera il buffer mono di una voce"""
    track_id = TRACK_IDS[track_idx]
    voice_fn = VOICES[track_id]
    # Noise seed variabile per evitare suoni identici identici
    noise_seed = np.random.randint(0, 1_000_000)
    sig = voice_fn(pitch=pitch, decay_mul=decay_mul, vel=vel,
                   noise_seed=noise_seed) if track_id in ('snare', 'hihat', 'openhat', 'clap', 'tom') else voice_fn(pitch=pitch, decay_mul=decay_mul, vel=vel)
    return sig


def apply_track_chain(sig, track_params):
    """Applica filter + gain della traccia"""
    p = track_params
    # Mute/solo già applicato in render_song
    # Filter
    if p.get('filterType', 'off') != 'off':
        cutoff = 50 * (360 ** p.get('filterCutoff', 0.7))
        sig = biquad(sig, p['filterType'], cutoff, p.get('filterQ', 1.0))
    # Gain
    sig = sig * p.get('volume', 0.85)
    return sig


def pan_to_stereo(sig_mono, pan):
    """Applica pan: -1=L, 0=C, +1=R (constant power approx)"""
    # constant power
    p = max(-1.0, min(1.0, pan))
    angle = (p + 1) * np.pi / 4  # da 0 a pi/2
    L = sig_mono * np.cos(angle)
    R = sig_mono * np.sin(angle)
    return L, R


def render_song(data, song_override=None):
    """Renderizza un set completo (patterns + trackParams + bpm + swing + ...) in stereo"""
    bpm = data['bpm']
    swing = data.get('swing', 0)
    pattern_length = data.get('patternLength', 16)
    humanize = data.get('humanize', False)
    track_params = data['trackParams']
    patterns = data['patterns']

    # Mute/solo logic
    any_solo = any(p.get('solo', False) for p in track_params)
    effective_mute = [
        p.get('mute', False) or (any_solo and not p.get('solo', False))
        for p in track_params
    ]

    # Sequenza
    if song_override is not None:
        sequence = song_override
    else:
        sequence = data.get('songSequence', ['A'])

    seconds_per_step = (60.0 / bpm) / 4
    total_steps = len(sequence) * pattern_length
    total_samples = int(SR * (total_steps * seconds_per_step + 1.0))  # +1s tail

    mix_L = np.zeros(total_samples)
    mix_R = np.zeros(total_samples)

    print(f"  Render · BPM {bpm} · swing {swing}% · {len(sequence)} patterns · ~{total_samples/SR:.1f}s")

    # Schedule tutti gli step
    for seq_idx, pat_name in enumerate(sequence):
        pat = patterns.get(pat_name)
        if not pat:
            continue
        for step in range(pattern_length):
            # Base time con swing
            base_s = (seq_idx * pattern_length + step) * seconds_per_step
            if step % 2 == 1 and swing > 0:
                base_s += (swing / 100) * seconds_per_step * 0.5

            for t_idx in range(8):
                if effective_mute[t_idx]:
                    continue
                cell = pat[t_idx][step] if step < len(pat[t_idx]) else None
                if not cell:
                    continue
                # Probability
                if cell.get('prob', 100) < 100 and np.random.rand() * 100 >= cell['prob']:
                    continue

                tp = track_params[t_idx]
                vel = cell['vel']
                nudge_s = cell.get('nudge', 0) / 1000.0

                # Humanize
                if humanize:
                    nudge_s += (np.random.rand() - 0.5) * 0.012
                    vel = max(0.05, min(1.0, vel + (np.random.rand() - 0.5) * 0.15))

                ratch = cell.get('ratch', 1)
                ratch_gap_s = (seconds_per_step * 0.9) / ratch

                for r in range(ratch):
                    t_s = base_s + nudge_s + r * ratch_gap_s
                    start_sample = int(t_s * SR)
                    if start_sample < 0 or start_sample >= total_samples:
                        continue

                    # Rendering della voce
                    v_base = vel * (1.0 if r == 0 else 0.7)
                    sig = render_voice(t_idx, v_base, tp.get('pitch', 0), tp.get('decay', 1.0))
                    sig = apply_track_chain(sig, tp)

                    # Pan
                    L, R = pan_to_stereo(sig, tp.get('pan', 0.0))

                    # Mix
                    end = min(start_sample + len(L), total_samples)
                    n = end - start_sample
                    mix_L[start_sample:end] += L[:n]
                    mix_R[start_sample:end] += R[:n]

    # Master gain
    master = 0.75
    mix_L *= master
    mix_R *= master

    # Soft clip (tanh) per evitare clipping duro
    peak = max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)))
    if peak > 0.98:
        print(f"  Soft-clipping applicato (peak era {peak:.2f})")
        mix_L = np.tanh(mix_L * 0.95)
        mix_R = np.tanh(mix_R * 0.95)

    return mix_L, mix_R


def save_wav(path, L, R):
    """Scrive WAV 16-bit stereo"""
    import wave
    L16 = np.clip(L * 32767, -32768, 32767).astype(np.int16)
    R16 = np.clip(R * 32767, -32768, 32767).astype(np.int16)
    stereo = np.empty(len(L) * 2, dtype=np.int16)
    stereo[0::2] = L16
    stereo[1::2] = R16
    with wave.open(path, 'wb') as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(stereo.tobytes())


# =======================================================
# CLI
# =======================================================

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input_json', help='Percorso JSON DrumAPP')
    ap.add_argument('output_wav', help='Percorso WAV output')
    ap.add_argument('--loops', type=int, default=None,
                    help='Numero loop del pattern corrente (ignora song sequence)')
    ap.add_argument('--pattern', default=None,
                    help="Se --loops, quale pattern loopare (default: primo di songSequence)")
    ap.add_argument('--song', action='store_true',
                    help='Usa la song sequence dal file (default)')
    ap.add_argument('--seed', type=int, default=42,
                    help='Seed random per riproducibilità (default 42)')
    args = ap.parse_args()

    np.random.seed(args.seed)

    with open(args.input_json) as f:
        data = json.load(f)

    # Determina la sequenza
    if args.loops:
        pat = args.pattern or data.get('songSequence', ['A'])[0]
        song = [pat] * args.loops
    else:
        song = None  # usa songSequence

    print(f"▶ {args.input_json}")
    L, R = render_song(data, song_override=song)
    save_wav(args.output_wav, L, R)
    print(f"✓ {args.output_wav} · {len(L)/SR:.1f}s · 44.1kHz 16-bit stereo")


if __name__ == "__main__":
    main()

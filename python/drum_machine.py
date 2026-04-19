"""
================================================================================
  DrumAPP - Drum Machine a 16 step in Python (versione desktop legacy)
  Sintesi audio matematica (senza WAV esterni) + GUI + Sequencer
  Librerie: pygame, numpy
  Licenza: MIT

  NOTA: questa e' la versione desktop storica.
  La versione corrente e' la PWA (vedi cartella principale del repo).
================================================================================

Tracce:
    - KICK  (cassa)      : sinusoide con inviluppo di pitch decrescente
    - SNARE (rullante)   : mix tono + rumore bianco
    - HIHAT (charleston) : rumore bianco filtrato passa-alto
    - CLAP  (battito)    : rumore con inviluppo multi-burst

Controlli:
    - Click sulle celle  : accende/spegne lo step
    - Bottone PLAY/STOP  : avvia/ferma il sequencer
    - Slider BPM         : regola il tempo (60 - 200 BPM)
    - SPAZIO             : Play/Stop da tastiera
    - C                  : Pulisce il pattern
    - Q o ESC            : Esce

Installazione:
    pip install -r requirements.txt
    python drum_machine.py
"""

import sys
import numpy as np
import pygame

# ==============================================================================
# 1) CONFIGURAZIONE AUDIO
# ==============================================================================
SAMPLE_RATE = 44100
BUFFER_SIZE = 512

pygame.mixer.pre_init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=BUFFER_SIZE)
pygame.init()
pygame.mixer.set_num_channels(16)


# ==============================================================================
# 2) SINTESI SONORA
# ==============================================================================
def to_sound(signal: np.ndarray) -> pygame.mixer.Sound:
    max_val = np.max(np.abs(signal))
    if max_val > 0:
        signal = signal / max_val
    audio = (signal * 32767 * 0.85).astype(np.int16)
    stereo = np.column_stack((audio, audio))
    stereo = np.ascontiguousarray(stereo)
    return pygame.sndarray.make_sound(stereo)


def generate_kick(duration: float = 0.5) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    freq_env = 45 + 120 * np.exp(-t * 25)
    phase = 2 * np.pi * np.cumsum(freq_env) / SAMPLE_RATE
    amp_env = np.exp(-t * 6)
    signal = np.sin(phase) * amp_env
    click_env = np.exp(-t * 150)
    signal += np.sin(2 * np.pi * 1200 * t) * click_env * 0.3
    return signal


def generate_snare(duration: float = 0.25) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = np.sin(2 * np.pi * 220 * t) + 0.5 * np.sin(2 * np.pi * 330 * t)
    tone_env = np.exp(-t * 30)
    noise = np.random.uniform(-1, 1, len(t))
    noise_env = np.exp(-t * 18)
    return 0.5 * tone * tone_env + 0.5 * noise * noise_env


def generate_hihat(duration: float = 0.08) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t))
    hp = np.diff(noise, prepend=0.0)
    amp_env = np.exp(-t * 70)
    return hp * amp_env


def generate_clap(duration: float = 0.3) -> np.ndarray:
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    noise = np.random.uniform(-1, 1, len(t))
    noise = noise - np.roll(noise, 1) * 0.3
    env = np.zeros_like(t)
    for delay in (0.0, 0.012, 0.024):
        mask = t >= delay
        env[mask] += np.exp(-(t[mask] - delay) * 120)
    env = env / np.max(env)
    tail = np.exp(-t * 15) * 0.6
    total_env = np.maximum(env, tail * (t > 0.03))
    return noise * total_env


# ==============================================================================
# 3) TRACCE
# ==============================================================================
TRACKS = [
    {"name": "KICK",  "color": (200,  85,  61), "sound": to_sound(generate_kick())},
    {"name": "SNARE", "color": (230, 162,  60), "sound": to_sound(generate_snare())},
    {"name": "HIHAT", "color": (109, 151, 115), "sound": to_sound(generate_hihat())},
    {"name": "CLAP",  "color": ( 61,  90, 128), "sound": to_sound(generate_clap())},
]
NUM_TRACKS = len(TRACKS)
NUM_STEPS = 16
pattern = [[False] * NUM_STEPS for _ in range(NUM_TRACKS)]


def load_demo_pattern() -> None:
    for s in (0, 4, 8, 12):
        pattern[0][s] = True
    for s in (4, 12):
        pattern[1][s] = True
    for s in range(0, 16, 2):
        pattern[2][s] = True
    pattern[3][12] = True


load_demo_pattern()


# ==============================================================================
# 4) UI
# ==============================================================================
WIDTH, HEIGHT = 960, 460
BG_COLOR      = (234, 227, 210)   # paper
PANEL_COLOR   = (220, 211, 185)   # paper-2
TEXT_COLOR    = ( 26,  26,  34)   # ink
SUBTEXT_COLOR = (106, 106, 117)   # ink-soft
ACCENT        = (247, 127,   0)   # accent
CELL_OFF      = (217, 209, 186)
CELL_DOWNBEAT = (204, 196, 170)

GRID_X, GRID_Y = 160, 110
CELL_SIZE, CELL_GAP, ROW_GAP = 42, 6, 14

PLAY_BTN_RECT = pygame.Rect(20, 22, 110, 42)
SLIDER_X, SLIDER_Y, SLIDER_W, SLIDER_H = 260, 42, 380, 6
BPM_MIN, BPM_MAX = 60, 200

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DrumAPP - 16 Step Drum Machine")
clock = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 22, bold=True)
font_med   = pygame.font.SysFont("Arial", 16, bold=True)
font_small = pygame.font.SysFont("Arial", 13)

playing = False
bpm = 120
current_step = -1
last_step_time = 0
dragging_slider = False


def step_interval_ms() -> int:
    return int(60000 / bpm / 4)


def cell_rect(track: int, step: int) -> pygame.Rect:
    x = GRID_X + step * (CELL_SIZE + CELL_GAP)
    y = GRID_Y + track * (CELL_SIZE + ROW_GAP)
    return pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)


def slider_knob_x() -> int:
    ratio = (bpm - BPM_MIN) / (BPM_MAX - BPM_MIN)
    return int(SLIDER_X + ratio * SLIDER_W)


def bpm_from_mouse_x(mx: int) -> int:
    mx = max(SLIDER_X, min(SLIDER_X + SLIDER_W, mx))
    ratio = (mx - SLIDER_X) / SLIDER_W
    return int(round(BPM_MIN + ratio * (BPM_MAX - BPM_MIN)))


def clear_pattern() -> None:
    for t in range(NUM_TRACKS):
        for s in range(NUM_STEPS):
            pattern[t][s] = False


def draw_header() -> None:
    pygame.draw.rect(screen, PANEL_COLOR, (0, 0, WIDTH, 86))
    btn_color = (200, 85, 61) if playing else (26, 26, 34)
    pygame.draw.rect(screen, btn_color, PLAY_BTN_RECT, border_radius=8)
    label = "STOP" if playing else "PLAY"
    txt = font_med.render(label, True, (234, 227, 210))
    screen.blit(txt, txt.get_rect(center=PLAY_BTN_RECT.center))

    bpm_label = font_small.render("BPM", True, SUBTEXT_COLOR)
    screen.blit(bpm_label, (SLIDER_X - 40, 36))
    pygame.draw.rect(screen, CELL_OFF, (SLIDER_X, SLIDER_Y, SLIDER_W, SLIDER_H), border_radius=3)
    kx = slider_knob_x()
    pygame.draw.rect(screen, ACCENT, (SLIDER_X, SLIDER_Y, kx - SLIDER_X, SLIDER_H), border_radius=3)
    pygame.draw.circle(screen, ACCENT, (kx, SLIDER_Y + SLIDER_H // 2), 10)
    pygame.draw.circle(screen, TEXT_COLOR, (kx, SLIDER_Y + SLIDER_H // 2), 10, 2)

    bpm_txt = font_big.render(f"{bpm}", True, TEXT_COLOR)
    screen.blit(bpm_txt, (SLIDER_X + SLIDER_W + 20, 30))


def draw_grid() -> None:
    for i, track in enumerate(TRACKS):
        y = GRID_Y + i * (CELL_SIZE + ROW_GAP) + CELL_SIZE // 2
        pygame.draw.circle(screen, track["color"], (30, y), 8)
        pygame.draw.circle(screen, TEXT_COLOR, (30, y), 8, 2)
        label = font_med.render(track["name"], True, TEXT_COLOR)
        screen.blit(label, (50, y - 10))

    for t in range(NUM_TRACKS):
        for s in range(NUM_STEPS):
            rect = cell_rect(t, s)
            is_active = pattern[t][s]
            is_current = (s == current_step)
            is_downbeat = (s % 4 == 0)

            if is_active:
                color = TRACKS[t]["color"]
                if is_current and playing:
                    color = ACCENT
            else:
                color = CELL_DOWNBEAT if is_downbeat else CELL_OFF

            pygame.draw.rect(screen, color, rect, border_radius=6)
            pygame.draw.rect(screen, TEXT_COLOR, rect, 2, border_radius=6)

    if playing and current_step >= 0:
        r = cell_rect(0, current_step)
        pygame.draw.rect(screen, ACCENT, (r.x, GRID_Y - 8, CELL_SIZE, 3), border_radius=2)


def draw_footer() -> None:
    y = HEIGHT - 50
    pygame.draw.rect(screen, PANEL_COLOR, (0, y - 5, WIDTH, 55))
    info1 = font_small.render(
        "Click per attivare gli step  |  SPAZIO: Play/Stop  |  C: Pulisci  |  Q/ESC: Esci",
        True, SUBTEXT_COLOR)
    screen.blit(info1, (20, y + 2))
    info2 = font_small.render(
        "DrumAPP - versione desktop (legacy)",
        True, SUBTEXT_COLOR)
    screen.blit(info2, (20, y + 22))


def handle_mouse_down(pos) -> None:
    global playing, last_step_time, current_step, dragging_slider, bpm
    if PLAY_BTN_RECT.collidepoint(pos):
        playing = not playing
        if playing:
            current_step = -1
            last_step_time = pygame.time.get_ticks() - step_interval_ms()
        return
    kx = slider_knob_x()
    knob_rect = pygame.Rect(kx - 12, SLIDER_Y - 10, 24, 26)
    track_rect = pygame.Rect(SLIDER_X - 5, SLIDER_Y - 10, SLIDER_W + 10, 26)
    if knob_rect.collidepoint(pos) or track_rect.collidepoint(pos):
        dragging_slider = True
        bpm = bpm_from_mouse_x(pos[0])
        return
    for t in range(NUM_TRACKS):
        for s in range(NUM_STEPS):
            if cell_rect(t, s).collidepoint(pos):
                pattern[t][s] = not pattern[t][s]
                if pattern[t][s]:
                    TRACKS[t]["sound"].play()
                return


def handle_mouse_motion(pos) -> None:
    global bpm
    if dragging_slider:
        bpm = bpm_from_mouse_x(pos[0])


def main() -> None:
    global playing, current_step, last_step_time, dragging_slider
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = False
            elif event.type == pygame.MOUSEMOTION:
                handle_mouse_motion(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    playing = not playing
                    if playing:
                        current_step = -1
                        last_step_time = pygame.time.get_ticks() - step_interval_ms()
                elif event.key == pygame.K_c:
                    clear_pattern()
                elif event.key in (pygame.K_q, pygame.K_ESCAPE):
                    running = False

        if playing:
            now = pygame.time.get_ticks()
            if now - last_step_time >= step_interval_ms():
                last_step_time = now
                current_step = (current_step + 1) % NUM_STEPS
                for t in range(NUM_TRACKS):
                    if pattern[t][current_step]:
                        TRACKS[t]["sound"].play()

        screen.fill(BG_COLOR)
        draw_header()
        draw_grid()
        draw_footer()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()

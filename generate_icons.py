"""
Genera le icone PWA per DrumAPP in stile "Studio Press":
- Sfondo carta avorio
- 4x4 griglia di pad stile drum machine con pattern four-on-the-floor
- Colori delle tracce coordinati al tema
- Versioni 'any' (con margine respiro) e 'maskable' (pieno canvas)
"""

import os
from PIL import Image, ImageDraw, ImageFilter

# Colori (coordinati con style.css)
PAPER     = (234, 227, 210, 255)
PAPER_2   = (220, 211, 185, 255)
INK       = (26, 26, 34, 255)
INK_SOFT  = (106, 106, 117, 255)
ACCENT    = (247, 127, 0, 255)
KICK      = (200, 85, 61, 255)
SNARE     = (230, 162, 60, 255)
HIHAT     = (109, 151, 115, 255)
CLAP      = (61, 90, 128, 255)

# Pattern esemplificativo per l'icona:
#   kick su 1, snare su 3 (diradato per leggibilita')
PATTERN = [
    [1, 0, 0, 0],  # KICK
    [0, 0, 1, 0],  # SNARE
    [1, 0, 1, 0],  # HIHAT
    [0, 0, 1, 0],  # CLAP
]
COLORS_ACTIVE = [KICK, SNARE, HIHAT, CLAP]


def draw_icon(size: int, maskable: bool = False) -> Image.Image:
    """
    Disegna l'icona quadrata `size x size`.
    - maskable=False: margine esterno, angoli arrotondati
    - maskable=True: disegna a pieno canvas (il sistema applichera' la sua maschera)
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if maskable:
        # Sfondo pieno
        draw.rectangle([0, 0, size, size], fill=PAPER)
        inset = int(size * 0.14)  # margine interno per la "safe zone" del maskable
    else:
        # Sfondo con angoli arrotondati
        radius = int(size * 0.18)
        draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=PAPER)
        inset = int(size * 0.11)

    # Bordo sottile (solo non-maskable)
    if not maskable:
        radius = int(size * 0.18)
        border_w = max(2, size // 80)
        for i in range(border_w):
            draw.rounded_rectangle(
                [i, i, size - 1 - i, size - 1 - i],
                radius=max(1, radius - i),
                outline=INK
            )

    # Accento arancione (barra in basso)
    accent_h = int(size * 0.06)
    if maskable:
        draw.rectangle([0, size - accent_h, size, size], fill=ACCENT)
    else:
        # barra arancione nella fascia inferiore con angoli smussati
        radius = int(size * 0.18)
        draw.rounded_rectangle(
            [int(size * 0.02), size - accent_h - int(size * 0.02),
             size - int(size * 0.02), size - int(size * 0.02)],
            radius=accent_h // 2,
            fill=ACCENT
        )

    # Griglia 4x4 di pad
    grid_top = inset
    grid_left = inset
    grid_right = size - inset
    grid_bottom = size - inset - int(size * 0.08)  # lascia spazio per la barra arancione
    grid_w = grid_right - grid_left
    grid_h = grid_bottom - grid_top

    cell_full_w = grid_w / 4
    cell_full_h = grid_h / 4
    gap = max(2, int(size * 0.015))
    cell_w = cell_full_w - gap
    cell_h = cell_full_h - gap
    pad_radius = int(min(cell_w, cell_h) * 0.18)
    pad_border = max(1, int(size / 120))

    for row in range(4):
        for col in range(4):
            x0 = grid_left + col * cell_full_w + gap / 2
            y0 = grid_top + row * cell_full_h + gap / 2
            x1 = x0 + cell_w
            y1 = y0 + cell_h

            if PATTERN[row][col]:
                fill = COLORS_ACTIVE[row]
            else:
                fill = PAPER_2

            draw.rounded_rectangle(
                [x0, y0, x1, y1],
                radius=pad_radius,
                fill=fill,
                outline=INK,
                width=pad_border
            )

    # Ombreggiatura leggera per dare profondita'
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    if not maskable:
        radius = int(size * 0.18)
        sdraw.rounded_rectangle(
            [2, 4, size - 1, size - 1],
            radius=radius,
            fill=(0, 0, 0, 18)
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=size // 80))
        # composita
        base = Image.new('RGBA', img.size, (0, 0, 0, 0))
        base = Image.alpha_composite(base, shadow)
        base = Image.alpha_composite(base, img)
        img = base

    return img


def main():
    out_dir = os.path.join(os.path.dirname(__file__), 'icons')
    os.makedirs(out_dir, exist_ok=True)

    for size in (192, 512):
        # Versione standard
        draw_icon(size, maskable=False).save(
            os.path.join(out_dir, f'icon-{size}.png'),
            optimize=True
        )
        # Versione maskable (per Android adaptive icons)
        draw_icon(size, maskable=True).save(
            os.path.join(out_dir, f'icon-{size}-maskable.png'),
            optimize=True
        )

    print('Icone generate:')
    for f in sorted(os.listdir(out_dir)):
        path = os.path.join(out_dir, f)
        print(f'  {f} ({os.path.getsize(path)} bytes)')


if __name__ == '__main__':
    main()

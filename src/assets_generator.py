"""
PalmMotion Assets Generator Module
Generates high-definition meme-style golden accordion bodies and reference WAV samples
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.io import wavfile

def generate_accordion_bodies(assets_dir: str):
    """
    Generates left_body.png and right_body.png in the assets directory if they don't already exist.
    Styled after the classic golden/amber meme accordion shown in the user reference images.
    """
    os.makedirs(assets_dir, exist_ok=True)
    left_path = os.path.join(assets_dir, "left_body.png")
    right_path = os.path.join(assets_dir, "right_body.png")

    width, height = 180, 440

    # 1. Left Body (Bass side: golden metallic frame, dark grille, bass pearl buttons)
    if not os.path.exists(left_path):
        img_left = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_left = ImageDraw.Draw(img_left)

        # Outer golden metallic casing
        # Gradient effect from bright gold #F5D061 to deep amber #B8860B
        c_outer = (220, 175, 45, 255)
        c_inner = (180, 130, 20, 255)
        c_border = (110, 75, 10, 255)
        c_grille = (70, 25, 25, 255) # dark mahogany center like in reference

        # Body rounded rectangle
        draw_left.rounded_rectangle([10, 10, width - 10, height - 10], radius=24, fill=c_outer, outline=c_border, width=4)
        draw_left.rounded_rectangle([18, 18, width - 18, height - 18], radius=18, fill=c_inner)

        # Inner mahogany / dark red accent plate
        draw_left.rounded_rectangle([35, 35, width - 35, height - 35], radius=12, fill=c_grille, outline=(140, 95, 20, 255), width=3)

        # Draw bass buttons (several columns of shiny pearl buttons)
        cols = [55, 85, 115]
        for c_idx, cx in enumerate(cols):
            start_y = 65 + (c_idx % 2) * 16
            for cy in range(start_y, height - 60, 32):
                # Button shadow
                draw_left.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(40, 20, 10, 200))
                # Button body
                draw_left.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(245, 240, 220, 255), outline=(190, 160, 90, 255), width=2)
                # Pearl shine highlight
                draw_left.ellipse([cx - 4, cy - 4, cx - 1, cy - 1], fill=(255, 255, 255, 255))

        # Golden mounting trims and screws
        for ty in [24, height - 24]:
            for tx in [30, width // 2, width - 30]:
                draw_left.ellipse([tx - 5, ty - 5, tx + 5, ty + 5], fill=(255, 220, 100, 255), outline=c_border, width=1)

        img_left.save(left_path, "PNG")
        print(f"[Assets] Generated left body: {left_path}")

    # 2. Right Body (Treble side: golden casing + keyboard / treble register keys)
    if not os.path.exists(right_path):
        img_right = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw_right = ImageDraw.Draw(img_right)

        c_outer = (220, 175, 45, 255)
        c_inner = (180, 130, 20, 255)
        c_border = (110, 75, 10, 255)

        # Body rounded rectangle
        draw_right.rounded_rectangle([10, 10, width - 10, height - 10], radius=24, fill=c_outer, outline=c_border, width=4)
        draw_right.rounded_rectangle([18, 18, width - 18, height - 18], radius=18, fill=c_inner)

        # Treble grill & keyboard area
        # Left half has grill vents, right half has piano keys
        kb_x0 = 30
        kb_y0 = 30
        kb_x1 = width - 25
        kb_y1 = height - 30
        draw_right.rounded_rectangle([kb_x0, kb_y0, kb_x1, kb_y1], radius=10, fill=(30, 30, 35, 255), outline=c_border, width=3)

        # Draw piano white keys
        key_count = 18
        key_h = (kb_y1 - kb_y0) / key_count
        for i in range(key_count):
            ky0 = kb_y0 + i * key_h
            ky1 = ky0 + key_h
            # White key rectangle
            draw_right.rectangle([kb_x0 + 35, ky0 + 1, kb_x1 - 4, ky1 - 1], fill=(250, 248, 240, 255), outline=(160, 160, 160, 255), width=1)
            # Subtle gradient shadow on bottom of key
            draw_right.line([kb_x0 + 36, ky1 - 2, kb_x1 - 5, ky1 - 2], fill=(200, 195, 180, 255))

        # Draw black keys
        black_key_indices = {1, 2, 4, 5, 6, 8, 9, 11, 12, 13, 15, 16}
        for i in range(key_count):
            if (i % 7) in {0, 1, 3, 4, 5} and i < key_count - 1:
                ky0 = kb_y0 + (i + 0.65) * key_h
                ky1 = ky0 + key_h * 0.70
                draw_right.rectangle([kb_x0 + 35, ky0, kb_x0 + 75, ky1], fill=(25, 25, 25, 255), outline=(10, 10, 10, 255), width=1)
                # Black key top highlight
                draw_right.line([kb_x0 + 37, ky0 + 1, kb_x0 + 73, ky0 + 1], fill=(70, 70, 75, 255))

        # Golden Treble register buttons on the left strip
        for ry in range(kb_y0 + 20, kb_y1 - 20, 35):
            draw_right.rounded_rectangle([kb_x0 + 6, ry, kb_x0 + 26, ry + 22], radius=4, fill=(240, 200, 60, 255), outline=(120, 80, 10, 255), width=2)
            draw_right.ellipse([kb_x0 + 13, ry + 7, kb_x0 + 19, ry + 15], fill=(255, 255, 255, 230))

        # Corner gold studs
        for ty in [24, height - 24]:
            for tx in [28, width - 28]:
                draw_right.ellipse([tx - 5, ty - 5, tx + 5, ty + 5], fill=(255, 220, 100, 255), outline=c_border, width=1)

        img_right.save(right_path, "PNG")
        print(f"[Assets] Generated right body: {right_path}")


def generate_accordion_wav_samples(assets_dir: str, sample_rate: int = 44100):
    """
    Generates reference push_chord.wav and draw_chord.wav samples with authentic accordion reeds:
    - Fundamental + Odd/Even harmonics
    - Musette dual-reed slight detune (vibrato beat)
    - Smooth natural ADSR envelope
    """
    os.makedirs(assets_dir, exist_ok=True)
    draw_wav_path = os.path.join(assets_dir, "draw_chord.wav")
    push_wav_path = os.path.join(assets_dir, "push_chord.wav")

    duration = 3.0  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    def create_reed_note(freq, length):
        """Simulates an accordion reed pipe with dual wet tuning"""
        # Detune for musette (~2.2 Hz)
        f1 = freq
        f2 = freq + 2.2
        sub_f = freq * 0.5  # Sub-octave reed

        # Harmonics weights (typical accordion: strong fundamental, 2nd, 3rd, 4th, 5th)
        sig = 1.0 * np.sin(2 * np.pi * f1 * length)
        sig += 0.85 * np.sin(2 * np.pi * f2 * length)
        sig += 0.45 * np.sin(2 * np.pi * 2 * f1 * length)
        sig += 0.35 * np.sin(2 * np.pi * 3 * f1 * length)
        sig += 0.20 * np.sin(2 * np.pi * 4 * f1 * length)
        sig += 0.30 * np.sin(2 * np.pi * sub_f * length)
        return sig

    # 1. Draw Chord (Open / Expansion: C major / dominant 7th flavor: C4, E4, G4, B4)
    if not os.path.exists(draw_wav_path):
        notes_draw = [261.63, 329.63, 392.00, 493.88]
        chord_draw = np.zeros_like(t)
        for f in notes_draw:
            chord_draw += create_reed_note(f, t)
        
        # Normalize and apply loopable envelope
        attack = int(0.12 * sample_rate)
        release = int(0.20 * sample_rate)
        env = np.ones_like(t)
        env[:attack] = np.linspace(0, 1, attack)
        env[-release:] = np.linspace(1, 0, release)
        chord_draw = chord_draw * env
        chord_draw = chord_draw / (np.max(np.abs(chord_draw)) + 1e-6) * 0.88
        audio_int16 = (chord_draw * 32767).astype(np.int16)
        wavfile.write(draw_wav_path, sample_rate, audio_int16)
        print(f"[Assets] Generated draw sample: {draw_wav_path}")

    # 2. Push Chord (Close / Compression: G major / bass punch: G3, B3, D4, G4)
    if not os.path.exists(push_wav_path):
        notes_push = [196.00, 246.94, 293.66, 392.00]
        chord_push = np.zeros_like(t)
        for f in notes_push:
            chord_push += create_reed_note(f, t)
        
        attack = int(0.10 * sample_rate)
        release = int(0.20 * sample_rate)
        env = np.ones_like(t)
        env[:attack] = np.linspace(0, 1, attack)
        env[-release:] = np.linspace(1, 0, release)
        chord_push = chord_push * env
        chord_push = chord_push / (np.max(np.abs(chord_push)) + 1e-6) * 0.88
        audio_int16 = (chord_push * 32767).astype(np.int16)
        wavfile.write(push_wav_path, sample_rate, audio_int16)
        print(f"[Assets] Generated push sample: {push_wav_path}")

def ensure_assets(assets_dir: str):
    """Ensure all required assets are present; generate them if missing."""
    generate_accordion_bodies(assets_dir)
    generate_accordion_wav_samples(assets_dir)

if __name__ == "__main__":
    assets_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")
    ensure_assets(assets_folder)

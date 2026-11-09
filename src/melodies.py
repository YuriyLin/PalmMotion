"""
PalmMotion World Melody Library for Accordion
Curated classic accordion melodies with lead melody notes and rich bass chord accompaniment:
1. Bella Ciao (Italian Folk / Anti-fascist anthem)
2. La Vie En Rose (Édith Piaf French Chanson)
3. Korobeiniki (Russian Folk / Tetris Theme)
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class MelodyNote:
    name: str
    lead_freq: float
    bass_chords: List[float]
    duration_weight: float = 1.0

# Standard chord frequencies in comfortable accordion octaves
CHORD_AM = [110.0, 164.81, 220.0, 261.63]       # A2, E3, A3, C4
CHORD_DM = [146.83, 174.61, 220.0, 293.66]      # D3, F3, A3, D4
CHORD_E7 = [164.81, 207.65, 246.94, 293.66]     # E3, G#3, B3, D4
CHORD_C  = [130.81, 196.00, 261.63, 329.63]     # C3, G3, C4, E4
CHORD_G  = [98.00, 196.00, 246.94, 293.66]      # G2, G3, B3, D4
CHORD_G7 = [98.00, 174.61, 246.94, 293.66]      # G2, F3, B3, D4
CHORD_F  = [174.61, 220.00, 261.63, 349.23]     # F3, A3, C4, F4
CHORD_FM = [174.61, 207.65, 261.63, 349.23]     # F3, Ab3, C4, F4
CHORD_BB = [116.54, 174.61, 233.08, 293.66]     # Bb2, F3, Bb3, D4

MELODY_LIBRARY: Dict[str, Dict] = {
    "bella_ciao": {
        "title": "Bella Ciao",
        "description": "Italian Folk / Passionate minor march",
        "notes": [
            MelodyNote("E4", 329.63, CHORD_AM, 0.8),
            MelodyNote("A4", 440.00, CHORD_AM, 0.8),
            MelodyNote("B4", 493.88, CHORD_AM, 0.8),
            MelodyNote("C5", 523.25, CHORD_AM, 1.2),
            MelodyNote("A4", 440.00, CHORD_AM, 1.0),

            MelodyNote("E4", 329.63, CHORD_AM, 0.8),
            MelodyNote("A4", 440.00, CHORD_AM, 0.8),
            MelodyNote("B4", 493.88, CHORD_AM, 0.8),
            MelodyNote("C5", 523.25, CHORD_AM, 1.2),
            MelodyNote("A4", 440.00, CHORD_AM, 1.0),

            MelodyNote("E4", 329.63, CHORD_AM, 0.8),
            MelodyNote("A4", 440.00, CHORD_AM, 0.8),
            MelodyNote("B4", 493.88, CHORD_AM, 0.8),
            MelodyNote("C5", 523.25, CHORD_AM, 1.0),
            MelodyNote("B4", 493.88, CHORD_AM, 0.8),
            MelodyNote("A4", 440.00, CHORD_AM, 0.8),
            MelodyNote("C5", 523.25, CHORD_AM, 1.0),
            MelodyNote("B4", 493.88, CHORD_E7, 0.8),
            MelodyNote("A4", 440.00, CHORD_E7, 0.8),
            MelodyNote("E5", 659.25, CHORD_E7, 1.8),

            MelodyNote("E5", 659.25, CHORD_DM, 0.8),
            MelodyNote("D5", 587.33, CHORD_DM, 0.8),
            MelodyNote("E5", 659.25, CHORD_DM, 0.8),
            MelodyNote("F5", 698.46, CHORD_DM, 1.5),
            MelodyNote("F5", 698.46, CHORD_DM, 1.0),

            MelodyNote("E5", 659.25, CHORD_AM, 0.8),
            MelodyNote("D5", 587.33, CHORD_AM, 0.8),
            MelodyNote("C5", 523.25, CHORD_AM, 1.0),
            MelodyNote("B4", 493.88, CHORD_E7, 1.0),
            MelodyNote("E5", 659.25, CHORD_E7, 1.0),
            MelodyNote("C5", 523.25, CHORD_E7, 0.8),
            MelodyNote("B4", 493.88, CHORD_E7, 0.8),
            MelodyNote("A4", 440.00, CHORD_AM, 2.0),
        ]
    },
    "la_vie_en_rose": {
        "title": "La Vie En Rose",
        "description": "Édith Piaf Romantic French Chanson",
        "notes": [
            MelodyNote("G4", 392.00, CHORD_C, 1.0),
            MelodyNote("G4", 392.00, CHORD_C, 0.8),
            MelodyNote("G4", 392.00, CHORD_C, 0.8),
            MelodyNote("F#4", 369.99, CHORD_C, 0.8),
            MelodyNote("G4", 392.00, CHORD_C, 1.0),
            MelodyNote("A4", 440.00, CHORD_C, 1.2),
            MelodyNote("G4", 392.00, CHORD_C, 1.2),
            MelodyNote("E4", 329.63, CHORD_C, 2.0),

            MelodyNote("F4", 349.23, CHORD_G7, 1.0),
            MelodyNote("F4", 349.23, CHORD_G7, 0.8),
            MelodyNote("F4", 349.23, CHORD_G7, 0.8),
            MelodyNote("E4", 329.63, CHORD_G7, 0.8),
            MelodyNote("F4", 349.23, CHORD_G7, 1.0),
            MelodyNote("G4", 392.00, CHORD_G7, 1.2),
            MelodyNote("F4", 349.23, CHORD_G7, 1.2),
            MelodyNote("D4", 293.66, CHORD_G7, 2.0),

            MelodyNote("E4", 329.63, CHORD_C, 1.0),
            MelodyNote("E4", 329.63, CHORD_C, 0.8),
            MelodyNote("E4", 329.63, CHORD_C, 0.8),
            MelodyNote("D#4", 311.13, CHORD_C, 0.8),
            MelodyNote("E4", 329.63, CHORD_C, 1.0),
            MelodyNote("C5", 523.25, CHORD_AM, 1.5),
            MelodyNote("B4", 493.88, CHORD_AM, 1.0),
            MelodyNote("A4", 440.00, CHORD_DM, 1.0),
            MelodyNote("G4", 392.00, CHORD_G7, 1.5),
            MelodyNote("C4", 261.63, CHORD_C, 2.2),
        ]
    },
    "korobeiniki": {
        "title": "Korobeiniki (Tetris)",
        "description": "Russian Folk / Fast Polka",
        "notes": [
            MelodyNote("E5", 659.25, CHORD_E7, 1.2),
            MelodyNote("B4", 493.88, CHORD_E7, 0.8),
            MelodyNote("C5", 523.25, CHORD_AM, 0.8),
            MelodyNote("D5", 587.33, CHORD_DM, 1.2),
            MelodyNote("C5", 523.25, CHORD_AM, 0.8),
            MelodyNote("B4", 493.88, CHORD_E7, 0.8),
            MelodyNote("A4", 440.00, CHORD_AM, 1.5),
            MelodyNote("A4", 440.00, CHORD_AM, 0.8),
            MelodyNote("C5", 523.25, CHORD_AM, 0.8),
            MelodyNote("E5", 659.25, CHORD_AM, 1.2),
            MelodyNote("D5", 587.33, CHORD_DM, 0.8),
            MelodyNote("C5", 523.25, CHORD_AM, 0.8),
            MelodyNote("B4", 493.88, CHORD_E7, 1.5),
            MelodyNote("C5", 523.25, CHORD_AM, 0.8),
            MelodyNote("D5", 587.33, CHORD_DM, 1.2),
            MelodyNote("E5", 659.25, CHORD_E7, 1.2),
            MelodyNote("C5", 523.25, CHORD_AM, 1.0),
            MelodyNote("A4", 440.00, CHORD_AM, 1.0),
            MelodyNote("A4", 440.00, CHORD_AM, 1.8),
        ]
    }
}

DEFAULT_SONG = "bella_ciao"

def get_melody(song_key: str):
    return MELODY_LIBRARY.get(song_key, MELODY_LIBRARY[DEFAULT_SONG])

def list_melody_keys() -> List[Tuple[str, str]]:
    """Returns list of (key, title)."""
    return [(k, v["title"]) for k, v in MELODY_LIBRARY.items()]

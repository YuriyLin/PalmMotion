"""
PalmMotion Configuration Module
"""

from dataclasses import dataclass, field
import os

@dataclass
class TrackingConfig:
    min_detection_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    smooth_alpha: float = 0.35          # EMA factor for positions (0.0: super smooth, 1.0: raw)
    angle_alpha: float = 0.30           # EMA factor for rotation angle
    velocity_alpha: float = 0.25        # EMA factor for opening/closing speed
    tilt_alpha: float = 0.28            # EMA factor for individual wrist tilts
    occlusion_fallback: bool = True     # Use Pose elbows -> wrists if hands missing
    fade_duration_sec: float = 0.3      # Fade out time when hands are lost

@dataclass
class VisualConfig:
    bellows_folds: int = 8              # Number of bellows segments (peaks)
    body_scale: float = 1.0             # Scale multiplier for left & right accordion bodies
    max_bellows_width_ratio: float = 0.85 # Max stretch width relative to frame width
    min_bellows_width_px: int = 15      # Min width when fully compressed
    show_hud: bool = True               # Show speed/distance/chord HUD
    show_debug_landmarks: bool = False  # Draw hand & pose skeletons
    enable_curved_bellows: bool = True  # Bézier curved fan bellows + independent wrist rotation
    enable_particles: bool = True       # Floating musical notes (♪ ♫) and sparkle particles
    enable_comic_popups: bool = True    # Comic meme popups ("HUGE!", "TREMENDOUS!", "BRAVO!")
    show_meme_score: bool = True        # Meme score & performance ranking HUD (SS / S / A / B)
    show_waveform: bool = True          # Dynamic bottom audio waveform / frequency bars

@dataclass
class AudioConfig:
    sample_rate: int = 44100
    buffer_size: int = 1024
    sound_mode: str = "synth"           # "synth" or "wav"
    master_volume: float = 0.9          # Accordion volume
    video_volume: float = 0.8           # Original video audio volume
    velocity_deadzone: float = 0.03     # Minimum hand movement speed to produce sound
    velocity_max: float = 0.70          # Speed at which volume reaches maximum
    pitch_mode: str = "melody"          # "melody", "chords", "continuous", or "fixed"
    melody_song: str = "bella_ciao"     # "bella_ciao", "la_vie_en_rose", "korobeiniki"
    melody_step_distance: float = 0.08  # Normalized distance accumulated to step to next note
    base_freq: float = 220.0            # Base fundamental (A3)
    musette_detune: float = 2.5         # Hz detune for accordion vibrato/wetness
    custom_draw_wav: str = ""           # Path to user-provided draw WAV
    custom_push_wav: str = ""           # Path to user-provided push WAV

@dataclass
class AppConfig:
    video_source: str = "0"             # "0" for webcam, or video file path
    output_video_path: str = ""         # Non-empty to trigger export
    export_fps: float = 30.0
    export_layout: str = "standard"     # "standard", "side_by_side", or "vertical_9_16"
    export_gif_path: str = ""           # Non-empty to export animated GIF
    assets_dir: str = field(default_factory=lambda: os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets"))
    
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    visual: VisualConfig = field(default_factory=VisualConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)

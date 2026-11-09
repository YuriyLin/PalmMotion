"""
PalmMotion - Main Entry Point
Supports both Desktop GUI Control Center and Command-Line Interface (CLI).
"""

import sys
import argparse
import os

from src.config import AppConfig
from src.player import RealtimePlayer
from src.exporter import VideoExporter
from src.assets_generator import ensure_assets

def parse_args():
    parser = argparse.ArgumentParser(description="PalmMotion: Hand Gesture Accordion Synthesizer")
    parser.add_argument("--source", type=str, default=None,
                        help="Video source: '0', '1' for webcam, or path to a video file (.mp4, etc.)")
    parser.add_argument("--export", type=str, default=None,
                        help="Output MP4 path to process and export the video with mixed audio track")
    parser.add_argument("--layout", type=str, choices=["standard", "side_by_side", "vertical_9_16"], default="standard",
                        help="Export video layout: 'standard', 'side_by_side' (16:9 comparison), or 'vertical_9_16' (Shorts/Reels)")
    parser.add_argument("--gif", type=str, default=None,
                        help="Export animated GIF preview path (e.g. assets/demo.gif)")
    parser.add_argument("--sound-mode", type=str, choices=["synth", "wav"], default="synth",
                        help="Audio generation mode: 'synth' (built-in accordion reeds) or 'wav' (sample-based)")
    parser.add_argument("--pitch-mode", type=str, choices=["melody", "chords", "continuous", "fixed"], default="melody",
                        help="Pitch modulation mode: 'melody' (auto-following song), 'chords', 'continuous', or 'fixed'")
    parser.add_argument("--song", type=str, choices=["bella_ciao", "la_vie_en_rose", "korobeiniki"], default="bella_ciao",
                        help="Active melody song for auto-following mode")
    parser.add_argument("--volume", type=float, default=0.9,
                        help="Accordion master volume (0.0 to 1.5)")
    parser.add_argument("--speech-volume", type=float, default=0.8,
                        help="Original video speech volume (0.0 to 1.5)")
    parser.add_argument("--smooth", type=float, default=0.35,
                        help="EMA smoothing alpha (0.1 to 0.9)")
    parser.add_argument("--folds", type=int, default=8,
                        help="Number of bellows folds")
    parser.add_argument("--no-hud", action="store_true",
                        help="Hide the dynamic HUD overlay")
    parser.add_argument("--no-score", action="store_true",
                        help="Hide the meme score HUD card")
    parser.add_argument("--no-juice", action="store_true",
                        help="Disable particles and comic word popups")
    parser.add_argument("--no-curved", action="store_true",
                        help="Disable Bézier curved fan bellows")
    parser.add_argument("--no-waveform", action="store_true",
                        help="Disable dynamic audio waveform bars")
    parser.add_argument("--landmarks", action="store_true",
                        help="Display hand and pose debug landmark points")
    parser.add_argument("--cli", action="store_true",
                        help="Force CLI mode instead of launching the desktop GUI")
    return parser.parse_args()

def main():
    args = parse_args()

    config = AppConfig()
    ensure_assets(config.assets_dir)

    # Apply command line overrides
    if args.sound_mode:
        config.audio.sound_mode = args.sound_mode
    if args.pitch_mode:
        config.audio.pitch_mode = args.pitch_mode
    if args.song:
        config.audio.melody_song = args.song
    if args.layout:
        config.export_layout = args.layout
    if args.gif:
        config.export_gif_path = args.gif
    if args.volume is not None:
        config.audio.master_volume = args.volume
    if args.speech_volume is not None:
        config.audio.video_volume = args.speech_volume
    if args.smooth is not None:
        config.tracking.smooth_alpha = args.smooth
    if args.folds is not None:
        config.visual.bellows_folds = args.folds
    if args.no_hud:
        config.visual.show_hud = False
    if args.no_score:
        config.visual.show_meme_score = False
    if args.no_juice:
        config.visual.enable_particles = False
        config.visual.enable_comic_popups = False
    if args.no_curved:
        config.visual.enable_curved_bellows = False
    if args.no_waveform:
        config.visual.show_waveform = False
    if args.landmarks:
        config.visual.show_debug_landmarks = True

    # If --export is specified, run exporter directly
    if args.export:
        if not args.source:
            print("Error: --export requires an input --source video file.")
            sys.exit(1)
        exporter = VideoExporter(config)
        print(f"Starting batch export from '{args.source}' to '{args.export}' (Layout: {config.export_layout})...")
        success = exporter.process_and_export(
            input_video_path=args.source,
            output_video_path=args.export,
            progress_cb=lambda c, t, p: print(f"Progress: {c}/{t} ({p:.1f}%)", end="\r")
        )
        print("\nExport completed successfully!" if success else "\nExport failed!")
        return

    # If --source or --cli is provided, run interactive player in CLI mode
    if args.source is not None or args.cli:
        if args.source is not None:
            config.video_source = args.source
        player = RealtimePlayer(config)
        player.run()
        return

    # Default: Launch Desktop GUI Control Center
    try:
        from src.gui import launch_gui
        launch_gui(config)
    except Exception as e:
        print(f"Could not initialize GUI ({e}). Falling back to CLI mode...")
        player = RealtimePlayer(config)
        player.run()

if __name__ == "__main__":
    main()

"""
PalmMotion End-to-End Pipeline Verification Test
Verifies:
1. Synthetic speech video generation with opening/closing hands
2. Audio Engine World Melody auto-following & Musette reed synthesis
3. Bézier curved fan bellows, juice particles, and comic word popups
4. Multi-layout MP4 export: 'standard', 'side_by_side', 'vertical_9_16'
5. Optimized palette GIF export
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import cv2
import numpy as np
from scipy.io import wavfile
import imageio_ffmpeg
import subprocess

from src.config import AppConfig
from src.tracker import AccordionTracker
from src.renderer import AccordionRenderer
from src.audio_engine import AccordionAudioEngine
from src.exporter import VideoExporter
from src.assets_generator import ensure_assets
from src.melodies import MELODY_LIBRARY

def create_synthetic_test_video(video_path: str, duration_sec: float = 2.5, fps: int = 30):
    """
    Creates a synthetic video featuring a speaker with moving hands and test speech tone.
    """
    os.makedirs(os.path.dirname(os.path.abspath(video_path)), exist_ok=True)
    w, h = 640, 480
    total_frames = int(duration_sec * fps)
    temp_raw_video = video_path + ".raw.mp4"
    temp_raw_audio = video_path + ".raw.wav"

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(temp_raw_video, fourcc, fps, (w, h))

    for i in range(total_frames):
        frame = np.ones((h, w, 3), dtype=np.uint8) * 30

        # Draw speaker head & podium
        cv2.circle(frame, (w // 2, 140), 50, (180, 160, 140), -1)
        cv2.rectangle(frame, (100, 320, w - 100, h), (40, 40, 50), -1)
        cv2.putText(frame, "TEST SPEECH RALLY", (180, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)

        # Hands oscillating horizontally
        t = (i / total_frames) * 2.0 * np.pi * 2.5
        spread = 80 + int(85 * (np.sin(t) + 1.0) * 0.5)

        lx = w // 2 - spread
        ly = 260 + int(15 * np.cos(t))
        cv2.circle(frame, (lx, ly), 24, (180, 195, 230), -1)

        rx = w // 2 + spread
        ry = 260 - int(15 * np.cos(t))
        cv2.circle(frame, (rx, ry), 24, (180, 195, 230), -1)

        writer.write(frame)
    writer.release()

    sr = 44100
    t_audio = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    carrier = np.sin(2 * np.pi * 220 * t_audio)
    modulator = 0.5 + 0.5 * np.sin(2 * np.pi * 3 * t_audio)
    speech_wave = (carrier * modulator * 0.6 * 32767).astype(np.int16)
    wavfile.write(temp_raw_audio, sr, speech_wave)

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        ffmpeg, "-y",
        "-i", temp_raw_video,
        "-i", temp_raw_audio,
        "-c:v", "libx264",
        "-c:a", "aac",
        video_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    if os.path.exists(temp_raw_video):
        os.remove(temp_raw_video)
    if os.path.exists(temp_raw_audio):
        os.remove(temp_raw_audio)

    print(f"[Test] Generated synthetic input video: {video_path}")

def run_e2e_tests():
    test_dir = os.path.join(PROJECT_ROOT, "tests", "data")
    os.makedirs(test_dir, exist_ok=True)
    input_video = os.path.join(test_dir, "sample_input.mp4")
    output_std = os.path.join(test_dir, "sample_output_standard.mp4")
    output_sbs = os.path.join(test_dir, "sample_output_sbs.mp4")
    output_v916 = os.path.join(test_dir, "sample_output_916.mp4")
    output_gif = os.path.join(test_dir, "sample_preview.gif")

    create_synthetic_test_video(input_video, duration_sec=2.0)

    config = AppConfig()
    ensure_assets(config.assets_dir)

    print("\n--- Testing 1: Audio Engine & Melody Library ---")
    audio = AccordionAudioEngine(config.audio, config.assets_dir)
    assert len(MELODY_LIBRARY) == 3, "Expected 3 world melodies in library!"
    for key, info in MELODY_LIBRARY.items():
        assert len(info["notes"]) > 5, f"Song {key} has too few notes!"
    print(f"Verified 3 classic melodies: {[v['title'] for v in MELODY_LIBRARY.values()]}")
    audio.close()

    print("\n--- Testing 2: Standard Layout MP4 Export with World Melody ---")
    config.export_layout = "standard"
    config.audio.pitch_mode = "melody"
    config.audio.melody_song = "bella_ciao"
    config.visual.enable_curved_bellows = True
    config.visual.enable_particles = True
    config.visual.enable_comic_popups = True
    config.visual.show_waveform = True
    config.visual.show_meme_score = True

    exporter = VideoExporter(config)
    ok_std = exporter.process_and_export(input_video, output_std)
    assert ok_std, "Standard export failed!"
    assert os.path.exists(output_std) and os.path.getsize(output_std) > 10000
    print(f"Standard MP4 OK ({os.path.getsize(output_std)} bytes)")

    print("\n--- Testing 3: 16:9 Side-by-Side (Comparison) Export ---")
    config.export_layout = "side_by_side"
    config.audio.melody_song = "la_vie_en_rose"
    ok_sbs = exporter.process_and_export(input_video, output_sbs)
    assert ok_sbs, "Side-by-side export failed!"
    assert os.path.exists(output_sbs) and os.path.getsize(output_sbs) > 10000
    print(f"Side-by-Side MP4 OK ({os.path.getsize(output_sbs)} bytes)")

    print("\n--- Testing 4: 9:16 Vertical (Shorts/Reels) Export ---")
    config.export_layout = "vertical_9_16"
    config.audio.melody_song = "korobeiniki"
    ok_v = exporter.process_and_export(input_video, output_v916)
    assert ok_v, "Vertical 9:16 export failed!"
    assert os.path.exists(output_v916) and os.path.getsize(output_v916) > 10000
    print(f"Vertical 9:16 MP4 OK ({os.path.getsize(output_v916)} bytes)")

    print("\n--- Testing 5: GIF Export ---")
    ok_gif = exporter.export_gif(output_std, output_gif, fps=12, max_width=480)
    assert ok_gif, "GIF export failed!"
    assert os.path.exists(output_gif) and os.path.getsize(output_gif) > 5000
    print(f"Optimized Palette GIF OK ({os.path.getsize(output_gif)} bytes)")

    print("\n[SUCCESS] ALL PIPELINE TESTS PASSED SUCCESSFULLY!\n")

if __name__ == "__main__":
    run_e2e_tests()

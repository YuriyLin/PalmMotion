"""
PalmMotion Interactive Player Module
Handles real-time webcam and video file playback, live accordion tracking,
melody auto-following audio, synchronized background video speech mixing, and OpenCV display.
"""

import time
import cv2
import numpy as np
from typing import Optional, Callable
from .config import AppConfig
from .tracker import AccordionTracker
from .renderer import AccordionRenderer
from .audio_engine import AccordionAudioEngine

class RealtimePlayer:
    def __init__(self, config: AppConfig):
        self.config = config
        self.is_running = False
        self.is_paused = False
        self.tracker = AccordionTracker(config.tracking)
        self.renderer = AccordionRenderer(config.visual, config.assets_dir)
        self.audio_engine = AccordionAudioEngine(config.audio, config.assets_dir)

    def run(self, status_cb: Optional[Callable[[str], None]] = None):
        """
        Main interactive loop. Reads frames from camera or video, processes and renders.
        """
        source = self.config.video_source
        is_camera = source.isdigit() or (isinstance(source, int))
        cam_id = int(source) if is_camera else 0

        if is_camera:
            cap = cv2.VideoCapture(cam_id, cv2.CAP_DSHOW)
            if not cap.isOpened():
                cap = cv2.VideoCapture(cam_id)
        else:
            cap = cv2.VideoCapture(source)
            # Pre-load synchronized speech audio from the video file
            self.audio_engine.load_background_video_audio(source)

        if not cap.isOpened():
            msg = f"Failed to open video source: {source}"
            print(f"[Player] {msg}")
            if status_cb:
                status_cb(msg)
            return

        window_name = "PalmMotion - Interactive Accordion Preview"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, 1024, 640)

        self.is_running = True
        self.is_paused = False
        fps_timer = time.time()
        frame_counter = 0
        current_fps = 0.0

        target_fps = cap.get(cv2.CAP_PROP_FPS)
        if target_fps <= 0 or target_fps != target_fps or is_camera:
            target_fps = 30.0
        frame_delay = 1.0 / target_fps

        print(f"[Player] Started playback (source: {source}). Press 'Q' or 'ESC' to exit.")

        try:
            while self.is_running:
                loop_start = time.time()

                if not self.is_paused:
                    ret, frame = cap.read()
                    if not ret:
                        if not is_camera:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                        else:
                            break

                    if is_camera:
                        frame = cv2.flip(frame, 1)
                    else:
                        cur_msec = cap.get(cv2.CAP_PROP_POS_MSEC)
                        self.audio_engine.sync_video_time(cur_msec / 1000.0, False)

                    frame_counter += 1
                    now = time.time()
                    if now - fps_timer >= 0.5:
                        current_fps = frame_counter / (now - fps_timer)
                        frame_counter = 0
                        fps_timer = now

                    # 1. Hand / Pose tracking
                    motion = self.tracker.process_frame(frame)

                    # 2. Update real-time audio synthesizer
                    self.audio_engine.update_motion(motion)

                    # 3. Render visual accordion, juice particles, popups & HUD
                    rendered_frame = self.renderer.render(
                        frame,
                        motion,
                        self.audio_engine.current_chord_name,
                        current_fps,
                        self.audio_engine.current_audio_level,
                        self.audio_engine.waveform_bins
                    )

                    cv2.imshow(window_name, rendered_frame)
                else:
                    self.audio_engine.sync_video_time(0.0, True)

                # Process keyboard interactions
                wait_time_ms = 1 if is_camera else max(1, int((frame_delay - (time.time() - loop_start)) * 1000))
                key = cv2.waitKey(wait_time_ms) & 0xFF

                if key in (27, ord('q'), ord('Q')): # ESC or Q
                    break
                elif key == 32: # SPACE: Pause / Resume
                    self.is_paused = not self.is_paused
                elif key in (ord('h'), ord('H')): # H: Toggle HUD
                    self.config.visual.show_hud = not self.config.visual.show_hud
                elif key in (ord('l'), ord('L')): # L: Toggle Debug Landmarks
                    self.config.visual.show_debug_landmarks = not self.config.visual.show_debug_landmarks
                elif key in (ord('r'), ord('R')): # R: Reset tracking filters & meme score
                    self.tracker.reset()
                elif key in (ord('m'), ord('M')): # M: Toggle Mute
                    if self.config.audio.master_volume > 0.0:
                        self.prev_vol = self.config.audio.master_volume
                        self.config.audio.master_volume = 0.0
                    else:
                        self.config.audio.master_volume = getattr(self, "prev_vol", 0.9)
                elif key in (ord('s'), ord('S')): # S: Toggle Synth vs WAV
                    self.config.audio.sound_mode = "wav" if self.config.audio.sound_mode == "synth" else "synth"
                elif key in (ord('n'), ord('N')): # N: Next Melody Song
                    new_song = self.audio_engine.next_melody_song()
                    print(f"[Player] Switched song to: {new_song}")
                elif key in (ord('p'), ord('P')): # P: Cycle Pitch Mode
                    modes = ["melody", "chords", "continuous", "fixed"]
                    try:
                        idx = modes.index(self.config.audio.pitch_mode)
                    except ValueError:
                        idx = 0
                    self.config.audio.pitch_mode = modes[(idx + 1) % len(modes)]
                    print(f"[Player] Pitch mode set to: {self.config.audio.pitch_mode}")
                elif key in (ord('j'), ord('J')): # J: Toggle Juice (particles + comic popups)
                    self.config.visual.enable_particles = not self.config.visual.enable_particles
                    self.config.visual.enable_comic_popups = not self.config.visual.enable_comic_popups
                    print(f"[Player] Visual juice: {self.config.visual.enable_particles}")
                elif key in (ord('c'), ord('C')): # C: Toggle Curved Bellows
                    self.config.visual.enable_curved_bellows = not self.config.visual.enable_curved_bellows
                    print(f"[Player] Curved bellows: {self.config.visual.enable_curved_bellows}")
                elif key in (ord('w'), ord('W')): # W: Toggle Waveform Bars
                    self.config.visual.show_waveform = not self.config.visual.show_waveform

        finally:
            self.is_running = False
            cap.release()
            cv2.destroyAllWindows()
            self.audio_engine.close()
            print("[Player] Playback finished and resources released.")

    def stop(self):
        self.is_running = False

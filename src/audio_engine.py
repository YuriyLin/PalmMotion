"""
PalmMotion Audio Engine
Real-time accordion reed synthesis, WAV sample playback, world melody auto-following,
synchronized background video speech mixing, and live audio energy analysis.
"""

import io
import math
import os
import subprocess
import threading
import time
import numpy as np
from typing import Optional, List, Tuple
from scipy.io import wavfile
import imageio_ffmpeg
from .config import AudioConfig
from .tracker import HandMotionState
from .melodies import get_melody, list_melody_keys, MELODY_LIBRARY

try:
    import sounddevice as sd
    HAS_SOUNDDEVICE = True
except Exception:
    HAS_SOUNDDEVICE = False


# Fallback chord frequencies table (Hz) for chord mode:
DRAW_CHORDS = [
    ("C Maj (Low)", [130.81, 164.81, 196.00]),         # C3, E3, G3
    ("F Maj", [174.61, 220.00, 261.63]),              # F3, A3, C4
    ("G7 Dominant", [196.00, 246.94, 293.66, 349.23]),# G3, B3, D4, F4
    ("C Maj (High)", [261.63, 329.63, 392.00, 523.25]),# C4, E4, G4, C5
    ("E7 / Brilliant", [329.63, 415.30, 493.88, 587.33]) # E4, G#4, B4, D5
]

PUSH_CHORDS = [
    ("C Bass / Power", [130.81, 196.00, 261.63]),      # C3, G3, C4
    ("A Minor", [110.00, 164.81, 220.00, 261.63]),     # A2, E3, A3, C4
    ("F Bass Punch", [174.61, 220.00, 349.23]),        # F3, A3, F4
    ("G Major", [196.00, 246.94, 293.66, 392.00]),     # G3, B3, D4, G4
    ("C Maj Finale", [261.63, 329.63, 392.00, 523.25]) # C4, E4, G4, C5
]


class AccordionAudioEngine:
    def __init__(self, config: AudioConfig, assets_dir: str):
        self.config = config
        self.assets_dir = assets_dir
        self.sample_rate = config.sample_rate
        self.lock = threading.Lock()

        # Dynamic synthesis state
        self.target_volume = 0.0
        self.current_volume = 0.0
        self.active_frequencies: List[float] = [261.63, 329.63, 392.00]
        self.current_chord_name: str = "Bella Ciao"
        self.is_drawing_state = True
        self.continuous_pitch_mult = 1.0

        # Melody auto-following state machine
        self.melody_note_index = 0
        self.melody_travel_accum = 0.0
        self.last_tracked_dist: Optional[float] = None
        self.last_pump_draw: Optional[bool] = None
        self.last_step_time = 0.0

        # Phase oscillators for synth mode (stereo dual reed)
        self.max_oscillators = 8
        self.phases = np.zeros(self.max_oscillators, dtype=np.float64)
        self.phases_detuned = np.zeros(self.max_oscillators, dtype=np.float64)

        # WAV samples cache
        self.draw_wav_data: Optional[np.ndarray] = None
        self.push_wav_data: Optional[np.ndarray] = None
        self.wav_playhead = 0.0
        self.load_wav_samples()

        # Synchronized background video speech audio for real-time preview
        self.bg_audio_data: Optional[np.ndarray] = None
        self.bg_audio_sample_rate: int = 44100
        self.bg_audio_pos: int = 0
        self.bg_is_paused: bool = False

        # Live visualizer metrics (for waveform & HUD)
        self.current_audio_level: float = 0.0
        self.waveform_bins: np.ndarray = np.zeros(16, dtype=np.float32)

        # Recording buffer for video export
        self.recorded_chunks: List[np.ndarray] = []
        self.is_recording = False

        # Live audio stream
        self.stream = None
        self._init_stream()

    def load_wav_samples(self):
        """Loads default or custom WAV samples."""
        draw_path = self.config.custom_draw_wav or os.path.join(self.assets_dir, "draw_chord.wav")
        push_path = self.config.custom_push_wav or os.path.join(self.assets_dir, "push_chord.wav")

        try:
            if os.path.exists(draw_path):
                sr, d = wavfile.read(draw_path)
                if d.ndim > 1:
                    d = d.mean(axis=1)
                self.draw_wav_data = d.astype(np.float32) / 32768.0
            if os.path.exists(push_path):
                sr, d = wavfile.read(push_path)
                if d.ndim > 1:
                    d = d.mean(axis=1)
                self.push_wav_data = d.astype(np.float32) / 32768.0
        except Exception as e:
            print(f"[AudioEngine] Warning loading WAV samples: {e}")

    def load_background_video_audio(self, video_path: str):
        """
        Extracts speech audio from a video file using FFmpeg into memory for real-time preview playback.
        """
        if not video_path or not os.path.exists(video_path):
            return

        try:
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            cmd = [
                ffmpeg_exe, "-y",
                "-i", video_path,
                "-vn",
                "-f", "wav",
                "-ac", "2",
                "-ar", str(self.sample_rate),
                "pipe:1"
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if res.returncode == 0 and len(res.stdout) > 44:
                sr, data = wavfile.read(io.BytesIO(res.stdout))
                if data.ndim == 1:
                    data = np.column_stack((data, data))
                with self.lock:
                    self.bg_audio_data = data.astype(np.float32) / 32768.0
                    self.bg_audio_pos = 0
                    print(f"[AudioEngine] Loaded synchronized video audio ({len(self.bg_audio_data)/self.sample_rate:.1f}s).")
        except Exception as e:
            print(f"[AudioEngine] Note: video audio extraction skipped ({e}).")

    def sync_video_time(self, timestamp_sec: float, is_paused: bool):
        """Syncs the background video audio position with video player timestamp."""
        with self.lock:
            self.bg_is_paused = is_paused
            if self.bg_audio_data is not None and len(self.bg_audio_data) > 0:
                expected_pos = int(timestamp_sec * self.sample_rate)
                # Allow minor natural jitter, re-align if drifted by > 0.15s
                if abs(expected_pos - self.bg_audio_pos) > int(0.15 * self.sample_rate):
                    self.bg_audio_pos = expected_pos % len(self.bg_audio_data)

    def set_melody_song(self, song_key: str):
        """Changes active melody song."""
        with self.lock:
            if song_key in MELODY_LIBRARY:
                self.config.melody_song = song_key
                self.melody_note_index = 0
                self.melody_travel_accum = 0.0

    def next_melody_song(self) -> str:
        """Cycles to the next song in the library and returns the title."""
        with self.lock:
            keys = list(MELODY_LIBRARY.keys())
            try:
                cur_idx = keys.index(self.config.melody_song)
            except ValueError:
                cur_idx = 0
            next_key = keys[(cur_idx + 1) % len(keys)]
            self.config.melody_song = next_key
            self.melody_note_index = 0
            self.melody_travel_accum = 0.0
            return MELODY_LIBRARY[next_key]["title"]

    def _init_stream(self):
        """Initialize sounddevice output stream."""
        if not HAS_SOUNDDEVICE:
            print("[AudioEngine] sounddevice not available. Running in silent/offline mode.")
            return

        try:
            self.stream = sd.OutputStream(
                samplerate=self.sample_rate,
                channels=2,
                blocksize=self.config.buffer_size,
                callback=self._audio_callback
            )
            self.stream.start()
            print("[AudioEngine] Real-time audio stream started.")
        except Exception as e:
            print(f"[AudioEngine] Could not start sounddevice stream: {e}. Running in offline mode.")
            self.stream = None

    def start_recording(self):
        """Start accumulating audio samples for video export."""
        with self.lock:
            self.recorded_chunks = []
            self.is_recording = True

    def stop_recording(self) -> np.ndarray:
        """Stop accumulating and return full stereo float32 audio."""
        with self.lock:
            self.is_recording = False
            if not self.recorded_chunks:
                return np.zeros((0, 2), dtype=np.float32)
            return np.concatenate(self.recorded_chunks, axis=0)

    def update_motion(self, motion: HandMotionState):
        """
        Called on each video frame to calculate target volume, chords, and pitch.
        """
        with self.lock:
            if not motion.is_valid or motion.opacity <= 0.01:
                self.target_volume = 0.0
                return

            speed = abs(motion.velocity)
            deadzone = self.config.velocity_deadzone
            v_max = self.config.velocity_max

            if speed < deadzone:
                vol = 0.0
            else:
                vol = min(1.0, (speed - deadzone) / max(1e-4, v_max - deadzone))

            self.target_volume = vol * self.config.master_volume * motion.opacity

            # Push vs Draw state
            if motion.is_drawing:
                self.is_drawing_state = True
            elif motion.is_pushing:
                self.is_drawing_state = False

            cur_time = time.time()

            # Pitch mode processing
            if self.config.pitch_mode == "melody":
                song_info = get_melody(self.config.melody_song)
                notes_list = song_info["notes"]

                # Accumulate traveled distance
                if self.last_tracked_dist is not None:
                    dist_delta = abs(motion.norm_distance - self.last_tracked_dist)
                else:
                    dist_delta = 0.0
                self.last_tracked_dist = motion.norm_distance
                self.melody_travel_accum += dist_delta

                # Trigger next note on direction change or enough distance accumulated
                dir_changed = (self.last_pump_draw is not None and self.last_pump_draw != self.is_drawing_state)
                step_dist = getattr(self.config, "melody_step_distance", 0.08)

                if (dir_changed and (cur_time - self.last_step_time > 0.12)) or (self.melody_travel_accum >= step_dist):
                    self.melody_travel_accum = 0.0
                    self.last_step_time = cur_time
                    self.last_pump_draw = self.is_drawing_state
                    self.melody_note_index = (self.melody_note_index + 1) % len(notes_list)

                note = notes_list[self.melody_note_index]
                self.active_frequencies = [note.lead_freq] + note.bass_chords
                self.current_chord_name = f"{song_info['title']}: {note.name}"
                self.continuous_pitch_mult = 1.0

            elif self.config.pitch_mode == "continuous":
                norm_d = np.clip(motion.norm_distance, 0.15, 0.75)
                d_ratio = (norm_d - 0.15) / (0.75 - 0.15)
                self.continuous_pitch_mult = 0.8 + 1.2 * d_ratio
                self.active_frequencies = [self.config.base_freq * self.continuous_pitch_mult]
                self.current_chord_name = f"{int(self.active_frequencies[0])} Hz"

            elif self.config.pitch_mode == "chords":
                norm_d = np.clip(motion.norm_distance, 0.15, 0.75)
                d_ratio = (norm_d - 0.15) / (0.75 - 0.15)
                chords_list = DRAW_CHORDS if self.is_drawing_state else PUSH_CHORDS
                idx = int(np.clip(d_ratio * len(chords_list), 0, len(chords_list) - 1))
                name, freqs = chords_list[idx]
                self.current_chord_name = f"{name} ({'Draw' if self.is_drawing_state else 'Push'})"
                self.active_frequencies = freqs
                self.continuous_pitch_mult = 1.0

            else: # "fixed"
                self.active_frequencies = [261.63, 329.63, 392.00]
                self.current_chord_name = "C Maj (Fixed)"
                self.continuous_pitch_mult = 1.0

    def _render_synth_samples(self, num_samples: int) -> np.ndarray:
        """
        Synthesizes `num_samples` of authentic dual-reed accordion audio with bass reinforcement.
        """
        dt = 1.0 / self.sample_rate
        freqs = self.active_frequencies
        num_notes = min(len(freqs), self.max_oscillators)
        detune = self.config.musette_detune

        out = np.zeros(num_samples, dtype=np.float32)

        for i in range(num_notes):
            f1 = freqs[i]
            # Musette detune primarily applies to lead notes (higher frequency)
            f2 = f1 + (detune if f1 > 200.0 else detune * 0.5)

            phase_step1 = 2.0 * np.pi * f1 * dt
            phase_step2 = 2.0 * np.pi * f2 * dt

            t_vec1 = self.phases[i] + np.arange(num_samples) * phase_step1
            t_vec2 = self.phases_detuned[i] + np.arange(num_samples) * phase_step2

            # Lead note is index 0 (given slightly higher presence)
            weight = 1.1 if i == 0 else 0.75

            # Harmonics (fundamental + vibrato reed + octave + 3rd harmonic + sub-octave)
            note_sig = 0.50 * np.sin(t_vec1)
            note_sig += 0.42 * np.sin(t_vec2)
            note_sig += 0.28 * np.sin(t_vec1 * 2.0)
            note_sig += 0.18 * np.sin(t_vec1 * 3.0)
            note_sig += 0.25 * np.sin(t_vec1 * 0.5)

            out += note_sig * weight

            self.phases[i] = (t_vec1[-1] + phase_step1) % (2.0 * np.pi)
            self.phases_detuned[i] = (t_vec2[-1] + phase_step2) % (2.0 * np.pi)

        # Subtle air noise / reed breath
        noise = (np.random.rand(num_samples).astype(np.float32) - 0.5) * 0.035
        out += noise

        # Normalize across notes
        if num_notes > 0:
            out /= (num_notes * 1.0 + 0.3)

        return out

    def _render_wav_samples(self, num_samples: int) -> np.ndarray:
        """Loops WAV sample with pitch shift and volume scaling."""
        wav_buf = self.draw_wav_data if self.is_drawing_state else self.push_wav_data
        if wav_buf is None or len(wav_buf) < 100:
            return self._render_synth_samples(num_samples)

        wav_len = len(wav_buf)
        speed = max(0.5, min(2.0, self.continuous_pitch_mult))
        indices = (self.wav_playhead + np.arange(num_samples) * speed) % wav_len
        self.wav_playhead = (self.wav_playhead + num_samples * speed) % wav_len

        int_idx = indices.astype(int)
        return wav_buf[int_idx]

    def _audio_callback(self, outdata, frames, time_info, status):
        """sounddevice stream callback"""
        with self.lock:
            # Volume envelope smoothing
            alpha_vol = 0.14 if self.target_volume > self.current_volume else 0.05
            vol_curve = np.linspace(self.current_volume,
                                    self.current_volume + (self.target_volume - self.current_volume) * alpha_vol,
                                    frames, dtype=np.float32)
            self.current_volume = float(vol_curve[-1])

            if self.config.sound_mode == "wav":
                mono = self._render_wav_samples(frames)
            else:
                mono = self._render_synth_samples(frames)

            # Apply smoothed envelope
            mono *= vol_curve

            # Stereo split
            stereo = np.column_stack((mono * 0.95, mono * 0.95))

            # Mix background video audio if available and not paused
            if self.bg_audio_data is not None and not self.bg_is_paused and len(self.bg_audio_data) > 0:
                bg_len = len(self.bg_audio_data)
                end_pos = self.bg_audio_pos + frames
                if end_pos <= bg_len:
                    bg_chunk = self.bg_audio_data[self.bg_audio_pos : end_pos]
                    self.bg_audio_pos = end_pos % bg_len
                else:
                    part1 = self.bg_audio_data[self.bg_audio_pos :]
                    part2 = self.bg_audio_data[: end_pos % bg_len]
                    bg_chunk = np.concatenate((part1, part2), axis=0)
                    self.bg_audio_pos = len(part2)

                stereo += bg_chunk * self.config.video_volume

            outdata[:] = stereo

            # Update live visualizer metrics
            rms = float(np.sqrt(np.mean(stereo ** 2) + 1e-8))
            self.current_audio_level = 0.3 * rms + 0.7 * self.current_audio_level

            # 16-band waveform bins
            slice_w = max(1, frames // 16)
            bins = [float(np.sqrt(np.mean(mono[i * slice_w : (i + 1) * slice_w] ** 2) + 1e-8)) for i in range(16)]
            self.waveform_bins = np.array(bins, dtype=np.float32)

            if self.is_recording:
                self.recorded_chunks.append(stereo.copy())

    def render_frame_audio(self, duration_sec: float) -> np.ndarray:
        """
        Offline generation of accordion audio for a video frame of length `duration_sec`.
        Used during video export.
        """
        frames = int(self.sample_rate * duration_sec)
        if frames <= 0:
            return np.zeros((0, 2), dtype=np.float32)

        with self.lock:
            alpha_vol = 0.18 if self.target_volume > self.current_volume else 0.08
            vol_curve = np.linspace(self.current_volume,
                                    self.current_volume + (self.target_volume - self.current_volume) * alpha_vol,
                                    frames, dtype=np.float32)
            self.current_volume = float(vol_curve[-1])

            if self.config.sound_mode == "wav":
                mono = self._render_wav_samples(frames)
            else:
                mono = self._render_synth_samples(frames)

            mono *= vol_curve
            stereo = np.column_stack((mono * 0.95, mono * 0.95))

            rms = float(np.sqrt(np.mean(stereo ** 2) + 1e-8))
            self.current_audio_level = 0.3 * rms + 0.7 * self.current_audio_level

            slice_w = max(1, frames // 16)
            bins = [float(np.sqrt(np.mean(mono[i * slice_w : (i + 1) * slice_w] ** 2) + 1e-8)) for i in range(16)]
            self.waveform_bins = np.array(bins, dtype=np.float32)

            return stereo

    def close(self):
        """Clean up audio stream."""
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

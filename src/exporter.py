"""
PalmMotion Exporter Module
Processes video files frame-by-frame, renders accordion graphics, synthesizes synchronous audio,
and muxes original video speech + dynamic accordion sound using portable FFmpeg.
Supports standard layout, 16:9 side-by-side comparison, 9:16 vertical short-form video, and high-quality GIF export.
"""

import math
import os
import subprocess
import tempfile
import cv2
import numpy as np
import imageio_ffmpeg
from scipy.io import wavfile
from typing import Callable, Optional

from .config import AppConfig
from .tracker import AccordionTracker
from .renderer import AccordionRenderer
from .audio_engine import AccordionAudioEngine

class VideoExporter:
    def __init__(self, config: AppConfig):
        self.config = config
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def _compose_layout_frame(self, raw_frame: np.ndarray, rendered_frame: np.ndarray,
                              layout: str, target_w: int, target_h: int) -> np.ndarray:
        """Composes output frame based on chosen layout."""
        if layout == "side_by_side":
            h, w = raw_frame.shape[:2]
            left = raw_frame.copy()
            right = rendered_frame.copy()

            # Add aesthetic pill badges
            cv2.rectangle(left, (16, 16), (140, 48), (20, 20, 25), -1)
            cv2.rectangle(left, (16, 16), (140, 48), (80, 80, 90), 1)
            cv2.putText(left, "ORIGINAL", (26, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 2, cv2.LINE_AA)

            cv2.rectangle(right, (16, 16), (190, 48), (20, 20, 25), -1)
            cv2.rectangle(right, (16, 16), (190, 48), (245, 208, 97), 1)
            cv2.putText(right, "PALMMOTION AI", (26, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (245, 208, 97), 2, cv2.LINE_AA)

            composed = np.hstack([left, right])
            if (composed.shape[1], composed.shape[0]) != (target_w, target_h):
                composed = cv2.resize(composed, (target_w, target_h), interpolation=cv2.INTER_LINEAR)
            return composed

        elif layout == "vertical_9_16":
            # 9:16 layout (e.g. 720x1280) clean video-only comparison (no text)
            canvas = np.ones((target_h, target_w, 3), dtype=np.uint8) * 14

            half_h = target_h // 2
            raw_aspect = raw_frame.shape[1] / raw_frame.shape[0]

            # Fit original in upper half
            new_raw_w = target_w
            new_raw_h = int(new_raw_w / raw_aspect)
            if new_raw_h > half_h:
                new_raw_h = half_h
                new_raw_w = int(new_raw_h * raw_aspect)
            raw_resized = cv2.resize(raw_frame, (new_raw_w, new_raw_h), interpolation=cv2.INTER_LINEAR)
            y_raw_offset = (half_h - new_raw_h) // 2
            x_raw_offset = (target_w - new_raw_w) // 2
            canvas[y_raw_offset : y_raw_offset + new_raw_h, x_raw_offset : x_raw_offset + new_raw_w] = raw_resized

            # Fit accordion in lower half
            rend_aspect = rendered_frame.shape[1] / rendered_frame.shape[0]
            new_rend_w = target_w
            new_rend_h = int(new_rend_w / rend_aspect)
            if new_rend_h > half_h:
                new_rend_h = half_h
                new_rend_w = int(new_rend_h * rend_aspect)
            rend_resized = cv2.resize(rendered_frame, (new_rend_w, new_rend_h), interpolation=cv2.INTER_LINEAR)
            y_rend_offset = half_h + (half_h - new_rend_h) // 2
            x_rend_offset = (target_w - new_rend_w) // 2
            canvas[y_rend_offset : y_rend_offset + new_rend_h, x_rend_offset : x_rend_offset + new_rend_w] = rend_resized

            # Clean subtle divider line
            cv2.line(canvas, (0, half_h), (target_w, half_h), (45, 45, 55), 2)

            return canvas

        else: # "standard"
            return rendered_frame

    def process_and_export(self, input_video_path: str, output_video_path: str,
                           progress_cb: Optional[Callable[[int, int, float], None]] = None,
                           stop_flag_check: Optional[Callable[[], bool]] = None) -> bool:
        """
        Process the entire input video and export to output_video_path.
        Returns True if successful.
        """
        if not os.path.exists(input_video_path):
            raise FileNotFoundError(f"Input video not found: {input_video_path}")

        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            raise IOError(f"Cannot open video file: {input_video_path}")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or math_isnan(fps):
            fps = 30.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_dur = 1.0 / fps

        layout = getattr(self.config, "export_layout", "standard")
        if layout == "side_by_side":
            out_w = width * 2
            out_h = height
        elif layout == "vertical_9_16":
            out_w = 720
            out_h = 1280
        else:
            out_w = width
            out_h = height

        tracker = AccordionTracker(self.config.tracking)
        renderer = AccordionRenderer(self.config.visual, self.config.assets_dir)
        audio_engine = AccordionAudioEngine(self.config.audio, self.config.assets_dir)

        temp_dir = tempfile.mkdtemp(prefix="palmmotion_")
        temp_video = os.path.join(temp_dir, "temp_video.mp4")
        temp_audio = os.path.join(temp_dir, "temp_accordion.wav")

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(temp_video, fourcc, fps, (out_w, out_h))

        all_audio_chunks = []
        frame_idx = 0

        print(f"[Exporter] Processing {input_video_path} ({total_frames} frames, {out_w}x{out_h} [{layout}] @ {fps:.1f} fps)...")

        try:
            while True:
                if stop_flag_check and stop_flag_check():
                    print("[Exporter] Cancelled by user.")
                    cap.release()
                    writer.release()
                    return False

                ret, frame = cap.read()
                if not ret:
                    break

                raw_frame = frame.copy()
                timestamp = frame_idx * frame_dur

                motion = tracker.process_frame(frame, timestamp)
                audio_engine.update_motion(motion)

                # Synthesize audio for this frame duration
                frame_sound = audio_engine.render_frame_audio(frame_dur)
                all_audio_chunks.append(frame_sound)

                # Render accordion visually with juice & audio metrics
                rendered = renderer.render(
                    frame,
                    motion,
                    audio_engine.current_chord_name,
                    fps,
                    audio_engine.current_audio_level,
                    audio_engine.waveform_bins
                )

                composed = self._compose_layout_frame(raw_frame, rendered, layout, out_w, out_h)
                writer.write(composed)

                frame_idx += 1
                if progress_cb:
                    pct = (frame_idx / max(1, total_frames)) * 100.0
                    progress_cb(frame_idx, total_frames, min(100.0, pct))

        finally:
            cap.release()
            writer.release()
            audio_engine.close()

        # Save synthetic accordion audio to WAV
        if all_audio_chunks:
            full_audio = np.concatenate(all_audio_chunks, axis=0)
            full_audio_int16 = np.clip(full_audio * 32767.0, -32768, 32767).astype(np.int16)
            wavfile.write(temp_audio, self.config.audio.sample_rate, full_audio_int16)
        else:
            dummy = np.zeros((self.config.audio.sample_rate, 2), dtype=np.int16)
            wavfile.write(temp_audio, self.config.audio.sample_rate, dummy)

        # Mux with FFmpeg
        print(f"[Exporter] Multiplexing video and audio to {output_video_path}...")
        success = self._mux_audio_video(temp_video, temp_audio, input_video_path, output_video_path)

        # Optional GIF export
        if success and getattr(self.config, "export_gif_path", ""):
            gif_out = self.config.export_gif_path
            print(f"[Exporter] Generating preview GIF to {gif_out}...")
            self.export_gif(output_video_path, gif_out)

        # Clean up temporary files
        try:
            if os.path.exists(temp_video):
                os.remove(temp_video)
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
            os.rmdir(temp_dir)
        except Exception:
            pass

        return success

    def export_gif(self, input_video: str, output_gif: str, fps: int = 15, max_width: int = 540) -> bool:
        """
        Converts video to high-quality optimized palette GIF for README.md.
        """
        try:
            out_dir = os.path.dirname(os.path.abspath(output_gif))
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)

            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", input_video,
                "-vf", f"fps={fps},scale={max_width}:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
                output_gif
            ]
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            if res.returncode == 0:
                print(f"[Exporter] GIF export successful: {output_gif}")
                return True
            else:
                print(f"[Exporter] GIF export warning: {res.stderr}")
                return False
        except Exception as e:
            print(f"[Exporter] Could not generate GIF: {e}")
            return False

    def _has_audio_stream(self, video_path: str) -> bool:
        """Check if video file contains an audio stream using ffmpeg probe."""
        cmd = [self.ffmpeg_exe, "-i", video_path]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "Audio:" in res.stderr

    def _mux_audio_video(self, temp_video: str, synth_audio: str, orig_video: str, output_path: str) -> bool:
        """Combines temp_video + synth_audio (+ orig_video audio if available) into output_path."""
        has_orig_audio = self._has_audio_stream(orig_video)
        vol_accordion = self.config.audio.master_volume
        vol_orig = self.config.audio.video_volume

        out_dir = os.path.dirname(os.path.abspath(output_path))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        if has_orig_audio:
            filter_str = f"[1:a]volume={vol_orig:.2f}[a1];[2:a]volume={vol_accordion:.2f}[a2];[a1][a2]amix=inputs=2:duration=longest[aout]"
            cmd = [
                self.ffmpeg_exe,
                "-y",
                "-i", temp_video,
                "-i", orig_video,
                "-i", synth_audio,
                "-filter_complex", filter_str,
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "20",
                "-c:a", "aac",
                "-b:a", "192k",
                output_path
            ]
        else:
            cmd = [
                self.ffmpeg_exe,
                "-y",
                "-i", temp_video,
                "-i", synth_audio,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "20",
                "-c:a", "aac",
                "-b:a", "192k",
                output_path
            ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            print(f"[Exporter] FFmpeg error: {res.stderr}")
            return False
        return True

def math_isnan(val: float) -> bool:
    return val != val

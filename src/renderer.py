"""
PalmMotion Visual Rendering Engine
Renders segmented 3D zigzag accordion bellows with dynamic Bézier curvature,
independent wrist tilt rotation, floating musical note particles, comic meme popups,
performance ranking HUD, and dynamic bottom audio waveform bars.
"""

import math
import os
import random
import time
import cv2
import numpy as np
from typing import Tuple, List, Dict, Optional
from .config import VisualConfig
from .tracker import HandMotionState

COMIC_WORDS = ["HUGE!", "TREMENDOUS!", "BELIEVE ME!", "BRAVO!", "MAESTRO!", "VIRTUOSO!"]

class AccordionRenderer:
    def __init__(self, config: VisualConfig, assets_dir: str):
        self.config = config
        self.assets_dir = assets_dir

        self.left_body_img = None
        self.right_body_img = None
        self.load_assets()

        # Dynamic Juice Particle System
        self.particles: List[Dict] = []
        self.last_particle_time = 0.0

        # Comic Meme Popups System
        self.popups: List[Dict] = []
        self.last_popup_time = 0.0

    def load_assets(self):
        """Load accordion body transparent PNG images."""
        left_path = os.path.join(self.assets_dir, "left_body.png")
        right_path = os.path.join(self.assets_dir, "right_body.png")

        if os.path.exists(left_path):
            self.left_body_img = cv2.imread(left_path, cv2.IMREAD_UNCHANGED)
        if os.path.exists(right_path):
            self.right_body_img = cv2.imread(right_path, cv2.IMREAD_UNCHANGED)

    def _overlay_rgba(self, bg_bgr: np.ndarray, fg_rgba: np.ndarray, x: int, y: int, opacity: float = 1.0):
        """Alpha blends an RGBA image onto a BGR image at position (x, y) with clamping."""
        if opacity <= 0.001 or fg_rgba is None:
            return

        h_fg, w_fg = fg_rgba.shape[:2]
        h_bg, w_bg = bg_bgr.shape[:2]

        x1_fg = max(0, -x)
        y1_fg = max(0, -y)
        x2_fg = min(w_fg, w_bg - x)
        y2_fg = min(h_fg, h_bg - y)

        if x1_fg >= x2_fg or y1_fg >= y2_fg:
            return

        x1_bg = max(0, x)
        y1_bg = max(0, y)
        x2_bg = x1_bg + (x2_fg - x1_fg)
        y2_bg = y1_bg + (y2_fg - y1_fg)

        crop_fg = fg_rgba[y1_fg:y2_fg, x1_fg:x2_fg]
        crop_bg = bg_bgr[y1_bg:y2_bg, x1_bg:x2_bg]

        alpha = (crop_fg[:, :, 3].astype(np.float32) / 255.0) * opacity
        alpha = alpha[:, :, np.newaxis]

        fg_rgb = crop_fg[:, :, :3].astype(np.float32)
        bg_rgb = crop_bg.astype(np.float32)

        blended = fg_rgb * alpha + bg_rgb * (1.0 - alpha)
        bg_bgr[y1_bg:y2_bg, x1_bg:x2_bg] = np.clip(blended, 0, 255).astype(np.uint8)

    def _draw_rotated_body(self, frame: np.ndarray, body_rgba: np.ndarray, center: Tuple[float, float],
                           angle_rad: float, target_height: float, opacity: float):
        """Scales and rotates an accordion body and blends it onto the frame at `center`."""
        if body_rgba is None or opacity <= 0.01:
            return

        orig_h, orig_w = body_rgba.shape[:2]
        scale = target_height / max(orig_h, 1)
        new_w = max(4, int(orig_w * scale))
        new_h = max(4, int(orig_h * scale))

        resized = cv2.resize(body_rgba, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

        angle_deg = math.degrees(angle_rad)
        rot_mat = cv2.getRotationMatrix2D((new_w / 2.0, new_h / 2.0), -angle_deg, 1.0)

        cos_val = abs(rot_mat[0, 0])
        sin_val = abs(rot_mat[0, 1])
        bound_w = int((new_h * sin_val) + (new_w * cos_val))
        bound_h = int((new_h * cos_val) + (new_w * sin_val))

        rot_mat[0, 2] += (bound_w / 2.0) - (new_w / 2.0)
        rot_mat[1, 2] += (bound_h / 2.0) - (new_h / 2.0)

        rotated = cv2.warpAffine(resized, rot_mat, (bound_w, bound_h),
                                 flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT,
                                 borderValue=(0, 0, 0, 0))

        top_left_x = int(center[0] - bound_w / 2.0)
        top_left_y = int(center[1] - bound_h / 2.0)

        self._overlay_rgba(frame, rotated, top_left_x, top_left_y, opacity)

    def _render_segmented_bellows(self, frame: np.ndarray,
                                  p_left: Tuple[float, float],
                                  p_right: Tuple[float, float],
                                  u_vec: np.ndarray,
                                  n_vec: np.ndarray,
                                  bellows_len: float,
                                  bellows_height: float,
                                  opacity: float,
                                  curved: bool = True):
        """
        Renders a segmented 3D zig-zag bellows between left and right bodies:
        - Quadratic Bézier curved fan arc
        - Folds with alternating shaded polygons and depth
        - Gold metallic rib borders & corner brackets
        """
        if bellows_len < 4 or opacity <= 0.01:
            return

        folds = max(4, self.config.bellows_folds)
        slices = folds * 2

        stretch = np.clip(bellows_len / (bellows_height * 2.2), 0.0, 1.0)
        protrude_amp = bellows_height * 0.07 * (1.2 - 0.7 * stretch)

        c_dark = np.array([20, 15, 60], dtype=np.float32)
        c_light = np.array([45, 30, 110], dtype=np.float32)
        c_gold_edge = (35, 175, 230)      # BGR gold for fold trims
        c_corner_silver = (210, 215, 220) # BGR silver/chrome corners

        half_h = bellows_height * 0.48
        overlay = frame.copy()

        # Compute Bézier control points
        p0 = np.array(p_left, dtype=np.float32)
        p2 = np.array(p_right, dtype=np.float32)

        # Sag / arch offset along normal vector
        # Negative normal pulls the arc downward in world coordinates (natural gravity/fan sag)
        arc_sag = (bellows_len * 0.12 * stretch) if curved else 0.0
        p1 = 0.5 * (p0 + p2) - n_vec * arc_sag

        pts_top = []
        pts_bot = []

        for i in range(slices + 1):
            t = i / slices

            # Quadratic Bézier: B(t) = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
            center_i = (1.0 - t)**2 * p0 + 2.0 * (1.0 - t) * t * p1 + (t**2) * p2

            # Local tangent B'(t) = 2(1-t)(P1 - P0) + 2t(P2 - P1)
            tangent = 2.0 * (1.0 - t) * (p1 - p0) + 2.0 * t * (p2 - p1)
            tangent_len = np.linalg.norm(tangent)
            if tangent_len > 1e-4:
                local_u = tangent / tangent_len
                local_n = np.array([-local_u[1], local_u[0]])
            else:
                local_n = n_vec

            is_peak = (i % 2 == 1)
            offset = protrude_amp if is_peak else -protrude_amp

            top_i = center_i + local_n * (half_h + offset)
            bot_i = center_i - local_n * (half_h + offset)

            pts_top.append(top_i)
            pts_bot.append(bot_i)

        # Draw each facet polygon
        for i in range(slices):
            poly = np.array([
                pts_top[i],
                pts_top[i + 1],
                pts_bot[i + 1],
                pts_bot[i]
            ], dtype=np.int32)

            light_mult = 1.0 + 0.35 * (1.0 - stretch) if (i % 2 == 0) else 0.75 - 0.25 * (1.0 - stretch)
            base_col = c_light if (i % 2 == 0) else c_dark
            poly_color = np.clip(base_col * light_mult, 0, 255).astype(np.uint8).tolist()

            cv2.fillConvexPoly(overlay, poly, poly_color, lineType=cv2.LINE_AA)

            pt_t1 = tuple(pts_top[i + 1].astype(int))
            pt_b1 = tuple(pts_bot[i + 1].astype(int))
            cv2.line(overlay, pt_t1, pt_b1, c_gold_edge, 1, lineType=cv2.LINE_AA)

            if i % 2 == 1:
                t_peak = pts_top[i].astype(int)
                b_peak = pts_bot[i].astype(int)
                cv2.circle(overlay, (t_peak[0], t_peak[1]), 3, c_corner_silver, -1, lineType=cv2.LINE_AA)
                cv2.circle(overlay, (b_peak[0], b_peak[1]), 3, c_corner_silver, -1, lineType=cv2.LINE_AA)

        top_curve = np.array(pts_top, dtype=np.int32).reshape((-1, 1, 2))
        bot_curve = np.array(pts_bot, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(overlay, [top_curve], isClosed=False, color=(20, 140, 210), thickness=2, lineType=cv2.LINE_AA)
        cv2.polylines(overlay, [bot_curve], isClosed=False, color=(20, 140, 210), thickness=2, lineType=cv2.LINE_AA)

        cv2.addWeighted(overlay, opacity, frame, 1.0 - opacity, 0, frame)

    def _spawn_particles(self, p_left: Tuple[float, float], p_right: Tuple[float, float], speed: float):
        """Spawns musical note and sparkle particles along the accordion bellows."""
        cur_time = time.time()
        if cur_time - self.last_particle_time < 0.08:
            return
        self.last_particle_time = cur_time

        count = random.randint(1, 3)
        for _ in range(count):
            t = random.uniform(0.1, 0.9)
            x = p_left[0] + (p_right[0] - p_left[0]) * t + random.uniform(-10, 10)
            y = p_left[1] + (p_right[1] - p_left[1]) * t + random.uniform(-25, 25)

            p_type = random.choice(["note8", "note16", "star"])
            p_color = random.choice([
                (40, 215, 255),   # Golden yellow
                (255, 180, 50),   # Cyan
                (180, 100, 255),  # Violet
                (60, 255, 120),   # Lime green
            ])

            self.particles.append({
                "x": x,
                "y": y,
                "vx": random.uniform(-1.5, 1.5),
                "vy": random.uniform(-3.5, -1.0) - speed * 2.0,
                "type": p_type,
                "color": p_color,
                "life": 1.0,
                "decay": random.uniform(0.025, 0.05),
                "scale": random.uniform(0.8, 1.3)
            })

    def _update_and_draw_particles(self, frame: np.ndarray):
        """Updates and renders vector musical notes & sparkles onto `frame`."""
        alive_particles = []
        for p in self.particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= p["decay"]

            if p["life"] <= 0.05:
                continue

            alive_particles.append(p)
            alpha = min(1.0, p["life"] * 1.5)
            x, y = int(p["x"]), int(p["y"])
            col = tuple(int(c * alpha) for c in p["color"])
            s = p["scale"]

            if p["type"] == "note8": # Eighth note ♪
                # Note head
                cv2.ellipse(frame, (x, y), (int(5 * s), int(4 * s)), -20, 0, 360, col, -1, lineType=cv2.LINE_AA)
                # Stem
                stem_top = (x + int(4 * s), y - int(14 * s))
                cv2.line(frame, (x + int(4 * s), y), stem_top, col, max(1, int(2 * s)), lineType=cv2.LINE_AA)
                # Flag
                cv2.line(frame, stem_top, (stem_top[0] + int(5 * s), stem_top[1] + int(4 * s)), col, max(1, int(2 * s)), lineType=cv2.LINE_AA)

            elif p["type"] == "note16": # Beamed pair ♫
                # Left head & stem
                cv2.ellipse(frame, (x - int(5 * s), y), (int(4 * s), int(3 * s)), -20, 0, 360, col, -1, lineType=cv2.LINE_AA)
                cv2.line(frame, (x - int(2 * s), y), (x - int(2 * s), y - int(12 * s)), col, max(1, int(1.5 * s)), lineType=cv2.LINE_AA)
                # Right head & stem
                cv2.ellipse(frame, (x + int(6 * s), y - int(2 * s)), (int(4 * s), int(3 * s)), -20, 0, 360, col, -1, lineType=cv2.LINE_AA)
                cv2.line(frame, (x + int(9 * s), y - int(2 * s)), (x + int(9 * s), y - int(14 * s)), col, max(1, int(1.5 * s)), lineType=cv2.LINE_AA)
                # Beam
                cv2.line(frame, (x - int(2 * s), y - int(12 * s)), (x + int(9 * s), y - int(14 * s)), col, max(1, int(2.5 * s)), lineType=cv2.LINE_AA)

            else: # Star / Sparkle
                rad = int(6 * s)
                cv2.line(frame, (x - rad, y), (x + rad, y), col, max(1, int(1.5 * s)), lineType=cv2.LINE_AA)
                cv2.line(frame, (x, y - rad), (x, y + rad), col, max(1, int(1.5 * s)), lineType=cv2.LINE_AA)
                cv2.circle(frame, (x, y), max(1, int(2 * s)), (255, 255, 255), -1, lineType=cv2.LINE_AA)

        self.particles = alive_particles

    def _trigger_comic_popup(self, frame_w: int, frame_h: int, text: Optional[str] = None):
        """Triggers a comic word bubble popup."""
        cur_time = time.time()
        if cur_time - self.last_popup_time < 1.1:
            return
        self.last_popup_time = cur_time

        word = text if text else random.choice(COMIC_WORDS)
        x = random.randint(int(frame_w * 0.25), int(frame_w * 0.70))
        y = random.randint(int(frame_h * 0.18), int(frame_h * 0.38))

        self.popups.append({
            "text": word,
            "x": x,
            "y": y,
            "life": 1.0,
            "decay": 0.035,
            "scale": 0.2,
            "target_scale": random.uniform(1.0, 1.25)
        })

    def _update_and_draw_comic_popups(self, frame: np.ndarray):
        """Updates and renders comic starburst burst bubbles with bold text."""
        alive_popups = []
        for p in self.popups:
            p["life"] -= p["decay"]
            if p["life"] <= 0.02:
                continue

            # Pop-in scaling animation
            p["scale"] += (p["target_scale"] - p["scale"]) * 0.35
            p["y"] -= 0.6 # Float upward slightly

            alive_popups.append(p)
            alpha = min(1.0, p["life"] * 1.8)

            cx, cy = int(p["x"]), int(p["y"])
            s = p["scale"]
            text = p["text"]

            font = cv2.FONT_HERSHEY_DUPLEX
            font_scale = 1.0 * s
            thickness = max(2, int(3 * s))
            (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)

            # Generate starburst polygon around text
            bw = int((tw + 48) * 0.5)
            bh = int((th + 36) * 0.5)

            num_points = 14
            pts = []
            for i in range(num_points):
                angle = (i / num_points) * 2.0 * math.pi
                r_scale = 1.25 if (i % 2 == 0) else 0.85
                px = cx + math.cos(angle) * bw * r_scale
                py = cy + math.sin(angle) * bh * r_scale
                pts.append([px, py])

            poly_pts = np.array(pts, dtype=np.int32)

            overlay = frame.copy()
            # Golden yellow fill
            cv2.fillConvexPoly(overlay, poly_pts, (25, 215, 255), lineType=cv2.LINE_AA)
            # Fiery red border
            cv2.polylines(overlay, [poly_pts], isClosed=True, color=(15, 20, 225), thickness=max(2, int(4 * s)), lineType=cv2.LINE_AA)

            # Text shadow + white foreground
            tx = cx - tw // 2
            ty = cy + th // 2
            cv2.putText(overlay, text, (tx + 2, ty + 2), font, font_scale, (10, 10, 10), thickness + 2, lineType=cv2.LINE_AA)
            cv2.putText(overlay, text, (tx, ty), font, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)

            cv2.addWeighted(overlay, alpha, frame, 1.0 - alpha, 0, frame)

        self.popups = alive_popups

    def _draw_meme_score_hud(self, frame: np.ndarray, motion: HandMotionState):
        """Draws top-right translucent performance & meme score card."""
        h_frame, w_frame = frame.shape[:2]
        hud_w, hud_h = 240, 110
        x0 = w_frame - hud_w - 14
        y0 = 14

        overlay = frame.copy()
        cv2.rectangle(overlay, (x0, y0), (x0 + hud_w, y0 + hud_h), (20, 20, 26), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        cv2.rectangle(frame, (x0, y0), (x0 + hud_w, y0 + hud_h), (90, 80, 120), 1)

        # Title
        cv2.putText(frame, "MEME MASTERY", (x0 + 12, y0 + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (245, 208, 97), 2, cv2.LINE_AA)

        # Score & Pumps
        cv2.putText(frame, f"SCORE: {motion.meme_score:,}", (x0 + 12, y0 + 46), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (230, 230, 230), 1, cv2.LINE_AA)
        cv2.putText(frame, f"PUMPS: {motion.pump_count}", (x0 + 12, y0 + 68), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (200, 200, 210), 1, cv2.LINE_AA)

        span_pct = int(motion.max_span_ratio * 100)
        cv2.putText(frame, f"MAX SPAN: {span_pct}%", (x0 + 115, y0 + 68), cv2.FONT_HERSHEY_SIMPLEX, 0.46, (180, 220, 255), 1, cv2.LINE_AA)

        # Dynamic Rank Badge
        rank_text = motion.rank_label
        badge_col = (50, 220, 255) if "SS" in rank_text else ((80, 230, 120) if "S" in rank_text else (230, 180, 70))
        cv2.putText(frame, f"RANK: {rank_text}", (x0 + 12, y0 + 94), cv2.FONT_HERSHEY_SIMPLEX, 0.48, badge_col, 2, cv2.LINE_AA)

    def _draw_waveform_bars(self, frame: np.ndarray, audio_level: float, waveform_bins: Optional[np.ndarray]):
        """Draws dynamic audio waveform equalizer bars at the bottom center of the frame."""
        h_frame, w_frame = frame.shape[:2]
        cx = w_frame // 2
        base_y = h_frame - 18
        num_bars = 16
        bar_w = 7
        gap = 4
        total_w = num_bars * (bar_w + gap)
        start_x = cx - total_w // 2

        bins = waveform_bins if (waveform_bins is not None and len(waveform_bins) == num_bars) else np.ones(num_bars) * (audio_level + 0.05)

        for i in range(num_bars):
            bx = start_x + i * (bar_w + gap)
            val = float(bins[i])
            bar_h = int(np.clip(val * 90.0, 3, 55))

            # Mirror gradient color from center outwards
            dist_from_mid = abs(i - (num_bars - 1) / 2.0) / (num_bars / 2.0)
            col_b = int(255 * (1.0 - dist_from_mid * 0.4))
            col_g = int(190 * (1.0 - dist_from_mid * 0.3))
            col_r = int(50 + 180 * dist_from_mid)

            cv2.rectangle(frame, (bx, base_y - bar_h), (bx + bar_w, base_y), (col_b, col_g, col_r), -1)

    def render(self, frame: np.ndarray, motion: HandMotionState,
               chord_name: str = "", fps: float = 0.0,
               audio_level: float = 0.0, waveform_bins: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Renders the complete accordion, dynamic juice particles, comic popups, HUD, and waveform.
        """
        h_frame, w_frame = frame.shape[:2]

        if not motion.is_valid or motion.opacity <= 0.01:
            if self.config.show_hud:
                self._draw_hud(frame, motion, chord_name, fps)
            if getattr(self.config, "show_meme_score", True):
                self._draw_meme_score_hud(frame, motion)
            return frame

        p_l = np.array(motion.p_left)
        p_r = np.array(motion.p_right)

        dx = p_r[0] - p_l[0]
        dy = p_r[1] - p_l[1]
        dist = float(np.hypot(dx, dy))
        if dist < 1e-4:
            return frame

        u_vec = np.array([dx / dist, dy / dist])
        n_vec = np.array([-u_vec[1], u_vec[0]])

        accordion_height = h_frame * 0.42 * self.config.body_scale
        body_width = accordion_height * 0.40

        center_left = p_l - u_vec * (body_width * 0.15)
        center_right = p_r + u_vec * (body_width * 0.15)

        inner_left = p_l + u_vec * (body_width * 0.35)
        inner_right = p_r - u_vec * (body_width * 0.35)

        bellows_span = np.linalg.norm(inner_right - inner_left)
        if bellows_span < self.config.min_bellows_width_px:
            bellows_span = self.config.min_bellows_width_px
            mid_pt = 0.5 * (inner_left + inner_right)
            inner_left = mid_pt - u_vec * (bellows_span * 0.5)
            inner_right = mid_pt + u_vec * (bellows_span * 0.5)

        # 1. Render segmented Bézier curved fan bellows
        use_curved = getattr(self.config, "enable_curved_bellows", True)
        self._render_segmented_bellows(
            frame,
            inner_left,
            inner_right,
            u_vec,
            n_vec,
            bellows_span,
            accordion_height * 0.88,
            motion.opacity,
            curved=use_curved
        )

        # 2. Render Left Body & Right Body with independent wrist tilts
        if use_curved:
            # Blend overall chord angle with individual wrist tilt angles
            left_angle = motion.angle_rad + np.clip(math.sin(motion.left_hand_tilt - (-math.pi / 2.0)), -0.6, 0.6) * 0.45
            right_angle = motion.angle_rad + np.clip(math.sin(motion.right_hand_tilt - (-math.pi / 2.0)), -0.6, 0.6) * 0.45
        else:
            left_angle = motion.angle_rad
            right_angle = motion.angle_rad

        self._draw_rotated_body(
            frame,
            self.left_body_img,
            (center_left[0], center_left[1]),
            left_angle,
            accordion_height,
            motion.opacity
        )

        self._draw_rotated_body(
            frame,
            self.right_body_img,
            (center_right[0], center_right[1]),
            right_angle,
            accordion_height,
            motion.opacity
        )

        # 3. Dynamic Juice: Musical Note Particles
        if getattr(self.config, "enable_particles", True):
            speed = abs(motion.velocity)
            if speed > 0.08:
                self._spawn_particles(inner_left, inner_right, speed)
            self._update_and_draw_particles(frame)

        # 4. Comic Word Popups ("HUGE!", "TREMENDOUS!")
        if getattr(self.config, "enable_comic_popups", True):
            if motion.norm_distance > 0.62:
                self._trigger_comic_popup(w_frame, h_frame, "HUGE!")
            elif abs(motion.velocity) > 0.45:
                self._trigger_comic_popup(w_frame, h_frame, "TREMENDOUS!")
            self._update_and_draw_comic_popups(frame)

        # 5. Debug Landmarks
        if self.config.show_debug_landmarks:
            cv2.circle(frame, (int(p_l[0]), int(p_l[1])), 8, (0, 255, 255), -1)
            cv2.circle(frame, (int(p_r[0]), int(p_r[1])), 8, (0, 255, 255), -1)
            cv2.line(frame, (int(p_l[0]), int(p_l[1])), (int(p_r[0]), int(p_r[1])), (0, 200, 255), 2)

        # 6. Dynamic Audio Waveform
        if getattr(self.config, "show_waveform", True):
            self._draw_waveform_bars(frame, audio_level, waveform_bins)

        # 7. HUDs
        if self.config.show_hud:
            self._draw_hud(frame, motion, chord_name, fps)

        if getattr(self.config, "show_meme_score", True):
            self._draw_meme_score_hud(frame, motion)

        return frame

    def _draw_hud(self, frame: np.ndarray, motion: HandMotionState, chord_name: str, fps: float):
        """Draw aesthetic transparent HUD pill in top-left."""
        hud_w, hud_h = 320, 110
        overlay = frame.copy()
        cv2.rectangle(overlay, (14, 14), (14 + hud_w, 14 + hud_h), (20, 20, 25), -1)
        cv2.addWeighted(overlay, 0.72, frame, 0.28, 0, frame)
        cv2.rectangle(frame, (14, 14), (14 + hud_w, 14 + hud_h), (80, 80, 90), 1)

        # Status text & badge
        if motion.is_drawing:
            status_text = "STATUS: DRAW (拉開)"
            badge_color = (60, 220, 90) # Green
        elif motion.is_pushing:
            status_text = "STATUS: PUSH (壓縮)"
            badge_color = (40, 140, 255) # Orange
        elif motion.is_valid:
            status_text = "STATUS: HOLD (靜止)"
            badge_color = (200, 200, 200) # Gray
        else:
            status_text = "STATUS: SEARCHING (尋找雙手)"
            badge_color = (120, 120, 150)

        cv2.putText(frame, status_text, (26, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.55, badge_color, 2, cv2.LINE_AA)

        # Velocity bar
        cv2.putText(frame, "Speed:", (26, 64), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220, 220, 220), 1, cv2.LINE_AA)
        bar_x, bar_y, bar_w, bar_h = 80, 53, 140, 12
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 60), -1)
        speed_ratio = np.clip(abs(motion.velocity) / 0.6, 0.0, 1.0)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_w * speed_ratio), bar_y + bar_h), badge_color, -1)

        # Chord / Melody info
        chord_display = f"Music: {chord_name if chord_name else 'None'}"
        cv2.putText(frame, chord_display, (26, 92), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (255, 220, 120), 1, cv2.LINE_AA)

        # FPS indicator
        if fps > 0:
            fps_str = f"{fps:.1f} FPS"
            cv2.putText(frame, fps_str, (240, 92), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)

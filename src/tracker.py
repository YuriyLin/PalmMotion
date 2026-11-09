"""
PalmMotion Tracker Module
Hybrid hand tracking (MediaPipe Hands + Pose fallback), EMA smoothing, and motion kinematics.
Includes individual wrist tilt smoothing and dynamic Meme Score tracking.
"""

import math
import time
import cv2
import numpy as np
import mediapipe as mp
from dataclasses import dataclass
from typing import Optional, Tuple
from .config import TrackingConfig

@dataclass
class HandMotionState:
    is_valid: bool
    opacity: float                    # 0.0 ~ 1.0 for smooth fade-in/out
    p_left: Tuple[float, float]       # (x, y) in image coordinates (viewer left)
    p_right: Tuple[float, float]      # (x, y) in image coordinates (viewer right)
    distance: float                   # Distance in pixels
    norm_distance: float              # Distance normalized by frame width
    angle_rad: float                  # Angle of vector from left to right hand
    angle_deg: float
    velocity: float                   # Normalized velocity (d(norm_dist)/dt), positive=draw, negative=push
    is_drawing: bool
    is_pushing: bool
    left_hand_tilt: float = 0.0       # Local tilt angle of left hand (radians)
    right_hand_tilt: float = 0.0      # Local tilt angle of right hand (radians)
    pump_count: int = 0               # Accumulated accordion pumps (push/pull alternations)
    max_span_ratio: float = 0.0       # Maximum stretch ratio recorded (norm_dist)
    meme_score: int = 0               # Overall performance meme score
    rank_label: str = "C (Warming Up)"# Dynamic rank badge


class AccordionTracker:
    def __init__(self, config: TrackingConfig):
        self.config = config

        self.mp_hands = mp.solutions.hands
        self.hands_detector = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=self.config.min_detection_confidence,
            min_tracking_confidence=self.config.min_tracking_confidence
        )

        self.mp_pose = mp.solutions.pose
        self.pose_detector = self.mp_pose.Pose(
            static_image_mode=False,
            min_detection_confidence=self.config.min_detection_confidence,
            min_tracking_confidence=self.config.min_tracking_confidence
        )

        # Filter states
        self.smooth_p_left: Optional[np.ndarray] = None
        self.smooth_p_right: Optional[np.ndarray] = None
        self.smooth_angle_vec = np.array([1.0, 0.0])
        self.smooth_left_tilt_vec = np.array([0.0, 1.0])
        self.smooth_right_tilt_vec = np.array([0.0, 1.0])
        self.smooth_velocity = 0.0
        self.prev_norm_distance: Optional[float] = None
        self.prev_time: Optional[float] = None

        # Fade state
        self.current_opacity = 0.0
        self.last_detection_time = 0.0

        # Meme Score State
        self.pump_count = 0
        self.max_span_ratio = 0.0
        self.meme_score = 0.0
        self.prev_draw_state: Optional[bool] = None
        self.last_pump_time = 0.0

    def reset(self):
        """Reset temporal filter states and meme score."""
        self.smooth_p_left = None
        self.smooth_p_right = None
        self.smooth_angle_vec = np.array([1.0, 0.0])
        self.smooth_left_tilt_vec = np.array([0.0, 1.0])
        self.smooth_right_tilt_vec = np.array([0.0, 1.0])
        self.smooth_velocity = 0.0
        self.prev_norm_distance = None
        self.prev_time = None
        self.current_opacity = 0.0
        self.pump_count = 0
        self.max_span_ratio = 0.0
        self.meme_score = 0.0
        self.prev_draw_state = None
        self.last_pump_time = 0.0

    def process_frame(self, frame_bgr: np.ndarray, timestamp_sec: Optional[float] = None) -> HandMotionState:
        """
        Process a single BGR video frame and extract hand motion kinematics.
        """
        h, w = frame_bgr.shape[:2]
        cur_time = timestamp_sec if timestamp_sec is not None else time.time()
        dt = 0.033
        if self.prev_time is not None and cur_time > self.prev_time:
            dt = max(1e-4, cur_time - self.prev_time)
        self.prev_time = cur_time

        rgb_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

        # 1. Detect Hands
        hands_result = self.hands_detector.process(rgb_frame)
        candidate_hands = []

        if hands_result.multi_hand_landmarks:
            for hand_lms in hands_result.multi_hand_landmarks:
                pts = np.array([
                    [hand_lms.landmark[0].x * w, hand_lms.landmark[0].y * h],
                    [hand_lms.landmark[5].x * w, hand_lms.landmark[5].y * h],
                    [hand_lms.landmark[9].x * w, hand_lms.landmark[9].y * h],
                    [hand_lms.landmark[17].x * w, hand_lms.landmark[17].y * h]
                ])
                palm_center = np.mean(pts, axis=0)

                # Local hand tilt angle from wrist to middle MCP
                wrist = np.array([hand_lms.landmark[0].x * w, hand_lms.landmark[0].y * h])
                mid_mcp = np.array([hand_lms.landmark[9].x * w, hand_lms.landmark[9].y * h])
                tilt = math.atan2(mid_mcp[1] - wrist[1], mid_mcp[0] - wrist[0])

                candidate_hands.append({
                    "pos": palm_center,
                    "tilt": tilt,
                    "landmarks": hand_lms
                })

        p_left_raw = None
        p_right_raw = None
        left_tilt_raw = 0.0
        right_tilt_raw = 0.0

        if len(candidate_hands) >= 2:
            candidate_hands.sort(key=lambda hnd: hnd["pos"][0])
            p_left_raw = candidate_hands[0]["pos"]
            p_right_raw = candidate_hands[1]["pos"]
            left_tilt_raw = candidate_hands[0]["tilt"]
            right_tilt_raw = candidate_hands[1]["tilt"]

        elif len(candidate_hands) == 1 and self.config.occlusion_fallback:
            pose_result = self.pose_detector.process(rgb_frame)
            if pose_result.pose_landmarks:
                plms = pose_result.pose_landmarks.landmark
                wrist_pts = []
                for elbow_idx, wrist_idx in [(13, 15), (14, 16)]:
                    if plms[wrist_idx].visibility > 0.4 and plms[elbow_idx].visibility > 0.3:
                        ew = np.array([plms[wrist_idx].x * w, plms[wrist_idx].y * h])
                        ee = np.array([plms[elbow_idx].x * w, plms[elbow_idx].y * h])
                        extrap_palm = ew + 0.25 * (ew - ee)
                        tilt_arm = math.atan2(ew[1] - ee[1], ew[0] - ee[0])
                        wrist_pts.append((extrap_palm, tilt_arm))
                
                single_hand_pos = candidate_hands[0]["pos"]
                for wp, wtilt in wrist_pts:
                    if np.linalg.norm(wp - single_hand_pos) > 0.15 * w:
                        if wp[0] < single_hand_pos[0]:
                            p_left_raw = wp
                            p_right_raw = single_hand_pos
                            left_tilt_raw = wtilt
                            right_tilt_raw = candidate_hands[0]["tilt"]
                        else:
                            p_left_raw = single_hand_pos
                            p_right_raw = wp
                            left_tilt_raw = candidate_hands[0]["tilt"]
                            right_tilt_raw = wtilt
                        break

        elif len(candidate_hands) == 0 and self.config.occlusion_fallback:
            pose_result = self.pose_detector.process(rgb_frame)
            if pose_result.pose_landmarks:
                plms = pose_result.pose_landmarks.landmark
                pts = []
                for elbow_idx, wrist_idx in [(13, 15), (14, 16)]:
                    if plms[wrist_idx].visibility > 0.3 and plms[elbow_idx].visibility > 0.3:
                        ew = np.array([plms[wrist_idx].x * w, plms[wrist_idx].y * h])
                        ee = np.array([plms[elbow_idx].x * w, plms[elbow_idx].y * h])
                        extrap_palm = ew + 0.25 * (ew - ee)
                        tilt_arm = math.atan2(ew[1] - ee[1], ew[0] - ee[0])
                        pts.append((extrap_palm, tilt_arm))
                if len(pts) == 2:
                    pts.sort(key=lambda item: item[0][0])
                    p_left_raw = pts[0][0]
                    p_right_raw = pts[1][0]
                    left_tilt_raw = pts[0][1]
                    right_tilt_raw = pts[1][1]

        # 2. Update tracking state & Temporal Filtering
        is_detected = (p_left_raw is not None and p_right_raw is not None)
        alpha = self.config.smooth_alpha
        ang_alpha = self.config.angle_alpha
        vel_alpha = self.config.velocity_alpha
        tilt_alpha = getattr(self.config, "tilt_alpha", 0.28)

        if is_detected:
            self.last_detection_time = cur_time
            self.current_opacity = min(1.0, self.current_opacity + dt / 0.12)

            if self.smooth_p_left is None:
                self.smooth_p_left = p_left_raw.astype(float)
                self.smooth_p_right = p_right_raw.astype(float)
            else:
                self.smooth_p_left = alpha * p_left_raw + (1.0 - alpha) * self.smooth_p_left
                self.smooth_p_right = alpha * p_right_raw + (1.0 - alpha) * self.smooth_p_right

            # Angle smoothing via 2D vector
            dx = self.smooth_p_right[0] - self.smooth_p_left[0]
            dy = self.smooth_p_right[1] - self.smooth_p_left[1]
            raw_angle = math.atan2(dy, dx)
            cur_vec = np.array([math.cos(raw_angle), math.sin(raw_angle)])
            self.smooth_angle_vec = ang_alpha * cur_vec + (1.0 - ang_alpha) * self.smooth_angle_vec
            norm_ang = np.linalg.norm(self.smooth_angle_vec)
            if norm_ang > 1e-4:
                self.smooth_angle_vec /= norm_ang
            angle_rad = math.atan2(self.smooth_angle_vec[1], self.smooth_angle_vec[0])

            # Left & Right wrist tilt smoothing via 2D vectors
            vec_l = np.array([math.cos(left_tilt_raw), math.sin(left_tilt_raw)])
            vec_r = np.array([math.cos(right_tilt_raw), math.sin(right_tilt_raw)])
            self.smooth_left_tilt_vec = tilt_alpha * vec_l + (1.0 - tilt_alpha) * self.smooth_left_tilt_vec
            self.smooth_right_tilt_vec = tilt_alpha * vec_r + (1.0 - tilt_alpha) * self.smooth_right_tilt_vec
            n_l = np.linalg.norm(self.smooth_left_tilt_vec)
            n_r = np.linalg.norm(self.smooth_right_tilt_vec)
            if n_l > 1e-4:
                self.smooth_left_tilt_vec /= n_l
            if n_r > 1e-4:
                self.smooth_right_tilt_vec /= n_r
            smooth_left_tilt = math.atan2(self.smooth_left_tilt_vec[1], self.smooth_left_tilt_vec[0])
            smooth_right_tilt = math.atan2(self.smooth_right_tilt_vec[1], self.smooth_right_tilt_vec[0])

            dist_px = float(np.hypot(dx, dy))
            norm_dist = dist_px / max(w, 1)

            # Velocity computation
            if self.prev_norm_distance is not None:
                raw_vel = (norm_dist - self.prev_norm_distance) / dt
            else:
                raw_vel = 0.0
            self.prev_norm_distance = norm_dist

            self.smooth_velocity = vel_alpha * raw_vel + (1.0 - vel_alpha) * self.smooth_velocity

        else:
            fade_rate = dt / max(self.config.fade_duration_sec, 0.05)
            self.current_opacity = max(0.0, self.current_opacity - fade_rate)
            self.smooth_velocity *= 0.8
            if self.smooth_p_left is None:
                self.smooth_p_left = np.array([w * 0.35, h * 0.6])
                self.smooth_p_right = np.array([w * 0.65, h * 0.6])
            dx = self.smooth_p_right[0] - self.smooth_p_left[0]
            dy = self.smooth_p_right[1] - self.smooth_p_left[1]
            angle_rad = math.atan2(self.smooth_angle_vec[1], self.smooth_angle_vec[0])
            smooth_left_tilt = math.atan2(self.smooth_left_tilt_vec[1], self.smooth_left_tilt_vec[0])
            smooth_right_tilt = math.atan2(self.smooth_right_tilt_vec[1], self.smooth_right_tilt_vec[0])
            dist_px = float(np.hypot(dx, dy))
            norm_dist = dist_px / max(w, 1)

        is_valid = (self.current_opacity > 0.01)
        is_drawing = bool(self.smooth_velocity > 0.04)
        is_pushing = bool(self.smooth_velocity < -0.04)

        # 3. Update Meme Score & Performance Ranking
        if is_valid and (is_drawing or is_pushing):
            current_draw_state = is_drawing
            if self.prev_draw_state is not None and self.prev_draw_state != current_draw_state:
                if (cur_time - self.last_pump_time) > 0.12:
                    self.pump_count += 1
                    self.meme_score += 65.0  # Big bonus for clean pump reversal
                    self.last_pump_time = cur_time

            self.prev_draw_state = current_draw_state

            # Continuous motion accumulation
            speed = abs(self.smooth_velocity)
            self.meme_score += speed * 45.0 * dt * 30.0

            if norm_dist > self.max_span_ratio:
                self.max_span_ratio = norm_dist

            # Span bonus
            if norm_dist > 0.50:
                self.meme_score += (norm_dist - 0.50) * 80.0 * dt * 30.0

        # Rank calculation
        score_val = int(self.meme_score)
        if score_val < 300:
            rank = "C (Warming Up)"
        elif score_val < 900:
            rank = "B (Street Performer)"
        elif score_val < 2000:
            rank = "A (Maestro)"
        elif score_val < 4000:
            rank = "S (Virtuoso)"
        else:
            rank = "SS (TREMENDOUS!)"

        return HandMotionState(
            is_valid=is_valid,
            opacity=float(np.clip(self.current_opacity, 0.0, 1.0)),
            p_left=(float(self.smooth_p_left[0]), float(self.smooth_p_left[1])),
            p_right=(float(self.smooth_p_right[0]), float(self.smooth_p_right[1])),
            distance=dist_px,
            norm_distance=norm_dist,
            angle_rad=angle_rad,
            angle_deg=math.degrees(angle_rad),
            velocity=float(self.smooth_velocity),
            is_drawing=is_drawing,
            is_pushing=is_pushing,
            left_hand_tilt=smooth_left_tilt,
            right_hand_tilt=smooth_right_tilt,
            pump_count=self.pump_count,
            max_span_ratio=self.max_span_ratio,
            meme_score=score_val,
            rank_label=rank
        )

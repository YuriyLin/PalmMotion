"""
PalmMotion Desktop GUI Control Center
Clean modern control panel for switching webcam/video, adjusting tracking/sound parameters,
choosing world melodies, customizing juice effects, launching real-time preview,
and exporting MP4 videos (standard / 16:9 side-by-side / 9:16 vertical) or animated GIFs.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional

from .config import AppConfig
from .player import RealtimePlayer
from .exporter import VideoExporter
from .assets_generator import ensure_assets
from .melodies import list_melody_keys

class PalmMotionGUI:
    def __init__(self, root: tk.Tk, config: Optional[AppConfig] = None):
        self.root = root
        self.config = config if config is not None else AppConfig()
        self.player_thread: Optional[threading.Thread] = None
        self.active_player: Optional[RealtimePlayer] = None
        self.is_exporting = False
        self.export_stop_flag = False

        ensure_assets(self.config.assets_dir)

        self._setup_window()
        self._build_widgets()

    def _setup_window(self):
        self.root.title("🪗 PalmMotion - 動態手風琴手勢偵測與名曲合成系統")
        self.root.geometry("720x820")
        self.root.minsize(680, 780)
        self.root.configure(bg="#1E1E24")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background="#1E1E24", foreground="#E0E0E0", font=("Microsoft JhengHei UI", 9))
        style.configure("TLabelframe", background="#1E1E24", foreground="#E5C07B", bordercolor="#3E3E48")
        style.configure("TLabelframe.Label", background="#1E1E24", foreground="#E5C07B", font=("Microsoft JhengHei UI", 10, "bold"))
        style.configure("TButton", background="#33333E", foreground="#FFFFFF", bordercolor="#4E4E5A", padding=6)
        style.map("TButton", background=[("active", "#454556"), ("pressed", "#252530")])
        style.configure("Accent.TButton", background="#986801", foreground="#FFFFFF", font=("Microsoft JhengHei UI", 10, "bold"))
        style.map("Accent.TButton", background=[("active", "#B8860B"), ("pressed", "#754F00")])
        style.configure("Export.TButton", background="#1F6FEB", foreground="#FFFFFF", font=("Microsoft JhengHei UI", 10, "bold"))
        style.map("Export.TButton", background=[("active", "#388BFD"), ("pressed", "#0F46A6")])
        style.configure("Gif.TButton", background="#8957E5", foreground="#FFFFFF", font=("Microsoft JhengHei UI", 9, "bold"))
        style.map("Gif.TButton", background=[("active", "#A371F7"), ("pressed", "#6E40C9")])
        style.configure("TProgressbar", thickness=14, troughcolor="#2A2A35", background="#E5C07B")

    def _build_widgets(self):
        header_frame = tk.Frame(self.root, bg="#18181E", pady=10, padx=15)
        header_frame.pack(fill="x")

        title_lbl = tk.Label(header_frame, text="🪗 PalmMotion 控制台 (Meme Edition)",
                             font=("Microsoft JhengHei UI", 16, "bold"), bg="#18181E", fg="#F5D061")
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(header_frame, text="雙手手勢辨識 • 貝茲扇形風箱 • 世界名曲自動跟彈 • 迷因字卡與對比短影音匯出",
                           font=("Microsoft JhengHei UI", 9), bg="#18181E", fg="#9DA5B4")
        sub_lbl.pack(anchor="w")

        main_canvas = tk.Frame(self.root, bg="#1E1E24", padx=15, pady=8)
        main_canvas.pack(fill="both", expand=True)

        # 1. Video Source Section
        src_group = ttk.LabelFrame(main_canvas, text=" 視訊輸入來源 (Input Source) ", padding=8)
        src_group.pack(fill="x", pady=4)

        self.source_mode_var = tk.StringVar(value="camera" if self.config.video_source.isdigit() else "file")

        row1 = tk.Frame(src_group, bg="#1E1E24")
        row1.pack(fill="x", pady=2)
        rb_cam = tk.Radiobutton(row1, text="電腦視訊鏡頭 (Webcam)", variable=self.source_mode_var,
                                value="camera", bg="#1E1E24", fg="#E0E0E0", selectcolor="#2E2E38",
                                activebackground="#1E1E24", activeforeground="#F5D061",
                                command=self._on_source_mode_change)
        rb_cam.pack(side="left")

        tk.Label(row1, text="鏡頭編號:", bg="#1E1E24", fg="#B0B0B0").pack(side="left", padx=(15, 5))
        self.cam_id_var = tk.StringVar(value="0")
        cam_spin = ttk.Spinbox(row1, from_=0, to=4, width=3, textvariable=self.cam_id_var)
        cam_spin.pack(side="left")

        row2 = tk.Frame(src_group, bg="#1E1E24")
        row2.pack(fill="x", pady=(4, 2))
        rb_file = tk.Radiobutton(row2, text="影片檔案 (Video File)", variable=self.source_mode_var,
                                 value="file", bg="#1E1E24", fg="#E0E0E0", selectcolor="#2E2E38",
                                 activebackground="#1E1E24", activeforeground="#F5D061",
                                 command=self._on_source_mode_change)
        rb_file.pack(side="left")

        self.file_path_var = tk.StringVar(value="" if self.config.video_source.isdigit() else self.config.video_source)
        self.file_entry = ttk.Entry(row2, textvariable=self.file_path_var)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(10, 5))
        btn_browse = ttk.Button(row2, text="瀏覽...", width=8, command=self._browse_input_file)
        btn_browse.pack(side="left")

        # 2. Real-time Parameters & Music Section
        param_group = ttk.LabelFrame(main_canvas, text=" 音樂與即時參數 (Music & Settings) ", padding=8)
        param_group.pack(fill="x", pady=4)

        # Song selection & Pitch mode
        row_song = tk.Frame(param_group, bg="#1E1E24")
        row_song.pack(fill="x", pady=3)

        tk.Label(row_song, text="音高/模式:", bg="#1E1E24", fg="#D0D0D0").pack(side="left")
        self.pitch_mode_var = tk.StringVar(value=self.config.audio.pitch_mode)
        cb_pitch = ttk.Combobox(row_song, textvariable=self.pitch_mode_var,
                                values=["melody", "chords", "continuous", "fixed"],
                                state="readonly", width=11)
        cb_pitch.pack(side="left", padx=(4, 12))
        cb_pitch.bind("<<ComboboxSelected>>", self._on_pitch_mode_change)

        tk.Label(row_song, text="跟彈曲目:", bg="#1E1E24", fg="#D0D0D0").pack(side="left")
        melody_pairs = list_melody_keys()
        self.song_map = {title: key for key, title in melody_pairs}
        self.song_rev_map = {key: title for key, title in melody_pairs}
        cur_title = self.song_rev_map.get(self.config.audio.melody_song, melody_pairs[0][1])
        self.song_title_var = tk.StringVar(value=cur_title)

        self.cb_song = ttk.Combobox(row_song, textvariable=self.song_title_var,
                                    values=[t for _, t in melody_pairs],
                                    state="readonly", width=22)
        self.cb_song.pack(side="left", padx=(4, 10))
        self.cb_song.bind("<<ComboboxSelected>>", self._on_song_change)

        tk.Label(row_song, text="音效:", bg="#1E1E24", fg="#D0D0D0").pack(side="left")
        self.sound_mode_var = tk.StringVar(value=self.config.audio.sound_mode)
        cb_sound = ttk.Combobox(row_song, textvariable=self.sound_mode_var, values=["synth", "wav"],
                                state="readonly", width=7)
        cb_sound.pack(side="left", padx=(4, 0))
        cb_sound.bind("<<ComboboxSelected>>", self._on_sound_mode_change)

        # Smoothness Slider
        row_s1 = tk.Frame(param_group, bg="#1E1E24")
        row_s1.pack(fill="x", pady=2)
        tk.Label(row_s1, text="動作平滑度 (EMA Filter):", width=22, anchor="w", bg="#1E1E24", fg="#D0D0D0").pack(side="left")
        self.smooth_scale = tk.Scale(row_s1, from_=0.10, to=0.80, resolution=0.05, orient="horizontal",
                                     bg="#1E1E24", fg="#E5C07B", highlightthickness=0, troughcolor="#2E2E38",
                                     command=self._update_smoothness)
        self.smooth_scale.set(self.config.tracking.smooth_alpha)
        self.smooth_scale.pack(side="left", fill="x", expand=True)

        # Accordion Volume Slider
        row_s2 = tk.Frame(param_group, bg="#1E1E24")
        row_s2.pack(fill="x", pady=2)
        tk.Label(row_s2, text="手風琴主音量 (Volume):", width=22, anchor="w", bg="#1E1E24", fg="#D0D0D0").pack(side="left")
        self.vol_scale = tk.Scale(row_s2, from_=0.0, to=1.5, resolution=0.05, orient="horizontal",
                                  bg="#1E1E24", fg="#E5C07B", highlightthickness=0, troughcolor="#2E2E38",
                                  command=self._update_volume)
        self.vol_scale.set(self.config.audio.master_volume)
        self.vol_scale.pack(side="left", fill="x", expand=True)

        # Video Speech Volume Slider
        row_s3 = tk.Frame(param_group, bg="#1E1E24")
        row_s3.pack(fill="x", pady=2)
        tk.Label(row_s3, text="原片人聲音量 (Speech):", width=22, anchor="w", bg="#1E1E24", fg="#D0D0D0").pack(side="left")
        self.speech_scale = tk.Scale(row_s3, from_=0.0, to=1.5, resolution=0.05, orient="horizontal",
                                     bg="#1E1E24", fg="#E5C07B", highlightthickness=0, troughcolor="#2E2E38",
                                     command=self._update_speech_volume)
        self.speech_scale.set(self.config.audio.video_volume)
        self.speech_scale.pack(side="left", fill="x", expand=True)

        # Juice & Visual Checkboxes Row 1
        row_chk1 = tk.Frame(param_group, bg="#1E1E24")
        row_chk1.pack(fill="x", pady=(4, 2))

        self.curved_var = tk.BooleanVar(value=self.config.visual.enable_curved_bellows)
        chk_curved = tk.Checkbutton(row_chk1, text="貝茲曲線扇形風箱", variable=self.curved_var,
                                    bg="#1E1E24", fg="#E0E0E0", selectcolor="#2E2E38",
                                    activebackground="#1E1E24", activeforeground="#F5D061",
                                    command=lambda: setattr(self.config.visual, "enable_curved_bellows", self.curved_var.get()))
        chk_curved.pack(side="left", padx=(0, 15))

        self.juice_var = tk.BooleanVar(value=self.config.visual.enable_particles)
        chk_juice = tk.Checkbutton(row_chk1, text="音符粒子與漫畫字卡", variable=self.juice_var,
                                   bg="#1E1E24", fg="#E0E0E0", selectcolor="#2E2E38",
                                   activebackground="#1E1E24", activeforeground="#F5D061",
                                   command=self._on_juice_toggle)
        chk_juice.pack(side="left", padx=(0, 15))

        self.waveform_var = tk.BooleanVar(value=self.config.visual.show_waveform)
        chk_wave = tk.Checkbutton(row_chk1, text="底部動態音波條", variable=self.waveform_var,
                                  bg="#1E1E24", fg="#E0E0E0", selectcolor="#2E2E38",
                                  activebackground="#1E1E24", activeforeground="#F5D061",
                                  command=lambda: setattr(self.config.visual, "show_waveform", self.waveform_var.get()))
        chk_wave.pack(side="left")

        # Visual Checkboxes Row 2
        row_chk2 = tk.Frame(param_group, bg="#1E1E24")
        row_chk2.pack(fill="x", pady=(2, 0))

        self.hud_var = tk.BooleanVar(value=self.config.visual.show_hud)
        chk_hud = tk.Checkbutton(row_chk2, text="狀態 HUD 面板", variable=self.hud_var,
                                 bg="#1E1E24", fg="#E0E0E0", selectcolor="#2E2E38",
                                 activebackground="#1E1E24", activeforeground="#F5D061",
                                 command=self._on_hud_toggle)
        chk_hud.pack(side="left", padx=(0, 15))

        self.score_var = tk.BooleanVar(value=self.config.visual.show_meme_score)
        chk_score = tk.Checkbutton(row_chk2, text="浮誇度計分板", variable=self.score_var,
                                   bg="#1E1E24", fg="#E0E0E0", selectcolor="#2E2E38",
                                   activebackground="#1E1E24", activeforeground="#F5D061",
                                   command=lambda: setattr(self.config.visual, "show_meme_score", self.score_var.get()))
        chk_score.pack(side="left", padx=(0, 15))

        self.landmarks_var = tk.BooleanVar(value=self.config.visual.show_debug_landmarks)
        chk_lm = tk.Checkbutton(row_chk2, text="骨架除錯點", variable=self.landmarks_var,
                                bg="#1E1E24", fg="#E0E0E0", selectcolor="#2E2E38",
                                activebackground="#1E1E24", activeforeground="#F5D061",
                                command=self._on_landmarks_toggle)
        chk_lm.pack(side="left")

        # 3. Actions & Export Section
        act_group = ttk.LabelFrame(main_canvas, text=" 操作與匯出 (Actions & Export) ", padding=8)
        act_group.pack(fill="x", pady=4)

        # Layout choice
        row_lay = tk.Frame(act_group, bg="#1E1E24")
        row_lay.pack(fill="x", pady=2)
        tk.Label(row_lay, text="匯出排版版型:", bg="#1E1E24", fg="#D0D0D0").pack(side="left")
        self.layout_var = tk.StringVar(value=self.config.export_layout)
        self.layout_map = {
            "單畫面手風琴特效": "standard",
            "16:9 左右原片對比 (Side-by-Side)": "side_by_side",
            "9:16 上下直式短影音 (Reels / Shorts)": "vertical_9_16"
        }
        self.layout_rev_map = {v: k for k, v in self.layout_map.items()}
        cb_lay = ttk.Combobox(row_lay, values=list(self.layout_map.keys()), state="readonly", width=34)
        cb_lay.set(self.layout_rev_map.get(self.config.export_layout, "單畫面手風琴特效"))
        cb_lay.pack(side="left", padx=(8, 0))
        cb_lay.bind("<<ComboboxSelected>>", lambda e: setattr(self.config, "export_layout", self.layout_map[cb_lay.get()]))

        # Action Buttons row
        btn_row = tk.Frame(act_group, bg="#1E1E24")
        btn_row.pack(fill="x", pady=5)

        self.btn_preview = ttk.Button(btn_row, text="▶ 啟動即時預覽 (Live Preview)", style="Accent.TButton",
                                      command=self.start_preview)
        self.btn_preview.pack(side="left", fill="x", expand=True, padx=(0, 4))

        self.btn_export = ttk.Button(btn_row, text="🎬 混音匯出 MP4", style="Export.TButton",
                                     command=self.start_export)
        self.btn_export.pack(side="left", fill="x", expand=True, padx=4)

        self.btn_gif = ttk.Button(btn_row, text="🎞️ 匯出 GIF", style="Gif.TButton",
                                  command=self.start_export_gif)
        self.btn_gif.pack(side="left", width=12, padx=(4, 0))

        # Export destination row
        row_exp = tk.Frame(act_group, bg="#1E1E24")
        row_exp.pack(fill="x", pady=(6, 2))
        tk.Label(row_exp, text="MP4 輸出路徑:", bg="#1E1E24", fg="#B0B0B0").pack(side="left")
        default_out = os.path.join(os.path.expanduser("~"), "Documents", "PalmMotion", "output_accordion.mp4")
        self.export_path_var = tk.StringVar(value=default_out)
        self.exp_entry = ttk.Entry(row_exp, textvariable=self.export_path_var)
        self.exp_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        btn_save_as = ttk.Button(row_exp, text="選擇路徑...", width=10, command=self._browse_output_file)
        btn_save_as.pack(side="left")

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_bar = ttk.Progressbar(act_group, variable=self.progress_var, maximum=100.0)
        self.progress_bar.pack(fill="x", pady=(8, 2))

        self.progress_lbl = tk.Label(act_group, text="就緒 (Ready)", font=("Microsoft JhengHei UI", 8),
                                     bg="#1E1E24", fg="#888894")
        self.progress_lbl.pack(anchor="w")

        # Shortcuts hint
        shortcut_lbl = tk.Label(main_canvas,
                                text="即時視窗快捷鍵：[Q/ESC] 退出 • [SPACE] 暫停 • [N] 切換下一首名曲 • [P] 音高模式 • [J] 迷因特效 • [C] 扇形風箱 • [M] 靜音",
                                font=("Microsoft JhengHei UI", 8), bg="#1E1E24", fg="#787886")
        shortcut_lbl.pack(pady=3)

    def _on_source_mode_change(self):
        mode = self.source_mode_var.get()
        if mode == "camera":
            self.config.video_source = self.cam_id_var.get()
        else:
            self.config.video_source = self.file_path_var.get()

    def _browse_input_file(self):
        f = filedialog.askopenfilename(
            title="選擇輸入影片檔案",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv *.webm"), ("All Files", "*.*")]
        )
        if f:
            self.file_path_var.set(f)
            self.source_mode_var.set("file")
            self.config.video_source = f

    def _browse_output_file(self):
        f = filedialog.asksaveasfilename(
            title="指定匯出影片儲存路徑",
            defaultextension=".mp4",
            filetypes=[("MP4 Video", "*.mp4")]
        )
        if f:
            self.export_path_var.set(f)

    def _update_smoothness(self, val):
        self.config.tracking.smooth_alpha = float(val)

    def _update_volume(self, val):
        self.config.audio.master_volume = float(val)

    def _update_speech_volume(self, val):
        self.config.audio.video_volume = float(val)

    def _on_sound_mode_change(self, event=None):
        self.config.audio.sound_mode = self.sound_mode_var.get()

    def _on_pitch_mode_change(self, event=None):
        self.config.audio.pitch_mode = self.pitch_mode_var.get()

    def _on_song_change(self, event=None):
        title = self.song_title_var.get()
        key = self.song_map.get(title, "bella_ciao")
        self.config.audio.melody_song = key

    def _on_juice_toggle(self):
        val = self.juice_var.get()
        self.config.visual.enable_particles = val
        self.config.visual.enable_comic_popups = val

    def _on_hud_toggle(self):
        self.config.visual.show_hud = self.hud_var.get()

    def _on_landmarks_toggle(self):
        self.config.visual.show_debug_landmarks = self.landmarks_var.get()

    def start_preview(self):
        if self.player_thread and self.player_thread.is_alive():
            messagebox.showinfo("提示", "即時預覽視窗已在執行中。請直接操作該視窗或按 Q 關閉。")
            return

        if self.source_mode_var.get() == "camera":
            self.config.video_source = self.cam_id_var.get()
        else:
            src_file = self.file_path_var.get().strip()
            if not src_file or not os.path.exists(src_file):
                messagebox.showerror("錯誤", "請先選擇有效的影片檔案！")
                return
            self.config.video_source = src_file

        self.btn_preview.config(state="disabled")
        self.progress_lbl.config(text=f"即時預覽執行中 (來源: {self.config.video_source})...", fg="#F5D061")

        def _run():
            self.active_player = RealtimePlayer(self.config)
            self.active_player.run(status_cb=lambda s: self.root.after(0, lambda: self.progress_lbl.config(text=s)))
            self.root.after(0, self._on_preview_finished)

        self.player_thread = threading.Thread(target=_run, daemon=True)
        self.player_thread.start()

    def _on_preview_finished(self):
        self.btn_preview.config(state="normal")
        self.progress_lbl.config(text="預覽已結束 (Ready)", fg="#888894")
        self.active_player = None

    def start_export(self):
        if self.is_exporting:
            messagebox.showinfo("提示", "正在匯出中，請稍候...")
            return

        src_file = self.file_path_var.get().strip()
        if not src_file or not os.path.exists(src_file):
            messagebox.showerror("錯誤", "混音匯出功能需要指定有效的影片檔案作為輸入源！")
            return

        out_file = self.export_path_var.get().strip()
        if not out_file:
            messagebox.showerror("錯誤", "請指定輸出檔案路徑！")
            return

        self.is_exporting = True
        self.export_stop_flag = False
        self.btn_export.config(state="disabled")
        self.btn_preview.config(state="disabled")
        self.btn_gif.config(state="disabled")
        self.progress_var.set(0.0)
        self.progress_lbl.config(text="準備匯出影片與混音...", fg="#388BFD")

        def _progress(cur, total, pct):
            self.root.after(0, lambda: self.progress_lbl.config(text=f"正在處理影格與合成音訊: {cur}/{total} ({pct:.1f}%)"))
            self.root.after(0, lambda: self.progress_var.set(pct))

        def _export_thread():
            exporter = VideoExporter(self.config)
            try:
                ok = exporter.process_and_export(
                    input_video_path=src_file,
                    output_video_path=out_file,
                    progress_cb=_progress,
                    stop_flag_check=lambda: self.export_stop_flag
                )
                self.root.after(0, lambda: self._on_export_finished(ok, out_file))
            except Exception as e:
                self.root.after(0, lambda: self._on_export_error(str(e)))

        threading.Thread(target=_export_thread, daemon=True).start()

    def start_export_gif(self):
        src_file = self.file_path_var.get().strip()
        if not src_file or not os.path.exists(src_file):
            messagebox.showerror("錯誤", "請先指定有效的影片檔案！")
            return

        gif_out = filedialog.asksaveasfilename(
            title="指定匯出 GIF 儲存路徑",
            defaultextension=".gif",
            filetypes=[("Animated GIF", "*.gif")]
        )
        if not gif_out:
            return

        self.is_exporting = True
        self.progress_lbl.config(text="正在生成調色盤優化之 GIF 動圖...", fg="#A371F7")
        self.btn_gif.config(state="disabled")

        def _gif_thread():
            exporter = VideoExporter(self.config)
            # Temporary mp4 export then convert to gif
            temp_mp4 = gif_out + ".temp.mp4"
            ok = exporter.process_and_export(input_video_path=src_file, output_video_path=temp_mp4)
            if ok:
                ok = exporter.export_gif(temp_mp4, gif_out, fps=15, max_width=540)
            if os.path.exists(temp_mp4):
                try:
                    os.remove(temp_mp4)
                except Exception:
                    pass
            self.root.after(0, lambda: self._on_gif_finished(ok, gif_out))

        threading.Thread(target=_gif_thread, daemon=True).start()

    def _on_export_finished(self, success: bool, out_path: str):
        self.is_exporting = False
        self.btn_export.config(state="normal")
        self.btn_preview.config(state="normal")
        self.btn_gif.config(state="normal")
        if success:
            self.progress_var.set(100.0)
            self.progress_lbl.config(text=f"✅ 匯出完成！檔案儲存於: {out_path}", fg="#60C070")
            messagebox.showinfo("匯出完成", f"手風琴特效與混音已成功匯出至：\n{out_path}")
        else:
            self.progress_lbl.config(text="❌ 匯出失敗或已取消", fg="#E06C75")
            messagebox.showerror("匯出失敗", "匯出過程中發生錯誤，請檢查終端機訊息。")

    def _on_gif_finished(self, success: bool, gif_path: str):
        self.is_exporting = False
        self.btn_gif.config(state="normal")
        if success:
            self.progress_lbl.config(text=f"✅ GIF 動圖匯出成功: {gif_path}", fg="#A371F7")
            messagebox.showinfo("GIF 匯出完成", f"預覽 GIF 已成功儲存至：\n{gif_path}")
        else:
            self.progress_lbl.config(text="❌ GIF 匯出失敗", fg="#E06C75")
            messagebox.showerror("GIF 失敗", "GIF 轉換失敗，請確認檔案格式。")

    def _on_export_error(self, err_msg: str):
        self.is_exporting = False
        self.btn_export.config(state="normal")
        self.btn_preview.config(state="normal")
        self.btn_gif.config(state="normal")
        self.progress_lbl.config(text=f"❌ 錯誤: {err_msg}", fg="#E06C75")
        messagebox.showerror("匯出錯誤", f"匯出發生例外狀況：\n{err_msg}")

def launch_gui(config: Optional[AppConfig] = None):
    root = tk.Tk()
    app = PalmMotionGUI(root, config)
    root.mainloop()

if __name__ == "__main__":
    launch_gui()

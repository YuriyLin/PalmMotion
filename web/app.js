/* Lucian UX/UI Prompt #007 · MIT License (c) 2026 Seokwoooo · https://lucianlabs.dev/uxui-prompt/#007 */
/* Lucian UX/UI Prompt #039 · MIT License (c) 2026 Seokwoooo · https://lucianlabs.dev/uxui-prompt/#039 */
/* Lucian UX/UI Prompt #047 · MIT License (c) 2026 Seokwoooo · https://lucianlabs.dev/uxui-prompt/#047 */

/**
 * Screening Room — Minimalist Black Cinema Accordion Studio
 * Powered by Lucian UX/UI Prompt:
 * - #007 Play–pause morph (SVG polygon interpolation)
 * - #039 Sliding pill tabs (3-option Musical Score selector)
 * - #047 Period segmented control (Stretchy knob Aspect/Layout switcher)
 */

// --- 1. Curated 3-Song World Melody Database ---
const CHORDS = {
  Am: [110.0, 164.81, 220.0, 261.63],
  Dm: [146.83, 174.61, 220.0, 293.66],
  E7: [164.81, 207.65, 246.94, 293.66],
  C:  [130.81, 196.00, 261.63, 329.63],
  G:  [98.00, 196.00, 246.94, 293.66],
  G7: [98.00, 174.61, 246.94, 293.66],
  F:  [174.61, 220.00, 261.63, 349.23]
};

const MELODY_DB = {
  bella_ciao: {
    title: "Bella Ciao",
    notes: [
      { name: "E4", lead: 329.63, bass: CHORDS.Am },
      { name: "A4", lead: 440.00, bass: CHORDS.Am },
      { name: "B4", lead: 493.88, bass: CHORDS.Am },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "A4", lead: 440.00, bass: CHORDS.Am },
      { name: "E4", lead: 329.63, bass: CHORDS.Am },
      { name: "A4", lead: 440.00, bass: CHORDS.Am },
      { name: "B4", lead: 493.88, bass: CHORDS.Am },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "A4", lead: 440.00, bass: CHORDS.Am },
      { name: "E4", lead: 329.63, bass: CHORDS.Am },
      { name: "A4", lead: 440.00, bass: CHORDS.Am },
      { name: "B4", lead: 493.88, bass: CHORDS.Am },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "B4", lead: 493.88, bass: CHORDS.Am },
      { name: "A4", lead: 440.00, bass: CHORDS.Am },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "B4", lead: 493.88, bass: CHORDS.E7 },
      { name: "A4", lead: 440.00, bass: CHORDS.E7 },
      { name: "E5", lead: 659.25, bass: CHORDS.E7 },
      { name: "E5", lead: 659.25, bass: CHORDS.Dm },
      { name: "D5", lead: 587.33, bass: CHORDS.Dm },
      { name: "E5", lead: 659.25, bass: CHORDS.Dm },
      { name: "F5", lead: 698.46, bass: CHORDS.Dm },
      { name: "E5", lead: 659.25, bass: CHORDS.Am },
      { name: "D5", lead: 587.33, bass: CHORDS.Am },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "B4", lead: 493.88, bass: CHORDS.E7 },
      { name: "E5", lead: 659.25, bass: CHORDS.E7 },
      { name: "C5", lead: 523.25, bass: CHORDS.E7 },
      { name: "B4", lead: 493.88, bass: CHORDS.E7 },
      { name: "A4", lead: 440.00, bass: CHORDS.Am }
    ]
  },
  la_vie_en_rose: {
    title: "La Vie En Rose",
    notes: [
      { name: "G4", lead: 392.00, bass: CHORDS.C },
      { name: "F#4", lead: 369.99, bass: CHORDS.C },
      { name: "G4", lead: 392.00, bass: CHORDS.C },
      { name: "A4", lead: 440.00, bass: CHORDS.C },
      { name: "G4", lead: 392.00, bass: CHORDS.C },
      { name: "E4", lead: 329.63, bass: CHORDS.C },
      { name: "F4", lead: 349.23, bass: CHORDS.G7 },
      { name: "E4", lead: 329.63, bass: CHORDS.G7 },
      { name: "F4", lead: 349.23, bass: CHORDS.G7 },
      { name: "G4", lead: 392.00, bass: CHORDS.G7 },
      { name: "D4", lead: 293.66, bass: CHORDS.G7 },
      { name: "C4", lead: 261.63, bass: CHORDS.C }
    ]
  },
  korobeiniki: {
    title: "Korobeiniki",
    notes: [
      { name: "E5", lead: 659.25, bass: CHORDS.E7 },
      { name: "B4", lead: 493.88, bass: CHORDS.E7 },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "D5", lead: 587.33, bass: CHORDS.Dm },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "B4", lead: 493.88, bass: CHORDS.E7 },
      { name: "A4", lead: 440.00, bass: CHORDS.Am },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "E5", lead: 659.25, bass: CHORDS.Am },
      { name: "D5", lead: 587.33, bass: CHORDS.Dm },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "B4", lead: 493.88, bass: CHORDS.E7 },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "D5", lead: 587.33, bass: CHORDS.Dm },
      { name: "E5", lead: 659.25, bass: CHORDS.E7 },
      { name: "C5", lead: 523.25, bass: CHORDS.Am },
      { name: "A4", lead: 440.00, bass: CHORDS.Am }
    ]
  }
};

/* Lucian UX/UI #007 Play–pause morph coordinates */
const U007_PLAY = [
  [[13, 8], [22.5, 13.6], [22.5, 26.4], [13, 32]],
  [[22.5, 13.6], [32, 20], [32, 20], [22.5, 26.4]]
];
const U007_PAUSE = [
  [[11, 9], [17, 9], [17, 31], [11, 31]],
  [[23, 9], [29, 9], [29, 31], [23, 31]]
];

function formatTime(seconds) {
  if (isNaN(seconds) || seconds < 0) return "00:00";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

// --- 2. Web Audio Accordion Synthesizer ---
class WebAccordionAudio {
  constructor() {
    this.ctx = null;
    this.masterGain = null;
    this.streamDest = null;
    this.oscillators = [];

    this.activeSong = "bella_ciao";
    this.noteIdx = 0;
    this.travelAccum = 0.0;
    this.lastDist = null;
    this.lastPumpDraw = null;
    this.lastStepTime = 0;

    this.currentMusicLabel = "Bella Ciao · E4";
  }

  init() {
    if (this.ctx) return;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    this.ctx = new AudioContext();
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.setValueAtTime(0.0, this.ctx.currentTime);

    this.streamDest = this.ctx.createMediaStreamDestination();

    this.masterGain.connect(this.ctx.destination);
    this.masterGain.connect(this.streamDest);

    // 6 dual-reed oscillator voices
    for (let i = 0; i < 6; i++) {
      const osc1 = this.ctx.createOscillator();
      const osc2 = this.ctx.createOscillator();
      const g = this.ctx.createGain();
      g.gain.value = 0.0;

      osc1.type = "sawtooth";
      osc2.type = "sawtooth";

      osc1.connect(g);
      osc2.connect(g);
      g.connect(this.masterGain);

      osc1.start();
      osc2.start();

      this.oscillators.push({ osc1, osc2, gain: g });
    }
  }

  silence() {
    if (!this.ctx || !this.masterGain) return;
    const now = this.ctx.currentTime;
    this.masterGain.gain.cancelScheduledValues(now);
    this.masterGain.gain.setValueAtTime(0.0, now);
  }

  updateMotion(motion, masterVol, isPaused = false) {
    if (!this.ctx) return;
    if (this.ctx.state === "suspended") this.ctx.resume();

    const now = this.ctx.currentTime;
    if (isPaused || !motion.isValid || motion.opacity <= 0.01) {
      this.masterGain.gain.cancelScheduledValues(now);
      this.masterGain.gain.setValueAtTime(0.0, now);
      return;
    }

    const speed = Math.abs(motion.velocity);
    let targetVol = 0.0;
    if (speed > 0.03) {
      targetVol = Math.min(1.0, (speed - 0.03) / 0.65) * masterVol * motion.opacity;
    }

    this.masterGain.gain.setTargetAtTime(targetVol, now, 0.04);

    const song = MELODY_DB[this.activeSong] || MELODY_DB.bella_ciao;
    const notes = song.notes;

    if (this.lastDist !== null) {
      this.travelAccum += Math.abs(motion.normDist - this.lastDist);
    }
    this.lastDist = motion.normDist;

    const dirChanged = (this.lastPumpDraw !== null && this.lastPumpDraw !== motion.isDrawing);
    const curMs = performance.now();

    if ((dirChanged && (curMs - this.lastStepTime > 130)) || this.travelAccum >= 0.08) {
      this.travelAccum = 0.0;
      this.lastStepTime = curMs;
      this.lastPumpDraw = motion.isDrawing;
      this.noteIdx = (this.noteIdx + 1) % notes.length;
    }

    const curNote = notes[this.noteIdx];
    this.currentMusicLabel = `${song.title} · ${curNote.name}`;
    const allFreqs = [curNote.lead, ...curNote.bass];

    for (let i = 0; i < this.oscillators.length; i++) {
      const voice = this.oscillators[i];
      if (i < allFreqs.length) {
        const f = allFreqs[i];
        const detune = (i === 0) ? 2.5 : 1.2;
        voice.osc1.frequency.setTargetAtTime(f, now, 0.03);
        voice.osc2.frequency.setTargetAtTime(f + detune, now, 0.03);
        voice.gain.gain.setTargetAtTime(i === 0 ? 0.35 : 0.18, now, 0.03);
      } else {
        voice.gain.gain.setTargetAtTime(0.0, now, 0.03);
      }
    }
  }
}

// --- 3. Screening Room Studio Controller ---
class PalmMotionWebStudio {
  constructor() {
    this.videoEl = document.getElementById("webcam");
    this.videoSourceEl = document.getElementById("video-source");
    this.canvasEl = document.getElementById("output-canvas");
    this.ctx = this.canvasEl.getContext("2d");

    // Offscreen rendering canvas for layout compositions
    this.fxCanvas = document.createElement("canvas");
    this.fxCtx = this.fxCanvas.getContext("2d");

    // Overlays & Header Telemetry
    this.standbyOverlay = document.getElementById("standby-overlay");
    this.loadingOverlay = document.getElementById("loading-overlay");
    this.loadingText = document.getElementById("loading-text");
    this.statusBadge = document.getElementById("status-badge");
    this.statusLed = document.getElementById("status-led");
    this.fpsBadge = document.getElementById("fps-badge");
    this.scoreTelemetry = document.getElementById("score-telemetry");
    this.telemetryState = document.getElementById("telemetry-state");
    this.telemetryNote = document.getElementById("telemetry-note");

    // Video Player Bar & Lucian #007 Morph Elements
    this.videoPlayerBar = document.getElementById("video-player-bar");
    this.btnPlayPause = document.getElementById("btn-play-pause");
    this.polyL = this.btnPlayPause.querySelector(".u007-l");
    this.polyR = this.btnPlayPause.querySelector(".u007-r");
    this.isMorphPlaying = false;
    this.morphRafId = 0;

    this.timeCurrent = document.getElementById("time-current");
    this.timeTotal = document.getElementById("time-total");
    this.videoScrubber = document.getElementById("video-scrubber");
    this.btnExportVideo = document.getElementById("btn-export-video");

    // Export Modal Elements
    this.exportModal = document.getElementById("export-modal");
    this.exportBarFill = document.getElementById("export-bar-fill");
    this.exportStatusText = document.getElementById("export-status-text");
    this.btnCancelExport = document.getElementById("btn-cancel-export");

    this.audio = new WebAccordionAudio();
    this.handLandmarker = null;

    // Modes & Layout
    this.isCameraRunning = false;
    this.useVideoFile = false;
    this.currentLayout = "solo"; // "solo", "side_by_side", "vertical"
    this.masterVolume = 0.25;    // Preset 25%
    this.smoothAlpha = 0.35;     // Internal EMA smoothing factor

    // Filters & Kinematics
    this.smoothLeft = null;
    this.smoothRight = null;
    this.smoothAngle = 0.0;
    this.smoothLeftTilt = 0.0;
    this.smoothRightTilt = 0.0;
    this.smoothVelocity = 0.0;
    this.prevNormDist = null;
    this.prevTime = null;
    this.currentOpacity = 0.0;

    // Video Audio Node
    this.videoAudioConnected = false;

    // Exporter State
    this.isExporting = false;
    this.exportRecorder = null;
    this.exportChunks = [];

    // FPS Counter
    this.lastFpsUpdate = 0;
    this.frameCount = 0;

    this.initUI();
    this.initLayoutSegmentedControl();
    this.initSongPillTabs();
    this.setPlayPauseGlyph(false, true);
    this.initMediaPipe();
  }

  initUI() {
    const btnCam = document.getElementById("btn-toggle-cam");
    const videoInput = document.getElementById("video-input");

    btnCam.onclick = () => this.toggleCamera();
    videoInput.onchange = (e) => this.handleVideoUpload(e);

    // Standby quick action buttons
    document.getElementById("btn-standby-cam").onclick = () => this.toggleCamera();
    document.getElementById("btn-standby-video").onclick = () => videoInput.click();

    // Volume Slider (preset to 25%)
    const sliderVol = document.getElementById("slider-vol");
    const volVal = document.getElementById("vol-val");
    sliderVol.value = "25";
    sliderVol.style.setProperty("--vol-pct", "25%");
    volVal.innerText = "25%";

    sliderVol.oninput = (e) => {
      const pct = parseFloat(e.target.value);
      this.masterVolume = pct / 100.0;
      sliderVol.style.setProperty("--vol-pct", `${pct}%`);
      volVal.innerText = `${Math.round(pct)}%`;
    };

    // Video player controls
    this.btnPlayPause.onclick = () => this.togglePlayPause();
    this.videoScrubber.oninput = () => this.handleScrubInput();
    this.videoScrubber.onchange = () => this.handleScrubEnd();

    this.videoSourceEl.ontimeupdate = () => this.handleTimeUpdate();
    this.videoSourceEl.onended = () => {
      this.audio.silence();
      if (this.isExporting) {
        this.finishExport();
      } else {
        this.setPlayPauseGlyph(false);
      }
    };

    // Keyboard Spacebar to Play/Pause
    window.addEventListener("keydown", (e) => {
      if (e.code === "Space" && e.target.tagName !== "INPUT" && e.target.tagName !== "BUTTON") {
        e.preventDefault();
        if (this.useVideoFile) this.togglePlayPause();
      }
    });

    // Export buttons
    this.btnExportVideo.onclick = () => this.startExport();
    this.btnCancelExport.onclick = () => this.cancelExport();
  }

  /* Lucian UX/UI #007 Play–pause morph animation */
  setPlayPauseGlyph(playing, immediate = false) {
    if (this.isMorphPlaying === playing && !immediate) return;
    const fromShape = this.isMorphPlaying ? U007_PAUSE : U007_PLAY;
    const toShape = playing ? U007_PAUSE : U007_PLAY;
    this.isMorphPlaying = playing;
    this.btnPlayPause.setAttribute("aria-pressed", String(playing));

    const applyPoints = (el, pts) => {
      el.setAttribute("points", pts.map((p) => p.join(",")).join(" "));
    };

    if (immediate || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      applyPoints(this.polyL, toShape[0]);
      applyPoints(this.polyR, toShape[1]);
      return;
    }

    cancelAnimationFrame(this.morphRafId);
    const t0 = performance.now();
    const duration = 260;

    const tick = (now) => {
      const k = Math.min(1, (now - t0) / duration);
      const e = 1 - Math.pow(1 - k, 3);
      [this.polyL, this.polyR].forEach((el, idx) => {
        const pts = fromShape[idx].map((p, j) => [
          (p[0] + (toShape[idx][j][0] - p[0]) * e).toFixed(2),
          (p[1] + (toShape[idx][j][1] - p[1]) * e).toFixed(2)
        ]);
        applyPoints(el, pts);
      });
      if (k < 1) {
        this.morphRafId = requestAnimationFrame(tick);
      }
    };
    this.morphRafId = requestAnimationFrame(tick);
  }

  /* Lucian UX/UI #047 Period segmented control (Stretchy Knob for Aspect/Layout) */
  initLayoutSegmentedControl() {
    const seg = document.getElementById("layout-seg");
    const knob = document.getElementById("layout-knob");
    const opts = Array.from(seg.querySelectorAll(".u047-opt"));
    let currentIdx = 0;

    const placeKnob = (i, dir) => {
      knob.dataset.dir = dir;
      const pctL = (i * 100) / opts.length;
      const pctR = ((opts.length - 1 - i) * 100) / opts.length;
      knob.style.setProperty("--l", `calc(${pctL}% + 3px)`);
      knob.style.setProperty("--r", `calc(${pctR}% + 3px)`);
    };

    placeKnob(0, "right");

    opts.forEach((opt, idx) => {
      opt.addEventListener("click", () => {
        if (idx === currentIdx) return;
        const dir = idx > currentIdx ? "right" : "left";
        opts[currentIdx].setAttribute("aria-checked", "false");
        opt.setAttribute("aria-checked", "true");
        currentIdx = idx;
        placeKnob(idx, dir);

        this.currentLayout = opt.getAttribute("data-layout");
        if (this.useVideoFile && this.videoSourceEl.paused) {
          this.processSingleFrame();
        }
      });
    });
  }

  /* Lucian UX/UI #039 Sliding pill tabs (3-Option Score Selector) */
  initSongPillTabs() {
    const tabsContainer = document.getElementById("song-tabs");
    const tabs = Array.from(tabsContainer.querySelectorAll(".u039-tab"));
    const pill = document.getElementById("song-pill");

    const movePill = (tab) => {
      pill.style.setProperty("--x", `${tab.offsetLeft}px`);
      pill.style.setProperty("--w", `${tab.offsetWidth}px`);
    };

    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        tabs.forEach((t) => t.setAttribute("aria-selected", "false"));
        tab.setAttribute("aria-selected", "true");
        movePill(tab);

        const songKey = tab.getAttribute("data-song");
        this.audio.activeSong = songKey;
        this.audio.noteIdx = 0;
        const songObj = MELODY_DB[songKey] || MELODY_DB.bella_ciao;
        this.telemetryNote.innerText = songObj.title;
      });
    });

    setTimeout(() => {
      const activeTab = tabsContainer.querySelector('.u039-tab[aria-selected="true"]') || tabs[0];
      movePill(activeTab);
    }, 80);

    window.addEventListener("resize", () => {
      const activeTab = tabsContainer.querySelector('.u039-tab[aria-selected="true"]') || tabs[0];
      movePill(activeTab);
    });
  }

  async initMediaPipe() {
    try {
      this.loadingText.innerText = "CALIBRATING OPTICAL HAND LANDMARKER...";

      let FilesetResolver, HandLandmarker;
      if (window.Vision) {
        FilesetResolver = window.Vision.FilesetResolver;
        HandLandmarker = window.Vision.HandLandmarker;
      } else {
        const visionModule = await import("./vision_bundle.js");
        FilesetResolver = visionModule.FilesetResolver || window.Vision?.FilesetResolver;
        HandLandmarker = visionModule.HandLandmarker || window.Vision?.HandLandmarker;
      }

      if (!FilesetResolver || !HandLandmarker) {
        throw new Error("無法取得 FilesetResolver / HandLandmarker");
      }

      let vision;
      try {
        vision = await FilesetResolver.forVisionTasks("./wasm");
      } catch (wasmErr) {
        vision = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@1.2.2/wasm");
      }

      const modelCandidates = [
        "./hand_landmarker.task",
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
      ];
      let landmarker = null;
      let lastError = null;

      for (const modelPath of modelCandidates) {
        for (const delegate of ["GPU", "CPU"]) {
          try {
            landmarker = await HandLandmarker.createFromOptions(vision, {
              baseOptions: { modelAssetPath: modelPath, delegate: delegate },
              runningMode: "VIDEO",
              numHands: 2,
              minHandDetectionConfidence: 0.5,
              minTrackingConfidence: 0.5
            });
            if (landmarker) break;
          } catch (createErr) {
            lastError = createErr;
          }
        }
        if (landmarker) break;
      }

      if (!landmarker) throw lastError || new Error("Failed to create HandLandmarker");

      this.handLandmarker = landmarker;
      this.loadingOverlay.style.opacity = "0";
      setTimeout(() => {
        this.loadingOverlay.style.display = "none";
      }, 420);
      this.statusBadge.innerText = "READY";
      this.statusLed.classList.add("ready");
    } catch (err) {
      console.error("MediaPipe initialization error:", err);
      this.loadingText.innerText = "ENGINE LOAD FAILED: " + (err.message || err);
    }
  }

  async toggleCamera() {
    this.audio.init();
    const btnCam = document.getElementById("btn-toggle-cam");
    const camLabel = document.getElementById("cam-btn-label");

    if (this.isCameraRunning) {
      const stream = this.videoEl.srcObject;
      if (stream) stream.getTracks().forEach((t) => t.stop());
      this.isCameraRunning = false;
      this.audio.silence();
      btnCam.classList.remove("active-cam");
      camLabel.innerText = "啟動鏡頭";
      this.statusBadge.innerText = "STANDBY";
      return;
    }

    try {
      if (this.useVideoFile && !this.videoSourceEl.paused) {
        this.videoSourceEl.pause();
        this.setPlayPauseGlyph(false);
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 1280, height: 720, facingMode: "user" },
        audio: false
      });
      this.videoEl.srcObject = stream;
      await this.videoEl.play();

      this.isCameraRunning = true;
      this.useVideoFile = false;
      this.standbyOverlay.classList.add("hidden");
      this.videoPlayerBar.classList.add("hidden");
      this.btnExportVideo.style.display = "none";
      btnCam.classList.add("active-cam");
      camLabel.innerText = "停止鏡頭";
      this.statusBadge.innerText = "LIVE LENS";

      requestAnimationFrame(() => this.processLoop());
    } catch (err) {
      alert("無法存取視訊鏡頭：" + err.message);
    }
  }

  handleVideoUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    this.audio.init();
    if (this.isCameraRunning) this.toggleCamera();

    const url = URL.createObjectURL(file);
    this.videoSourceEl.src = url;
    this.useVideoFile = true;
    this.standbyOverlay.classList.add("hidden");
    this.statusBadge.innerText = "REEL LOADED";

    this.videoSourceEl.onloadedmetadata = () => {
      this.videoPlayerBar.classList.remove("hidden");
      this.btnExportVideo.style.display = "inline-flex";
      this.setPlayPauseGlyph(false, true);
      this.timeCurrent.innerText = "00:00";
      this.timeTotal.innerText = formatTime(this.videoSourceEl.duration);
      this.videoScrubber.value = 0;
      this.videoScrubber.style.setProperty("--progress", "0%");

      if (!this.videoAudioConnected && this.audio.ctx) {
        try {
          const sourceNode = this.audio.ctx.createMediaElementSource(this.videoSourceEl);
          sourceNode.connect(this.audio.ctx.destination);
          sourceNode.connect(this.audio.streamDest);
          this.videoAudioConnected = true;
        } catch (e) {
          console.warn("MediaElementAudioSource notice:", e);
        }
      }

      this.videoSourceEl.currentTime = 0;
      setTimeout(() => this.processSingleFrame(), 140);
    };
  }

  togglePlayPause() {
    if (!this.useVideoFile) return;
    if (this.videoSourceEl.paused) {
      this.videoSourceEl.play();
      this.setPlayPauseGlyph(true);
      this.statusBadge.innerText = "SCREENING";
      requestAnimationFrame(() => this.processLoop());
    } else {
      this.videoSourceEl.pause();
      this.setPlayPauseGlyph(false);
      this.audio.silence();
      this.statusBadge.innerText = "PAUSED";
      this.updateHeaderTelemetry({ isValid: false, isDrawing: false, isPushing: false }, true);
    }
  }

  handleScrubInput() {
    if (!this.useVideoFile || !this.videoSourceEl.duration) return;
    const pct = parseFloat(this.videoScrubber.value);
    this.videoScrubber.style.setProperty("--progress", `${pct}%`);
    const targetTime = (pct / 100.0) * this.videoSourceEl.duration;
    this.videoSourceEl.currentTime = targetTime;
    this.timeCurrent.innerText = formatTime(targetTime);
    this.audio.silence();
    if (this.videoSourceEl.paused) {
      this.processSingleFrame();
    }
  }

  handleScrubEnd() {
    if (!this.useVideoFile || !this.videoSourceEl.duration) return;
    this.handleScrubInput();
    if (this.videoSourceEl.paused) {
      this.audio.silence();
    }
  }

  handleTimeUpdate() {
    if (!this.useVideoFile || !this.videoSourceEl.duration) return;
    const cur = this.videoSourceEl.currentTime;
    const dur = this.videoSourceEl.duration;
    const pct = (cur / dur) * 100.0;
    this.videoScrubber.value = pct;
    this.videoScrubber.style.setProperty("--progress", `${pct.toFixed(1)}%`);
    this.timeCurrent.innerText = formatTime(cur);
    this.timeTotal.innerText = formatTime(dur);

    if (this.isExporting) {
      const exportPct = Math.min(100, Math.round(pct));
      this.exportBarFill.style.width = `${exportPct}%`;
      this.exportStatusText.innerText = `進度：${exportPct}% (${formatTime(cur)} / ${formatTime(dur)})`;
    }
  }

  updateHeaderTelemetry(motion, isPaused = false) {
    this.scoreTelemetry.classList.remove("active-draw", "active-push");
    if (isPaused || !motion.isValid) {
      this.telemetryState.innerText = isPaused ? "PAUSED" : "STANDBY";
    } else if (motion.isDrawing) {
      this.scoreTelemetry.classList.add("active-draw");
      this.telemetryState.innerText = "DRAW";
    } else if (motion.isPushing) {
      this.scoreTelemetry.classList.add("active-push");
      this.telemetryState.innerText = "PUSH";
    } else {
      this.telemetryState.innerText = "HOLD";
    }
    this.telemetryNote.innerText = this.audio.currentMusicLabel;
  }

  processSingleFrame() {
    const activeVideo = this.videoSourceEl;
    if (!activeVideo || !activeVideo.videoWidth) return;
    const now = performance.now();
    let motionState = { isValid: false, opacity: 0.0 };

    if (this.handLandmarker) {
      const results = this.handLandmarker.detectForVideo(activeVideo, now);
      motionState = this.extractMotion(results, activeVideo.videoWidth, activeVideo.videoHeight, now);
    }

    // Video is paused or scrubbing: strictly silence accordion audio
    this.audio.updateMotion(motionState, this.masterVolume, true);
    this.audio.silence();
    this.updateHeaderTelemetry(motionState, true);
    this.compositeScene(activeVideo, motionState);
  }

  processLoop() {
    const activeVideo = this.useVideoFile ? this.videoSourceEl : this.videoEl;
    if (!activeVideo || (activeVideo.paused && !this.isExporting)) {
      if (this.useVideoFile && activeVideo.paused) {
        this.audio.silence();
      }
      return;
    }

    const now = performance.now();
    let motionState = { isValid: false, opacity: 0.0 };

    if (this.handLandmarker && activeVideo.videoWidth > 0) {
      const results = this.handLandmarker.detectForVideo(activeVideo, now);
      motionState = this.extractMotion(results, activeVideo.videoWidth, activeVideo.videoHeight, now);
    }

    const isPaused = this.useVideoFile ? activeVideo.paused : false;
    this.audio.updateMotion(motionState, this.masterVolume, isPaused);
    this.updateHeaderTelemetry(motionState, isPaused);
    this.compositeScene(activeVideo, motionState);

    // Update FPS
    this.frameCount++;
    if (now - this.lastFpsUpdate >= 500) {
      const fps = (this.frameCount * 1000) / (now - this.lastFpsUpdate);
      this.fpsBadge.innerText = `${fps.toFixed(1)} FPS`;
      this.frameCount = 0;
      this.lastFpsUpdate = now;
    }

    if (this.isCameraRunning || !activeVideo.paused || this.isExporting) {
      requestAnimationFrame(() => this.processLoop());
    }
  }

  extractMotion(results, w, h, now) {
    const dt = this.prevTime ? Math.max(0.001, (now - this.prevTime) / 1000) : 0.033;
    this.prevTime = now;

    let pLeft = null;
    let pRight = null;
    let leftTilt = 0;
    let rightTilt = 0;

    if (results.landmarks && results.landmarks.length >= 2) {
      const hands = results.landmarks.map((lms) => {
        const rawX = (lms[0].x + lms[5].x + lms[9].x + lms[17].x) * 0.25 * w;
        const cx = this.useVideoFile ? rawX : w - rawX;
        const cy = (lms[0].y + lms[5].y + lms[9].y + lms[17].y) * 0.25 * h;
        const dx = (lms[9].x - lms[0].x) * w * (this.useVideoFile ? 1 : -1);
        const tilt = Math.atan2((lms[9].y - lms[0].y) * h, dx);
        return { x: cx, y: cy, tilt };
      });

      hands.sort((a, b) => a.x - b.x);
      pLeft = [hands[0].x, hands[0].y];
      pRight = [hands[1].x, hands[1].y];
      leftTilt = hands[0].tilt;
      rightTilt = hands[1].tilt;
    }

    const isDetected = (pLeft !== null && pRight !== null);
    const alpha = this.smoothAlpha;

    if (isDetected) {
      this.currentOpacity = Math.min(1.0, this.currentOpacity + dt / 0.12);

      if (!this.smoothLeft) {
        this.smoothLeft = [...pLeft];
        this.smoothRight = [...pRight];
      } else {
        this.smoothLeft[0] = alpha * pLeft[0] + (1 - alpha) * this.smoothLeft[0];
        this.smoothLeft[1] = alpha * pLeft[1] + (1 - alpha) * this.smoothLeft[1];
        this.smoothRight[0] = alpha * pRight[0] + (1 - alpha) * this.smoothRight[0];
        this.smoothRight[1] = alpha * pRight[1] + (1 - alpha) * this.smoothRight[1];
      }

      const dx = this.smoothRight[0] - this.smoothLeft[0];
      const dy = this.smoothRight[1] - this.smoothLeft[1];
      this.smoothAngle = Math.atan2(dy, dx);
      this.smoothLeftTilt = alpha * leftTilt + (1 - alpha) * this.smoothLeftTilt;
      this.smoothRightTilt = alpha * rightTilt + (1 - alpha) * this.smoothRightTilt;

      const dist = Math.hypot(dx, dy);
      const normDist = dist / w;
      const rawVel = this.prevNormDist !== null ? (normDist - this.prevNormDist) / dt : 0;
      this.prevNormDist = normDist;
      this.smoothVelocity = 0.25 * rawVel + 0.75 * this.smoothVelocity;
    } else {
      this.currentOpacity = Math.max(0.0, this.currentOpacity - dt / 0.3);
      this.smoothVelocity *= 0.8;
    }

    return {
      isValid: this.currentOpacity > 0.01,
      opacity: this.currentOpacity,
      pLeft: this.smoothLeft || [w * 0.35, h * 0.5],
      pRight: this.smoothRight || [w * 0.65, h * 0.5],
      angle: this.smoothAngle,
      leftTilt: this.smoothLeftTilt,
      rightTilt: this.smoothRightTilt,
      normDist: this.prevNormDist || 0.3,
      velocity: this.smoothVelocity,
      isDrawing: this.smoothVelocity > 0.04,
      isPushing: this.smoothVelocity < -0.04
    };
  }

  /* Pure Cinema Frame Compositor — Zero Text / Zero HUD Overlays on Video Canvas */
  compositeScene(video, motion) {
    const vw = video.videoWidth || 1280;
    const vh = video.videoHeight || 720;

    // Render raw video and accordion into offscreen fxCanvas
    this.fxCanvas.width = vw;
    this.fxCanvas.height = vh;
    const fxCtx = this.fxCtx;

    fxCtx.save();
    if (!this.useVideoFile) {
      fxCtx.translate(vw, 0);
      fxCtx.scale(-1, 1);
    }
    fxCtx.drawImage(video, 0, 0, vw, vh);
    fxCtx.restore();

    if (motion.isValid && motion.opacity > 0.01) {
      this.renderAccordionBellows(fxCtx, motion, vw, vh);
    }

    const ctx = this.ctx;
    const layout = this.currentLayout;

    if (layout === "solo") {
      this.canvasEl.width = vw;
      this.canvasEl.height = vh;
      ctx.drawImage(this.fxCanvas, 0, 0, vw, vh);

    } else if (layout === "side_by_side") {
      // Pure 16:9 Side-by-Side visual comparison without text badges
      const outW = vw * 2;
      const outH = vh;
      this.canvasEl.width = outW;
      this.canvasEl.height = outH;

      // Left: Original video
      ctx.save();
      if (!this.useVideoFile) {
        ctx.translate(vw, 0);
        ctx.scale(-1, 1);
      }
      ctx.drawImage(video, 0, 0, vw, vh);
      ctx.restore();

      // Right: Accordion effect
      ctx.drawImage(this.fxCanvas, vw, 0, vw, vh);

      // Hairline divider
      ctx.strokeStyle = "rgba(255, 255, 255, 0.14)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(vw, 0);
      ctx.lineTo(vw, vh);
      ctx.stroke();

    } else if (layout === "vertical") {
      // Pure 9:16 Vertical comparison (720 x 1280) without text or banners
      const outW = 720;
      const outH = 1280;
      this.canvasEl.width = outW;
      this.canvasEl.height = outH;

      ctx.fillStyle = "#040406";
      ctx.fillRect(0, 0, outW, outH);

      const halfH = Math.round(outH / 2);
      const aspect = vw / vh;
      let newW = outW;
      let newH = Math.round(newW / aspect);
      if (newH > halfH) {
        newH = halfH;
        newW = Math.round(newH * aspect);
      }
      const xOffset = Math.round((outW - newW) / 2);
      const yUpperOffset = Math.round((halfH - newH) / 2);
      const yLowerOffset = Math.round(halfH + (halfH - newH) / 2);

      // Upper: Original video
      ctx.save();
      if (!this.useVideoFile) {
        ctx.translate(xOffset + newW, yUpperOffset);
        ctx.scale(-1, 1);
        ctx.drawImage(video, 0, 0, newW, newH);
      } else {
        ctx.drawImage(video, xOffset, yUpperOffset, newW, newH);
      }
      ctx.restore();

      // Lower: Accordion effect
      ctx.drawImage(this.fxCanvas, xOffset, yLowerOffset, newW, newH);

      // Hairline divider
      ctx.strokeStyle = "rgba(255, 255, 255, 0.14)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(0, halfH);
      ctx.lineTo(outW, halfH);
      ctx.stroke();
    }
  }

  renderAccordionBellows(ctx, m, w, h) {
    ctx.save();
    ctx.globalAlpha = m.opacity;

    const pL = m.pLeft;
    const pR = m.pRight;
    const dx = pR[0] - pL[0];
    const dy = pR[1] - pL[1];
    const dist = Math.hypot(dx, dy);
    if (dist < 1e-4) {
      ctx.restore();
      return;
    }

    const u = [dx / dist, dy / dist];
    const n = [-u[1], u[0]];
    const accH = h * 0.42;
    const bodyW = accH * 0.40;

    const innerL = [pL[0] + u[0] * (bodyW * 0.35), pL[1] + u[1] * (bodyW * 0.35)];
    const innerR = [pR[0] - u[0] * (bodyW * 0.35), pR[1] - u[1] * (bodyW * 0.35)];

    // 1. Bézier Fan Bellows
    this.drawBellows(ctx, innerL, innerR, u, n, accH * 0.88);

    // 2. Left & Right Golden Accordion Bodies
    const leftAngle = m.angle + Math.sin(m.leftTilt - (-Math.PI / 2)) * 0.45;
    const rightAngle = m.angle + Math.sin(m.rightTilt - (-Math.PI / 2)) * 0.45;

    this.drawAccordionBody(ctx, pL[0] - u[0] * (bodyW * 0.15), pL[1] - u[1] * (bodyW * 0.15), bodyW, accH, leftAngle, "left");
    this.drawAccordionBody(ctx, pR[0] + u[0] * (bodyW * 0.15), pR[1] + u[1] * (bodyW * 0.15), bodyW, accH, rightAngle, "right");

    ctx.restore();
  }

  drawBellows(ctx, p0, p2, u, n, bellowsH) {
    const folds = 8;
    const slices = folds * 2;
    const dist = Math.hypot(p2[0] - p0[0], p2[1] - p0[1]);
    const stretch = Math.min(1.0, dist / (bellowsH * 2.2));
    const protrude = bellowsH * 0.07 * (1.2 - 0.7 * stretch);
    const halfH = bellowsH * 0.48;

    const sag = dist * 0.12 * stretch;
    const p1 = [(p0[0] + p2[0]) * 0.5 - n[0] * sag, (p0[1] + p2[1]) * 0.5 - n[1] * sag];

    const topPts = [];
    const botPts = [];

    for (let i = 0; i <= slices; i++) {
      const t = i / slices;
      const cx = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0];
      const cy = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1];

      const tx = 2 * (1 - t) * (p1[0] - p0[0]) + 2 * t * (p2[0] - p1[0]);
      const ty = 2 * (1 - t) * (p1[1] - p0[1]) + 2 * t * (p2[1] - p1[1]);
      const tlen = Math.hypot(tx, ty) || 1;
      const ln = [-ty / tlen, tx / tlen];

      const offset = (i % 2 === 1) ? protrude : -protrude;
      topPts.push([cx + ln[0] * (halfH + offset), cy + ln[1] * (halfH + offset)]);
      botPts.push([cx - ln[0] * (halfH + offset), cy - ln[1] * (halfH + offset)]);
    }

    for (let i = 0; i < slices; i++) {
      ctx.beginPath();
      ctx.moveTo(topPts[i][0], topPts[i][1]);
      ctx.lineTo(topPts[i + 1][0], topPts[i + 1][1]);
      ctx.lineTo(botPts[i + 1][0], botPts[i + 1][1]);
      ctx.lineTo(botPts[i][0], botPts[i][1]);
      ctx.closePath();

      ctx.fillStyle = (i % 2 === 0) ? "#552028" : "#2C1014";
      ctx.fill();

      ctx.strokeStyle = "#E6C168";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(topPts[i + 1][0], topPts[i + 1][1]);
      ctx.lineTo(botPts[i + 1][0], botPts[i + 1][1]);
      ctx.stroke();

      if (i % 2 === 1) {
        ctx.fillStyle = "#E0E0E0";
        ctx.beginPath();
        ctx.arc(topPts[i][0], topPts[i][1], 2.5, 0, Math.PI * 2);
        ctx.arc(botPts[i][0], botPts[i][1], 2.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  drawAccordionBody(ctx, cx, cy, w, h, angle, side) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(angle);

    // Golden metallic body casing
    ctx.beginPath();
    ctx.roundRect(-w / 2, -h / 2, w, h, 16);
    ctx.fillStyle = "#E5B02A";
    ctx.fill();
    ctx.strokeStyle = "#6E450A";
    ctx.lineWidth = 3;
    ctx.stroke();

    // Dark mahogany inner plate
    ctx.beginPath();
    ctx.roundRect(-w / 2 + 8, -h / 2 + 8, w - 16, h - 16, 10);
    ctx.fillStyle = "#38181A";
    ctx.fill();

    if (side === "left") {
      ctx.fillStyle = "#FAF0D0";
      for (let bx = -w / 4; bx <= w / 4; bx += 14) {
        for (let by = -h / 2 + 30; by <= h / 2 - 30; by += 22) {
          ctx.beginPath();
          ctx.arc(bx, by, 4.5, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    } else {
      const keyH = (h - 36) / 14;
      for (let k = 0; k < 14; k++) {
        const ky = -h / 2 + 18 + k * keyH;
        ctx.fillStyle = "#F8F6ED";
        ctx.fillRect(-w / 2 + 12, ky, w - 24, keyH - 2);
        if ([0, 1, 3, 4, 5, 7, 8, 10, 11, 12].includes(k)) {
          ctx.fillStyle = "#1E1E22";
          ctx.fillRect(-w / 2 + 12, ky + keyH * 0.55, (w - 24) * 0.6, keyH * 0.85);
        }
      }
    }

    ctx.restore();
  }

  /* One-Click Video Exporter */
  async startExport() {
    if (!this.useVideoFile || !this.videoSourceEl.duration) {
      alert("請先載入影片檔案後再進行匯出！");
      return;
    }

    this.isExporting = true;
    this.exportModal.classList.add("active");
    this.exportBarFill.style.width = "0%";
    this.exportStatusText.innerText = "正在準備匯出管線...";

    const canvasStream = this.canvasEl.captureStream(30);

    let mixedStream = canvasStream;
    if (this.audio.streamDest) {
      const audioTracks = this.audio.streamDest.stream.getAudioTracks();
      if (audioTracks.length > 0) {
        mixedStream = new MediaStream([...canvasStream.getVideoTracks(), ...audioTracks]);
      }
    }

    this.exportChunks = [];
    const mimeTypes = [
      "video/mp4;codecs=avc1,mp4a.40.2",
      "video/mp4",
      "video/webm;codecs=vp9,opus",
      "video/webm"
    ];
    let selectedMime = "video/webm";
    for (const m of mimeTypes) {
      if (MediaRecorder.isTypeSupported(m)) {
        selectedMime = m;
        break;
      }
    }

    this.exportRecorder = new MediaRecorder(mixedStream, { mimeType: selectedMime });
    this.exportRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) this.exportChunks.push(e.data);
    };

    this.exportRecorder.onstop = () => {
      const ext = selectedMime.includes("mp4") ? "mp4" : "webm";
      const blob = new Blob(this.exportChunks, { type: selectedMime });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `AccordionCinema_${this.currentLayout}_${Date.now()}.${ext}`;
      a.click();

      this.exportModal.classList.remove("active");
      this.isExporting = false;
      this.setPlayPauseGlyph(false);
      this.audio.silence();
    };

    this.videoSourceEl.currentTime = 0;
    await this.videoSourceEl.play();
    this.setPlayPauseGlyph(true);
    this.exportRecorder.start();
    requestAnimationFrame(() => this.processLoop());
  }

  finishExport() {
    if (this.exportRecorder && this.exportRecorder.state === "recording") {
      this.exportRecorder.stop();
    }
  }

  cancelExport() {
    if (this.exportRecorder && this.exportRecorder.state === "recording") {
      this.exportRecorder.stop();
    }
    this.videoSourceEl.pause();
    this.audio.silence();
    this.setPlayPauseGlyph(false);
    this.exportModal.classList.remove("active");
    this.isExporting = false;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  window.palmMotionApp = new PalmMotionWebStudio();
});

/**
 * DSP Interactive Studio - MindMarket Editorial Theme Integration
 * Pure White Cards on Cream Paper with Sky Pop, Coral Pop, and Fresh Grass.
 * Full KaTeX Auto-Rendering Engine for Human-Readable Mathematical Notation.
 */

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initNavigation();
  initKaTeXAutoRender();
  initPart1();
  initPart2();
  initCustomStudio();
  initPresetsGallery();

  // Initialize Animator
  if (window.dspAnimator) {
    window.dspAnimator.init();
  }
});


// =============================================================================
// KATEX AUTO-RENDER HELPER
// =============================================================================

function initKaTeXAutoRender() {
  const tryRender = () => {
    if (typeof renderMathInElement === "function") {
      try {
        renderMathInElement(document.body, {
          delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false }
          ],
          throwOnError: false
        });
      } catch (e) {
        console.warn("KaTeX auto-render error:", e);
      }
    } else {
      setTimeout(tryRender, 100);
    }
  };
  tryRender();
}

function triggerMathRender(el) {
  if (typeof renderMathInElement === "function" && el) {
    try {
      renderMathInElement(el, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false }
        ],
        throwOnError: false
      });
    } catch (e) {}
  }
}


// =============================================================================
// GLOBAL TOAST NOTIFICATIONS
// =============================================================================

function showToast(msg, icon = "fa-circle-check") {
  const toast = document.getElementById("toastNotification");
  const text = document.getElementById("toastMessage");
  if (!toast || !text) return;

  toast.querySelector("i").className = `fa-solid ${icon}`;
  text.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2800);
}


// =============================================================================
// THEME SWITCHER (MINDMARKET WARM CREAM PAPER CANVAS)
// =============================================================================

function initTheme() {
  const toggleBtn = document.getElementById("themeToggleBtn");
  const icon = document.getElementById("themeIcon");
  if (icon) icon.className = "fa-solid fa-feather";

  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      showToast("MindMarket Warm Cream Canvas Active", "fa-palette");
    });
  }
}


// =============================================================================
// NAVIGATION TABS
// =============================================================================

function initNavigation() {
  const tabs = document.querySelectorAll(".tab-btn");
  const contents = document.querySelectorAll(".tab-content");

  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      contents.forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.dataset.tab;
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
        triggerMathRender(targetContent);
      }

      setTimeout(() => {
        window.dispatchEvent(new Event("resize"));
      }, 50);
    });
  });
}


// =============================================================================
// CHART FACTORIES (MINDMARKET COLOR SYSTEM)
// =============================================================================

function createStemChart(canvasId, color = "#2ba0ff", label = "x[n]") {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const ctx = canvas.getContext("2d");

  return new Chart(ctx, {
    type: "scatter",
    data: {
      datasets: [
        {
          label: label,
          data: [],
          borderColor: color,
          backgroundColor: color,
          pointRadius: 4.5,
          pointHoverRadius: 7,
          showLine: false
        },
        {
          label: "Envelope",
          data: [],
          borderColor: color,
          borderWidth: 1.5,
          borderDash: [4, 4],
          pointRadius: 0,
          fill: false,
          showLine: true,
          hidden: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 100 },
      scales: {
        x: {
          grid: { color: "#e0dbce" },
          ticks: { color: "#2c2e2a", font: { family: "JetBrains Mono", size: 10 } }
        },
        y: {
          grid: { color: "#e0dbce" },
          ticks: { color: "#2c2e2a", font: { family: "JetBrains Mono", size: 10 } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `n = ${ctx.raw.x}, ${label} = ${ctx.raw.y.toFixed(4)}`
          }
        }
      }
    },
    plugins: [{
      id: "stemPlugin_" + canvasId,
      beforeDatasetsDraw(chart) {
        const { ctx, scales: { x, y } } = chart;
        const dataset = chart.data.datasets[0];
        const yZero = y.getPixelForValue(0);

        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.6;

        dataset.data.forEach(pt => {
          if (pt.y !== null && !isNaN(pt.y)) {
            const xPix = x.getPixelForValue(pt.x);
            const yPix = y.getPixelForValue(pt.y);
            ctx.beginPath();
            ctx.moveTo(xPix, yZero);
            ctx.lineTo(xPix, yPix);
            ctx.stroke();
          }
        });

        // Zero baseline
        ctx.strokeStyle = "#80827f";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(x.left, yZero);
        ctx.lineTo(x.right, yZero);
        ctx.stroke();

        ctx.restore();
      }
    }]
  });
}

function createFrequencyChart(canvasId, color = "#2ba0ff", label = "|X(f)|") {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const ctx = canvas.getContext("2d");

  return new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          label: label,
          data: [],
          borderColor: color,
          backgroundColor: "rgba(43, 160, 255, 0.08)",
          borderWidth: 2,
          pointRadius: 0,
          fill: true,
          tension: 0.1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 100 },
      scales: {
        x: {
          type: "linear",
          min: -0.5,
          max: 0.5,
          grid: { color: "#e0dbce" },
          ticks: {
            stepSize: 0.1,
            color: "#2c2e2a",
            font: { family: "JetBrains Mono", size: 10 },
            callback: (val) => val.toFixed(1)
          }
        },
        y: {
          grid: { color: "#e0dbce" },
          ticks: { color: "#2c2e2a", font: { family: "JetBrains Mono", size: 10 } }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `f = ${ctx.raw.x.toFixed(3)}, mag = ${ctx.raw.y.toFixed(4)}`
          }
        }
      }
    }
  });
}


// =============================================================================
// TAB 1: PART I - SINGULARITY LAB LOGIC
// =============================================================================

let p1TimeChart = null;
let p1FreqChart = null;
let p1CurrentData = null;
let p1FreqView = "mag";

function initPart1() {
  p1TimeChart = createStemChart("p1TimeCanvas", "#2ba0ff", "x[n]");
  p1FreqChart = createFrequencyChart("p1FreqCanvas", "#2ba0ff", "|X(f)|");

  // Signal type pills
  document.querySelectorAll(".sig-pill").forEach(pill => {
    pill.addEventListener("click", (e) => {
      document.querySelectorAll(".sig-pill").forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      const sigType = pill.dataset.type;
      updatePart1ControlVisibility(sigType);
      fetchPart1Signal();
    });
  });

  // Sliders
  syncSliderAndNum("p1_A_range", "p1_A_num", "p1_A_val", "", () => fetchPart1Signal());
  syncSliderAndNum("p1_n0_range", "p1_n0_num", "p1_n0_val", "", () => fetchPart1Signal());
  syncSliderAndNum("p1_N_range", "p1_N_num", "p1_N_val", "", () => fetchPart1Signal());
  syncSliderAndNum("p1_f0_range", "p1_f0_num", "p1_f0_val", "", () => fetchPart1Signal());
  syncSliderAndNum("p1_phi_range", "p1_phi_num", "p1_phi_val", " rad", () => fetchPart1Signal());
  syncSliderAndNum("p1_alpha_range", "p1_alpha_num", "p1_alpha_val", "", () => fetchPart1Signal());
  syncSliderAndNum("p1_sigma_range", "p1_sigma_num", "p1_sigma_val", "", () => fetchPart1Signal());

  // Range inputs
  const nminInput = document.getElementById("p1_nmin");
  const nmaxInput = document.getElementById("p1_nmax");
  if (nminInput && nmaxInput) {
    const updateRange = () => {
      document.getElementById("p1_range_val").textContent = `[${nminInput.value}, ${nmaxInput.value}]`;
      fetchPart1Signal();
    };
    nminInput.addEventListener("change", updateRange);
    nmaxInput.addEventListener("change", updateRange);
  }

  // Envelope toggle
  const envToggle = document.getElementById("p1_toggle_envelope");
  if (envToggle) {
    envToggle.addEventListener("change", (e) => {
      if (p1TimeChart) {
        p1TimeChart.data.datasets[1].hidden = !e.target.checked;
        p1TimeChart.update();
      }
    });
  }

  // Audio Playback
  const btnAudio = document.getElementById("btnPlayP1Audio");
  if (btnAudio) {
    btnAudio.addEventListener("click", () => {
      if (p1CurrentData && p1CurrentData.x && window.dspAudio) {
        window.dspAudio.playSignalBuffer(p1CurrentData.x, 8000, 1.5);
        showToast("Playing synthesized signal", "fa-volume-high");
      }
    });
  }

  // Frequency view tabs
  const btnMag = document.getElementById("p1_btn_mag");
  const btnPhase = document.getElementById("p1_btn_phase");
  const btnRealImag = document.getElementById("p1_btn_real_imag");

  [btnMag, btnPhase, btnRealImag].forEach(btn => {
    if (btn) {
      btn.addEventListener("click", () => {
        [btnMag, btnPhase, btnRealImag].forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        if (btn === btnMag) p1FreqView = "mag";
        else if (btn === btnPhase) p1FreqView = "phase";
        else p1FreqView = "real_imag";
        renderPart1FreqPlot();
      });
    }
  });

  // Reset Button
  const btnReset = document.getElementById("btnResetP1");
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      document.getElementById("p1_A_range").value = 1.0;
      document.getElementById("p1_A_num").value = 1.0;
      document.getElementById("p1_A_val").textContent = "1.0";
      document.getElementById("p1_n0_range").value = 0;
      document.getElementById("p1_n0_num").value = 0;
      document.getElementById("p1_n0_val").textContent = "0";
      fetchPart1Signal();
      showToast("Parameters reset to default");
    });
  }

  fetchPart1Signal();
}

function updatePart1ControlVisibility(sigType) {
  const badge = document.getElementById("part1SigBadge");
  if (badge) badge.textContent = sigType;

  document.getElementById("row_p1_N").style.display = (sigType === "rect") ? "block" : "none";
  document.getElementById("row_p1_f0").style.display = (sigType === "sin" || sigType === "cos") ? "block" : "none";
  document.getElementById("row_p1_phi").style.display = (sigType === "sin" || sigType === "cos") ? "block" : "none";
  document.getElementById("row_p1_alpha").style.display = (sigType === "exponential") ? "block" : "none";
  document.getElementById("row_p1_sigma").style.display = (sigType === "gaussian") ? "block" : "none";
}

function syncSliderAndNum(rangeId, numId, valDisplayId, suffix = "", onChange) {
  const range = document.getElementById(rangeId);
  const num = document.getElementById(numId);
  const valDisp = document.getElementById(valDisplayId);

  if (range && num) {
    range.addEventListener("input", (e) => {
      num.value = e.target.value;
      if (valDisp) valDisp.textContent = `${e.target.value}${suffix}`;
      if (onChange) onChange();
    });

    num.addEventListener("change", (e) => {
      range.value = e.target.value;
      if (valDisp) valDisp.textContent = `${e.target.value}${suffix}`;
      if (onChange) onChange();
    });
  }
}

async function fetchPart1Signal() {
  const activePill = document.querySelector(".sig-pill.active");
  const sigType = activePill ? activePill.dataset.type : "step";

  const payload = {
    type: sigType,
    A: parseFloat(document.getElementById("p1_A_num").value) || 1.0,
    n0: parseInt(document.getElementById("p1_n0_num").value) || 0,
    N: parseInt(document.getElementById("p1_N_num").value) || 4,
    f0: parseFloat(document.getElementById("p1_f0_num").value) || 0.1,
    phi: parseFloat(document.getElementById("p1_phi_num").value) || 0.0,
    alpha: parseFloat(document.getElementById("p1_alpha_num").value) || 0.8,
    sigma: parseFloat(document.getElementById("p1_sigma_num").value) || 3.0,
    n_min: parseInt(document.getElementById("p1_nmin").value) || -20,
    n_max: parseInt(document.getElementById("p1_nmax").value) || 20
  };

  try {
    const resp = await fetch("/api/signal/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (data.status === "success") {
      p1CurrentData = data;
      renderPart1View(data);
    }
  } catch (err) {
    console.error("Part I API error:", err);
  }
}

function renderPart1View(data) {
  const formulaBox = document.getElementById("p1_katex_formula");
  if (formulaBox && window.katex) {
    const latexExpr = `x[n] = ${data.latex}`;
    try {
      window.katex.render(latexExpr, formulaBox, { displayMode: true, throwOnError: false });
    } catch (e) {
      formulaBox.textContent = latexExpr;
    }
  }

  const s = data.stats;
  document.getElementById("p1_stat_energy").textContent = s.energy.toFixed(3);
  document.getElementById("p1_stat_power").textContent = s.power.toFixed(4);
  document.getElementById("p1_stat_peak").textContent = s.peak.toFixed(3);
  document.getElementById("p1_stat_mean").textContent = s.mean.toFixed(4);
  document.getElementById("p1_stat_support").textContent = s.support;

  const pts = data.n.map((n, i) => ({ x: n, y: data.x[i] }));
  p1TimeChart.data.datasets[0].data = pts;
  p1TimeChart.data.datasets[1].data = pts;
  p1TimeChart.update();

  renderPart1FreqPlot();
}

function renderPart1FreqPlot() {
  if (!p1CurrentData || !p1FreqChart) return;
  const f = p1CurrentData.f;

  let yVals = p1CurrentData.mag_X;
  let label = "|X(f)| (Magnitude)";
  let color = "#2ba0ff";

  if (p1FreqView === "phase") {
    yVals = p1CurrentData.phase_X;
    label = "∠X(f) (Phase in Radians)";
    color = "#80827f";
  } else if (p1FreqView === "real_imag") {
    yVals = p1CurrentData.real_X;
    label = "Re{X(f)} (Real Component)";
    color = "#48a820";
  }

  const pts = f.map((fVal, i) => ({ x: fVal, y: yVals[i] }));
  p1FreqChart.data.datasets[0].data = pts;
  p1FreqChart.data.datasets[0].label = label;
  p1FreqChart.data.datasets[0].borderColor = color;
  p1FreqChart.update();
}


// =============================================================================
// TAB 2: PART II - CONVOLUTION & DTFT MATRIX (3x2 GRID)
// =============================================================================

let p2Charts = {};
let p2LastResult = null;

function initPart2() {
  p2Charts.x = createStemChart("p2Canvas_x", "#2ba0ff", "x[n]");
  p2Charts.Xmag = createFrequencyChart("p2Canvas_Xmag", "#2ba0ff", "|X(f)|");
  p2Charts.h = createStemChart("p2Canvas_h", "#ff705d", "h[n]");
  p2Charts.Hmag = createFrequencyChart("p2Canvas_Hmag", "#ff705d", "|H(f)|");
  p2Charts.y = createStemChart("p2Canvas_y", "#48a820", "y[n] = x[n] * h[n]");
  p2Charts.Ymag = createVerificationChart("p2Canvas_Ymag");

  // Presets
  document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".preset-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      loadPart2Preset(btn.dataset.preset);
    });
  });

  // Inputs
  ["p2_x_type", "p2_x_A", "p2_x_n0", "p2_x_N", "p2_x_f0",
   "p2_h_type", "p2_h_A", "p2_h_n0", "p2_h_N", "p2_h_f0"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", () => fetchPart2Analysis());
  });

  // Export
  const btnExport = document.getElementById("btnExportMatplotlib");
  if (btnExport) {
    btnExport.addEventListener("click", exportMatplotlibPNG);
  }

  // Send to Animator
  const btnSendAnim = document.getElementById("btnSendToAnimator");
  if (btnSendAnim) {
    btnSendAnim.addEventListener("click", () => {
      const specX = getSpecFromUI("x");
      const specH = getSpecFromUI("h");
      if (window.dspAnimator) {
        window.dspAnimator.setSignals(specX, specH);
      }
      document.querySelector('.tab-btn[data-tab="tab-animator"]').click();
      showToast("Loaded signals into Step-by-Step Animator", "fa-film");
    });
  }

  fetchPart2Analysis();
}

function createVerificationChart(canvasId) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return null;
  const ctx = canvas.getContext("2d");

  return new Chart(ctx, {
    type: "line",
    data: {
      datasets: [
        {
          label: "|Y(f)| (Direct DTFT of y[n])",
          data: [],
          borderColor: "#48a820",
          borderWidth: 2.2,
          pointRadius: 0,
          fill: false
        },
        {
          label: "|X(f) · H(f)| (Product of Transforms)",
          data: [],
          borderColor: "#ff705d",
          borderWidth: 1.8,
          borderDash: [5, 4],
          pointRadius: 0,
          fill: false
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 100 },
      scales: {
        x: {
          type: "linear",
          min: -0.5,
          max: 0.5,
          grid: { color: "#e0dbce" },
          ticks: {
            stepSize: 0.1,
            color: "#2c2e2a",
            font: { family: "JetBrains Mono", size: 10 },
            callback: (val) => val.toFixed(1)
          }
        },
        y: {
          grid: { color: "#e0dbce" },
          ticks: { color: "#2c2e2a", font: { family: "JetBrains Mono", size: 10 } }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: "top",
          labels: { color: "#2c2e2a", boxWidth: 12, font: { size: 10 } }
        },
        tooltip: {
          callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.raw.y.toFixed(4)}`
          }
        }
      }
    }
  });
}

function getSpecFromUI(prefix) {
  const type = document.getElementById(`p2_${prefix}_type`).value;
  const A = parseFloat(document.getElementById(`p2_${prefix}_A`).value) || 1.0;
  const n0 = parseInt(document.getElementById(`p2_${prefix}_n0`).value) || 0;
  const N = parseInt(document.getElementById(`p2_${prefix}_N`).value) || 4;
  const f0 = parseFloat(document.getElementById(`p2_${prefix}_f0`).value) || 0.1;

  const nContainer = document.getElementById(`p2_${prefix}_N_container`);
  const fContainer = document.getElementById(`p2_${prefix}_f0_container`);
  if (nContainer) nContainer.style.display = (type === "rect") ? "block" : "none";
  if (fContainer) fContainer.style.display = (type === "sin" || type === "cos") ? "block" : "none";

  return { type, A, n0, N, f0, n_min: -20, n_max: 20 };
}

function loadPart2Preset(presetId) {
  if (presetId === "sec4") {
    setSpecToUI("x", { type: "step", A: 2.0, n0: 2 });
    setSpecToUI("h", { type: "impulse", A: 1.0, n0: 1 });
  } else if (presetId === "rect_pulses") {
    setSpecToUI("x", { type: "rect", A: 3.0, n0: 2, N: 5 });
    setSpecToUI("h", { type: "rect", A: 2.0, n0: -1, N: 4 });
  } else if (presetId === "cosine_ma") {
    setSpecToUI("x", { type: "cos", A: 2.0, n0: 0, f0: 0.1 });
    setSpecToUI("h", { type: "rect", A: 0.333333, n0: 0, N: 3 });
  } else if (presetId === "delay_echo") {
    setSpecToUI("x", { type: "rect", A: 2.0, n0: 0, N: 3 });
    setSpecToUI("h", { type: "impulse", A: 1.0, n0: 4 });
  } else if (presetId === "differentiator") {
    setSpecToUI("x", { type: "step", A: 1.5, n0: 0 });
    setSpecToUI("h", { type: "impulse", A: 1.0, n0: 0 });
  }
  fetchPart2Analysis();
}

function setSpecToUI(prefix, spec) {
  if (spec.type) document.getElementById(`p2_${prefix}_type`).value = spec.type;
  if (spec.A !== undefined) document.getElementById(`p2_${prefix}_A`).value = spec.A;
  if (spec.n0 !== undefined) document.getElementById(`p2_${prefix}_n0`).value = spec.n0;
  if (spec.N !== undefined) document.getElementById(`p2_${prefix}_N`).value = spec.N;
  if (spec.f0 !== undefined) document.getElementById(`p2_${prefix}_f0`).value = spec.f0;
}

async function fetchPart2Analysis() {
  const specX = getSpecFromUI("x");
  const specH = getSpecFromUI("h");

  try {
    const resp = await fetch("/api/convolution/compute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ x: specX, h: specH })
    });
    const data = await resp.json();
    if (data.status === "success") {
      p2LastResult = data;
      renderPart2View(data);
    }
  } catch (err) {
    console.error("Part II calculation error:", err);
  }
}

function renderPart2View(data) {
  const t = data.time_domain;
  const f = data.freq_domain;
  const m = data.metrics;

  const xLatex = document.getElementById("p2_x_latex");
  const hLatex = document.getElementById("p2_h_latex");
  if (xLatex && window.katex) {
    window.katex.render(`x[n] = ${t.x_latex}`, xLatex, { throwOnError: false });
  }
  if (hLatex && window.katex) {
    window.katex.render(`h[n] = ${t.h_latex}`, hLatex, { throwOnError: false });
  }

  document.getElementById("p2_max_err").textContent = m.max_absolute_error.toExponential(3);
  document.getElementById("p2_mse_err").textContent = m.mean_squared_error.toExponential(3);

  // Subplot 1: x[n] (Sky Pop)
  p2Charts.x.data.datasets[0].data = t.nx.map((n, i) => ({ x: n, y: t.x[i] }));
  p2Charts.x.update();

  // Subplot 2: |X(f)| (Sky Pop)
  p2Charts.Xmag.data.datasets[0].data = f.f.map((fVal, i) => ({ x: fVal, y: f.mag_X[i] }));
  p2Charts.Xmag.update();

  // Subplot 3: h[n] (Coral Pop)
  p2Charts.h.data.datasets[0].data = t.nh.map((n, i) => ({ x: n, y: t.h[i] }));
  p2Charts.h.update();

  // Subplot 4: |H(f)| (Coral Pop)
  p2Charts.Hmag.data.datasets[0].data = f.f.map((fVal, i) => ({ x: fVal, y: f.mag_H[i] }));
  p2Charts.Hmag.update();

  // Subplot 5: y[n] (Fresh Grass)
  p2Charts.y.data.datasets[0].data = t.ny_display.map((n, i) => ({ x: n, y: t.y_display[i] }));
  p2Charts.y.update();

  // Subplot 6: Verification Overlay
  p2Charts.Ymag.data.datasets[0].data = f.f.map((fVal, i) => ({ x: fVal, y: f.mag_Y[i] }));
  p2Charts.Ymag.data.datasets[1].data = f.f.map((fVal, i) => ({ x: fVal, y: f.mag_Y_prod[i] }));
  p2Charts.Ymag.update();
}

async function exportMatplotlibPNG() {
  const specX = getSpecFromUI("x");
  const specH = getSpecFromUI("h");
  showToast("Rendering publication figure...", "fa-camera");

  try {
    const resp = await fetch("/api/export/figure", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ x: specX, h: specH })
    });
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "part2_dsp_analysis_3x2.png";
    document.body.appendChild(a);
    a.click();
    a.remove();
    showToast("Downloaded part2_dsp_analysis_3x2.png", "fa-circle-check");
  } catch (e) {
    console.error("Download failed:", e);
    showToast("Failed to download figure", "fa-circle-xmark");
  }
}


// =============================================================================
// TAB 4: CUSTOM FORMULA & ARBITRARY SEQUENCE STUDIO
// =============================================================================

let customTimeChart = null;
let customFreqChart = null;
let customMode = "expr";

function initCustomStudio() {
  customTimeChart = createStemChart("customTimeCanvas", "#2ba0ff", "x[n]");
  customFreqChart = createFrequencyChart("customFreqCanvas", "#2ba0ff", "|X(f)|");

  const btnExpr = document.getElementById("btnModeExpr");
  const btnArray = document.getElementById("btnModeArray");
  const exprBox = document.getElementById("customExprContainer");
  const arrayBox = document.getElementById("customArrayContainer");

  if (btnExpr && btnArray) {
    btnExpr.addEventListener("click", () => {
      btnExpr.classList.add("active");
      btnArray.classList.remove("active");
      exprBox.style.display = "block";
      arrayBox.style.display = "none";
      customMode = "expr";
    });

    btnArray.addEventListener("click", () => {
      btnArray.classList.add("active");
      btnExpr.classList.remove("active");
      exprBox.style.display = "none";
      arrayBox.style.display = "block";
      customMode = "array";
    });
  }

  document.querySelectorAll(".chip").forEach(chip => {
    chip.addEventListener("click", () => {
      document.getElementById("customExprInput").value = chip.dataset.expr;
      evaluateCustomSignal();
    });
  });

  const btnEval = document.getElementById("btnEvalCustom");
  if (btnEval) {
    btnEval.addEventListener("click", evaluateCustomSignal);
  }

  const btnUseAsX = document.getElementById("btnUseCustomAsX");
  if (btnUseAsX) {
    btnUseAsX.addEventListener("click", () => {
      document.querySelector('.tab-btn[data-tab="tab-part2"]').click();
      showToast("Custom signal ready in Convolution Studio", "fa-check");
    });
  }

  evaluateCustomSignal();
}

async function evaluateCustomSignal() {
  const A = parseFloat(document.getElementById("customARange").value) || 1.0;
  document.getElementById("customAVal").textContent = A.toFixed(1);

  let payload = { A: A, n_min: -20, n_max: 20 };

  if (customMode === "expr") {
    payload.type = "custom_expr";
    payload.expression = document.getElementById("customExprInput").value;
  } else {
    payload.type = "custom_array";
    payload.values = document.getElementById("customArrayInput").value;
    payload.origin_idx = parseInt(document.getElementById("customOriginRange").value) || 0;
    document.getElementById("customOriginVal").textContent = payload.origin_idx;
  }

  try {
    const resp = await fetch("/api/signal/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const data = await resp.json();
    if (data.status === "success") {
      customTimeChart.data.datasets[0].data = data.n.map((n, i) => ({ x: n, y: data.x[i] }));
      customTimeChart.update();

      customFreqChart.data.datasets[0].data = data.f.map((fVal, i) => ({ x: fVal, y: data.mag_X[i] }));
      customFreqChart.update();

      showToast("Signal evaluated successfully", "fa-circle-check");
    }
  } catch (err) {
    console.error("Custom evaluate error:", err);
  }
}


// =============================================================================
// TAB 5: PRESETS GALLERY
// =============================================================================

function initPresetsGallery() {
  document.querySelectorAll(".load-preset-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const presetId = btn.dataset.preset;
      document.querySelector('.tab-btn[data-tab="tab-part2"]').click();
      loadPart2Preset(presetId);
      showToast(`Loaded ${presetId} preset into studio`, "fa-wand-magic-sparkles");
    });
  });
}

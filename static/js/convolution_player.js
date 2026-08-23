/**
 * DSP Interactive Studio - Convolution Step-by-Step Animator
 * MindMarket Storybook Palette: Sky Pop, Coral Pop, and Fresh Grass.
 */

class ConvolutionAnimator {
  constructor() {
    this.currentN = 0;
    this.minN = -20;
    this.maxN = 20;
    this.isPlaying = false;
    this.speedMs = 1000;
    this.timer = null;

    // Canvas Chart instances
    this.chartXk = null;
    this.chartHnmk = null;
    this.chartProd = null;
    this.chartYacc = null;

    this.specX = { type: "rect", N: 5, n0: 2, A: 3.0, n_min: -20, n_max: 20 };
    this.specH = { type: "rect", N: 4, n0: -1, A: 2.0, n_min: -20, n_max: 20 };
  }

  init() {
    this.setupListeners();
    this.initCharts();
    this.fetchStep(0);
  }

  setSignals(x, h) {
    this.specX = JSON.parse(JSON.stringify(x));
    this.specH = JSON.parse(JSON.stringify(h));
    this.currentN = 0;
    this.fetchStep(0);
  }

  setupListeners() {
    const btnPlay = document.getElementById("btnAnimPlayToggle");
    const btnPrev = document.getElementById("btnAnimPrev");
    const btnNext = document.getElementById("btnAnimNext");
    const btnFirst = document.getElementById("btnAnimFirst");
    const btnLast = document.getElementById("btnAnimLast");
    const scrub = document.getElementById("animScrubRange");

    if (btnPlay) btnPlay.addEventListener("click", () => this.togglePlay());
    if (btnPrev) btnPrev.addEventListener("click", () => this.step(-1));
    if (btnNext) btnNext.addEventListener("click", () => this.step(1));
    if (btnFirst) btnFirst.addEventListener("click", () => this.goTo(this.minN));
    if (btnLast) btnLast.addEventListener("click", () => this.goTo(this.maxN));

    if (scrub) {
      scrub.addEventListener("input", (e) => {
        this.goTo(parseInt(e.target.value, 10));
      });
    }

    document.querySelectorAll(".speed-controls .pill-sm").forEach(btn => {
      btn.addEventListener("click", (e) => {
        document.querySelectorAll(".speed-controls .pill-sm").forEach(b => b.classList.remove("active"));
        e.target.classList.add("active");
        this.speedMs = parseInt(e.target.dataset.speed, 10);
        if (this.isPlaying) {
          this.pause();
          this.play();
        }
      });
    });
  }

  togglePlay() {
    if (this.isPlaying) {
      this.pause();
    } else {
      this.play();
    }
  }

  play() {
    this.isPlaying = true;
    const btnIcon = document.getElementById("animPlayIcon");
    const btnText = document.getElementById("animPlayText");
    if (btnIcon) btnIcon.className = "fa-solid fa-pause";
    if (btnText) btnText.textContent = "Pause";

    this.timer = setInterval(() => {
      if (this.currentN >= this.maxN) {
        this.currentN = this.minN;
      } else {
        this.currentN += 1;
      }
      this.fetchStep(this.currentN);
    }, this.speedMs);
  }

  pause() {
    this.isPlaying = false;
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    const btnIcon = document.getElementById("animPlayIcon");
    const btnText = document.getElementById("animPlayText");
    if (btnIcon) btnIcon.className = "fa-solid fa-play";
    if (btnText) btnText.textContent = "Play Animation";
  }

  step(direction) {
    this.pause();
    let nextN = this.currentN + direction;
    if (nextN < this.minN) nextN = this.minN;
    if (nextN > this.maxN) nextN = this.maxN;
    this.goTo(nextN);
  }

  goTo(nVal) {
    this.currentN = nVal;
    const scrub = document.getElementById("animScrubRange");
    if (scrub) scrub.value = nVal;
    const lbl = document.getElementById("animCurrentNVal");
    if (lbl) lbl.textContent = `n = ${nVal}`;
    this.fetchStep(nVal);
  }

  async fetchStep(nVal) {
    try {
      const resp = await fetch("/api/convolution/step", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          x: this.specX,
          h: this.specH,
          current_n: nVal
        })
      });
      const data = await resp.json();
      if (data.status === "success") {
        this.updateView(data);
      }
    } catch (err) {
      console.error("Error in fetchStep:", err);
    }
  }

  updateView(data) {
    this.minN = data.ny_range[0];
    this.maxN = data.ny_range[1];

    const scrub = document.getElementById("animScrubRange");
    if (scrub) {
      scrub.min = this.minN;
      scrub.max = this.maxN;
      scrub.value = data.current_n;
    }

    const lbl = document.getElementById("animCurrentNVal");
    if (lbl) lbl.textContent = `n = ${data.current_n}`;

    if (window.dspAudio && Math.abs(data.current_y_val) > 1e-4) {
      const clickPitch = 340 + Math.min(500, Math.abs(data.current_y_val) * 50);
      window.dspAudio.playClickTone(clickPitch, 0.03);
    }

    // 1. Stationary x[k] (Sky Pop)
    this.updateStemChart(this.chartXk, data.k_axis, data.x_k, "#2ba0ff", "x[k]");

    // 2. Flipped & Shifted h[n - k] (Coral Pop)
    this.updateStemChart(this.chartHnmk, data.k_axis, data.h_flipped_shifted, "#ff705d", `h[${data.current_n} - k]`);

    // 3. Pointwise Product p[k] (Coral Pop)
    this.updateStemChart(this.chartProd, data.k_axis, data.prod_k, "#ff705d", `x[k]·h[${data.current_n} - k]`);

    // 4. Accumulated Output y[n] (Fresh Grass)
    const nyAll = [];
    const yAll = [];
    const colors = [];
    const pointRadii = [];

    const accumDict = {};
    data.y_accumulated.forEach(item => { accumDict[item.n] = item.y; });

    for (let n = this.minN; n <= this.maxN; n++) {
      nyAll.push(n);
      if (n in accumDict) {
        yAll.push(accumDict[n]);
        if (n === data.current_n) {
          colors.push("#2c2e2a"); // Ink Black focus marker
          pointRadii.push(6);
        } else {
          colors.push("#48a820"); // Fresh grass marker
          pointRadii.push(4);
        }
      } else {
        yAll.push(null);
        colors.push("transparent");
        pointRadii.push(0);
      }
    }

    this.updateAccumulatedChart(this.chartYacc, nyAll, yAll, colors, pointRadii);

    // 5. Update Arithmetic KaTeX Breakdown
    this.renderArithmetic(data);
  }

  renderArithmetic(data) {
    const arithBox = document.getElementById("animArithBody");
    if (!arithBox) return;

    const terms = data.terms;
    let equationStr = `y[${data.current_n}] = \\sum_{k} x[k]\\,h[${data.current_n} - k] = `;

    if (terms.length === 0) {
      equationStr += `0.0 \\quad \\text{(No overlapping samples)}`;
    } else {
      const termStrings = terms.map(t => `(${t.x_k} \\times ${t.h_nmk})`);
      if (terms.length > 6) {
        equationStr += termStrings.slice(0, 5).join(" + ") + ` + \\dots (${terms.length} \\text{ terms}) = \\mathbf{${data.current_y_val.toFixed(3)}}`;
      } else {
        equationStr += termStrings.join(" + ") + ` = \\mathbf{${data.current_y_val.toFixed(3)}}`;
      }
    }

    if (window.katex) {
      try {
        window.katex.render(equationStr, arithBox, { displayMode: true, throwOnError: false });
      } catch (e) {
        arithBox.textContent = equationStr;
      }
    } else {
      arithBox.textContent = equationStr;
    }
  }

  initCharts() {
    this.chartXk = this.createStemChart("animCanvas_xk", "#2ba0ff", "x[k]");
    this.chartHnmk = this.createStemChart("animCanvas_hnmk", "#ff705d", "h[n - k]");
    this.chartProd = this.createStemChart("animCanvas_prod", "#ff705d", "p[k]");
    this.chartYacc = this.createAccumChart("animCanvas_yacc");
  }

  createStemChart(canvasId, color, label) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext("2d");

    return new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [{
          label: label,
          data: [],
          borderColor: color,
          backgroundColor: color,
          pointRadius: 4,
          pointHoverRadius: 6,
          showLine: false
        }]
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
              label: (ctx) => `k = ${ctx.raw.x}, val = ${ctx.raw.y.toFixed(3)}`
            }
          }
        }
      },
      plugins: [{
        id: "stemLinesPlugin_" + canvasId,
        beforeDatasetsDraw(chart) {
          const { ctx, scales: { x, y } } = chart;
          const dataset = chart.data.datasets[0];
          const yZero = y.getPixelForValue(0);

          ctx.save();
          ctx.strokeStyle = color;
          ctx.lineWidth = 1.5;

          dataset.data.forEach(pt => {
            const xPix = x.getPixelForValue(pt.x);
            const yPix = y.getPixelForValue(pt.y);
            ctx.beginPath();
            ctx.moveTo(xPix, yZero);
            ctx.lineTo(xPix, yPix);
            ctx.stroke();
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

  createAccumChart(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext("2d");

    return new Chart(ctx, {
      type: "scatter",
      data: {
        datasets: [{
          label: "y[n]",
          data: [],
          borderColor: "#48a820",
          backgroundColor: [],
          pointRadius: [],
          showLine: false
        }]
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
          legend: { display: false }
        }
      },
      plugins: [{
        id: "stemLinesAccumPlugin_" + canvasId,
        beforeDatasetsDraw(chart) {
          const { ctx, scales: { x, y } } = chart;
          const dataset = chart.data.datasets[0];
          const yZero = y.getPixelForValue(0);

          ctx.save();
          ctx.strokeStyle = "#48a820";
          ctx.lineWidth = 1.8;

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

  updateStemChart(chart, xVals, yVals, color, label) {
    if (!chart) return;
    const points = xVals.map((k, i) => ({ x: k, y: yVals[i] }));
    chart.data.datasets[0].data = points;
    chart.update();
  }

  updateAccumulatedChart(chart, xVals, yVals, colors, pointRadii) {
    if (!chart) return;
    const points = [];
    const validColors = [];
    const validRadii = [];

    xVals.forEach((n, i) => {
      if (yVals[i] !== null) {
        points.push({ x: n, y: yVals[i] });
        validColors.push(colors[i]);
        validRadii.push(pointRadii[i]);
      }
    });

    chart.data.datasets[0].data = points;
    chart.data.datasets[0].pointBackgroundColor = validColors;
    chart.data.datasets[0].pointBorderColor = validColors;
    chart.data.datasets[0].pointRadius = validRadii;
    chart.update();
  }
}

window.dspAnimator = new ConvolutionAnimator();

#!/usr/bin/env python3
"""
DSP Interactive Studio - Web Backend Application
Flask-powered REST API and SPA server for Discrete-Time Signals,
Convolution, and DTFT Analysis.
"""

import io
import math
import base64
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server rendering
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, jsonify, send_file

# Import the core DSP homework modules
from part1 import (
    unit_impulse,
    unit_step,
    rect_pulse,
    sinusoid,
    cosinusoid,
    signum,
    unit_ramp,
    get_default_time_axis,
    plot_stem_signal,
    DEFAULT_N_MIN,
    DEFAULT_N_MAX
)
from part2 import (
    dtft,
    direct_convolve,
    align_to_range,
    get_default_freq_axis,
    plot_part2_analysis,
    DEFAULT_F_MIN,
    DEFAULT_F_MAX,
    DEFAULT_NUM_FREQ
)

app = Flask(__name__)


# =============================================================================
# SIGNAL GENERATION HELPER
# =============================================================================

def generate_signal_from_spec(spec: dict, default_n_min: int = -20, default_n_max: int = 20):
    """
    Generate discrete-time signal x[n] and its mathematical LaTeX label from a config dictionary.
    """
    sig_type = spec.get("type", "step").lower()
    n_min = int(spec.get("n_min", default_n_min))
    n_max = int(spec.get("n_max", default_n_max))
    if n_min >= n_max:
        n_min, n_max = -20, 20
        
    n = get_default_time_axis(n_min, n_max)
    A = float(spec.get("A", 1.0))
    n0 = int(spec.get("n0", 0))
    
    # Format shift string for LaTeX display
    shift_str = f" - {n0}" if n0 > 0 else (f" + {-n0}" if n0 < 0 else "")
    amp_str = f"{A:g}" if A != 1.0 else ""
    if A == -1.0:
        amp_str = "-"

    if sig_type == "impulse":
        _, x = unit_impulse(n, n0=n0, A=A)
        latex = f"{amp_str}\\delta[n{shift_str}]" if amp_str != "" else f"\\delta[n{shift_str}]"
        name = f"Unit Impulse: {amp_str}δ[n{shift_str}]"

    elif sig_type == "step":
        _, x = unit_step(n, n0=n0, A=A)
        latex = f"{amp_str}u[n{shift_str}]" if amp_str != "" else f"u[n{shift_str}]"
        name = f"Unit Step: {amp_str}u[n{shift_str}]"

    elif sig_type == "rect":
        N = max(1, int(spec.get("N", 4)))
        _, x = rect_pulse(n, N=N, n0=n0, A=A)
        latex = f"{amp_str}\\mathrm{{rect}}_{{{N}}}[n{shift_str}]" if amp_str != "" else f"\\mathrm{{rect}}_{{{N}}}[n{shift_str}]"
        name = f"Rect Pulse: {amp_str}rect_{N}[n{shift_str}]"

    elif sig_type == "sin":
        f0 = float(spec.get("f0", 0.1))
        phi = float(spec.get("phi", 0.0))
        _, x = sinusoid(n, f0=f0, n0=n0, A=A, phi=phi)
        phi_str = f" + {phi:.2f}" if abs(phi) > 1e-4 else ""
        latex = f"{amp_str}\\sin(2\\pi \\cdot {f0:g}(n{shift_str}){phi_str})" if amp_str != "" else f"\\sin(2\\pi \\cdot {f0:g}(n{shift_str}){phi_str})"
        name = f"Sinusoid: {A:g} sin(2π·{f0:g}(n{shift_str}))"

    elif sig_type == "cos":
        f0 = float(spec.get("f0", 0.1))
        phi = float(spec.get("phi", 0.0))
        _, x = cosinusoid(n, f0=f0, n0=n0, A=A, phi=phi)
        phi_str = f" + {phi:.2f}" if abs(phi) > 1e-4 else ""
        latex = f"{amp_str}\\cos(2\\pi \\cdot {f0:g}(n{shift_str}){phi_str})" if amp_str != "" else f"\\cos(2\\pi \\cdot {f0:g}(n{shift_str}){phi_str})"
        name = f"Cosinusoid: {A:g} cos(2π·{f0:g}(n{shift_str}))"

    elif sig_type == "sgn":
        _, x = signum(n, n0=n0, A=A)
        latex = f"{amp_str}\\mathrm{{sgn}}[n{shift_str}]" if amp_str != "" else f"\\mathrm{{sgn}}[n{shift_str}]"
        name = f"Signum: {amp_str}sgn[n{shift_str}]"

    elif sig_type == "ramp":
        _, x = unit_ramp(n, n0=n0, A=A)
        latex = f"{amp_str}r[n{shift_str}]" if amp_str != "" else f"r[n{shift_str}]"
        name = f"Unit Ramp: {amp_str}r[n{shift_str}]"

    elif sig_type == "exponential":
        alpha = float(spec.get("alpha", 0.8))
        m = n - n0
        # a^m * u[m]
        x = np.where(m >= 0, A * (alpha ** m), 0.0)
        latex = f"{amp_str}({alpha:g})^{{n{shift_str}}} u[n{shift_str}]"
        name = f"Exponential Decay: {A:g}({alpha:g})^(n{shift_str}) u[n{shift_str}]"

    elif sig_type == "gaussian":
        sigma = max(0.5, float(spec.get("sigma", 3.0)))
        m = n - n0
        x = A * np.exp(-0.5 * (m / sigma) ** 2)
        latex = f"{amp_str}\\exp\\left(-\\frac{{(n{shift_str})^2}}{{2 \\cdot {sigma:g}^2}}\\right)"
        name = f"Gaussian Pulse: {A:g} exp(-(n{shift_str})^2 / 2σ^2)"

    elif sig_type == "custom_array":
        raw_vals = spec.get("values", [1.0])
        origin_idx = int(spec.get("origin_idx", 0))
        if isinstance(raw_vals, str):
            try:
                raw_vals = [float(v.strip()) for v in raw_vals.split(",") if v.strip()]
            except Exception:
                raw_vals = [1.0]
        raw_vals = np.asarray(raw_vals, dtype=float)
        L = len(raw_vals)
        n_start = -origin_idx
        n_end = n_start + L - 1
        n_sig = np.arange(n_start, n_end + 1, dtype=int)
        
        # Place onto standard n or custom range
        x = np.zeros(len(n), dtype=float)
        for i, idx in enumerate(n_sig):
            if n_min <= idx <= n_max:
                x[idx - n_min] = raw_vals[i] * A
        latex = f"\\text{{Arbitrary Sequence }} [{', '.join(f'{v:g}' for v in raw_vals[:8])}{'...' if L>8 else ''}]"
        name = f"Custom Array (L={L})"

    elif sig_type == "custom_expr":
        expr = spec.get("expression", "sin(2*pi*0.1*n)")
        x = evaluate_custom_expression(expr, n, A, n0)
        latex = f"{amp_str} \\left( {expr} \\right)"
        name = f"Expression: {expr}"

    else:
        _, x = unit_step(n, n0=n0, A=A)
        latex = f"u[n{shift_str}]"
        name = f"Unit Step: u[n{shift_str}]"

    return n, x, latex, name


def evaluate_custom_expression(expr: str, n: np.ndarray, A: float = 1.0, n0: int = 0) -> np.ndarray:
    """Safely evaluate mathematical expressions using numpy and elementary functions."""
    scope = {
        "n": n,
        "np": np,
        "pi": np.pi,
        "e": np.e,
        "A": A,
        "n0": n0,
        "sin": lambda t: np.sin(t),
        "cos": lambda t: np.cos(t),
        "tan": lambda t: np.tan(t),
        "exp": lambda t: np.exp(t),
        "abs": lambda t: np.abs(t),
        "sqrt": lambda t: np.sqrt(np.maximum(0, t)),
        "sinc": lambda t: np.sinc(t / np.pi),
        "delta": lambda m, shift=0: np.where(m == shift, 1.0, 0.0),
        "step": lambda m, shift=0: np.where(m >= shift, 1.0, 0.0),
        "rect": lambda m, width=4, shift=0: np.where((m >= shift) & (m < shift + width), 1.0, 0.0),
        "sgn": lambda m, shift=0: np.sign(m - shift).astype(float),
        "ramp": lambda m, shift=0: np.where(m >= shift, (m - shift).astype(float), 0.0)
    }
    try:
        res = eval(expr, {"__builtins__": {}}, scope)
        res = np.asarray(res, dtype=float)
        if res.shape != n.shape:
            res = np.full_like(n, float(res), dtype=float)
        return A * res
    except Exception:
        return np.zeros(len(n), dtype=float)


def compute_signal_stats(n: np.ndarray, x: np.ndarray) -> dict:
    """Calculate key signal metrics (energy, power, bounds, mean, peak)."""
    abs_x = np.abs(x)
    energy = float(np.sum(abs_x ** 2))
    power = float(np.mean(abs_x ** 2))
    peak = float(np.max(abs_x)) if len(abs_x) > 0 else 0.0
    mean_val = float(np.mean(x)) if len(x) > 0 else 0.0
    
    nz_indices = n[abs_x > 1e-9]
    if len(nz_indices) > 0:
        support_start = int(nz_indices[0])
        support_end = int(nz_indices[-1])
        support_str = f"[{support_start}, {support_end}] ({support_end - support_start + 1} samples)"
    else:
        support_str = "None (All Zero)"

    return {
        "energy": energy,
        "power": power,
        "peak": peak,
        "mean": mean_val,
        "support": support_str,
        "samples_count": len(n),
        "n_min": int(n[0]),
        "n_max": int(n[-1])
    }


# =============================================================================
# REST API ENDPOINTS
# =============================================================================

@app.route("/")
def index():
    """Render main SPA frontend."""
    return render_template("index.html")


@app.route("/api/signal/generate", methods=["POST"])
def api_generate_signal():
    """Generate discrete-time signal and its single-signal DTFT spectrum."""
    data = request.get_json() or {}
    n_min = int(data.get("n_min", -20))
    n_max = int(data.get("n_max", 20))
    
    n, x, latex, name = generate_signal_from_spec(data, n_min, n_max)
    stats = compute_signal_stats(n, x)

    # Compute DTFT directly via part2.dtft
    f = get_default_freq_axis(-0.5, 0.5, 501)
    _, X = dtft(x, n, f)
    mag_X = np.abs(X).tolist()
    phase_X = np.angle(X).tolist()
    real_X = np.real(X).tolist()
    imag_X = np.imag(X).tolist()

    return jsonify({
        "status": "success",
        "n": n.tolist(),
        "x": x.tolist(),
        "latex": latex,
        "name": name,
        "stats": stats,
        "f": f.tolist(),
        "mag_X": mag_X,
        "phase_X": phase_X,
        "real_X": real_X,
        "imag_X": imag_X
    })


@app.route("/api/convolution/compute", methods=["POST"])
def api_compute_convolution():
    """
    Perform direct convolution and DTFT analysis on signals x[n] and h[n].
    Strictly uses direct definitions from part1.py and part2.py.
    """
    data = request.get_json() or {}
    spec_x = data.get("x", {"type": "step", "n0": 2, "A": 2.0, "n_min": -20, "n_max": 20})
    spec_h = data.get("h", {"type": "impulse", "n0": 1, "A": 1.0, "n_min": -20, "n_max": 20})

    nx, x, x_latex, x_name = generate_signal_from_spec(spec_x)
    nh, h, h_latex, h_name = generate_signal_from_spec(spec_h)

    # 1. Frequency axis
    f = get_default_freq_axis(DEFAULT_F_MIN, DEFAULT_F_MAX, DEFAULT_NUM_FREQ)

    # 2. Compute DTFT of x[n] and h[n] directly
    _, X = dtft(x, nx, f)
    _, H = dtft(h, nh, f)
    mag_X = np.abs(X)
    mag_H = np.abs(H)

    # 3. Direct convolution summation
    ny_full, y_full = direct_convolve(x, nx, h, nh)

    # Align y to standard display range [-20, 20]
    n_display = get_default_time_axis(DEFAULT_N_MIN, DEFAULT_N_MAX)
    y_aligned = align_to_range(ny_full, y_full, n_display)

    # 4. Compute DTFT of convolution on its full exact support
    _, Y_full_dtft = dtft(y_full, ny_full, f)
    mag_Y = np.abs(Y_full_dtft)

    # 5. Theoretical frequency-domain product: X(f) * H(f)
    Y_prod = X * H
    mag_Y_prod = np.abs(Y_prod)

    # Error metrics
    abs_diff = np.abs(mag_Y - mag_Y_prod)
    max_err = float(np.max(abs_diff))
    mse_err = float(np.mean(abs_diff ** 2))
    mae_err = float(np.mean(abs_diff))

    return jsonify({
        "status": "success",
        "time_domain": {
            "nx": nx.tolist(),
            "x": x.tolist(),
            "x_latex": x_latex,
            "x_name": x_name,
            "nh": nh.tolist(),
            "h": h.tolist(),
            "h_latex": h_latex,
            "h_name": h_name,
            "ny_display": n_display.tolist(),
            "y_display": y_aligned.tolist(),
            "ny_full": ny_full.tolist(),
            "y_full": y_full.tolist(),
        },
        "freq_domain": {
            "f": f.tolist(),
            "mag_X": mag_X.tolist(),
            "mag_H": mag_H.tolist(),
            "mag_Y": mag_Y.tolist(),
            "mag_Y_prod": mag_Y_prod.tolist(),
            "error_diff": abs_diff.tolist()
        },
        "metrics": {
            "max_absolute_error": max_err,
            "mean_squared_error": mse_err,
            "mean_absolute_error": mae_err,
            "passed": bool(max_err < 1e-10)
        }
    })


@app.route("/api/convolution/step", methods=["POST"])
def api_convolution_step():
    """
    Step-by-step calculation for the interactive Convolution Flip & Shift Visualizer.
    For a given target index n_val, returns:
      - Dummy index k axis
      - Stationary sequence x[k]
      - Flipped and shifted sequence h[n_val - k]
      - Product sequence p[k] = x[k] * h[n_val - k]
      - Non-zero arithmetic multiplication terms
      - Output accumulated up to step n_val
    """
    data = request.get_json() or {}
    spec_x = data.get("x", {"type": "rect", "N": 4, "n0": 0, "A": 2.0})
    spec_h = data.get("h", {"type": "rect", "N": 3, "n0": 0, "A": 1.0})
    step_n = int(data.get("current_n", 0))

    nx, x, x_latex, _ = generate_signal_from_spec(spec_x)
    nh, h, h_latex, _ = generate_signal_from_spec(spec_h)

    # Full convolution result
    ny_full, y_full = direct_convolve(x, nx, h, nh)

    # Restrict / expand dummy variable k to encompass non-zero regions
    k_min = min(int(nx[0]), int(ny_full[0]), step_n - int(nh[-1])) - 3
    k_max = max(int(nx[-1]), int(ny_full[-1]), step_n - int(nh[0])) + 3
    k_axis = np.arange(k_min, k_max + 1, dtype=int)

    # x[k] evaluated on k_axis
    dict_x = dict(zip(nx, x))
    x_k = np.array([dict_x.get(k, 0.0) for k in k_axis], dtype=float)

    # h[n - k] evaluated on k_axis
    dict_h = dict(zip(nh, h))
    h_flipped_shifted = np.array([dict_h.get(step_n - k, 0.0) for k in k_axis], dtype=float)

    # Pointwise product
    prod_k = x_k * h_flipped_shifted

    # Compute step value y[step_n]
    current_y_val = float(np.sum(prod_k))

    # Detailed arithmetic breakdown
    terms = []
    for k_val, x_val, h_val, p_val in zip(k_axis, x_k, h_flipped_shifted, prod_k):
        if abs(p_val) > 1e-9 or (abs(x_val) > 1e-9 and abs(h_val) > 1e-9):
            terms.append({
                "k": int(k_val),
                "x_k": float(x_val),
                "h_nmk": float(h_val),
                "prod": float(p_val)
            })

    # Accumulated output array for points <= step_n
    y_accumulated = []
    for idx_n, n_val in enumerate(ny_full):
        if n_val <= step_n:
            y_accumulated.append({"n": int(n_val), "y": float(y_full[idx_n])})

    return jsonify({
        "status": "success",
        "current_n": step_n,
        "k_axis": k_axis.tolist(),
        "x_k": x_k.tolist(),
        "h_flipped_shifted": h_flipped_shifted.tolist(),
        "prod_k": prod_k.tolist(),
        "current_y_val": current_y_val,
        "terms": terms,
        "ny_range": [int(ny_full[0]), int(ny_full[-1])],
        "y_accumulated": y_accumulated,
        "x_latex": x_latex,
        "h_latex": h_latex
    })


@app.route("/api/export/figure", methods=["POST"])
def api_export_figure():
    """
    Generate and stream high-resolution Matplotlib 3x2 Figure PNG matching
    the exact homework report formatting.
    """
    data = request.get_json() or {}
    spec_x = data.get("x", {"type": "step", "n0": 2, "A": 2.0, "n_min": -20, "n_max": 20})
    spec_h = data.get("h", {"type": "impulse", "n0": 1, "A": 1.0, "n_min": -20, "n_max": 20})

    nx, x, x_latex, _ = generate_signal_from_spec(spec_x)
    nh, h, h_latex, _ = generate_signal_from_spec(spec_h)

    fig, _ = plot_part2_analysis(
        x=x, nx=nx,
        h=h, nh=nh,
        x_label_title=rf"$x[n] = {x_latex}$",
        h_label_title=rf"$h[n] = {h_latex}$",
        save_path=None
    )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    
    return send_file(
        buf,
        mimetype="image/png",
        as_attachment=True,
        download_name="dsp_3x2_analysis.png"
    )


@app.route("/api/presets", methods=["GET"])
def api_get_presets():
    """Return built-in educational and homework presets."""
    presets = [
        {
            "id": "sec4",
            "title": "HW Section 4 Example",
            "description": "Convolution of delayed unit step and impulse: 2·u[n - 2] * δ[n - 1]",
            "category": "Homework",
            "x": {"type": "step", "n0": 2, "A": 2.0, "n_min": -20, "n_max": 20},
            "h": {"type": "impulse", "n0": 1, "A": 1.0, "n_min": -20, "n_max": 20},
            "theory": "y[n] = 2·u[n - 3]. DTFT property holds with ~10^-14 machine precision error."
        },
        {
            "id": "rect_pulses",
            "title": "Rectangular Pulses Convolution",
            "description": "Convolution of two boxcar pulses resulting in a trapezoidal pulse: 3·rect_5[n - 2] * 2·rect_4[n + 1]",
            "category": "Homework",
            "x": {"type": "rect", "N": 5, "n0": 2, "A": 3.0, "n_min": -20, "n_max": 20},
            "h": {"type": "rect", "N": 4, "n0": -1, "A": 2.0, "n_min": -20, "n_max": 20},
            "theory": "Convolution of rects yields a trapezoid in time and sinc product in frequency."
        },
        {
            "id": "cosine_ma",
            "title": "Cosine + 3-Point Moving Average",
            "description": "Low-pass filtering a discrete cosine signal with a moving average filter: 2·cos(2π·0.1·n) * (1/3)·rect_3[n]",
            "category": "Homework",
            "x": {"type": "cos", "f0": 0.1, "n0": 0, "A": 2.0, "n_min": -20, "n_max": 20},
            "h": {"type": "rect", "N": 3, "n0": 0, "A": 1.0 / 3.0, "n_min": -20, "n_max": 20},
            "theory": "Moving average attenuates the cosine amplitude by H(0.1) = sin(3π·0.1)/(3·sin(π·0.1))."
        },
        {
            "id": "delay_echo",
            "title": "Echo / Delay Filter",
            "description": "Discrete-time echo simulator with primary signal plus attenuated 4-sample reflection: x[n] * (δ[n] + 0.6·δ[n - 4])",
            "category": "Audio & Filters",
            "x": {"type": "rect", "N": 3, "n0": 0, "A": 2.0, "n_min": -20, "n_max": 20},
            "h": {"type": "custom_expr", "expression": "delta(n, 0) + 0.6*delta(n, 4)", "A": 1.0, "n_min": -20, "n_max": 20},
            "theory": "Produces direct output plus delayed replica creating a comb filter spectrum."
        },
        {
            "id": "differentiator",
            "title": "Discrete Differentiator (High-Pass)",
            "description": "First difference operator y[n] = x[n] - x[n - 1] acting on a step signal: u[n] * (δ[n] - δ[n - 1])",
            "category": "Audio & Filters",
            "x": {"type": "step", "n0": 0, "A": 1.5, "n_min": -20, "n_max": 20},
            "h": {"type": "custom_expr", "expression": "delta(n, 0) - delta(n, 1)", "A": 1.0, "n_min": -20, "n_max": 20},
            "theory": "Difference of a unit step produces a unit impulse δ[n]."
        },
        {
            "id": "exp_decay",
            "title": "Exponential Decay Filter",
            "description": "First-order IIR-like truncated impulse response: (0.75)^n u[n]",
            "category": "Filters",
            "x": {"type": "rect", "N": 4, "n0": 0, "A": 2.0, "n_min": -20, "n_max": 20},
            "h": {"type": "exponential", "alpha": 0.75, "n0": 0, "A": 1.0, "n_min": -20, "n_max": 20},
            "theory": "Classic single-pole low-pass frequency response."
        }
    ]
    return jsonify({"status": "success", "presets": presets})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

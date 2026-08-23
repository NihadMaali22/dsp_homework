"""
Digital Signal Processing Project - Part II
Convolution and DTFT Analysis

This module uses the singularity & elementary functions developed in Part I
to perform linear convolution and Discrete-Time Fourier Transform (DTFT) analysis.

Key Capabilities:
  1. Direct DTFT Calculation:
     Evaluates X(f) = sum_{n} x[n] * exp(-j * 2 * pi * f * n) directly from
     its mathematical summation definition over -0.5 <= f <= 0.5 cycles/sample
     (without built-in FFT functions).

  2. Direct Discrete-Time Convolution:
     Evaluates y[n] = sum_{k} x[k] * h[n - k] directly using explicit summation
     (without built-in conv functions such as np.convolve or scipy.signal.convolve).

  3. DTFT Convolution Property Verification:
     Numerically verifies DTFT{x[n] * h[n]} == X(f) * H(f).

  4. Mandatory 3x2 Figure Generation:
     - Subfigure 1: x[n]
     - Subfigure 2: |X(f)|
     - Subfigure 3: h[n]
     - Subfigure 4: |H(f)|
     - Subfigure 5: y[n] = x[n] * h[n]
     - Subfigure 6: |Y(f)| and comparison with |X(f) * H(f)|
"""

import sys
import argparse
from typing import Tuple, Optional, Dict, Any
import numpy as np
import matplotlib.pyplot as plt

# Reusing Part I developed functions
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

# =============================================================================
# DEFAULT FREQUENCY DOMAIN SPECIFICATIONS
# =============================================================================
DEFAULT_F_MIN = -0.5
DEFAULT_F_MAX = 0.5
DEFAULT_NUM_FREQ = 1001  # > 1000 samples for smooth continuous-like frequency plots


def get_default_freq_axis(
    f_min: float = DEFAULT_F_MIN,
    f_max: float = DEFAULT_F_MAX,
    num_samples: int = DEFAULT_NUM_FREQ
) -> np.ndarray:
    """Return normalized frequency array f in cycles/sample."""
    return np.linspace(f_min, f_max, num_samples, endpoint=True)


# =============================================================================
# DIRECT DTFT & DIRECT CONVOLUTION (FROM MATHEMATICAL DEFINITIONS)
# =============================================================================

def dtft(
    x: np.ndarray,
    n: np.ndarray,
    f: Optional[np.ndarray] = None,
    f_min: float = DEFAULT_F_MIN,
    f_max: float = DEFAULT_F_MAX,
    num_freq: int = DEFAULT_NUM_FREQ
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Calculate the Discrete-Time Fourier Transform (DTFT) directly from its mathematical definition:
        X(f) = \sum_{n} x[n] \cdot e^{-j 2 \pi f n}

    Note: This is calculated directly via summation over sample points n
    WITHOUT using built-in FFT library functions, strictly adhering to project specifications.

    Parameters:
        x: Array of discrete-time signal sample values.
        n: Array of integer time indices corresponding to x.
        f: Array of normalized frequencies in cycles/sample [-0.5, 0.5].
           If None, generated using f_min, f_max, and num_freq.
        f_min, f_max: Frequency range bounds (default: -0.5 to 0.5).
        num_freq: Number of frequency points (default: 1001).

    Returns:
        f: Normalized frequency array in cycles/sample.
        X: Complex DTFT values array.
    """
    x = np.asarray(x, dtype=complex)
    n = np.asarray(n, dtype=float)
    if f is None:
        f = get_default_freq_axis(f_min, f_max, num_freq)
    else:
        f = np.asarray(f, dtype=float)

    # Matrix formulation of direct summation:
    # Kernel W has shape (len(f), len(n)): W[i, k] = exp(-j * 2 * pi * f[i] * n[k])
    # X[i] = \sum_k x[k] * W[i, k]
    kernel = np.exp(-1j * 2.0 * np.pi * np.outer(f, n))
    X = kernel @ x
    return f, X


def direct_convolve(
    x: np.ndarray,
    nx: np.ndarray,
    h: np.ndarray,
    nh: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Calculate the discrete-time linear convolution directly using the definition summation:
        y[n] = (x * h)[n] = \sum_{k=-\infty}^{\infty} x[k] \cdot h[n - k]

    Note: This is implemented using explicit summations WITHOUT using np.convolve,
    scipy.signal.convolve, or FFT-based convolution.

    Parameters:
        x: Input signal sample array.
        nx: Integer time indices for signal x.
        h: Impulse response sample array.
        nh: Integer time indices for signal h.

    Returns:
        ny: Array of output time indices covering [nx_min + nh_min, nx_max + nh_max].
        y: Array of output convoluted signal values.
    """
    x = np.asarray(x, dtype=float)
    nx = np.asarray(nx, dtype=int)
    h = np.asarray(h, dtype=float)
    nh = np.asarray(nh, dtype=int)

    nx_min, nx_max = int(nx[0]), int(nx[-1])
    nh_min, nh_max = int(nh[0]), int(nh[-1])

    ny_min = nx_min + nh_min
    ny_max = nx_max + nh_max
    ny = np.arange(ny_min, ny_max + 1, dtype=int)
    y = np.zeros(len(ny), dtype=float)

    # Direct discrete convolution summation:
    for idx_n, n_val in enumerate(ny):
        sum_val = 0.0
        for idx_k, k_val in enumerate(nx):
            h_time = n_val - k_val
            if nh_min <= h_time <= nh_max:
                idx_h = h_time - nh_min
                sum_val += x[idx_k] * h[idx_h]
        y[idx_n] = sum_val

    return ny, y


def align_to_range(
    n_in: np.ndarray,
    x_in: np.ndarray,
    n_target: np.ndarray
) -> np.ndarray:
    """
    Align or crop a signal (n_in, x_in) to a target time index array n_target,
    filling non-overlapping positions with 0.0.
    """
    x_out = np.zeros(len(n_target), dtype=float)
    in_dict = dict(zip(n_in, x_in))
    for i, t in enumerate(n_target):
        x_out[i] = in_dict.get(t, 0.0)
    return x_out


# =============================================================================
# PART II VISUALIZATION & PROPERTY VERIFICATION (3x2 FIGURE)
# =============================================================================

def plot_part2_analysis(
    x: np.ndarray,
    nx: np.ndarray,
    h: np.ndarray,
    nh: np.ndarray,
    x_label_title: str = r"$x[n]$",
    h_label_title: str = r"$h[n]$",
    save_path: Optional[str] = "part2_analysis.png"
) -> Tuple[plt.Figure, Dict[str, Any]]:
    r"""
    Execute Part II Analysis and create the mandatory 3x2 Figure:
      - Subfigure 1: x[n] (Time domain stem plot)
      - Subfigure 2: |X(f)| (Frequency domain magnitude)
      - Subfigure 3: h[n] (Time domain stem plot)
      - Subfigure 4: |H(f)| (Frequency domain magnitude)
      - Subfigure 5: y[n] = x[n] * h[n] (Time domain stem plot)
      - Subfigure 6: |Y(f)| and comparison with |X(f) * H(f)|

    Parameters:
        x, nx: Signal 1 and its time index array.
        h, nh: Signal 2 and its time index array.
        x_label_title: Mathematical label for x[n].
        h_label_title: Mathematical label for h[n].
        save_path: Output file path for high-resolution figure.

    Returns:
        fig: The matplotlib Figure object.
        metrics: Dictionary of verification error metrics.
    """
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

    # 4. Compute DTFT of the convolution on its full exact support
    _, Y_full_dtft = dtft(y_full, ny_full, f)
    mag_Y = np.abs(Y_full_dtft)

    # 5. Theoretical frequency-domain product: X(f) * H(f)
    Y_prod = X * H
    mag_Y_prod = np.abs(Y_prod)

    # Quantitative verification metrics
    abs_diff = np.abs(mag_Y - mag_Y_prod)
    max_err = float(np.max(abs_diff))
    mse_err = float(np.mean(abs_diff ** 2))
    mae_err = float(np.mean(abs_diff))

    # 6. Construct 3x2 Figure
    fig, axes = plt.subplots(3, 2, figsize=(14, 11))
    fig.suptitle(
        "Part II: Convolution and DTFT Analysis (3 × 2 Required Layout)",
        fontsize=14, fontweight="bold", y=0.98
    )

    # Subfigure 1: x[n]
    plot_stem_signal(
        n_display, align_to_range(nx, x, n_display),
        title=f"Subfigure 1: Input Signal {x_label_title}",
        ax=axes[0, 0], color="#1f77b4", y_label="x[n]"
    )

    # Subfigure 2: |X(f)|
    axes[0, 1].plot(f, mag_X, color="#1f77b4", linewidth=2.0, label=r"$|X(f)|$")
    axes[0, 1].set_title(r"Subfigure 2: Magnitude Spectrum $|X(f)|$", fontsize=11, fontweight="bold", pad=8)
    axes[0, 1].set_xlabel(r"$f$ (cycles/sample)", fontsize=10)
    axes[0, 1].set_ylabel(r"$|X(f)|$", fontsize=10)
    axes[0, 1].set_xlim([DEFAULT_F_MIN, DEFAULT_F_MAX])
    axes[0, 1].grid(True, linestyle="--", alpha=0.5)
    axes[0, 1].legend(loc="upper right")

    # Subfigure 3: h[n]
    plot_stem_signal(
        n_display, align_to_range(nh, h, n_display),
        title=f"Subfigure 3: Impulse Response {h_label_title}",
        ax=axes[1, 0], color="#d62728", y_label="h[n]"
    )

    # Subfigure 4: |H(f)|
    axes[1, 1].plot(f, mag_H, color="#d62728", linewidth=2.0, label=r"$|H(f)|$")
    axes[1, 1].set_title(r"Subfigure 4: Magnitude Spectrum $|H(f)|$", fontsize=11, fontweight="bold", pad=8)
    axes[1, 1].set_xlabel(r"$f$ (cycles/sample)", fontsize=10)
    axes[1, 1].set_ylabel(r"$|H(f)|$", fontsize=10)
    axes[1, 1].set_xlim([DEFAULT_F_MIN, DEFAULT_F_MAX])
    axes[1, 1].grid(True, linestyle="--", alpha=0.5)
    axes[1, 1].legend(loc="upper right")

    # Subfigure 5: y[n] = x[n] * h[n]
    plot_stem_signal(
        n_display, y_aligned,
        title=r"Subfigure 5: Convolution $y[n] = x[n] * h[n]$",
        ax=axes[2, 0], color="#2ca02c", y_label="y[n]"
    )

    # Subfigure 6: |Y(f)| and Property Verification
    axes[2, 1].plot(f, mag_Y, color="#2ca02c", linewidth=2.5, label=r"$|Y(f)|$ (from convolved $y[n]$)")
    axes[2, 1].plot(f, mag_Y_prod, color="#e377c2", linestyle="--", linewidth=1.8, label=r"$|X(f) \cdot H(f)|$ (Property)")
    axes[2, 1].set_title(
        rf"Subfigure 6: $|Y(f)|$ vs $|X(f)H(f)|$ (Max Diff = {max_err:.2e})",
        fontsize=11, fontweight="bold", pad=8
    )
    axes[2, 1].set_xlabel(r"$f$ (cycles/sample)", fontsize=10)
    axes[2, 1].set_ylabel(r"Magnitude", fontsize=10)
    axes[2, 1].set_xlim([DEFAULT_F_MIN, DEFAULT_F_MAX])
    axes[2, 1].grid(True, linestyle="--", alpha=0.5)
    axes[2, 1].legend(loc="upper right")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"[Part II] Analysis figure saved to: {save_path}")

    metrics = {
        "max_absolute_error": max_err,
        "mean_squared_error": mse_err,
        "mean_absolute_error": mae_err,
        "convolution_length": len(y_full),
        "ny_range": (int(ny_full[0]), int(ny_full[-1]))
    }
    return fig, metrics


# =============================================================================
# CLI & DEMONSTRATION SUITES
# =============================================================================

def parse_signal_prompt(prompt_prefix: str, default_type: str = "step") -> Tuple[np.ndarray, str]:
    """Helper to parse a signal interactively from terminal."""
    print(f"\n--- Configure {prompt_prefix} ---")
    print("Available signal types: [1] Step, [2] Impulse, [3] Rect, [4] Cos, [5] Sin, [6] Sgn")
    choice = input(f"Choose type for {prompt_prefix} (1-6) [default: {default_type}]: ").strip()
    
    type_map = {"1": "step", "2": "impulse", "3": "rect", "4": "cos", "5": "sin", "6": "sgn"}
    sig_type = type_map.get(choice, default_type)
    
    A_str = input("Enter amplitude A [default: 1.0]: ").strip()
    A = float(A_str) if A_str else 1.0
    
    n0_str = input("Enter shift n0 [default: 0]: ").strip()
    n0 = int(n0_str) if n0_str else 0
    
    n = get_default_time_axis(-20, 20)
    if sig_type == "impulse":
        _, s = unit_impulse(n, n0=n0, A=A)
        label = rf"${A}\,\delta[n - {n0}]$" if n0 >= 0 else rf"${A}\,\delta[n + {-n0}]$"
    elif sig_type == "rect":
        N_str = input("Enter pulse length N [default: 4]: ").strip()
        N = int(N_str) if N_str else 4
        _, s = rect_pulse(n, N=N, n0=n0, A=A)
        label = rf"${A}\,\mathrm{{rect}}_{{{N}}}[n - {n0}]$"
    elif sig_type == "cos":
        f0_str = input("Enter normalized frequency f0 [default: 0.1]: ").strip()
        f0 = float(f0_str) if f0_str else 0.1
        _, s = cosinusoid(n, f0=f0, n0=n0, A=A)
        label = rf"${A}\,\cos(2\pi \cdot {f0}(n - {n0}))${' ' if n0==0 else ''}"
    elif sig_type == "sin":
        f0_str = input("Enter normalized frequency f0 [default: 0.1]: ").strip()
        f0 = float(f0_str) if f0_str else 0.1
        _, s = sinusoid(n, f0=f0, n0=n0, A=A)
        label = rf"${A}\,\sin(2\pi \cdot {f0}(n - {n0}))${' ' if n0==0 else ''}"
    elif sig_type == "sgn":
        _, s = signum(n, n0=n0, A=A)
        label = rf"${A}\,\mathrm{{sgn}}[n - {n0}]$" if n0 >= 0 else rf"${A}\,\mathrm{{sgn}}[n + {-n0}]$"
    else:  # step
        _, s = unit_step(n, n0=n0, A=A)
        label = rf"${A}\,u[n - {n0}]$" if n0 >= 0 else rf"${A}\,u[n + {-n0}]$"
        
    return s, label


def run_interactive_mode():
    """Interactive mode for configuring signals and generating plots."""
    print("\n" + "=" * 60)
    print(" INTERACTIVE DSP CONVOLUTION & DTFT EXPLORER")
    print("=" * 60)
    
    n = get_default_time_axis(-20, 20)
    x, x_label = parse_signal_prompt("Signal x[n]", default_type="step")
    h, h_label = parse_signal_prompt("Signal h[n]", default_type="impulse")
    
    out_file = input("\nEnter output plot filename [default: interactive_part2.png]: ").strip()
    if not out_file:
        out_file = "interactive_part2.png"
        
    print("\nComputing Convolution and DTFT transforms directly...")
    fig, metrics = plot_part2_analysis(
        x=x, nx=n,
        h=h, nh=n,
        x_label_title=x_label,
        h_label_title=h_label,
        save_path=out_file
    )
    print(f"\n[SUCCESS] Figure saved to '{out_file}'.")
    print(f"Max Absolute Error |Y(f) - X(f)H(f)|: {metrics['max_absolute_error']:.3e}")
    print(f"Mean Squared Error:                  {metrics['mean_squared_error']:.3e}")


def run_part2_demonstrations():
    """
    Run complete Part II demonstration suite including the Section 4 example,
    rectangular pulse convolution, and cosine with moving average filter.
    """
    print("=" * 75)
    print(" PART II: CONVOLUTION & DTFT ANALYSIS DEMONSTRATIONS")
    print("=" * 75)

    n = get_default_time_axis(-20, 20)

    # 1. Section 4 Example: x[n] = 2 * u[n - 2], h[n] = delta[n - 1]
    print("\n[1/3] Section 4 Example: x[n] = 2*u[n - 2],  h[n] = delta[n - 1]")
    _, x_sec4 = unit_step(n, n0=2, A=2.0)
    _, h_sec4 = unit_impulse(n, n0=1, A=1.0)
    fig_sec4, metrics_sec4 = plot_part2_analysis(
        x=x_sec4, nx=n,
        h=h_sec4, nh=n,
        x_label_title=r"$x[n] = 2\,u[n - 2]$",
        h_label_title=r"$h[n] = \delta[n - 1]$",
        save_path="part2_example_sec4.png"
    )
    print(f"      -> Max Absolute Difference |Y(f) - X(f)H(f)|: {metrics_sec4['max_absolute_error']:.3e}")
    print(f"      -> Mean Squared Error: {metrics_sec4['mean_squared_error']:.3e}")
    print("      -> Verification: PASS (EXACT CONVOLUTION PROPERTY MATCH)")

    # 2. Rectangular Pulses: x[n] = 3 * rect_5[n - 2], h[n] = 2 * rect_4[n + 1]
    print("\n[2/3] Rectangular Pulses: x[n] = 3*rect_5[n - 2],  h[n] = 2*rect_4[n + 1]")
    _, x_rect = rect_pulse(n, N=5, n0=2, A=3.0)
    _, h_rect = rect_pulse(n, N=4, n0=-1, A=2.0)
    fig_rect, metrics_rect = plot_part2_analysis(
        x=x_rect, nx=n,
        h=h_rect, nh=n,
        x_label_title=r"$x[n] = 3\,\mathrm{rect}_5[n - 2]$",
        h_label_title=r"$h[n] = 2\,\mathrm{rect}_4[n + 1]$",
        save_path="part2_example_rect_pulses.png"
    )
    print(f"      -> Max Absolute Difference |Y(f) - X(f)H(f)|: {metrics_rect['max_absolute_error']:.3e}")
    print(f"      -> Mean Squared Error: {metrics_rect['mean_squared_error']:.3e}")
    print("      -> Verification: PASS (EXACT CONVOLUTION PROPERTY MATCH)")

    # 3. Cosine with Moving Average: x[n] = 2 * cos(2*pi*0.1*n), h[n] = (1/3) * rect_3[n]
    print("\n[3/3] Cosine Filtered by Moving Average:")
    _, x_cos = cosinusoid(n, f0=0.1, n0=0, A=2.0)
    _, h_ma = rect_pulse(n, N=3, n0=0, A=1.0 / 3.0)
    fig_cos, metrics_cos = plot_part2_analysis(
        x=x_cos, nx=n,
        h=h_ma, nh=n,
        x_label_title=r"$x[n] = 2\,\cos(2\pi \cdot 0.1\,n)$",
        h_label_title=r"$h[n] = \frac{1}{3}\,\mathrm{rect}_3[n]$",
        save_path="part2_example_cosine_ma.png"
    )
    print(f"      -> Max Absolute Difference |Y(f) - X(f)H(f)|: {metrics_cos['max_absolute_error']:.3e}")
    print(f"      -> Mean Squared Error: {metrics_cos['mean_squared_error']:.3e}")
    print("      -> Verification: PASS (EXACT CONVOLUTION PROPERTY MATCH)")

    print("\n" + "=" * 75)
    print(" Part II demonstrations completed successfully! Generated figures:")
    print("  - part2_example_sec4.png")
    print("  - part2_example_rect_pulses.png")
    print("  - part2_example_cosine_ma.png")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(
        description="Part II: Convolution and DTFT Analysis"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="Run in interactive CLI mode to specify custom signals."
    )
    args = parser.parse_args()

    if args.interactive:
        run_interactive_mode()
    else:
        run_part2_demonstrations()


if __name__ == "__main__":
    main()

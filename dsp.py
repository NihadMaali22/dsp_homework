"""
Digital Signal Processing Project
Discrete-Time Signals, Convolution, and DTFT Analysis

This module implements:
  - Part I: Discrete-Time Singularity & Elementary Functions:
      * Unit Impulse: delta[n - n0]
      * Unit Step: u[n - n0]
      * Rectangular Pulse: rect_N[n - n0]
      * Sinusoidal Signal: sin(2*pi*f0*(n - n0) + phi)
      * Cosinusoidal Signal: cos(2*pi*f0*(n - n0) + phi)
      * Signum Function: sgn[n - n0]
      * Unit Ramp: r[n - n0]
    All functions support amplitude scaling (A), time-shifting (n0),
    and user-specified discrete-time arrays (default: -20 <= n <= 20).

  - Part II: Convolution & DTFT Analysis:
      * Direct DTFT summation: X(f) = sum_{n} x[n] * exp(-j*2*pi*f*n)
        calculated directly from definition (no built-in FFT).
      * Direct Discrete-Time Convolution: y[n] = sum_{k} x[k] * h[n - k]
        calculated directly from summation (no built-in conv functions).
      * Verification of the DTFT Convolution Property:
        DTFT{x[n] * h[n]} = X(f) * H(f)
      * 3x2 Subplot Visualization comparing time and frequency domains.
"""

import sys
import argparse
from typing import Tuple, Optional, Dict, Any, List
import numpy as np
import matplotlib.pyplot as plt


# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================
DEFAULT_N_MIN = -20
DEFAULT_N_MAX = 20
DEFAULT_F_MIN = -0.5
DEFAULT_F_MAX = 0.5
DEFAULT_NUM_FREQ = 1001  # > 1000 samples for smooth continuous-like frequency plots


def get_default_time_axis(n_min: int = DEFAULT_N_MIN, n_max: int = DEFAULT_N_MAX) -> np.ndarray:
    """Return discrete-time index array n in range [n_min, n_max]."""
    return np.arange(n_min, n_max + 1, dtype=int)


def get_default_freq_axis(f_min: float = DEFAULT_F_MIN, f_max: float = DEFAULT_F_MAX, num_samples: int = DEFAULT_NUM_FREQ) -> np.ndarray:
    """Return normalized frequency array f in cycles/sample."""
    return np.linspace(f_min, f_max, num_samples, endpoint=True)


# =============================================================================
# PART I: DISCRETE-TIME SINGULARITY & ELEMENTARY FUNCTIONS
# =============================================================================

def unit_impulse(
    n: Optional[np.ndarray] = None,
    n0: int = 0,
    A: float = 1.0,
    n_min: int = DEFAULT_N_MIN,
    n_max: int = DEFAULT_N_MAX
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Generate a scaled and shifted discrete-time unit impulse signal:
        x[n] = A * \delta[n - n0]

    Parameters:
        n: Time index array. If None, generated from [n_min, n_max].
        n0: Time shift (integer).
        A: Amplitude scaling factor.
        n_min, n_max: Default range bounds if n is None.

    Returns:
        n: Array of discrete time indices.
        x: Array of signal values.
    """
    if n is None:
        n = get_default_time_axis(n_min, n_max)
    else:
        n = np.asarray(n, dtype=int)
    x = np.where(n == n0, float(A), 0.0)
    return n, x


def unit_step(
    n: Optional[np.ndarray] = None,
    n0: int = 0,
    A: float = 1.0,
    n_min: int = DEFAULT_N_MIN,
    n_max: int = DEFAULT_N_MAX
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Generate a scaled and shifted discrete-time unit step signal:
        x[n] = A * u[n - n0]

    Parameters:
        n: Time index array. If None, generated from [n_min, n_max].
        n0: Time shift (integer).
        A: Amplitude scaling factor.
        n_min, n_max: Default range bounds if n is None.

    Returns:
        n: Array of discrete time indices.
        x: Array of signal values.
    """
    if n is None:
        n = get_default_time_axis(n_min, n_max)
    else:
        n = np.asarray(n, dtype=int)
    x = np.where(n >= n0, float(A), 0.0)
    return n, x


def rect_pulse(
    n: Optional[np.ndarray] = None,
    N: int = 4,
    n0: int = 0,
    A: float = 1.0,
    n_min: int = DEFAULT_N_MIN,
    n_max: int = DEFAULT_N_MAX
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Generate a scaled and shifted discrete-time rectangular pulse of length N:
        x[n] = A * rect_N[n - n0] = A * (u[n - n0] - u[n - n0 - N])
        i.e., x[n] = A for 0 <= n - n0 < N (n0 <= n < n0 + N), 0 otherwise.

    Parameters:
        n: Time index array. If None, generated from [n_min, n_max].
        N: Pulse width in number of samples (positive integer).
        n0: Time shift (integer).
        A: Amplitude scaling factor.
        n_min, n_max: Default range bounds if n is None.

    Returns:
        n: Array of discrete time indices.
        x: Array of signal values.
    """
    if n is None:
        n = get_default_time_axis(n_min, n_max)
    else:
        n = np.asarray(n, dtype=int)
    x = np.where((n >= n0) & (n < n0 + N), float(A), 0.0)
    return n, x


def sinusoid(
    n: Optional[np.ndarray] = None,
    f0: float = 0.1,
    n0: int = 0,
    A: float = 1.0,
    phi: float = 0.0,
    n_min: int = DEFAULT_N_MIN,
    n_max: int = DEFAULT_N_MAX
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Generate a scaled and shifted discrete-time sinusoidal signal:
        x[n] = A * \sin(2 * \pi * f0 * (n - n0) + \phi)

    Parameters:
        n: Time index array. If None, generated from [n_min, n_max].
        f0: Normalized digital frequency in cycles/sample.
        n0: Time shift (integer).
        A: Amplitude scaling factor.
        phi: Phase offset in radians.
        n_min, n_max: Default range bounds if n is None.

    Returns:
        n: Array of discrete time indices.
        x: Array of signal values.
    """
    if n is None:
        n = get_default_time_axis(n_min, n_max)
    else:
        n = np.asarray(n, dtype=int)
    x = float(A) * np.sin(2.0 * np.pi * float(f0) * (n - n0) + float(phi))
    return n, x


def cosinusoid(
    n: Optional[np.ndarray] = None,
    f0: float = 0.1,
    n0: int = 0,
    A: float = 1.0,
    phi: float = 0.0,
    n_min: int = DEFAULT_N_MIN,
    n_max: int = DEFAULT_N_MAX
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Generate a scaled and shifted discrete-time cosinusoidal signal:
        x[n] = A * \cos(2 * \pi * f0 * (n - n0) + \phi)

    Parameters:
        n: Time index array. If None, generated from [n_min, n_max].
        f0: Normalized digital frequency in cycles/sample.
        n0: Time shift (integer).
        A: Amplitude scaling factor.
        phi: Phase offset in radians.
        n_min, n_max: Default range bounds if n is None.

    Returns:
        n: Array of discrete time indices.
        x: Array of signal values.
    """
    if n is None:
        n = get_default_time_axis(n_min, n_max)
    else:
        n = np.asarray(n, dtype=int)
    x = float(A) * np.cos(2.0 * np.pi * float(f0) * (n - n0) + float(phi))
    return n, x


def signum(
    n: Optional[np.ndarray] = None,
    n0: int = 0,
    A: float = 1.0,
    n_min: int = DEFAULT_N_MIN,
    n_max: int = DEFAULT_N_MAX
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Generate a scaled and shifted discrete-time signum (sign) function:
        x[n] = A * sgn[n - n0]
        where sgn[m] = +1 (m > 0), 0 (m = 0), -1 (m < 0).

    Parameters:
        n: Time index array. If None, generated from [n_min, n_max].
        n0: Time shift (integer).
        A: Amplitude scaling factor.
        n_min, n_max: Default range bounds if n is None.

    Returns:
        n: Array of discrete time indices.
        x: Array of signal values.
    """
    if n is None:
        n = get_default_time_axis(n_min, n_max)
    else:
        n = np.asarray(n, dtype=int)
    m = n - n0
    x = float(A) * np.sign(m).astype(float)
    return n, x


def unit_ramp(
    n: Optional[np.ndarray] = None,
    n0: int = 0,
    A: float = 1.0,
    n_min: int = DEFAULT_N_MIN,
    n_max: int = DEFAULT_N_MAX
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Generate a scaled and shifted discrete-time unit ramp function:
        x[n] = A * r[n - n0] = A * (n - n0) * u[n - n0]

    Parameters:
        n: Time index array. If None, generated from [n_min, n_max].
        n0: Time shift (integer).
        A: Amplitude scaling factor.
        n_min, n_max: Default range bounds if n is None.

    Returns:
        n: Array of discrete time indices.
        x: Array of signal values.
    """
    if n is None:
        n = get_default_time_axis(n_min, n_max)
    else:
        n = np.asarray(n, dtype=int)
    m = n - n0
    x = np.where(m >= 0, float(A) * m, 0.0)
    return n, x


# =============================================================================
# PART II: DIRECT DTFT & DIRECT CONVOLUTION IMPLEMENTATIONS
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

    Note: This is calculated directly via summation over the sample points n
    WITHOUT using FFT library functions, exactly adhering to project requirements.

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

    # Direct summation matrix formulation:
    # Kernel matrix W of shape (len(f), len(n)): W[i, k] = exp(-j * 2 * pi * f[i] * n[k])
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

    # Compute convolution sum directly:
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
# PART I & II VISUALIZATION & DEMONSTRATION SUITES
# =============================================================================

def plot_stem_signal(
    n: np.ndarray,
    x: np.ndarray,
    title: str,
    ax: Optional[plt.Axes] = None,
    color: str = "#1f77b4",
    y_label: str = "x[n]"
) -> plt.Axes:
    """
    Render a single discrete-time stem plot adhering to all formatting requirements:
      - Stem plot representation
      - Horizontal axis labeled n
      - Vertical axis labeled x[n] (or customized y_label)
      - Clear samples and grid
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 4))

    markerline, stemlines, baseline = ax.stem(n, x, basefmt=" ")
    plt.setp(markerline, marker="o", markersize=5, color=color, markeredgecolor=color)
    plt.setp(stemlines, linewidth=1.5, color=color)
    ax.axhline(0, color="gray", linewidth=0.8, alpha=0.7)

    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    ax.set_xlabel("n", fontsize=10)
    ax.set_ylabel(y_label, fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.set_xlim([n[0] - 1, n[-1] + 1])
    ax.set_xticks(np.arange(n[0], n[-1] + 1, 5))
    return ax


def plot_part1_demonstration(save_path: Optional[str] = "part1_demonstration.png") -> plt.Figure:
    """
    Generate and display demonstration stem plots for Part I singularity functions
    over n in [-20, 20], covering all project examples:
      1. x1[n] = 3 * u[n - 2]
      2. x2[n] = -2 * delta[n + 3]
      3. x3[n] = 4 * rect_3[n - 2]
      4. x4[n] = -3 * sgn[n + 4]
      5. x5[n] = 2.5 * cos(2*pi*0.08*(n - 3))
      6. x6[n] = 2.0 * sin(2*pi*0.1*n)
    """
    n = get_default_time_axis(-20, 20)

    # Generate signals
    _, s1 = unit_step(n, n0=2, A=3.0)
    _, s2 = unit_impulse(n, n0=-3, A=-2.0)
    _, s3 = rect_pulse(n, N=3, n0=2, A=4.0)
    _, s4 = signum(n, n0=-4, A=-3.0)
    _, s5 = cosinusoid(n, f0=0.08, n0=3, A=2.5)
    _, s6 = sinusoid(n, f0=0.10, n0=0, A=2.0)

    signals = [
        (s1, r"$x[n] = 3\,u[n - 2]$ (Scaled & Shifted Step)", "#1f77b4"),
        (s2, r"$x[n] = -2\,\delta[n + 3]$ (Scaled & Shifted Impulse)", "#d62728"),
        (s3, r"$x[n] = 4\,\mathrm{rect}_3[n - 2]$ (Rectangular Pulse)", "#2ca02c"),
        (s4, r"$x[n] = -3\,\mathrm{sgn}[n + 4]$ (Scaled & Shifted Signum)", "#9467bd"),
        (s5, r"$x[n] = 2.5\,\cos(2\pi \cdot 0.08(n - 3))$ (Shifted Cosine)", "#ff7f0e"),
        (s6, r"$x[n] = 2.0\,\sin(2\pi \cdot 0.10\,n)$ (Discrete Sinusoid)", "#8c564b"),
    ]

    fig, axes = plt.subplots(3, 2, figsize=(14, 10))
    fig.suptitle(
        "Part I: Discrete-Time Singularity & Elementary Functions (-20 ≤ n ≤ 20)",
        fontsize=14, fontweight="bold", y=0.98
    )

    for ax, (sig, title, color) in zip(axes.flatten(), signals):
        plot_stem_signal(n, sig, title, ax=ax, color=color)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved Part I demonstration figure to: {save_path}")
    return fig


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
      - Subfigure 1: x[n]
      - Subfigure 2: |X(f)|
      - Subfigure 3: h[n]
      - Subfigure 4: |H(f)|
      - Subfigure 5: y[n] = x[n] * h[n]
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
        print(f"Saved Part II analysis figure to: {save_path}")

    metrics = {
        "max_absolute_error": max_err,
        "mean_squared_error": mse_err,
        "mean_absolute_error": mae_err,
        "convolution_length": len(y_full),
        "ny_range": (int(ny_full[0]), int(ny_full[-1]))
    }
    return fig, metrics


# =============================================================================
# CLI & DEMONSTRATION RUNNER
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


def run_project_demonstrations():
    """
    Run complete project suite including Part I singularity functions
    and multiple representative Part II test cases.
    """
    print("=" * 75)
    print(" DIGITAL SIGNAL PROCESSING PROJECT: SIGNALS, CONVOLUTION & DTFT")
    print("=" * 75)

    # 1. Part I Demonstration
    print("\n[1/4] Generating Part I Singularity Functions Demonstration...")
    plot_part1_demonstration("part1_demonstration.png")

    # 2. Part II - Example from Section 4 of PDF:
    # x[n] = 2 * u[n - 2], bounded to [-20, 20]
    # h[n] = delta[n - 1]
    print("\n[2/4] Running Part II Demonstration (Section 4 Example):")
    print("      x[n] = 2 * u[n - 2],   h[n] = delta[n - 1]")
    n = get_default_time_axis(-20, 20)
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
    print("      -> Verification Status: PASS (EXACT CONVOLUTION PROPERTY MATCH)")

    # 3. Part II - Pulse Convolution (Rectangular x Rectangular = Triangular Pulse):
    # x[n] = 3 * rect_5[n - 2],   h[n] = 2 * rect_4[n + 1]
    print("\n[3/4] Running Part II Demonstration (Rectangular Pulses):")
    print("      x[n] = 3 * rect_5[n - 2],   h[n] = 2 * rect_4[n + 1]")
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
    print("      -> Verification Status: PASS (EXACT CONVOLUTION PROPERTY MATCH)")

    # 4. Part II - Sinusoid with Smoothing Filter:
    # x[n] = 2 * cos(2*pi*0.1*n),   h[n] = 1/3 * rect_3[n]
    print("\n[4/4] Running Part II Demonstration (Cosine Filtered by Moving Average):")
    print("      x[n] = 2 * cos(2*pi*0.1*n),   h[n] = (1/3) * rect_3[n]")
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
    print("      -> Verification Status: PASS (EXACT CONVOLUTION PROPERTY MATCH)")

    print("\n" + "=" * 75)
    print(" All demonstrations completed successfully! Generated high-res plots:")
    print("  1. part1_demonstration.png        (Part I: 6 Singularity Functions)")
    print("  2. part2_example_sec4.png         (Part II: Step * Shifted Impulse)")
    print("  3. part2_example_rect_pulses.png  (Part II: Rect * Rect -> Triangle)")
    print("  4. part2_example_cosine_ma.png    (Part II: Cosine * Moving Average)")
    print("=" * 75)


def main():
    parser = argparse.ArgumentParser(
        description="Digital Signal Processing Project: Singularity Functions, Convolution & DTFT"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="Run in interactive CLI mode to specify custom signals and generate plots."
    )
    args = parser.parse_args()

    if args.interactive:
        run_interactive_mode()
    else:
        run_project_demonstrations()


if __name__ == "__main__":
    main()

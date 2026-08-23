"""
Digital Signal Processing Project - Part I
Discrete-Time Singularity and Elementary Functions

This module implements reusable functions for generating scaled and shifted
discrete-time singularity and elementary functions of the general form:
    x[n] = A * s[n - n0]

Implemented Functions:
  1. Unit Impulse:     delta[n - n0]
  2. Unit Step:        u[n - n0]
  3. Rectangular Pulse: rect_N[n - n0]
  4. Sinusoid:         sin(2*pi*f0*(n - n0) + phi)
  5. Cosinusoid:       cos(2*pi*f0*(n - n0) + phi)
  6. Signum:           sgn[n - n0]
  7. Unit Ramp:        r[n - n0]

All functions support:
  - Amplitude scaling factor A
  - Time shift n0 (delay if n0 > 0, advance if n0 < 0)
  - Time range array n (default: -20 <= n <= 20)
"""

from typing import Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# DEFAULT TIME DOMAIN SPECIFICATIONS
# =============================================================================
DEFAULT_N_MIN = -20
DEFAULT_N_MAX = 20


def get_default_time_axis(n_min: int = DEFAULT_N_MIN, n_max: int = DEFAULT_N_MAX) -> np.ndarray:
    """Return discrete-time index array n in range [n_min, n_max]."""
    return np.arange(n_min, n_max + 1, dtype=int)


# =============================================================================
# REUSABLE SINGULARITY & ELEMENTARY FUNCTIONS
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
        where \delta[0] = 1, and \delta[m] = 0 for m != 0.

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
        where u[m] = 1 for m >= 0, and u[m] = 0 for m < 0.

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
        i.e., x[n] = A for n0 <= n < n0 + N, and 0 otherwise.

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
# PART I PLOTTING & DEMONSTRATION
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
      - Clear discrete samples and grid
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


def run_part1_demonstration(save_path: Optional[str] = "part1_demonstration.png") -> plt.Figure:
    """
    Demonstrate Part I implemented functions by plotting scaled and shifted
    versions of the basic signals over -20 <= n <= 20:
      1. x1[n] = 3 * u[n - 2]
      2. x2[n] = -2 * delta[n + 3]
      3. x3[n] = 4 * rect_3[n - 2]
      4. x4[n] = -3 * sgn[n + 4]
      5. x5[n] = 2.5 * cos(2*pi*0.08*(n - 3))
      6. x6[n] = 2.0 * sin(2*pi*0.10*n)
    """
    n = get_default_time_axis(-20, 20)

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
        print(f"[Part I] Demonstration plot saved to: {save_path}")
    return fig


if __name__ == "__main__":
    print("=" * 65)
    print(" PART I: DISCRETE-TIME SINGULARITY FUNCTIONS DEMONSTRATION")
    print("=" * 65)
    run_part1_demonstration("part1_demonstration.png")
    print("=" * 65)

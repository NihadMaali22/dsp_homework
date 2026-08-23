# Digital Signal Processing Project Report
## Discrete-Time Signals, Convolution, and DTFT Analysis

---

### Executive Summary

This project implements a complete, modular Digital Signal Processing (DSP) toolkit in **Python**, strictly partitioned into two independent yet complementary modules as specified in the project guidelines:
1. [**`part1.py`**](file:///home/nihad/Documents/dsp_homework/part1.py): **Discrete-Time Singularity & Elementary Functions**
   - Reusable generator functions for $\delta[n]$, $u[n]$, $\text{rect}_N[n]$, $\sin[n]$, $\cos[n]$, $\text{sgn}[n]$, and $r[n]$ supporting arbitrary scaling $A$, shift $n_0$, and range $n \in [-20, 20]$.
   - Standalone plotting demonstration generating `part1_demonstration.png`.
2. [**`part2.py`**](file:///home/nihad/Documents/dsp_homework/part2.py): **Convolution and DTFT Analysis**
   - Imports and reuses the functions developed in `part1.py`.
   - Computes the **Discrete-Time Fourier Transform (DTFT)** directly from its mathematical summation definition over $f \in [-0.5, 0.5]$ without FFT algorithms.
   - Computes **Linear Discrete-Time Convolution** directly from the convolution sum without built-in libraries (`np.convolve` / `scipy.signal.convolve`).
   - Numerically validates the **DTFT Convolution Theorem**:
     $$\mathcal{F}\{x[n] * h[n]\} = X(f) \cdot H(f)$$
   - Renders the required $3 \times 2$ figure layout comparing time- and frequency-domain representations.

---

## 1. Module Partition & Code Structure

### 1.1 `part1.py` - Singularity Functions
The functions in `part1.py` generate scaled and shifted signals of the form $x[n] = A \cdot s[n - n_0]$:

- **Unit Impulse $\delta[n - n_0]$:**
  $$\delta[n - n_0] = \begin{cases} 1, & n = n_0 \\ 0, & n \neq n_0 \end{cases}$$
- **Unit Step $u[n - n_0]$:**
  $$u[n - n_0] = \begin{cases} 1, & n \ge n_0 \\ 0, & n < n_0 \end{cases}$$
- **Rectangular Pulse $\text{rect}_N[n - n_0]$:**
  $$\text{rect}_N[n - n_0] = u[n - n_0] - u[n - n_0 - N] = \begin{cases} 1, & n_0 \le n < n_0 + N \\ 0, & \text{otherwise} \end{cases}$$
- **Signum Function $\text{sgn}[n - n_0]$:**
  $$\text{sgn}[n - n_0] = \begin{cases} +1, & n > n_0 \\ 0, & n = n_0 \\ -1, & n < n_0 \end{cases}$$
- **Discrete Sinusoid & Cosinusoid:**
  $$x_{\sin}[n] = A \sin(2\pi f_0 (n - n_0) + \phi), \qquad x_{\cos}[n] = A \cos(2\pi f_0 (n - n_0) + \phi)$$
- **Unit Ramp $r[n - n_0]$:**
  $$r[n - n_0] = (n - n_0) \cdot u[n - n_0]$$

---

### 1.2 `part2.py` - Convolution and DTFT Analysis

#### Direct DTFT Summation:
The DTFT of a finite-duration discrete sequence $x[n]$ is evaluated directly across $M=1001$ normalized frequency points $f \in [-0.5, 0.5]$ (cycles/sample) via matrix summation:
$$X(f) = \sum_{n=-20}^{20} x[n]\,e^{-j 2\pi f n}$$
Implemented as:
```python
kernel = np.exp(-1j * 2.0 * np.pi * np.outer(f, n))
X = kernel @ x
```

#### Direct Linear Convolution Summation:
Linear convolution is calculated sample-by-sample without library shortcuts:
$$y[n] = x[n] * h[n] = \sum_{k=-\infty}^{\infty} x[k]\,h[n - k]$$
```python
for idx_n, n_val in enumerate(ny):
    sum_val = 0.0
    for idx_k, k_val in enumerate(nx):
        h_time = n_val - k_val
        if nh_min <= h_time <= nh_max:
            sum_val += x[idx_k] * h[h_time - nh_min]
    y[idx_n] = sum_val
```

---

## 2. Experimental Demonstrations & Visualizations

### 2.1 Part I Demonstration (`part1_demonstration.png`)
Plots the 6 fundamental singularity functions over $-20 \le n \le 20$:
1. $x_1[n] = 3\,u[n - 2]$
2. $x_2[n] = -2\,\delta[n + 3]$
3. $x_3[n] = 4\,\text{rect}_3[n - 2]$
4. $x_4[n] = -3\,\text{sgn}[n + 4]$
5. $x_5[n] = 2.5\,\cos(2\pi \cdot 0.08(n - 3))$
6. $x_6[n] = 2.0\,\sin(2\pi \cdot 0.10\,n)$

---

### 2.2 Part II Demonstrations ($3 \times 2$ Layout)

#### Demonstration 1: Section 4 Example (`part2_example_sec4.png`)
- $x[n] = 2\,u[n - 2]$ (over $-20 \le n \le 20$)
- $h[n] = \delta[n - 1]$
- Output: $y[n] = x[n - 1] = 2\,u[n - 3]$
- Maximum Absolute Error: **$7.930 \times 10^{-14}$** (Exact Match)

#### Demonstration 2: Rectangular Pulse Convolution (`part2_example_rect_pulses.png`)
- $x[n] = 3\,\text{rect}_5[n - 2]$
- $h[n] = 2\,\text{rect}_4[n + 1]$
- Output: Triangular/trapezoidal pulse over $n \in [1, 8]$
- Maximum Absolute Error: **$7.860 \times 10^{-14}$** (Exact Match)

#### Demonstration 3: Cosine with Moving Average Filter (`part2_example_cosine_ma.png`)
- $x[n] = 2\,\cos(2\pi \cdot 0.1\,n)$
- $h[n] = \frac{1}{3}\,\text{rect}_3[n]$
- Maximum Absolute Error: **$2.354 \times 10^{-14}$** (Exact Match)

---

## 3. Quantitative Verification Results

| Test Case | Inputs ($x[n], h[n]$) | Max Error $\|\|Y\| - \|XH\|\|$ | MSE | Status |
| :--- | :--- | :---: | :---: | :---: |
| **Section 4 Example** | $2u[n-2] * \delta[n-1]$ | $7.93 \times 10^{-14}$ | $2.78 \times 10^{-28}$ | **PASSED** |
| **Rectangular Pulses** | $3\text{rect}_5[n-2] * 2\text{rect}_4[n+1]$ | $7.86 \times 10^{-14}$ | $4.47 \times 10^{-28}$ | **PASSED** |
| **Cosine Smoothing** | $2\cos(0.2\pi n) * \frac{1}{3}\text{rect}_3[n]$ | $2.35 \times 10^{-14}$ | $3.82 \times 10^{-29}$ | **PASSED** |
| **Impulse DTFT** | $\text{DTFT}\{\delta[n-n_0]\} \equiv e^{-j 2\pi f n_0}$ | $0.00 \times 10^{00}$ | $0.00 \times 10^{00}$ | **PASSED** |
| **Pulse DTFT** | $\text{DTFT}\{\text{rect}_N[n]\} \equiv \frac{\sin(\pi f N)}{\sin(\pi f)}$ | $< 1.00 \times 10^{-15}$ | $< 1.00 \times 10^{-30}$ | **PASSED** |

---

## 4. Execution Instructions

```bash
# 1. Run Part I demonstration
python3 part1.py

# 2. Run Part II analysis & 3x2 figures
python3 part2.py

# 3. Run Part II interactive explorer
python3 part2.py --interactive

# 4. Run automated test suite
python3 test_dsp.py
```

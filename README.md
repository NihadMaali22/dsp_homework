# Digital Signal Processing (DSP) Project
### Discrete-Time Signals, Convolution, and DTFT Analysis in Python

---

## 📌 Project Architecture

The project is cleanly split into two independent modules as required by the project specifications:

### 1. `part1.py` (Part I: Discrete-Time Singularity Functions)
Contains reusable functions for generating scaled and shifted elementary signals ($x[n] = A \cdot s[n - n_0]$):
- `unit_impulse(n, n0, A)`: $\;x[n] = A\,\delta[n - n0]$
- `unit_step(n, n0, A)`: $\;x[n] = A\,u[n - n0]$
- `rect_pulse(n, N, n0, A)`: $\;x[n] = A\,\text{rect}_N[n - n0]$
- `sinusoid(n, f0, n0, A, phi)`: $\;x[n] = A\,\sin(2\pi f_0 (n - n0) + \phi)$
- `cosinusoid(n, f0, n0, A, phi)`: $\;x[n] = A\,\cos(2\pi f_0 (n - n0) + \phi)$
- `signum(n, n0, A)`: $\;x[n] = A\,\text{sgn}[n - n0]$
- `unit_ramp(n, n0, A)`: $\;x[n] = A\,r[n - n0]$
- `run_part1_demonstration()`: Generates `part1_demonstration.png` for $-20 \le n \le 20$.

### 2. `part2.py` (Part II: Convolution & DTFT Analysis)
Imports functions from `part1.py` and implements:
- `dtft(x, n, f)`: Direct DTFT summation $X(f) = \sum_n x[n] e^{-j 2\pi f n}$ over $-0.5 \le f \le 0.5$ ($1001$ samples, no FFT library).
- `direct_convolve(x, nx, h, nh)`: Direct linear convolution $y[n] = \sum_k x[k] h[n - k]$ without library conv functions.
- `plot_part2_analysis(...)`: Renders the mandatory $3 \times 2$ figure.
- Interactive mode (`python3 part2.py --interactive`).

---

## 🚀 How to Run

```bash
# 1. Run Part I demonstration:
python3 part1.py

# 2. Run Part II analysis demonstrations:
python3 part2.py

# 3. Run interactive mode:
python3 part2.py --interactive

# 4. Run automated unit test suite:
python3 test_dsp.py
```

---

## 📊 Generated High-Resolution Figures
- [`part1_demonstration.png`](file:///home/nihad/Documents/dsp_homework/part1_demonstration.png): Part I stem plots of 6 singularity signals.
- [`part2_example_sec4.png`](file:///home/nihad/Documents/dsp_homework/part2_example_sec4.png): Part II $3 \times 2$ figure for $2u[n-2] * \delta[n-1]$.
- [`part2_example_rect_pulses.png`](file:///home/nihad/Documents/dsp_homework/part2_example_rect_pulses.png): Part II $3 \times 2$ figure for rectangular pulses.
- [`part2_example_cosine_ma.png`](file:///home/nihad/Documents/dsp_homework/part2_example_cosine_ma.png): Part II $3 \times 2$ figure for cosine with moving average.

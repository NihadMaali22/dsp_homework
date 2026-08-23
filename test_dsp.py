"""
Unit Tests for DSP Project Modules (part1.py and part2.py)
Validates mathematical correctness of:
  - Part I Singularity & Elementary Functions (part1.py)
  - Direct DTFT Calculation (part2.py) against analytical formulas
  - Direct Convolution Summation (part2.py) against analytical results
  - DTFT Convolution Property: DTFT{x[n] * h[n]} == X(f) * H(f)
"""

import unittest
import numpy as np
from part1 import (
    unit_impulse,
    unit_step,
    rect_pulse,
    sinusoid,
    cosinusoid,
    signum,
    unit_ramp,
    get_default_time_axis
)
from part2 import (
    dtft,
    direct_convolve,
    align_to_range,
    get_default_freq_axis
)


class TestPart1SingularityFunctions(unittest.TestCase):
    def setUp(self):
        self.n = get_default_time_axis(-20, 20)

    def test_unit_impulse(self):
        # x[n] = -2 * delta[n + 3] (impulse at n = -3)
        n, x = unit_impulse(self.n, n0=-3, A=-2.0)
        self.assertEqual(len(x), 41)
        self.assertEqual(x[self.n == -3][0], -2.0)
        self.assertEqual(np.sum(np.abs(x)), 2.0)
        self.assertTrue(np.all(x[self.n != -3] == 0.0))

    def test_unit_step(self):
        # x[n] = 3 * u[n - 2]
        n, x = unit_step(self.n, n0=2, A=3.0)
        self.assertTrue(np.all(x[self.n >= 2] == 3.0))
        self.assertTrue(np.all(x[self.n < 2] == 0.0))

    def test_rect_pulse(self):
        # x[n] = 4 * rect_3[n - 2] -> non-zero for n in {2, 3, 4}
        n, x = rect_pulse(self.n, N=3, n0=2, A=4.0)
        self.assertTrue(np.all(x[(self.n >= 2) & (self.n < 5)] == 4.0))
        self.assertTrue(np.all(x[(self.n < 2) | (self.n >= 5)] == 0.0))
        self.assertEqual(np.sum(x), 12.0)

    def test_signum(self):
        # x[n] = -3 * sgn[n + 4] -> shift is -4
        n, x = signum(self.n, n0=-4, A=-3.0)
        self.assertTrue(np.all(x[self.n > -4] == -3.0))
        self.assertEqual(x[self.n == -4][0], 0.0)
        self.assertTrue(np.all(x[self.n < -4] == 3.0))

    def test_sinusoid_and_cosinusoid(self):
        n, s = sinusoid(self.n, f0=0.1, n0=0, A=2.0)
        n, c = cosinusoid(self.n, f0=0.1, n0=0, A=2.0)
        self.assertAlmostEqual(s[self.n == 0][0], 0.0, places=7)
        self.assertAlmostEqual(c[self.n == 0][0], 2.0, places=7)


class TestPart2DirectDTFT(unittest.TestCase):
    def setUp(self):
        self.n = get_default_time_axis(-20, 20)
        self.f = get_default_freq_axis(-0.5, 0.5, 501)

    def test_dtft_of_shifted_impulse(self):
        # Analytical DTFT of A * delta[n - n0] is A * exp(-j * 2 * pi * f * n0)
        n0 = 5
        A = 3.5
        _, x = unit_impulse(self.n, n0=n0, A=A)
        _, X_computed = dtft(x, self.n, self.f)
        X_analytical = A * np.exp(-1j * 2.0 * np.pi * self.f * n0)
        np.testing.assert_allclose(X_computed, X_analytical, atol=1e-12)

    def test_dtft_of_rect_pulse(self):
        # Analytical DTFT of rect_N[n] is exp(-j*pi*f*(N-1)) * sin(pi*f*N)/sin(pi*f)
        N = 5
        A = 1.0
        _, x = rect_pulse(self.n, N=N, n0=0, A=A)
        _, X_computed = dtft(x, self.n, self.f)

        X_analytical = np.zeros(len(self.f), dtype=complex)
        for idx, f_val in enumerate(self.f):
            if np.isclose(f_val, 0.0):
                X_analytical[idx] = float(N)
            else:
                X_analytical[idx] = np.exp(-1j * np.pi * f_val * (N - 1)) * (
                    np.sin(np.pi * f_val * N) / np.sin(np.pi * f_val)
                )
        np.testing.assert_allclose(X_computed, X_analytical, atol=1e-12)


class TestPart2DirectConvolution(unittest.TestCase):
    def test_impulse_shifting_property(self):
        # x[n] * delta[n - n0] == x[n - n0]
        n = get_default_time_axis(-10, 10)
        _, x = rect_pulse(n, N=4, n0=0, A=2.0)
        _, h = unit_impulse(n, n0=3, A=1.0)

        ny, y = direct_convolve(x, n, h, n)
        y_expected = np.where((ny >= 3) & (ny < 7), 2.0, 0.0)
        np.testing.assert_allclose(y, y_expected, atol=1e-12)

    def test_convolution_commutativity(self):
        n = get_default_time_axis(-5, 5)
        _, x = rect_pulse(n, N=3, n0=-1, A=2.0)
        _, h = unit_step(n, n0=0, A=1.5)

        ny1, y1 = direct_convolve(x, n, h, n)
        ny2, y2 = direct_convolve(h, n, x, n)
        np.testing.assert_array_equal(ny1, ny2)
        np.testing.assert_allclose(y1, y2, atol=1e-12)


class TestPart2DTFTConvolutionProperty(unittest.TestCase):
    def test_convolution_theorem_match(self):
        # Test property: DTFT{x[n] * h[n]} == X(f) * H(f)
        n = get_default_time_axis(-20, 20)
        f = get_default_freq_axis(-0.5, 0.5, 1001)

        # Test Case: Step and shifted impulse
        _, x = unit_step(n, n0=2, A=2.0)
        _, h = unit_impulse(n, n0=1, A=1.0)

        _, X = dtft(x, n, f)
        _, H = dtft(h, n, f)
        ny, y = direct_convolve(x, n, h, n)
        _, Y = dtft(y, ny, f)

        diff = np.abs(np.abs(Y) - np.abs(X * H))
        max_error = np.max(diff)
        self.assertLess(max_error, 1e-12)


if __name__ == "__main__":
    unittest.main()

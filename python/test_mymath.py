import unittest

from pylab import *

import mymath as m

class TestFwhm(unittest.TestCase):

    def setUp(self):
        self.x = arange(10)

    def test_multiple_peaks(self):
        y = array([1, 10, 6, 3, 5, 10, 7, 2, 1, 1])
        self.assertRaises(m.MultiplePeaks, m.fwhm, self.x, y)

    def test_flat(self):
        y = ones(self.x.shape)
        self.assertRaises(m.NoPeaksFound, m.fwhm, self.x, y)

    def test_gaussian(self):
        sigma = rand()
        x = linspace(-2*sigma, 2*sigma, 100)
        y = exp(-(x/sigma)**2/2)
        fwhm = m.fwhm(x, y)
        gaus_fwhm = 2*sqrt(2*log(2))*sigma
        self.assertAlmostEqual(fwhm, gaus_fwhm, places=3)

class TestCorr(unittest.TestCase):

    def test_autocorr(self):
        A = rand(10, 15)
        corr0 = m.autocorr(A)
        self.assertAlmostEqual(corr0[0, 0], 1.0)

    def test_normalization(self):
        """All values of the correlation should be between -1 and 1."""
        A = rand(10, 15)
        B = rand(10, 15)
        C = m.corr(A, B)
        self.assertTrue((abs(C) <= 1.000000001).all())

if __name__ == '__main__':
    unittest.main()

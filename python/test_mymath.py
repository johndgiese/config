import unittest

from pylab import *

import mymath as m

class TestFwhm(unittest.TestCase):

    def setUp(self):
        self.x = arange(10)

    def test_multiple_peaks(self):
        self.y = array([1, 10, 6, 3, 5, 10, 7, 2, 1, 1])
        self.assertRaises(m.MultiplePeaks, m.fwhm, self.x, self.y)

    def test_flat(self):
        self.y = ones(self.x.shape)
        self.assertRaises(m.NoPeaksFound, m.fwhm, self.x, self.y)

    def test_gaussian(self):
        self.sigma = rand()
        self.x = linspace(-2*self.sigma, 2*self.sigma, 100)
        self.y = exp(-(self.x/self.sigma)**2/2)
        self.fwhm = m.fwhm(self.x, self.y)
        self.gaus_fwhm = 2*sqrt(2*log(2))*self.sigma
        self.assertAlmostEqual(self.fwhm, self.gaus_fwhm, places=3)

if __name__ == '__main__':
    unittest.main()

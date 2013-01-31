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

class TestInterpMax(unittest.TestCase):

    def test_closest_in_grid(self):
        x, y = m.closest_in_grid(2, 3, 0, 0)
        self.assertEqual((x, y), (0, 0))
        x, y = m.closest_in_grid(2, 3, -1, 0)
        self.assertEqual((x, y), (0, 0))
        x, y = m.closest_in_grid(2, 3, -1, -4)
        self.assertEqual((x, y), (0, 0))

        x, y = m.closest_in_grid(2, 3, 2, 3)
        self.assertEqual((x, y), (1, 2))
        x, y = m.closest_in_grid(2, 3, 1, 30)
        self.assertEqual((x, y), (1, 2))
        x, y = m.closest_in_grid(2, 3, 100, 0)
        self.assertEqual((x, y), (1, 0))

    def test_easy(self):
        img = array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
        x = [1, 2, 3]
        y = [1, 2, 3]
        xx, yy, zz = m.interp_max(img, x=x, y=y)
        self.assertAlmostEqual(xx, 2)
        self.assertAlmostEqual(yy, 2)
        self.assertAlmostEqual(zz, 1)

    def test_easy_using_indices(self):
        img = array([[0, 0, 0], [0, 1, 0], [0, 0, 0]])
        xx, yy, zz = m.interp_max(img)
        self.assertAlmostEqual(xx, 1)
        self.assertAlmostEqual(yy, 1)
        self.assertAlmostEqual(zz, 1)

    def test_surface(self):
        precision = 200
        # restrict range of zero to middle or 1x1 grid
        xm = rand()*0.8 + 0.1
        ym = rand()*0.8 + 0.1
        x = linspace(0, 1, 10)
        y = linspace(0, 1, 10)
        X, Y = meshgrid(x, y)
        def func(x, y):
            return -3*(x - xm)**2 - (y - ym)**2
        Z = reshape(array(map(func, X, Y)), (len(x), len(y)))
        xx, yy, zz = m.interp_max(Z, x, y, precision=precision)
        expected_places = 1
        self.assertAlmostEqual(xx, xm, places=expected_places)
        self.assertAlmostEqual(yy, ym, places=expected_places)

if __name__ == '__main__':
    unittest.main()

import unittest

# I am slowly transitioning to using proper namespacing
from pylab import *
import pylab as pl
import scipy
import numpy as np

import mymath as m

PLOTTING = False

class NumericTestCase(unittest.TestCase):
    """Test case with assertions for numeric computing."""

    def assertArraysClose(self, a, b, rtol=1e-05, atol=1e-08):
        """Check that the two arrays are almost equal, see np.allclose."""
        arrays_close = np.allclose(a, b)

        if not arrays_close:
            Ea = sum(abs(a)**2)
            Eb = sum(abs(b)**2)
            Ed = sum(abs(a - b)**2)
            msg = "The arrays\n%s\n and \n%s\n are not nearly equal." % (str(a), str(b))
            msg += "\nThe energy of a is %s.\n" % (str(Ea),)
            msg += "\nThe energy of b is %s.\n" % (str(Eb),)
            msg += "\nThe energy of a - b is %s.\n" % (str(Ed),)
            raise self.failureException(msg)

class TestFwhm(NumericTestCase):

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

class TestCorr(NumericTestCase):

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

class TestZpadf(NumericTestCase):

    def test_1d(self):
        a = array([1.0, 1.0])
        za = array([1.0, 0.5, 0, 0.5])
        self.assertArraysClose(za, m.zpadf(a, 2))
        self.assertArraysClose(za, m.zpadf(a, (2,)))


        a = array([1.0, 2, 3])
        za = array([1, 2, 0, 0, 3])
        self.assertArraysClose(za, m.zpadf(a, 2))

        a = array([1.0, 2, 3, 4])
        za = array([1, 2, 1.5, 0, 1.5, 4])
        self.assertArraysClose(za, m.zpadf(a, 2))

        a = array([1.0, 2, 3, 4])
        za = array([1, 2, 1.5, 0, 0, 1.5, 4])
        self.assertArraysClose(za, m.zpadf(a, 3))

    def test_2d(self):
        a = array([
            [1.0, 2], 
            [3, 8]
        ])
        za = array([
            [1,   1, 0, 1], 
            [1.5, 2, 0, 2],
            [0,   0, 0, 0],
            [1.5, 2, 0, 2]
        ])
        self.assertArraysClose(za, m.zpadf(a, 2))
        self.assertArraysClose(za, m.zpadf(a, (2, 2)))

        za = array([
            [1,   2], 
            [1.5, 4],
            [0,   0],
            [1.5, 4]
        ])
        self.assertArraysClose(za, m.zpadf(a, (2, 0)))

        za = array([
            [1,   1, 0, 1], 
            [3,   4, 0, 4],
        ])
        self.assertArraysClose(za, m.zpadf(a, (0, 2)))


class TestInterpMax(NumericTestCase):

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

class TestRegister(NumericTestCase):

    def setUp(self):
        self.img0 = scipy.misc.lena()
        self.img0ft = fft2(self.img0)
        ny, nx = self.img0.shape
        self.ny = ny
        self.nx = nx
        self.row_shift = randint(self.nx)
        self.col_shift = randint(self.ny)
        self.img1 = m.circshift(self.img0ft, 
                self.row_shift, self.col_shift, transformed=True)
        self.img1ft = fft2(self.img1)

    def test_upsample_1(self):
        """Test algorithm without subpixel registration."""


        img0 = scipy.misc.lena()
        img0ft = fft2(img0)
        ny, nx = img0.shape
        row_shift = randint(-nx/2, nx/2)
        col_shift = randint(-ny/2, ny/2)
        row_shift = 10.4
        col_shift = 27.4
        img1 = m.circshift(img0ft, row_shift, col_shift, transformed=True)
        img1 = abs(img1)
        img1ft = fft2(img1)

        if PLOTTING:
            subplot(211)
            imshow(img0)
            title('original')
            subplot(212)
            imshow(img1)
            title('shifted by {}x{}'.format(row_shift, col_shift))
            show()

        row, col = m.register(img0ft, img1ft, transformed=True)
        self.assertEqual(row, row_shift)
        self.assertEqual(col, col_shift)

    def test_upsample_10(self):
        row, col = m.register(self.img0ft, self.img1ft, 
                upsample=11, transformed=True)
        self.assertEqual(row, self.row_shift)
        self.assertEqual(col, self.col_shift)

class TestDFTUpsample(NumericTestCase):

    def setUp(self):

        ## pick random odd upsampling
        upsample = randint(1, 16)
        if m.iseven(upsample):
            half = int((upsample - 1)/2.0)
        else:
            half = int(upsample/2.0) - 1

        # setup random area to calculate idft on
        nx = randint(10, 100)
        ny = randint(10, 100)
        height = randint(4, ny*upsample)
        width = randint(4, nx*upsample)
        try:
            top = randint(0, ny*upsample - height)
        except:
            top = 0
        try:
            left = randint(0, nx*upsample - width)
        except:
            left = 0

        # generate a random image
        aa = rand(ny, nx)
        aa[:-5, :-5] += 1
        aa[:-2, :] += 2
        a = fft2(aa)

        ## attach data to test case
        self.a = a
        self.nx = nx
        self.ny = ny
        self.height = height
        self.width = width
        self.top = top
        self.left = left
        self.upsample = upsample


    def test_equivalence(self):
        """
        The dft_upsample function should be equivalent to:
        1. Embedding the array "a" in an array that is "upsample" times larger
           in each dimension. ifftshift to bring the center of the image to
           (0, 0).
        2. Take the IFFT of the larger array
        3. Extract an [height, width] region of the result. Starting with the 
           [top, left] element.
        """
        a = self.a
        nx = self.nx
        ny = self.ny
        height = self.height
        width = self.width
        top = self.top
        left = self.left
        upsample = self.upsample

        ## calculate the slow way
        extra_zeros = ((upsample - 1)*ny, (upsample - 1)*nx)
        padded = m.zpadf(a, extra_zeros)
        b_slow_big = ifft2(padded)
        b_slow = b_slow_big[
            top:top + height,
            left:left + width,
        ]

        # calculate the fast way
        b_fast = m.upsampled_idft2(a, upsample, height, width, top, left)
        b_fast_big = m.upsampled_idft2(a, upsample, upsample*ny, upsample*nx, 0, 0)

        if PLOTTING:
            subplot(411)
            imshow(abs(b_fast_big))
            subplot(412)
            imshow(abs(b_slow_big))
            subplot(413)
            imshow(abs(b_fast))
            subplot(414)
            imshow(abs(b_slow))
            title('{}x{} starting at {}x{}'.format(height, width, top, left))
            figure()
            imshow(aa)
            show()

        if PLOTTING:
            subplot(221)
            imshow(abs(b_slow))
            title('slow abs')
            subplot(222)
            imshow(abs(b_fast))
            title('fast abs')
            subplot(223)
            imshow(unwrap(angle(b_slow)))
            title('slow angle')
            subplot(224)
            imshow(unwrap(angle(b_fast)))
            title('fast angle')
            show()

        # are they the same (within a multiplier)
        b_slow = b_slow/mean(abs(b_slow))
        b_fast = b_fast/mean(abs(b_fast))
        self.assertArraysClose(b_slow, b_fast, rtol=1e-2)

    def test_normalization(self):
        """The function should be properly normalized."""
        a = ones([10, 10])
        aa = fft2(a)
        b = m.upsampled_idft2(aa, 3, 30, 30, 0, 0)
        self.assertAlmostEqual(amax(a), amax(abs(b)))

    def test_full_array(self):
        nx = self.nx
        ny = self.ny
        upsample = self.upsample

        aa = rand(ny, nx)
        aa[:-5, :-5] += 1
        aa[:-2, :] += 2
        a = fft2(aa)

        ## calculate the slow way
        extra_zeros = ((upsample - 1)*ny, (upsample - 1)*nx)
        padded = m.zpadf(a, extra_zeros)
        b_slow_big = ifft2(padded)

        # calculate the fast way
        b_fast_big = m.upsampled_idft2(a, upsample, upsample*ny, upsample*nx, 0, 0)

        b_slow_big = b_slow_big/mean(abs(b_slow_big))
        b_fast_big = b_fast_big/mean(abs(b_fast_big))
        self.assertArraysClose(abs(b_fast_big), abs(b_slow_big), rtol=1e-2)


    def test_known2x2(self):
        A = array([[1, 4], [0, 2]])
        AA = fft2(A)
        known_out = array([[4, 2.5], [3, 1.75]])
        out = m.upsampled_idft2(AA, 2, 4, 4, 0, 0)

    def test_simple(self):
        """
        Fourier transforms can be accomplished using matrices.

        You need two of them (one for each dimension).

        This test is a simple sanity check.
        """

        a = fft2(array([[0, 2, 2, 0],
                        [0, 2, 2, 2],
                        [0, 0, 0, 2],
                        [10, 0, 0, 2]]))
        ny, nx = a.shape

        F = array([[1, 1, 1, 1],
                   [1, 1j, -1, -1j],
                   [1, -1, 1, -1],
                   [1, -1j, -1, 1j]])
        self.assertArraysClose(ifft2(a), m.dot(F, a, F)/nx/ny)

class TestCircshift(NumericTestCase):
    
    def test_allones(self):
        N = randint(1, 30)
        shift = 2*N*rand()
        x = ones([N])
        xx = m.circshift(x, shift)
        self.assertArraysClose(x, xx)

    def test_multiple_dimensions(self):
        shape = array([5, 11, 20, 6])
        shift = randint(30, size=shape.shape)
        x = rand(*shape)
        xx = m.circshift(x, shift)
        self.assertArraysClose(x, xx)

class TestOuter(NumericTestCase):

    def test_2(self):
        a = array([1, 2])
        b = array([0, 0, 4])
        ab = m.outer(a, b)
        ab_true = array([[0, 0, 4],
                         [0, 0, 8]])
        self.assertArraysClose(ab, ab_true)

    def test_3(self):
        a = array([1, 2])
        b = array([0, 4])
        c = array([1, 2])
        abc = m.outer(a, b, c)
        abc_true = array([[[0, 4],
                           [0, 8]],
                          [[0, 8],
                           [0, 16]]])
        self.assertArraysClose(abc, abc_true)

    def test_by_definition(self):
        a = around(10*rand(5, 6))
        b = around(30*rand(3))
        c = around(40*rand(5, 6, 7))
        outer_true = empty([5, 6, 3, 5, 6, 7])
        for i in arange(5):
            for j in arange(6):
                for k in arange(3):
                    for l in arange(5):
                        for n in arange(6):
                            for o in arange(7):
                                outer_true[i,j,k,l,n,o] = a[i,j]*b[k]*c[l,n,o]

        outer = m.outer(a, b, c)
        self.assertArraysClose(outer, outer_true)


if __name__ == '__main__':
    unittest.main()

import unittest

from pylab import *
import pylab as pl
import scipy

import mymath as m

PLOTTING = False

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

class TestRegister(unittest.TestCase):

    def setUp(self):
        self.img0 = scipy.misc.lena()
        self.img0ft = fft2(self.img0)
        ny, nx = self.img0.shape
        self.ny = ny
        self.nx = nx
        self.row_shift = randint(self.nx)
        self.col_shift = randint(self.ny)
        self.img1 = m.circular_shift(self.img0ft, 
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
        img1 = m.circular_shift(img0ft, row_shift, col_shift, transformed=True)
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

class TestDFTUpsample(unittest.TestCase):

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

        # pick random odd upsampling
        upsample = randint(1, 16)
        upsample = 4
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

        # calculate the slow way
        padded = zeros([upsample*ny, upsample*nx], dtype='complex')
        padded[half*ny:(half+1)*ny,half*nx:(half+1)*nx] = fftshift(a)
        padded = ifftshift(padded)
        paddedft = ifft2(padded)
        b_slow = paddedft[
            top:top + height,
            left:left + width,
        ]

        # calculate the fast way
        b_fast = m.upsampled_idft2(a, upsample, height, width, top, left)

        if PLOTTING:
            subplot(411)
            imshow(aa)
            subplot(412)
            imshow(abs(paddedft))
            subplot(413)
            imshow(abs(b_fast))
            subplot(414)
            imshow(abs(b_slow))
            title('{}x{} starting at {}x{}'.format(height, width, top, left))
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
        self.assertTrue(np.allclose(b_slow, b_fast))

    def test_normalization(self):
        """The function should be properly normalized."""
        a = ones([10, 10])
        aa = fft2(a)
        b = m.upsampled_idft2(aa, 3, 30, 30, 0, 0)
        self.assertAlmostEqual(amax(a), amax(abs(b)))

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
        self.assertTrue(np.allclose(ifft2(a), m.dot(F, a, F)/nx/ny))

if __name__ == '__main__':
    unittest.main()

from os.path import exists, splitext
from re import search

from numpy import array
from pylab import * # TODO: eventually only use necessary imports
from scipy import interpolate
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splrep, sproot, splev
import numpy as np

class MultiplePeaks(Exception): pass
class NoPeaksFound(Exception): pass

## IMAGE PROCESSING

def corr(a, b):
    """Circular correlation using fourier transform."""
    A = fftn(a)
    A[0, 0] = 0.0
    A = A/std(a)
    if a is b:
        B = A
    else:
        B = fftn(b)
        B[0, 0] = 0.0
        B = B/std(b)
    Nx, Ny = a.shape
    G = ifftn(A*conj(B))/Nx/Ny
    if a.dtype.kind == 'f':
        G = real(G)
    return G


def autocorr(a):
    """Circular autocorrelation using fourier transform."""
    return corr(a, a)


def register(img0, img1, upsample=1, transformed=False):
    """
    Efficiently register two images to a given fraction of a pixel.

    The upsampling determines the precision of the registration; for example,
    and upsampling of 10 will register the images to within 1/10th of a pixel.

    The algorithm is based off of the following citation:
        Manuel Guizar-Sicairos, Samuel T. Thurman, and James R. Fienup, 
        "Efficient subpixel image registration algorithms," Opt. Lett. 33, 
        156-158 (2008).

    Arguments:
        img0 - first image (or its fft, not fftshifted)
        img1 - second image (or its fft)
        upsample - amount of upsampling
        transformed - have the inputs been transformed?
    """

    def peak_shift_from_index(img):
        """
        Determine the image shift from the correlation.

        Because the correlation is taken in the fourier domain, it is a
        "circular correlation," and thus a negative shift appears to wrap
        around the other side of the correlation image; this function accounts
        for this.  
        
        Note that if you have shifts greater than half the image size it is
        ambiguous because of the circular nature of the correlation.  To simplify
        the code, all shifts are assumed to be less than half the image
        size.

        Also note that the original images were assumed to be real.
        """
        ny, nx = img.shape
        row, col = unravel_index(argmax(img), (ny, nx))
        if row > floor(ny/2):
            row = row - ny
        if col > floor(nx/2):
            col = col - nx
        return row, col

    if not transformed:
        img0ft = fft2(img0)
        img1ft = fft2(img1)
    else:
        img0ft = img0
        img1ft = img1

    ny, nx = img0ft.shape
    corr_img = ifft2(img1ft*conj(img0ft))
    corr_img = abs(corr_img) 
    row_first_guess, col_first_guess = peak_shift_from_index(corr_img)

    if upsample > 1:
        # define portion of image centered on the first guess
        side = 3.0
        height = width = ceil(side*upsample)
        top = round((row_first_guess - side/2.0)*upsample)
        left = round((col_first_guess - side/2.0)*upsample)

        # calculate zero-padded inverse dft on area around first guess
        a = img1ft*conj(img0ft)
        b = upsampled_idft2(a, upsample, height, width, top, left)
        b = abs(b) # removing leftover imaginary part

        imshow(b); figure(); imshow(img0); show()

        # use upsampled idft to find max in terms of the original images pixels
        sub_row, sub_col = unravel_index(argmax(b), b.shape)
        row_final_guess = (top  + sub_row)/upsample
        col_final_guess = (left + sub_col)/upsample
    else:
        row_final_guess = row_first_guess
        col_final_guess = col_first_guess

    return row_final_guess, col_final_guess


def upsampled_idft2(a, upsample, height, width, top, left):
    """
    Calculate a portion of the upsampled inverse DFT of a using a matrix.
    
    Height, width, top and left specify the portion of the IDFT that will be
    taken in terms of upsampled pixels

    The returned array is normalized so that it has the same values as
    ift(input) --- of course there will be slight variations due to
    interpolatation.

    See G. Strang, Introduction to Linear Algebra, Section 10.3 for some
    explanation of the fourier matrices.
    """

    rows_a, cols_a = a.shape

    # generate matrix that does the column inverse dft
    wc = np.fft.fftfreq(cols_a)/upsample
    wr = arange(left, left + width)
    w = outer(wc, wr)
    kernc = exp(2j*pi*w)

    # generate matrix that does the row inverse dft
    wc = np.fft.fftfreq(rows_a)/upsample
    wr = arange(top, top + height)
    w = outer(wr, wc)
    kernr = exp(2j*pi*w)

    norm = rows_a*cols_a

    return dot(kernr, a, kernc)/norm


def circular_shift(img, row_shift, col_shift, transformed=False):
    """Subpixel shift an image using the Fourier-shift theorem."""

    if not transformed:
        imgft = fft2(img)
    else:
        imgft = img
    nx, ny = imgft.shape
    x = linspace(0, 1, nx, endpoint=False)
    y = linspace(0, 1, ny, endpoint=False)
    Y, X = meshgrid(y, x)
    shiftedft = imgft*exp(-(Y*col_shift + X*row_shift)*2j*pi)
    return ifft2(shiftedft)


def interp_max(img, x=None, y=None, precision=10):
    """
    Find the maximum value in an image using cubic interpolation.

    Assumes that the maximum value is near the maximum pixel.
    
    Arguments:
    X - x grid positions
    Y - y grid positions
    precision - increase in grid spacing from interpolation

    Returns:
    max - the value of the maximum
    x - the x position of the maximum
    y - the y position of the maximum
    """
    nx, ny = img.shape
    if x == None:
        x = arange(nx)
    if y == None:
        y = arange(ny)

    # find max of current image
    xmax, ymax = unravel_index(argmax(img), img.shape)

    # create subimg centered around the maximum
    xe, ye = closest_in_grid(nx, ny, xmax + 5, ymax + 5)
    xs, ys = closest_in_grid(nx, ny, xmax - 5, ymax - 5)
    xe = x[xe]
    ye = y[ye]
    xs = x[xs]
    ys = y[ys]

    # +1 to stay on original grid
    xx = linspace(xs, xe, precision*(xe - xs) + 1) 
    yy = linspace(ys, ye, precision*(ye - ys) + 1)
    XX, YY = meshgrid(xx, yy)

    X, Y = meshgrid(x, y)
    points = zip(X.flatten(), Y.flatten())

    sum_img = img[xs:xe, ys:ye]
    values = img.flatten()
    ZZ = interpolate.griddata(points, values, 
            (XX.flatten(), YY.flatten()), method='cubic')
    imax = argmax(ZZ)
    xmax, ymax = unravel_index(imax, XX.shape)
    return XX[xmax, ymax], YY[xmax, ymax], ZZ[imax]


## GENERAL SIGNAL PROCESSING

# TODO: test this
def findpeaks(X, threshold=None, smooth=1, width=1):
    """ 
    Find peaks in an array.

    optional parameters:
    smooth - apply a moving average of this length, default=1
    width - the approximate width of the peak
    """
    N = len(X)
    if not smooth == 1:
        X = convolve(X.astype(float), ones(smooth), mode='same')/smooth

    peaks = []
    indices = []
    for i in range(width, N - width):
        fd1 = X[i] - X[i+1]
        bd1 = X[i] - X[i-1]
        fdw = X[i] - X[i+width]
        bdw = X[i] - X[i-width]
        if fdw > 0 and bdw > 0 and fd1 > 0 and bd1 > 0:

            if threshold:
                if fd1 < threshold or bd1 < threshold:
                    break

            peaks.append(X[i])
            indices.append(i)

    return array(indices)


def findvalleys(X, *args, **kwargs):
    """Find the valleys in an array.  Same options as findpeaks."""
    return findpeaks(-X, *args, **kwargs);


def fwhm(x, y):
    """
    Determine full-with-half-maximum of a peaked set of points, x and y.

    Assumes that there is only one peak present in the datasset.  The function
    uses a spline interpolation of order k.
    """
    half_max = amax(y)/2.0
    s = splrep(x, y - half_max)
    roots = sproot(s)
    
    if len(roots) > 2:
        raise MultiplePeaks("The dataset appears to have multiple peaks, and "
                "thus the FWHM can't be determined.")
    elif len(roots) < 2:
        raise NoPeaksFound("No proper peaks were found in the data set; likely "
                "the dataset is flat (e.g. all zeros).")
    else:
        return abs(roots[1] - roots[0])


## VISUALIZATION

# TODO: handle zero-padding appropriatly
def savenextfig(fname, *arrs):
    """
    Save figure using next available numbered name.

    If no number is present in the name, then 0 is used.
    
    examples:
        hello.png --> hello0.png
        already_five.png --> already_five6.png

    """
    while exists(fname):
        fname_noext, ext = splitext(fname)
        match = search(r'(.*[^\d])(\d+)$', fname_noext)
        if match:
            num = str(int(match.group(2)) + 1)
            fname = match.group(1) + num + ext
        else:
            fname = fname_noext + '0' + ext
    savefig(fname, *arrs)


def interact(func, x, y, adjustable):
    """ Interactively plot a functions' values. 

    Arguments:
    func -- the function that generates the plotted values
    x -- a string, indicating the variable to be plotted on the x-axis
         if None, the y-values will be plotted against their indicies
         if it is a numpy array, it will be used for plotting
    y -- a string, indicating the variable to be plotted on the y-axis
    adjustable -- a dict whose key's are the names of variables being
         passed to func, and value can be either a value, or a tuple.
         If the value is a single value, it will be staticly passed to 
         func on every plot update.
         If the value is a tuple, a slider will be generated that will allow 
         you to vary this function through out these values.  The initial 
         value will be in the middle of the range.
    """

    from matplotlib.widgets import Slider, Button, RadioButtons
    
    # initialize arguments
    args = {}
    for k, v in adjustable.items():
        if not isinstance(v, tuple):
            del adjustable[k] # remove static variables
            args[k] = v

    # get vars from sliders, run func, then plot
    def run_and_plot(event):
        for sl in sliders:
            args[sl.label.get_text()] = sl.val

        ret = func(**args)
        if not y:
            yval = ret
        else: # if isinstance(y, (str, int))
            yval = ret[y]

        if isinstance(x, (str, int)):
            xval = ret[x]
        else:
            xval = x
        pax.plot(xval, yval, lw=2, axes=pax)
        draw()
    
    # inialize the plot
    pax = subplot(111)
    subplots_adjust(bottom=0.25)
    
    bot = 0.1
    axs = []
    sliders = []
    for var, ends in adjustable.items():
        axs.append(axes([0.15, bot, 0.75, 0.03]))
        bot += 0.05
        sliders.append(Slider(axs[-1], var, ends[0], ends[1], valinit=mean(ends)))

    resetax = axes([0.8, 0.025, 0.1, 0.04])
    button = Button(resetax, 'Plot', hovercolor='0.975')
    button.on_clicked(run_and_plot)

    run_and_plot(None) # make the first plot
    show()


def scatter3(X, Y, Z):
    """Create a 3D scatter plot."""
    fig = figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter3D(X, Y, Z)
    return fig
    

def plot_fwhm(x, y, k=10):
    y_max = amax(y)
    s = splrep(x, y - y_max/2.0)
    r1, r2 = sproot(s)
    xx = linspace(amin(x), amax(x), 200)
    yy = splev(xx, s) + y_max/2.0

    f = figure()
    plot(x, y, 'ko')
    plot(xx, yy, 'r-')
    axvspan(r1, r2, facecolor='k', alpha=0.5)
    return f



## CONVENIENCE FUNCTIONS 

def closest_in_grid(gx, gy, x, y):
    """Given grid size and a point, return the closest point in the grid."""

    x = max(min(gx - 1, x), 0)
    y = max(min(gy - 1, y), 0)
    return x, y


# TODO: optimize this
def findf(x):
    """Return the indice of the first true value in x."""

    i = 0
    for val in x:
        if val:
            return i
        i += 1
    return false


def meshgridn(*arrs):
    """A multi-dimensional version of meshgrid."""

    arrs = tuple(reversed(arrs))
    lens = map(len, arrs)
    dim = len(arrs)

    sz = 1
    for s in lens:
        sz *= s

    ans = []    
    for i, arr in enumerate(arrs):
        slc = [1]*dim
        slc[i] = lens[i]
        arr2 = asarray(arr).reshape(slc)
        for j, sz in enumerate(lens):
            if j!=i:
                arr2 = arr2.repeat(sz, axis=j) 
        ans.append(arr2)
    return tuple(ans)


def dot(*arrays):
    """
    Dot product of many arrays.
    
    For 2-D arrays it is equivalent to matrix multiplication, and for 1-D
    arrays it is the inner product without taking the complex conjugate.  For
    N-D arrays it is the sum of the product over the last two axis.
    """
    
    if len(arrays) < 2:
        raise TypeError("Need at least two matrices to multiply.") 
    
    out = np.dot(arrays[0], arrays[1])
    for m in arrays[2:]:
        out = np.dot(out, m)
    return out


@vectorize
def iseven(el):
    return 1 - el % 2


@vectorize
def isodd(el):
    return el % 2

def padarray(a, padsize, padval=0):
    d = a.shape
    out = zeros(d + padsize)


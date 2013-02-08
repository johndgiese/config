from os.path import exists, splitext
from re import search

from numpy import array
from pylab import * # TODO: eventually only use necessary imports
from scipy import interpolate
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splrep, sproot, splev

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

def linescan(img, start, stop, npoints, method='cubic'):
    """
    Extract line scan from an image.

    Points outside the image indices are set to the mean of the image.
    
    Arguments:
    img - the image being interpolated on
    start - tuple specifying the start indices
    stop - tuple specifying the end indices
    npoints - the number of points in the linescan
    method - the kind of interpolation {'linear', 'nearest', 'cubic'}
    """
    nx, ny = img.shape
    x = linspace(start[0], stop[0], npoints)
    y = linspace(start[1], stop[1], npoints)

    x_grid = arange(nx)
    y_grid = arange(ny)
    x_grid, y_grid = meshgrid(x_grid, y_grid)
    points = zip(x_grid.flatten(), y_grid.flatten())
    z = interpolate.griddata(points, img.flatten(), (x, y), method=method)
    return x, y, z


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
        sz*=s

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


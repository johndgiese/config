from numpy import array
from os.path import exists, splitext
from re import search
from pylab import zeros, savefig, fftn, ifftn, fftshift, conj, isreal, real

def autocorr(a, rmimag=True):
    """ N-d circular autocorrelation using fourier transform. """
    A = fftn(a)
    G = fftshift(ifftn(A*conj(A)))
    if rmimag and a.dtype.kind == 'c':
        G = real(G)
    return G

def mean_autocorr(I):
    """ Mean autocorrelation across the columns of an image. """
    m, n = I.shape
    mac = zeros(m)
    for col in I.T:
        mac += autocorr(col, rmimag=False)
    if I.dtype.kind == 'c':
        mac = real(mac)
    return mac

# TODO: test this
def findpeaks(X, threshold=None):
    N = len(X)
    peaks = []
    indices = []
    for i in range(2, N - 1):
        fd = X[i] - X[i+1]
        bd = X[i] - X[i-1]
        if fd > 0 and bd > 0: # is it a peak?
            # if it is, run other tests...

            if threshold:
                if fd < threshold or bd < threshold:
                    break

            # if it passes all tests, append to result arrays
            peaks.append(X[i])
            indices.append(i)

    return array(peaks), array(indices)

def findvalleys(X, *args, **kwargs):
    pks, ind = findpeaks(-X, *args, **kwargs);
    return -pks, ind

# TODO: optimize this
def findf(x):
    """ Return the indice of the first true value in x. """
    i = 0
    for val in x:
        if val:
            return i
        i += 1
    return false

""" from stack-exchange: http://stackoverflow.com/questions/1827489/numpy-meshgrid-in-3d """
def meshgridn(*arrs):
    arrs = tuple(reversed(arrs))  #edit
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

def savenextfig(fname, *arrs):
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
    


    


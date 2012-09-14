from pylab import *
import warnings
import beam
# import ray

# TODO: implement polarization submodule
# TODO: implement ray submodule

C = 299792458 # celeritas [m/s]
H = 6.62606957e-34 # Planck's constant [J/s]
HBAR = H*2*pi # Reduced Planck's constant [J*rad/s]


def fabry_perot(nu, r1, r2, d):
    F = pi*sqrt(abs(r1*r2))/(1 - abs(r1*r2))
    T_max = (1 - abs(r1)**2)*(1 - abs(r2)**2)/(1 - abs(r1*r2))**2
    nu_F = C/(2*d)
    T = T_max/(1 + (2*F/pi*sin(pi*nu/nu_F))**2)
    return T

def fabry_perot_emp(nu, T_min, T_max, nu_F):
    """ Returns Spectral Intensity Transmission of a Fabry Perot.

    The transmission is evaluated at the provided frequencies.  This function
    is most useful for simulating known equipment, because the parameters are
    three measureable quantities, T_min and T_max are the intensity
    transmission maximums, and nu_F is the frequency spacing. """
    if T_min > T_max:
        warnings.warn("T_min is greater than T_max!? Switching the variables for you...")
        T_min, T_max = T_max, T_min
    if T_min < 0 or T_max < 0 or T_min > 1 or T_max > 1:
        raise ValueError(" T_min and T_max must be between 0 and 1.")

    F = sqrt(T_max/T_min - 1)*(pi/2)
    return T_max/(1 + (2*F/pi*sin(pi*nu/nu_F))**2)

def gaussian_spectra(nu, nu0, tau, a=0):
    """ Return the shape of the spectral intensity of a chirped Gaussian Pulse.

    Notice that there is no power or intensity included here; you need to
    multiply this yourself.  E.g.:

    nu = linspace(nu_min, num_max, 200)
    nu0 = mean(nu_min, num_max)
    S = I0*gaussian_spectra(nu, nu_0, tau, a=2)

    See Eqn. 22.1-19 
    Actually, there was a mistake in Eqn. 22-1-19 (it is corrected in 3e)"""

    k = pi*tau**2/sqrt(1 + a**2)
    S = k*exp(-2*(pi*tau*(nu-nu0))**2/(1 + a**2))
    return S

# FIXME
def gaussian_field(nu, nu0, tau, a=0):
    """ Return the spectral field of a chirped Gaussian Pulse.

    Notice that there is no power or intensity included here; you need to
    multiply this yourself.

    See Eqn. 22.1-19 """

    k = tau/(2*sqrt(pi*(1 - 1j*a)))
    return k*exp(-(pi*tau*(nu - nu0))**2/(1 - 1j*a))

def fresnel_fourier(U0, z, wl=633e-9, dx0=10e-6, dy0=10e-6):
    """ Propagate a coherent optical field using the Fourier form of the Fresnel eqn. """
    U1 = empty(U0.shape, dtype='F')

    Nx, Ny = U0.shape
    dx1 = dx0/(wl*z)
    dy1 = dy0/(wl*z)
    x0lim = (Nx - 1)*dx0/2
    y0lim = (Ny - 1)*dy0/2
    x1lim = (Nx - 1)*dx1/2
    y1lim = (Ny - 1)*dy1/2
    x1 = linspace(-x1lim, x1lim, Nx)
    y1 = linspace(-y1lim, y1lim, Ny)
    X1, Y1 = meshgrid(x1, y1)
    R2 = X1**2 + Y1**2
    del X1, Y1

    k = 2*pi/wl

    # the factor of 5 is arbitrary
    lhs = z**3
    rhs = pi/(4*wl)*((x1lim + x0lim)**2 + (y1lim + y0lim)**2)**2
    if lhs < 5*rhs:
        warning = 'The Fresnel approximation may not be valid!\n \
                z**3 >> pi/(4*wl)*max((x1 - x0)**2 + (y1 - y0)**2)**2\n \
                in your case the rhs is %g times the lhs.\n' % (rhs/lhs)
        warnings.warn(warning)

    pre = exp(1j*k*z + 1j*k/(2*z)*R2)/(1j*wl*z)

    # resuse X1 and Y1 (by scalling with 1/(wl*z)**2), 
    # to avoid exccesive memory use
    U1 = pre*fftshift(fft2(U0*exp(1j*k/(2*z)*R2*(wl*z)**2)))

    return U1, dx1, dy1


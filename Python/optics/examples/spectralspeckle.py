""" This module implements a number of functions related to my investigations
of spectral speckle, and the temporal effects of strong scattering. """

def GI_slab(zF, zR, wl0, nus, n=1.4, ls=2.9e-3, z=1e-3):
    """ Intensity correlation of a Gaussian beam after a scattering slab.

    Beam Properties:
        zF  -- distance from the front surface to the focal plane
        zR  -- Rayleigh range of the beam
        wl0 -- center wavelength
        nus -- wavelength shifts used calculate the correlation

    Sample Properties:
        n   -- index of refraction of the slab
        ls  -- reduced scattering mean free path
        z   -- thickness of the slab

    The default sample properties are for a 1mm slab of mouse brain.
    """

    bs = 2*pi*n/wl0/ls
    es = wl0*nus/3e8
    num = zR**2 + zF**2 + z**2 - 2*zF*z + 2/3*bs*zR*z**3
    dem = (zR**2 + zF**2 + zF*z + 1j*2*zR*z/es)*cos(z*sqrt(1j*bs*es)) + \
            (z**2 - 3*zF*z - 1j*2*zR*z/es)*sinc(z*sqrt(1j*bs*es))
    return num/dem


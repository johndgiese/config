"""The toolbox provides a set of classes that may be used to assist in
simulating Gaussian Beam propagation through optical systems.  

Note: throughout the code, equations are refering to Fundamentals of Photonics,
2e Saleh and Teich -- a great book

Also Note: MKS units are used throughout, even for absorption cross sections
etc."""
# TODO: improve commenting

from scipy.optimize import fsolve
import numpy as np
import warnings
from collections import Iterable
from math import pi, sqrt, exp, log, atan
from copy import deepcopy
import optics

class Beam:
    """An ideal monochromatic Gaussian beam.

    The beam object retains its position along the optical axis, and
    propagating it through optical elements will modify its internal state
    appropriatly.

    There are a few different ways to initialize the beam.  All methods require
    you to specify the wavelength (wl) and power (p).  You can optionally
    specify dz which is used for recording purposes (see details below).  There
    are two remaining degrees of freedom, which can be specified using the
    following methods:

    Method 1:
        Beam(p=power, w=width, r=radius-of-curvature, wl=wavelength)
            power = power of the beam [W]
            width = the radius/width of the beam [m]
            radius = radius-of-curvature [m]
            wavelength = wavelength of the beam [m]
            dz = the maximum beam propagation beteween recordings [m]
                leave it as float('inf') if you don't want to record -- see
                below for more details on this functionality.

    Method 2:
        Beam(p=power, wl=wavelength, r1=width1, r2=width2, / 
            d1=distance-to-plane1, d2=distance-to-plane2)

        This second method requires two measurements of the beam radius (r1 and
        r2), and the distance from the measurements to the plane where the Beam
        object will be initialized (d1 and d2).  See eqn. 3.1-27 and 3.1-28.

                    d1         r1 is radius-of-curvature here
        |<-------------------->| 
        |<------------------------------>|
        ^           d2                   r2 is the radius-of curvature here
        |
        This is the position of the initialized beam

        I don't know when this initialization method would every be useful...

    Method 3:
        Beam(p=power, wl=wavelength, w1=width1, w2=width2, / 
            d1=distance-to-plane1, d2=distance-to-plane2, winside=False)

                        d1         w1 is the waist radius here
            |<-------------------->| 
            |<------------------------------>|
            ^           d2                   w2 is the waist radius here
            |
            This is the position of the initialized beam

        There is an additional keyword argument (winside) because there are two
        possible solutions given the width of the beam at two locations; either
        the location of the waist-radius could lie between the two measurement
        planes (between d1 and d2), or on beyond the smaller of the two.  It is
        physically impossible that the waist radius lie beyond the larger
        radius measurement.  
        
        Often the which of these two possibilites will be know before hand by
        the person characterizing the beam.  The boolean parameter winside
        specifies whether the waist radius is located between the two
        measurements, our outside of them; it defaults to False because this is
        how we usually take the measurements.

        This method is certainly the most useful when simulating real beams
        where you have measured the waist radius.  See:
            McCally 1984 Measurement of Gaussian beam parameters, Applied
            Optics Vol. 23, No. 14 pp. 227

    One very powerful feature of the Beam object, is its ability to track and
    store its states as it propagates through the system.  This feature is off
    by default, but if dz is greater than 0, the values of the expressions
    contained in the static expr_to_record list will be recorded at each
    propagation step.  If any propagation step will propagate the beam forward
    more than dz, the Beam will automatically split the propagation into
    smaller pieces.
    
    Example:
        # initialize a 10 mW beam, at its waist radius (hence the infinity)
        b1 = Beam(p=10e-3, w=1e-3, r=float('inf'), wl=800e-9)
        b1.echo('initial beam properties') # print all the beam properties
        b1.prop(Space(3e-2)).echo('after propagating 3cm')
        b1.prop(Lens(3e-2)).echo('after lens')
        b1.prop(Space(3e-2)).echo('at other focal plane')

    """
    # TODO: test phase
    # TODO: add intensity plot
    
    _beam_vars = ['p', 'w', 'r', 'wl', 'nu', 'z', 'z0', 'W0', 
            'phase', 'I', 'div']

    # these are the variables that are plotted by the echo function
    # note that some of the values are actually calcualted using functions, so
    # the parenthesis are required after them
    expr_to_record = ['p', 'w', 'r', 'z', 'z0']

    def __init__(self, p=10e-3, wl=632e-9, dz=float('inf'), **kwargs):
        """ See the documentation for the Beam object. """
        self.p = p
        self.wl = wl
        self.dz = dz

        # figure out how we are inializing the beam
        if kwargs.has_key('d1') and kwargs.has_key('d2'):
            d1 = kwargs['d1']
            d2 = kwargs['d2']

            if kwargs.has_key('r1') and kwargs.has_key('r2'):
                # TODO: implement this (see Exercise 3.1-5 of FOP)
                raise NotImplementedError("Sorry :(")

            elif kwargs.has_key('w1') and kwargs.has_key('w2'):
                # The following equations were solved in Mathematica:
                #    w1 = W0*sqrt(1 + (z*wl/W0**2/pi)**2)
                #    w2 = W0*sqrt(1 + ((z + d)*wl/W0**2/pi)**2)
                # where we are solving for W0 and z, and wl, d, W1 and W2 are known
                
                w1 = kwargs['w1']
                w2 = kwargs['w2']
                if d1 > d2:
                    warnings.warn("When initializing a beam, d1 should be greater \
                            than d2.  We swapped the parameters for you.")
                    d1, d2 = d2, d1
                    w1, w2 = w1, w2
                d = d2 - d1

                if kwargs.get('winside', False):
                    num = d**2*pi*(w1**2 + w2**2)*wl**2 + \
                           2*sqrt(d**4*pi**2*w1**2*w2**2*wl**4 - d**6*wl**6)
                    den = pi**3*(w1**2 - w2**2)**2 + 4*d**2*pi*wl**2
                    W0 = sqrt(num/den)

                    num = d**2*pi**2*w1**2*(-w1**2 + w2**2)*wl**2 - \
                        2*d**4*wl**4 + pi*(-w1**2 + w2**2)*\
                        sqrt(d**4*pi**2*w1**2*w2**2*wl**4 - d**6*wl**6)
                    den = d*wl**2*(pi**2*(w1**2 - w2**2)**2 + 4*d**2*wl**2)
                    z = d1 - num/den
                else:
                    num = d**2*pi*(w1**2 + w2**2)*wl**2 - \
                            2*sqrt(d**4*pi**2*w1**2*w2**2*wl**4 - d**6*wl**6)
                    den = pi**3*(w1**2 - w2**2)**2 + 4*d**2*pi*wl**2
                    W0 = sqrt(num/den)

                    num = d**2*pi**2*w1**2*(-w1**2 + w2**2)*wl**2 - \
                            2*d**4*wl**4 + pi*(w1**2 - w2**2)*\
                            sqrt( d**4*pi**2*w1**2*w2**2*wl**4 - d**6*wl**6 )
                    den = d*wl**2*(pi**2*(w1**2 - w2**2)**2 + 4*d**2*wl**2)
                    z = d1 - num/den
                z0 = W0**2*pi/wl
                self.r = z*(1 + (z0/z)**2)
                self.w = W0*sqrt(1 + (z/z0)**2)

        elif kwargs.has_key('r') and kwargs.has_key('w'):
            self.w = w
            self.r = r # distance to waist radius
        else:
            raise TypeError("Incorrect Beam initialization.  See the \
                    documentation for Beam")

        # initialize record keeping if dz is less than infinity
        if not self.dz == float('inf'):
            self.recording = True
            self.records = {}
            for var in Beam.expr_to_record:
                self.records[var] = []
        else:
            self.recording = False

    def __str__(self):
        ret_str = ''
        for k in Beam.expr_to_record:
            ret_str += '  ' + str(k) + ' = '
            item = eval('self.' + k)
            if hasattr(item, '__call__'):
                ret_str += str(item()) + '\n'
            else:
                ret_str += str(item) + '\n'
        return ret_str

    def _take_records(self):
        for expression, record_holder in self.records.items():
            record_holder.append(eval('self.' + expression))

    def copy(self, n=1):
        """ Return n copies of the beam.

        Ordinarily propagating a beam changes its state, thus if you want
        to keep a record of the state before a propagation for comparison, you
        may need to copy the beam first, and propagate the copied beam.

        By default a single beam is returned, however if you provide n = 10, 
        it will return a list of 10 beams.
        This function is also useful if you want to compare the results of
        propagating a beam through a number of different systems."""

        if n == 1:
            return deepcopy(self)
        else:
            out = []
            for x in xrange(n):
                out.append(deepcopy(self))
            return out
        
    def prop(self, oes):
        """ Propagate the beam through an optical element, returning the beam.

        This is the primary method of "moving" the beam through an optical setup.
        Note that because propagation always returns the beam object, several 
        propagations can be strung together.  For example a simple 1-f system
        would be expressed as follows:
            b = Beam()
            f = 1e-3
            b.prop(Space(f)).prop(Lens(f)).prop(Space(f))
        or equivalently:
            b.prop([Space(f), Lens(f), Space(f)])

        Also note that if a number is provided instead of an optical element, 
        then the beam is propagated through space, i.e.:
            b.prop(3-e3)
            b.prop(Space(3e-3))
        are equivalent. Also the previous example can be written more compactly:
            b.prop([f, Lens(f), f])
        """
        if not isinstance(oes, Iterable):
            oes = [oes]

        for oe in oes:
            if isinstance(oe, (int, float)):
                oe = Space(float(oe))
            if self.recording:
                if isinstance(oe, Space):
                    # if the propagation distance is longer than
                    if oe.d > self.dz:
                        final_z = oe.d + self.z
                        while self.z < (final_z - self.dz):
                            self.prop(Space(self.dz))
                        # propagate the last little bit
                        return self.prop(Space(final_z - self.z))
                self._take_records()

            oe.transmit(self)
        return self


    @property
    def nu(self):
        """ Calculate the wavelength of the light of the beam [Hz]. """
        return 299792458/self.wl

    @property
    def r(self):
        """ Radius of curvature (different than the radius!). """
        z = self.z
        z0 = self.z0
        return z*(1 + (z0/z)**2)
    
    @property
    def z(self):
        """ Distance from current position of the beam, to the beam radius.
        
        Note that positive distances indicates the beam waist is to the left
        (see eqn 3.1-25). """
        if self.r == float('inf'):
            return 0
        return self.r/(1 + pow(self.wl*self.r/(pi*self.w*self.w),2))

    @property
    def W0(self):
        """ Calculate the waist radius, or width, of the beam (eqn 3.1-26)."""
        if self.r == float('inf'):
            return self.w
        return self.w/sqrt(1 + pow((pi*pow(self.w,2))/(self.wl*self.r),2))

    @property
    def z0(self):
        """ Calculate the rayleigh range (eqn 3.1-11).""" 
        return pow(self.W0,2)*pi/self.wl

    def phase(self, r=0):
        """ Calculate the phase of the Guassian beam (eqn. 3.1-23).
        
        Takes a single, arguemnt to specify the radial position.  
        If omitted, defaults to the on-axis position."""

        k = 2*pi/self.wl
        z = self.z
        onaxis_phase = k*z - atan(z/self.z0)
        return onaxis_phase + k*r*r/(2*self.r)

    @property
    def div(self):
        """ Calculate the beam divergence angle (eqn. 3.1.21)

        Note that the divergence angle = \theta_0*2, using the notation of FOP2
        """
        return 2*self.wl/(pi*self.W0)

    def I(self, r=0):
        """ Calculate the intensity of the Gaussian beam (eqn 3.1-16).
        
        Takes a single, argument to specify the radial position.  
        If omitted, defaults to the on-axis position."""

        w = self.w
        I_onaxis = 2*self.p/(pi*w*w)
        return I_onaxis*exp(-2*r**2/(w*w))

    @property
    def A(self):
        """ the cross-sectional area of the beam """

        return pi*pow(self.w,2)

    def echo(self, comment=None):
        """Print the beam properties"""
        if comment:
            print(comment)
        print(self)
        return self

# TODO: extend echo functionality for Beam subclasses
class PulsedBeam(Beam):
    """ A pulsed beam. """

    def __init__(self, p, w, r, wl, rr, dz=float('inf')):
        Beam.__init__(self, p, w, r, wl, dz=dz)
        self.rr = rr
    def E(self):
        return self.p/self.rr

# TODO: implement a set of beams
#class Beams:
    #""" a convenience class for investigating the parameters space of an 
    #experiment. """
    #def __init__(self, power, width, radius, wavelength):
        ## TODO: implement this for more than two parameters
        ## TODO: implement this for two parameters
        ## TODO: extend this to work with any iterable
        ## convert all objects to numpy arrays
        #shape = []
        #self.p = array(power, ndmin=1); shape.append(len(power))
        #self.w = array(width, ndmin=1); shape.append(len(width))
        #self.r = array(radius, ndmin=1); shape.append(len(radius))
        #self.wl = array(wavelength, ndmin=1); shape.append(len(wavelength))
        #self.shape = shape

        ## there has to be a better way to do this...
        #self.Beams = np.empty(shape, dtype=Beam)
        #_eachbeam(Beam.__iter__)
            
    #def _eachbeam(self, func):
        #for p in range(shape[0]):
            #for w in range(shape[1]):
                #for r in range(shape[2]):
                    #for wl in range(shape[3]):
                        #func(self.Beams[p,w,r,wl],
                                #self.p[p],
                                #self.w[w],
                                #self.r[r],
                                #self.wl[wl])

    #def get(self, varname):


class OpticalElement:
    """ An abstrac class for optical elements. """
        
    def transmit(self):
        raise NotImplementedError("must have a transmit method")

    def __str__(self):
        ret_str = ''
        for k, v in self.__dict__.items():
            ret_str += '  ' + str(k) + ' = ' + str(v) + '\n'
        return ret_str

    def echo(self, comment):
        print(comment)
        print(str(self))
        return
    # TODO:
    #def reflect(self):
        #pass
    #def plot():
        #pass

class Lens(OpticalElement):
    """ A common lens.
    
    Lens(focallength)
        focalength = focallength of the lens [m]
    """
    def __init__(self, focallength):
        self.f = focallength
    def transmit(self, beam):
        # writting the equation this way ensures that it works well with inf
        beam.r = 1/(1/beam.r - 1/self.f) # see eqn 3.2-2
        return beam
    def M(self, beam):
        f = self.f
        z = beam.z
        if z - f == 0:
            return f/beam.z0()
        else:
            Mr = abs(f/(z - f))
            r = beam.z0/(z - f)
            return Mr/sqrt(1 + r**2)

class Obj(Lens):
    """ An Objective lens, specified by magnification and manufacturer.

    """

    def __init__(self, mag, co="Olympus"):
        # TODO: add more companies
        self.mag = mag
        if co == "Olympus":
            f_tube = 180e-3
        else:
            f_tube = 180e-3
        f_obj = abs(f_tube/mag)
        Lens.__init__(self, f_obj)

class Space(OpticalElement):
    """ The most basic optical element.
    
    Space(distance)
        distance = distance the beam will travel [m]

    Negative distances propagate backwards, so:
        b = Beam(p=1e-3, r=1, w=2e-3, wl=800e-9)
        b.prop(Space(1e-3)).prop(Space(-1e-3))
    should not affect the beam (within roundoff error).

    Note that there is a shortcut to propagating a beam through space:
        b.prop(3-e3)
        b.prop(Space(3e-3))
    are equivalent.
    """

    def __init__(self, distance):
        self.d = distance
    def transmit(self, beam):
        W0 = beam.W0
        z = beam.z
        z0 = beam.z0
        beam.w = W0*sqrt(1 + pow((z + self.d)/z0,2)) # eqn 3.1-18
        if z + self.d == 0:
            beam.r = float('inf')
        else:
            beam.r = (z + self.d)*(1 + pow(z0/(z + self.d), 2)) # eqn 3.1-9
        return beam

# this only reduces the power of the beam, it doesn't account for diffraction
# or anything complicated like that... it is mainly useful when dealing with
# photodiodes
class Aperture(OpticalElement):
    def __init__(self, radius):
        self.r = radius
    def transmit(self, beam):
        beam.p = beam.p*(1 - exp(-2*pow(self.r,2)/pow(beam.w,2)))
        return beam

# TODO: add warning if the thin-sample approximation is violated
# TODO: add ability to pass in a tuple (wl, siga) or a function, for wavlength
# dependent absorption
class LinearAbsorber(OpticalElement):
    """ Absorber that follows Beer-lambert

    LinearAbsorber(siga, n, length)
        siga   = 'absorbption cross-section [m^2]
        n      = number density [1/m^3]
        length = length of absorber [m] 

    Note that the beam's shape is as well.
    """

    def __init__(self, siga, n, length):
        self.L = length
        self.alpha = siga*n
    def transmit(self, beam):
        beam.p = beam.p*exp(-self.L*self.alpha) # Beer-Lambert
        beam.prop(Space(self.L)) # account for space propagation
        return beam

# TODO: research more about the different types of non-linear absorbers; include
# some details about this here (maybe different classes etc.)
# TODO: currently uses the thin-sample approximation
class SaturableAbsorber(OpticalElement):
    """ Saturable absorber where: dE = -sig_a*E/(1 + E/Es) 

    SaturableAbsorber(siga, n, length)
        siga   = 'absorbption cross-section [m^2]
        n      = number density [1/m^3]
        length = length of absorber [m] 

    The saturation energy is determined by first determing the number of
    absorbers in the focal volume, then multiplying this by the energy per
    photon of the beam.

    Note that the beam's shape is as well, however effects such as self phase
    modulation and the like are not accounted for.  Also, the spatial shape of
    the beam is not accounted for.
    """
    def __init__(self, siga, n, length):
        self.L = length
        self.siga = siga
        self.n = n # number density of absorber
        self.n0 = n # this saves the inital density
        self.prev_r = None 
    def transmit(self, beam):
        if not isinstance(beam, PulsedBeam):
            raise TypeError("It doesn't make sense to consider the effects of a \
                            nonlinear absorber on anything except a pulsed beam")
        # TODO: extend this implementation to handle more complicated geometries
        #if self.prev_r and not beam.r == self.prev_r:
            #warnings.warn("The current implementation of the saturable absorber \
                         #object assumes that all incident beams have the same \
                         #radius.  The previous beam had a radius of %g [m], and \
                         #the current beam has a radius of %g [m]" \
                         #% (self.prev_r, beam.r))

        alpha_0 = self.siga*self.n
        focal_volume = self.L*(pi*beam.w*beam.w)
        E_per_absorber = beam.nu*H
        number_of_absorbers = focal_volume*self.n
        E_s = E_per_absorber*number_of_absorbers
        E_0 = beam.E
        def _f_implicit(E):
            return -alpha_0*self.L + log(E_0/E) + (E_0 - E)/E_s
        def _df_implicit(E):
            return -1/E - 1/E_s
        # the output power will always be greater than for a linear absorber
        E_1_min = E_0*exp(-self.L*alpha_0) 
        E_1 = fsolve(_f_implicit, E_1_min, xtol=E_1_min/10000,
                fprime=_df_implicit)
        # update absorber state
        self.n -= (E_0 - E_1)/(E_per_absorber*focal_volume)
        if self.n < 0:
            self.n = 0
            warnings.warn('n had become negative, so it was forcibly set to 0')
        self.prev_r = beam.r
        # update beam state
        beam.p = E_1*beam.rr
        beam.prop(Space(self.L))
        return beam
    def E_s(self, beam):
        """ Return the Pulse Saturation Energy of the Saturable absoerber, with
        respect to the provided beam."""
        alpha_0 = self.siga*self.n
        focal_volume = self.L*(pi*beam.w*beam.w)
        E_per_absorber = beam.nu*H
        number_of_absorbers = focal_volume*self.n
        E_s = E_per_absorber*number_of_absorbers
        return E_s

def main():
    pass 

if __name__ == '__main__':
    main()

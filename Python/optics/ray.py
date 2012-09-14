from pylab import *
import optics
from collections import Iterable

class RayBundle:
    def __init__(self, z, x, th):
        # TODO: figure out a better way to do this:
        isit = False
        for var in [z, x, th]:
            if isinstance(var, Iterable):
                isit = var
                break
        if not isinstance(x, Iterable):
            x = x*ones(isit.shape)
        if not isinstance(z, Iterable):
            z = z*ones(isit.shape)
        if not isinstance(th, Iterable):
            th = th*ones(isit.shape)

        self.rays = []
        for i in xrange(len(isit)):
            self.rays.append(Ray(x[i], th[i], z[i])

    def prop(self, oes):
        for r in self.rays:
            r.prop(oes)
        return self

    def plot(self, linestyle='k-'):
        for r in self.rays:
            plot(r.histz, r.histx, linestyle)
        axis('equal')

class Ray:
    def __init__(self, x0, th0, z0):
        self.x = x0
        self.th = th0
        self.z = z0
        self.histx = [x0]
        self.histz = [z0]

    def prop(self, oes):
        if not isinstance(oes, Iterable):
            oes = [oes]

        for oe in oes:
            oe.transmit(self)
        return self

class OpticalElement:
    def transmit(self, r):
        temp = self.mat*mat([[r.x],[r.th]])
        r.x = temp[0].item()
        r.th = temp[1].item()
        r.z += self.dz
        r.histx.append(r.x)
        r.histz.append(r.z)
        return r

    def plot(self, z=0, linestyle='k-'):
        return

class Interface(OpticalElement):
    # the default curvature is flat (i.e. a plane interface)
    def __init__(self, n1=1, n2=1.4, r=float('inf'), dx=2.54e-2/2):
        self.n1 = n1
        self.n2 = n2
        self.r = r
        self.dz = 0
        self.dx = dx # the radius of the element (used for plotting, and throwing out bad rays)
        self.mat = mat([[1, 0],[(n1 - n2)/(n2*r), n1/n2]])

    def __repr__(self):
        if self.r != float('inf'):
            return 'Spherical Interface: n1=%g n2=%g r=%g' % (self.n1,self.n2,self.r)
        else:
            return 'Planar Interface: n1=%g n2=%g' % (self.n1,self.n2)

    def plot(self, z=0, linestyle='k-'):
        # need to implement this
        N = 100
        x = linspace(-self.dx, self.dx, N)
        dz = abs(self.r) - sqrt(self.r**2 - x**2)
        if self.r == float('inf'):
            z = z*ones(x.shape)
        elif self.r > 0: 
            z = z + dz
        else:
            z = z - dz
        plot(z, x, linestyle)

class Space(OpticalElement):
    def __init__(self, d, n=1):
        self.dz = d
        self.mat = mat([[1, d/n],[0, 1]])

    def __repr__(self):
        return 'Space: dz=%g' % self.dz

class ThinLens(OpticalElement):
    def __init__(self, f, dx=2.54e-2/2):
        self.f = f
        self.mat = mat([[1, 0],[-1/f, 1]])

    def __repr__(self):
        return 'Thin Lens: f=%g' % self.f

    def plot(self, z=0, linestyle='k-'):
        x = linspace(-self.dx, self.dx, N)
        z = z*ones(x.shape)
        plot(z, x, linestyle)

def plot_oes(oes, z=0, linestyle='k-'):
    for oe in oes:
        oe.plot(z=z, linestyle=linestyle)
        z = z + oe.dz


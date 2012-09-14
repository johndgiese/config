""" Solve the 1D diffusion equation with a 0 initial condition and a single
edge (at L) fixed at A. """

from pylab import *

L = 1
A = 1

kappa = 1
tau = 1/(kappa*pi**2/L**2)

Nx = 2**9
x = linspace(0, 1, Nx)

t_ = linspace(0.2, 2, 5)*tau
leg = []
for t in t_:
    v = zeros(x.shape)
    for n in xrange(1, 41):
        v += exp(-n**2*t/tau)*sin(n*pi*x/L)*(-1)**n/n
    v *= -2*A/pi

    plot(x, x - v, 'r-')
    leg.append(r't = {}$\tau$'.format(t/tau))

xlabel('position')
legend(leg, loc="top left")
show()

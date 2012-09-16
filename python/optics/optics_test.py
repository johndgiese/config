import optics as op
from pylab import *
reload(op)

def ff(x, f):
    return sin(x*f)

adj = {'x':linspace(1,2,10), 'f': (2,5)}
op.interact(ff, x=linspace(1,2,10), y=0, adjustable=adj)


#nu = linspace(op.c/750e-9, op.c/770e-9, 200)
#d = 100e-6
#r = 0.3

#T = op.fabry_perot_emp(nu, 4.8, 0.7, 1/2e-12)

#plot(op.c/nu/1e-9, T)
#xlabel('wavelength [nm]')
#show()

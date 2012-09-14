from pylab import *
import optics as op
import time
reload(op)

t0 = time.clock()
Z = 2**10
Nx = Ny = Z
dx0 = 10e-6
dy0 = 10e-6
nlim = (Z - 1)/2
n = linspace(-nlim, nlim, Z)
N, M = meshgrid(n, n)
U0 = zeros(N.shape, dtype='F')
U0[N**2 + M**2 < (Z/10)**2] = 1

U1, dx1, dy1 = op.fresnel_fourier(U0, z=2, dx0=dx0, dy0=dy0)

I0 = abs(U0)**2
I1 = abs(U1)**2
x0lim = (Nx - 1)*dx0/2
y0lim = (Ny - 1)*dy0/2
x1lim = (Nx - 1)*dx1/2
y1lim = (Ny - 1)*dy1/2
imshow(I0/amax(I0), extent=[-x0lim, x0lim, -y0lim, y0lim])
title('original')
figure()
imshow(I1/amax(I1), extent=[-x1lim, x1lim, -y1lim, y1lim])
title('propagated')
t1 = time.clock()

print('took %d ms' % ((t1 - t0)*1000))

show()

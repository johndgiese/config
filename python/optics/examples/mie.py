# Mie theory
# Use SI units
from math import sqrt, pi
from scipy.special import jv

# I like function form better
def real(a): return a.real
def conj(a): return a.conjugate()

diameter = 90e-6      # Diameter of sphere in nm
radius = diameter/2
wl = 700e-9           # Wavelength in nm
n_s = 1.57            # Refractive index of sphere
n_b = 1.33            # Refractive index of background
w_s = 1.05e3          # Specific weight of sphere
w_b = 1e3             # Specific weight of background
concentration = 0.002 # Concentration by weight

k = 2*pi*n_b/wl
x = k*radius
n_rel = n_s/n_b
y = n_rel*x

# Calculate the summations
err = 1e-8
Qs = 0
gQs = 0
for n in xrange(1,1000):
    Snx = sqrt(pi*x/2)*jv(n + 0.5, x)
    Sny = sqrt(pi*y/2)*jv(n + 0.5, y)
    Cnx = -sqrt(pi*x/2)*jv(n + 0.5, x)
    Zetax = Snx + 1j*Cnx

    # Calculate the first-order derivatives
    Snx_prime = - (n/x)*Snx + sqrt(pi*x/2)*jv(n - 0.5,x)
    Sny_prime = - (n/y)*Sny + sqrt(pi*y/2)*jv(n - 0.5,y)
    Cnx_prime = - (n/x)*Cnx - sqrt(pi*x/2)*jv(n - 0.5,x)
    Zetax_prime = Snx_prime + 1j*Cnx_prime

    an_num = Sny_prime*Snx - n_rel*Sny*Snx_prime
    an_den = Sny_prime*Zetax - n_rel*Sny*Zetax_prime
    an = an_num/an_den

    bn_num = n_rel*Sny_prime*Snx - Sny*Snx_prime
    bn_den = n_rel*Sny_prime*Zetax - Sny*Zetax_prime
    bn = bn_num/bn_den

    Qs1 = (2*n + 1)*(abs(an)**2 + abs(bn)**2)
    Qs += Qs1

    if n > 1:
        gQs1 = (n - 1)*(n + 1)/n*real(an_1*conj(an) + bn_1*conj(bn)) \
             + (2*n - 1)/((n - 1)*n)*real(an_1*conj(bn_1))
        gQs = gQs + gQs1

    an_1 = an
    bn_1 = bn

    if abs(Qs1) < (err*Qs) and abs(gQs1) < (err*gQs):
        break

Qs = (2/x**2)*Qs
gQs = (4/x**2)*gQs
g = gQs/Qs

vol_s = 4*pi/3*radius**3
N_s = concentration*w_b/(vol_s*w_s)
sigma_s = Qs*pi*radius**2
mu_s = N_s*sigma_s

mu_s_prime = mu_s*(1 - g)

# Output results
plot(x, 

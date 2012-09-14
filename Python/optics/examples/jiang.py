from pylab import * 
from optics import fabry_perot_emp, h, hbar, c, gaussian_spectra, gaussian_field
import optics as op
reload(op)

# Spectra of two pulses
nu_ = linspace(c/880e-9, c/900e-9, 400, endpoint=False)
pw = 190e-15     # pulse width [s]
W0 = 100e-3      # average power after the EOM
A=0.5
B=0.5
tdelay=2e-12
S = W0*gaussian_spectra(nu_, nu, pw)
Sdouble = S*(abs(A)**2 + abs(B)**2 + 2*real(A*conj(B)*exp(1j*2*pi*nu_*tdelay)))

# Intensity Transmission of a Fabry Perot
T_max = 0.65 # Trans max
T_min = 0.12 # Trans min
wl_ = c/nu_/1e-9 # wl array
dnu = abs(diff(nu_[:2]))
dwl = 2.8e-9
nu_F = 1/2e-12 # free spectral range
FP = fabry_perot_emp(nu_, T_min, T_max, nu_F)

# Calculate the power transmitted and reflected
Wt = sum(Sdouble*FP)*dnu/pw
Wr = sum(Sdouble*(1 - FP))*dnu/pw

## plot some stuff
plot(nu_, Sdouble/amax(Sdouble), 'r-', nu_, FP/amax(FP), 'k-')
xlabel('frequency [Hz]')
legend(['Spectral Intensity of Double Pulses', 'Intensity Transmission of FP'])
show()

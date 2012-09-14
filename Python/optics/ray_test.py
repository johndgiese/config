from optics.ray import *

### Test Snell's Law

#oes = [Space(5e-3), Interface(1, 1.4), Space(5e-3)]
#rb = RayBundle(0, 0, linspace(-.2, .2, 7))
#rb.prop(oes).plot()
#plot_oes(oes,linestyle='r-')
#show()

## 4-f System using two Thorlabs AC254-050 achromatic doublets

## Define the lens
r_1 = 33.34e-3
r_2 = -22.28e-3
r_3 = -291.07e-3
t_c1 = 9e-3
t_c2 = 2.5e-3
t_e  = 8.7e-3
n1 = 1.670
n2 = 1.728
dfl = [] # doublet with the flat side last
dfl.append(Interface(1, n1, r_1))
dfl.append(Space(t_c1, n1))
dfl.append(Interface(n1, n2, r_2))
dfl.append(Space(t_c2, n2))
dfl.append(Interface(n2, 1, r_3))

dff = [] # doublet with the flat side first
dff.append(Interface(1, n2, -r_3))
dff.append(Space(t_c2, n2))
dff.append(Interface(n2, n1, -r_2))
dff.append(Space(t_c1, n1))
dff.append(Interface(n1, 1, -r_1))
## Define the system
oes = []
f = 5e-2
oes.append(Space(f))
oes.extend(dff) # we want the flat end facing out
oes.append(Space(2*f))
oes.extend(dfl)
oes.append(Space(f))

rb1 = RayBundle(0, 0, linspace(-.1, .1, 7))
rb1.prop(oes).plot(linestyle='b-')
plot_oes(oes,linestyle='r-')

oes2 = []
oes2.append(Space(f))
oes2.extend(dfl) # we want the flat end facing out
oes2.append(Space(2*f))
oes2.extend(dff)
oes2.append(Space(f))
rb2 = RayBundle(0, 0, linspace(-.1, .1, 7))
rb2.prop(oes2).plot(linestyle='k-')
show()

## Find the principal planes
oes3 = [Space(5e-2)]
oes3.extend(dfl)
oes3.append(Space(6e-2))
def plot3(x=0, z=0, event=None):
    print(repr(event))
    if event:
        z = event.xdata
        x = event.ydata
        print('x=%g z=%g' %(x,z))
    rb3 = RayBundle(z, x, linspace(-.1, .1, 5))
    rb3.prop(oes3).plot(linestyle='k-')
    plot_oes(oes3,linestyle='r-')
    draw()
plot3()

connect('button_press_event', plot3)
show()

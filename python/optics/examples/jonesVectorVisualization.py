""" Create an animation to demonstrate linear vs. circular Jones vector basis. 

The user provides an initial jones vector, and it is plotted through a full
optical cycle, with a decomposition in both a circular and linear basis. """

from pylab import *
import matplotlib.animation as animation

E0 = array([1,1j])/sqrt(2) # initial jones vector
t = linspace(0, 2*pi, 100, endpoint=False)
x = E0[0]*exp(-1j*t)
y = E0[1]*exp(-1j*t)
lim = 1.1*sum(abs(E0*E0))

fig = figure()

ax_linear = fig.add_subplot(211)
ax_linear.set_xlim([-lim, lim])
ax_linear.set_ylim([-lim, lim])
line_E, = ax_linear.plot([], [], 'k-', lw   = 2)
line_Ex, = ax_linear.plot([], [], 'r-', lw   = 2)
line_Ey, = ax_linear.plot([], [], 'b-', lw   = 2)

ax_circular = fig.add_subplot(212)
ax_circular.set_xlim([-lim, lim])
ax_circular.set_ylim([-lim, lim])
line_F, = ax_circular.plot([], [], 'k-', lw = 2)
line_Fr, = ax_circular.plot([], [], 'r-', lw = 2)
line_Fl, = ax_circular.plot([], [], 'b-', lw = 2)

i = 0 # frame counter
def animate(i):
    xdata = array([0, x[i]])
    ydata = array([0, y[i]])
    line_E.set_data(xdata, ydata)
    line_Ex.set_data(array([0, x[i]]), array([0, 0]))
    line_Ey.set_data(array([0, 0]), array([0, y[i]]))
    line_F.set_data(xdata, ydata)
    i = i + 1
    return line_E, line_Ex, line_Ey, line_F

def init():
    line_E.set_data([],[])
    line_Ex.set_data([],[])
    line_Ey.set_data([],[])
    line_F.set_data([],[])
    return line_E, line_Ex, line_Ey, line_F


ani = animation.FuncAnimation(fig, run, arange(1, len(t)), blit=True, interval=10, repeat=True, init_func=init)
show()

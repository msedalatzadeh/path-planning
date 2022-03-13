from scipy import integrate
import numpy as np

from matplotlib import animation
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
from parameters import *
from numpy import matmul, diag, array, meshgrid, ones, zeros
import ffmpy
from FTCS_2D import *
from nodes import *
from numpy.random import rand

class boat:
    boat.x0 = 0
    boat.y0 = 0
    boat.psi0 = 0
    boat.u0 = 0
    boat.v0 = 0
    boat.r0 = 0
    
    def drive(self,Tu,Tr,Tf):
        def velocity_rate(u, v, r):
            Du = Tu + v*r
            Dv = -u*r   
            Dr = Tr 
            return [Du, Dv, Dr] 
        Time = np.linspace(0,Tf,100)
        
        sol = integrate.odeint(velocity_rate, [boat.u0, boat.v0, boat.r0], Time)
        boat.u = sol[:, 0]
        boat.v = sol[:, 1]
        boat.r = sol[:, 2]
        boat.x = integrate.trapezoid(boat.u, Time)
        boat.y = integrate.trapezoid(boat.v, Time)
        boat.psi = integrate.trapezoid(boat.r, Time)
    
    def animate(self):
    fig = plt.figure()
    y_min, y_max = [-10, 10]
    x_min, x_max = [-10, 10]
    ax = plt.axes(xlim=(x_min,x_max), ylim=(y_min,y_max))
    time=ax.annotate('$time=$0',xy=(2, 9))
    line, = ax.plot([], [], lw=2)

    plt.xlabel('$x$')
    plt.ylabel('$y$')

    plotcols = ["blue" , "red", "red"]
    plotlabels = ["Center" , "Front", "End"]
    plotlws = [3, 1, 1] 
    plotmarkers = ['o','*','*']
    lines = []
    
    for index in range(3):
        lobj = ax.plot([],[], 's', lw=plotlws[index], marker=plotmarkers[index], color=plotcols[index], label=plotlabels[index])[0]
        ax.legend()
        lines.append(lobj)


    def init():
        for line in lines:
            line.set_data([],[])
        return lines




    def animate(i,dt):
        xlist = [boat.x[4*i], boat.x[4*i]+0.1*np.cos(boat.psi[4*i]), boat.x[4*i]-np.cos(boat.psi[4*i])]
        ylist = [boat.y[4*i], boat.x[4*i]+0.1*np.sin(boat.psi[4*i]), boat.x[4*i]-np.sin(boat.psi[4*i])]
        s=4*i*dt
        time.set_text('$time=$%2.1f'%s)
        for lnum, line in enumerate(lines):
            line.set_data(xlist[lnum], ylist[lnum]) # set data for each line separately. 
        return lines

    path_mp4 = './mp4s/' + FileName + '.mp4'
    path_gif = './gifs/' + FileName + '.gif'

    anim = animation.FuncAnimation(fig,lambda i: animate(i,dt), init_func=init,frames=int(t_max/dt/4), interval=0.1, blit=False)
    anim.save(path_mp4, fps=30, extra_args=['-vcodec', 'libx264'])
    ff = ffmpy.FFmpeg(inputs = {path_mp4:None} , outputs = {path_gif: None})
    ff.run()
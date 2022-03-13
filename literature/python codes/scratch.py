## the following line load numeric and scientific packages
from scipy import integrate, misc
import numpy as np
from numpy import matmul, diag, array, meshgrid, ones, zeros
from numpy.random import rand

## these two lines are for installing simpy package for real time environment
import simpy

## the following lines are for importing visualization and animation packages
import scipy.ndimage as ndimage
from matplotlib import animation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.image as mpimg 
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import ffmpy


























class boat():    
    
    def __init__(self, initial_state={'x0':0, 'y0':0, 'psi0':0,'u0':0, 'v0':0, \
        'r0':0}, parameters={'boat length':1, 'time_increment':0.1}, real_time_environment=0):
        self.env = real_time_environment
        self.length = parameters['boat length'] 
        self.time_increment = parameters['time_increment']
        self.state = list(initial_state.values())
    
    def drive(self, controller, time):
        feedback_law = controller.law
        
        def Dstate_Dt(state, t, feedback_law):
            u, v, r, x, y, psi = state
            Tu, Tr, Tf = feedback_law(t)
            
            Du = Tu + v*r
            Dv = -u*r   
            Dr = Tr 
            Dx = u
            Dy = v
            Dpsi = r

            Dstate_Dt = [Du, Dv, Dr, Dx, Dy, Dpsi] 
            return Dstate_Dt
        
        if self.env:
            while self.env.now < time:
                timeframe = [self.env.now, self.env.now + self.time_increment]
                sol = integrate.odeint(Dstate_Dt, self.state[:-1], timeframe, args=(feedback_law,))
                self.env.timeout(self.env.now + self.time_increment)
                self.state.append([sol[1, 0], sol[1, 1], sol[1, 2], sol[1, 3], sol[1, 4], sol[1, 5], self.env.now])
        else:
            t = np.arange(0, time, self.time_increment)
            sol = integrate.odeint(Dstate_Dt, self.state, t, args=(feedback_law,))
            self.state = sol
            self.x = sol[:,0]
            self.y = sol[:,1]
            self.psi = sol[0,:2]
            self.u = sol[0,:3]
            self.v = sol[0,:4]
            self.r = sol[0,:5]

            
    
    def animate(self, FileName, Realtime=False):
        fig = plt.figure()
        #im = plt.imread('boat2.png')
        y_min, y_max = [-10, 10]
        x_min, x_max = [-10, 10]
        ax = plt.axes(xlim=(x_min,x_max), ylim=(y_min,y_max))
        time=ax.annotate('$time=$0',xy=(-9, 9))
        #line, = ax.plot([], [], lw=2)

        plt.xlabel('$x$')
        plt.ylabel('$y$')

        plotcols = ["blue" , "red", "red"]
        plotlabels = ["Center" , "Front", "End"]
        plotlws = [3, 1, 1] 
        plotmarkers = ['o','*','.']
        lines = []
        
        for index in range(3):
            lobj = ax.plot([],[], 's', lw=plotlws[index], marker=plotmarkers[index], color=plotcols[index], label=plotlabels[index])[0]
            #ax.legend()
            lines.append(lobj)

        def init():
            for line in lines:
                line.set_data([],[])
            return lines

        global ann
        ann = []
        def animated(i,dt):
            global ann
            if ann:
                ann.remove()
            #for artist in plt.gca().lines + plt.gca().collections:
            #    artist.remove()
            
            L = self.length

            def rotate_image(path, degree):
                img = plt.imread(path)
                img = ndimage.rotate(img, degree)
                return OffsetImage(img, zoom=0.2)
            
            ann = AnnotationBbox(rotate_image('boat2.png', self.psi[i]*180/np.pi), (self.x[i], self.y[i]), frameon=False)
            ax.add_artist(ann)
            #ax.axis('off')
            #ann_list.append(ann)
            
            #newax = fig.add_axes([0, 0, L/10, L/10], anchor='C')
            #img_boat_rotated = ndimage.rotate(im, self.psi[i]*180/np.pi)
            #img_boat_rotated_shifted = ndimage.shift(img_boat_rotated, [self.x[i], self.y[i], 0])
            #newax.imshow(img_boat_rotated_shifted)
            #newax.axis('off')
        
            #xlist = [self.x[i], self.x[i]+L*np.cos(self.psi[i]), self.x[i]-L*np.cos(self.psi[i])]
            #ylist = [self.y[i], self.y[i]+L*np.sin(self.psi[i]), self.y[i]-L*np.sin(self.psi[i])]
            s=i*dt
            time.set_text('$time=$%2.1f'%s)
            #for lnum, line in enumerate(lines):
            #    line.set_data(xlist[lnum], ylist[lnum]) # set data for each line separately. 
            #return lines

        path_mp4 = './mp4s/' + FileName + '.mp4'
        path_gif = './gifs/' + FileName + '.gif'

        dt = self.time[1]-self.time[0]
        t_max = self.time[-1]
        
        anim = animation.FuncAnimation(fig,lambda i: animated(i,dt), init_func=init,frames=int(t_max/dt), interval=0.1, blit=False)
        anim.save(path_mp4, fps=10, extra_args=['-vcodec', 'libx264'])
        ff = ffmpy.FFmpeg(inputs = {path_mp4:None} , outputs = {path_gif: None})
        ff.run()
        
        if Realtime:
            anim.show()









class controller():
    def __init__(self, feedback_law, real_time_environment=0):
        self.env = real_time_environment
        self.law = feedback_law
        
    def find_input(self, boat):
        feedback_law = self.law
        control_input = feedback_law(boat.sate)
        return control_input






def control_law(t):
    return (np.sin(t), np.sin(t), 0)

mycontroller = controller(control_law)

myboat = boat()

myboat.drive(mycontroller, 10)

print(myboat.state)
myboat.animate("animation24")
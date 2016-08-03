import numpy as np
import matplotlib.pyplot as plt

file= 'input.dat'
file= 'output.dat'
#file='potential.dat'

f = open(file, "rb")

nx=np.fromfile(f,count=1,dtype=np.int32)[0]
ny=np.fromfile(f,count=1,dtype=np.int32)[0]

print nx,ny

x=np.fromfile(f,count=nx,dtype=np.float32)
y=np.fromfile(f,count=ny,dtype=np.float32)
psi=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
mask=np.fromfile(f,count=nx*ny,dtype=np.int32).reshape((nx,ny))
u=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
v=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
u2=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
p=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
vort=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))

print u[0,nx/2]
print v[0,nx/2]
print u2[0,nx/2]


#plt.subplot(221)
#colour=u2
#plt.streamplot(x,y,u,v,density=1,color=colour,arrowstyle='fancy')
#plt.colorbar()
##plt.contour(x,y,psi,50, colors='black', linestyles='solid')
###plt.imshow(psi,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
###plt.colorbar()
#plt.axis('equal')
#plt.title("Flowlines")

#plt.subplot(222)
#plt.imshow(u2,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
#plt.colorbar()
#plt.axis('equal')
#plt.title("Velocity")

#plt.subplot(223)
#plt.imshow(vort,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))#,vmin=-10.,vmax=10.)
#plt.colorbar()
#plt.axis('equal')
#plt.title("Vorticity")

#plt.subplot(224)
#plt.imshow(p,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
#plt.colorbar()
#plt.axis('equal')
#plt.title("Pressure")




plt.subplot(121)
colour=u2
plt.streamplot(x,y,u,v,density=1,color=colour,arrowstyle='fancy')
plt.colorbar()
#plt.contour(x,y,psi,50, colors='black', linestyles='solid')
##plt.imshow(psi,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
##plt.colorbar()
plt.axis('equal')
plt.title("Flowlines")


plt.subplot(122)
plt.imshow(p,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
plt.colorbar()
plt.axis('equal')
plt.title("Pressure")





plt.show()

#plt.imshow(mask)
#plt.colorbar()
##plt.axis('equal')
#plt.show()

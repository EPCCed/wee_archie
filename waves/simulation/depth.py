import numpy as np
import matplotlib.pyplot as plt
import imageio
import scipy
import sys
import os

def place_block(x,y,mask):
    (nx,ny) = mask.shape
    print nx, ny
    mask[y-10:y+10,x-5:x+5]=0.


#read png image
im=imageio.imread("coast3.png")

nx = len(im)
ny=len(im[0])
print nx,ny

im2=np.asarray(im)

# get R channel
result=np.dsplit(im2,4)
r=result[0]
r=r.reshape((nx,ny),order="F")
print r.shape
r=r.astype(np.float64)
#normalise 0->1
r=r/255.

#sys.exit()

print r.shape
#print r[0]

#write this as a datafile
f=open("coast.img","wb")
f.write(np.asarray(nx,np.int32))
f.write(np.asarray(ny,np.int32))
f.write(r)
f.close()

#generate the base depth profile
os.system("./generate_depth")



#read in the mask
f=open("mask.dat","rb")
ftype=np.fromfile(f,np.byte,20)
ftype=str(ftype)
nxy=np.fromfile(f,np.int32,2)
t=np.fromfile(f,np.float64,1)
print(ftype)
print(nxy)
print(t)
mask=np.fromfile(f,np.float64,nx*ny)
f.close()

mask=mask.reshape((nx,ny))

#add blocks
f=open("blocks.txt","r")
n=int(f.readline())
for i in range(n):
    ln=f.readline()
    xy=ln.split()
    x=int(xy[0])
    y=int(xy[1])
    place_block(x,y,mask)


plt.imshow(mask)
plt.show()





#Write mask back to file
f=open("mask_blocks.dat","wb")
f.write("%-20s"%("mask_blocks"))
f.write(np.asarray(nx, np.int32))
f.write(np.asarray(ny, np.int32))
f.write(np.asarray(0., np.float64))
f.write(mask)
f.close()


os.system("./generate_ic")



f=open("depth.dat","rb")
ftype=np.fromfile(f,np.byte,20)
ftype=str(ftype)
nxy=np.fromfile(f,np.int32,2)
t=np.fromfile(f,np.float64,1)
print(ftype)
print(nxy)
print(t)
data=np.fromfile(f,np.float64,nx*ny)
f.close()

data=data.reshape((nx,ny))

plt.imshow(data)
plt.show()

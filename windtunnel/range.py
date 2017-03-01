from __future__ import print_function

import wx
import numpy as np
from numpy import sin, cos, pi
import matplotlib.pyplot as plt
import matplotlib.colors as cm


from config import *


lon_0=-80
lon_0=-10


class Range(wx.Frame):

    def __init__(self,parent,title,size,rangekm=None,c_lift=None,c_drag=None):
        super(Range, self).__init__(parent, title=title,size=size)

        self.parent=parent

        try:
            self.GetParent().RangeButton.Disable()
        except:
            pass

        if rangekm == None:
            rangekm=self.GetRange(c_lift,c_drag)

        globe=wx.Bitmap("map.png")
        background = wx.StaticBitmap(self,-1,globe)


        self.GetMask(rangekm)

        range=wx.Bitmap("range.png")
        mask=wx.StaticBitmap(self,-1,range)

        background.SetPosition((0,0))
        mask.SetPosition((0,0))

        self.Bind(wx.EVT_CLOSE,self.OnClose)



        print("Displaying range map!")


    def OnClose(self,e):
        print("Closing range window")
        try:
            self.GetParent().RangeButton.Enable(True)
        except:
            pass
        self.Destroy()


    def GetRange(self,c_lift,c_drag):



        if c_lift <=0.:
            cruise = 0.0
            print("Plane cannot fly (negative lift) - zero range")

            if self.parent != None:
                parent.logfile.write("    Cruise Speed = 0.0 km/h\n")
                parent.logfile.write("    Range = 0.0 km\n")
                self.parent.logfile.flush()
            return 0.
        else:
            cruise = np.sqrt( (2.*mass*1000*10) / (rho * c_lift * 2*wlgth) )


        if cruise > np.sqrt( (2.*thrust*1000) / (rho * c_drag * 2*wlgth) ):
            print("Plane cannot fly (can't fly fast enough) - zero range")
            if self.parent != None:
                self.parent.logfile.write("    Range =  0 km\n")
                self.parent.logfile.write("    Cruise Speed = 0 km/h\n")
                self.parent.logfile.flush()
            return 0.

        if self.parent != None:
            self.parent.logfile.write("    Cruise Speed = "+str(cruise*3.6)+" km/h\n")


        cruise_thrust = 0.5*rho*cruise*cruise * c_drag * 2*wlgth
        efficiency = cruise_thrust/1000/thrust



        t_flight = fuel / (efficiency*maxrate)

        print("Flight time  = ",t_flight/3600, " hours")
        print("Cruise Speed = ",cruise*3.6, " km/h")
        print("Range        =",t_flight*cruise/1000," km")
        print("Efficiency   =",1-efficiency)

        if self.parent != None:
            self.parent.logfile.write("    Range = "+str(t_flight*cruise/1000)+" km \n")
            self.parent.logfile.flush()



        return t_flight*cruise/1000






    def GetMask(self,rangekm):


        maxang = rangekm/re #angular distance around earth (in radians) the plane can do

        #location of Edinburgh (theta,phi - radians)
        phi0=lon0*pi/180.
        theta0=(90 - lat0)*pi/180.

        #Cartesian unit vector pointing from the centre of the earth to Edinburgh
        r0 = np.zeros(3)
        r0[0] = sin(theta0)*cos(phi0)
        r0[1] = sin(theta0)*sin(phi0)
        r0[2] = cos(theta0)


        #setup latitude and longitude grid
        res=1080
        nph=res
        nth=res/2

        lon=np.zeros(nph)
        lat=np.zeros(nth)
        theta=np.zeros(nth)

        dx=360./1080.

        for i in range(nph):
            lon[i]=(dx*(i+0.5))-180.-lon_0

        for j in range(nth):
            theta[j]=(dx*(j-0.5))
            lat[j]=90-theta[j]

        print(lon[0],lon[-1])
        print(lat[0],lat[-1])


        lon[:] = lon[:]*pi/180
        theta[:] = theta[:]*pi/180

        #set up 'map'
        img=np.zeros((nth,nph))


        r=np.zeros(3)

        img[:][:]=-1

        acos=np.arccos
        dot=np.dot

        for i in range(nph):
            for j in range(nth):
                r[0] = sin(theta[j])*cos(lon[i])
                r[1] = sin(theta[j])*sin(lon[i])
                r[2] = cos(theta[j])

                angle=acos(dot(r,r0))

                if angle <= maxang:
                    img[j][i]=angle/maxang


        colourmap = cm.ListedColormap(["lime","lime","lime","lime","lime","lime","lime","orange","orange","red"],"map")
        colourmap.set_under(color='white',alpha=0.)


        mydpi=96.
        fig=plt.figure(frameon=False,figsize=(1080/mydpi,540/mydpi),dpi=mydpi)
        fig.set_size_inches(1080/mydpi,540/mydpi)

        ax = plt.axes([0,0,1,1])

        plot=plt.imshow(img,extent=(0,2,0,1),alpha=0.3,vmin=0.0,vmax=1.0,cmap=colourmap)
        plt.axis("off")
        #plt.savefig("test.png", bbox_inches='tight')
        plot.axes.get_xaxis().set_visible(False)
        plot.axes.get_yaxis().set_visible(False)
        plt.savefig('range.png',transparent=True,dpi=mydpi)





if __name__ == "__main__":
    app=wx.App()
    range=Range(None,"Range",(1080,540),c_lift=1.0,c_drag=0.2)
    range.Show()
    app.MainLoop()

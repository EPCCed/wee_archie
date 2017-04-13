from __future__ import print_function
from takeoff import FlightIns

import wx
import numpy as np
from numpy import sin, cos, pi
import matplotlib.pyplot as plt
import matplotlib.colors as cm
import matplotlib.cm as clm
import math


from config import *


lon_0=-80
lon_0=-10

green=wx.Colour(0,180,0)
orange=wx.Colour(255,127,0)
bgcol=wx.Colour(53,53,53)

class Range(wx.Frame):

    def __init__(self,parent,title,size,rangekm=None,c_lift=None,c_drag=None):
        super(Range, self).__init__(parent, title=title,size=size,style=wx.FRAME_FLOAT_ON_PARENT|wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.parent=parent

        try:
            self.GetParent().RangeButton.Disable()
        except:
            pass

        if rangekm == None:
            rangekm=self.GetRange(c_lift,c_drag)

        self.globe=wx.Image("map_new.png",wx.BITMAP_TYPE_PNG)
        #background = wx.StaticBitmap(self,-1,wx.BitmapFromImage(self.globe))

        self.colours=["None","None","None","None","None","None","None","None","None","None"]
        


        self.GetMask(rangekm)
        #range=wx.Bitmap("range.png")
        #self.mask=wx.StaticBitmap(self,-1,range)

        #background.SetPosition((0,0))
        #self.mask.SetPosition((0,0))

        hours=math.floor(self.time)
        mins = (self.time - hours)*60.
        self.time_unit=self.time/500
        self.time_passed=0.

        # self.sb=self.CreateStatusBar()
        # self.sb.SetMinHeight(50)
        # self.sb.SetStatusText("Hello world")

        self.text="Speed = %d kmph\nFlight Time =  %d Hours %d Minutes \nRange = %d km" % (self.speed,hours,mins,self.range)

        self.clock=wx.StaticText(self,wx.ID_ANY,pos=(75,425))
        self.clock.SetForegroundColour(wx.WHITE)
        
        self.tx=wx.StaticText(self,wx.ID_ANY,pos=(600,425))

        colour=wx.Colour(128,0,128)
        bgc=wx.Colour(255,255,255)

        #tx.SetForegroundColour(colour)
        #tx.SetBackgroundColour(bgc)

        print(self.text)

        self.Bind(wx.EVT_CLOSE,self.OnClose)
        self.Bind(wx.EVT_ERASE_BACKGROUND,self.on_erase)
        self.Bind(wx.EVT_PAINT,self.on_paint)

        self.mask_set=False
        self.buffer=wx.EmptyBitmap(840,270)
        self.backbuffer=wx.EmptyBitmap(840,270)

        self.fuel=FlightIns(((115,315)),((1,1)),60)

        #range only expands & fuel only decreases if some range is displayed
        if(self.able):
            self.timer=wx.Timer(self)
            self.Bind(wx.EVT_TIMER,self.TimerCallback,self.timer)
            self.counter=125
            self.timer.Start(10)
        else:
            self.update(125)


        print("Displaying range map!")


    def TimerCallback(self,e):
        
        #painting fuel dial
        
        self.update(self.counter)
        self.counter-=0.5

        #updating colourmap, painting range
        if self.counter==124.5:
            self.colours[0]="lime"
            self.Paint()   
        elif self.counter==100:
            self.colours[1]="lime"
            self.Paint()  
        elif self.counter==75:
            self.colours[2]="lime"
            self.Paint()
        elif self.counter==50:
            self.colours[3]="lime"
            self.Paint()
        elif self.counter==25:
            self.colours[4]="lime"
            self.Paint()
        elif self.counter==0:
            self.colours[5]="lime"
            self.Paint()
        elif self.counter==-25:
            self.colours[6]="lime"
            self.Paint()
        elif self.counter==-50:
            self.colours[7]="orange"
            self.Paint()
        elif self.counter==-75:
            self.colours[8]="orange"
            self.Paint()
        elif self.counter==-100:
            self.colours[9]="red"
            self.Paint()

        if self.counter==-125:
            self.timer.Stop()

    def on_erase(self,e):
        pass    


    def OnClose(self,e):
        print("Closing range window")
        try:
            self.GetParent().RangeButton.Enable(True)
        except:
            pass
        if(self.able):
            self.timer.Stop()
        self.Destroy()

    def update(self,val):

        self.buffer=wx.BitmapFromImage(self.globe)
        self.backbuffer=wx.BitmapFromImage(self.globe)
        
        dc=wx.MemoryDC()
        dc.SelectObject(self.backbuffer)
        self.fuel.CalcArrow(val)
        self.fuel.DrawArrow(dc,wx.RED)

        self.write(self.tx,self.text,15)      
        self.time_passed+=self.time_unit
        hours=int(math.floor(self.time_passed))
        mins=int((self.time_passed-hours)*60)
        if mins<10:
            mins="0%d"%mins
        if hours<10:
            hours="0%d"%hours
        self.write(self.clock,"%s:%s"%(hours,mins),20)

        self.buffer,self.backbuffer=self.backbuffer,self.buffer
        dc.SelectObject(wx.NullBitmap)

        self.Refresh()

    def write(self,text,label,size):
        font=wx.Font(size,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        text.SetLabel(label)
        text.SetFont(font)

    def on_paint(self,e):
        dc=wx.BufferedPaintDC(self,self.buffer)

    def GetRange(self,c_lift,c_drag):

        if c_lift <=0.:
            cruise = 0.0
            print("Plane cannot fly (negative lift) - zero range")
            self.speed=0.
            self.range=0.
            self.time=0.
            self.able=False

            if self.parent != None:
                self.parent.logfile.write("    Cruise Speed = 0.0 km/h\n")
                self.parent.logfile.write("    Range = 0.0 km\n")
                self.parent.logfile.flush()
            return 0.
        else:
            cruise = np.sqrt( (2.*mass*1000*10) / (rho * c_lift * 2*wlgth) )


        if cruise > np.sqrt( (2.*thrust*1000) / (rho * c_drag * 2*wlgth) ):
            print("Plane cannot fly (can't fly fast enough) - zero range")
            self.speed=0.
            self.range=0.
            self.time=0.
            self.able=False
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

        self.speed=cruise*3.6
        self.range=t_flight*cruise/1000
        self.time=t_flight/3600
        self.able=True

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
        self.img=np.zeros((nth,nph))


        r=np.zeros(3)

        self.img[:][:]=-1

        acos=np.arccos
        dot=np.dot

        for i in range(nph):
            for j in range(nth):
                r[0] = sin(theta[j])*cos(lon[i])
                r[1] = sin(theta[j])*sin(lon[i])
                r[2] = cos(theta[j])

                angle=acos(dot(r,r0))

                if angle <= maxang:
                    
                    self.img[j][i]=angle/maxang


        #colours range with given colourmap (timer)
    def Paint(self):
        mydpi=96.
        fig=plt.figure(frameon=False,figsize=(1080/mydpi,540/mydpi),dpi=mydpi)
        fig.set_size_inches(1080/mydpi,540/mydpi)
        
        self.map=cm.ListedColormap(self.colours,"rangemap")
        self.map.set_under(color='white',alpha=0.)

        ax = plt.axes([0,0,1,1])

        plot=plt.imshow(self.img,extent=(0,2,0,1),alpha=0.3,vmin=0.0,vmax=1.0,cmap=self.map)
        plt.axis("off")
        #plt.savefig("test.png", bbox_inches='tight')
        plot.axes.get_xaxis().set_visible(False)
        plot.axes.get_yaxis().set_visible(False)
        plt.savefig('range.png',transparent=True,dpi=mydpi)

        if(self.mask_set):
            self.mask.Destroy()
        range=wx.Bitmap("range.png")
        self.mask=wx.StaticBitmap(self,-1,range)
        self.mask.SetPosition((0,0))
        self.mask_set=True


if __name__ == "__main__":
    app=wx.App()
    range=Range(None,"Range",(1080,540),c_lift=1.0,c_drag=0.2)
    range.Show()
    app.MainLoop()

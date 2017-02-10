from __future__ import print_function

import wx
import numpy as np
from config import *

def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result


# lmax = 2000. #runway length (m)
# wlgth = 15 #wing length (m)
# mass = 50 #tonnes
# wgt=mass*10*1000. #weight in N
# thrust = 170 #kN
#
# rho = 1.225 #air density (kg/m^3)
#
#
# fuel = 250. #units of fuel
# maxrate = 0.1 #amount of fuel used per second at maxthrust
#
# c_lift = 0.5
# c_drag = 1.5
#
# atop = 2.0 #top length of wing (m)
# aside = 0.2 #side length of wing (m)
#
# dt = 0.05 #timestep (s)
#
# scale = 0.38 #scale metres to pixels

x = 0.0 #initial position of plane
v = 0.0 #initial velocity of plane
y = 0.0 #initial height
t = 0.0


lift=0.0
drag=0.0






class Takeoff(wx.Frame):
    def __init__(self, parent,title,size,c_lift,c_drag):
        super(Takeoff, self).__init__(parent, title=title,size=size)
        path="background.png"
        background = wx.Bitmap(path)
        #background = scale_bitmap(background, 1200, 670)
        bg = wx.StaticBitmap(self, -1, background)
        bg.SetPosition((0, 0))

        self.c_lift=c_lift
        self.c_drag=c_drag

        #initial position of plane
        self.x = 1050.
        self.y = 300.

        #plane properties
        self.vx= 0.
        self.vy= 0.
        self.t = 0.

        spl = wx.Bitmap("splash.png")
        spl = scale_bitmap(spl,159,67)
        self.splash=wx.StaticBitmap(self,-1,spl)
        self.splash.SetPosition((10,-500))


        plane = wx.Bitmap("plane.png")
        self.control = wx.StaticBitmap(self, -1, plane)
        self.control.SetPosition((self.x, self.y))


        self.waterlevel=580

        h20 = wx.Bitmap("water.png")
        self.water = wx.StaticBitmap(self, -1, h20)
        self.water.SetPosition((-25,self.waterlevel))

        self.counter=0

        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.TimerCallback,self.timer)

        self.crash=False
        self.takeoff=False
        self.touchdown=False

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.x0 = self.x

        # self.maxv = np.sqrt( (2.*thrust*1000) / (rho * c_drag * 2*aside*wlgth) ) #maximum speed where drag balances thrust
        # self.takeoff = np.sqrt( (2.*mass*1000*10) / (rho * c_lift * 2*atop*wlgth) ) #cruise speed/takeoff speed (lift = weight)

        try:
            self.GetParent().TakeoffButton.Disable()
        except:
            pass




        self.timer.Start(10)

    def OnClose(self,e):
        print("Exiting Take Off")
        try:
            self.GetParent().TakeoffButton.Enable(True)
        except:
            pass
        self.timer.Stop()
        self.Destroy()


    def TimerCallback(self,e):
        #self.x-= 0.1

        self.Integrate()

        self.control.SetPosition((self.x,self.y))
        if self.x < -200:
            print("Plane left for its travels")
            self.timer.Stop()



    def Integrate(self):

        if (not self.crash):

            thrust2=thrust
            lift = self.c_lift*wlgth*2 * 0.5*rho*self.vx*self.vx
            drag = self.c_drag*wlgth*2 * 0.5*rho*self.vx*self.vx

            self.vx = self.vx + (thrust2*1000-drag)*dt/(mass*1000)
            self.x = self.x - self.vx*dt*scale
            self.t = self.t+dt

            if (lift > wgt):
                self.y= self.y - 10.*dt
                if not self.takeoff:
                    print("Takeoff :)")
                    self.takeoff=True

            if ((self.x0-self.x)/scale > lmax) and not self.takeoff:
                print("takeoff failed at",self.x)
                self.crash=True

        elif not self.touchdown:

            self.vy = self.vy + 10*dt
            self.y = self.y + self.vy*dt
            self.x = self.x - self.vx*dt*scale

            if self.y > 500:
                self.y=500
                self.touchdown=True
                print("splashdown")
                self.splash.SetPosition((self.x-10,510))

        else:
            self.counter +=1

            #if self.counter>90:
               # self.splash.SetPosition((-500,-500))

            if self.counter>100:
                self.vy=0.5
                self.y = self.y+ self.vy*dt

                self.waterlevel=self.waterlevel-3.*self.vy*dt
                self.water.SetPosition((-25,self.waterlevel))

                if self.waterlevel < 510:
                    self.timer.Stop()
                    print("Plane sunk")





if __name__ == '__main__':
    app = wx.App()
    takeoff=Takeoff(None,"Take Off",(1200,675),c_lift=0.5,c_drag=0.1)
    takeoff.Show()
    app.MainLoop()

from __future__ import print_function

import wx
import numpy as np
from config import *
import random

def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result



scale = 0.35 #scale metres to pixels



lift=0.0
drag=0.0





class Takeoff(wx.Frame):
    def __init__(self, parent,title,size,c_lift,c_drag):
        super(Takeoff, self).__init__(parent, title=title,size=size)

        self.parent=parent

        #get lift and drag coefficients from input
        self.c_lift=c_lift
        self.c_drag=c_drag


        #initial position of plane
        self.x = 1000.
        self.y = 345.

        #plane properties
        self.vx= 0.
        self.vy= 0.
        self.t = 0.

        #load background image
        bg = wx.Image("background2.png",wx.BITMAP_TYPE_PNG)
        bg.Rescale(1200, 670)
        background = wx.StaticBitmap(self, -1, wx.BitmapFromImage(bg))
        background.SetPosition((0, 0))


        ##add placename text
        #text=wx.StaticText(self,label=placename,pos=(595,150),style=wx.ALIGN_CENTRE_HORIZONTAL)
        #font = wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL)
        #text.SetFont(font)

        #load splash image
        spl = wx.Image("splash.png",wx.BITMAP_TYPE_PNG)
        spl.Rescale(159,67)
        self.splash=wx.StaticBitmap(self,-1,wx.BitmapFromImage(spl))
        self.splash.SetPosition((10,-500))

        #load plane image
        self.planeimg = wx.Image("plane2.png",wx.BITMAP_TYPE_PNG)
        self.planeimg.Rescale(158,50)
        self.plane = wx.StaticBitmap(self, -1, wx.BitmapFromImage(self.planeimg))
        self.plane.SetPosition((self.x, self.y))



        #load image of water (used to cover sinking plane)
        self.waterlevel=580

        h20 = wx.Image("water2.png",wx.BITMAP_TYPE_PNG)
        self.water = wx.StaticBitmap(self, -1, wx.BitmapFromImage(h20))
        self.water.SetPosition((-25,self.waterlevel))
        self.water.SetPosition((-25,-1000))



        #load image of raft
        raft=wx.Image("raft.png", wx.BITMAP_TYPE_PNG)
        raft.Rescale(30,13)

        #Create a list of the 4 rafts
        self.rafts=[]
        for i in range(4):
            img=wx.StaticBitmap(self,-1,wx.BitmapFromImage(raft))
            #calculate angle of raft from x axis (45, -45, 135, -135 degrees)
            angle=i*np.pi/2. + np.pi/4.
            #get a position vector for the raft
            pos=((2.*np.cos(angle)*25,np.sin(angle)*25))
            #get the direction it will drift in
            dr=((2.*np.cos(angle),np.sin(angle)))
            #append LifeRaft object to list
            self.rafts.append( LifeRaft(img,pos,dr) )

        #hide the rafts (move them offscreen)
        for raft in self.rafts:
            raft.Hide()



        self.counter=0

        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.TimerCallback,self.timer)

        self.crash=False
        self.takeoff=False
        self.touchdown=False

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.x0 = self.x

        #disable the takeoff button from the main window
        try:
            self.GetParent().TakeoffButton.Disable()
        except:
            pass

        #start the timer
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

        #integrate movement of plane (and any other objects (i.e. liferafts))
        self.Integrate()

        self.plane.SetPosition((self.x,self.y))
        if self.x < -200:
            print("Plane left for its travels")
            self.timer.Stop()



    def Integrate(self):
        #if the plane hasn't crashed
        if (not self.crash):

            thrust2=thrust
            lift = self.c_lift*wlgth*2 * 0.5*rho*self.vx*self.vx
            drag = self.c_drag*wlgth*2 * 0.5*rho*self.vx*self.vx

            self.vx = self.vx + (thrust2*1000-drag)*dt/(mass*1000)
            self.x = self.x - self.vx*dt*scale
            self.t = self.t+dt

            #if the plane can take off/has taken off
            if (lift > wgt):
                self.y= self.y - 10.*dt
                if not self.takeoff:
                    print("Takeoff :)")
                    self.planeimg=self.planeimg.Rotate(-np.pi/12,wx.Point(0.,0.))
                    self.y -= 10.
                    self.plane.SetBitmap(wx.BitmapFromImage(self.planeimg))
                    self.takeoff=True
                    if self.parent != None:
                        self.parent.logfile.write("    Takeoff = True\n")
                        self.parent.logfile.write("    Runway Dist= "+str((self.x0-self.x)/scale)+" m \n")
                        self.parent.logfile.flush()

            #if the plane overruns the runway
            if ((self.x0-self.x)/scale > lmax) and not self.takeoff:
                print("takeoff failed at",(self.x0-self.x)/scale)
                self.crash=True

                if self.parent != None:
                    self.parent.logfile.write("    Takeoff = False\n")
                    self.parent.logfile.flush()

        #if the plane is falling but hasn't hit the water yet
        elif not self.touchdown:

            self.vy = self.vy + 10*dt
            self.y = self.y + self.vy*dt
            self.x = self.x - self.vx*dt*scale

            if self.y > 500:
                self.y=500
                self.touchdown=True
                print("splashdown")
                self.splash.SetPosition((self.x-10,510))
                for raft in self.rafts:
                    xp=self.x+50.
                    yp=self.y+30.
                    raft.SetPos((xp,yp))


        #once/if the plane has hit the sea
        else:
            self.counter +=1

            #if 50 time units have passed, start moving the rafts
            if self.counter>50:
                for raft in self.rafts:
                    raft.Move()

            #after 100 time units, start plane sinking
            if self.counter>100:
                self.vy=0.5
                self.y = self.y+ self.vy*dt

                self.waterlevel=self.waterlevel-3.*self.vy*dt
                self.water.SetPosition((-25,self.waterlevel))

                if self.waterlevel < 510:
                    self.timer.Stop()
                    print("Plane sunk")



#liferaft class
class LifeRaft:
    def __init__(self,image,pos,dr):
        self.image=image
        self.pos=pos
        self.dr=dr

    #Updates the position of the raft on the screen
    def UpdatePosition(self):
        self.image.SetPosition(self.pos)

    #set the position of the raft (relative to its current position)
    def SetPos(self,pos):
        xp,yp=pos
        x,y=self.pos

        x+=xp
        y+=yp
        self.pos=(x,y)
        #self.UpdatePosition

    #move the raft offscreen
    def Hide(self):
        self.image.SetPosition((-100,-100))

    #set the displacement vector of the raft
    def SetDr(self,dr):
        self.dr=dr

    #move the raft (in the direction of dr, but with a random component added in to make it 'rock' about)
    def Move(self):
        x,y=self.pos
        dx,dy=self.dr

        x+=(dx+random.gauss(0.,5.))*0.01
        y+=(dy+random.gauss(0.,5.))*0.01

        self.pos=(x,y)

        self.UpdatePosition()




if __name__ == '__main__':
    app = wx.App()
    takeoff=Takeoff(None,"Take Off",(1200,675),c_lift=2*1.0,c_drag=0.1)
    takeoff.Show()
    app.MainLoop()

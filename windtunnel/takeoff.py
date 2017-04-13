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


bgc1=wx.Colour(53,53,53)
bgc2=wx.Colour(35,35,35)

class Takeoff(wx.Frame):
    def __init__(self, parent,title,size,c_lift,c_drag):
        super(Takeoff, self).__init__(parent, title=title,size=size,style=wx.FRAME_FLOAT_ON_PARENT|wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.parent=parent

        parent_pos=self.GetPositionTuple()

        self.db=Dashboard(self,"Dashboard",(parent_pos[0]+600,parent_pos[1]+900),((840,270)))
        self.db.Show()

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
        self.i=0
        self.vsp=0
        self.altitude=0

        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.TimerCallback,self.timer)

        self.crash=False
        self.takeoff=False
        self.touchdown=False

        self.Bind(wx.EVT_CLOSE,self.OnClose)

        self.x0 = self.x

        #calculate critical speed: self.c_lift can be negative, in that case use default value 2.0
        if self.c_lift>0:           
            self.crit=np.sqrt(wgt/(self.c_lift*wlgth*2 * 0.5*rho))
        else:
            self.crit=np.sqrt(wgt/(2*wlgth*2*0.5*rho))

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
        #if self.x < -200:
            #print("Plane left for its travels")
            #self.timer.Stop()
        if (self.altitude >995) or (self.vx>355):
            print("Plane left for its travels")
            self.timer.Stop()


    def Integrate(self):
        #if the plane hasn't crashed


        if (not self.crash):

            self.db.update((self.db.crit,self.db.speed,self.db.al_hun,self.db.al_ten,self.db.vm),(self.crit,self.vx,0,0,-125),(wx.RED,wx.GREEN,'GREY','LIGHT GREY',wx.CYAN))

            #calculating
            thrust2=thrust
            lift = self.c_lift*wlgth*2 * 0.5*rho*self.vx*self.vx
            drag = self.c_drag*wlgth*2 * 0.5*rho*self.vx*self.vx

            self.vx = self.vx + (thrust2*1000-drag)*dt/(mass*1000)
            self.x = self.x - self.vx*dt*scale
            self.t = self.t+dt    
        

            #if the plane can take off/has taken off
            if (lift > wgt):
                self.y= self.y - 10.*dt

                vso=self.altitude
                self.altitude+=10.*dt/0.35
                vs=self.altitude-vso
                vs*=100 #convert into m/s
                if self.vsp<=(vs-10):
                    self.vsp+=10
                else:
                    self.vsp=vs
                ten=self.altitude%100
                hun=self.altitude-ten

                #-125 because of the rotated circle, could also put +500, does not change the sin/cos value
                self.db.update((self.db.al_ten,self.db.al_hun,self.db.crit,self.db.speed,self.db.vm),(ten,hun,self.crit,self.vx,(self.vsp-125)),('LIGHT GREY','GREY',wx.RED,wx.GREEN,wx.CYAN))
        
                #attitude indicator (not so true, should be at ~47 degrees)
                self.i+=1
                if self.i<13:
                    self.db.attbg.SetPosition((360,13+self.i))
                    self.db.attr.SetPosition((350,5))    
        

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

            #variometer
            vso=self.altitude
            self.altitude-=10.*dt/0.35
            vs=self.altitude-vso
            vs*=100 #convert into m/s
            if self.vsp>=(vs+5):
                self.vsp-=5
            else:
                self.vsp=vs 

            self.db.update((self.db.al_hun,self.db.al_ten,self.db.crit,self.db.speed,self.db.vm),(0,0,self.crit,self.vx,(self.vsp-125)),('GREY','LIGHT GREY',wx.RED,wx.GREEN,wx.CYAN))

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

            #dashboard starts blinking red
            self.db.dashBl.SetPosition((0,0))
            self.db.dashBr.SetPosition((640,0))
        
            if self.waterlevel < 500:
                self.db.dashRl.SetPosition((-210,-270))
                self.db.dashRr.SetPosition((-210,-270))
            elif ((self.counter%50) in range(25)):
                self.db.dashRl.SetPosition((1,0))
                self.db.dashRr.SetPosition((631,0))
            else:
                self.db.dashRl.SetPosition((-210,-270))
                self.db.dashRr.SetPosition((-210,-270))

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

#flight instruments class
class FlightIns:
    def __init__(self,ctr,scale,lng):
        self.ctr=ctr
        self.scale=scale
        self.end=list(ctr)
        self.lng=lng
        self.CalcArrow(0)

    def CalcArrow(self,value):
        val=value*self.scale[0]/self.scale[1]
        val=np.radians(val)
        self.end[0]=self.ctr[0]+np.sin(val)*self.lng
        self.end[1]=self.ctr[1]-np.cos(val)*self.lng

    def DrawArrow(self,area,colour):
        ar=area
        ar.SetPen(wx.Pen(colour,width=2,style=wx.SOLID))
        ar.DrawLine(self.ctr[0],self.ctr[1],self.end[0],self.end[1])

    


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

class Dashboard(wx.Frame):  
    def __init__(self, parent,title,pos,size):
        super(Dashboard, self).__init__(parent, title=title,pos=pos,size=size,style=wx.FRAME_FLOAT_ON_PARENT | wx.CAPTION | wx.CLIP_CHILDREN)

        #load cockpit images

        self.dashboard=wx.Image("dashboard_whole.png",wx.BITMAP_TYPE_PNG)

        dashboard1l=wx.Image("dashboard_black_l.png",wx.BITMAP_TYPE_PNG)
        self.dashBl=wx.StaticBitmap(self,-1,wx.BitmapFromImage(dashboard1l))
        self.dashBl.SetPosition((-210,-270))

        dashboard1r=wx.Image("dashboard_black_r.png",wx.BITMAP_TYPE_PNG)
        self.dashBr=wx.StaticBitmap(self,-1,wx.BitmapFromImage(dashboard1r))
        self.dashBr.SetPosition((-210,-270))

        dashboard2l=wx.Image("dashboard_red_l.png",wx.BITMAP_TYPE_PNG)
        self.dashRl=wx.StaticBitmap(self,-1,wx.BitmapFromImage(dashboard2l))
        self.dashRl.SetPosition((-210,-270))

        dashboard2r=wx.Image("dashboard_red_r.png",wx.BITMAP_TYPE_PNG)
        self.dashRr=wx.StaticBitmap(self,-1,wx.BitmapFromImage(dashboard2r))
        self.dashRr.SetPosition((-210,-270))

        attitude=wx.Image("attit_bg.png",wx.BITMAP_TYPE_PNG)
        attitude.Rescale(98,98)
        self.attbg=wx.StaticBitmap(self, -1, wx.BitmapFromImage(attitude))
        self.attbg.SetPosition((-98,-98))

        attitude2=wx.Image("attit_ring.png",wx.BITMAP_TYPE_PNG)
        attitude2.Rescale(120,120)
        self.attr=wx.StaticBitmap(self, -1, wx.BitmapFromImage(attitude2))
        self.attr.SetPosition((-120,-120))

        self.speed=FlightIns((260,65),(1,1),33)
        self.crit=FlightIns((260,65),(1,1),60)
        self.al_ten=FlightIns((563,65),(90,25),30)
        self.al_hun=FlightIns((563,65),(90,250),40)
        self.vm=FlightIns((560,195),(90,125),30)
        self.vm.end=list((530,195))

        self.Bind(wx.EVT_CLOSE,self.on_close)
        self.Bind(wx.EVT_ERASE_BACKGROUND,self.on_erase)
        self.Bind(wx.EVT_PAINT,self.on_paint)

        self.buffer=wx.EmptyBitmap(840,270)
        self.backbuffer=wx.EmptyBitmap(840,270)

    def on_close(self,e):
        pass

    def on_erase(self,e):
        pass        

    def update(self,instruments,val,colours):

        self.buffer=wx.BitmapFromImage(self.dashboard)
        self.backbuffer=wx.BitmapFromImage(self.dashboard)
        
        dc=wx.MemoryDC()
        dc.SelectObject(self.backbuffer)
        try:
            for ins, v, c in zip(instruments, val, colours):
                ins.CalcArrow(v)
                ins.DrawArrow(dc,c)
        except TypeError:
            instruments.CalcArrow(val)
            instruments.DrawArrow(dc,colours)
        self.buffer,self.backbuffer=self.backbuffer,self.buffer
        dc.SelectObject(wx.NullBitmap)

        self.Refresh()


    def on_paint(self,e):
        dc=wx.BufferedPaintDC(self,self.buffer)


if __name__ == '__main__':
    app = wx.App()
    takeoff=Takeoff(None,"Take Off",(1200,675),c_lift=2*1.0,c_drag=0.1)
    takeoff.Show()
    app.MainLoop()

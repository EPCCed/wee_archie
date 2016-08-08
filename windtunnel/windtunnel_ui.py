from __future__ import print_function
import client
import numpy as np
import wx
import subprocess



#select the UI abstract superclass to derive from
UI=client.AbstractmatplotlibUI

# Derive the demo-specific GUI class from the Abstract??UI class
class WindTunnelWindow(UI):

    def __init__(self,parent,title,demo,servercomm):

        #call superclass' __init__
        UI.__init__(self,parent,title,demo,servercomm)

        #INSERT CODE HERE TO SET LAYOUT OF WINDOW/ADD BUTTONS ETC


        #set up sizers that allow you to position window elements easily

        #main sizer - arrange items horizontally on screen (controls on left, vtk interactor on right)
        self.mainsizer=wx.BoxSizer(wx.HORIZONTAL)
        #sizer for buttons (align buttons vertically)
        self.buttonsizer=wx.BoxSizer(wx.VERTICAL)
        #sizer for rewind, step forward, step back and fast forward buttons






        #button to start simulation (at the moment it just switches between screens)
        self.simbutton=wx.Button(self,wx.ID_ANY,"Start a Simulation")
        self.Bind(wx.EVT_BUTTON,self.SwapScreens,self.simbutton)




        #controls for viewing results
        self.loadradio=wx.RadioBox(self,wx.ID_ANY,label="Result Type",choices=["Potential","Viscous"],majorDimension=2,style=wx.RA_SPECIFY_COLS)

        self.radiobox=wx.RadioBox(self,wx.ID_ANY,label="Variable",choices=["Flow","Pressure", "Vorticity","Velocity"],majorDimension=2,style=wx.RA_SPECIFY_COLS)

        self.button=wx.Button(self,wx.ID_ANY,label="Go")

        self.Bind(wx.EVT_BUTTON,self.UpdateResults,self.button)
        self.Bind(wx.EVT_RADIOBOX,self.UpdateResults,self.radiobox)
        self.Bind(wx.EVT_RADIOBOX,self.UpdateResults,self.loadradio)

        self.logger = wx.TextCtrl(self, style=wx.TE_READONLY)

        self.logger.SetValue("")


        #controls for setting up simulation

        self.shaperadio=wx.RadioBox(self,wx.ID_ANY,label="Shape",choices=["Ellipse", "Aerofoil"])
        self.Bind(wx.EVT_RADIOBOX,self.SwapShape,self.shaperadio)

        self.angleslider=wx.Slider(self,wx.ID_ANY,value=0,minValue=-45,maxValue=45)

        self.aslider=wx.Slider(self,wx.ID_ANY,value=10,minValue=2,maxValue=10)
        self.bslider=wx.Slider(self,wx.ID_ANY,value=10,minValue=2,maxValue=10)

        self.mslider=wx.Slider(self,wx.ID_ANY,value=0,minValue=-30,maxValue=30)
        self.tslider=wx.Slider(self,wx.ID_ANY,value=2,minValue=1,maxValue=6)

        self.angletext=wx.StaticText(self,label="Angle of attack = 0 degrees")
        self.atext=wx.StaticText(self,label="Red Axis = 1")
        self.btext=wx.StaticText(self,label="Green Axis = 1")

        #self.Bind(wx.EVT_RADIOBOX,self.GetShape,self.shaperadio)
        self.Bind(wx.EVT_SLIDER,self.GetShape,self.aslider)
        self.Bind(wx.EVT_SLIDER,self.GetShape,self.bslider)
        self.Bind(wx.EVT_SLIDER,self.GetShape,self.mslider)
        self.Bind(wx.EVT_SLIDER,self.GetShape,self.tslider)
        self.Bind(wx.EVT_SLIDER,self.RotateShape,self.angleslider)





        #self.ShowResultsControls()
        self.ShowSetupControls()

        self.resultsscreen=False


        self.mainsizer.Add(self.buttonsizer)
        self.mainsizer.Add(self.canvas)





        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        # self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.SetSizer(self.mainsizer)
        self.Fit()

        #self.plot()



        #show window
        self.Show()







    def StartInteractor(self):
        UI.StartInteractor(self)
        #INSERT ANY CUSTOM CODE HERE




    def StartSim(self,config):
        UI.StartSim(self,config)
        #INSERT ANY CUSTOM CODE HERE




    def StopSim(self):
        UI.StopSim(self)
        #INSERT ANY CUSTOM CODE HERE




    def TimerCallback(self,e):
        UI.TimerCallback(self,e)
        #INSERT ANY CUSTOM CODE HERE




    def OnClose(self,e):
        UI.OnClose(self,e)
        #INSERT ANY CUSTOM CODE HERE



    #----------------------------------------------------------------------
    #------------- New methods specific to demo go here -------------------
    #----------------------------------------------------------------------

    def UpdateResults(self,e):

        simtype=self.loadradio.GetSelection()

        vartype=self.radiobox.GetSelection()

        self.demo.RenderFrame(self,self.dto,simtype,vartype)

        self.canvas.draw()
        self.canvas.Refresh()

    def SwapScreens(self,e):
        if self.resultsscreen == True:
            self.shaperadio.SetSelection(0)
            self.ShowSetupControls()
            self.resultsscreen=False
        else:
            self.write_paramfile()
            print("Running code. Please wait a few seconds whilst this completes")
            subprocess.call(["mpiexec","-n","4","./simulation/windtunnel"])
            self.dto = self.demo.GetVTKData()
            self.ShowResultsControls()
            self.resultsscreen=True

    def ShowResultsControls(self):
        self.figure.clf()
        self.HideSetupControls()
        self.buttonsizer.Clear()

        self.simbutton.Show()
        self.loadradio.Show()
        self.radiobox.Show()
        #self.button.Show()
        self.logger.Show()


        self.buttonsizer.Add(self.simbutton,1,wx.EXPAND)
        self.buttonsizer.AddStretchSpacer(1)
        self.buttonsizer.Add(self.loadradio)
        #self.buttonsizer.Add(self.loadbutton,1,wx.EXPAND)
        self.buttonsizer.Add(self.radiobox)
        #self.buttonsizer.Add(self.button,1,wx.EXPAND)
        self.buttonsizer.AddStretchSpacer(12)
        self.buttonsizer.Add(self.logger,1,wx.EXPAND)



        self.buttonsizer.Layout()
        self.Fit()
        self.simbutton.SetLabel("New Simulation")


        self.UpdateResults(0)

    def HideResultsControls(self):
        self.simbutton.Hide()
        self.loadradio.Hide()
        self.radiobox.Hide()
        self.button.Hide()
        self.logger.Hide()



    def ShowSetupControls(self):
        self.figure.clf()
        self.canvas.draw()
        self.canvas.Refresh()
        self.HideSetupControls()
        self.HideResultsControls()
        self.buttonsizer.Clear()

        self.simbutton.Show()
        self.shaperadio.Show()
        self.angletext.Show()
        self.atext.Show()
        self.btext.Show()
        self.angleslider.Show()



        if self.shaperadio.GetSelection() == 0:
            self.aslider.Show()
            self.bslider.Show()
            self.mslider.Hide()
            self.tslider.Hide()
        else:
            self.mslider.Show()
            self.tslider.Show()
            self.aslider.Hide()
            self.bslider.Hide()



        self.buttonsizer.Add(self.simbutton,1,wx.EXPAND)
        self.buttonsizer.AddStretchSpacer(1)
        self.buttonsizer.Add(self.shaperadio)
        self.buttonsizer.AddStretchSpacer(1)
        self.buttonsizer.Add(self.angletext)
        self.buttonsizer.Add(self.angleslider)
        if self.shaperadio.GetSelection() == 0:
            self.buttonsizer.Add(self.atext)
            self.buttonsizer.Add(self.aslider)
            self.buttonsizer.Add(self.btext)
            self.buttonsizer.Add(self.bslider)
            print("Ellipse")
        else:
            self.buttonsizer.Add(self.atext)
            self.buttonsizer.Add(self.mslider)
            self.buttonsizer.Add(self.btext)
            self.buttonsizer.Add(self.tslider)
            print("Aerofoil")


        self.buttonsizer.Layout()
        self.Fit()

        self.simbutton.SetLabel("Run Simulation")
        self.GetShape(0)




    def HideSetupControls(self):
        self.simbutton.Hide()
        self.shaperadio.Hide()
        self.angleslider.Hide()
        self.aslider.Hide()
        self.bslider.Hide()
        self.mslider.Hide()
        self.tslider.Hide()
        self.angletext.Hide()
        self.atext.Hide()
        self.btext.Hide()


    def SwapShape(self,e):
        self.ShowSetupControls()
        self.GetShape(0)

    def GetShape(self,e):
        if self.shaperadio.GetSelection()==0:
            #print "Getting Ellipse"
            self.GetEllipse()
            a=0.1*self.aslider.GetValue()
            b=0.1*self.bslider.GetValue()
            self.atext.SetLabel("Red Axis = %3.1f"%a)
            self.btext.SetLabel("Blue Axis = %3.1f"%b)

        else:
            #print "Getting Aerofoil"
            self.GetAerofoil()
            m=0.01*self.mslider.GetValue()
            t=0.1*self.tslider.GetValue()
            self.atext.SetLabel("Camber    = %4.2f"%m)
            self.btext.SetLabel("Thickness = %3.1f"%t)

        self.RotateShape(0)

    def GetEllipse(self):
        a=self.aslider.GetValue()*0.1
        b=self.bslider.GetValue()*0.1
        xu=np.linspace(-a,a,100)
        xd=np.flipud(xu)

        yu=b*np.sqrt(1-(xu/a)**2)
        yd=-b*np.sqrt(1-(xd/a)**2)

        self.x=np.append(xu,xd)
        self.y=np.append(yu,yd)
        #print "Got ellipse"



    def GetAerofoil(self):
        m=self.mslider.GetValue()*0.01
        t=self.tslider.GetValue()*0.1
        p=0.4
        c=2.

        xl=np.linspace(0,p,50)
        xu=np.linspace(p,1,50)


        ycl=m*xl/p/p * (2*p-xl)
        thetal = 2.*m/p/p * (p-xl)

        ycu=m*(1-xu)/(1.-p)/(1.-p) * (1+xu-2*p)
        thetau=2.*m/(1.-p)/(1.-p) * (p-xu)

        theta=np.append(thetal,thetau)
        theta=np.arctan(theta)

        x=np.append(xl,xu)
        yc=np.append(ycl,ycu)

        yt=5*t*(0.2969*np.sqrt(x)-0.1260*x-0.3516*x*x+0.2843*x*x*x-0.1015*x*x*x*x)


        # xu=xx-yt*sin(theta)
        yu=yc+yt*np.cos(theta)

        # xl=xx+yt*sin(theta)
        yl=yc-yt*np.cos(theta)

        self.x=np.append(x,np.flipud(x))
        self.x=self.x*c-1
        self.y=np.append(yu,np.flipud(yl))






        #print "Got aerofoil"

    def RotateShape(self,e):
        theta=self.angleslider.GetValue()*np.pi/180.*(-1.)

        xrot = self.x * np.cos(theta) - self.y * np.sin(theta)
        yrot = self.y * np.cos(theta) + self.x * np.sin(theta)


        self.figure.clf()
        self.plt=self.figure.add_subplot(111)

        self.plt.plot(xrot,yrot,color="black")

        self.plt.axis('equal')
        self.plt.set_xlim(-2.,2.)
        self.plt.set_xlabel("x (m)")
        self.plt.set_ylabel("y (m)")
        self.plt.set_ylim(-2.,2.)
        self.plt.set_aspect('equal', adjustable='box')

        if self.shaperadio.GetSelection() == 0:
            a=self.aslider.GetValue()*0.1
            b=self.bslider.GetValue()*0.1
            ax=np.array([a*np.cos(-theta),-a*np.cos(-theta)])
            ay=np.array([-a*np.sin(-theta),a*np.sin(-theta)])

            bx=np.array([-b*np.sin(-theta),b*np.sin(-theta)])
            by=np.array([-b*np.cos(-theta),b*np.cos(-theta)])

            self.plt.plot(ax,ay,color='red')
            self.plt.plot(bx,by,color='blue')


        self.canvas.draw()
        self.canvas.Refresh()

        self.angletext.SetLabel("Angle = %i degrees"%self.angleslider.GetValue())


    def write_paramfile(self):
        #for now just write the shape parameters

        shapetype = self.shaperadio.GetSelection()
        alpha = self.angleslider.GetValue()*1.0

        if shapetype == 0:
            a=self.aslider.GetValue()*0.1
            b=self.bslider.GetValue()*0.1
        else:
            m=self.mslider.GetValue()*0.01
            t=self.tslider.GetValue()*0.1

        f=open('params.dat','w')

        f.write("&SHAPEPARAMS\n")
        f.write("SHAPE= %i,\n"%(shapetype+1))
        f.write("ALPHA= %f,\n"%alpha)
        if shapetype ==0:
            f.write("A= %f,\n"%a)
            f.write("B= %f,\n"%b)
        else:
            f.write("M= %f,\n"%m)
            f.write("T= %f,\n"%t)
        f.write("/\n")
        f.close()

        print("Created parameter file")

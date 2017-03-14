from __future__ import print_function
import client
import numpy as np
import wx
import subprocess
import shutil
import time
import range as Range
import takeoff
import datetime



#select the UI abstract superclass to derive from
UI=client.AbstractmatplotlibUI

# Derive the demo-specific GUI class from the Abstract??UI class
class WindTunnelWindow(UI):

    def __init__(self,parent,title,demo,servercomm):

        #call superclass' __init__
        UI.__init__(self,parent,title,demo,servercomm)

        self.serverversion=True
        self.Vorticity=False

        self.now = datetime.datetime.now

        self.date=self.now().strftime("%Y-%m-%d")

        filename = self.date+".log"

        self.logfile = open(filename,'a')




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

        if self.Vorticity:
            self.radiobox=wx.RadioBox(self,wx.ID_ANY,label="Variable",choices=["Flow","Pressure", "Vorticity","Velocity"],majorDimension=2,style=wx.RA_SPECIFY_COLS)
        else:
            self.radiobox=wx.RadioBox(self,wx.ID_ANY,label="Variable",choices=["Flow","Pressure"],majorDimension=2,style=wx.RA_SPECIFY_COLS)



        self.Bind(wx.EVT_RADIOBOX,self.UpdateResults,self.radiobox)
        self.Bind(wx.EVT_RADIOBOX,self.UpdateResults,self.loadradio)

        self.logger = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_NO_VSCROLL,size=(-1,60))
        self.logger.SetDefaultStyle(wx.TextAttr(wx.Colour(0,0,0),wx.Colour(0,0,0)))
        self.logger.AppendText(" \n \n")
        self.logger.Refresh()


        #controls for setting up simulation

        self.shaperadio=wx.RadioBox(self,wx.ID_ANY,label="Shape",choices=["Ellipse", "Aerofoil"])
        self.Bind(wx.EVT_RADIOBOX,self.SwapShape,self.shaperadio)
        self.shaperadio.SetSelection(1)

        self.angleslider=wx.Slider(self,wx.ID_ANY,value=0,minValue=-45,maxValue=45)

        self.aslider=wx.Slider(self,wx.ID_ANY,value=6,minValue=2,maxValue=10)
        self.bslider=wx.Slider(self,wx.ID_ANY,value=6,minValue=2,maxValue=10)

        self.mslider=wx.Slider(self,wx.ID_ANY,value=0,minValue=-30,maxValue=30)
        self.tslider=wx.Slider(self,wx.ID_ANY,value=10,minValue=0,maxValue=50)

        self.angletext=wx.StaticText(self,label="Angle of attack = 0 degrees")
        self.atext=wx.StaticText(self,label="Red Axis = 1")
        self.btext=wx.StaticText(self,label="Green Axis = 1")

        self.ResetButton=wx.Button(self,wx.ID_ANY,label="Reset Options")

        self.TakeoffButton=wx.Button(self,wx.ID_ANY,label="Take off")
        self.RangeButton=wx.Button(self,wx.ID_ANY,label="Range")


        self.Bind(wx.EVT_SLIDER,self.GetShape,self.aslider)
        self.Bind(wx.EVT_SLIDER,self.GetShape,self.bslider)
        self.Bind(wx.EVT_SLIDER,self.GetShape,self.mslider)
        self.Bind(wx.EVT_SLIDER,self.GetShape,self.tslider)
        self.Bind(wx.EVT_SLIDER,self.RotateShape,self.angleslider)
        self.Bind(wx.EVT_BUTTON,self.reset,self.ResetButton)

        self.Bind(wx.EVT_BUTTON,self.ShowRange,self.RangeButton)
        self.Bind(wx.EVT_BUTTON,self.ShowTakeoff,self.TakeoffButton)

        self.range=False
        self.takeoff=False

        self.ShowSetupControls()

        self.resultsscreen=False

        # self.dto = self.demo.GetVTKData()
        # self.ShowResultsControls()
        # self.resultsscreen=True


        self.mainsizer.Add(self.buttonsizer,1,wx.EXPAND | wx.ALL)
        self.mainsizer.Add(self.canvas,3,wx.EXPAND | wx.ALL)



        self.SetSizer(self.mainsizer)
        self.Fit()



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
        #UI.TimerCallback(self,e)
        #INSERT ANY CUSTOM CODE HERE
        if self.servercomm.IsStarted():

            #if one file is available:
            if self.nfiles.value == 1:
                self.dlg.Update(50,"Calculating viscous flow")


            #if all files are ready
            if self.nfiles.value == 2:
                self.dlg.Update(90,"Downloading results")

                if self.potential == None:
                    #need to fetch potential results...
                    if self.newdata.value==True:
                        #read data from process:
                        self.dto=self.pipemain.recv() #get the dto from process
                        self.newdata.value=False
                        self.getdata.value=False
                        self.pipemain.send(0)
                        self.potential=self.dto.GetData()
                    else:
                        #request process reads new data
                        self.frameno.value=0
                        self.getdata.value=True


                if self.viscous == None and self.potential != None:
                    #need to fetch potential results...
                    if self.newdata.value==True:
                        #read data from process:
                        self.dto=self.pipemain.recv() #get the dto from process
                        self.newdata.value=False
                        self.getdata.value=False
                        self.finished.value=True
                        self.pipemain.send(0)
                        self.viscous=self.dto.GetData()

                    else:
                        #request process reads new data
                        self.frameno.value=1
                        self.getdata.value=True

                if (self.viscous != None) and (self.potential != None):

                    self.ShowResultsControls()
                    self.resultsscreen=True
                    self.dlg.Update(100,"Done")
                    self.tstop=time.time()
                    print("Time to complete = ",self.tstop-self.tstart)
                    self.StopSim()

                    self.logfile.write("    Time to Complete = "+str(self.tstop-self.tstart)+"\n")
                    self.logfile.write("    Lift= "+str(self.potential.lift[0])+"\n")
                    self.logfile.write("    Drag= "+str(self.potential.drag[0])+"\n")
                    self.logfile.write("    Lift/drag= "+str(self.potential.lift[0]/self.potential.drag[0])+"\n")
                    self.logfile.write("    Lift coeff= "+str(self.potential.C_l)+"\n")
                    self.logfile.write("    Drag coeff= "+str(self.potential.C_d)+"\n")

                    self.logfile.flush()

                    for widget in self.GetChildren():
                        widget.Enable(True)

                    self.timer.Stop()















    def OnClose(self,e):
        print("Requested an exit")
        UI.OnClose(self,e)
        self.logfile.close()
        quit()

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
            #**** uncomment these to always reset shape options when setting up a new sim ********
            #self.shaperadio.SetSelection(0)
            #self.reset(0)
            #*************************************************************************************
            self.ShowSetupControls()
            self.resultsscreen=False
        else:

            self.viscous=None
            self.potential=None

            self.write_paramfile()

            self.add_lines()




            self.dlg=wx.ProgressDialog(title="Running Simulation - Please Wait",message="Starting simulation",style=wx.PD_AUTO_HIDE|wx.PD_APP_MODAL,parent=self)

            for widget in self.GetChildren():
                widget.Enable(False)
            self.tstart=time.time()
            if self.serverversion:
                self.StartSim('config.txt')
                self.logfile.write("    simID="+self.servercomm.simid+"\n")



            self.dlg.Update(10,"Calculating potential flow")

            if not self.serverversion:
                print("Running code. Please wait a few seconds whilst this completes")
                subprocess.call(["mpiexec","-n","4","./simulation/windtunnel"])

                self.logfile.write("    simID=None\n")

                #get potential data file
                shutil.copy2('potential.dat','tmp.nc')
                self.dto = self.demo.GetVTKData(None)
                self.potential=self.dto.GetData()
                self.dlg.Update(50,"Got potential file")

                #get viscous data file
                shutil.copy2('output.dat','tmp.nc')
                self.dto = self.demo.GetVTKData(None)
                self.viscous=self.dto.GetData()
                self.dlg.Update(90,"Got viscous file")



                #dlg.Update(90,"Run simulation")

                #self.dto = self.demo.GetVTKData()

                self.dlg.Update(100,"Done")
                self.tstop=time.time()
                print("Time to complete = ",self.tstop-self.tstart)

                self.logfile.write("    Time to Complete = "+str(self.tstop-self.tstart)+"\n")
                self.logfile.write("    Lift= "+str(self.potential.lift[0])+"\n")
                self.logfile.write("    Drag= "+str(self.potential.drag[0])+"\n")
                self.logfile.write("    Lift/drag= "+str(self.potential.lift[0]/self.potential.drag[0])+"\n")
                self.logfile.write("    Lift coeff= "+str(self.potential.C_l)+"\n")
                self.logfile.write("    Drag coeff= "+str(self.potential.C_d)+"\n")

                self.logfile.flush()


                for widget in self.GetChildren():
                    widget.Enable(True)


                self.ShowResultsControls()
                self.resultsscreen=True

            self.logfile.flush()

    def ShowResultsControls(self):
        self.figure.clf()
        self.HideSetupControls()
        self.buttonsizer.Clear()

        self.simbutton.Show()
        if self.Vorticity:
            self.loadradio.Show()
        self.radiobox.Show()
        self.logger.Show()

        self.TakeoffButton.Show()
        self.RangeButton.Show()


        self.buttonsizer.Add(self.simbutton,0,wx.EXPAND|wx.TOP)
        self.buttonsizer.AddStretchSpacer(0)
        self.buttonsizer.Add(self.loadradio,0,wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        self.buttonsizer.Add(self.radiobox,0,wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        self.buttonsizer.AddStretchSpacer(4.5)

        self.buttonsizer.Add(self.TakeoffButton,0,wx.EXPAND)
        self.buttonsizer.Add(self.RangeButton,0,wx.EXPAND)

        self.buttonsizer.Add(self.logger,0,wx.EXPAND | wx.ALIGN_CENTER)



        self.buttonsizer.Layout()
        #self.Fit()
        self.simbutton.SetLabel("New Simulation")


        self.UpdateResults(0)

    def HideResultsControls(self):
        self.simbutton.Hide()
        self.loadradio.Hide()
        self.radiobox.Hide()
        self.logger.Hide()
        self.TakeoffButton.Hide()
        self.RangeButton.Hide()
        try:
            self.TakeoffFrame.Destroy()
            self.TakeoffButton.Enable()
        except:
            pass
        try:
            self.RangeFrame.Destroy()
            self.RangeButton.Enable()
        except:
            pass



    def ShowSetupControls(self):
        self.figure.clf()
        self.canvas.draw()
        self.canvas.Refresh()
        self.HideSetupControls()
        self.HideResultsControls()
        self.buttonsizer.Clear()

        self.simbutton.Show()
        self.shaperadio.Hide()
        self.angletext.Show()
        self.atext.Show()
        self.btext.Show()
        self.angleslider.Show()
        self.ResetButton.Show()



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



        self.buttonsizer.Add(self.simbutton,0,wx.EXPAND)
        self.buttonsizer.AddStretchSpacer(0)
        self.buttonsizer.Add(self.shaperadio,0,wx.ALIGN_CENTRE | wx.EXPAND)
        #self.buttonsizer.AddStretchSpacer(1)
        self.buttonsizer.Add(self.angletext)
        self.buttonsizer.Add(self.angleslider,0,wx.EXPAND)
        if self.shaperadio.GetSelection() == 0:
            self.buttonsizer.Add(self.atext)
            self.buttonsizer.Add(self.aslider,0,wx.EXPAND)
            self.buttonsizer.Add(self.btext)
            self.buttonsizer.Add(self.bslider,0,wx.EXPAND)
            print("Ellipse")
        else:
            self.buttonsizer.Add(self.atext)
            self.buttonsizer.Add(self.mslider,0,wx.EXPAND)
            self.buttonsizer.Add(self.btext)
            self.buttonsizer.Add(self.tslider,0,wx.EXPAND)
            print("Aerofoil")
        self.buttonsizer.AddStretchSpacer(5)
        self.buttonsizer.Add(self.ResetButton,0,wx.EXPAND | wx.ALIGN_BOTTOM)


        self.buttonsizer.Layout()
        #self.Fit() #if uncommented this causes window to resize upon swapping screens

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
        self.ResetButton.Hide()

    def reset(self,e):
        self.aslider.SetValue(6)
        self.bslider.SetValue(6)
        self.angleslider.SetValue(0)
        self.mslider.SetValue(0)
        self.tslider.SetValue(2)
        self.GetShape(0)




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
            t=0.01*self.tslider.GetValue()+0.1
            self.atext.SetLabel("Camber    = %4.2f"%m)
            self.btext.SetLabel("Thickness = %3.2f"%t)

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
        t=self.tslider.GetValue()*0.01+0.1
        p=0.4
        c=2.

        xl=np.linspace(0,p*c,40)
        xu=np.linspace(p*c,c,60)
        x=np.append(xl,xu)
        xc=x/c
        xlc=xl/c
        xuc=xu/c

        yt=5*t*(0.2969*np.sqrt(xc) -0.1260*xc -0.3516*(xc*xc) + 0.2843*xc*xc*xc - 0.1015*xc*xc*xc*xc )

        #ycl = m/p**2 * (2*p*xlc - xlc**2) #correct way, but looks odd-shaped for large T and M
        ycl = m*xl/p/p * (2*p-xlc)

        #ycu = m/(1-p)**2 * ( (1-2*p) + 2*p*(xuc) - xuc**2) #correct way, but looks odd-shaped for large T and M
        ycu = m*(c-xu)/(1-p)/(1-p) * (1+xuc-2*p)

        yc=np.append(ycl,ycu)

        tanthetal = 2*m/p/p * (p-xlc)
        tanthetau = 2*m/(1-p)**2 * (p-xuc)

        theta = np.arctan(np.append(tanthetal,tanthetau))

        xu = x #- yt*np.sin(theta) #technically correct, but looks odd
        yu = yc + yt*np.cos(theta)

        xl = x #+ yt*np.sin(theta) #technically correct but looks odd
        yl = yc - yt*np.cos(theta)


        self.x=np.append(xu,np.flipud(xl))-1.

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

        #add arrows to show airflow direction

        self.plt.arrow(-1.5,-1.5,1.0,0.0,lw=1,head_width=0.1,color="black")
        self.plt.arrow(-1.5,1.5,1.0,0.0,lw=1,head_width=0.1,color="black")
        self.plt.arrow(0.5,-1.5,1.0,0.0,lw=1,head_width=0.1,color="black")
        self.plt.arrow(0.5,1.5,1.0,0.0,lw=1,head_width=0.1,color="black")


        self.canvas.draw()
        self.canvas.Refresh()

        self.angletext.SetLabel("Angle = %i degrees"%self.angleslider.GetValue())


    def add_lines(self):

        nvert=4
        nhoriz=4

        #draw vertical lines
        if nvert > 0:
            dx=4./nvert
            for i in range(nvert):
                x=[i*dx-2.0,i*dx-2.0]
                y=[-2.,2.]
                self.plt.plot(x,y,color="black",linestyle="dashed")

        #draw horizontal lines
        if nhoriz > 0:
            dx=4./nhoriz
            for i in range(nhoriz):
                x=[-2.,2.]
                y=[i*dx-2.0,i*dx-2.0]
                self.plt.plot(x,y,color="black",linestyle="dashed")

        self.canvas.draw()
        self.canvas.Refresh()




    def write_paramfile(self):
        #for now just write the shape parameters
        curtime=self.now().strftime("%H:%M:%S")
        self.logfile.write("* New Simulation\n")
        self.logfile.write("    Time= "+curtime+"\n")

        shapetype = self.shaperadio.GetSelection()
        alpha = self.angleslider.GetValue()*1.0

        if shapetype == 0:
            a=self.aslider.GetValue()*0.1
            b=self.bslider.GetValue()*0.1
        else:
            m=self.mslider.GetValue()*0.01
            t=self.tslider.GetValue()*0.01+0.1

        f=open('config.txt','w')

        f.write("&SHAPEPARAMS\n")
        f.write("SHAPE= %i,\n"%(shapetype+1))
        f.write("ALPHA= %f,\n"%alpha)
        if shapetype ==0:
            f.write("A= %f,\n"%a)
            f.write("B= %f,\n"%b)
        else:
            f.write("M= %f,\n"%m)
            f.write("T= %f,\n"%t)
            self.logfile.write("    alpha= "+str(alpha)+"\n")
            self.logfile.write("    m= "+str(m)+"\n")
            self.logfile.write("    t= "+str(t)+"\n")

        f.write("/\n")

        if self.Vorticity == False:
            f.write("&VORTPARAMS\n")
            f.write("VORTICITY= .FALSE.\n")
            f.write("/\n")


        f.close()

        print("Created parameter file")


    def ShowRange(self,e):
        (c_lift,c_drag)=(self.potential.C_la,self.potential.C_da)
        print("lift=",c_lift,"  drag=",c_drag)
        self.RangeFrame = Range.Range(self,"Range",(1080,540),c_lift=c_lift,c_drag=c_drag)
        self.RangeFrame.Show()


    def ShowTakeoff(self,e):

        (c_lift,c_drag)=(self.potential.C_la,self.potential.C_da)
        print("lift=",c_lift,"  drag=",c_drag)
        self.TakeoffFrame = takeoff.Takeoff(self,'Runway',size=(1200,675),c_lift=c_lift,c_drag=c_drag)
        self.TakeoffFrame.Show()

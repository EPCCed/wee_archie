from __future__ import print_function
import client
import numpy as np
import wx



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

        self.mslider=wx.Slider(self,wx.ID_ANY,value=0,minValue=-20,maxValue=20)
        self.tslider=wx.Slider(self,wx.ID_ANY,value=2,minValue=1,maxValue=6)





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

        self.dto = demo.GetVTKData()





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
            self.ShowResultsControls()
            #self.ShowSetupControls()
            self.resultsscreen=True

    def ShowResultsControls(self):
        self.figure.clf()
        self.HideSetupControls()
        self.buttonsizer.Clear()

        self.simbutton.Show()
        self.loadradio.Show()
        self.radiobox.Show()
        self.button.Show()
        self.logger.Show()


        self.buttonsizer.Add(self.simbutton,1,wx.EXPAND)
        self.buttonsizer.AddStretchSpacer(1)
        self.buttonsizer.Add(self.loadradio)
        #self.buttonsizer.Add(self.loadbutton,1,wx.EXPAND)
        self.buttonsizer.Add(self.radiobox)
        self.buttonsizer.Add(self.button,1,wx.EXPAND)
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
        self.buttonsizer.Add(self.angleslider)
        if self.shaperadio.GetSelection() == 0:
            self.buttonsizer.Add(self.aslider)
            self.buttonsizer.Add(self.bslider)
        else:
            self.buttonsizer.Add(self.mslider)
            self.buttonsizer.Add(self.tslider)


        self.buttonsizer.Layout()
        self.Fit()

        self.simbutton.SetLabel("Run Simulation")




    def HideSetupControls(self):
        self.simbutton.Hide()
        self.shaperadio.Hide()
        self.angleslider.Hide()
        self.aslider.Hide()
        self.bslider.Hide()
        self.mslider.Hide()
        self.tslider.Hide()


    def SwapShape(self,e):
        self.ShowSetupControls()

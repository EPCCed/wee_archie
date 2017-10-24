# -*- coding: utf-8 -*-
import client
import wx
from wx.lib.masked import *
import vtk

import numpy as np

import matplotlib
matplotlib.use("WXAgg")

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
from time import strftime

# New module to import the live weather forcast
from weather_live import LiveWeather

# select the UI abstract superclass to derive from
UI = client.AbstractvtkUI

imageFile = 'uk.jpg'
rain = 'resizedrain.jpg'
cloud = 'resizedcloud.jpg'
sun = 'resizedsun.jpg'

edinburgh = []
london = []
cornwall = []
highlands = []

# Derive the demo-specific GUI class from the AbstractUI class
class WeatherWindow(UI):
    def __init__(self, parent, title, demo, servercomm):

        # call superclass' __init__
        UI.__init__(self, parent, title, demo, servercomm)

        # panel=wx.Panel(self)
        wx.Frame.CenterOnScreen(self)

        self.fullscreen = False
        self.playing = False
        self.decompositiongrid = True
        self.timeofyear = None
        self.rainmass = 0
        self.cropslevel = 0
        self.waterlevel = 0
        self.numberofcores = 0
        self.columnsinX = 1
        self.columnsinY = 1
        self.mappers = {}
        self.actors = {}
        self.filters = {}
        self.widgets = {}
        self.views = {}

        self.demo = demo
        self.servercomm = servercomm
        self.title = title

        self.mode = 0

        menubar = wx.MenuBar()
        playbackMenu = wx.Menu()
        self.playpauseitem = playbackMenu.Append(wx.ID_ANY, 'Pause', 'Pause playback')
        cease = playbackMenu.Append(wx.ID_ANY, 'Stop', 'Stop simulation')

        fileMenu = wx.Menu()
        settings = fileMenu.Append(wx.ID_ANY, 'Settings', 'Open settings window')
        playbackAdded = fileMenu.AppendSubMenu(playbackMenu, 'Playback', 'Playback control')
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')

        viewMenu = wx.Menu()
        temp = viewMenu.Append(wx.ID_ANY, 'Temperature', 'Change to temp view')
        press = viewMenu.Append(wx.ID_ANY, 'Pressure', 'Change to press view')
        real = viewMenu.Append(wx.ID_ANY, 'Real World', 'Change to real view')

        gridCheckItem=viewMenu.AppendCheckItem(wx.ID_ANY, 'Show grid', 'Show decomposition grid')

        menubar.Append(fileMenu, '&File')
        menubar.Append(viewMenu, '&Views')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        self.Bind(wx.EVT_MENU, self.OpenWindow, settings)
        self.Bind(wx.EVT_MENU, self.temp_view, temp)
        self.Bind(wx.EVT_MENU, self.press_view, press)
        self.Bind(wx.EVT_MENU, self.real_view, real)

        self.Bind(wx.EVT_MENU, self.pauseResult, self.playpauseitem)
        self.Bind(wx.EVT_MENU, self.onStopSim, cease)
        self.Bind(wx.EVT_MENU, self.togglegrid, gridCheckItem)

        # add another renderer for the bottom part
        self.bottomrenderer = vtk.vtkRenderer()
        self.bottomrenderer.SetViewport(0, 0, 1, 0.3)

        # set up sizers that allow you to position window elements easily
        # main sizer - arrange items horizontally on screen (controls on left, vtk interactor on right)
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        # text at bottom that displays the current frame number
        #self.logger = wx.TextCtrl(self, style=wx.TE_READONLY)

        # This is where the demo is attached to the window.
        self.mainsizer.Add(self.vtkwidget, 2, wx.EXPAND)

        # attach main sizer to the window
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(1)
        self.mainsizer.Fit(self)

        # create mapper
        # self.mapper=vtk.vtkPolyDataMapper()

        self.StartInteractor()

        # show window
        self.Show()

    # Function to call NewWindow class to allow a button to open it.
    def OpenWindow(self, event):
        self.new = NewWindow(None, -1, self.title, self.demo, self.servercomm, self)
        self.new.Show()

    def temp_view(self, e):
        self.mode = 1

    def press_view(self, e):
        self.mode = 2

    def real_view(self, e):
        self.mode = 0

    def OnQuit(self, e):
        self.Close()

    def StartInteractor(self):
        UI.StartInteractor(self)

    def StartSim(self, config):
        UI.StartSim(self, config)

    def onStopSim(self, e):
        self.StopSim()

    def togglegrid(self, e):
        if self.decompositiongrid is True:
            self.decompositiongrid = False
        else:
            self.decompositiongrid = True

        if self.timer.IsRunning():
            self.timer.Stop()
            self.timer.Start()

    def pauseResult(self, e):
        if not self.playing:  # play
            self.getdata.value = True
            self.playpauseitem.SetText("Pause")
            self.playing = True

        else:  # pause
            self.getdata.value = False
            self.playpauseitem.SetText("Resume")
            self.playing = False

    def StopSim(self):
        UI.StopSim(self)

    def TimerCallback(self, e):
        UI.TimerCallback(self, e)

        #self.logger.SetValue("Frame %d of %d" % (self.CurrentFrame, self.nfiles.value - 1))

    def OnClose(self, e):
        UI.OnClose(self, e)

    # ----------------------------------------------------------------------
    # ------------- New methods specific to demo go here -------------------
    # ----------------------------------------------------------------------

########----------------------------------------Sam's new classes---------------------------


# Class to create a new window for the "settings".
class NewWindow(wx.Frame):
    def __init__(self, parent, id, title, demo, servercomm, mainWeatherWindow):
        wx.Frame.__init__(self, parent, id, 'Settings', size=(1800, 2800))
        wx.Frame.CenterOnScreen(self)

        self.demo = demo
        self.servercomm = servercomm
        self.title = title

        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # Create the tab windows
        tab3 = TabAdvanced(nb, self.title, self.demo, self.servercomm, mainWeatherWindow)
        tab2 = TabSetup(nb, tab3, self.servercomm, mainWeatherWindow, self)
        tab1 = TabLocation(nb, tab3, tab2, 1800)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "Location")
        nb.AddPage(tab2, "Setup")
        nb.AddPage(tab3, "Advanced")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)

class TabSetup(wx.Panel):
    def __init__(self, parent, mainTabAdvanced, servercomm, mainWeatherWindow, setupWindow):
        wx.Panel.__init__(self, parent)
        self.weatherLocationCode=None
        self.servercomm=servercomm
		#The window's sizer - for the rows of control panels and the go button
        self.WinSizer=wx.BoxSizer(wx.VERTICAL)

        self.setupWindow=setupWindow

        #sizer for the top row of controls
        self.TopSizer=wx.BoxSizer(wx.HORIZONTAL)

        self.TopLeftSizer=wx.BoxSizer(wx.VERTICAL)

        #Add this to the window's sizer
        self.WinSizer.Add(self.TopSizer,1,wx.EXPAND)

        self.mainTabAdvanced=mainTabAdvanced
        self.mainWeatherWindow=mainWeatherWindow

        # Top row of control panels
        self.LocationPanel=wx.Panel(self,style=wx.BORDER_SUNKEN,size=(200,100))
        self.CoresPanel=wx.Panel(self,style=wx.BORDER_SUNKEN,size=(200,100))
        self.NodesPanel=wx.Panel(self,style=wx.BORDER_SUNKEN,size=(200,100))

        self.TopLeftSizer.Add(self.LocationPanel, 1,wx.EXPAND | wx.ALL,border=5)
        self.TopLeftSizer.Add(self.CoresPanel, 1,wx.EXPAND | wx.ALL,border=5)

        #Add these panels to their sizer
        self.TopSizer.Add(self.TopLeftSizer,1,wx.EXPAND | wx.ALL,border=5)
        self.TopSizer.Add(self.NodesPanel,1,wx.EXPAND| wx.ALL,border=5)

        #Bottom panel, which will contain the sliders and piechart panels
        self.PhysicsPanel=wx.Panel(self,style=wx.BORDER_SUNKEN)

        #Add this to the window's sizer
        self.WinSizer.Add(self.PhysicsPanel,1,wx.EXPAND| wx.ALL, border=5)

        #sizer for the bottom row of controls
        self.BottomSizer=wx.BoxSizer(wx.HORIZONTAL)

        #assign this sizer to the PhysicsPanel
        self.PhysicsPanel.SetSizer(self.BottomSizer)

        #the bottom panels
        self.SlidersPanel=wx.Panel(self.PhysicsPanel,size=(200,100))
        self.PiePanel=wx.Panel(self.PhysicsPanel,size=(200,100))

        #Add the bottom panels to the BottomSizer
        self.BottomSizer.Add(self.SlidersPanel,1,wx.EXPAND| wx.ALL, border=5)
        self.BottomSizer.Add(self.PiePanel,1,wx.EXPAND| wx.ALL, border=5)

        locationSizer=wx.BoxSizer(wx.VERTICAL)
        self.LocationPanel.SetSizer(locationSizer)

        self.text_Location=wx.StaticText(self.LocationPanel,label="Location: Edinburgh")
        self.time_Location=wx.StaticText(self.LocationPanel,label="Time: 0600 Z")
        self.weather_Location=wx.StaticText(self.LocationPanel,label="Weather: Cloudy")

        locationSizer.Add(self.text_Location,0,wx.LEFT,border=5)
        locationSizer.Add(self.time_Location,0,wx.LEFT,border=5)
        locationSizer.Add(self.weather_Location,0,wx.LEFT,border=5)

        # Cores Panel

        #set up main sizer for the panel
        coresSizer=wx.BoxSizer(wx.VERTICAL)
        self.CoresPanel.SetSizer(coresSizer)

        #label for the panel
        t1=wx.StaticText(self.CoresPanel,label="Number of Cores per Node")


        #load initial image - this will be reloaded, but we need something there to workout the dimensions of the panel
        file="chip1.png"
        bmp=wx.Image(file, wx.BITMAP_TYPE_ANY).Scale(300,300).ConvertToBitmap()
        self.bitmap1 = wx.StaticBitmap(self.CoresPanel,bitmap=bmp, size=(100, 100))

        #Radiobox to select the number of cores
        self.coresRadio=wx.RadioBox(self.CoresPanel,choices=["1","2","3","4"])
        self.coresRadio.SetSelection(0)

        #bind changing the selection to the UpdateChip method (which redraws the image of the chip)
        self.Bind(wx.EVT_RADIOBOX,self.UpdateChip,self.coresRadio)

        #Add these to their sizer
        coresSizer.Add(t1,0,wx.CENTRE,border=5)
        coresSizer.Add(self.bitmap1,1,wx.ALIGN_CENTRE)
        coresSizer.Add(self.coresRadio,0,wx.ALIGN_CENTRE)

        # Nodes Panel

        #set up main sizer
        nodesSizer=wx.BoxSizer(wx.VERTICAL)
        self.NodesPanel.SetSizer(nodesSizer)

        #label for the panel
        t2=wx.StaticText(self.NodesPanel,label="Number of Nodes")

        #create a grid of panels corresponding to each pi in Wee Archie.
        nodesGrid=wx.GridSizer(rows=4,cols=4)

        self.nodes=[]
        for i in range(16):
            self.nodes.append(wx.Panel(self.NodesPanel,style=wx.BORDER_SUNKEN))

        #place them in the sizer (filling up rows then columns)
        for row in range(4):
            for col in range(4):
                i=col*4+row
                nodesGrid.Add(self.nodes[i],1,wx.EXPAND)

        #slider to select the number of nodes
        self.NodesSlider=wx.Slider(self.NodesPanel,minValue=1,maxValue=16,value=1,name="nodes")
        self.SetNodes()

        #bind moving the sliders to the method SetNodes (which colours the node panels according to your selection)
        self.Bind(wx.EVT_SLIDER,self.SetNodes,self.NodesSlider)

        #add these to their sizer
        nodesSizer.Add(t2,0,wx.CENTRE,border=5)
        nodesSizer.Add(nodesGrid,1,wx.EXPAND|wx.ALL,border=10)
        nodesSizer.Add(self.NodesSlider,0,wx.EXPAND)

        #sliders panel

        #set up main sizer
        slidersSizer=wx.BoxSizer(wx.VERTICAL)
        self.SlidersPanel.SetSizer(slidersSizer)

        #label for this panel
        t3=wx.StaticText(self.SlidersPanel,label="Physics")
        slidersSizer.Add(t3,0,wx.CENTRE,border=5)

        #set up the sliders
        self.sliders=[]
        for i in range(3):
            self.sliders.append(wx.Slider(self.SlidersPanel,minValue=0,maxValue=100,value=33))

        for slider in self.sliders:
            slidersSizer.Add(slider,1,wx.EXPAND)

        #set up the reset button and bind pressing it to the ResetSliders method
        self.SliderResetButton=wx.Button(self.SlidersPanel,label="Reset")
        slidersSizer.Add(self.SliderResetButton,1,wx.EXPAND)
        self.Bind(wx.EVT_BUTTON,self.ResetSliders,self.SliderResetButton)

        #define the initial values of A, B and C (A+B+C=1)
        self.A=1./3.
        self.B=1./3.
        self.C=1./3.

        #call the method to set the sliders to the appropriate places to reflect the values of A, B, C
        self.setSliders()

        #bind moving the sliders to the relevant methods to update the values of the others
        self.Bind(wx.EVT_SLIDER,self.UpdateA,self.sliders[0])
        self.Bind(wx.EVT_SLIDER,self.UpdateB,self.sliders[1])
        self.Bind(wx.EVT_SLIDER,self.UpdateC,self.sliders[2])

        #pie chart panel

        #set up the main sizer
        pieSizer=wx.BoxSizer(wx.VERTICAL)
        self.PiePanel.SetSizer(pieSizer)

        #t4=wx.StaticText(self.PiePanel,label="pie chart")
        #pieSizer.Add(t4,0,wx.LEFT)

        #setup the pie chart figure (transparent background  - facecolor=none)
        self.figure=Figure(facecolor="none")
        self.canvas = FigureCanvas(self.PiePanel, -1, self.figure)
        pieSizer.Add(self.canvas,1,wx.GROW)

        #simulation start button

        self.GoButton=wx.Button(self,label="Start Simulation")
        self.Bind(wx.EVT_BUTTON,self.go,self.GoButton)
        self.WinSizer.Add(self.GoButton,0,wx.EXPAND)


        #assign the main windows's sizer
        self.SetSizer(self.WinSizer)

        #fit all the graphical elements to the window then display the window
        self.Fit()
        self.Show()

        #update the pie chart and the chip graphic (window must be drawn first to get everything positioned properly)
        self.UpdatePie()
        self.UpdateChip()

    def UpdateLocationText(self, locationText, weatherText, locationCode):
        self.text_Location.SetLabel("Location: "+locationText)
        self.weather_Location.SetLabel("Weather: "+weatherText)
        time = int(strftime("%H")) - 3
        self.time_Location.SetLabel("Time: "+("0" if time < 10 else "") +str(time)+"00Z")
        self.weatherLocationCode=locationCode

    #called when the number of cores is altered. This redraws the graphic
    def UpdateChip(self,e=None):
        #get the size of the part of the window that contains the graphic
        (w,h) = self.bitmap1.Size

        #set the width ahd height of the image to be the same (i.e. square)
        if (w>h):
            w=h
        else:
            h=w

        #get the number of cores selected
        cores=self.coresRadio.GetSelection()

        #assign the correct image file to be loaded
        if cores == 0:
            file="chip1.png"
        elif cores == 1:
            file="chip2.png"
        elif cores == 2:
            file="chip3.png"
        else:
            file="chip4.png"

        #load and scale the image, assign it to the bitmap object
        bmp=wx.Image(file, wx.BITMAP_TYPE_ANY).Scale(w,h).ConvertToBitmap()
        self.bitmap1.SetBitmap(bmp)

        #force a redraw of the window to make sure the new image gets positioned correctly
        self.Layout()



    #The method called when the start simulation button is pressed
    def go(self,e=None):
        print("Cores Per Node=",self.coresRadio.GetSelection()+1)
        print("Number of Nodes=",self.NodesSlider.GetValue())
        print("(a,b,c)=(",self.A,",",self.B,",",self.C,")")
        print("GO!")
        self.StartStopSim(None)

    def StartStopSim(self, e):
        # if simulation is not started then start a new simulation
        if not self.servercomm.IsStarted():
            self.writeConfig()

            dlg = wx.MessageDialog(self, "Do you wish to continue?", "This will start a simulation", wx.OK | wx.CANCEL)

            if dlg.ShowModal() == wx.ID_OK:
                # write to config

                config = "config.mcf"
                # config  = "config_nice.mcf"
                self.mainWeatherWindow.StartSim(config)
                self.mainWeatherWindow.playing = False
                # load the first data file
                self.mainWeatherWindow.getdata.value = True
                self.setupWindow.Close()

        # if simulation is started then stop simulation
        else:
            dlg = wx.MessageDialog(self, "Are you sure?", "This will stop the current simulation.", wx.OK | wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:
                self.mainWeatherWindow.StopSim()
                try:
                    for actor in self.mainWeatherWindow.renderer.GetActors():
                        self.mainWeatherWindow.renderer.RemoveActor(actor)
                    self.mainWeatherWindow.actors.clear()
                except:
                    pass
                self.mainWeatherWindow.vtkwidget.GetRenderWindow().Render()

    def writeConfig(self):
        # because the events or something does not work for setting there values, set them here

        weatherInstance=LiveWeather(self.weatherLocationCode)

        f = open('config.mcf', 'w+')

        f.write('global_configuration=outreach_config')

        # pressure settings
        f.write('\nsurface_pressure='+str(weatherInstance.pressure())+'00')
        f.write('\nsurface_reference_pressure='+str(weatherInstance.pressure())+'00')
        f.write('\nfixed_cloud_number=1.0e9')

        # switch sef.timeofyear

        f.write('\nf_force_pl_q=-1.2e-8, -1.2e-8, 0.0, 0.0')

        f.write('\nsurface_latent_heat_flux=200.052')
        f.write('\nsurface_sensible_heat_flux=16.04')

        # amount of water
        f.write('\nz_init_pl_q=0.0, 520.0, 1480., 2000., 3000.')
        f.write('\nf_init_pl_q=17.0e-3, 16.3e-3, 10.7e-3, 4.2e-3, 3.0e-3')

        # wind config

        wind_direction=weatherInstance.wind_direction()[0]
        winforce = weatherInstance.wind_speed() # TODO - negative and direction

        if (wind_direction == "N" or wind_direction == "S"):
            prognotic_wind_field="u"
        else:
            prognotic_wind_field="v"

        if (wind_direction == "S" or wind_direction == "W"): winforce=-winforce
        f.write('\nz_init_pl_'+prognotic_wind_field+'=0.0, 700.0, 3000.')
        f.write('\nf_init_pl_'+prognotic_wind_field+'=' + str(round(winforce*-1.7,2)) + ', ' + str(round(winforce*-1.6,2)) + ', ' + str(winforce*-0.8))

        # temperature settings
        temperature = 273.15 + weatherInstance.temperature()
        tempstr = str(temperature)

        f.write('\nthref0 = ' + tempstr)

        f.write('\nz_init_pl_theta=0.0, 520.0, 1480., 2000., 3000.')

        f.write('\nf_init_pl_theta=' + tempstr + ', ' + tempstr + ', ' + str(temperature+2) + ', ' + str(temperature+5) + ', ' + str(temperature+7))

        # core number and decomposition
        f.write('\ncores_per_pi=' + str(self.coresRadio.GetSelection()+1))
        f.write('\nnum_nodes=' + str(self.NodesSlider.GetValue()))

        if (self.A < 0.2):
            f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-1')
        elif (self.A > 0.2 and self.A < 0.3):
            f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-2')
        elif (self.A > 0.3 and self.A < 0.4):
            f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-3')
        elif (self.A > 0.4 and self.A < 0.5):
            f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-5')
        elif (self.A > 0.5 and self.A < 0.6):
            f.write('\nfftsolver_enabled=.true.\niterativesolver_enabled=.false.')
        else:
            f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-8')

        if (self.B < 0.2):
             f.write('\nadvection_flow_fields=pw\nadvection_theta_field=pw\nadvection_q_fields=pw')
        elif (self.B > 0.2 and self.A < 0.3):
            f.write('\nadvection_flow_fields=pw\nadvection_theta_field=tvd\nadvection_q_fields=pw')
        elif (self.B > 0.3 and self.A < 0.4):
            f.write('\nadvection_flow_fields=pw\nadvection_theta_field=tvd\nadvection_q_fields=tvd')
        else:
            f.write('\nadvection_flow_fields=tvd\nadvection_theta_field=tvd\nadvection_q_fields=tvd')

        if (self.B < 0.3):
            f.write('\ncasim_enabled=.false.\nsimplecloud_enabled=.false.')
        elif (self.B > 0.2 and self.B < 0.3):
            f.write('\ncasim_enabled=.false.\nsimplecloud_enabled=.true.')
        else:
            f.write('\ncasim_enabled=.true.\nsimplecloud_enabled=.false.')

        f.close()


    #colours node blocks when the node selecting slider is moved
    def SetNodes(self,e=None):
        #get the number of nodes selected
        a=self.NodesSlider.GetValue()

        #colour nodes appropriately
        for i in range(16):
            if i < a:
                self.nodes[i].SetBackgroundColour("Green")
            else:
                self.nodes[i].SetBackgroundColour(wx.NullColour)
        self.Refresh()



    #(re)draws the pie chart
    def UpdatePie(self,e=None):
        #get the values of A, B, C
        a=self.A
        b=self.B
        c=self.C

        values=[a,b,c]
        labels=["Pressure","Advection","Microphysics"]
        #clear existing figure
        self.figure.clf()

        #redraw figure
        self.axes=self.figure.add_subplot(111)
        self.axes.pie(values,labels=labels)
        self.axes.axis("equal")
        self.canvas.draw()
        self.canvas.Refresh()

    #resets the sliders to the default values
    def ResetSliders(self,e=None):
        self.A=1./3.
        self.B=1./3.
        self.C=1./3.

        self.setSliders()

        #redraw the pie chart
        self.UpdatePie()


    #methods called when the pie chart sliders are adjusted
    def UpdateA(self,e=None):
        self.UpdateABC(0,self.sliders[0].GetValue())

    def UpdateB(self,e=None):
        self.UpdateABC(1,self.sliders[1].GetValue())

    def UpdateC(self,e=None):
        self.UpdateABC(2,self.sliders[2].GetValue())


    #sets the sliders to the values of a, b, c
    def setSliders(self):
        a=int(self.A*100)
        b=int(self.B*100)
        c=int(self.C*100)

        self.sliders[0].SetValue(a)
        self.sliders[1].SetValue(b)
        self.sliders[2].SetValue(c)

    #given an updated slider (number i, value a), will alter the other two sliders (b and c) to ensure a+b+c=1
    def UpdateABC(self,i,a):

        a=float(a)/100.

        #control how a,b,c map to A,B,C (the actual sliders)
        if (i == 0):
            b=self.B
            c=self.C
        elif (i == 1):
            b=self.C
            c=self.A
        else:
            b=self.A
            c=self.B

        #A+B+C should equal 1, but it won't as 'a' has been updated
        new1 = a+b+c
        #print("new1=",1)

        #find the amount we need to adjust b and c by to get back to a+b+c=1
        diff = 1.0-new1

        #divide this amount up proportionately between b and c
        db = diff * b/(b+c)
        dc = diff * c/(b+c)

        #update b and c
        b=b+db
        c=c+dc


        #assign new values
        if (i == 0):
            self.A=a
            self.B=b
            self.C=c
        elif (i == 1):
            self.B=a
            self.C=b
            self.A=c
        else:
            self.A=b
            self.B=c
            self.C=a

        #move sliders as required and update the pie chart
        self.setSliders()
        self.UpdatePie()


class TabAdvanced(wx.Panel):
    def __init__(self, parent, title, demo, servercomm, mainWeatherWindow):
        wx.Panel.__init__(self, parent)

        self.demo = demo
        self.mainWeatherWindow = mainWeatherWindow
        self.servercomm = servercomm
        self.title = title

        # set up sizers that allow you to position window elements easily
        # sizer for buttons (align buttons vertically)
        self.buttonsizer = wx.BoxSizer(wx.VERTICAL)
        # sizer for rewind, step forward, step back and fast forward buttons
        self.weesizer = wx.BoxSizer(wx.HORIZONTAL)

        # create 'array' of buttons
        self.buttons = []

        self.buttons.append(wx.Button(self, label='Start Simulation'))
        self.buttons.append(wx.Button(self, label='Play'))
        self.buttons.append(wx.Button(self, label='<<'))
        self.buttons.append(wx.Button(self, label='<'))
        self.buttons.append(wx.Button(self, label='>'))
        self.buttons.append(wx.Button(self, label='>>'))

        self.buttons.append(wx.Button(self, label='Summer'))
        self.buttons.append(wx.Button(self, label='Autumn'))
        self.buttons.append(wx.Button(self, label='Winter'))
        self.buttons.append(wx.Button(self, label='Spring'))

        self.buttons.append(wx.Button(self, label='Toggle Grid'))

        self.buttons.append(wx.Button(self, label='Low'))
        self.buttons.append(wx.Button(self, label='Middle'))
        self.buttons.append(wx.Button(self, label='High'))

        # bind button clicks (wx.EVT_BUTTONT) to methods
        self.Bind(wx.EVT_BUTTON, self.StartStopSim, self.buttons[0])
        self.Bind(wx.EVT_BUTTON, self.play, self.buttons[1])
        self.Bind(wx.EVT_BUTTON, self.rewind, self.buttons[2])
        self.Bind(wx.EVT_BUTTON, self.stepback, self.buttons[3])
        self.Bind(wx.EVT_BUTTON, self.stepforward, self.buttons[4])
        self.Bind(wx.EVT_BUTTON, self.fastforward, self.buttons[5])

        self.Bind(wx.EVT_BUTTON, self.togglegrid, self.buttons[10])

        self.Bind(wx.EVT_BUTTON, self.setSummer, self.buttons[6])
        self.Bind(wx.EVT_BUTTON, self.setAutumn, self.buttons[7])
        self.Bind(wx.EVT_BUTTON, self.setWinter, self.buttons[8])
        self.Bind(wx.EVT_BUTTON, self.setSpring, self.buttons[9])

        self.Bind(wx.EVT_BUTTON, self.setWaterLow, self.buttons[11])
        self.Bind(wx.EVT_BUTTON, self.setWaterMiddle, self.buttons[12])
        self.Bind(wx.EVT_BUTTON, self.setWaterHigh, self.buttons[13])

        # Adding dropdown menu and text fields for core numbers and decomposition topology
        self.coretext1 = wx.StaticText(self, label="Cores per Pi:")
        self.coretext2 = wx.StaticText(self, label="Cores depth:")
        self.coretext3 = wx.StaticText(self, label="Cores width:")

        self.corenum = wx.SpinCtrl(self, id=wx.ID_ANY, value='1')  # number of cores used per Pi
        self.corenum.SetRange(1, 4)
        self.columnsizex = wx.SpinCtrl(self, id=wx.ID_ANY, value='1')  # number of columns each core gets in X
        self.columnsizey = wx.SpinCtrl(self, id=wx.ID_ANY, value='1')  # number of columns each core gets in Y

        sampleList = ['Iterative', 'FFT']
        self.solver = wx.ComboBox(self, id=wx.ID_ANY, choices=sampleList, value='Iterative')

        self.Bind(EVT_NUM, self.setCoreNum, self.corenum)

        # add a slider to control refresh rate
        # text box to display slider value
        self.text = wx.StaticText(self, label="Refreshrate =...")
        self.slider = wx.Slider(self, wx.ID_ANY, value=5, minValue=1, maxValue=20)  # must be integer
        self.sliderdt = 0.1  # slider interval
        self.refreshrate = (self.slider.GetValue() * self.sliderdt)
        str = "Refresh rate: %3.1f" % self.refreshrate
        self.text.SetLabel(str)
        # bind changing slider value to UpdateSlider method
        self.Bind(wx.EVT_SCROLL, self.UpdateFrameSlider, self.slider)

        # add a slider to control Wind power
        self.windtext = wx.StaticText(self, label="Wind power: ...")
        self.windslider = wx.Slider(self, wx.ID_ANY, value=5, minValue=1, maxValue=20)  # must be integer
        str = "Wind power: %3.1f" % self.windslider.GetValue()
        self.windtext.SetLabel(str)
        self.Bind(wx.EVT_SCROLL, self.UpdateWindSlider, self.windslider)

        # add a slider to control Temperature
        self.temptext = wx.StaticText(self, label="Temperature: ...")
        self.tempslider = wx.Slider(self, wx.ID_ANY, value=25, minValue=0, maxValue=40)  # must be integer
        str = "Temperature: %3.1f °C" % self.tempslider.GetValue()
        self.temptext.SetLabel(str)
        self.Bind(wx.EVT_SCROLL, self.UpdateTempSlider, self.tempslider)

        # add a slider to control Pressure
        self.pressuretext = wx.StaticText(self, label="Pressure: ...")
        self.pressureslider = wx.Slider(self, wx.ID_ANY, value=100000, minValue=80000, maxValue=120000)  # integer
        str = "Pressure: %3.1f" % self.pressureslider.GetValue()
        self.pressuretext.SetLabel(str)
        self.Bind(wx.EVT_SCROLL, self.UpdatePressureSlider, self.pressureslider)

        # add buttons to the button (vertical) sizer
        self.buttonsizer.Add(self.buttons[0], 1, wx.EXPAND)
        self.buttonsizer.Add(self.buttons[1], 1, wx.EXPAND)

        # add <<, <, > and >> buttons to the weesizer
        self.weesizer.Add(self.buttons[2], 0.5, wx.EXPAND)
        self.weesizer.Add(self.buttons[3], 0.5, wx.EXPAND)
        self.weesizer.Add(self.buttons[4], 0.5, wx.EXPAND)
        self.weesizer.Add(self.buttons[5], 0.5, wx.EXPAND)

        # add weesizer to the button sizer
        self.buttonsizer.Add(self.weesizer, 1, wx.EXPAND)

        self.buttonsizer.Add(self.buttons[10], 1, wx.EXPAND)

        self.buttonsizer.Add((10, 30))

        # add slider to the sizer
        self.buttonsizer.Add(self.windtext, 1, wx.EXPAND)
        self.buttonsizer.Add(self.windslider, 1, wx.EXPAND)

        self.buttonsizer.Add(self.temptext, 1, wx.EXPAND)
        self.buttonsizer.Add(self.tempslider, 1, wx.EXPAND)

        self.buttonsizer.Add(self.pressuretext, 1, wx.EXPAND)
        self.buttonsizer.Add(self.pressureslider, 1, wx.EXPAND)

        self.buttonsizer.Add((10, 30))

        self.timeofyeartext = wx.StaticText(self, label="Time of year: ")
        self.buttonsizer.Add(self.timeofyeartext, 1, wx.EXPAND)

        self.timeofyearsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.timeofyearsizer.Add(self.buttons[6], 0.5, wx.EXPAND)
        self.timeofyearsizer.Add(self.buttons[7], 0.5, wx.EXPAND)
        self.timeofyearsizer.Add(self.buttons[8], 0.5, wx.EXPAND)
        self.timeofyearsizer.Add(self.buttons[9], 0.5, wx.EXPAND)
        self.buttonsizer.Add(self.timeofyearsizer, 1, wx.EXPAND)

        self.watertext = wx.StaticText(self, label="Amount of water: ")
        self.buttonsizer.Add(self.watertext, 1, wx.EXPAND)

        self.watersizer = wx.BoxSizer(wx.HORIZONTAL)
        self.watersizer.Add(self.buttons[11], 1, wx.EXPAND)
        self.watersizer.Add(self.buttons[12], 1, wx.EXPAND)
        self.watersizer.Add(self.buttons[13], 1, wx.EXPAND)
        self.buttonsizer.Add(self.watersizer, 1, wx.EXPAND)

        self.buttonsizer.Add((10, 30))

        self.coreconfixtextsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.coreconfixtextsizer.Add(self.coretext1, 1, wx.EXPAND)
        self.coreconfixtextsizer.Add(self.coretext2, 1, wx.EXPAND)
        self.coreconfixtextsizer.Add(self.coretext3, 1, wx.EXPAND)
        self.buttonsizer.Add(self.coreconfixtextsizer, 1, wx.EXPAND)

        self.coreconfigsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.coreconfigsizer.Add(self.corenum, 1, wx.EXPAND)
        self.coreconfigsizer.Add(self.columnsizex, 1, wx.EXPAND)
        self.coreconfigsizer.Add(self.columnsizey, 1, wx.EXPAND)
        self.buttonsizer.Add(self.coreconfigsizer, 1, wx.EXPAND)
        self.buttonsizer.Add((10, 30))

        self.solvertext = wx.StaticText(self, label="Method: ")
        self.buttonsizer.Add(self.solvertext, 1, wx.EXPAND)

        self.buttonsizer.Add(self.solver, 1, wx.EXPAND)

        # add some vertical space
        self.buttonsizer.Add((10, 150))

        # add slider to the sizer
        self.buttonsizer.Add(self.text, 1, wx.EXPAND)
        self.buttonsizer.Add(self.slider, 1, wx.EXPAND)

        # text at bottom that displays the current frame number
        self.logger = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.buttonsizer.Add(self.logger, 1, wx.EXPAND)

        # disable buttons (as no simulation is running at startup so the buttons are useless)
        self.buttons[1].Enable(False)
        self.buttons[2].Enable(False)
        self.buttons[3].Enable(False)
        self.buttons[4].Enable(False)
        self.buttons[5].Enable(False)

        self.buttons[10].Enable(False)

        # attach main sizer to the window
        self.SetSizer(self.buttonsizer)
        self.SetAutoLayout(1)
        self.buttonsizer.Fit(self)

        #self.start_interactor()

    def StartStopSim(self, e):
        # if simulation is not started then start a new simulation
        if not self.servercomm.IsStarted():
            self.writeConfig()

            dlg = wx.MessageDialog(self, "Do you wish to continue?", "This will start a simulation", wx.OK | wx.CANCEL)

            if dlg.ShowModal() == wx.ID_OK:
                # write to config


                config = "config.mcf"
                # config  = "config_nice.mcf"
                self.start_sim(config)

                self.buttons[0].SetLabel("Stop Simulation")

                self.buttons[1].Enable(True)
                self.buttons[2].Enable(True)
                self.buttons[3].Enable(True)
                self.buttons[4].Enable(True)
                self.buttons[5].Enable(True)
                self.buttons[10].Enable(True)

                self.mainWeatherWindow.playing = False

                # load the first data file
                self.mainWeatherWindow.getdata.value = True

        # if simulation is started then stop simulation
        else:

            dlg = wx.MessageDialog(self, "Are you sure?", "This will stop the current simulation.", wx.OK | wx.CANCEL)

            if dlg.ShowModal() == wx.ID_OK:

                self.stop_sim()

                self.buttons[0].SetLabel("Start Simulation")

                self.logger.SetValue("")

                self.playing = False

                self.buttons[1].SetLabel("Play")
                self.buttons[1].Enable(False)
                self.buttons[2].Enable(False)
                self.buttons[3].Enable(False)
                self.buttons[4].Enable(False)
                self.buttons[5].Enable(False)

                self.buttons[10].Enable(False)

                try:
                    for actor in self.mainWeatherWindow.renderer.GetActors():
                        self.mainWeatherWindow.renderer.RemoveActor(actor)
                    self.mainWeatherWindow.actors.clear()
                except:
                    pass
                self.mainWeatherWindow.vtkwidget.GetRenderWindow().Render()

    def UpdateWindSlider(self, e):
        str = "Wind power: %3.1f" % self.windslider.GetValue()
        self.windtext.SetLabel(str)

    def UpdateTempSlider(self, e):
        str = "Temperature: %3.1f °C" % self.tempslider.GetValue()
        self.temptext.SetLabel(str)

    def UpdatePressureSlider(self, e):
        str = "Pressure: %3.1f" % self.pressureslider.GetValue()
        self.pressuretext.SetLabel(str)

    def setSummer(self, e):
        self.buttons[6].Enable(False)
        self.buttons[7].Enable(True)
        self.buttons[8].Enable(True)
        self.buttons[9].Enable(True)

        self.timeofyear = 'Summer'

    def setAutumn(self, e):
        self.buttons[6].Enable(True)
        self.buttons[7].Enable(False)
        self.buttons[8].Enable(True)
        self.buttons[9].Enable(True)

        self.timeofyear = 'Autumn'

    def setWinter(self, e):
        self.buttons[6].Enable(True)
        self.buttons[7].Enable(True)
        self.buttons[8].Enable(False)
        self.buttons[9].Enable(True)

        self.timeofyear = 'Winter'

    def setSpring(self, e):
        self.buttons[6].Enable(True)
        self.buttons[7].Enable(True)
        self.buttons[8].Enable(True)
        self.buttons[9].Enable(False)

        self.timeofyear = 'Spring'

    def setWaterLow(self, e):
        self.buttons[11].Enable(False)
        self.buttons[12].Enable(True)
        self.buttons[13].Enable(True)

        self.waterlevel = 1

    def setWaterMiddle(self, e):
        self.buttons[11].Enable(True)
        self.buttons[12].Enable(False)
        self.buttons[13].Enable(True)

        self.waterlevel = 2

    def setWaterHigh(self, e):
        self.buttons[11].Enable(True)
        self.buttons[12].Enable(True)
        self.buttons[13].Enable(False)

        self.waterlevel = 3

    def writeConfig(self):

        # because the events or something does not work for setting there values, set them here
        self.numberofcores = self.corenum.GetValue()
        self.columnsinX = self.columnsizex.GetValue()
        self.columnsinY = self.columnsizey.GetValue()

        f = open('config.mcf', 'w+')

        f.write('global_configuration=outreach_config')

        # pressure settings
        f.write('\nsurface_pressure=' + str(self.pressureslider.GetValue()))
        f.write('\nsurface_reference_pressure=' + str(self.pressureslider.GetValue()))
        f.write('\nfixed_cloud_number=1.0e9')

        # switch sef.timeofyear

        f.write('\nf_force_pl_q=-1.2e-8, -1.2e-8, 0.0, 0.0')

        f.write('\nsurface_latent_heat_flux=200.052')
        f.write('\nsurface_sensible_heat_flux=16.04')

        # amount of water
        f.write('\nz_init_pl_q=0.0, 520.0, 1480., 2000., 3000.')
        f.write('\nf_init_pl_q=17.0e-3, 16.3e-3, 10.7e-3, 4.2e-3, 3.0e-3')

        # wind config

        winforce = self.windslider.GetValue()

        f.write('\nz_init_pl_u=0.0, 700.0, 3000.')
        f.write('\nf_init_pl_u=' + str(round(winforce*-1.7,2)) + ', ' + str(round(winforce*-1.6,2)) + ', ' + str(winforce*-0.8))

        # temperature settings
        tempstr = str(self.tempslider.GetValue() + 273.15)
        temperature = self.tempslider.GetValue() + 273.15

        f.write('\nthref0 = ' + tempstr)

        f.write('\nz_init_pl_theta=0.0, 520.0, 1480., 2000., 3000.')

        f.write('\nf_init_pl_theta=' + tempstr + ', ' + tempstr + ', ' + str(temperature+2) + ', ' + str(temperature+5) + ', ' + str(temperature+7))

        # core number and decomposition
        f.write('\ncores_per_pi=' + str(self.corenum.GetValue()))
        f.write('\nnum_px=' + str(self.columnsizex.GetValue()))
        f.write('\nnum_py=' + str(self.columnsizey.GetValue()))

        if self.solver.GetValue() == 'Iterative':
            f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.')
        else:
            f.write('\nfftsolver_enabled=.true.\niterativesolver_enabled=.false.')

        f.close()


    def setCoreNum(self):
        self.numberofcores = self.corenum.GetValue()

    def setColumnSizeX(self):
        self.columnsinX = self.columnsizex.GetValue()

    def setColumnSizeY(self):
        self.columnsinY = self.columnsizey.GetValue()

    def play(self, e):

        if not self.mainWeatherWindow.playing:  # play
            self.mainWeatherWindow.getdata.value = True
            self.buttons[1].SetLabel("Pause")
            self.mainWeatherWindow.playing = True
        else:  # pause
            self.mainWeatherWindow.getdata.value = False
            self.buttons[1].SetLabel("Play")
            self.mainWeatherWindow.playing = False

    # Go back to the first frame
    def rewind(self, e):

        self.mainWeatherWindow.playing = False  # stop playing (if it is playing)
        self.mainWeatherWindow.frameno.value = 0
        self.mainWeatherWindow.getdata.value = True
        self.buttons[1].SetLabel("Play")
        self.rainmass = 0

    # go to the latest frame
    def fastforward(self, e):

        self.mainWeatherWindow.playing = False  # stop playing (if it is playing)
        self.mainWeatherWindow.frameno.value = self.mainWeatherWindow.nfiles.value - 1
        self.mainWeatherWindow.getdata.value = True
        self.buttons[1].SetLabel("Play")

    # step one frame backwards
    def stepback(self, e):

        self.mainWeatherWindow.playing = False  # stop playing (if it is playing)
        self.mainWeatherWindow.frameno.value = self.mainWeatherWindow.CurrentFrame - 1
        self.mainWeatherWindow.getdata.value = True
        self.buttons[1].SetLabel("Play")

    # step one frame forwards
    def stepforward(self, e):

        self.mainWeatherWindow.playing = False  # stop playing (if it is playing)
        self.mainWeatherWindow.frameno.value = self.c + 1
        self.mainWeatherWindow.getdata.value = True
        self.buttons[1].SetLabel("Play")

    def togglegrid(self, e):
        if self.decompositiongrid is True:
            self.decompositiongrid = False
        else:
            self.decompositiongrid = True

        if self.mainWeatherWindow.timer.IsRunning():
            self.mainWeatherWindow.timer.Stop()
            self.mainWeatherWindow.timer.Start()

    def UpdateFrameSlider(self, e):
        # this method runs every time the slider is moved. It sets the new refreshrate, updates the refreshrate GUI
        # text, and stops and starts the timer with the new framerate (if it is on)

        # get new framerate
        self.refreshrate = (self.slider.GetValue() * self.sliderdt)
        # update framerate text
        str = "Refresh rate: %3.1f s" % self.refreshrate
        self.text.SetLabel(str)

        if self.mainWeatherWindow.timer.IsRunning():
            self.mainWeatherWindow.timer.Stop()
            self.mainWeatherWindow.timer.Start(self.refreshrate * 1000)

    def start_interactor(self):
        self.mainWeatherWindow.StartInteractor(None)

    def start_sim(self, config):
        self.mainWeatherWindow.StartSim(config)

    def stop_sim(self):
        self.mainWeatherWindow.StopSim()

    def timer_callback(self, e):
        self.mainWeatherWindow.TimerCallback(None)


class TabLocation(wx.Panel):
    def __init__(self, parent, mainTabAdvanced, setupTab, setWidth):
        wx.Panel.__init__(self, parent)

        self.mainTabAdvanced = mainTabAdvanced
        self.setupTab=setupTab
        self.parent=parent

        maxWidth, maxHeight= wx.GetDisplaySize()

        heightCorrector=100
        maxHeight-=heightCorrector
        # Set up background image of the UK:
        self.MaxImageSize = 2400
        self.Image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(self.MaxImageSize, self.MaxImageSize))
        Img = wx.Image(imageFile, wx.BITMAP_TYPE_JPEG)
        Img = Img.Scale(maxHeight/1.4, maxHeight)
        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.Image.SetBitmap(wx.BitmapFromImage(Img))

        # Using a Sizer to handle the layout: I never like to use absolute postioning
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.Image, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        self.SetSizerAndFit(box)

        # Get the size of the image.....attempting to reposition the buttons depending on the window size.
        W, H = self.Image.GetSize()

        print maxWidth

        weatherBtnSizes=40

        # Set up image button for Edinburgh(city):
        bmp = wx.Bitmap(self.weather_data(edinburgh, 3166)[0], wx.BITMAP_TYPE_ANY)
        image = wx.ImageFromBitmap(bmp)
        image = image.Scale(weatherBtnSizes-10, weatherBtnSizes-10, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.BitmapFromImage(image)
        self.button1 = wx.BitmapButton(self, -1, bmp, size = (weatherBtnSizes, weatherBtnSizes), pos=((W/1.96) + ((setWidth-W)/2), (H/3.4 + heightCorrector)))
        self.Bind(wx.EVT_BUTTON, self.go, self.button1)
        self.button1.Bind(wx.EVT_ENTER_WINDOW, self.changeCursor)
        self.button1.Bind(wx.EVT_ENTER_WINDOW, self.changeCursorBack)
        self.button1.SetDefault()

        # Set up image button for Highlands(mountains):
        bmp = wx.Bitmap(self.weather_data(highlands, 3047)[0], wx.BITMAP_TYPE_ANY)
        image = wx.ImageFromBitmap(bmp)
        image = image.Scale(weatherBtnSizes-10, weatherBtnSizes-10, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.BitmapFromImage(image)
        self.button2 = wx.BitmapButton(self, -1, bmp, size=(weatherBtnSizes, weatherBtnSizes), pos=((W / 2.3) + ((setWidth-W)/2), (H / 6.7 + heightCorrector)))
        self.Bind(wx.EVT_BUTTON, self.go, self.button2)
        self.button2.Bind(wx.EVT_ENTER_WINDOW, self.changeCursor)
        self.button2.Bind(wx.EVT_ENTER_WINDOW, self.changeCursorBack)
        self.button2.SetDefault()

        # Set up image button for London(city+river):
        bmp = wx.Bitmap(self.weather_data(london, 3772)[0], wx.BITMAP_TYPE_ANY)
        image = wx.ImageFromBitmap(bmp)
        image = image.Scale(weatherBtnSizes-10, weatherBtnSizes-10, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.BitmapFromImage(image)
        self.button3 = wx.BitmapButton(self, -1, bmp, size=(weatherBtnSizes, weatherBtnSizes), pos=((W / 1.4) + ((setWidth-W)/2), (H / 1.55 + heightCorrector)))
        self.Bind(wx.EVT_BUTTON, self.go, self.button3)
        self.button3.Bind(wx.EVT_ENTER_WINDOW, self.changeCursor)
        self.button3.Bind(wx.EVT_ENTER_WINDOW, self.changeCursorBack)
        self.button3.SetDefault()

        # Set up image button for Cornwall(seaside):
        bmp = wx.Bitmap(self.weather_data(cornwall, 3808)[0], wx.BITMAP_TYPE_ANY)
        image = wx.ImageFromBitmap(bmp)
        image = image.Scale(weatherBtnSizes-10, weatherBtnSizes-10, wx.IMAGE_QUALITY_HIGH)
        bmp = wx.BitmapFromImage(image)
        self.button4 = wx.BitmapButton(self, -1, bmp, size=(weatherBtnSizes, weatherBtnSizes), pos=((W / 2.52) + ((setWidth-W)/2), (H / 1.33 + heightCorrector)))
        self.Bind(wx.EVT_BUTTON, self.go, self.button4)
        self.button4.Bind(wx.EVT_ENTER_WINDOW, self.changeCursor)
        self.button4.Bind(wx.EVT_ENTER_WINDOW, self.changeCursorBack)
        self.button4.SetDefault()

    def go(self, event):
        if (event.GetEventObject() == self.button1):
            self.setupTab.UpdateLocationText("Edinburgh", self.generateWeatherText(3166), 3166)
        elif (event.GetEventObject() == self.button2):
            self.setupTab.UpdateLocationText("Highlands", self.generateWeatherText(3047), 3047)
        elif (event.GetEventObject() == self.button3):
            self.setupTab.UpdateLocationText("London", self.generateWeatherText(3772), 3772)
        elif (event.GetEventObject() == self.button4):
            self.setupTab.UpdateLocationText("Cornwall", self.generateWeatherText(3808), 3808)
        self.parent.SetSelection(1)
        #self.mainTabAdvanced.StartStopSim(None)

    def generateWeatherText(self, numb):
        weatherInstance=LiveWeather(numb)
        weatherString=""
        live=weatherInstance.hour_weather()
        if live <= 1:
            weatherString+="Sunny"
        elif 9 > live > 1:
            weatherString+="Cloudy"
        else:
            weatherString+="Raining"
        weatherString+=" "+str(weatherInstance.wind_speed())+"m/s "+weatherInstance.wind_direction()+" "+str(weatherInstance.pressure())+"hpa "+str(weatherInstance.temperature())+"C "+str(weatherInstance.visibility())+"m"
        return weatherString


    def weather_data(self, place, numb):
        live = LiveWeather(numb).hour_weather()
        place = place
        if live <= 1:
            place.append(sun)
        elif 9 > live > 1:
            place.append(cloud)
        else:
            place.append(rain)
        return place

    # Change the cursor to a hand every time the cursor goes over a button
    def changeCursor(self, event):
        myCursor = wx.StockCursor(wx.CURSOR_HAND)
        self.button1.SetCursor(myCursor)
        self.button2.SetCursor(myCursor)
        self.button3.SetCursor(myCursor)
        self.button4.SetCursor(myCursor)
        event.Skip()

    # Change the cursor back to the arrow every time the cursor leaves a button
    def changeCursorBack(self, event):
        myCursor = wx.StockCursor(wx.CURSOR_ARROW)
        self.button1.SetCursor(myCursor)
        self.button2.SetCursor(myCursor)
        self.button3.SetCursor(myCursor)
        self.button4.SetCursor(myCursor)
        event.Skip()

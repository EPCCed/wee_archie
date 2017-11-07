# -*- coding: utf-8 -*-
import client
import wx
from wx.lib.masked import *
import vtk
import sys

import numpy as np

import matplotlib
matplotlib.use("WXAgg")

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from time import strftime
import random

# New module to import the live weather forcast
from weather_live import LiveWeather

# select the UI abstract superclass to derive from
UI = client.AbstractvtkUI

imageFile = 'uk.jpg'
rain = 'resizedrain.jpg'
cloud = 'resizedcloud.jpg'
sun = 'resizedsun.jpg'
scoreFile='scores'

edinburgh = []
london = []
cornwall = []
highlands = []

EDINBURGH_LOCATION=1
LONDON_LOCATION=2
CORNWALL_LOCATION=3
HIGHLANDS_LOCATION=4

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

        try:
            self.scores=np.loadtxt(scoreFile, delimiter=',')
        except:
            self.scores=np.array([[0,0]], dtype=int)

        menubar = wx.MenuBar()
        playbackMenu = wx.Menu()
        self.playpauseitem = playbackMenu.Append(wx.ID_ANY, 'Pause', 'Pause playback')
        cease = playbackMenu.Append(wx.ID_ANY, 'Stop', 'Stop simulation')

        fileMenu = wx.Menu()
        settings = fileMenu.Append(wx.ID_ANY, 'Settings', 'Open settings window')
        scoreboard = fileMenu.Append(wx.ID_ANY, 'Score board', 'Open scoreboard window')
        self.internalWeatherCheckItem=fileMenu.AppendCheckItem(wx.ID_ANY, 'Internal weather', 'Use internal weather')
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
        self.Bind(wx.EVT_MENU, self.OpenScoreboard, scoreboard)
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

        self.OpenWindow()

    def OpenScoreboard(self, event=None):
        self.showScoreBoard(None, None)

    def showScoreBoard(self, time_modelled, accuracy_achieved):
        newWindow=FinishedWindow(self, time_modelled, accuracy_achieved)
        newWindow.Show()
        if (not (time_modelled is None or accuracy_achieved is None)):
            self.scores=np.append(self.scores, [[accuracy_achieved, time_modelled]], axis=0)
            np.savetxt(scoreFile, self.scores, delimiter=',', fmt='%d')

    # Function to call NewWindow class to allow a button to open it.
    def OpenWindow(self, event=None):
        self.new = NewWindow(self, -1, self.title, self.demo, self.servercomm, self)
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
        self.GetLatestFrame=True
        UI.TimerCallback(self, e)

        #self.logger.SetValue("Frame %d of %d" % (self.CurrentFrame, self.nfiles.value - 1))

    def OnClose(self, e):
        UI.OnClose(self, e)
        try:
            self.StopSim()
        except:
            pass
        sys.exit()

    # ----------------------------------------------------------------------
    # ------------- New methods specific to demo go here -------------------
    # ----------------------------------------------------------------------

class FinishedWindow(wx.Frame):
    def __init__(self, parent, time_modelled, accuracy_achieved):
        #W,H= wx.GetDisplaySize()
        #height=0.9*H
        #width=height*(9./14.)
        wx.Frame.__init__(self, parent, -1, 'Score board')
        wx.Frame.CenterOnScreen(self)

        self.parent=parent

        p = wx.Panel(self)
        sizer = wx.BoxSizer()

        self.WinSizer=wx.BoxSizer(wx.VERTICAL)

        self.LocationPanel=wx.Panel(self,style=wx.BORDER_SUNKEN)
        self.WinSizer.Add(self.LocationPanel,1,wx.EXPAND | wx.ALL,border=5)

        locationSizer=wx.BoxSizer(wx.VERTICAL)
        self.LocationPanel.SetSizer(locationSizer)

        # Create plot
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, axisbg="1.0")

        max_x=0

        #get previous score data and compare to current run
        x=[]
        y=[]

        for xx,yy in parent.scores:
            x.append(xx)
            y.append(yy)

        #sort the data and reverse (so the top score is at position 0 of the array)

        x.sort()
        y.sort()

        x.reverse()
        y.reverse()

        #now go through each score list and find where the current score resides on the scoreboard

        #get time position
        tplace=1

        print("Time:")
        for t in y:
            if t < time_modelled:
                break
            tplace+=1

        #get accuracy position
        aplace=1
        for a in x:
            if a < accuracy_achieved:
                break
            aplace+=1



        for data in parent.scores:
            if (data[0] > 0 and data[1] > 0):
                ax.scatter(data[0], data[1], alpha=0.8, c="black", edgecolors='none',marker='x', s=20)
                if (data[1] > max_x): max_x=data[1]

        if (not (time_modelled is None or accuracy_achieved is None)):
            ax.scatter(accuracy_achieved, time_modelled, alpha=1.0, c="green", edgecolors='none', s=200)
            if (time_modelled > max_x): max_x=time_modelled

        plt.title('Score board')
        plt.xlabel('Accuracy (%)')
        plt.ylabel('Minutes simulated')
        ax.text(5,max_x+5,"Position "+str(tplace)+" out of "+str(len(y)+1)+" for minutes simulated")
        ax.text(5,max_x+10,"Position "+str(aplace)+" out of "+str(len(x)+1)+" for accuracy achieved")
        ax.text(5,max_x+15,str(int(time_modelled))+" minutes simulated, with an accuracy of "+str(round(accuracy_achieved,1))+"%")
        plt.xlim(0, 100)
        plt.ylim(0, max_x+20)



        self.canvas = FigureCanvas(self.LocationPanel, -1, fig)
        locationSizer.Add(self.canvas,1,wx.GROW | wx.EXPAND | wx.ALL)

        #assign the main windows's sizer
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetSizer(self.WinSizer)
        self.Show()
        self.Fit()

    def OnClose(self, event):
        self.parent.OpenWindow()
        self.Destroy()

# Class to create a new window for the "settings".
class NewWindow(wx.Frame):
    def __init__(self, parent, id, title, demo, servercomm, mainWeatherWindow):
        W,H= wx.GetDisplaySize()
        height=0.9*H
        width=height*(9./14.)
        wx.Frame.__init__(self, parent, id, 'Settings', size=(width, height))
        wx.Frame.CenterOnScreen(self)

        self.parent=parent
        self.weatherLocationCode=3166
        self.mainWeatherWindow=mainWeatherWindow

        self.demo = demo
        self.servercomm = servercomm
        self.title = title

        # Create a panel and notebook (tabs holder)
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        #we want to draw the window on screen first to make sure everything is sized coreectly
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)

        p.SetSizer(sizer)

        self.Show()
        self.Fit()

        # Create the tab windows
        #self.tab3 = TabAdvanced(nb, self.title, self.demo, self.servercomm, mainWeatherWindow)
        self.tab2 = TabSetup(nb, self)
        self.tab3= TabWeather(nb, self)
        self.tab1 = TabLocation(nb, self.tab3, self.tab2, width, height, self)

        # Add the windows to tabs and name them.
        nb.AddPage(self.tab1, "Location")

        #make sure layout of the tab2 is correct
        self.tab2.Layout()
        self.tab3.Layout()

        #redraw the chip image and the pie chart to make sure they display correctly
        self.tab2.UpdateChip()
        self.tab3.UpdatePie()

        self.tab2.Hide()
        self.tab3.Hide()

    def StartStopSim(self, e):

        if (self.demo.init_scene):
            self.demo.init_scene=False
            self.demo.accuracy_achieved=0.0
            self.demo.accuracy_ticks=0
            self.demo.resetScene(self.mainWeatherWindow)

        # if simulation is not started then start a new simulation
        if self.servercomm.IsStarted(): self.mainWeatherWindow.StopSim()

        self.writeConfig()
        config = "config.mcf"
        self.mainWeatherWindow.StartSim(config)
        self.mainWeatherWindow.playing = True
        # load the first data file
        self.mainWeatherWindow.getdata.value = True
        self.Close()

    def writeConfig(self):

        #first of all, tell the demo to render the ground:

        self.demo.RenderFrame(self.parent,None,landscape_only=True)

        # because the events or something does not work for setting there values, set them here

        weatherInstance=LiveWeather(self.weatherLocationCode, use_internal_values=self.mainWeatherWindow.internalWeatherCheckItem.IsChecked())

        if (self.weatherLocationCode == 3166):
            selected_location=EDINBURGH_LOCATION
        elif (self.weatherLocationCode == 3047):
            selected_location=HIGHLANDS_LOCATION
        elif (self.weatherLocationCode == 3772):
            selected_location=LONDON_LOCATION
        elif (self.weatherLocationCode == 3808):
            selected_location=CORNWALL_LOCATION

        self.demo.setSubmittedParameters(weatherInstance.target_time(), weatherInstance.wind_compass_direction(), weatherInstance.wind_speed(), weatherInstance.wind_gust(),
                weatherInstance.pressure(), weatherInstance.temperature(), weatherInstance.hour_weather(), self.tab2.accuracySlider.GetValue())

        f = open('config.mcf', 'w+')

        f.write('global_configuration=outreach_config')

        # pressure settings
        f.write('\nsurface_pressure='+str(weatherInstance.pressure())+'00.0')
        f.write('\nsurface_reference_pressure='+str(weatherInstance.pressure())+'00.0')
        f.write('\nfixed_cloud_number=1.0e9') # 9

        self.demo.reference_pressure=weatherInstance.pressure()*100

        # switch sef.timeofyear

        f.write('\nl_force_pl_q=.false.')

        f.write('\nz_force_pl_q=0.0, 300.0, 500.0, 1000.')
        f.write('\nf_force_pl_q=-10.0, 0.0, 4.2e-3, 0.0')
        #f.write('\nf_force_pl_q=17.0e-3, 16.3e-3, 10.7e-3, 4.2e-3, 3.0e-3')

        f.write('\nl_constant_forcing_theta=.false.\nl_subs_pl_theta=.true.\nl_constant_forcing_q=.false.\nl_subs_pl_q=.false.')

        f.write('\nz_subs_pl=0.0, 1500.0, 2100.0, 3000.')
        f.write('\nf_subs_pl=0.0, -0.0065, 0.0, 10.7e-3')

        if (selected_location==CORNWALL_LOCATION):
            f.write('\nsurface_latent_heat_flux=1000.0')
            f.write('\nsurface_sensible_heat_flux=100.0')

        # amount of water
        f.write('\nl_init_pl_q=.true.')

        if (weatherInstance.hour_weather() == 7 or weatherInstance.hour_weather() == 8):
            # Cloudy weather
            f.write('\nz_init_pl_q=0.0, 500.0, 2200., 2500., 3000.')
            if (selected_location==HIGHLANDS_LOCATION):
                f.write('\nf_init_pl_q=0.0, 4.3e-3, 4.3e-3, 0.0, 0.0')
            else:
                f.write('\nf_init_pl_q=0.0, 4.3e-3, 4.3e-3, 0.0, 0.0')
            if (self.tab2.accuracySlider.GetValue() > 40):
                f.write('\nl_init_pl_q_patchy=.true.')
                num_clouds=abs((self.tab2.accuracySlider.GetValue() - 20) / 5)
                start_posns=[]
                end_posns=[]
                divisor=32/num_clouds
                for i in range(num_clouds):
                    split_quad=abs(((i+1)*divisor)/4)
                    start_posn=random.randint(i*divisor,(i*divisor) + (divisor/4))
                    end_posn=random.randint(((i+1)*divisor) - (divisor/4),(i+1)*divisor)
                    if (start_posn >= end_posn): end_posn=start_posn+2
                    start_posns.append(start_posn)
                    end_posns.append(end_posn)
                f.write('\nq_x_start=')
                first_write=True
                for x in start_posns:
                    if (not first_write): f.write(',')
                    f.write(str(x))
                    first_write=False
                f.write('\nq_x_end=')
                first_write=True
                for x in end_posns:
                    if (not first_write): f.write(',')
                    f.write(str(x))
                    first_write=False

                f.write('\nq_y_start=')
                first_write=True
                bunch=True
                for x in start_posns:
                    if (not first_write): f.write(',')
                    f.write("1" if bunch else "5")
                    first_write=False
                    bunch=False if bunch else True
                f.write('\nq_y_end=')
                first_write=True
                bunch=False
                for x in end_posns:
                    if (not first_write): f.write(',')
                    f.write("31" if bunch else "25")
                    first_write=False
                    bunch=False if bunch else True
                #f.write('\nq_x_start=3,22\nq_x_end=17,31\nq_y_start=1,1\nq_y_end=30,30')
        elif (weatherInstance.hour_weather() == 5 or weatherInstance.hour_weather() == 6):
            # Misty/fog weather
            f.write('\nz_init_pl_q=0.0, 100.0, 1800., 2000., 3000.')
            f.write('\nf_init_pl_q=6.3e-3, 6.3e-3, 0.0, 0.0, 0.0')
        elif (weatherInstance.hour_weather() >= 9 and weatherInstance.hour_weather() <= 12):
            # Light rain weather
            f.write('\nz_init_pl_q=0.0, 1000.0, 1800., 2000., 3000.')
            f.write('\nf_init_pl_q=0.0, 6.3e-2, 0.0, 0.0, 0.0')
            f.write('\nl_init_pl_q_patchy=.true.')
            f.write('\nq_x_start=3,10,22\nq_x_end=10,20,32\nq_y_start=10,5,9\nq_y_end=25,20,30')
        elif (weatherInstance.hour_weather() >= 13):
            # Heavy rain weather
            f.write('\nz_init_pl_q=0.0, 500.0, 1000., 2000., 3000.')
            f.write('\nf_init_pl_q=0.0, 8.3e-2, 2.3e-3, 4.3e-3, 0.0')
            f.write('\nl_init_pl_q_patchy=.true.')
            f.write('\nq_x_start=3\nq_x_end=22\nq_y_start=10\nq_y_end=30')
        else:
            # Sunny weather
            f.write('\nz_init_pl_q=0.0, 500.0, 1000., 2000., 3000.')
            f.write('\nf_init_pl_q=0.0, 4.3e-3, 4.3e-3, 0.0, 0.0')
            f.write('\nl_init_pl_q_patchy=.true.')
            f.write('\nq_x_start=3,10,20\nq_x_end=17,22,25\nq_y_start=5,10,2\nq_y_end=20,25,25')
        #else:
        #    f.write('\nz_init_pl_q=0.0, 520.0, 1480., 2000., 3000.')
        #    f.write('\nf_init_pl_q=0.0, 0.0, 4.2e-3, 0.0, 0.0')

        #f.write('\nf_init_pl_q=17.0e-3, 16.3e-3, 10.7e-3, 4.2e-3, 3.0e-3')

        # wind config
        winforce=[0.0]*2
        windmultiplier=[1.0]*2

        strength=float(weatherInstance.wind_speed())/len(weatherInstance.wind_direction())
        for i in range(len(weatherInstance.wind_direction())):
            wind_direction=weatherInstance.wind_direction()[i]
            idx=0 if wind_direction == "N" or wind_direction == "S" else 1
            winforce[idx]+=-strength if wind_direction == "S" or wind_direction == "W" else strength

        wind_gust=weatherInstance.wind_gust()
        if (wind_gust > 0):
            gust_difference=wind_gust-weatherInstance.wind_speed()
            if (gust_difference > 0):
                windmultiplier[0]+=gust_difference/100
                windmultiplier[1]+=windmultiplier[0]*2
            else:
                if (weatherInstance.wind_speed > 20):
                    windmultiplier[0]=1.2
                    windmultiplier[1]=1.4

        if (winforce[0] == 0.0):
            f.write('\nl_init_pl_u=.false.')
        else:
            f.write('\nl_init_pl_u=.true.')
            f.write('\nz_init_pl_u=0.0, 700.0, 3000.')
            f.write('\nf_init_pl_u=' + str(round(winforce[0],2)) + ', ' + str(round(winforce[0]*windmultiplier[0],2)) + ', ' + str(winforce[0]*windmultiplier[1]))

        if (winforce[1] == 0.0):
            f.write('\nl_init_pl_v=.false.')
        else:
            f.write('\nl_init_pl_v=.true.')
            f.write('\nz_init_pl_v=0.0, 700.0, 3000.')
            f.write('\nf_init_pl_v=' + str(round(winforce[1],2)) + ', ' + str(round(winforce[1]*windmultiplier[0],2)) + ', ' + str(winforce[1]*windmultiplier[1]))

        # temperature settings
        temperature = 273.15 + weatherInstance.temperature()
        tempstr = str(temperature)

        f.write('\nthref0 = ' + tempstr)
        f.write('\nl_init_pl_theta=.true.')

        if (weatherInstance.hour_weather() == 7 or weatherInstance.hour_weather() == 8):
            # Cloudy weather
            f.write('\nz_init_pl_theta=0.0, 1000.0, 1480., 2000., 3000.')
            if (selected_location==CORNWALL_LOCATION):
                f.write('\nf_init_pl_theta=' + str(temperature+4) + ', ' + str(temperature+2) + ', ' + str(temperature) + ', ' + str(temperature-2) + ', ' + str(temperature-6))
            elif (selected_location==HIGHLANDS_LOCATION):
                f.write('\nf_init_pl_theta=' + str(temperature-10) + ', ' + str(temperature-8) + ', ' + str(temperature) + ', ' + str(temperature+2) + ', ' + str(temperature))
            else:
                f.write('\nf_init_pl_theta=' + str(temperature) + ', ' + str(temperature-2) + ', ' + str(temperature-4) + ', ' + str(temperature-6) + ', ' + str(temperature-10))
        elif (weatherInstance.hour_weather() == 5 or weatherInstance.hour_weather() == 6):
            # Misty/foggy weather
            f.write('\nz_init_pl_theta=0.0, 1000.0, 1480., 2000., 3000.')
            f.write('\nf_init_pl_theta=' + str(temperature-4) + ', ' + str(temperature-2) + ', ' + str(temperature-2) + ', ' + str(temperature-2) + ', ' + str(temperature-6))
        elif (weatherInstance.hour_weather() >= 9 and weatherInstance.hour_weather() <= 12):
            # Light rain weather
            f.write('\nz_init_pl_theta=0.0, 1000.0, 1480., 2000., 3000.')
            f.write('\nf_init_pl_theta=' + str(temperature-4) + ', ' + str(temperature-2) + ', ' + str(temperature-2) + ', ' + str(temperature-2) + ', ' + str(temperature-6))
        elif (weatherInstance.hour_weather() >= 13):
            # Heavy rain weather
            f.write('\nz_init_pl_theta=0.0, 1000.0, 1480., 2000., 3000.')
            f.write('\nf_init_pl_theta=' + str(temperature-4) + ', ' + str(temperature-2) + ', ' + str(temperature-2) + ', ' + str(temperature-2) + ', ' + str(temperature-6))
        else:
            # Sunny weather
            f.write('\nz_init_pl_theta=0.0, 1000.0, 1480., 2000., 3000.')
            f.write('\nf_init_pl_theta=' + str(temperature) + ', ' + str(temperature-2) + ', ' + str(temperature-2) + ', ' + str(temperature-4) + ', ' + str(temperature-6))

        #f.write('\nz_init_pl_theta=0.0, 520.0, 1480., 2000., 3000.')
        #f.write('\nf_init_pl_theta=' + tempstr + ', ' + str(temperature) + ', ' + str(temperature-10) + ', ' + str(temperature-10) + ', ' + str(temperature-10))

        #f.write('\nl_constant_forcing_theta=.true.')
       # f.write('\nf_force_pl_theta=2.0, 2.0, -10.0, -10.0')

        # core number and decomposition
        f.write('\ncores_per_pi=' + str(self.tab2.coresRadio.GetSelection()+1))
        f.write('\nnum_nodes=' + str(self.tab2.NodesSlider.GetValue()))

        pressure_accuracy=self.tab3.A
        wind_accuracy=self.tab3.B
        micro_phys_accuracy=self.tab3.C

        if (self.tab2.accuracySlider.GetValue() != 60):
            if (self.tab2.accuracySlider.GetValue() >= 0 and self.tab2.accuracySlider.GetValue() < 50):
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-1')
            if (self.tab2.accuracySlider.GetValue() >= 0 and self.tab2.accuracySlider.GetValue() < 20):
                f.write('\ncasim_enabled=.false.\nsimplecloud_enabled=.false.')
            if (self.tab2.accuracySlider.GetValue() >= 0 and self.tab2.accuracySlider.GetValue() < 30):
                f.write('\nadvection_flow_fields=pw\nadvection_theta_field=pw\nadvection_q_fields=pw')
            if (self.tab2.accuracySlider.GetValue() >= 20 and self.tab2.accuracySlider.GetValue() < 50):
                if (weatherInstance.hour_weather() < 4):
                    f.write('\ncasim_enabled=.false.\nsimplecloud_enabled=.false.')
                else:
                    f.write('\ncasim_enabled=.true.\nsimplecloud_enabled=.false.')
            if (self.tab2.accuracySlider.GetValue() >= 30 and self.tab2.accuracySlider.GetValue() < 50):
                f.write('\nadvection_flow_fields=pw\nadvection_theta_field=tvd\nadvection_q_fields=pw')
            if (self.tab2.accuracySlider.GetValue() >= 50 and self.tab2.accuracySlider.GetValue() < 60):
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-2')
                f.write('\nadvection_flow_fields=pw\nadvection_theta_field=pw\nadvection_q_fields=tvd')
                if (weatherInstance.hour_weather() < 4):
                    f.write('\ncasim_enabled=.false.\nsimplecloud_enabled=.false.')
                else:
                    f.write('\ncasim_enabled=.true.\nsimplecloud_enabled=.false.')
            if (self.tab2.accuracySlider.GetValue() >= 60 and self.tab2.accuracySlider.GetValue() < 70):
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-3')
                f.write('\nadvection_flow_fields=pw\nadvection_theta_field=tvd\nadvection_q_fields=tvd')
            if (self.tab2.accuracySlider.GetValue() >= 70 and self.tab2.accuracySlider.GetValue() < 80):
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-4')
                f.write('\nadvection_flow_fields=tvd\nadvection_theta_field=tvd\nadvection_q_fields=tvd')
            if (self.tab2.accuracySlider.GetValue() >= 80):
                f.write('\nfftsolver_enabled=.true.')
                f.write('\nadvection_flow_fields=tvd\nadvection_theta_field=tvd\nadvection_q_fields=tvd')
        else:
            if (pressure_accuracy < 0.2):
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-1')
            elif (pressure_accuracy >= 0.2 and pressure_accuracy < 0.3):
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-2')
            elif (pressure_accuracy >= 0.3 and pressure_accuracy < 0.4):
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-3')
            elif (pressure_accuracy >= 0.4 and pressure_accuracy < 0.5):
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-5')
            elif (pressure_accuracy >= 0.5 and pressure_accuracy < 0.6):
                f.write('\nfftsolver_enabled=.true.\niterativesolver_enabled=.false.')
            else:
                f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.\ntolerance=1.e-8')

            if (wind_accuracy < 0.2):
                 f.write('\nadvection_flow_fields=pw\nadvection_theta_field=pw\nadvection_q_fields=pw')
            elif (wind_accuracy >= 0.2 and wind_accuracy < 0.3):
                f.write('\nadvection_flow_fields=pw\nadvection_theta_field=tvd\nadvection_q_fields=pw')
            elif (wind_accuracy >= 0.3 and wind_accuracy < 0.4):
                f.write('\nadvection_flow_fields=pw\nadvection_theta_field=tvd\nadvection_q_fields=tvd')
            else:
                f.write('\nadvection_flow_fields=tvd\nadvection_theta_field=tvd\nadvection_q_fields=tvd')

            if (micro_phys_accuracy < 0.3):
                f.write('\ncasim_enabled=.false.\nsimplecloud_enabled=.false.')
            elif (micro_phys_accuracy >= 0.2 and micro_phys_accuracy < 0.3):
                f.write('\ncasim_enabled=.false.\nsimplecloud_enabled=.true.')
            else:
                f.write('\ncasim_enabled=.true.\nsimplecloud_enabled=.false.')

        f.close()

class TabWeather(wx.Panel):
    def __init__(self, parent, setupWindow):
        wx.Panel.__init__(self, parent)

        self.WinSizer=wx.BoxSizer(wx.VERTICAL)
         #Bottom panel, which will contain the sliders and piechart panels
        self.PhysicsPanel=wx.Panel(self,style=wx.BORDER_SUNKEN)

        #Add this to the window's sizer
        self.WinSizer.Add(self.PhysicsPanel,2,wx.EXPAND| wx.ALL, border=5)

        #sizer for the bottom row of controls
        self.BottomSizer=wx.BoxSizer(wx.VERTICAL)

        #assign this sizer to the PhysicsPanel
        self.PhysicsPanel.SetSizer(self.BottomSizer)

        #the bottom panels
        self.SlidersPanel=wx.Panel(self.PhysicsPanel,size=(200,100))
        self.PiePanel=wx.Panel(self.PhysicsPanel,size=(200,100))

        #Add the bottom panels to the BottomSizer
        self.BottomSizer.Add(self.SlidersPanel,1,wx.EXPAND| wx.ALL, border=5)
        self.BottomSizer.Add(self.PiePanel,1,wx.EXPAND| wx.ALL, border=5)

        #sliders panel

        #set up main sizer
        slidersSizer=wx.BoxSizer(wx.VERTICAL)
        self.SlidersPanel.SetSizer(slidersSizer)

        #label for this panel
        t3=wx.StaticText(self.SlidersPanel,label="Weather")
        slidersSizer.Add(t3,0,wx.CENTRE,border=5)

        #set up the sliders
        self.sliders=[]
        for i in range(3):
            self.sliders.append(wx.Slider(self.SlidersPanel,minValue=0,maxValue=100,value=33))

        #s1=wx.StaticText(self.SlidersPanel,label="Pressure")
        #s1.SetForegroundColour((255,0,0))
        slidersSizer.Add(wx.StaticText(self.SlidersPanel,label="Pressure"),0,wx.LEFT)
        slidersSizer.Add(self.sliders[0],1,wx.EXPAND)

        slidersSizer.Add(wx.StaticText(self.SlidersPanel,label="Wind"),0,wx.LEFT)
        slidersSizer.Add(self.sliders[1],1,wx.EXPAND)

        slidersSizer.Add(wx.StaticText(self.SlidersPanel,label="Cloud"),0,wx.LEFT)
        slidersSizer.Add(self.sliders[2],1,wx.EXPAND)

        #set up the reset button and bind pressing it to the ResetSliders method
        self.SliderResetButton=wx.Button(self.SlidersPanel,label="Reset")
        slidersSizer.Add(self.SliderResetButton,0,wx.EXPAND)
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

        self.GoButton=wx.Button(self,label="Start Simulation")
        self.Bind(wx.EVT_BUTTON,setupWindow.StartStopSim,self.GoButton)
        self.WinSizer.Add(self.GoButton,0,wx.EXPAND)

        self.SetSizer(self.WinSizer)

        #fit all the graphical elements to the window then display the window


        #update the pie chart and the chip graphic (window must be drawn first to get everything positioned properly)

        self.Show()
        self.Layout()

        self.UpdatePie()

         #(re)draws the pie chart
    def UpdatePie(self,e=None):
        #get the values of A, B, C
        self.Layout()

        a=self.A
        b=self.B
        c=self.C

        values=[a,b,c]
        labels=["Pressure","Wind","Cloud"]
        colors=["red","green","blue"]
        #clear existing figure
        self.figure.clf()

        #redraw figure
        self.axes=self.figure.add_subplot(111)
        self.axes.pie(values,labels=labels,colors=colors)
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

        a=float(a)/100.001+0.000005

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


class TabSetup(wx.Panel):
    def __init__(self, parent, setupWindow):
        wx.Panel.__init__(self, parent)
		#The window's sizer - for the rows of control panels and the go button
        self.WinSizer=wx.BoxSizer(wx.VERTICAL)

        self.setupWindow=setupWindow

        #sizer for the top row of controls
        self.TopSizer=wx.BoxSizer(wx.VERTICAL)

        self.LocationPanel=wx.Panel(self,style=wx.BORDER_SUNKEN)
        self.AccuracyPanel=wx.Panel(self,style=wx.BORDER_SUNKEN)
        #self.TopLeftSizer=wx.BoxSizer(wx.VERTICAL)

        #Add this to the window's sizer
        self.WinSizer.Add(self.LocationPanel,0,wx.EXPAND | wx.ALL,border=5)
        self.WinSizer.Add(self.AccuracyPanel,0,wx.EXPAND | wx.ALL,border=5)
        self.WinSizer.Add(self.TopSizer,1,wx.EXPAND)

        # Top row of control panels

        self.CoresPanel=wx.Panel(self,style=wx.BORDER_SUNKEN,size=(200,100))
        self.NodesPanel=wx.Panel(self,style=wx.BORDER_SUNKEN,size=(200,100))


        #self.TopLeftSizer.Add(self.LocationPanel, 1,wx.EXPAND | wx.ALL,border=5)
        #self.TopLeftSizer.Add(self.CoresPanel, 1,wx.EXPAND | wx.ALL,border=5)

        #Add these panels to their sizer
        self.TopSizer.Add(self.CoresPanel,1,wx.EXPAND | wx.ALL,border=5)
        self.TopSizer.Add(self.NodesPanel,1,wx.EXPAND| wx.ALL,border=5)

        locationSizer=wx.BoxSizer(wx.VERTICAL)
        self.LocationPanel.SetSizer(locationSizer)

        self.text_Location=wx.StaticText(self.LocationPanel,label="Location: Edinburgh")
        self.time_Location=wx.StaticText(self.LocationPanel,label="Time: 0600 Z")
        self.weather_Location=wx.StaticText(self.LocationPanel,label="Weather: Cloudy")

        locationSizer.Add(self.text_Location,0,wx.LEFT| wx.TOP,border=5)
        locationSizer.Add(self.time_Location,0,wx.LEFT| wx.ALL,border=5)
        locationSizer.Add(self.weather_Location,0,wx.LEFT | wx.BOTTOM,border=5)

        accuracySizer=wx.BoxSizer(wx.HORIZONTAL)
        self.AccuracyPanel.SetSizer(accuracySizer)
        accuracy_text=wx.StaticText(self.AccuracyPanel,label="Accuracy:")
        self.accuracySlider=wx.Slider(self.AccuracyPanel,minValue=1,maxValue=100,value=60,name="accuracy")
        accuracySizer.Add(accuracy_text,0,wx.LEFT | wx.TOP ,border=5)
        accuracySizer.Add(self.accuracySlider,1,wx.EXPAND | wx.TOP,border=5)

        # Cores Panel

        #set up main sizer for the panel
        coresSizer=wx.BoxSizer(wx.VERTICAL)
        self.CoresPanel.SetSizer(coresSizer)

        #label for the panel
        t1=wx.StaticText(self.CoresPanel,label="Number of Cores per Node")


        #load initial image - this will be reloaded, but we need something there to workout the dimensions of the panel
        file="chip1.png"
        bmp=wx.Image(file, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.bitmap1 = wx.StaticBitmap(self.CoresPanel,bitmap=bmp, size=(300, 300))

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

        #simulation start button

        self.GoButton=wx.Button(self,label="Start Simulation")
        self.Bind(wx.EVT_BUTTON,setupWindow.StartStopSim,self.GoButton)
        self.WinSizer.Add(self.GoButton,0,wx.EXPAND)


        #assign the main windows's sizer
        self.SetSizer(self.WinSizer)

        #fit all the graphical elements to the window then display the window


        #update the pie chart and the chip graphic (window must be drawn first to get everything positioned properly)

        self.Show()
        self.Layout()
        self.UpdateChip()


    def UpdateLocationText(self, locationText, weatherText):
        self.text_Location.SetLabel("Location: "+locationText)
        self.weather_Location.SetLabel("Weather: "+weatherText)
        time = int(strftime("%H")) - 3
        self.time_Location.SetLabel("Time: "+("0" if time < 10 else "") +str(time)+"00Z")

    #called when the number of cores is altered. This redraws the graphic
    def UpdateChip(self,e=None):
        #get the size of the part of the window that contains the graphic
        (w,h) = self.bitmap1.Size
        if (w ==0 or h==0):
            w=300
            h=300
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

class TabLocation(wx.Panel):
    def __init__(self, parent, weatherConfigTab, parallelismConfigTab, setWidth, setHeight, setupWindow):
        wx.Panel.__init__(self, parent)

        self.weatherConfigTab = weatherConfigTab
        self.parallelismConfigTab=parallelismConfigTab
        self.parent=parent

        self.setupWindow=setupWindow

        maxWidth, maxHeight= wx.GetDisplaySize()
        W,H=parent.GetClientSize()

        heightCorrector=100
        maxHeight-=heightCorrector
        # Set up background image of the UK:
        self.MaxImageSize = 2400
        self.Image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(self.MaxImageSize, self.MaxImageSize))
        Img = wx.Image(imageFile, wx.BITMAP_TYPE_JPEG)
        #Img = Img.Scale(maxHeight/1.4, maxHeight)
        Img = Img.Scale(setHeight/1.4*0.9,setHeight*0.9)
        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.Image.SetBitmap(wx.BitmapFromImage(Img))

        # Using a Sizer to handle the layout: I never like to use absolute postioning
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.Image, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        self.SetSizerAndFit(box)

        # Get the size of the image.....attempting to reposition the buttons depending on the window size.
        W, H = self.Image.GetSize()

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
            self.parallelismConfigTab.UpdateLocationText("Edinburgh", self.generateWeatherText(3166))
            self.setupWindow.weatherLocationCode=3166
            self.setupWindow.demo.Location="Edinburgh"
        elif (event.GetEventObject() == self.button2):
            self.parallelismConfigTab.UpdateLocationText("Highlands", self.generateWeatherText(3047))
            self.setupWindow.weatherLocationCode=3047
            self.setupWindow.demo.Location="Schiehallion"
        elif (event.GetEventObject() == self.button3):
            self.parallelismConfigTab.UpdateLocationText("London", self.generateWeatherText(3772))
            self.setupWindow.weatherLocationCode=3772
            self.setupWindow.demo.Location="London"
        elif (event.GetEventObject() == self.button4):
            self.parallelismConfigTab.UpdateLocationText("Cornwall", self.generateWeatherText(3808))
            self.setupWindow.weatherLocationCode=3808
            self.setupWindow.demo.Location="StIves"

        if (self.parent.GetPageCount() == 1):
            self.parallelismConfigTab.Show()
            self.weatherConfigTab.Show()
            self.parent.AddPage(self.parallelismConfigTab, "Parallelism")
            self.parent.AddPage(self.weatherConfigTab, "Weather")

        self.parent.SetSelection(1)

    def generateWeatherText(self, numb):
        weatherInstance=LiveWeather(numb, use_internal_values=self.setupWindow.mainWeatherWindow.internalWeatherCheckItem.IsChecked())
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
        live = LiveWeather(numb, use_internal_values=self.setupWindow.mainWeatherWindow.internalWeatherCheckItem.IsChecked()).hour_weather()
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

# -*- coding: utf-8 -*-
import client
import wx
from wx.lib.masked import *
import vtk

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
#places = [edinburgh, london, cornwall, highlands]

if LiveWeather(3166).hour_weather() <= 1:
    edinburgh.append(sun)
elif 9 > LiveWeather(3166).hour_weather() > 1:
    edinburgh.append(cloud)
else:
    edinburgh.append(rain)

if LiveWeather(3772).hour_weather() <= 1:
    london.append(sun)
elif 9 > LiveWeather(3772).hour_weather() > 1:
    london.append(cloud)
else:
    london.append(rain)

if LiveWeather(3808).hour_weather() <= 1:
    cornwall.append(sun)
elif 9 > LiveWeather(3808).hour_weather() > 1:
    cornwall.append(cloud)
else:
    cornwall.append(rain)

if LiveWeather(3047).hour_weather() <= 1:
    highlands.append(sun)
elif 9 > LiveWeather(3047).hour_weather() > 1:
    highlands.append(cloud)
else:
    highlands.append(rain)


# Derive the demo-specific GUI class from the AbstractUI class
class WeatherWindow(UI):
    def __init__(self, parent, title, demo, servercomm):

        # call superclass' __init__
        UI.__init__(self, parent, title, demo, servercomm)

        # panel=wx.Panel(self)
        wx.Frame.CenterOnScreen(self)

        self.fullscreen = False
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

        ID_SETTINGS = 1

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        fileMenu.Append(ID_SETTINGS, 'Settings', 'Open settings window')
        fitem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, fitem)
        self.Bind(wx.EVT_MENU, self.OpenWindow, None, 1)

        # add another renderer for the bottom part
        self.bottomrenderer = vtk.vtkRenderer()
        self.bottomrenderer.SetViewport(0, 0, 1, 0.3)

        # set up sizers that allow you to position window elements easily
        # main sizer - arrange items horizontally on screen (controls on left, vtk interactor on right)
        self.mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        # text at bottom that displays the current frame number
        self.logger = wx.TextCtrl(self, style=wx.TE_READONLY)

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

    def OnQuit(self, e):
        self.Close()

    def StartInteractor(self):
        UI.StartInteractor(self)

    def StartSim(self, config):
        UI.StartSim(self, config)

    def StopSim(self):
        UI.StopSim(self)

    def TimerCallback(self, e):
        UI.TimerCallback(self, e)

        self.logger.SetValue("Frame %d of %d" % (self.CurrentFrame, self.nfiles.value - 1))

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
        tab2 = TabTwo(nb, self.title, self.demo, self.servercomm, mainWeatherWindow)
        tab1 = TabOne(nb, tab2)

        # Add the windows to tabs and name them.
        nb.AddPage(tab1, "Basic")
        nb.AddPage(tab2, "Advanced")

        # Set noteboook in a sizer to create the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)


class TabTwo(wx.Panel):
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
        self.mainWeatherWindow.StopSim(None)

    def timer_callback(self, e):
        self.mainWeatherWindow.TimerCallback(None)


class TabOne(wx.Panel):
    def __init__(self, parent, mainTabTwo):
        wx.Panel.__init__(self, parent)

        self.mainTabTwo = mainTabTwo

        # Set up background image of the UK:
        self.MaxImageSize = 2400
        self.Image = wx.StaticBitmap(self, bitmap=wx.EmptyBitmap(self.MaxImageSize, self.MaxImageSize))
        Img = wx.Image(imageFile, wx.BITMAP_TYPE_JPEG)
        Img = Img.Scale(1800, 2400)
        # convert it to a wx.Bitmap, and put it on the wx.StaticBitmap
        self.Image.SetBitmap(wx.BitmapFromImage(Img))

        # Using a Sizer to handle the layout: I never like to use absolute postioning
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.Image, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL | wx.ADJUST_MINSIZE, 10)
        self.SetSizerAndFit(box)

        # Get the size of the image.....attempting to reposition the buttons depending on the window size.
        W, H = self.Image.GetSize()

        # Set up image button for Edinburgh(city):
        bmp = wx.Bitmap(edinburgh[0], wx.BITMAP_TYPE_ANY)
        self.button1 = wx.BitmapButton(self, -1, bmp, size = (80, 80), pos=(W/1.96, H/3.4))
        self.Bind(wx.EVT_BUTTON, self.go, self.button1)
        self.button1.SetDefault()

        # Set up image button for Highlands(mountains):
        bmp = wx.Bitmap(highlands[0], wx.BITMAP_TYPE_ANY)
        self.button2 = wx.BitmapButton(self, -1, bmp, size=(80, 80), pos=(W / 2.3, H / 6.7))
        self.Bind(wx.EVT_BUTTON, self.go, self.button2)
        self.button2.SetDefault()

        # Set up image button for London(city+river):
        bmp = wx.Bitmap(london[0], wx.BITMAP_TYPE_ANY)
        self.button3 = wx.BitmapButton(self, -1, bmp, size=(80, 80), pos=(W / 1.4, H / 1.55))
        self.Bind(wx.EVT_BUTTON, self.go, self.button3)
        self.button3.SetDefault()

        # Set up image button for Cornwall(seaside):
        bmp = wx.Bitmap(self.weather_data(cornwall, 3808)[0], wx.BITMAP_TYPE_ANY)
        self.button4 = wx.BitmapButton(self, -1, bmp, size=(80, 80), pos=(W / 2.52, H / 1.33))
        self.Bind(wx.EVT_BUTTON, self.go, self.button4)
        self.button4.SetDefault()

        # Set up image button for Ireland:
        bmp = wx.Bitmap(rain, wx.BITMAP_TYPE_ANY)
        self.button5 = wx.BitmapButton(self, -1, bmp, size=(80, 80), pos=(W / 3.7, H / 2.1))
        self.Bind(wx.EVT_BUTTON, self.always_rain, self.button5)
        # Calls the functions that change the cursor icon
        self.button5.Bind(wx.EVT_ENTER_WINDOW, self.changeCursor)
        self.button5.Bind(wx.EVT_ENTER_WINDOW, self.changeCursorBack)
        self.button5.SetDefault()

    def go(self, config):
        self.mainTabTwo.StartStopSim(None)

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

    def always_rain(self, event):
        dial = wx.MessageDialog(self, "Who are you kidding? The forecast is always rain here",
                                "Irish Weather", wx.OK | wx.CANCEL)
        dial.ShowModal()

    # Change the cursor to a hand every time the cursor goes over a button
    def changeCursor(self, event):
        myCursor = wx.StockCursor(wx.CURSOR_HAND)
        self.button5.SetCursor(myCursor)
        self.button1.SetCursor(myCursor)
        self.button2.SetCursor(myCursor)
        self.button3.SetCursor(myCursor)
        self.button4.SetCursor(myCursor)
        event.Skip()

    # Change the cursor back to the arrow every time the cursor leaves a button
    def changeCursorBack(self, event):
        myCursor = wx.StockCursor(wx.CURSOR_ARROW)
        self.button5.SetCursor(myCursor)
        self.button1.SetCursor(myCursor)
        self.button2.SetCursor(myCursor)
        self.button3.SetCursor(myCursor)
        self.button4.SetCursor(myCursor)
        event.Skip()

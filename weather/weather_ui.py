import client
import wx
from wx.lib.masked import *
import vtk

# Derive the demo-specific GUI class from the AbstractUI class
class WeatherWindow(client.AbstractUI):
    
    def __init__(self,parent,title,demo,servercomm):
        
        #call superclass' __init__
        client.AbstractUI.__init__(self,parent,title,demo,servercomm)

        self.fullscreen = False
        self.decompositiongrid = True
        self.timeofyear = None
        self.rainmass = 0
        self.cropslevel = 0
        self.waterlevel = 0
        self.numberofcores = 0
        self.columnsinX = 0
        self.columnsinY = 0
        self.mappers = {}
        self.actors = {}
        self.filters = {}
        self.widgets = {}
        self.views = {}

        # add another renderer for the bottom part
        self.bottomrenderer = vtk.vtkRenderer()
        self.bottomrenderer.SetViewport(0,0,1,0.3)

        #set up sizers that allow you to position window elements easily

        #main sizer - arrange items horizontally on screen (controls on left, vtk interactor on right)
        self.mainsizer=wx.BoxSizer(wx.HORIZONTAL)
        #sizer for buttons (align buttons vertically)
        self.buttonsizer=wx.BoxSizer(wx.VERTICAL)
        #sizer for rewind, step forward, step back and fast forward buttons
        self.weesizer=wx.BoxSizer(wx.HORIZONTAL)
        
        #create 'array' of buttons
        self.buttons=[]

        self.buttons.append(wx.Button(self,label='Start Simulation'))
        self.buttons.append(wx.Button(self,label='Play'))
        self.buttons.append(wx.Button(self,label='<<'))
        self.buttons.append(wx.Button(self,label='<'))
        self.buttons.append(wx.Button(self,label='>'))
        self.buttons.append(wx.Button(self,label='>>'))


        self.buttons.append(wx.Button(self,label='Summer'))
        self.buttons.append(wx.Button(self,label='Autumn'))
        self.buttons.append(wx.Button(self,label='Winter'))
        self.buttons.append(wx.Button(self,label='Spring'))

        self.buttons.append(wx.Button(self,label='Toggle Grid'))

        self.buttons.append(wx.Button(self, label='Low'))
        self.buttons.append(wx.Button(self, label='Middle'))
        self.buttons.append(wx.Button(self, label='High'))

        #bind button clicks (wx.EVT_BUTTONT) to methods
        self.Bind(wx.EVT_BUTTON,self.StartStopSim,self.buttons[0])
        self.Bind(wx.EVT_BUTTON,self.play,self.buttons[1])
        self.Bind(wx.EVT_BUTTON,self.rewind,self.buttons[2])
        self.Bind(wx.EVT_BUTTON,self.stepback,self.buttons[3])
        self.Bind(wx.EVT_BUTTON,self.stepforward,self.buttons[4])
        self.Bind(wx.EVT_BUTTON,self.fastforward,self.buttons[5])

        self.Bind(wx.EVT_BUTTON, self.togglegrid, self.buttons[10])

        self.Bind(wx.EVT_BUTTON, self.setSummer, self.buttons[6])
        self.Bind(wx.EVT_BUTTON, self.setAutumn, self.buttons[7])
        self.Bind(wx.EVT_BUTTON, self.setWinter, self.buttons[8])
        self.Bind(wx.EVT_BUTTON, self.setSpring, self.buttons[9])

        self.Bind(wx.EVT_BUTTON, self.setWaterLow, self.buttons[11])
        self.Bind(wx.EVT_BUTTON, self.setWaterMiddle, self.buttons[12])
        self.Bind(wx.EVT_BUTTON, self.setWaterHigh, self.buttons[13])

        #Adding dropdown menu and text fields for core numbers and decomposition topology
        self.coretext1 = wx.StaticText(self,label="Cores per Pi:")
        self.coretext2 = wx.StaticText(self,label="Cores depth:")
        self.coretext3 = wx.StaticText(self,label="Cores width:")

        self.corenum = wx.SpinCtrl(self,id=wx.ID_ANY,  value='4') #number of cores used per Pi
        self.corenum.SetRange(1,4)
        self.columnsizex = wx.SpinCtrl(self, id=wx.ID_ANY, value='2')#number of columns each core gets in X
        self.columnsizey = wx.SpinCtrl(self, id=wx.ID_ANY, value='16') #number of columns each core gets in Y

        sampleList = ['Iterative','FFT']
        self.solver = wx.ComboBox(self, id=wx.ID_ANY, choices=sampleList, value='Iterative')

        self.Bind(EVT_NUM, self.setCoreNum, self.corenum)
        #self.Bind(EVT_NUM, self.setColumnSizeX, self.columnsizex)
        #self.Bind(EVT_NUM, self.setColumnSizeY, self.columnsizey)


        #add a slider to control refresh rate
        #text box to display slider value
        self.text=wx.StaticText(self,label="Refreshrate =...")
        self.slider=wx.Slider(self,wx.ID_ANY,value=5, minValue=1, maxValue=20) #must be integer
        self.sliderdt=0.1 #slider interval
        self.refreshrate=(self.slider.GetValue() * self.sliderdt)
        str="Refresh rate: %3.1f"%self.refreshrate
        self.text.SetLabel(str)
        #bind changing slider value to UpdateSlider method
        self.Bind(wx.EVT_SCROLL,self.UpdateFrameSlider,self.slider)

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
        self.pressureslider = wx.Slider(self, wx.ID_ANY, value=100000, minValue=80000, maxValue=120000)  # must be integer
        str = "Pressure: %3.1f" % self.pressureslider.GetValue()
        self.pressuretext.SetLabel(str)
        self.Bind(wx.EVT_SCROLL, self.UpdatePressureSlider, self.pressureslider)

        #add buttons to the button (vertical) sizer
        self.buttonsizer.Add(self.buttons[0],1,wx.EXPAND)
        self.buttonsizer.Add(self.buttons[1],1,wx.EXPAND)

        #add <<, <, > and >> buttons to the weesizer
        self.weesizer.Add(self.buttons[2],0.5,wx.EXPAND)
        self.weesizer.Add(self.buttons[3],0.5,wx.EXPAND)
        self.weesizer.Add(self.buttons[4],0.5,wx.EXPAND)
        self.weesizer.Add(self.buttons[5],0.5,wx.EXPAND)

        #add weesizer to the button sizer
        self.buttonsizer.Add(self.weesizer,1,wx.EXPAND)

        self.buttonsizer.Add(self.buttons[10],1,wx.EXPAND)

        self.buttonsizer.Add((10,30))

        #add slider to the sizer
        self.buttonsizer.Add(self.windtext,1,wx.EXPAND)
        self.buttonsizer.Add(self.windslider,1,wx.EXPAND)

        self.buttonsizer.Add(self.temptext,1,wx.EXPAND)
        self.buttonsizer.Add(self.tempslider,1,wx.EXPAND)

        self.buttonsizer.Add(self.pressuretext,1,wx.EXPAND)
        self.buttonsizer.Add(self.pressureslider,1,wx.EXPAND)

        self.buttonsizer.Add((10,30))

        self.timeofyeartext = wx.StaticText(self, label="Time of year: ")
        self.buttonsizer.Add(self.timeofyeartext, 1, wx.EXPAND)

        self.timeofyearsizer=wx.BoxSizer(wx.HORIZONTAL)
        self.timeofyearsizer.Add(self.buttons[6],0.5,wx.EXPAND)
        self.timeofyearsizer.Add(self.buttons[7],0.5,wx.EXPAND)
        self.timeofyearsizer.Add(self.buttons[8],0.5,wx.EXPAND)
        self.timeofyearsizer.Add(self.buttons[9],0.5,wx.EXPAND)
        self.buttonsizer.Add(self.timeofyearsizer, 1, wx.EXPAND)

        self.watertext = wx.StaticText(self, label="Amount of water: ")
        self.buttonsizer.Add(self.watertext, 1, wx.EXPAND)

        self.watersizer = wx.BoxSizer(wx.HORIZONTAL)
        self.watersizer.Add(self.buttons[11], 1, wx.EXPAND)
        self.watersizer.Add(self.buttons[12], 1, wx.EXPAND)
        self.watersizer.Add(self.buttons[13], 1, wx.EXPAND)
        self.buttonsizer.Add(self.watersizer, 1, wx.EXPAND)

        self.buttonsizer.Add((10,30))

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
        self.buttonsizer.Add((10,30))

        self.solvertext = wx.StaticText(self, label="Method: ")
        self.buttonsizer.Add(self.solvertext, 1, wx.EXPAND)

        self.buttonsizer.Add(self.solver, 1, wx.EXPAND)

        #add some vertical space
        self.buttonsizer.Add((10,150))

        #add slider to the sizer
        self.buttonsizer.Add(self.text,1,wx.EXPAND)
        self.buttonsizer.Add(self.slider,1,wx.EXPAND)

        #text at bottom that displays the current frame number
        self.logger = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.buttonsizer.Add(self.logger,1,wx.EXPAND)


        #disable buttons (as no simulation is running at startup so the buttons are useless)
        self.buttons[1].Enable(False)
        self.buttons[2].Enable(False)
        self.buttons[3].Enable(False)
        self.buttons[4].Enable(False)
        self.buttons[5].Enable(False)

        self.buttons[10].Enable(False)

        
        #add button sizer to the left panel of the main sizer, vtk widget to the right (with horizontal width ratio of 1:8)
        self.mainsizer.Add(self.buttonsizer,0.5,wx.EXPAND)
        self.mainsizer.Add(self.vtkwidget,2,wx.EXPAND)

        #attach main sizer to the window
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(1)
        self.mainsizer.Fit(self)
        
        #create mapper
        #self.mapper=vtk.vtkPolyDataMapper()
        
        self.StartInteractor()

        #show window
        self.Show()


    def StartInteractor(self):
        client.AbstractUI.StartInteractor(self)


    def StartSim(self,config):
        client.AbstractUI.StartSim(self,config)

        
    def StopSim(self):
        client.AbstractUI.StopSim(self)

        
    def TimerCallback(self,e):
        client.AbstractUI.TimerCallback(self,e)
        
        self.logger.SetValue("Frame %d of %d"%(self.CurrentFrame,self.nfiles.value-1))

    
    def StartStopSim(self,e):
        
        #if simulation is not started then start a new simulation
        if not self.servercomm.IsStarted():
            self.writeConfig()

            dlg=wx.MessageDialog(self,"Do you wish to continue?","This will start a simulation",wx.OK|wx.CANCEL)
            
            if dlg.ShowModal() == wx.ID_OK:

                # write to config


                config="config.mcf"
                #config  = "config_nice.mcf"
                self.StartSim(config)
                
                self.buttons[0].SetLabel("Stop Simulaton")

                self.buttons[1].Enable(True)
                self.buttons[2].Enable(True)
                self.buttons[3].Enable(True)
                self.buttons[4].Enable(True)
                self.buttons[5].Enable(True)
                self.buttons[10].Enable(True)

                self.playing=False

                #load the first data file
                self.getdata.value=True
        
        #if simulation is started then stop simulation
        else:
            
            dlg=wx.MessageDialog(self,"Are you sure?","This will stop the current simulation.",wx.OK|wx.CANCEL)
            
            if dlg.ShowModal() == wx.ID_OK:
                
                self.StopSim()
                
                self.buttons[0].SetLabel("Start Simulation")
                
                self.logger.SetValue("")
                
                self.playing=False
                
                self.buttons[1].SetLabel("Play")
                self.buttons[1].Enable(False)
                self.buttons[2].Enable(False)
                self.buttons[3].Enable(False)
                self.buttons[4].Enable(False)
                self.buttons[5].Enable(False)

                self.buttons[10].Enable(False)

                try:
                    for actor in self.renderer.GetActors():
                        self.renderer.RemoveActor(actor)
                    self.actors.clear()
                except:
                    pass
                self.vtkwidget.GetRenderWindow().Render()
            
            
    
    def OnClose(self,e):
        client.AbstractUI.OnClose(self,e)
    
    

    #----------------------------------------------------------------------
    #------------- New methods specific to demo go here -------------------
    #----------------------------------------------------------------------


    #play or pause (depending upon whether the 'movie' is paused or playing )
    def play(self,e):

        if not self.playing: #play
            self.getdata.value=True
            self.buttons[1].SetLabel("Pause")
            self.playing=True
        else: #pause
            self.getdata.value=False
            self.buttons[1].SetLabel("Play")
            self.playing=False


    #Go back to the first frame
    def rewind(self,e):

        self.playing=False #stop playing (if it is playing)
        self.frameno.value=0
        self.getdata.value=True
        self.buttons[1].SetLabel("Play")
        self.rainmass = 0

    #go to the latest frame
    def fastforward(self,e):

        self.playing=False #stop playing (if it is playing)
        self.frameno.value=self.nfiles.value-1
        self.getdata.value=True
        self.buttons[1].SetLabel("Play")



    #step one frame backwards
    def stepback(self,e):

        self.playing=False #stop playing (if it is playing)
        self.frameno.value=self.CurrentFrame-1
        self.getdata.value=True
        self.buttons[1].SetLabel("Play")


    #step one frame forwards
    def stepforward(self,e):

        self.playing=False #stop playing (if it is playing)
        self.frameno.value=self.CurrentFrame+1
        self.getdata.value=True
        self.buttons[1].SetLabel("Play")

    def togglegrid(self, e):
        if self.decompositiongrid is True:
            self.decompositiongrid = False
        else:
            self.decompositiongrid = True

        if self.timer.IsRunning():
            self.timer.Stop()
            self.timer.Start()

    def UpdateFrameSlider(self,e):
        #this method runs every time the slider is moved. It sets the new refreshrate, updates the refreshrate GUI text, and stops and starts the timer with the new framerate (if it is on)

        #get new framerate
        self.refreshrate=(self.slider.GetValue() * self.sliderdt)
        #update framerate text
        str="Refresh rate: %3.1f s"%self.refreshrate
        self.text.SetLabel(str)

        if self.timer.IsRunning():
            self.timer.Stop()
            self.timer.Start(self.refreshrate*1000)

    def UpdateWindSlider(self, e):
        str =  "Wind power: %3.1f"%self.windslider.GetValue()
        self.windtext.SetLabel(str)
    def UpdateTempSlider(self, e):
        str =  "Temperature: %3.1f °C"%self.tempslider.GetValue()
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

    def setCoreNum(self):
        self.numberofcores = self.corenum.GetValue()

    def setColumnSizeX(self):
        self.columnsinX = self.columnsizex.GetValue()

    def setColumnSizeY(self):
        self.columnsinY = self.columnsizey.GetValue()

    def writeConfig(self):

        # because the events or something does not work for setting there values, set them here
        self.numberofcores = self.corenum.GetValue()
        self.columnsinX = self.columnsizex.GetValue()
        self.columnsinY = self.columnsizey.GetValue()

        f = open('config.mcf', 'w+')

        f.write('global_configuration=outreach_config')

        #pressure settings
        f.write('\nsurface_pressure=' + str(self.pressureslider.GetValue()))
        f.write('\nsurface_reference_pressure=' + str(self.pressureslider.GetValue()))
        f.write('\nfixed_cloud_number=1.0e9')

        #switch sef.timeofyear

        f.write('\nf_force_pl_q=-1.2e-8, -1.2e-8, 0.0, 0.0')

        f.write('\nsurface_latent_heat_flux=200.052')
        f.write('\nsurface_sensible_heat_flux=16.04')

        #amount of water
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

        #core number and decomposition
        f.write('\ncores_per_pi=' + str(self.corenum.GetValue()))
        f.write('\nnum_px=' + str(self.columnsizex.GetValue()))
        f.write('\nnum_py=' + str(self.columnsizey.GetValue()))

        if self.solver.GetValue() == 'Iterative':
            f.write('\nfftsolver_enabled=.false.\niterativesolver_enabled=.true.')
        else:
            f.write('\nfftsolver_enabled=.true.\niterativesolver_enabled=.false.')


        f.close()

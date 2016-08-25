import client
import wx
import vtk




# Derive the demo-specific GUI class from the AbstractUI class
class GalaxyWindow(client.AbstractUI):
    
    def __init__(self,parent,title,demo,servercomm):
        
        #call superclass' __init__
        client.AbstractUI.__init__(self,parent,title,demo,servercomm)
        
        
        
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

        #bind button clicks (wx.EVT_BUTTONT) to methods
        self.Bind(wx.EVT_BUTTON,self.StartStopSim,self.buttons[0])
        self.Bind(wx.EVT_BUTTON,self.play,self.buttons[1])
        self.Bind(wx.EVT_BUTTON,self.rewind,self.buttons[2])
        self.Bind(wx.EVT_BUTTON,self.stepback,self.buttons[3])
        self.Bind(wx.EVT_BUTTON,self.stepforward,self.buttons[4])
        self.Bind(wx.EVT_BUTTON,self.fastforward,self.buttons[5])


        #add a slider to control refresh rate
        #text box to display slider value
        self.text=wx.StaticText(self,label="Refreshrate =...")
        self.slider=wx.Slider(self,wx.ID_ANY,value=5,minValue=1,maxValue=20) #must be integer

        self.sliderdt=0.1 #slider interval
        self.refreshrate=(self.slider.GetValue() * self.sliderdt)

        str="Refresh rate=: %3.1f s"%self.refreshrate
        self.text.SetLabel(str)

        #bind changing slider value to UpdateSlider method
        self.Bind(wx.EVT_SCROLL,self.UpdateSlider,self.slider)



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

        #add some vertical space
        self.buttonsizer.Add((10,500))

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
        
        
        #add button sizer to the left panel of the main sizer, vtk widget to the right (with horizontal width ratio of 1:8)
        self.mainsizer.Add(self.buttonsizer,1,wx.EXPAND)
        self.mainsizer.Add(self.vtkwidget,2,wx.EXPAND)

        #attach main sizer to the window
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(1)
        self.mainsizer.Fit(self)
        
        #create mapper
        self.mapper=vtk.vtkPolyDataMapper()
        
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
            
            dlg=wx.MessageDialog(self,"Do you wish to continue?","This will start a simulation",wx.OK|wx.CANCEL)
            
            if dlg.ShowModal() == wx.ID_OK:
            
                config="config.txt"
                
                self.StartSim(config)
                
                self.buttons[0].SetLabel("Stop Simulaton")

                self.buttons[1].Enable(True)
                self.buttons[2].Enable(True)
                self.buttons[3].Enable(True)
                self.buttons[4].Enable(True)
                self.buttons[5].Enable(True)
                
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
                
                try:
                    self.renderer.RemoveActor(self.actor)
                    del self.actor
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



    def UpdateSlider(self,e):
        #this method runs every time the slider is moved. It sets the new refreshrate, updates the refreshrate GUI text, and stops and starts the timer with the new framerate (if it is on)

        #get new framerate
        self.refreshrate=(self.slider.GetValue() * self.sliderdt)

        #update framerate text
        str="Refresh rate= %3.1f s"%self.refreshrate
        self.text.SetLabel(str)

        if self.timer.IsRunning():
            self.timer.Stop()
            self.timer.Start(self.refreshrate*1000)

 
        



import wx
import vtk
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
import multiprocessing as mp
import numpy as np
from netCDF4 import Dataset
import abc
import time


import requests
import shutil
import json


#class which describes the ways by which the program can interact with the server.
class Serverclass:
    #input is the name of the simulation (as known to the server)
    def __init__(self,simname):
        self.targetbase='http://127.0.0.1:5000/'
        self.simname=simname
        print "Server initialised for simulation '"+self.simname+"'."
        self.started=False

    #tell server to start the simulation. Pass in the configuration file
    def StartSim(self,configfile):
        if not self.started:
            files= {'fileToUpload': open(configfile,'rb')}
            postrequest = requests.post(self.targetbase+'simulation/'+self.simname, files=files)
            self.simid=postrequest.text
            self.base= self.targetbase +'simulation/'+ self.simname +'/'+ self.simid
            self.data_base=self.base+'/data/'
            self.started=True
            print "Simulation Started. ID="+self.simid
        else:
            print "Error, simulation has already started"
            print "Simulation ID="+self.simid

    #get the status of the simulation. Returns a dictionary containing 'status' (running,finished etc) and 'files' (list of results files)
    def GetStatus(self):
        if self.started:
            statusrequest = requests.get(self.base,stream=True)
            self.status=json.loads(statusrequest.text)
            return self.status
        else:
            print "Error: No simulation is running"

    #Downloads the file 'file_to_get' from the server and saves it to the temp file 'name_of_tmp_file'
    def GetDataFile(self,file_to_get,name_of_tmp_file):
        if self.started:
            filerequest=requests.get(self.data_base + file_to_get,stream=True)
            with open(name_of_tmp_file,'wb') as f:
                for chunk in filerequest.iter_content(1024):
                    f.write(chunk)
        else:
            print "Error: No simulation is running"

    # delete the file 'file' from the server
    def DeleteFile(self,file):
        if self.started:
            deletefilerequest=requests.delete(self.data_base+file)
            print "Deleted file: '"+file+"'"
        else:
            print "Error: No simulation is running"

    #delete all the simulation's output files from the server
    def DeleteSim(self):
        if self.started:
            deletefilerequest=requests.delete(self.base)
            print "Deleted Simulation"
            self.started=False
        else:
            print "Error: No simulation to be deleted"

    #returns whether the server class object has started a simulation
    def IsStarted(self):
        return self.started





#Entry point to the GUI. This method needs to be called in the demo
def Start(window_name,demo,server):
    app=wx.App(False)
    window=MyWindow(None,window_name,demo,server)
    #start eventloop
    app.MainLoop()





#define an abstract demo class which is the 'template' class for all demo-specific code.
#Note that each demo MUST define its own subclass of this class, and define its own vesion of each of the methods
class abstractdemo(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def GetFilename(self,frame):
        return

    @abc.abstractmethod
    def GetVTKData(self,root):
        return

    @abc.abstractmethod
    def RenderFrame(self,win,data):
        return




#process that periodically checks the server for the simulation status, and downloads new data files and sends them to the GUI process if requested.
def process(frameno,nfiles,getdata,newdata,pipe,demo,server):
    # frameno=shared variable containing current frame number
    # nfiles=shared variable containing number of files on server
    # getdata=flag to tell process whether to download new data from server
    # newdata = flag to tell GUI if process has downloaded a data file and is ready to send it
    # pipe = communication object
    # demo = object contaning demo-specific functions
    # server = Serverclass object

    print "Process initiated"

    while True: #infinite loop

        # get status and set nfiles
        status=server.GetStatus()
        datafiles=status['files']
        nfiles.value=len(datafiles)

        if getdata.value == True: #if GUI has requested a new file
            n=frameno.value

            try:
                fname=datafiles[n] #get name of file to download
                server.GetDataFile(fname,'tmp.nc') #get the data file

                root=Dataset('tmp.nc','r') #get the netcdf handle for the data file

                data=demo.GetVTKData(root) #read it into a Data Transfer Object

                newdata.value=True #set flag to tell GUI there is new data available
                pipe.send(data) #send the data across
                ok=pipe.recv() #get a read receipt
                newdata.value=False #say we no longer have new data (since its been sent and received)

            except: #no new data ready...
                time.sleep(0.1)

        else:
            time.sleep(0.1)





#Create MyWindow class (subclass of wx.Frame - the wxWidgets equivalent of a window)
class MyWindow(wx.Frame):


    def __init__(self,parent,title,demo,server):
        wx.Frame.__init__(self,parent,title=title,size=(1000,800))
        self.demo=demo
        self.server=server



        #bind closing the window to the OnClose() method (kills the process)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        #set up sizers that allow you to position window elements easily

        #main sizer - arrange items horizontally on screen (controls on left, vtk interactor on right)
        self.mainsizer=wx.BoxSizer(wx.HORIZONTAL)
        #sizer for buttons (align buttons vertically)
        self.buttonsizer=wx.BoxSizer(wx.VERTICAL)
        #sizer for rewind, step forward, step back and fast forward buttons
        self.weesizer=wx.BoxSizer(wx.HORIZONTAL)


        #timer which periodically checks from process to see if there is new data avaiable etc.
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.TimerCallback,self.timer)


        #create 'array' of buttons
        self.buttons=[]

        self.buttons.append(wx.Button(self,label='Start Simulation'))
        self.buttons.append(wx.Button(self,label='Play'))
        self.buttons.append(wx.Button(self,label='<<'))
        self.buttons.append(wx.Button(self,label='<'))
        self.buttons.append(wx.Button(self,label='>'))
        self.buttons.append(wx.Button(self,label='>>'))

        #bind button clicks (wx.EVT_BUTTONT) to methods
        self.Bind(wx.EVT_BUTTON,self.Start,self.buttons[0])
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


        #disable buttons
        self.buttons[1].Enable(False)
        self.buttons[2].Enable(False)
        self.buttons[3].Enable(False)
        self.buttons[4].Enable(False)
        self.buttons[5].Enable(False)



        #create vtk render widget
        self.widget=wxVTKRenderWindowInteractor(self,wx.ID_ANY)

        #add button sizer to the left panel of the main sizer, vtk widget to the right (with horizontal width ratio of 1:8)
        self.mainsizer.Add(self.buttonsizer,1,wx.EXPAND)
        self.mainsizer.Add(self.widget,2,wx.EXPAND)

        #attach main sizer to the window
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(1)
        self.mainsizer.Fit(self)

        #flag to determine if the vtk widget has been initialised (has a renderer attached)
        self.StartInteractor() #start the interactor

        #create mapper
        self.mapper=vtk.vtkPolyDataMapper()

        #show window
        self.Show()


    # attach renderer to the vtk widget and draw axes
    def StartInteractor(self):

        print "Starting interactor"
        self.renderer=vtk.vtkRenderer()
        self.widget.GetRenderWindow().AddRenderer(self.renderer)
        camera=self.renderer.GetActiveCamera()
        camera.SetFocalPoint(0.,0.,0.)
        camera.SetPosition(50.,0.,0.)
        camera.Roll(-90)

        mouse=vtk.vtkInteractorStyleTrackballCamera()
        self.widget.SetInteractorStyle(mouse)

        #create some axes to indicate the orientation of the galaxy
        axes = vtk.vtkAxesActor()
        self.axisw=vtk.vtkOrientationMarkerWidget()
        self.axisw.SetOutlineColor( 0.9300, 0.5700, 0.1300 );
        self.axisw.SetOrientationMarker( axes );
        self.axisw.SetInteractor( self.widget._Iren );
        self.axisw.SetViewport( 0.0, 0.0, 0.3, 0.3 );
        self.axisw.SetEnabled( 1 );
        self.axisw.InteractiveOn();


        self.widget.GetRenderWindow().Render()


    #start/stop the simulation
    def Start(self,e):
        if not self.server.IsStarted(): #if the simulation hasn't been started

            dlg=wx.MessageDialog(self,"Do you wish to continue?","This will start a simulation",wx.OK|wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:

                self.server.StartSim('galaxy.py') #pass in dummy file as a config file

                (self.pipemain,pipeprocess)=mp.Pipe() #create pipe for sending data between processes
                self.frameno=mp.Value('i',0) #frameno is an integer, initialised to 0
                self.nfiles=mp.Value('i',0) #number of files available on server
                self.getdata=mp.Value('b',False) #flag to tell process to get new data
                self.newdata=mp.Value('b',False) #flag saying if process has new data ready

                #kick off process
                self.p=mp.Process(target=process,args=(self.frameno,self.nfiles,self.getdata,self.newdata,pipeprocess,self.demo,self.server))
                self.p.start() #start off process

                self.buttons[0].SetLabel("Stop Simulaton")

                self.CurrentFrame=0
                self.playing=False

                #start timer
                self.timer.Start(self.refreshrate*1000)
                self.buttons[1].Enable(True)
                self.buttons[2].Enable(True)
                self.buttons[3].Enable(True)
                self.buttons[4].Enable(True)
                self.buttons[5].Enable(True)

                self.getdata.value=True


        else: #if the simulation is already running
            dlg=wx.MessageDialog(self,"Are you sure?","This will stop the current simulation.",wx.OK|wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:
                print "Deleting Simulation"
                self.p.terminate()
                self.server.DeleteSim()
                self.buttons[0].SetLabel("Start Simulation")
                self.nfiles.value=0
                self.CurrentFrame=0
                self.playing=False
                self.buttons[1].SetLabel("Play")
                self.buttons[1].Enable(False)
                self.buttons[2].Enable(False)
                self.buttons[3].Enable(False)
                self.buttons[4].Enable(False)
                self.buttons[5].Enable(False)
                try:
                    self.renderer.RemoveActor(self.actor)
                except:
                    pass
                self.widget.GetRenderWindow().Render()

    #function that checks for new data from the process. If so, it downloads it and (if required) renders it
    def TimerCallback(self,e):
        if self.server.IsStarted():

            if self.newdata.value: #if new data is available

                if self.getdata.value: #if we have requested new data

                    data=self.pipemain.recv() #get data from process

                    self.CurrentFrame=self.frameno.value #set the current frame number to the one the process has just read in

                    if self.playing: #increment frame number by 1 and tell process to fetch it
                        self.frameno.value += 1
                        self.getdata.value=True
                    else: #we don't need any more data
                        self.getdata.value=False

                    self.pipemain.send(1)#read receipt

                    self.demo.RenderFrame(self,data) #render the data


                else: #we didn't request new data (likely someone hit 'pause' after a request for new data was put into the process). We don't need/want this data, so read it into a dummy array then do nothing
                    dummydata=self.pipemain.recv() #read data into dummy array and do nothing
                    self.pipemain.send(1)

            #update logger at bottom of screen to update current frame number, and total frame count
            self.logger.SetValue("Frame %d of %d"%(self.CurrentFrame,self.nfiles.value-1))
        else:
            self.logger.SetValue("")



    #play or pause (depending upon whether the )
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




    #Make sure any background processes are killed off when the main window is closed
    def OnClose(self,evt):
      print "Exiting Program..."
      try:
          self.p.terminate()
          print "Terminating processes"
      except:
          print "no process to be terminated"
      if self.server.IsStarted():
          print "Deleting simulation temp files"
          self.server.DeleteSim()
      print "Done!"
      self.Destroy()

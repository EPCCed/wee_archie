import wx
import vtk
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
import multiprocessing as mp
import time
from . import process

import abc




#define an abstract UI class which contains code to interact with server.
#Note that each demo MUST derive its own subclass of this class (in *demo_name*_UI.py), and modify existing/add new methods to customise the GUI to the demo's needs.


class AbstractUI(wx.Frame):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self,parent,title,demo,servercomm):
        wx.Frame.__init__(self,parent,title=title,size=(1000,800))
        self.demo=demo
        self.servercomm=servercomm

        #bind closing the window to the OnClose() method (kills the process and deletes the simulation from the server)
        self.Bind(wx.EVT_CLOSE,self.OnClose)

        #timer which periodically checks from process to see if there is new data avaiable etc.
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.TimerCallback,self.timer)


        #create vtk render widget and start it
        self.vtkwidget=wxVTKRenderWindowInteractor(self,wx.ID_ANY)
        
        #default refreshrate to 0.5s
        self.refreshrate=0.5
        

       
    
    # attach renderer to the vtk widget and draw axes
    @abc.abstractmethod
    def StartInteractor(self):

        print "Starting interactor"
        self.renderer=vtk.vtkRenderer()
        self.vtkwidget.GetRenderWindow().AddRenderer(self.renderer)
        camera=self.renderer.GetActiveCamera()
        camera.SetFocalPoint(0.,0.,0.)
        camera.SetPosition(50.,0.,0.)
        camera.Roll(-90)

        mouse=vtk.vtkInteractorStyleTrackballCamera()
        self.vtkwidget.SetInteractorStyle(mouse)

        #create some axes to indicate the orientation of the galaxy
        axes = vtk.vtkAxesActor()
        self.axisw=vtk.vtkOrientationMarkerWidget()
        self.axisw.SetOutlineColor( 0.9300, 0.5700, 0.1300 );
        self.axisw.SetOrientationMarker( axes );
        self.axisw.SetInteractor( self.vtkwidget._Iren );
        self.axisw.SetViewport( 0.0, 0.0, 0.3, 0.3 );
        self.axisw.SetEnabled( 1 );
        self.axisw.InteractiveOn();


        self.vtkwidget.GetRenderWindow().Render()

    
    #start the simulation
    @abc.abstractmethod
    def StartSim(self,config):
        
            self.servercomm.StartSim(config) #pass in config file 

            (self.pipemain,pipeprocess)=mp.Pipe() #create pipe for sending data between processes
            self.frameno=mp.Value('i',0) #frameno is an integer, initialised to 0
            self.nfiles=mp.Value('i',0) #number of files available on server
            self.getdata=mp.Value('b',False) #flag to tell process to get new data
            self.newdata=mp.Value('b',False) #flag saying if process has new data ready

            #kick off process
            self.p=mp.Process(target=process.process,args=(self.frameno,self.nfiles,self.getdata,self.newdata,pipeprocess,self.demo,self.servercomm))
            self.p.start() #start off process

            self.CurrentFrame=0
            
            #Start timer (argument to .Start is in milliseconds)
            self.timer.Start(self.refreshrate*1000)
    
    
    #stop the simulation
    @abc.abstractmethod
    def StopSim(self):

            print "Deleting Simulation"
            self.p.terminate()
            self.servercomm.DeleteSim()
            self.nfiles.value=0
            self.CurrentFrame=0
            self.timer.Stop()
                
               
    
    #function that checks for new data from the process. If so, it downloads it and (if required) renders it
    @abc.abstractmethod
    def TimerCallback(self,e):
        if self.servercomm.IsStarted():
            

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

        

    
    #Make sure any background processes are killed off when the main window is closed
    @abc.abstractmethod
    def OnClose(self,evt):
      print "Exiting Program..."
      try:
          self.p.terminate()
          print "Terminating processes"
      except:
          print "no process to be terminated"
      if self.servercomm.IsStarted():
          print "Deleting simulation temp files"
          self.servercomm.DeleteSim()
      print "Done!"
      self.Destroy()


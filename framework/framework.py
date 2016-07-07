import wx
import vtk
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
import multiprocessing as mp
import numpy as np
from netCDF4 import Dataset
import abc



#Entry point to the GUI. This method needs to be called in the demo
def Start(window_name,demo):
    app=wx.App(False)
    window=MyWindow(None,window_name,demo)
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
    



#process that reads a netcdf file into numpy arrays, and sends it to the main process
def process(frameno,pipe,demo): # frameno=shared variable containing current frame number, pipe = communication object, demo=object contaning demo-specific functions
    print "Process initiated"
    while True: #infinite loop
        frame=frameno.value #get frame number
        
        if (frame >= 0): #we have to read a file
            fname=demo.GetFilename(frame)
            try: #if there is a file of that name:
                
                root=Dataset(fname,"r")
                
                data=demo.GetVTKData(root)
                
                pipe.send(True) #we have data
            
                pipe.send(data) #send the data
                
                #find out if frame nuber is to be iterated
                iterate=pipe.recv()
                if iterate:
                    frameno.value += 1 #increment frame number
                    
            except: #if there is no such file
                print "Invalid frame number"
                pipe.send(False) #tell main process that there is no data
                frameno.value -= 1
                ok=pipe.recv() #receive instruction to iterate frame number (not used if frame number is invalid)
            
                
            
        else: #invalid (negative) frame number - don't read anything and set frame number to 0
            pipe.send(False) #no data
            frameno.value=0 #set frame to zero number
            iterate=pipe.recv() #read dummy value
            
        







        

#Create MyWindow class (subclass of wx.Frame - the wxWidgets equivalent of a window)
class MyWindow(wx.Frame):
    
    
    def __init__(self,parent,title,demo):
        wx.Frame.__init__(self,parent,title=title,size=(1000,800))
        self.demo=demo
        self.pipemain,pipeprocess=mp.Pipe() #create pipe for sending data betwee processes
        self.frameno=mp.Value('i',0) #frameno is an integer, initialised to 0
        self.p=mp.Process(target=process,args=(self.frameno,pipeprocess,self.demo))
        self.p.start() #start off process
                
        
        #bind closing the window to the OnClose() method (kills the process)
        self.Bind(wx.EVT_CLOSE,self.OnClose)
        
        #set up sizers that allow you to position window elements easily
        
        #main sizer - arrange items horizontally on screen (controls on left, vtk interactor on right)
        self.mainsizer=wx.BoxSizer(wx.HORIZONTAL)
        #sizer for buttons (align buttons vertically)
        self.buttonsizer=wx.BoxSizer(wx.VERTICAL)
        #sizer for step forward/back buttons
        self.weesizer=wx.BoxSizer(wx.HORIZONTAL)
        
        #set up a timer with an interval of 1000ms = 1second
        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.timercallback,self.timer)
        
        
        #create 'array' of buttons
        self.buttons=[]
        
        self.buttons.append(wx.Button(self,label='Play'))
        self.buttons.append(wx.Button(self,label='Pause'))
        self.buttons.append(wx.Button(self,label='Rewind'))
        self.buttons.append(wx.Button(self,label='<'))
        self.buttons.append(wx.Button(self,label='>'))

        
        
        #bind button clicks (wx.EVT_BUTTONT) to methods
        
        self.Bind(wx.EVT_BUTTON,self.play,self.buttons[0])
        self.Bind(wx.EVT_BUTTON,self.pause,self.buttons[1])
        self.Bind(wx.EVT_BUTTON,self.rewind,self.buttons[2])
        self.Bind(wx.EVT_BUTTON,self.stepback,self.buttons[3])
        self.Bind(wx.EVT_BUTTON,self.stepforward,self.buttons[4])

        
        #add buttons to the button (vertical) sizer
        self.buttonsizer.Add(self.buttons[0],1,wx.EXPAND)
        self.buttonsizer.Add(self.buttons[1],1,wx.EXPAND)
        self.buttonsizer.Add(self.buttons[2],1,wx.EXPAND)
        
        self.weesizer.Add(self.buttons[3],1,wx.EXPAND)
        self.weesizer.Add(self.buttons[4],1,wx.EXPAND)
        
        self.buttonsizer.Add(self.weesizer,1,wx.EXPAND)

        #add some vertical space
        self.buttonsizer.Add((10,800))
        
        #text at bottom that displays the current frame number
        self.logger = wx.TextCtrl(self, style=wx.TE_READONLY)
        self.buttonsizer.Add(self.logger,1,wx.EXPAND)
        
        
        #create vtk render widget
        self.widget=wxVTKRenderWindowInteractor(self,wx.ID_ANY)
        
        #add button sizer to the left panel of the main sizer, vtk widget to the right (with horizontal width ratio of 1:8)
        self.mainsizer.Add(self.buttonsizer,1,wx.EXPAND)
        self.mainsizer.Add(self.widget,8,wx.EXPAND)
        
        #attach main sizer to the window
        self.SetSizer(self.mainsizer)
        self.SetAutoLayout(1)
        self.mainsizer.Fit(self)
        
        #flag to determine if the vtk widget has been initialised (has a renderer attached)
        self.rendering=False
        self.StartInteractor() #start the interactor
        
        #create mapper 
        self.mapper=vtk.vtkPolyDataMapper()
        
        #show window
        self.Show()
        
        
        
        
        
    # attach renderer to the vtk widget and draw axes
    def StartInteractor(self):
        if self.rendering==False:
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
            
            self.rendering=True
            
        else:
            print "Interactor has already started"
            
            
            
            
            
          
    #make time move forward (play a 'movie' of the evolving galaxy)    
    def play(self,e):
        if self.rendering:
            print "Starting play"
            self.timer.Start(100) #start a timer with 100ms interval
        else:
            print "You need to start the interactor"
    
    
    
    
    
    # a timer callback that checks if there is new data on the process. If there is, read it from the process            
    def timercallback(self,e):
        if not self.GetFrame(iterate=True): #get and display new frame. if there isn't a new frame, stop the timer
            print "Stoping timer"
            self.timer.Stop()
        
    
    
    #Pause the movie (stop the timer) 
    def pause(self,e):
        if self.rendering:
            print "Pausing"
            self.timer.Stop()
        else:
            print "You need to start the interactor"
            
            
            
            
            
    
    #Go back to the first frame            
    def rewind(self,e):
        if self.rendering:
            print "Rewinding"
            self.timer.Stop()
            self.frameno.value=0
            
            self.SetFrame(0) #tell the process to read in frame 0
            self.GetFrame(iterate=False) #get frame 0, do not have the process read in the next file
            
        else:
            print "You need to start the interactor"
            
            
            
            
            
    #step one frame backwards  
    def stepback(self,e):
       # self.lock.acquire()
        val = self.frameno.value
       # self.lock.release()
        self.SetFrame(val-1)
        self.GetFrame(iterate=False)
        
        
        
        
    #step one frame forwards
    def stepforward(self,e):
      #  self.lock.acquire()
        val = self.frameno.value
      #  self.lock.release()
        self.SetFrame(val+1)
        self.GetFrame(iterate=False)

        
    
       
    #get a new frame's data from process        
    def GetFrame(self,iterate):
        
        test=self.pipemain.recv() #is there new data
        val = self.frameno.value #read frame number
      
        if (test): #if new data
            
            #display frame number at bottom of screen
            self.logger.SetValue("Frame %d"%val)
            
            #get new data
            data=self.pipemain.recv()
            
            #do we want process to read in the next file?
            if iterate:
                self.pipemain.send(True)
            else:
                self.pipemain.send(False)
            
            #render the frame
            self.demo.RenderFrame(self,data)
            
            return True #say yes, we have rendered something new
            
        else:
            self.pipemain.send(False) #send dummy acknowledgement
            print "Main program acking no data"
            return False #no we didn't render anythng new
        
        
        
        
        
        
    #tell process the frame number to read (for its next iteration)
    def SetFrame(self,number):
        test=self.pipemain.recv() #is there new data?
        self.frameno.value=number #set data number
        if test:
            dummy=self.pipemain.recv() #read the buffered data
        self.pipemain.send(False) #tell process not to update frame number
        #now the process will read in the frame number specified in 'number'
        
        

    #Make sure any background processes are killed off when the main window is closed 
    def OnClose(self,evt):
      print "Exiting Program - Terminating all processes"
      self.p.terminate()
      print "Done!"
      self.Destroy()
      
      
      
      




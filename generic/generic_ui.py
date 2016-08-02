import client
import vtk

#select the UI abstract superclass to derive from
UI=client.AbstractvtkUI

# Derive the demo-specific GUI class from the Abstract??UI class
class GenericWindow(UI):

    def __init__(self,parent,title,demo,servercomm):

        #call superclass' __init__
        UI.__init__(self,parent,title,demo,servercomm)

        #INSERT CODE HERE TO SET LAYOUT OF WINDOW/ADD BUTTONS ETC

        #start the vtkinteractor
        self.StartInteractor()

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
        UI.TimerCallback(self,e)
        #INSERT ANY CUSTOM CODE HERE




    def OnClose(self,e):
        UI.OnClose(self,e)
        #INSERT ANY CUSTOM CODE HERE



    #----------------------------------------------------------------------
    #------------- New methods specific to demo go here -------------------
    #----------------------------------------------------------------------

import client
import wx
import vtk




# Derive the demo-specific GUI class from the AbstractUI class
class GenericWindow(client.AbstractUI):

    def __init__(self,parent,title,demo,servercomm):

        #call superclass' __init__
        client.AbstractUI.__init__(self,parent,title,demo,servercomm)

        #INSERT CODE HERE TO SET LAYOUT OF WINDOW/ADD BUTTONS ETC

        #start the vtkinteractor
        self.StartInteractor()

        #show window
        self.Show()




    def StartInteractor(self):
        client.AbstractUI.StartInteractor(self)
        #INSERT ANY CUSTOM CODE HERE




    def StartSim(self,config):
        client.AbstractUI.StartSim(self,config)
        #INSERT ANY CUSTOM CODE HERE




    def StopSim(self):
        client.AbstractUI.StopSim(self)
        #INSERT ANY CUSTOM CODE HERE




    def TimerCallback(self,e):
        client.AbstractUI.TimerCallback(self,e)
        #INSERT ANY CUSTOM CODE HERE




    def OnClose(self,e):
        client.AbstractUI.OnClose(self,e)
        #INSERT ANY CUSTOM CODE HERE



    #----------------------------------------------------------------------
    #------------- New methods specific to demo go here -------------------
    #----------------------------------------------------------------------


    

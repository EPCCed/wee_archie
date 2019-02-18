import wx
from . import AbstractUI
import vtk
from vtk.wx.wxVTKRenderWindowInteractor import wxVTKRenderWindowInteractor
import abc


# An abstract class defining a UI with a vtk view window
class AbstractvtkUI(AbstractUI):
    #__metaclass__ = abc.ABCMeta

    #@abc.abstractmethod
    def __init__(self,parent,title,demo,servercomm):
        AbstractUI.__init__(self,parent,title,demo,servercomm)

        #create vtk render widget
        self.vtkwidget=wxVTKRenderWindowInteractor(self,wx.ID_ANY)




    # attach renderer to the vtk widget and draw axes
    #@abc.abstractmethod
    def StartInteractor(self):

        print("Starting interactor")
        self.renderer=vtk.vtkRenderer()
        self.vtkwidget.GetRenderWindow().AddRenderer(self.renderer)

        # allow click and drag interaction
        mouse=vtk.vtkInteractorStyleTrackballCamera()
        self.vtkwidget.SetInteractorStyle(mouse)




    #start the simulation
    #@abc.abstractmethod
    def StartSim(self,config):
        AbstractUI.StartSim(self,config)



    #stop the simulation
    #@abc.abstractmethod
    def StopSim(self):
        AbstractUI.StopSim(self)



    #function that checks for new data from the process. If so, it downloads it and (if required) renders it
    #@abc.abstractmethod
    def TimerCallback(self,e):
        AbstractUI.TimerCallback(self,e)


    #Make sure any background processes are killed off when the main window is closed
    #@abc.abstractmethod
    def OnClose(self,evt):
        AbstractUI.OnClose(self,evt)

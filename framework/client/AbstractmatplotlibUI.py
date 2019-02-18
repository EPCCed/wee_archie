import wx
from . import AbstractUI
import numpy as np
import matplotlib
matplotlib.use("WXAgg")

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import abc


# An abstract class defining a UI with a matplotlib view window
class AbstractmatplotlibUI(AbstractUI):
    #__metaclass__ = abc.ABCMeta

    #@abc.abstractmethod
    def __init__(self,parent,title,demo,servercomm):
        AbstractUI.__init__(self,parent,title,demo,servercomm)

        #set up matplotlib figure
        self.figure = Figure()
        #self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)



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

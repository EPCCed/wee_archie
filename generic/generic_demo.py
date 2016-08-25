import client

import vtk
import numpy as np
from netCDF4 import Dataset






#Data transfer object
class DTO(client.AbstractDTO):
    def SetData(self,data):
        self.Data=data

    def GetData(self):
        return self.Data




#class containing demo-specific functions
class GenericDemo(client.AbstractDemo):

    # read in data and convert it to a data transfer object
    def GetVTKData(self,root):

        #INSERT CODE TO READIN DATA FROM ROOT AND PREPARE IT FOR TRANSFER TO GUI

        dto=DTO()

        #INSERT CODE TO PUT DATA INTO DTO

        return dto


    # Renders a frame with data contained within the data transfer object, data
    def RenderFrame(self,win,dto):

        #INSERT CODE TO UNPACK DTO AND RENDER THE DATA IT CONTAINS
        #'win' IS THE GUI CLASS WHICH THE VTK RENDERER BELONGS TO

        #update renderer
        win.vtkwidget.GetRenderWindow().Render()

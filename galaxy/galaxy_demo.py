import client

import vtk
import numpy as np
from netCDF4 import Dataset
import sys





#Data transfer object
class DTO(client.AbstractDTO):
    def SetData(self,data):
        self.Data=data

    def GetData(self):
        return self.Data




#class containing demo-specific functions
class GalaxyDemo(client.AbstractDemo):

    # read in data and convert it to a data transfer object
    def GetVTKData(self,root): #root=netcdf handle

        #create numpy arrays
        x=root.variables['x'][:]
        y=root.variables['y'][:]
        z=root.variables['z'][:]

        n=x.size


        #create vtk objects from numpy arrays
        points=vtk.vtkPoints()
        vertices = vtk.vtkCellArray()

        #loop over points in data and add them to the vtkpoints and vtkvertices objects
        for i in range(0,n):
            id = points.InsertNextPoint(x[i],y[i],z[i])
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(id)


        # Create a polydata object
        galaxy = vtk.vtkPolyData()

        # Set the points and vertices we created as the geometry and topology of the polydata
        galaxy.SetPoints(points)
        galaxy.SetVerts(vertices)

        #create writer to write polydata to an xml string to be sent to main process
        writer=vtk.vtkXMLPolyDataWriter()
        writer.SetInputData(galaxy)
        writer.WriteToOutputStringOn()
        writer.Write()
        xml=writer.GetOutputString()

        #create data transfer object and put the xml string into it
        data=DTO()
        data.SetData(xml)
        return data


    # Renders a frame with data contained within the data transfer object, data
    def RenderFrame(self,win,data):

        #unpack xml string from data transfer object
        xml=data.GetData()

        #read in xml data
        reader=vtk.vtkXMLPolyDataReader()
        reader.ReadFromInputStringOn()
        reader.SetInputString(xml)
        reader.Update()


        #update mapper
        try:
            win.mapper
        except:
            win.mapper=vtk.vtkPolyDataMapper()
            
        win.mapper.SetInputConnection(reader.GetOutputPort())


        try: #does the actor exist? if not, create one
            win.actor
        except:
            win.actor=vtk.vtkActor()
            win.renderer.AddActor(win.actor)
            win.actor.SetMapper(win.mapper)


        #update renderer
        win.vtkwidget.GetRenderWindow().Render()




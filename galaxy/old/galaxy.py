import vtk
import numpy as np
from netCDF4 import Dataset
import sys

sys.path.append('../framework/')
import framework



#********************* CODE SPECIFIC TO DEMO ********************************

#Data transfer object
class DTO:
    def SetData(self,data):
        self.Data=data

    def GetData(self):
        return self.Data




#class containing demo-specific functions
class galaxydemo(framework.abstractdemo):

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
        win.mapper.SetInputConnection(reader.GetOutputPort())


        try: #does the actor exist? if not, create one
            win.actor
        except:
            win.actor=vtk.vtkActor()
            win.renderer.AddActor(win.actor)
            win.actor.SetMapper(win.mapper)


        #update renderer
        win.widget.GetRenderWindow().Render()


    def GetFilename(self,num):
        return "data/data%5.5d.nc"%num #get filename


#************************** END OF DEMO SPECIFIC CODE ******************************


#Launch demo
if __name__ == '__main__':
    demo=galaxydemo()
    server=framework.Serverclass("GALAXY")
    framework.Start("Galaxy Simulator",demo,server)

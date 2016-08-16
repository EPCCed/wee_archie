import client
import vtk
import random
import time

#Data transfer object
class DTO(client.AbstractDTO):
    def SetData(self, data):
        self.Data=data

    def GetData(self):
        return self.Data

#class containing demo-specific functions
class WeatherDemo(client.AbstractDemo):

    # read in data and convert it to a data transfer object
    def GetVTKData(self, root): # root=netcdf handle

        q = root.variables['q']

        rm = root.variables['ground_rain'][:]

        coords = root.variables['q'].shape[1:]

        vapor = (q[0] / 0.018) - 0.08  # return normalized vapor field data

        clouds = (q[1] - 0.00004)/ q[1].max()  # return normalized cloud data
        rain = (q[2]/q[2].max())
        data = [vapor, clouds, rain, coords, rm]

        # create data transfer object and put the array into it
        dto = DTO()
        dto.SetData(data)


        return dto

    # Renders a frame with data contained within the data transfer object, data
    def RenderFrame(self, win, dto):


        #unpack  data transfer object
        data = dto.GetData()
        vapor, clouds, rain, coords, rm = data
        win.renderer.SetBackground(0.22,.67,.87)
        x, y, z = coords

        glyph3D, colors, col, surf = RenderCloud(clouds, coords, rain)

        # update mapper
        try:
            win.mappers['CloudMapper']
        except:
            win.mappers['CloudMapper'] = vtk.vtkPolyDataMapper()

        win.mappers['CloudMapper'].SetInputConnection(surf.GetOutputPort())
        win.mappers['CloudMapper'].SetScalarModeToUsePointFieldData()
        win.mappers['CloudMapper'].SetScalarRange(0, 3)
        win.mappers['CloudMapper'].SelectColorArray("Ccol")  # // !!!to set color (nevertheless you will have nothing)
        win.mappers['CloudMapper'].SetLookupTable(colors)


        try:  # does the actor exist? if not, create one
            win.actors['CloudActor']
        except:
            win.actors['CloudActor'] = vtk.vtkActor()
            win.actors['CloudActor'].GetProperty().SetOpacity(1.0)
            win.renderer.AddActor(win.actors['CloudActor'])
            win.actors['CloudActor'].SetMapper(win.mappers['CloudMapper'])

        ################# SEA  #############################

        Sglyph3D, Ssurf = RenderSea(data[1], coords)

        # update mapper
        try:
            win.mappers['SeaMapper']
        except:
            win.mappers['SeaMapper'] = vtk.vtkPolyDataMapper()

        win.mappers['SeaMapper'].SetInputConnection(Ssurf.GetOutputPort())
        win.mappers['SeaMapper'].SetScalarModeToUsePointFieldData()
        win.mappers['SeaMapper'].SetScalarRange(0, 3)

        try:  # does the actor exist? if not, create one
            win.actors['SeaActor']
        except:
            win.actors['SeaActor'] = vtk.vtkActor()
            win.actors['SeaActor'].GetProperty().SetOpacity(1.)
            win.actors['SeaActor'].GetProperty().SetColor(0., 0.412, 0.58)
            win.renderer.AddActor(win.actors['SeaActor'])
            win.actors['SeaActor'].SetMapper(win.mappers['SeaMapper'])
        ################# LAND  #############################

        Lglyph3D, Lsurf = RenderLand(coords)

        # update mapper
        try:
            win.mappers['LandMapper']
        except:
            win.mappers['LandMapper'] = vtk.vtkPolyDataMapper()

            win.mappers['LandMapper'].SetInputConnection(Lsurf.GetOutputPort())
            win.mappers['LandMapper'].SetScalarModeToUsePointFieldData()
            win.mappers['LandMapper'].SetScalarRange(0, 3)

        try:  # does the actor exist? if not, create one
            win.actors['LandActor']
        except:
            win.actors['LandActor'] = vtk.vtkActor()
            win.actors['LandActor'].GetProperty().SetOpacity(1.0)
            win.actors['LandActor'].GetProperty().SetColor(0.475, 0.31, 0.09)
            win.renderer.AddActor(win.actors['LandActor'])
            win.actors['LandActor'].SetMapper(win.mappers['LandMapper'])


            #####VAPOR POINTZ########
        if win.vapor is True:

            Vglyph3D, Vcolors, Vcol = RenderVapor(vapor, coords)

            # update mapper
            try:
                win.mappers['VaporPMapper']
            except:
                win.mappers['VaporPMapper'] = vtk.vtkPolyDataMapper()

            win.mappers['VaporPMapper'].SetInputConnection(Vglyph3D.GetOutputPort())
            win.mappers['VaporPMapper'].SetScalarModeToUsePointFieldData()
            win.mappers['VaporPMapper'].SetScalarRange(0, 3)
            win.mappers['VaporPMapper'].SelectColorArray("Vcol")  # // !!!to set color (nevertheless you will have nothing)
            win.mappers['VaporPMapper'].SetLookupTable(Vcolors)

            try:  # does the actor exist? if not, create one
                win.actors['VaporPActor']
            except:
                win.actors['VaporPActor'] = vtk.vtkActor()
                win.actors['VaporPActor'].GetProperty().SetOpacity(0.2)
                win.actors['VaporPActor'].SetMapper(win.mappers['VaporPMapper'])

            win.renderer.AddActor(win.actors['VaporPActor'])
        else:
            try:
                win.renderer.RemoveActor(win.actors['VaporPActor'])
            except:
                pass

###########RAIN MASS

        Rglyph3D, Rcolors, Rcol = RenderRain(rain, coords)

        # update mapper
        try:
            win.mappers['RainMapper']
        except:
            win.mappers['RainMapper'] = vtk.vtkPolyDataMapper()
        win.mappers['RainMapper'].SetInputConnection(Rglyph3D.GetOutputPort())
        win.mappers['RainMapper'].SetScalarRange(0, 3)

        win.mappers['RainMapper'].SetScalarModeToUsePointFieldData()
        win.mappers['RainMapper'].SelectColorArray("Rcol")  # // !!!to set color (nevertheless you will have nothing)
        win.mappers['RainMapper'].SetLookupTable(Rcolors)

        try:  # does the actor exist? if not, create one
            win.actors['RainActor']
        except:
            win.actors['RainActor'] = vtk.vtkActor()
            win.actors['RainActor'].GetProperty().SetOpacity(0.1)
            win.actors['RainActor'].SetMapper(win.mappers['RainMapper'])

        win.renderer.AddActor(win.actors['RainActor'])

    ################## CROPS

        win.rainmass += sum(sum(rm))
        print(win.rainmass)

        crops = RenderCrops(5, coords)

        # update mapper
        try:
            win.mappers['CropsMapper']
        except:
            win.mappers['CropsMapper'] = vtk.vtkPolyDataMapper()
        win.mappers['CropsMapper'].SetInputData(crops)

        try:  # does the actor exist? if not, create one
            win.actors['CropsActor']
        except:
            win.actors['CropsActor'] = vtk.vtkActor()
        win.actors['CropsActor'].GetProperty().SetOpacity(1.0)
        win.actors['CropsActor'].GetProperty().SetLineWidth(10)
        win.actors['CropsActor'].GetProperty().SetColor(0.39, 0.65, 0.04)
        win.actors['CropsActor'].SetMapper(win.mappers['CropsMapper'])

        win.renderer.AddActor(win.actors['CropsActor'])

########### CAMERA SETTINGS

        try:
            win.camera
        except:
            win.camera = win.renderer.GetActiveCamera()
            win.camera.SetFocalPoint(y/2,z/2,x/2)
            win.camera.Azimuth(110)
            win.camera.Elevation(50)
            win.camera.Dolly(0.3)


        ###########OUTLINE BOX

        outlineglyph3D, outlinecolors, outlinecol = RenderOutline(coords)

        try:
            win.filters['Outline']
        except:
            win.filters['Outline'] = vtk.vtkOutlineFilter()
            win.filters['Outline'].SetInputData(outlineglyph3D.GetOutput())

            outlineMapper = vtk.vtkPolyDataMapper()
            outlineMapper.SetInputConnection(win.filters['Outline'].GetOutputPort())
            outlineMapper.SetScalarModeToUsePointFieldData()
            outlineMapper.SetScalarRange(0, 3)
            outlineMapper.SelectColorArray("cols")
            outlineMapper.SetLookupTable(outlinecolors)

            outlineActor = vtk.vtkActor()
            outlineActor.SetMapper(outlineMapper)
            outlineActor.GetProperty().SetColor(1, 1, 1)
            #win.renderer.AddActor(outlineActor)


        # # screenshot code:
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(win.vtkwidget.GetRenderWindow())
        w2if.Update()

        writer = vtk.vtkPNGWriter()
        savename = str(time.time()) + '.png'
        writer.SetFileName(savename)
        writer.SetInputData(w2if.GetOutput())
        #writer.Write()

        win.vtkwidget.GetRenderWindow().Render()


def RenderOutline(coords):

    x,y,z = coords
    points = vtk.vtkPoints()

    cols = vtk.vtkFloatArray()
    cols.SetName("cols")

    colors = vtk.vtkLookupTable()
    colors.SetNumberOfTableValues(1)
    colors.SetTableValue(0, 1.0, 1.0, 1.0, 0.0)  # black

    ### for the outline, don't ask
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(0, 0, x)
    points.InsertNextPoint(0, y, 0)
    points.InsertNextPoint(0, y, 9)
    points.InsertNextPoint(z, 0, 0)
    points.InsertNextPoint(z, 0, x)
    points.InsertNextPoint(z, y, 0)
    points.InsertNextPoint(z, y, x)

    cols.InsertNextValue(0)
    cols.InsertNextValue(0)
    cols.InsertNextValue(0)
    cols.InsertNextValue(0)
    cols.InsertNextValue(0)
    cols.InsertNextValue(0)
    cols.InsertNextValue(0)
    cols.InsertNextValue(0)

    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.GetPointData().AddArray(cols)

    sphere = vtk.vtkSphereSource()

    glyph3D = vtk.vtkGlyph3D()

    glyph3D.SetSourceConnection(sphere.GetOutputPort())
    glyph3D.SetInputData(grid)
    glyph3D.Update()

    return glyph3D, colors, cols


def RenderCloud(cloud,coords, rain):

    x,y,z = coords
    print("Coods ", coords)

    points = vtk.vtkPoints()

    scales = vtk.vtkFloatArray()
    scales.SetName("scales")

    col = vtk.vtkUnsignedCharArray()
    col.SetName('Ccol')  # Any name will work here.
    col.SetNumberOfComponents(3)

    nc = vtk.vtkNamedColors()

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.Build()

    # Fill in a few known colors, the rest will be generated if needed
    lut.SetTableValue(0, nc.GetColor4d("Black"))
    lut.SetTableValue(1, nc.GetColor4d("Banana"))
    lut.SetTableValue(2, nc.GetColor4d("Tomato"))
    lut.SetTableValue(3, nc.GetColor4d("Wheat"))
    lut.SetTableValue(4, nc.GetColor4d("Lavender"))
    lut.SetTableValue(5, nc.GetColor4d("Flesh"))
    lut.SetTableValue(6, nc.GetColor4d("Raspberry"))
    lut.SetTableValue(7, nc.GetColor4d("Salmon"))
    lut.SetTableValue(8, nc.GetColor4d("Mint"))
    lut.SetTableValue(9, nc.GetColor4d("Peacock"))

    for i in range(z):
        for j in range(y):
            for k in range(x):
                if cloud[k][j][i] > 0:
                    #print(i,j,k)
                    points.InsertNextPoint(j, i, k)
                    scales.InsertNextValue(1)  # random radius between 0 and 0.99
                    #rgb = [0.0, 0.0, 0.0]
                    #lut.GetColor(rain[k][j][i], rgb)
                    #ucrgb = list(map(int, [x * 255 for x in rgb]))
                    #col.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.GetPointData().AddArray(scales)
    grid.GetPointData().SetActiveScalars("scales")  # // !!!to set radius first
    #grid.GetPointData().AddArray(col)

    sphere = vtk.vtkSphereSource()

    glyph3D = vtk.vtkGlyph3D()
    glyph3D.SetSourceConnection(sphere.GetOutputPort())
    glyph3D.SetInputData(grid)
    glyph3D.Update()

    polydata = vtk.vtkPolyData()

    polydata.SetPoints(points)
    #polydata.GetPointData().SetScalars(col)

    splatter = vtk.vtkGaussianSplatter()

    splatter.SetInputData(polydata)
    #splatter.SetSampleDimensions(50, 50, 50)
    splatter.SetRadius(0.07)
    #splatter.ScalarWarpingOff()

    cf = vtk.vtkContourFilter()

    if points.GetNumberOfPoints() > 0:
        cf.SetInputConnection(splatter.GetOutputPort())
    else: #weird things happen if you give him a splatter with no points
        cf.SetInputData(polydata)

    cf.SetValue(0, 0.01)

    reverse = vtk.vtkReverseSense()
    reverse.SetInputConnection(cf.GetOutputPort())
    reverse.ReverseCellsOn()
    reverse.ReverseNormalsOn()

    return glyph3D, lut, col, reverse


def RenderVapor(vapor, coords):

    x, y, z = coords
    points = vtk.vtkPoints()

    scales = vtk.vtkFloatArray()
    scales.SetName("Vscales")

    col = vtk.vtkUnsignedCharArray()
    col.SetName('Vcol')  # Any name will work here.
    col.SetNumberOfComponents(3)

    nc = vtk.vtkNamedColors()

    tableSize = x * y * z
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tableSize)
    lut.Build()

    # Fill in a few known colors, the rest will be generated if needed
    lut.SetTableValue(0, nc.GetColor4d("Black"))
    lut.SetTableValue(1, nc.GetColor4d("Banana"))
    lut.SetTableValue(2, nc.GetColor4d("Tomato"))
    lut.SetTableValue(3, nc.GetColor4d("Wheat"))
    lut.SetTableValue(4, nc.GetColor4d("Lavender"))
    lut.SetTableValue(5, nc.GetColor4d("Flesh"))
    lut.SetTableValue(6, nc.GetColor4d("Raspberry"))
    lut.SetTableValue(7, nc.GetColor4d("Salmon"))
    lut.SetTableValue(8, nc.GetColor4d("Mint"))
    lut.SetTableValue(9, nc.GetColor4d("Peacock"))

    for k in range(x):
        for j in range(y):
            for i in range(z):
                if vapor[k][j][i] > 0.85:
                    points.InsertNextPoint(j, i, k)
                    scales.InsertNextValue(1)
                    rgb = [0.0, 0.0, 0.0]
                    lut.GetColor(vapor[k][j][i], rgb)
                    ucrgb = list(map(int, [x * 255 for x in rgb]))
                    col.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.GetPointData().AddArray(scales)
    grid.GetPointData().SetActiveScalars("scales")  # // !!!to set radius first
    grid.GetPointData().AddArray(col)

    sphere = vtk.vtkSphereSource()

    glyph3D = vtk.vtkGlyph3D()

    glyph3D.SetSourceConnection(sphere.GetOutputPort())
    glyph3D.SetInputData(grid)
    glyph3D.Update()

    return glyph3D, lut, col


def RenderRain(rain, coords):

    x, y, z = coords
    points = vtk.vtkPoints()

    scales = vtk.vtkFloatArray()
    scales.SetName("Rscales")

    col = vtk.vtkUnsignedCharArray()
    col.SetName('Rcol')  # Any name will work here.
    col.SetNumberOfComponents(3)

    nc = vtk.vtkNamedColors()

    tableSize = x * y * z
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(200)
    lut.SetHueRange(0.65, 0.53)
    lut.SetAlphaRange(0.6,0.7)
    lut.Build()



    for k in range(x):
        for j in range(y):
            for i in range(z):
                if rain[k][j][i] > 0.0000001:
                    points.InsertNextPoint(j, i, k)
                    scales.InsertNextValue(1)
                    rgb = [0.0, 0.0, 0.0]
                    lut.GetColor(rain[k][j][i], rgb)
                    ucrgb = list(map(int, [x * 255 for x in rgb]))
                    col.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.GetPointData().AddArray(scales)
    grid.GetPointData().SetActiveScalars("Rscales")  # // !!!to set radius first
    grid.GetPointData().AddArray(col)

    sphere = vtk.vtkSphereSource()

    glyph3D = vtk.vtkGlyph3D()

    glyph3D.SetSourceConnection(sphere.GetOutputPort())
    glyph3D.SetInputData(grid)
    glyph3D.Update()

    return glyph3D, lut, col


def RenderSea(sealevel, coords):

    x,y,z = coords

    points = vtk.vtkPoints()

    sealevel = -5 #(-5 ,1)

    for k in range(x):
        for j in range(-20, int((y*0.6))):
            for i in range(-10,sealevel):
                points.InsertNextPoint(j, i, k)

    for k in range(x):
        for j in range(-20, int((y*0.6))):
            for i in range(sealevel,sealevel+1):
                if random.random()>0.85:
                    points.InsertNextPoint(j, i, k)

    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)

    sphere = vtk.vtkSphereSource()

    glyph3D = vtk.vtkGlyph3D()

    glyph3D.SetSourceConnection(sphere.GetOutputPort())
    glyph3D.SetInputData(grid)
    glyph3D.Update()

    polydata = vtk.vtkPolyData()

    polydata.SetPoints(points)

    splatter = vtk.vtkGaussianSplatter()

    splatter.SetInputData(polydata)
    #splatter.SetSampleDimensions(50, 50, 50)
    splatter.SetRadius(0.05)
    #splatter.ScalarWarpingOff()

    cf = vtk.vtkContourFilter()
    cf.SetInputConnection(splatter.GetOutputPort())
    cf.SetValue(0, 0.05)

    reverse = vtk.vtkReverseSense()
    reverse.SetInputConnection(cf.GetOutputPort())
    reverse.ReverseCellsOn()
    reverse.ReverseNormalsOn()


    return glyph3D, reverse


def RenderLand(coords):

    x,y,z = coords

    points = vtk.vtkPoints()

    for k in range(x):
        for j in range(y-int((y*0.4)), y+20):
            for i in range(-5,3):
                points.InsertNextPoint(j, i, k)

    for k in range(x):
        for j in range(y-int((y*0.4)), y+20):
            for i in range(3,4):
                if random.random()>0.9:
                    points.InsertNextPoint(j, i, k)

    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)

    sphere = vtk.vtkSphereSource()

    glyph3D = vtk.vtkGlyph3D()

    glyph3D.SetSourceConnection(sphere.GetOutputPort())
    glyph3D.SetInputData(grid)
    glyph3D.Update()

    polydata = vtk.vtkPolyData()

    polydata.SetPoints(points)

    splatter = vtk.vtkGaussianSplatter()

    splatter.SetInputData(polydata)
    splatter.SetRadius(0.06)

    cf = vtk.vtkContourFilter()
    cf.SetInputConnection(splatter.GetOutputPort())
    cf.SetValue(0, 0.05)

    reverse = vtk.vtkReverseSense()
    reverse.SetInputConnection(cf.GetOutputPort())
    reverse.ReverseCellsOn()
    reverse.ReverseNormalsOn()


    return glyph3D, reverse


def RenderCrops(level, coords):

    x, y, z = coords
    points = vtk.vtkPoints()


    for k in range(x):
        for j in range(y-int((y*0.4)), y+20):
                points.InsertNextPoint(j, 2, k)
                points.InsertNextPoint(j, level, k)

    # Create a polydata to store everything in
    linesPolyData = vtk.vtkPolyData()
    linesPolyData.Allocate()

    for i in range(0, points.GetNumberOfPoints(),2 ):
        linesPolyData.InsertNextCell(vtk.VTK_LINE, 2, [i, i+1])

    # Add the points to the dataset
    linesPolyData.SetPoints(points)

    return linesPolyData


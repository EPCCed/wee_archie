import client
import vtk
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

        vapor = (q[0] / 0.018) - 0.08  # return normalized vapor field data

        clouds = (q[1] - 0.00004)/ q[1].max()  # return normalized cloud data
        rain = (q[2]/q[2].max())
        data = [vapor, clouds, rain]

        # create data transfer object and put the array into it
        dto = DTO()
        dto.SetData(data)


        return dto

    # Renders a frame with data contained within the data transfer object, data
    def RenderFrame(self, win, dto):
        x, y, z = coords = [10, 64, 76]
        #unpack  data transfer object
        data = dto.GetData()
        win.renderer.SetBackground(1,.7,1)

# ############### VAPOR FIELD  PLANE####################################
        #print(win.vapor)
        plane = RenderVaporPlane(data[0])
         #update mapper

        try:
            win.mappers['VaporMapper']
        except:
            win.mappers['VaporMapper'] = vtk.vtkPolyDataMapper()
            win.mappers['VaporMapper'].SetInputConnection(plane.GetOutputPort())

        try:
            win.actors['VaporActor']
        except:
            win.actors['VaporActor'] = vtk.vtkActor()
            win.actors['VaporActor'].SetMapper(win.mappers['VaporMapper'])
            #win.renderer.AddActor(win.actors['VaporActor'])

################# CLOUD FIELD #############################

        glyph3D, colors, col, surf = RenderCloud(data[1], coords)

        # update mapper
        try:
            win.mappers['CloudMapper']
        except:
            win.mappers['CloudMapper'] = vtk.vtkPolyDataMapper()

        win.mappers['CloudMapper'].SetInputConnection(surf.GetOutputPort())
        win.mappers['CloudMapper'].SetScalarModeToUsePointFieldData()
        win.mappers['CloudMapper'].SetScalarRange(0, 3)
        win.mappers['CloudMapper'].SelectColorArray("col")  # // !!!to set color (nevertheless you will have nothing)
        win.mappers['CloudMapper'].SetLookupTable(colors)

        try:  # does the actor exist? if not, create one
            win.actors['CloudActor']
        except:
            win.actors['CloudActor'] = vtk.vtkActor()
            win.actors['CloudActor'].GetProperty().SetOpacity(0.6)
            win.renderer.AddActor(win.actors['CloudActor'])
            win.actors['CloudActor'].SetMapper(win.mappers['CloudMapper'])

#####VAPOR POINTZ########
        if win.vapor is True:

            Vglyph3D, Vcolors, Vcol = RenderVapor(data[0], coords)

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
                print('lala')

###########RAIN MASS

        Rglyph3D, Rcolors, Rcol = RenderRain(data[2], coords)

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
        try:
            win.camera
        except:
            win.camera = win.renderer.GetActiveCamera()
            win.camera.SetFocalPoint(y/2,z/2,x/2)
            win.camera.Azimuth(110)
            win.camera.Elevation(50)
            win.camera.Dolly(0.3)

        outlineglyph3D, outlinecolors, outlinecol = RenderOutline()

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
            win.renderer.AddActor(outlineActor)


        # # screenshot code:
        w2if = vtk.vtkWindowToImageFilter()
        w2if.SetInput(win.vtkwidget.GetRenderWindow())
        w2if.Update()

        writer = vtk.vtkPNGWriter()
        savename = str(time.time()) + '.png'
        writer.SetFileName(savename)
        writer.SetInputData(w2if.GetOutput())
        writer.Write()

        win.vtkwidget.GetRenderWindow().Render()


def RenderOutline():
    points = vtk.vtkPoints()

    cols = vtk.vtkFloatArray()
    cols.SetName("cols")

    colors = vtk.vtkLookupTable()
    colors.SetNumberOfTableValues(1)
    colors.SetTableValue(0, 1.0, 1.0, 1.0, 0.0)  # black

    ### for the outline, don't ask
    points.InsertNextPoint(0, 0, 0)
    points.InsertNextPoint(0, 0, 9)
    points.InsertNextPoint(0, 75, 0)
    points.InsertNextPoint(0, 75, 9)
    points.InsertNextPoint(63, 0, 0)
    points.InsertNextPoint(63, 0, 9)
    points.InsertNextPoint(63, 75, 0)
    points.InsertNextPoint(63, 75, 9)

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
def RenderCloud(cloud,coords):

    x,y,z = coords

    points = vtk.vtkPoints()

    scales = vtk.vtkFloatArray()
    scales.SetName("scales")

    col = vtk.vtkFloatArray()
    col.SetName("col")

    colors = vtk.vtkLookupTable()
    colors.SetNumberOfTableValues(4)
    #colors.SetTableValue(0, 1.0, 1.0, 1.0, 0.0)  # black
    colors.SetTableValue(0, 1.0, 1.0, 1.0, 1.0)  # black
    colors.SetTableValue(1, 0.7, 0.7, 0.7, 1.0)  # black
    colors.SetTableValue(2, 0.5, 0.5, 0.5, 1.0)  # black
    colors.SetTableValue(3, 0.3, 0.3, 0.3, 1.0)  # bldack
    # colors.SetTableValue(3 ,1.0 ,1.0 ,0.0 ,1.0); # yellow
    # the last double value is for opacity (1->max, 0->min)

    for k in range(x):
        for j in range(y):
            for i in range(z):
                if cloud[k][j][i] > 0:
                    points.InsertNextPoint(j, i, k)
                    scales.InsertNextValue(3)  # random radius between 0 and 0.99
                    col.InsertNextValue(cloud[k][j][i])  # random color label

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

    polydata = vtk.vtkPolyData()

    polydata.SetPoints(points)

    splatter = vtk.vtkGaussianSplatter()

    splatter.SetInputData(polydata)
    #splatter.SetSampleDimensions(50, 50, 50)
    splatter.SetRadius(0.07)
    #splatter.ScalarWarpingOff()

    cf = vtk.vtkContourFilter()
    cf.SetInputConnection(splatter.GetOutputPort())
    cf.SetValue(0, 0.01)

    reverse = vtk.vtkReverseSense()
    reverse.SetInputConnection(cf.GetOutputPort())
    reverse.ReverseCellsOn()
    reverse.ReverseNormalsOn()


    return glyph3D, colors, col, reverse
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
                if rain[k][j][i] > 0.000000000:
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

def RenderVaporPlane(qn):

    #  Get the lookup tables mapping cell data to colors
    nc = vtk.vtkNamedColors()

    plane = vtk.vtkPlaneSource()
    plane.SetXResolution(64)
    plane.SetYResolution(76)
    #  Force an update so we can set cell data
    plane.Update()

    tableSize = 64 * 76
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

    colorData = vtk.vtkUnsignedCharArray()
    colorData.SetName('colors')  # Any name will work here.
    colorData.SetNumberOfComponents(3)

    for i in range(76):
        for j in range(64):
            rgb = [0.0, 0.0, 0.0]
            lut.GetColor(qn[0][j][i], rgb)
            ucrgb = list(map(int, [x * 255 for x in rgb]))
            colorData.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

    plane.GetOutput().GetCellData().SetScalars(colorData)

    return plane

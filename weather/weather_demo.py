import client
import vtk
import random
import time
import math

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

        timepersec = root.variables['time_per_sec'][0]

        overalltime = root.variables['overall_time'][:]
        communicationtime =root.variables['communication_time'][:]

        data = [vapor, clouds, rain, coords, rm, timepersec, overalltime, communicationtime]

        # create data transfer object and put the array into it
        dto = DTO()
        dto.SetData(data)

        return dto

    # Renders a frame with data contained within the data transfer object, data
    def RenderFrame(self, win, dto):


        #unpack  data transfer object
        data = dto.GetData()
        vapor, clouds, rain, coords, rm, timepersec, overalltime, commtime = data

        win.renderer.SetBackground(0.22,.67,.87)
        win.renderer.SetViewport(0, 0.3, 1, 1)
        win.bottomrenderer.SetViewport(0,0,1,0.3)
        x, y, z = coords

        try:
            win.actors['TimePerSecActor']
        except:
            win.actors['TimePerSecActor'] = vtk.vtkTextActor()

        win.actors['TimePerSecActor'].SetInput(str(round(timepersec,2)) + " SPS")
        #win.actors['TimePerSecActor'].SetDisplayPosition(20, 900)
        #win.actors['TimePerSecActor'].GetTextProperty().SetFontSize(42)
        win.actors['TimePerSecActor'].GetTextProperty().SetColor(1.0, 0.0, 0.0)

        text_representation = vtk.vtkTextRepresentation()
        text_representation.GetPositionCoordinate().SetValue(0.5, 0.5)
        text_representation.GetPosition2Coordinate().SetValue(0.2, 0.2)
        text_representation.SetPosition(0,0.8)

        try:
            win.widgets['SPSWidget']
        except:
            win.widgets['SPSWidget'] = vtk.vtkTextWidget()
            win.widgets['SPSWidget'].SetRepresentation(text_representation)

        win.widgets['SPSWidget'].SetInteractor(win.vtkwidget.GetRenderWindow().GetInteractor())
        win.widgets['SPSWidget'].SetTextActor(win.actors['TimePerSecActor'])
        win.widgets['SPSWidget'].SelectableOff()
        win.widgets['SPSWidget'].On()

        #win.renderer.AddActor2D(win.actors['TimePerSecActor'])

        ### Clouds
        try:
            win.actors['CloudActor']
        except:
            win.actors['CloudActor'] = vtk.vtkActor()

        RenderCloud(clouds, coords, win.actors['CloudActor'])
        win.renderer.AddActor(win.actors['CloudActor'])

        ### Sea
        try:
            win.actors['SeaActor']
        except:
            win.actors['SeaActor'] = vtk.vtkActor()

        RenderSea(win.waterlevel, coords, win.renderer, win.actors['SeaActor'])

        win.renderer.AddActor(win.actors['SeaActor'])

        ### Land
        if win.frameno.value == 0:
            #TODO landactor try
            RenderLand(coords, win.renderer)

            RenderDecompGrid(coords, win.renderer, win.columnsinX, win.columnsinY)


        ### Vapor, TODO
        if win.vapor is True:

            try:  # does the actor exist? if not, create one
                win.actors['VaporPActor']
            except:
                win.actors['VaporPActor'] = vtk.vtkActor()

            RenderVapor(vapor, coords, win.actors['VaporPActor'])

            win.renderer.AddActor(win.actors['VaporPActor'])
        else:
            try:
                win.renderer.RemoveActor(win.actors['VaporPActor'])
            except:
                pass

        ### Rain
        try:
            win.actors['RainActor']
        except:
            win.actors['RainActor'] = vtk.vtkActor()

        RenderRain(rain, coords, win.actors['RainActor'])
        win.renderer.AddActor(win.actors['RainActor'])

        ### Crops
        try:  # does the actor exist? if not, create one
            win.actors['CropsActor']
        except:
            win.actors['CropsActor'] = vtk.vtkActor()

        win.rainmass += sum(sum(rm))
        if win.rainmass < 1.5:
            win.cropslevel = int(win.rainmass * 3) + 2
        else:
            if win.cropslevel > 4:
                win.cropslevel -= 1
            else:
                win.cropslevel = 4

        RenderCrops(win.cropslevel, coords, win.actors['CropsActor'])

        if win.rainmass > 1.5:
            win.actors['CropsActor'].GetProperty().SetColor(0, 0, 0)

        win.renderer.AddActor(win.actors['CropsActor'])

        ### Camera settings

        try:
            win.camera
        except:
            win.camera = win.renderer.GetActiveCamera()
            win.camera.SetFocalPoint(int(x/2),int(y/2),int(z/2))
            win.camera.Roll(80)
            win.camera.Dolly(0.35)
            win.camera.Elevation(70)
            win.camera.Roll(50)
            win.camera.Azimuth(180)
            win.camera.Elevation(-30)

        # Uncomment if you want to get a screenshot of every frame, see function description
        #Screenshot(win.vtkwidget.GetRenderWindow())

        #win.vtkwidget.GetRenderWindow.SetFullScreen(False)
        #win.vtkwidget.GetRenderWindow().FullScreenOn()

        ### Render the barplot
        try:
            win.views['BarPlot']
        except:
            win.views['BarPlot'] = vtk.vtkContextView()

        try:
            win.views['BarPlot'].GetScene().RemoveItem(0)
        except:
            pass

        ratio = commtime / overalltime
        chart = RenderPlot(ratio)

        win.views['BarPlot'].GetScene().AddItem(chart)
        win.views['BarPlot'].GetRenderer().SetViewport(0,0,1,0.3)

        win.vtkwidget.GetRenderWindow().AddRenderer(win.views['BarPlot'].GetRenderer())
        win.vtkwidget.GetRenderWindow().Render()


def Screenshot(rw):
    # Outputs a .png for every frame, input is a renderwindow
    # You can then combine the .pngs into a animated gif using the linux tool 'convert'
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(rw)
    w2if.Update()

    writer = vtk.vtkPNGWriter()
    savename = str(time.time()) + '.png'
    writer.SetFileName(savename)
    writer.SetInputData(w2if.GetOutput())
    writer.Write()

def RenderPlot(ratio):
    chart = vtk.vtkChartXY()
    chart.SetShowLegend(True)

    table = vtk.vtkTable()

    arrX = vtk.vtkFloatArray()
    arrX.SetName('Core')

    arrC = vtk.vtkFloatArray()
    arrC.SetName('Computation')

    arrS = vtk.vtkFloatArray()
    arrS.SetName('Communication')

    table.AddColumn(arrX)
    table.AddColumn(arrC)
    table.AddColumn(arrS)

    numberofbars = len(ratio)

    table.SetNumberOfRows(numberofbars)

    for i in range(numberofbars):
        table.SetValue(i, 0, i)
        table.SetValue(i, 1, 1 - ratio[i])
        table.SetValue(i, 2, ratio[i])

    bar = chart.AddPlot(vtk.vtkChart.BAR)
    bar.SetInputData(table, 0, 1)
    bar.SetColor(0, 255, 0, 255)
    bar.SetWidth(1.5)

    bar = chart.AddPlot(vtk.vtkChart.BAR)
    bar.SetInputData(table, 0, 2)
    bar.SetColor(255, 0, 0, 255)
    bar.SetWidth(1.5)

    chart.GetAxis(vtk.vtkAxis.LEFT).SetRange(0., 1.0)
    chart.GetAxis(vtk.vtkAxis.LEFT).SetNotation(2)
    chart.GetAxis(vtk.vtkAxis.LEFT).SetPrecision(1)
    chart.GetAxis(vtk.vtkAxis.LEFT).SetBehavior(vtk.vtkAxis.FIXED)
    chart.GetAxis(vtk.vtkAxis.LEFT).SetTitle("% of overall time")
    chart.GetAxis(vtk.vtkAxis.BOTTOM).SetTitle("Core number")

    return chart


def RenderDecompGrid(coords, renderer, px, py):
    x, y, z = coords

    localsizey = int(y/py)
    localsizex = int(x/px)
    overflowy = int(y-(localsizey*py))
    overflowx = x-(localsizex*px)
    localsizey+=1
    #localsizex+=1
    # the first few bigger chunks
    for i in range(1, int(overflowy)+1):
        localsizex += 1
        for j in range(1, int(overflowx) + 1):
            points = vtk.vtkPoints()
            ### for the outline, don't ask
            points.InsertNextPoint(0, 0, 0)
            points.InsertNextPoint(0, localsizey * i-1, 0)
            points.InsertNextPoint(int(localsizex * j)-1, localsizey * i-1, 0)
            points.InsertNextPoint(int(localsizex * j)-1, 0, 0)
            points.InsertNextPoint(0, 0, z)
            if i==1:
                print(overflowy, localsizey, localsizey*i)

            grid = vtk.vtkUnstructuredGrid()
            grid.SetPoints(points)

            sphere = vtk.vtkSphereSource()

            glyph3D = vtk.vtkGlyph3D()

            glyph3D.SetSourceConnection(sphere.GetOutputPort())
            glyph3D.SetInputData(grid)
            glyph3D.Update()

            filter = vtk.vtkOutlineFilter()

            filter.SetInputData(glyph3D.GetOutput())

            outlineMapper = vtk.vtkPolyDataMapper()
            outlineMapper.SetInputConnection(filter.GetOutputPort())

            outlineActor = vtk.vtkActor()
            outlineActor.SetMapper(outlineMapper)
            outlineActor.GetProperty().SetColor(1, 1, 1)

            renderer.AddActor(outlineActor)
        localsizex -= 1
        for j in range(int(overflowx) + 1, px + 1):
            points = vtk.vtkPoints()
            ### for the outline, don't ask
            points.InsertNextPoint(0, 0, 0)
            points.InsertNextPoint(0, int(localsizey * i)-1, 0)
            points.InsertNextPoint(int(localsizex * j + overflowx)-1, int(localsizey * i)-1, 0)
            points.InsertNextPoint(int(localsizex * j + overflowx)-1, 0, 0)
            points.InsertNextPoint(0, 0, z)

            grid = vtk.vtkUnstructuredGrid()
            grid.SetPoints(points)
            sphere = vtk.vtkSphereSource()
            glyph3D = vtk.vtkGlyph3D()
            glyph3D.SetSourceConnection(sphere.GetOutputPort())
            glyph3D.SetInputData(grid)
            glyph3D.Update()

            filter = vtk.vtkOutlineFilter()
            filter.SetInputData(glyph3D.GetOutput())
            outlineMapper = vtk.vtkPolyDataMapper()
            outlineMapper.SetInputConnection(filter.GetOutputPort())

            outlineActor = vtk.vtkActor()
            outlineActor.SetMapper(outlineMapper)
            outlineActor.GetProperty().SetColor(1, 1, 1)

            renderer.AddActor(outlineActor)
    # the next regular ones
    localsizey -=1

    for i in range(int(overflowy)+1, py+1):
        localsizex += 1
        for j in range(1, int(overflowx) + 1):
            points = vtk.vtkPoints()
            ### for the outline, don't ask
            print("Localsize and j, ", localsizex, j)
            points.InsertNextPoint(0, 0, 0)
            points.InsertNextPoint(0, int(localsizey * i)+overflowy-1, 0)
            points.InsertNextPoint(int(localsizex * j)-1, int(localsizey * i)+overflowy-1, 0)
            points.InsertNextPoint(int(localsizex * j)-1, 0, 0)
            points.InsertNextPoint(0, 0, z)

            grid = vtk.vtkUnstructuredGrid()
            grid.SetPoints(points)

            sphere = vtk.vtkSphereSource()

            glyph3D = vtk.vtkGlyph3D()

            glyph3D.SetSourceConnection(sphere.GetOutputPort())
            glyph3D.SetInputData(grid)
            glyph3D.Update()

            filter = vtk.vtkOutlineFilter()

            filter.SetInputData(glyph3D.GetOutput())

            outlineMapper = vtk.vtkPolyDataMapper()
            outlineMapper.SetInputConnection(filter.GetOutputPort())

            outlineActor = vtk.vtkActor()
            outlineActor.SetMapper(outlineMapper)
            outlineActor.GetProperty().SetColor(1, 1, 1)

            renderer.AddActor(outlineActor)
        localsizex -= 1
        for j in range(int(overflowx) + 1, px + 1):
            points = vtk.vtkPoints()
            ### for the outline, don't ask
            points.InsertNextPoint(0, 0, 0)
            points.InsertNextPoint(0, int(localsizey * i)+overflowy-1, 0)
            points.InsertNextPoint(int(localsizex * j + overflowx)-1, int(localsizey * i)+overflowy-1, 0)
            points.InsertNextPoint(int(localsizex * j + overflowx)-1, 0, 0)
            points.InsertNextPoint(0, 0, z)

            grid = vtk.vtkUnstructuredGrid()
            grid.SetPoints(points)
            sphere = vtk.vtkSphereSource()
            glyph3D = vtk.vtkGlyph3D()
            glyph3D.SetSourceConnection(sphere.GetOutputPort())
            glyph3D.SetInputData(grid)
            glyph3D.Update()

            filter = vtk.vtkOutlineFilter()
            filter.SetInputData(glyph3D.GetOutput())
            outlineMapper = vtk.vtkPolyDataMapper()
            outlineMapper.SetInputConnection(filter.GetOutputPort())

            outlineActor = vtk.vtkActor()
            outlineActor.SetMapper(outlineMapper)
            outlineActor.GetProperty().SetColor(1, 1, 1)

            renderer.AddActor(outlineActor)


def RenderOutline(coords, renderer):

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

    outlinefilter =  vtk.vtkOutlineFilter()
        # win.filters['Outline'].SetInputData(outlineglyph3D.GetOutput())

    outlineMapper = vtk.vtkPolyDataMapper()
    outlineMapper.SetInputConnection(outlinefilter.GetOutputPort())
    outlineMapper.SetScalarModeToUsePointFieldData()
    outlineMapper.SetScalarRange(0, 3)
    outlineMapper.SelectColorArray("cols")
    # outlineMapper.SetLookupTable(outlinecolors)

    outlineActor = vtk.vtkActor()
    outlineActor.SetMapper(outlineMapper)
    outlineActor.GetProperty().SetColor(1, 1, 1)
    renderer.AddActor(outlineActor)

    return glyph3D, colors, cols


def RenderCloud(cloud,coords, cloudactor):

    x,y,z = coords

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
                    points.InsertNextPoint(k, j, i)
                    scales.InsertNextValue(1)  # random radius between 0 and 0.99
                    rgb = [0.0, 0.0, 0.0]
                    lut.GetColor(cloud[k][j][i], rgb)
                    ucrgb = list(map(int, [x * 255 for x in rgb]))
                    col.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

    grid = vtk.vtkUnstructuredGrid()
    grid.SetPoints(points)
    grid.GetPointData().AddArray(scales)
    grid.GetPointData().SetActiveScalars("scales")
    sr = grid.GetScalarRange()# // !!!to set radius first
    #grid.GetPointData().AddArray(col)

    sphere = vtk.vtkSphereSource()

    glyph3D = vtk.vtkGlyph3D()
    glyph3D.SetSourceConnection(sphere.GetOutputPort())
    glyph3D.SetInputData(grid)
    glyph3D.Update()

    polydata = vtk.vtkPolyData()

    polydata.SetPoints(points)
    #polydata.GetPointData().SetScalars(col)
    #polydata.GetPointData().SetScalars(col)

    splatter = vtk.vtkGaussianSplatter()

    splatter.SetInputData(polydata)
    splatter.SetRadius(0.07)

    cf = vtk.vtkContourFilter()

    if points.GetNumberOfPoints() > 0:
        cf.SetInputConnection(splatter.GetOutputPort())
    else: #weird things happen if you give him a splatter with no points
        cf.SetInputData(polydata)

    cf.SetValue(0, 0.01)
    cf.GetOutput().GetPointData().SetScalars(col)

    reverse = vtk.vtkReverseSense()
    reverse.SetInputConnection(cf.GetOutputPort())
    reverse.ReverseCellsOn()
    reverse.ReverseNormalsOn()

    cloudmapper = vtk.vtkPolyDataMapper()
    cloudmapper.SetInputConnection(cf.GetOutputPort())
    cloudmapper.SetScalarModeToUseCellFieldData()
    cloudmapper.SetScalarRange(sr)
    cloudmapper.SelectColorArray("Ccol")  # // !!!to set color (nevertheless you will have nothing)
    cloudmapper.SetLookupTable(lut)

    cloudactor.GetProperty().SetOpacity(1.0)
    cloudactor.SetMapper(cloudmapper)


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
    grid.GetPointData().SetActiveScalars("Vscales")  # // !!!to set radius first
    grid.GetPointData().AddArray(col)

    sphere = vtk.vtkSphereSource()

    glyph3D = vtk.vtkGlyph3D()

    glyph3D.SetSourceConnection(sphere.GetOutputPort())
    glyph3D.SetInputData(grid)
    glyph3D.Update()

    # update mapper
    vapormapper = vtk.vtkPolyDataMapper()

    vapormapper.SetInputConnection(glyph3D.GetOutputPort())
    vapormapper.SetScalarModeToUsePointFieldData()
    vapormapper.SetScalarRange(0, 3)
    vapormapper.SelectColorArray("Vcol")  # // !!!to set color (nevertheless you will have nothing)
    vapormapper.SetLookupTable(lut)


def RenderRain(rain, coords, rainactor):

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
                    points.InsertNextPoint(k, j, i)
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

# update mapper
    rainmapper = vtk.vtkPolyDataMapper()
    rainmapper.SetInputConnection(glyph3D.GetOutputPort())
    rainmapper.SetScalarRange(0, 3)

    rainmapper.SetScalarModeToUsePointFieldData()
    rainmapper.SelectColorArray("Rcol")  # // !!!to set color (nevertheless you will have nothing)
    rainmapper.SetLookupTable(lut)

    rainactor.GetProperty().SetOpacity(0.1)
    rainactor.SetMapper(rainmapper)


def RenderSea(sealevel, coords, renderer, seaactor):

    x,y,z = coords

    points = vtk.vtkPoints()
    level = 0

    #sealevel = -5 #(-5 ,1)
    if sealevel == 1:
        level = -2
    elif sealevel == 3:
        level = 3

    for k in range(x):
        for j in range(-20, int((y*0.6))):
            for i in range(-10,level):
                points.InsertNextPoint(k, j, i)

    for k in range(x):
        for j in range(-20, int((y*0.6))):
            for i in range(level,level+1):
                if random.random()>0.85:
                    points.InsertNextPoint(k, j, i)

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
    splatter.SetRadius(0.08)

    cf = vtk.vtkContourFilter()
    cf.SetInputConnection(splatter.GetOutputPort())
    cf.SetValue(0, 0.1)

    reverse = vtk.vtkReverseSense()
    reverse.SetInputConnection(cf.GetOutputPort())
    reverse.ReverseCellsOn()
    reverse.ReverseNormalsOn()

    # update mapper
    seamapper = vtk.vtkPolyDataMapper()

    seamapper.SetInputConnection(reverse.GetOutputPort())
    seamapper.SetScalarModeToUsePointFieldData()
    seamapper.SetScalarRange(0, 3)

    seaactor.GetProperty().SetOpacity(1.)
    seaactor.GetProperty().SetColor(0., 0.412, 0.58)
    seaactor.SetMapper(seamapper)


def RenderLand(coords, renderer):

    x,y,z = coords

    points = vtk.vtkPoints()

    for k in range(x):
        for j in range(y-int((y*0.4)), y+20):
            for i in range(-5,3):
                points.InsertNextPoint(k, j, i)

    for k in range(x):
        for j in range(y-int((y*0.4)), y+20):
            for i in range(3,4):
                if random.random()>0.9:
                    points.InsertNextPoint(k, j, i)

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


    landmapper = vtk.vtkPolyDataMapper()

    landmapper.SetInputConnection(reverse.GetOutputPort())
    landmapper.SetScalarModeToUsePointFieldData()
    landmapper.SetScalarRange(0, 3)
    landactor = vtk.vtkActor()
    landactor.GetProperty().SetOpacity(1.0)
    landactor.GetProperty().SetColor(0.475, 0.31, 0.09)
    renderer.AddActor(landactor)
    landactor.SetMapper(landmapper)


def RenderCrops(level, coords, cropsactor):

    x, y, z = coords
    points = vtk.vtkPoints()


    for k in range(x):
        for j in range(y-int((y*0.4)), y+20):
            points.InsertNextPoint(k, j, 2)
            points.InsertNextPoint(k, j, level)

    # Create a polydata to store everything in
    linesPolyData = vtk.vtkPolyData()
    linesPolyData.Allocate()

    for i in range(0, points.GetNumberOfPoints(),2 ):
        linesPolyData.InsertNextCell(vtk.VTK_LINE, 2, [i, i+1])

    # Add the points to the dataset
    linesPolyData.SetPoints(points)

    # update mapper
    cropsmapper = vtk.vtkPolyDataMapper()
    cropsmapper.SetInputData(linesPolyData)


    cropsactor.GetProperty().SetOpacity(1.0)
    cropsactor.GetProperty().SetLineWidth(10)
    cropsactor.GetProperty().SetColor(0.39, 0.65, 0.04)
    cropsactor.SetMapper(cropsmapper)



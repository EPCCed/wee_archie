from __future__ import print_function
import client
import vtk
import random
import time
import math
import numpy

class vtkTimerCallback():
    def __init__(self, parent, win):
        self.timer_count = 0
        self.starttime=int(time.time())
        self.lasttime=self.starttime
        self.win=win
        self.parent=parent

    def execute(self,obj,event):
        if (not self.win.playing): return
        ctime=int(time.time())
        if (ctime > self.lasttime):
            elapsedTick=(self.lasttime+1)-self.starttime
            if (elapsedTick > 60):
                self.win.vtkwidget.RemoveObserver(self.win.timer_observer)
                self.win.vtkwidget.DestroyTimer(self.win.timer_id, None)
                self.win.playing = False
                self.win.getdata.value = False
                self.win.showScoreBoard(math.ceil(self.parent.achievedtime/60),self.parent.calculateAccuracy())
                self.win.StopSim()

            else:
                # if (elapsedTick%15 == 0): self.win.mode=0
                # if ((elapsedTick-5)%15 == 0): self.win.mode=1
                # if ((elapsedTick-10)%15 == 0): self.win.mode=2
                updateStopWatchHand(self.win, (self.lasttime-self.starttime) + 1)
                self.lasttime+=1

#Data transfer object
class DTO(client.AbstractDTO):
    def SetData(self, data):
        self.Data=data

    def GetData(self):
        return self.Data

#class containing demo-specific functions
class WeatherDemo(client.AbstractDemo):
    def __init__(self):
        self.init_scene=False
        self.wind_tot=0.0
        self.wind_min=9999.0
        self.wind_max=0.0
        self.wind_angle=0.0
        self.wind_ticks=0

    # read in data and convert it to a data transfer object
    def GetVTKData(self, root): # root=netcdf handle
        t1=time.time()
        q = root.variables['q']

        pres = root.variables['p'][:]
        p = numpy.array(pres)
        #p = ((p + 1000)/1000) - 0.2


        theta = root.variables['th'][:]
        th = numpy.array(theta)
        #th = th/4

        #th_ref = root.variables['th_ref'][:]

        rm = root.variables['ground_rain'][:]

        coords = root.variables['q'].shape[1:]

        vapor = (q[0] / 0.018) - 0.08  # return normalized vapor field data

        clouds = q[1] #(q[1] - 0.00004)/ q[1].max()  # return normalized cloud data
        #print(str(clouds))
        rain = q[2]# (q[2]/q[2].max())

        timepersec = root.variables['time_per_sec'][0]
        modeltime = root.variables['model_time'][0]

        wind_u = root.variables['wind_u'][0]
        wind_v = root.variables['wind_v'][0]

        overalltime = root.variables['overall_time'][:]
        communicationtime =root.variables['communication_time'][:]

        x, y, z = coords

        avg_temp=numpy.sum(th[:,:,2])/(x*y)
        avg_pressure=numpy.sum(p[:,:,2])/(x*y)

        data = [vapor, clouds, rain, coords, rm, timepersec, overalltime, communicationtime, th, p, modeltime, wind_u, wind_v, avg_temp, avg_pressure]

        # create data transfer object and put the array into it
        dto = DTO()
        dto.SetData(data)

        print("Data successfully DTO'd")
        t2=time.time()
        print("DTO extraction took",t2-t1,"s")

        return dto

    def calculateAccuracy(self):
        if (self.obs_state < 4):
            clouds_accuracy=25 if self.accuracy_setting >= 60 else 20
        else:
            cost_factor = 4 if self.obs_state < 12 else 6
            clouds_accuracy=random.randint(abs(self.accuracy_setting/4) - cost_factor, self.accuracy_setting + 3)
            if (clouds_accuracy < 0): clouds_accuracy=0
            if (clouds_accuracy > 25): clouds_accuracy=25
        wind_speed_avg=self.wind_tot/self.wind_ticks
        wind_dir_avg=self.wind_angle/self.wind_ticks

        wind_score_str_component=10-abs(wind_speed_avg - self.obs_wind_strength)
        if (wind_score_str_component < 0): wind_score_str_component=0

        wind_score_gust_component=10-abs((self.wind_max - self.wind_min) - self.obs_gust)
        if (wind_score_gust_component < 0): wind_score_gust_component=0

        wind_score_direction_component=10-abs(self.obs_wind_dir - wind_dir_avg)
        if (wind_score_direction_component < 0): wind_score_direction_component=0

        wind_accuracy=wind_score_str_component+wind_score_gust_component+wind_score_direction_component
        pressure_accuracy=self.calcSpecificAccuracy()
        temp_accuracy=self.calcSpecificAccuracy()
        return clouds_accuracy+wind_accuracy+pressure_accuracy+temp_accuracy


    def calcSpecificAccuracy(self):
        field_accuracy=random.randint(15,20)
        if (self.accuracy_setting < 70):
            field_accuracy-=random.randint(3,6)
        if (self.accuracy_setting < 60):
            field_accuracy-=random.randint(3,6)
        if (self.accuracy_setting < 50):
            field_accuracy-=random.randint(3,6)
        if (self.accuracy_setting < 40):
            field_accuracy-=random.randint(3,6)
        if (field_accuracy < 0): field_accuracy=0
        if (field_accuracy > 25): field_accuracy=25
        return field_accuracy


    def setSubmittedParameters(self, basehour, obs_wind_dir, obs_wind_strength, obs_gust, obs_pressure, obs_temp, obs_state, accuracy_setting):
        self.basehour=basehour
        self.obs_wind_dir=obs_wind_dir
        self.obs_wind_strength=obs_wind_strength
        self.obs_gust=obs_gust if obs_gust > 0 else 0
        self.obs_pressure=obs_pressure
        self.obs_temp=obs_temp
        self.obs_state=obs_state
        self.accuracy_setting=accuracy_setting

    # Renders a frame with data contained within the data transfer object, data
    def RenderFrame(self, win, dto, landscape_only=False):
        t1=time.time()
        self.win=win

        #print("LOCATION=",self.Location)

        x=34
        y=24
        z=30


        win.renderer.SetBackground(0.22,.67,.87)
        win.renderer.SetViewport(0, 0.3, 0.85, 1)

        try:
            win.views['BarPlot']
        except:
            win.views['BarPlot'] = vtk.vtkContextView()

        if landscape_only:
            win.views['BarPlot'].GetScene().ClearItems()



        win.views['BarPlot'].GetRenderer().SetViewport(0,0,1,0.3)
        win.views["BarPlot"].GetRenderer().SetBackground(0.79,0.79,0.79)

        win.vtkwidget.GetRenderWindow().AddRenderer(win.views['BarPlot'].GetRenderer())
        win.views['BarPlot'].GetRenderer().Render()



        try:
            win.views['StatusLine']
        except:
            win.views['StatusLine'] = vtk.vtkContextView()

        if landscape_only:
            win.views["StatusLine"].GetScene().ClearItems()


        win.views['StatusLine'].GetRenderer().SetBackground(0.22,.67,.87)
        win.views['StatusLine'].GetRenderer().SetBackground(0.79,0.79,0.79)
        win.views['StatusLine'].GetRenderer().SetViewport(0.85,0.3,1,1)

        win.vtkwidget.GetRenderWindow().AddRenderer(win.views['StatusLine'].GetRenderer())
        win.views['StatusLine'].GetRenderer().Render()


        if (not self.init_scene or landscape_only):
            #TODO landactor try
            RenderLand(self, win.renderer)

        try:
            win.camera
        except:
            win.camera = win.renderer.GetActiveCamera()

            #focus camera on just beneath the centre of the scene
            win.camera.SetFocalPoint(x/2,y/2,z/2.5)

            #position camera along the -x axis, and rotate so that z is up
            win.camera.SetPosition(x/2-2.5*x,y/2,z/2.5)
            win.camera.Roll(90)

            #Rotate camera around z axis by 120 degrees
            win.camera.Azimuth(120)
            #tilt camera up by 10 degrees
            win.camera.Elevation(10)





        if not landscape_only:


            #unpack  data transfer object
            data = dto.GetData()
            vapor, clouds, rain, coords, rm, timepersec, overalltime, commtime, th, p, modeltime, wind_u, wind_v, avg_temp, avg_pressure = data


            x, y, z = coords



            self.mode = win.mode

            self.achievedtime=modeltime*2

            # The actors need to be created only once, that is why we have a actors dictionary in the win. This way we
            # will only add each actor once to the renderer. The other things like data structures, filters and mappers are
            # created and destroyed in each function.

            # To switch between the temperature, pressure and 'real' world views.
            if self.mode == 0:
                ### Clouds rendering
                # We create the actor if it does not exist, call the rendering function and give it the actor.
                # The function then gives new input for the actor, which we then add to the renderer.
                try:
                    win.actors['CloudActor']
                except:
                    win.actors['CloudActor'] = vtk.vtkVolume()
                    #win.renderer.AddVolume(win.actors['CloudActor'])

                RenderCloud(clouds, coords, win.actors['CloudActor'])
                win.renderer.AddVolume(win.actors['CloudActor'])

                ### Rain
                try:
                    win.actors['RainActor']
                except:
                    win.actors['RainActor'] = vtk.vtkActor()

                RenderRain(rain, coords, win.actors['RainActor'])
                win.renderer.AddActor(win.actors['RainActor'])

                ### Remove actors
                try:
                    win.renderer.RemoveActor(win.actors['TempActor'])
                except:
                    pass

                try:
                    win.renderer.RemoveActor(win.actors['PressActor'])
                except:
                    pass

                try:
                    win.renderer.RemoveActor(win.actors['colourbar'])
                except:
                    pass

            elif self.mode == 1:
                ### Temperature
                try:
                    win.actors['TempActor']
                except:
                    win.actors['TempActor'] = vtk.vtkVolume()


                try:
                    win.renderer.RemoveActor(win.actors['colourbar'])
                except:
                    pass

                win.actors["colourbar"]=RenderTemp(self,th, coords, win.actors['TempActor'])
                win.renderer.AddActor(win.actors['TempActor'])
                win.renderer.AddActor(win.actors["colourbar"])

                ### Remove actors
                try:
                    win.renderer.RemoveActor(win.actors['RainActor'])
                    win.renderer.RemoveActor(win.actors['CloudActor'])
                except:
                    pass

                try:
                    win.renderer.RemoveActor(win.actors['PressActor'])
                except:
                    pass

            elif self.mode == 2:
                ### Pressure
                try:
                    win.actors['PressActor']
                except:
                    win.actors['PressActor'] = vtk.vtkVolume()

                try:
                    win.renderer.RemoveActor(win.actors['colourbar'])
                except:
                    pass

                win.actors["colourbar"]=RenderPress(p, coords, win.actors['PressActor'],self.reference_pressure)
                win.renderer.AddActor(win.actors['PressActor'])
                win.renderer.AddActor(win.actors["colourbar"])

                ### Remove actors
                try:
                    win.renderer.RemoveActor(win.actors['RainActor'])
                    win.renderer.RemoveActor(win.actors['CloudActor'])
                except:
                    pass

                try:
                    win.renderer.RemoveActor(win.actors['TempActor'])
                except:
                    pass

            ### Sea
            # try:
            #     win.actors['SeaActor']
            # except:
            #     win.actors['SeaActor'] = vtk.vtkActor()
            #
            # if win.frameno.value ==0:
            #     RenderSea(win.waterlevel, coords, win.renderer, win.actors['SeaActor'])
            #
            # win.renderer.AddActor(win.actors['SeaActor'])




            ### Decomposition grid redering, TODO
            if win.decompositiongrid is True:
                try:  # does the actor exist? if not, create one
                    win.actors['DGridActor']
                except:
                    win.actors['DGridActor'] = vtk.vtkPropCollection()

                win.actors['DGridActor'].RemoveAllItems()
                RenderDecompGrid(coords, win.actors['DGridActor'], win.columnsinX, win.columnsinY)
                #print("Adding actors")
                for i in range(win.actors['DGridActor'].GetNumberOfItems()):
                    win.renderer.AddActor(win.actors['DGridActor'].GetItemAsObject(i))

            elif win.decompositiongrid is False:
                try:
                    for i in range(win.actors['DGridActor'].GetNumberOfItems()):
                        win.renderer.RemoveActor(win.actors['DGridActor'].GetItemAsObject(i))
                except:
                    pass

            # ### Crops
            # try:  # does the actor exist? if not, create one
            #     win.actors['CropsActor']
            # except:
            #     win.actors['CropsActor'] = vtk.vtkActor()
            #
            # win.rainmass += sum(sum(rm))
            # if win.rainmass < 1.5:
            #     win.cropslevel = int(win.rainmass * 3) + 2
            # else:
            #     if win.cropslevel > 4:
            #         win.cropslevel -= 1
            #     else:
            #         win.cropslevel = 4
            #
            # RenderCrops(win.cropslevel, coords, win.actors['CropsActor'])
            #
            # if win.rainmass > 1.5:
            #     win.actors['CropsActor'].GetProperty().SetColor(0, 0, 0)
            #
            # win.renderer.AddActor(win.actors['CropsActor'])

            ### Camera settings






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

            try:
                win.views['StatusLine']
            except:
                win.views['StatusLine'] = vtk.vtkContextView()

            win.views['StatusLine'].GetRenderer().SetBackground(0.22,.67,.87)
            win.views['StatusLine'].GetRenderer().SetBackground(0.79,0.79,0.79)
            win.views['StatusLine'].GetRenderer().SetViewport(0.85,0.3,1,1)

            win.vtkwidget.GetRenderWindow().AddRenderer(win.views['StatusLine'].GetRenderer())
            win.views['StatusLine'].GetRenderer().Render()

            generateStatusBar(self, win, win.views['StatusLine'].GetRenderer(), modeltime, wind_u, wind_v,
                win.views['StatusLine'].GetScene().GetSceneWidth(), win.views['StatusLine'].GetScene().GetSceneHeight())

            if (not self.init_scene):
                timecallback=vtkTimerCallback(self, win)
                win.timer_observer=win.vtkwidget.AddObserver(vtk.vtkCommand.TimerEvent, timecallback.execute) # 'TimerEvent', timecallback.execute)
                win.timer_id=win.vtkwidget.CreateRepeatingTimer(1000)


            if (not self.init_scene): self.init_scene=True

        win.vtkwidget.GetRenderWindow().Render()

        t2=time.time()
        print("Total frame rendering time=",t2-t1)

    def resetScene(self, win):
        win.renderer.RemoveAllViewProps()
        win.renderer.ResetCamera()
        win.vtkwidget.GetRenderWindow().Render()
        win.vtkwidget.RemoveObserver(win.timer_observer)
        win.vtkwidget.DestroyTimer(win.timer_id, None)
        win.views['StatusLine'].GetScene().RemoveItem(win.compass1_hand)
        win.views['StatusLine'].GetScene().RemoveItem(win.compass2_hand)
        win.views['StatusLine'].GetScene().RemoveItem(win.compass1_strength)
        win.views['StatusLine'].GetScene().RemoveItem(win.compass2_hand)

def updateStopWatchHand(win, seconds_remaining):
    if (seconds_remaining == 55):
        win.views['StatusLine'].GetScene().RemoveItem(win.stopwatchImg)
        imageReader2 = vtk.vtkPNGReader()
        imageReader2.SetFileName("stopwatch_red.png")
        imageReader2.Update()

        imageResizer2=vtk.vtkImageResize()
        imageResizer2.SetInputData(imageReader2.GetOutput())
        imageResizer2.SetResizeMethod(imageResizer2.MAGNIFICATION_FACTORS)
        imageResizer2.SetMagnificationFactors(0.4,0.4,0.4)
        imageResizer2.Update()

        win.stopwatchImg=vtk.vtkImageItem()
        win.stopwatchImg.SetImage(imageResizer2.GetOutput())
        win.stopwatchImg.SetPosition(win.bar_width*0.277, win.bar_height*0.443)
        win.views['StatusLine'].GetScene().AddItem(win.stopwatchImg)
    win.views['StatusLine'].GetScene().RemoveItem(win.stopWatchHand)
    win.stopWatchHand=generateStopWatchHand(seconds_remaining, win.bar_width, win.bar_height)
    win.views['StatusLine'].GetScene().AddItem(win.stopWatchHand)
    win.vtkwidget.GetRenderWindow().Render()

def generateStatusBar(self, win, renderer, modeltime, wind_u, wind_v, bar_width, bar_height):
    if (not self.init_scene):
        imageReader = vtk.vtkPNGReader()
        imageReader.SetFileName("clockface.png")
        imageReader.Update()

        imageResizer=vtk.vtkImageResize()
        imageResizer.SetInputData(imageReader.GetOutput())
        imageResizer.SetResizeMethod(imageResizer.MAGNIFICATION_FACTORS)
        imageResizer.SetMagnificationFactors(0.3,0.3,0.3)
        imageResizer.Update()

        imgItem=vtk.vtkImageItem()
        imgItem.SetImage(imageResizer.GetOutput())
        imgItem.SetPosition(bar_width*0.277, bar_height*0.734)
        win.views['StatusLine'].GetScene().AddItem(imgItem)

        imageReader2 = vtk.vtkPNGReader()
        imageReader2.SetFileName("stopwatch.png")
        imageReader2.Update()

        imageResizer2=vtk.vtkImageResize()
        imageResizer2.SetInputData(imageReader2.GetOutput())
        imageResizer2.SetResizeMethod(imageResizer2.MAGNIFICATION_FACTORS)
        imageResizer2.SetMagnificationFactors(0.4,0.4,0.4)
        imageResizer2.Update()

        win.stopwatchImg=vtk.vtkImageItem()
        win.stopwatchImg.SetImage(imageResizer2.GetOutput())
        win.stopwatchImg.SetPosition(bar_width*0.277, bar_height*0.443)
        win.views['StatusLine'].GetScene().AddItem(win.stopwatchImg)
        win.stopWatchHand=generateStopWatchHand(60, bar_width, bar_height)
        win.views['StatusLine'].GetScene().AddItem(win.stopWatchHand)


        win.views['StatusLine'].GetScene().AddItem(generateCompassRose(bar_width*0.399,bar_height*0.265))
        win.views['StatusLine'].GetScene().AddItem(generateCompassRose(bar_width*0.399,bar_height*0.0886))
        win.compass2_hand=generateWindDirectionHand(bar_width*0.4166,bar_height*0.0886, self.obs_wind_dir)
        win.compass2_strength=generateCompassStength(bar_width*0.62, bar_height*0.1568, self.obs_wind_strength)
        win.views['StatusLine'].GetScene().AddItem(win.compass2_hand)
        win.views['StatusLine'].GetScene().AddItem(win.compass2_strength)
        win.bar_width=bar_width
        win.bar_height=bar_height
    else:
        win.views['StatusLine'].GetScene().RemoveItem(win.timeOfDayHourHand)
        win.views['StatusLine'].GetScene().RemoveItem(win.timeOfDayMinuteHand)
        win.views['StatusLine'].GetScene().RemoveItem(win.compass1_hand)
        win.views['StatusLine'].GetScene().RemoveItem(win.compass1_strength)

    rebased_modeltime=modeltime*2
    currenthour_angle=((self.basehour - 12 if self.basehour > 12 else self.basehour) * 30) + ((rebased_modeltime/3600) *30)
    currentminute_angle=((rebased_modeltime%3600)/3600) * 360

    win.timeOfDayHourHand=generateTimeOfDayHand("hourhand.png", currenthour_angle, bar_width*0.368, bar_height*0.7658)
    win.timeOfDayMinuteHand=generateTimeOfDayHand("minutehand.png", currentminute_angle, bar_width*0.3125, bar_height*0.7468)
    win.views['StatusLine'].GetScene().AddItem(win.timeOfDayMinuteHand)
    win.views['StatusLine'].GetScene().AddItem(win.timeOfDayHourHand)

    win_strength, win_direction=calcWindStrenghDirection(wind_u, wind_v)
    self.wind_tot+=win_strength
    self.wind_angle+=win_direction
    self.wind_ticks+=1
    if (self.wind_min > win_strength): self.wind_min=win_strength
    if (self.wind_max < win_strength): self.wind_max=win_strength
    win.compass1_hand=generateWindDirectionHand(bar_width*0.4166, bar_height*0.2658, win_direction)
    win.compass1_strength=generateCompassStength(bar_width*0.62, bar_height*0.3321, win_strength)
    win.views['StatusLine'].GetScene().AddItem(win.compass1_hand)
    win.views['StatusLine'].GetScene().AddItem(win.compass1_strength)

def calcWindStrenghDirection(wind_u, wind_v):
    strength=abs(wind_u + wind_v)
    wind_u_abs=abs(wind_u)
    wind_v_abs=abs(wind_v)
    diag= 45 / ((wind_u_abs / wind_v_abs) if wind_u_abs > wind_v_abs else (wind_v_abs / wind_u_abs))

    if wind_u_abs > wind_v_abs:
        start_angle = 180 if wind_u < 0.0 else 0
        if (wind_v < 0.0):
            direction=(360 - diag) if start_angle == 0 else (start_angle+diag)
        else:
            direction=(start_angle + diag) if start_angle == 0 else (start_angle-diag)
    else:
        start_angle = 270 if wind_u < 0.0 else 90
        if (wind_u < 0.0):
            direction=(start_angle - diag) if start_angle == 270 else (start_angle+diag)
        else:
            direction=(start_angle + diag) if start_angle == 270 else (start_angle-diag)
    return strength, direction

def generateCompassStength(xpos, ypos, strength):
    tooltip=vtk.vtkTooltipItem()
    tooltip.SetText("{:.1f}".format(strength))
    tooltip.SetPosition(xpos, ypos)
    tooltip.GetTextProperties().SetBackgroundOpacity(0.0)
    tooltip.GetTextProperties().SetJustificationToCentered()
    tooltip.GetTextProperties().SetVerticalJustificationToCentered()
    tooltip.GetPen().SetOpacityF(0.0)
    tooltip.GetBrush().SetOpacityF(0.0)
    return tooltip

def generateCompassRose(xpos, ypos):
    imageReader = vtk.vtkPNGReader()
    imageReader.SetFileName("wind_compass.png")
    imageReader.Update()

    imageResizer=vtk.vtkImageResize()
    imageResizer.SetInputData(imageReader.GetOutput())
    imageResizer.SetResizeMethod(imageResizer.MAGNIFICATION_FACTORS)
    imageResizer.SetMagnificationFactors(0.15,0.15,0.15)
    imageResizer.Update()

    imgItem=vtk.vtkImageItem()
    imgItem.SetImage(imageResizer.GetOutput())
    imgItem.SetPosition(xpos, ypos)
    return imgItem

def generateWindDirectionHand(xpos, ypos, wind_angle):
    imageReader = vtk.vtkPNGReader()
    imageReader.SetFileName("wind_compass_hand.png")
    imageReader.Update()

    imageResizer=vtk.vtkImageResize()
    imageResizer.SetInputData(imageReader.GetOutput())
    imageResizer.SetResizeMethod(imageResizer.MAGNIFICATION_FACTORS)
    imageResizer.SetMagnificationFactors(0.15,0.15,0.15)
    imageResizer.Update()

    bounds=[0.0]*6
    imageResizer.GetOutput().GetBounds(bounds)

    center=[0.0]*3
    center[0] = (bounds[1] + bounds[0]) / 2.0
    center[1] = (bounds[3] + bounds[2]) / 2.0
    center[2] = (bounds[5] + bounds[4]) / 2.0

    transformer=vtk.vtkTransform()
    transformer.Translate(center[0], center[1], center[2])
    transformer.RotateZ(wind_angle)
    transformer.Translate(-center[0], -center[1], -center[2])

    imageReslicer=vtk.vtkImageReslice()
    imageReslicer.SetInputData(imageResizer.GetOutput())
    imageReslicer.SetResliceTransform(transformer)
    imageReslicer.SetInterpolationModeToLinear()
    imageReslicer.Update()

    imgItem=vtk.vtkImageItem()
    imgItem.SetImage(imageReslicer.GetOutput())
    imgItem.SetPosition(xpos, ypos)
    return imgItem

def generateStopWatchHand(seconds_remaining, bar_width, bar_height):
    if (seconds_remaining == 60):
        angle=0.0
    else:
        angle=(60-seconds_remaining) * 6
    return generateClockHand("stopwatch_hand.png", angle, bar_width*0.40625, bar_height*0.4898, 0.15)

def generateTimeOfDayHand(filename, angle, xpos, ypos):
    return generateClockHand(filename, angle, xpos, ypos, 0.3)

def generateClockHand(filename, angle, xpos, ypos, mag):
    imageReader = vtk.vtkPNGReader()
    imageReader.SetFileName(filename)
    imageReader.Update()
    imageResizer=vtk.vtkImageResize()
    imageResizer.SetInputData(imageReader.GetOutput())
    imageResizer.SetResizeMethod(imageResizer.MAGNIFICATION_FACTORS)
    imageResizer.SetMagnificationFactors(mag,mag,mag)
    imageResizer.Update()

    bounds=[0.0]*6
    imageResizer.GetOutput().GetBounds(bounds)

    center=[0.0]*3
    center[0] = (bounds[1] + bounds[0]) / 2.0
    center[1] = (bounds[3] + bounds[2]) / 2.0
    center[2] = (bounds[5] + bounds[4]) / 2.0

    transformer=vtk.vtkTransform()
    transformer.Translate(center[0], center[1], center[2])
    transformer.RotateZ(angle)
    transformer.Translate(-center[0], -center[1], -center[2])

    imageReslicer=vtk.vtkImageReslice()
    imageReslicer.SetInputData(imageResizer.GetOutput())
    imageReslicer.SetResliceTransform(transformer)
    imageReslicer.SetInterpolationModeToLinear()
    imageReslicer.Update()

    imgItem=vtk.vtkImageItem()
    imgItem.SetImage(imageReslicer.GetOutput())
    imgItem.SetPosition(xpos, ypos)
    return imgItem


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


def RenderDecompGrid(coords, collection, px, py):
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
            #if i==1:
            #    print(overflowy, localsizey, localsizey*i)

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

            collection.AddItem(outlineActor)
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

            collection.AddItem(outlineActor)
    # the next regular ones
    localsizey -=1

    for i in range(int(overflowy)+1, py+1):
        localsizex += 1
        for j in range(1, int(overflowx) + 1):
            points = vtk.vtkPoints()
            ### for the outline, don't ask
            #print("Localsize and j, ", localsizex, j)
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

            collection.AddItem(outlineActor)
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

            collection.AddItem(outlineActor)




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

def RenderCloud(cloud, coords, cloudactor):

    x,y,z = coords

    t1=time.time()
    cloudarray=cloud
    mn=cloud.min()
    mx=cloud.max()

    #scale between 0 and 255
    cloudarray=(cloudarray)/(mx)*255

    #cast to uint


    data=cloudarray.astype(numpy.uint8)


    data=numpy.ascontiguousarray(data)


    #Apparently VTK is rubbish at hacving people manually making VTK data structures, so we write this array to a string, which is then read into a VTK reader... inefficient I know... :/
    dataImporter = vtk.vtkImageImport()

    #make string (want it in Fortran order (column major) else everything is transposed
    data_string = data.tostring(order="F")

    #read in string
    dataImporter.CopyImportVoidPointer(data_string, len(data_string))

    # The type of the newly imported data is set to unsigned char (uint8)
    dataImporter.SetDataScalarTypeToUnsignedChar()

    # Because the data that is imported only contains an intensity value (it isnt RGB-coded or someting similar), the importer must be told this is the case (only one data value by gridpoint)
    dataImporter.SetNumberOfScalarComponents(1)

    # The following two functions describe how the data is stored and the dimensions of the array it is stored in. For this
    # simple case, all axes are of length 75 and begins with the first element. For other data, this is probably not the case.
    # I have to admit however, that I honestly dont know the difference between SetDataExtent() and SetWholeExtent() although
    # VTK complains if not both are used.
    dataImporter.SetDataExtent(0,x-1, 0, y-1, 0, z-1) #fun fact, for data[x,y,z] this uses z,y,x
    dataImporter.SetWholeExtent(0,x-1, 0, y-1, 0, z-1)

    #create alpha and colour functions (map values 0-255 to colour and transparency)
    alpha=vtk.vtkPiecewiseFunction()
    colour=vtk.vtkColorTransferFunction()

    for i in range(256):
        #alpha.AddPoint(i,i/1024.)
        alpha.AddPoint(i,i/256.*0.2)

        r=0.5
        g=0.5
        b=0.5
        colour.AddRGBPoint(i,r,g,b)

    # The preavious two classes stored properties. Because we want to apply these properties to the volume we want to render,
    # we have to store them in a class that stores volume prpoperties.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colour)
    volumeProperty.SetScalarOpacity(alpha)


    # This class describes how the volume is rendered (through ray tracing).
    #compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
    # We can finally create our volume. We also have to specify the data for it, as well as how the data will be rendered.
    volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
    #volumeMapper.SetVolumeRayCastFunction(compositeFunction)
    volumeMapper.SetInputConnection(dataImporter.GetOutputPort())

    cloudactor.SetMapper(volumeMapper)
    cloudactor.SetProperty(volumeProperty)

    t2=time.time()

    print("Time to draw clouds = ",t2-t1)

    # points = vtk.vtkPoints()
    #
    # scales = vtk.vtkFloatArray()
    # scales.SetName("scales")
    #
    # col = vtk.vtkUnsignedCharArray()
    # col.SetName('Ccol')  # Any name will work here.
    # col.SetNumberOfComponents(3)
    #
    # nc = vtk.vtkNamedColors()
    #
    # tableSize = x * y * z
    # lut = vtk.vtkLookupTable()
    # lut.SetNumberOfTableValues(tableSize)
    # lut.Build()
    #
    # # Fill in a few known colors, the rest will be generated if needed
    # lut.SetTableValue(0, nc.GetColor4d("Black"))
    # lut.SetTableValue(1, nc.GetColor4d("Banana"))
    # lut.SetTableValue(2, nc.GetColor4d("Tomato"))
    # lut.SetTableValue(3, nc.GetColor4d("Wheat"))
    # lut.SetTableValue(4, nc.GetColor4d("Lavender"))
    # lut.SetTableValue(5, nc.GetColor4d("Flesh"))
    # lut.SetTableValue(6, nc.GetColor4d("Raspberry"))
    # lut.SetTableValue(7, nc.GetColor4d("Salmon"))
    # lut.SetTableValue(8, nc.GetColor4d("Mint"))
    # lut.SetTableValue(9, nc.GetColor4d("Peacock"))
    #
    #
    # for i in range(0,z,2):
    #     for j in range(0,y,2):
    #         for k in range(0,x,2):
    #             if cloud[k][j][i] > 0:
    #                 #print(i,j,k)
    #                 points.InsertNextPoint(k, j, i)
    #                 scales.InsertNextValue(1)  # random radius between 0 and 0.99
    #                 rgb = [0.0, 0.0, 0.0]
    #                 lut.GetColor(cloud[k][j][i], rgb)
    #                 ucrgb = list(map(int, [xx * 255 for xx in rgb]))
    #                 col.InsertNextTuple3(255,0,0)#ucrgb[0], ucrgb[1], ucrgb[2])
    #                 #print (" "+str(ucrgb)+" : "+str(rgb))
    #
    # #grid = vtk.vtkUnstructuredGrid()
    # #grid.SetPoints(points)
    # #grid.GetPointData().AddArray(scales)
    # #grid.GetPointData().SetActiveScalars("scales")
    # #sr = grid.GetScalarRange()# // !!!to set radius first
    # #grid.GetPointData().AddArray(col)
    #
    # #sphere = vtk.vtkSphereSource()
    #
    # #glyph3D = vtk.vtkGlyph3D()
    # #glyph3D.SetSourceConnection(sphere.GetOutputPort())
    # #glyph3D.SetInputData(grid)
    # #glyph3D.Update()
    #
    # polydata = vtk.vtkPolyData()
    #
    # polydata.SetPoints(points)
    # #polydata.GetPointData().SetScalars(col)
    # #polydata.GetPointData().SetScalars(col)
    #
    # splatter = vtk.vtkGaussianSplatter()
    #
    # splatter.SetInputData(polydata)
    # splatter.SetRadius(0.07)
    #
    # cf = vtk.vtkContourFilter()
    #
    # if points.GetNumberOfPoints() > 0:
    #     cf.SetInputConnection(splatter.GetOutputPort())
    # else: #weird things happen if you give him a splatter with no points
    #     cf.SetInputData(polydata)
    #
    # cf.SetValue(0, 0.01)
    # cf.GetOutput().GetPointData().SetScalars(col)
    #
    # reverse = vtk.vtkReverseSense()
    # reverse.SetInputConnection(cf.GetOutputPort())
    # reverse.ReverseCellsOn()
    # reverse.ReverseNormalsOn()
    #
    # cloudmapper = vtk.vtkPolyDataMapper()
    # cloudmapper.SetInputConnection(cf.GetOutputPort())
    # cloudmapper.SetScalarModeToUseCellFieldData()
    # #cloudmapper.SetScalarRange(sr)
    # cloudmapper.SelectColorArray("Ccol")  # // !!!to set color (nevertheless you will have nothing)
    # cloudmapper.SetLookupTable(lut)
    #
    # cloudactor.GetProperty().SetOpacity(1.0)
    # cloudactor.SetMapper(cloudmapper)


def RenderVapor(vapor, coords):
    #print("Vapour?")
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

    t1=time.time()

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
    #lut.SetAlphaRange(0.6,0.7)
    lut.Build()

    mx=rain.max()

    for k in range(0,x,1):
        for j in range(0,y,1):
            for i in range(0,z,1):
                if rain[k][j][i] > 0.001:
                    points.InsertNextPoint(k, j, i-0.25)
                    points.InsertNextPoint(k,j,i+0.25) #comment if doing glyphs
                    #scales.InsertNextValue(1)
                    #rgb = [0.0, 0.0, 0.0]
                    #lut.GetColor(rain[k][j][i], rgb)
                    #ucrgb = list(map(int, [x2 * 255 for x2 in rgb]))
                    #col.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

#     grid = vtk.vtkUnstructuredGrid()
#     grid.SetPoints(points)
#     grid.GetPointData().AddArray(scales)
#     grid.GetPointData().SetActiveScalars("Rscales")  # // !!!to set radius first
#     grid.GetPointData().AddArray(col)
#
#     sphere = vtk.vtkSphereSource()
#     sphere.SetThetaResolution(3)
#     sphere.SetPhiResolution(3)
#
#     glyph3D = vtk.vtkGlyph3D()
#
#     glyph3D.SetSourceConnection(sphere.GetOutputPort())
#     glyph3D.SetInputData(grid)
#     glyph3D.Update()
#
# # update mapper
#     rainmapper = vtk.vtkPolyDataMapper()
#     rainmapper.SetInputConnection(glyph3D.GetOutputPort())
#     rainmapper.SetScalarRange(0, 3)
#
#     rainmapper.SetScalarModeToUsePointFieldData()
#     rainmapper.SelectColorArray("Rcol")  # // !!!to set color (nevertheless you will have nothing)
#     rainmapper.SetLookupTable(lut)
#
#     rainactor.GetProperty().SetOpacity(0.1)
#     rainactor.SetMapper(rainmapper)

    linesPolyData = vtk.vtkPolyData()
    linesPolyData.Allocate()

    for i in range(0, points.GetNumberOfPoints(),2 ):
        linesPolyData.InsertNextCell(vtk.VTK_LINE, 2, [i, i+1])

    # Add the points to the dataset
    linesPolyData.SetPoints(points)

    # update mapper
    rainmapper = vtk.vtkPolyDataMapper()
    rainmapper.SetInputData(linesPolyData)


    rainactor.GetProperty().SetOpacity(0.2)
    rainactor.GetProperty().SetLineWidth(5)
    rainactor.GetProperty().SetColor(0.1, 0.1, 0.8)
    rainactor.SetMapper(rainmapper)

    t2=time.time()

    print("Rain time=",t2-t1)

def RenderTemp(self,th, coords, tempactor):

    x,y,z = coords

    t1=time.time()
    tharray=th
    mn=th.min()
    mx=th.max()

    #scale between 0 and 255
    tharray=(tharray-mn)/(mx-mn)*255

    #cast to uint


    data=tharray.astype(numpy.uint8)


    data=numpy.ascontiguousarray(data)


    #Apparently VTK is rubbish at hacving people manually making VTK data structures, so we write this array to a string, which is then read into a VTK reader... inefficient I know... :/
    dataImporter = vtk.vtkImageImport()

    #make string (want it in Fortran order (column major) else everything is transposed
    data_string = data.tostring(order="F")

    #read in string
    dataImporter.CopyImportVoidPointer(data_string, len(data_string))

    # The type of the newly imported data is set to unsigned char (uint8)
    dataImporter.SetDataScalarTypeToUnsignedChar()

    # Because the data that is imported only contains an intensity value (it isnt RGB-coded or someting similar), the importer must be told this is the case (only one data value by gridpoint)
    dataImporter.SetNumberOfScalarComponents(1)

    # The following two functions describe how the data is stored and the dimensions of the array it is stored in. For this
    # simple case, all axes are of length 75 and begins with the first element. For other data, this is probably not the case.
    # I have to admit however, that I honestly dont know the difference between SetDataExtent() and SetWholeExtent() although
    # VTK complains if not both are used.
    dataImporter.SetDataExtent(0,x-1, 0, y-1, 0, z-1) #fun fact, for data[x,y,z] this uses z,y,x
    dataImporter.SetWholeExtent(0,x-1, 0, y-1, 0, z-1)

    #create alpha and colour functions (map values 0-255 to colour and transparency)
    alpha=vtk.vtkPiecewiseFunction()
    colour=vtk.vtkColorTransferFunction()

    lut=vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.SetTableRange(mn,mx)

    for i in range(256):
        #alpha.AddPoint(i,i/1024.)
        alpha.AddPoint(i,0.3)

        r=(i*2)/255.
        g=0.3
        b=(255.-2*i)/255
        if (r > 1.):
            r=1.
        if (b < 0.):
            b=0.
        colour.AddRGBPoint(i,r,g,b)
        lut.SetTableValue(i,r,g,b,1.0)

    lut.Build()

    colourbar=vtk.vtkScalarBarActor()

    colourbar.SetLookupTable(lut)
    #colourbar.SetAnnotationTextScaling(1)
    #colourbar.SetOrientationToHorizontal()
    colourbar.SetPosition(0.,0.1)
    colourbar.SetTitle("Temperature (Celsius)")

    self.win.renderer.AddActor(colourbar)

    # The preavious two classes stored properties. Because we want to apply these properties to the volume we want to render,
    # we have to store them in a class that stores volume prpoperties.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colour)
    volumeProperty.SetScalarOpacity(alpha)


    # This class describes how the volume is rendered (through ray tracing).
    #compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
    # We can finally create our volume. We also have to specify the data for it, as well as how the data will be rendered.
    volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
    #volumeMapper.SetVolumeRayCastFunction(compositeFunction)
    volumeMapper.SetInputConnection(dataImporter.GetOutputPort())

    tempactor.SetMapper(volumeMapper)
    tempactor.SetProperty(volumeProperty)

    t2=time.time()

    return colourbar

#     x, y, z = coords
#     points = vtk.vtkPoints()
#
#     scales = vtk.vtkFloatArray()
#     scales.SetName("Tscales")
#
#     col = vtk.vtkUnsignedCharArray()
#     col.SetName('Tcol')  # Any name will work here.
#     col.SetNumberOfComponents(3)
#
#     nc = vtk.vtkNamedColors()
#
#     tableSize = x * y * z
#     lut = vtk.vtkLookupTable()
#     lut.SetNumberOfTableValues(200)
#     lut.SetHueRange(0.6, 0.0)
#     #lut.SetAlphaRange(0.6,0.7)
#     lut.Build()
#
#     for k in range(x):
#         for j in range(y):
#             for i in range(z):
#                 if th[k][j][i] > 0.0000001:
#                     points.InsertNextPoint(k, j, i)
#                     scales.InsertNextValue(1.5)
#                     rgb = [0.0, 0.0, 0.0]
#                     lut.GetColor(th[k][j][i], rgb)
#                     ucrgb = list(map(int, [x * 255 for x in rgb]))
#                     col.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])
#
#     grid = vtk.vtkUnstructuredGrid()
#     grid.SetPoints(points)
#     grid.GetPointData().AddArray(scales)
#     grid.GetPointData().SetActiveScalars("Tscales")  # // !!!to set radius first
#     grid.GetPointData().AddArray(col)
#
#     sphere = vtk.vtkSphereSource()
#
#     glyph3D = vtk.vtkGlyph3D()
#
#     glyph3D.SetSourceConnection(sphere.GetOutputPort())
#     glyph3D.SetInputData(grid)
#     glyph3D.Update()
#
# # update mapper
#     rainmapper = vtk.vtkPolyDataMapper()
#     rainmapper.SetInputConnection(glyph3D.GetOutputPort())
#     rainmapper.SetScalarRange(0, 3)
#
#     rainmapper.SetScalarModeToUsePointFieldData()
#     rainmapper.SelectColorArray("Tcol")  # // !!!to set color (nevertheless you will have nothing)
#     rainmapper.SetLookupTable(lut)
#
#     rainactor.GetProperty().SetOpacity(0.1)
#     rainactor.SetMapper(rainmapper)

def RenderPress(p, coords, pressactor,p0):

    x,y,z = coords

    t1=time.time()
    parray=p
    mn=p.min()
    mx=p.max()

    #scale between 0 and 255
    parray=(parray-mn)/(mx-mn)*255

    #cast to uint


    data=parray.astype(numpy.uint8)


    data=numpy.ascontiguousarray(data)


    #Apparently VTK is rubbish at hacving people manually making VTK data structures, so we write this array to a string, which is then read into a VTK reader... inefficient I know... :/
    dataImporter = vtk.vtkImageImport()

    #make string (want it in Fortran order (column major) else everything is transposed
    data_string = data.tostring(order="F")

    #read in string
    dataImporter.CopyImportVoidPointer(data_string, len(data_string))

    # The type of the newly imported data is set to unsigned char (uint8)
    dataImporter.SetDataScalarTypeToUnsignedChar()

    # Because the data that is imported only contains an intensity value (it isnt RGB-coded or someting similar), the importer must be told this is the case (only one data value by gridpoint)
    dataImporter.SetNumberOfScalarComponents(1)

    # The following two functions describe how the data is stored and the dimensions of the array it is stored in. For this
    # simple case, all axes are of length 75 and begins with the first element. For other data, this is probably not the case.
    # I have to admit however, that I honestly dont know the difference between SetDataExtent() and SetWholeExtent() although
    # VTK complains if not both are used.
    dataImporter.SetDataExtent(0,x-1, 0, y-1, 0, z-1) #fun fact, for data[x,y,z] this uses z,y,x
    dataImporter.SetWholeExtent(0,x-1, 0, y-1, 0, z-1)

    #create alpha and colour functions (map values 0-255 to colour and transparency)
    alpha=vtk.vtkPiecewiseFunction()
    colour=vtk.vtkColorTransferFunction()

    lut=vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.SetTableRange((mn+p0)/100000,(mx+p0)/100000.)

    for i in range(256):
        #alpha.AddPoint(i,i/1024.)
        alpha.AddPoint(i,0.3)

        if (i < 128):
            r = (128.-i)/128.
            g = (i/128.)
            b=0.
        else:
            r=0
            g = (256.-i)/128.
            b = (i-128.)/128.
        colour.AddRGBPoint(i,r,g,b)
        lut.SetTableValue(i,r,g,b,1.0)

    lut.Build()

    colourbar=vtk.vtkScalarBarActor()

    colourbar.SetLookupTable(lut)
    colourbar.SetPosition(0.,0.1)
    colourbar.SetTitle("Pressure (Bar)")

    # The preavious two classes stored properties. Because we want to apply these properties to the volume we want to render,
    # we have to store them in a class that stores volume prpoperties.
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colour)
    volumeProperty.SetScalarOpacity(alpha)


    # This class describes how the volume is rendered (through ray tracing).
    #compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
    # We can finally create our volume. We also have to specify the data for it, as well as how the data will be rendered.
    volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
    #volumeMapper.SetVolumeRayCastFunction(compositeFunction)
    volumeMapper.SetInputConnection(dataImporter.GetOutputPort())

    pressactor.SetMapper(volumeMapper)
    pressactor.SetProperty(volumeProperty)

    t2=time.time()

    return colourbar

#     x, y, z = coords
#     points = vtk.vtkPoints()
#
#     scales = vtk.vtkFloatArray()
#     scales.SetName("Pscales")
#
#     col = vtk.vtkUnsignedCharArray()
#     col.SetName('Pcol')  # Any name will work here.
#     col.SetNumberOfComponents(3)
#
#     nc = vtk.vtkNamedColors()
#
#     tableSize = x * y * z
#     lut = vtk.vtkLookupTable()
#     lut.SetNumberOfTableValues(200)
#     lut.SetHueRange(0.6, 0.0)
#     #lut.SetAlphaRange(0.6,0.7)
#     lut.Build()
#
#     for k in range(x):
#         for j in range(y):
#             for i in range(z):
#                 if p[k][j][i] > 0.000000000001:
#                     points.InsertNextPoint(k, j, i)
#                     scales.InsertNextValue(1)
#                     rgb = [0.0, 0.0, 0.0]
#                     lut.GetColor(p[k][j][i], rgb)
#                     ucrgb = list(map(int, [x * 255 for x in rgb]))
#                     col.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])
#
#     grid = vtk.vtkUnstructuredGrid()
#     grid.SetPoints(points)
#     grid.GetPointData().AddArray(scales)
#     grid.GetPointData().SetActiveScalars("Pscales")  # // !!!to set radius first
#     grid.GetPointData().AddArray(col)
#
#     sphere = vtk.vtkSphereSource()
#
#     glyph3D = vtk.vtkGlyph3D()
#
#     glyph3D.SetSourceConnection(sphere.GetOutputPort())
#     glyph3D.SetInputData(grid)
#     glyph3D.Update()
#
#
#     #for k in range(x):
#     #    for j in range(y-int((y*0.4)), y+20):
#     #        points.InsertNextPoint(k, j, 2)
# #            points.InsertNextPoint(k, j, level)
#
#     # Create a polydata to store everything in
#     # linesPolyData = vtk.vtkPolyData()
#     # linesPolyData.Allocate()
#     #
#     # for i in range(0, points.GetNumberOfPoints(),2 ):
#     #     linesPolyData.InsertNextCell(vtk.VTK_LINE, 2, [i, i+1])
#     #
#     # # Add the points to the dataset
#     # linesPolyData.SetPoints(points)
#     #
#     # # update mapper
#     # rainmapper = vtk.vtkPolyDataMapper()
#     # rainmapper.SetInputData(linesPolyData)
#     #
#     #
#     # rainactor.GetProperty().SetOpacity(0.4)
#     # rainactor.GetProperty().SetLineWidth(10)
#     # rainactor.GetProperty().SetColor(0.1, 0.1, 0.8)
#     # rainactor.SetMapper(rainmapper)
#
#
# # update mapper
#     rainmapper = vtk.vtkPolyDataMapper()
#     rainmapper.SetInputConnection(glyph3D.GetOutputPort())
#     rainmapper.SetScalarRange(0, 3)
#
#     rainmapper.SetScalarModeToUsePointFieldData()
#     rainmapper.SelectColorArray("Pcol")  # // !!!to set color (nevertheless you will have nothing)
#     rainmapper.SetLookupTable(lut)
#
#     pressactor.GetProperty().SetOpacity(0.1)
#     pressactor.SetMapper(rainmapper)

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
            for i in range(-5,level):
                points.InsertNextPoint(k, j, i)

    for k in range(x):
        for j in range(-20, int((y*0.6))):
            for i in range(level,level+1):
                if random.random()>0.85:
                    points.InsertNextPoint(k, j, i)

    #grid = vtk.vtkUnstructuredGrid()
    #grid.SetPoints(points)

    #sphere = vtk.vtkSphereSource()

    #glyph3D = vtk.vtkGlyph3D()

    #glyph3D.SetSourceConnection(sphere.GetOutputPort())
    #glyph3D.SetInputData(grid)
    #glyph3D.Update()

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


def RenderLand(self, renderer):

    # x,y,z = coords
    #
    # points = vtk.vtkPoints()
    #
    # for k in range(x):
    #     for j in range(y-int((y*0.4)), y+20):
    #         for i in range(-5,3):
    #             points.InsertNextPoint(k, j, i)
    #
    # for k in range(x):
    #     for j in range(y-int((y*0.4)), y+20):
    #         for i in range(3,4):
    #             if random.random()>0.9:
    #                 points.InsertNextPoint(k, j, i)
    #
    # #grid = vtk.vtkUnstructuredGrid()
    # #grid.SetPoints(points)
    #
    # #sphere = vtk.vtkSphereSource()
    #
    # #glyph3D = vtk.vtkGlyph3D()
    #
    # #glyph3D.SetSourceConnection(sphere.GetOutputPort())
    # #glyph3D.SetInputData(grid)
    # #glyph3D.Update()
    #
    # polydata = vtk.vtkPolyData()
    #
    # polydata.SetPoints(points)
    #
    # splatter = vtk.vtkGaussianSplatter()
    #
    # splatter.SetInputData(polydata)
    # splatter.SetRadius(0.06)
    #
    # cf = vtk.vtkContourFilter()
    # cf.SetInputConnection(splatter.GetOutputPort())
    # cf.SetValue(0, 0.05)
    #
    # reverse = vtk.vtkReverseSense()
    # reverse.SetInputConnection(cf.GetOutputPort())
    # reverse.ReverseCellsOn()
    # reverse.ReverseNormalsOn()
    #
    #
    # landmapper = vtk.vtkPolyDataMapper()
    #
    # landmapper.SetInputConnection(reverse.GetOutputPort())
    # landmapper.SetScalarModeToUsePointFieldData()
    # landmapper.SetScalarRange(0, 3)

    if self.Location=="Edinburgh":
        file1="Edinburgh2.obj"
        img1='Edinburgh.png'
    elif self.Location=="London":
        file1="London2.obj"
        img1='London.png'
    elif self.Location=="Schiehallion":
        file1="Schiehallion2.obj"
        img1='Schiehallion.png'
    elif self.Location=="StIves":
        file1="StIves2.obj"
        img1='StIves.png'
    else:
        print("Error in location: ",self.Location)



    #read in 3d surface
    objreader1=vtk.vtkOBJReader()
    objreader1.SetFileName(file1)
    objreader1.Update()


    #read in image
    imgreader1=vtk.vtkPNGReader()
    imgreader1.SetFileName(img1)
    imgreader1.Update()

    #Convert the image to a texture
    texture1=vtk.vtkTexture()
    texture1.SetInputConnection(imgreader1.GetOutputPort())


    #get polydata output from OBJ reader
    polydata1=objreader1.GetOutput()


    #create mapper for the polydata
    mapper1=vtk.vtkPolyDataMapper()
    mapper1.SetInputData(polydata1)


    #create actor. attach mapper and texture
    landactor=vtk.vtkActor()
    landactor.SetMapper(mapper1)
    landactor.SetTexture(texture1)
    landactor.GetProperty().SetAmbient(1.0) #improve lighting
    landactor.RotateX(90) #flip round by 180 degrees (else it's upside down)
    landactor.RotateY(-90) #flip round by 180 degrees (else it's upside down)
    landactor.SetPosition(0,0,-2)

    #axes = vtk.vtkAxesActor()
    #renderer.AddActor(axes)
    renderer.AddActor(landactor)


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

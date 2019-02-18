# -*- coding: utf-8 -*-
from __future__ import print_function
import client
import numpy as np
import wx
import subprocess
import shutil
import time
import datetime
import argparse
import os

#select the UI abstract superclass to derive from
UI=client.AbstractmatplotlibUI

# Derive the demo-specific GUI class from the Abstract??UI class
class WaveWindow(UI):

    def __init__(self,parent,title,demo,servercomm,args):

        #call superclass' __init__
        UI.__init__(self,parent,title,demo,servercomm)

        self.args=args

        self.serverversion=False

        self.refreshrate = 0.1

        #variables for the log file
        self.now = datetime.datetime.now
        self.date=self.now().strftime("%Y-%m-%d")
        filename = self.date+".log"
        self.logfile = open(filename,'a')



        #INSERT CODE HERE TO SET LAYOUT OF WINDOW/ADD BUTTONS ETC

        #set up sizers that allow you to position window elements easily

        #main sizer - arrange items horizontally on screen (controls on left, display on right)
        self.mainsizer=wx.BoxSizer(wx.HORIZONTAL)

        #sizer for the plot window on the right ofthe screen
        self.PlotSizer=wx.BoxSizer(wx.VERTICAL)

        #sizer for buttons (align buttons vertically)
        self.buttonsizer=wx.BoxSizer(wx.VERTICAL)


        #button to start simulation/reset to setup screen
        self.SimButton=wx.Button(self,wx.ID_ANY,"Start a Simulation")
        self.Bind(wx.EVT_BUTTON,self.SwapScreens,self.SimButton)

        #Text box to display info on the costings
        self.logger = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2,size=(-1,-1))

        #Text box to show info on what the mouse is hovering over
        self.info = wx.TextCtrl(self,style=wx.TE_READONLY,size=(-1,-1))


        #Button for resetting the setup screen
        self.ResetButton=wx.Button(self,wx.ID_ANY,label="Reset")
        self.Bind(wx.EVT_BUTTON,self.reset,self.ResetButton)

        #Button for entering/exiting delete mode
        self.DeleteModeButton=wx.Button(self,wx.ID_ANY,"Enter Delete Mode")
        self.Bind(wx.EVT_BUTTON,self.DeleteMode,self.DeleteModeButton)

        #bar to display instructions to user
        self.infobar=wx.InfoBar(self)
        #tel the infobar to have no opening/closing animations as it slows down the UI
        self.infobar.SetShowHideEffects(wx.SHOW_EFFECT_NONE,wx.SHOW_EFFECT_NONE)


        #play/pause button for simulation results
        self.PlayButton=wx.Button(self,wx.ID_ANY,"Play")

        self.RewindButton=wx.Button(self,wx.ID_ANY,"Rewind")

        self.ResultsButton=wx.Button(self,wx.ID_ANY,"Results")


        #Place items in sizers
        self.mainsizer.Add(self.buttonsizer,1,wx.EXPAND | wx.ALL)
        self.mainsizer.Add(self.PlotSizer,3,wx.EXPAND)

        self.PlotSizer.Add(self.infobar,0,wx.EXPAND)
        self.PlotSizer.Add(self.canvas,3,wx.EXPAND | wx.ALL)

        self.fno=4




        self.ShowSetupControls()

        self.resultsscreen=False


        self.SetSizer(self.mainsizer)
        self.Fit()



        #show window
        self.Show()



    def StartInteractor(self):
        UI.StartInteractor(self)
        #INSERT ANY CUSTOM CODE HERE




    def StartSim(self,config):
        UI.StartSim(self,config)
        #INSERT ANY CUSTOM CODE HERE




    def StopSim(self):
        UI.StopSim(self)
        #INSERT ANY CUSTOM CODE HERE

    # Renders the contents of a file on the server
    def RenderFrame(self,number):
        if self.nfiles.value>4:
            self.frameno.value=number
            print("Frame number= %d"%number)
            self.getdata.value=True
            self.dto=self.pipemain.recv()
            self.getdata.value=False
            self.pipemain.send(0)

            print("Datatype=", self.dto.GetData().GetType())

            self.figure.clf()
            self.plt=self.figure.add_subplot(111)

            data=self.dto.GetData().GetData()
            self.plt.imshow(data - 20*(1-self.mask),vmin=-10,vmax=2,cmap="ocean")
            self.plt.axis("off")
            self.canvas.draw()




    def TimerCallback(self,e):

        if self.servercomm.IsStarted():
            print("Number of files= %d"%self.nfiles.value)

            self.RenderFrame(self.fno)
            self.fno+=1
            if self.fno == 124:
                self.fno=4
                self.timer.Stop()






    def OnClose(self,e):
        print("Requested an exit")
        UI.OnClose(self,e)
        self.logfile.close()
        quit()

        #INSERT ANY CUSTOM CODE HERE



    #----------------------------------------------------------------------
    #------------- New methods specific to demo go here -------------------
    #----------------------------------------------------------------------

    def UpdateResults(self,e):
        print("nothing to see here")



    def SwapScreens(self,e):
        if self.resultsscreen == True:
            self.StopSim()
            self.ShowSetupControls()
            self.resultsscreen=False
        else:

            dlg=wx.ProgressDialog("Please Wait","Setting up the simulation.",parent=self,)
            dlg.Show()
            dlg.Update(0)

            #Add defences to the mask
            depth=self.depth
            mask=self.mask

            for block in self.blocks:
                x,y = block.get_position()
                print("Adding block at x=%d, y=%d"%(x,y))
                xi=x-5
                xf=x+5
                yi=y-10
                yf=y+10
                mask[yi:yf,xi:xf]=0.
                block.disconnect()

            dlg.Update(10)





            self.resultsscreen=True

            #Do a few jacobi iterations over the depth to smooth out the sharp jumps in depth caused by the defences

            ny=len(mask)
            nx=len(mask[0])
            tmp = np.zeros((ny,nx),np.float64)
            tmp[:,:] = 4*depth[:,:]
            for n in range(100):
                print(n)
                tmp[1:ny-1,1:nx-1] = depth[0:ny-2,1:nx-1]+depth[2:ny,1:nx-1]+depth[1:ny-1,0:nx-2]+depth[1:ny-1,2:nx]
                depth=0.25*tmp*mask


            dlg.Update(40)



            type="%-20s"%"depth"


            #rescale the depth so it gors from 0.05-1 rather than 0-1
            depth = 0.95*depth + 0.05

            #write the new depth profiles and damping coefficents to file

            f=open("depth.dat","wb")
            f.write(type)
            f.write(np.asarray([nx,ny],np.int32))
            f.write(np.asarray(0.,np.float64))
            f.write(depth)
            f.close()

            type="%-20s"%"damping"
            damping = 1.*(1.-mask)
            f=open("damping.dat","wb")
            f.write(type)
            f.write(np.asarray([nx,ny],np.int32))
            f.write(np.asarray(0.,np.float64))
            f.write(damping)
            f.close()

            dlg.Update(60)

            #os.system("cp damping.dat depth.dat mask.dat simulation/")
            os.system("tar -czf data.tar.gz damping.dat mask.dat depth.dat")
            #os.system("export OMP_NUM_THREADS=4; simulation/main")

            dlg.Update(100)

            self.ShowResultsControls()

            self.fno=4

            time.sleep(1)

            self.StartSim("data.tar.gz")

            dlg.Destroy()



    def ShowResultsControls(self):
        self.figure.clf()
        self.HideSetupControls()
        self.buttonsizer.Clear()

        self.SimButton.Show()
        self.PlayButton.Show()
        self.RewindButton.Show()
        self.ResultsButton.Show()

        self.buttonsizer.Add(self.SimButton,0,wx.EXPAND|wx.ALIGN_TOP)
        self.SimButton.SetLabel("New Simulation")
        self.buttonsizer.Add(self.logger,1,wx.EXPAND)
        self.buttonsizer.Add(self.PlayButton,0,wx.EXPAND)
        self.buttonsizer.Add(self.RewindButton,0,wx.EXPAND)
        self.buttonsizer.Add(self.ResultsButton,0,wx.EXPAND|wx.ALIGN_BOTTOM)

        self.logger.Clear()

        self.logger.AppendText("Simulation playing...")

        self.ResultsButton.Disable()

        self.buttonsizer.Layout()
        self.Fit()
        self.Update()

        self.infobar.Dismiss()



    def HideResultsControls(self):
        self.SimButton.Hide()
        self.PlayButton.Hide()
        self.RewindButton.Hide()
        self.ResultsButton.Hide()


    def HideSetupControls(self):
        self.SimButton.Hide()
        self.ResetButton.Hide()
        self.DeleteModeButton.Hide()
        self.info.Hide()




    def ShowSetupControls(self):
        self.HideResultsControls()
        self.buttonsizer.Clear()

        self.SimButton.Show()
        self.logger.Show()
        self.DeleteModeButton.Show()
        self.ResetButton.Show()
        self.info.Show()

        self.buttonsizer.Add(self.SimButton,0,wx.EXPAND|wx.ALIGN_TOP)
        self.buttonsizer.Add(self.logger,1,wx.EXPAND | wx.ALIGN_CENTER)
        self.DeleteModeButton.Disable()
        self.buttonsizer.Add(self.DeleteModeButton,0,wx.EXPAND)
        self.buttonsizer.Add(self.ResetButton,0,wx.EXPAND | wx.ALIGN_BOTTOM)
        self.buttonsizer.Add(self.info,0,wx.EXPAND)

        self.infobar.ShowMessage("Click on the sea to add defences. Click and drag on existing defences to move them.")

        self.buttonsizer.Layout()
        self.Fit()

        self.SimButton.SetLabel("Run Simulation")


        self.budget=100


        self.figure.clf()

        self.depth=self.ReadCoastArray("depth_profile.dat")
        self.mask=self.ReadCoastArray("mask.dat")


        self.plt=self.figure.add_subplot(111)
        #self.plt.imshow(self.blob,zorder=2,extent=(145,165,140,160))
        self.plt.imshow(self.mask,vmin=0,vmax=1.2,zorder=1,cmap="ocean")
        self.plt.axis("off")
        self.figure.tight_layout()
        #levels=np.arange(-1,1,0.1)
        #cs=self.plt.contour(self.depth,levels=levels,cmap="Blues")#colors="Black")
        #self.plt.clabel(cs,zorder=1)
        self.canvas.draw()
        self.canvas.Refresh()



        self.canvas.mpl_connect("button_press_event",self.onclick)
        self.canvas.mpl_connect("motion_notify_event",self.mousemove)
        self.nblock=0

        self.blocks=[]

        self.delete=False



        self.spreadsheet()





    def ReadCoastArray(self,fname):
        f=open(fname,"rb")
        print("---------------------------")
        print("Opening '%s'"%fname)
        text=np.fromfile(f,np.byte,20)
        text=text.tostring()
        print("Filetype is: %s"%text)
        nxy=np.fromfile(f,np.int32,2)
        #print(nxy)
        print("nx=%d, ny=%d"%(nxy[0],nxy[1]))
        t=np.fromfile(f,np.float64,1)
        print("Time is %2.2f"%t)
        print("---------------------------")

        data=np.fromfile(f,np.float64,nxy[0]*nxy[1])

        f.close()

        return data.reshape((nxy[0],nxy[1]))



    # Callback for when the mouse is moved over the matplotlib window
    # (Updates the info bar with information on where the mouse is over)
    def mousemove(self,e):
        self.info.Clear()
        x=(e.xdata)
        y=(e.ydata)
        if (x == None or y==None):
            return
        x=int(x)
        y=int(y)

        d=self.depth[y][x]
        if d> 0.05:
            self.info.AppendText("Depth = %3.0fm, Cost = £%2d,000"%(100.*d,15+int(10*d)))
        else:
            self.info.AppendText("You cannot place a defence here")


    # Determine if a defence can be placed here
    def can_place(self,x,y):
        i=0
        if x<5 or x>=235 or y<10 or y>=230: return False
        if self.depth[y][x] < 0.05: return False
        for block in self.blocks:
            xp,yp = block.get_position()
            if (np.abs(x-xp) < 5 and np.abs(y-yp) < 10):
                print(i)
                if self.delete:
                    block.disconnect()
                    self.blocks.pop(i)
                    self.canvas.draw()
                    self.canvas.Refresh()
                    self.nblock-=1
                return False
            i+=1

        return True

    #Callback when an area of the matplotlib window is clicked on
    def onclick(self,e):

        x=e.xdata
        y=e.ydata

        if (x == None or y == None):
            print("Invalid input")
            return

        i=int(x)
        j=int(y)

        if not self.can_place(i,j):
            print("Can't place a block here")
            return

        if self.delete: return

        if self.budget <= 0:
            wx.MessageDialog(self,"You do not have any more money. Please delete or move an existing defence.","Warning",wx.OK).ShowModal()
            return



        imax = min(239,i+5)
        imin = max(0,i-5)

        jmax= min(j+10,239)
        jmin = max(0,j-10)

        #We not want to place a defence
        self.nblock+=1
        block=self.plt.bar(x=x,height=20,width=10,bottom=y-10,align="center",zorder=3,color="Grey")
        label=self.plt.text(x,y,"%d"%(self.nblock),horizontalalignment="center",verticalalignment="center")
        block=block[0]

        rect=DraggableRectangle(block,label,self.depth,self)
        rect.connect()

        self.blocks.append(rect)


        self.canvas.draw()
        self.canvas.Refresh()

        self.logger.AppendText("x=%d, y=%d \n"%(x,y))

        if self.nblock >= 1:
            #for block in self.blocks:
            #    block.rect.set_color("Red")
            #self.delete=True
            self.DeleteModeButton.Enable()

        self.spreadsheet()





    def reset(self,e):
        for block in self.blocks:
            block.disconnect()
        self.blocks=[]
        self.canvas.draw()
        self.nblock=0
        self.logger.Clear()
        self.delete=False
        self.DeleteModeButton.Disable()
        self.spreadsheet()

    def DeleteMode(self,e):
        #We are already in delete mode. Switch it off
        if self.delete:
            self.infobar.ShowMessage("Click on the sea to add defences. Click and drag on existing defences to move them.")
            self.SimButton.Enable()
            self.ResetButton.Enable()
            self.delete=False
            self.DeleteModeButton.SetLabel("Enter Delete Mode")
            i=1
            for block in self.blocks:
                block.rect.set_color("Grey")
                block.label.set_text("%d"%i)
                i+=1
            if len(self.blocks) == 0:
                self.DeleteModeButton.Disable()
            self.canvas.draw()
            self.spreadsheet()

        else: #we are not in delete mode. Turn it on
            self.infobar.ShowMessage("Click on defences to delete them. Click 'Done' once finished")
            self.delete=True
            self.DeleteModeButton.SetLabel("Done")
            self.SimButton.Disable()
            self.ResetButton.Disable()
            for block in self.blocks:
                block.rect.set_color("Red")
                #block.label.set_text("-")
            self.canvas.draw()

    # Display text in the logger that describes money spent on existing defences
    def spreadsheet(self):
        self.logger.Clear()
        self.budget = 100
        basecost=15
        self.logger.AppendText("Total budget = £%3d,000\n"%self.budget)
        self.logger.AppendText("\n")
        i=1
        for block in self.blocks:
            block.label.set_text("%d"%i)
            depthcost=int(block.depthm*10)+15
            self.budget -= depthcost
            self.logger.AppendText("Block %2d:   - £%2d,000\n"%(i,depthcost))
            i+=1
        self.logger.AppendText("\n")
        self.logger.AppendText("-----------------\n")
        self.logger.AppendText("Remaining budget= ")
        if self.budget >= 0:
            self.logger.SetDefaultStyle(wx.TextAttr(wx.Colour((0,150,0))))
        else:
            self.logger.SetDefaultStyle(wx.TextAttr(wx.Colour(255,0,0)))

        self.logger.AppendText("£%3d,000"%self.budget)
        self.logger.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        if self.budget < 0:
            self.SimButton.Disable()
        else:
            if not self.delete:
                self.SimButton.Enable()





class DraggableRectangle:
    def __init__(self, rect,label,depth,parent):
        self.rect = rect
        self.label=label
        self.depth=depth
        self.press = None
        self.parent = parent
        self.getxy()
        self.depthm=depth[int(self.y),int(self.x)]
        print("New block with (x,y)= (%d, %d)"%(self.x,self.y))

    def getxy(self):
        self.x, self.y=self.rect.xy
        self.x+=5
        self.y+=10

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.rect.figure.canvas.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect(
            'motion_notify_event', self.on_motion)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if (event.inaxes != self.rect.axes) and  (event.inaxis != self.label.axes): return


        contains, attrd = self.rect.contains(event)
        if not contains: return
        print('event contains', self.rect.xy)

        x0, y0 = self.rect.xy
        self.press = x0, y0, event.xdata, event.ydata

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if self.press is None: return
        if (event.inaxes != self.rect.axes) and  (event.inaxis != self.label.axes): return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        if self.depth[int(event.ydata)][int(event.xdata)] < 0.05:
            #print(event.xdata,event.ydata)
            return
        #print('x0=%f, xpress=%f, event.xdata=%f, dx=%f, x0+dx=%f' %
        #      (x0, xpress, event.xdata, dx, x0+dx))
        self.rect.set_x(x0+dx)
        self.rect.set_y(y0+dy)
        self.label.set_x(x0+dx+5)
        self.label.set_y(y0+dy+10)

        self.rect.figure.canvas.draw()


    def on_release(self, event):
        'on release we reset the press data'
        self.press = None
        self.getxy()
        self.depthm=self.depth[int(self.y),int(self.x)]
        self.rect.figure.canvas.draw()
        self.parent.spreadsheet()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)
        self.rect.remove()
        self.label.remove()
        print("Deleting Block")


    def get_position(self):
        x,y = self.rect.xy
        return int(x+5),int(y+10)




    #
    # def ShowRange(self,e):
    #     (c_lift,c_drag)=(self.potential.C_la,self.potential.C_da)
    #     print("lift=",c_lift,"  drag=",c_drag)
    #     self.RangeFrame = Range.Range(self,"Range",(1080,540),c_lift=c_lift,c_drag=c_drag)
    #     self.RangeFrame.Show()
    #
    #
    # def ShowTakeoff(self,e):
    #
    #     (c_lift,c_drag)=(self.potential.C_la,self.potential.C_da)
    #     print("lift=",c_lift,"  drag=",c_drag)
    #     self.TakeoffFrame = takeoff.Takeoff(self,'Runway',size=(1200,675),c_lift=c_lift,c_drag=c_drag)
    #     self.TakeoffFrame.Show()

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
import matplotlib.gridspec as gridspec

#select the UI abstract superclass to derive from
UI=client.AbstractmatplotlibUI

# Derive the demo-specific GUI class from the Abstract??UI class
class WaveWindow(UI):

    def __init__(self,parent,title,demo,servercomm,args):

        #call superclass' __init__
        UI.__init__(self,parent,title,demo,servercomm)

        self.args=args

        self.serverversion=False

        self.refreshrate = 0.25

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
        #self.PlayButton=wx.Button(self,wx.ID_ANY,"Play")

        #self.RewindButton=wx.Button(self,wx.ID_ANY,"Rewind")

        self.ResultsButton=wx.Button(self,wx.ID_ANY,"Results")
        self.Bind(wx.EVT_BUTTON,self.results,self.ResultsButton)


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
    # def RenderFrame(self,number):
    #     if self.nfiles.value>4:
    #         self.frameno.value=number
    #         print("Frame number= %d"%number)
    #         self.getdata.value=True
    #         self.dto=self.pipemain.recv()
    #         self.getdata.value=False
    #         self.pipemain.send(0)
    #
    #         print("Datatype=", self.dto.GetData().GetType())
    #
    #         self.figure.clf()
    #         self.plt=self.figure.add_subplot(111)
    #
    #         data=self.dto.GetData().GetData()
    #         self.plt.imshow(data - 20*(1-self.mask),vmin=-10,vmax=2,cmap="ocean")
    #         self.plt.axis("off")
    #         self.canvas.draw()

    def get_dto(self,number):

        self.frameno.value=number
        print("Frame number= %d"%number)
        self.getdata.value=True
        dto=self.pipemain.recv()
        self.getdata.value=False
        self.pipemain.send(0)
        return dto






    def TimerCallback(self,e):

        if self.servercomm.IsStarted():
            nfiles=self.nfiles.value
            print("In timer callback: nfiles=%d, fno=%d"%(nfiles,self.fno))
            if self.simfinished.value:
                self.logger.Clear()
                self.logger.AppendText("Simulation complete.\n\nClick 'Results' below to view wave heights")
                self.ResultsButton.Enable()

            if self.fno <= nfiles-1:
                print("Trying to get file #%d"%self.fno)
                self.dto= self.get_dto(self.fno)

                atype = "%-20s"%"A"
                whtype= "%-20s"%"waveheights"

                if self.dto.GetData().GetType() == atype:
                    self.figure.clf()
                    self.plt=self.figure.add_subplot(111)

                    data=self.dto.GetData().GetData()
                    self.plt.imshow(data - 20*(1-self.mask),vmin=-10,vmax=2,cmap="ocean")
                    self.plt.axis("off")
                    self.canvas.draw()
                elif self.dto.GetData().GetType() == whtype:
                    print("Waveheights file reached")
                    self.ResultsButton.Enable()
                    #self.timer.Stop()

                    self.results(0)

                else:
                    print("ERROR")
                    print("'%s'"%self.dto.GetData().GetType())

                self.fno+=1#=nfiles-1





    def results(self,e):
        if self.timer.IsRunning():
            self.timer.Stop()
            self.dto= self.get_dto(self.nfiles.value-1)
            self.logger.Clear()
            self.logger.AppendText("Some results go here...")

            self.figure.clf()

            spec = gridspec.GridSpec(ncols=1,nrows=3,figure=self.figure)
            #ax1=self.figure.add_subplot(211)
            ax1=self.figure.add_subplot(spec[0:2,:])
            #self.plt2=self.figure.add_subplot(212)

            data=self.dto.GetData().GetData()

            reference=self.ReadCoastArray("reference.dat")

            data2=smooth(data,10)
            reference2=smooth(reference,10)

            ax1.plot(data2,label="With Defences",color="green")
            ax1.plot(reference2,label="No Defences",color="red")
            ax1.get_xaxis().set_visible(False)
            ax1.legend()
            ax1.set_ylabel("Wave Height (m)")

            ax1.axes.set_ylim(bottom=0)

            #self.plt=self.figure.add_subplot(212,sharex=ax1)
            self.plt=self.figure.add_subplot(spec[2,:],sharex=ax1)
            self.plt.imshow(self.mask[120:,:],aspect="auto",vmin=0,vmax=1.2,zorder=1,cmap="ocean")
            self.plt.axis("off")

            self.canvas.draw()

            self.ResultsButton.SetLabel('Replay')

        else:
            self.ResultsButton.SetLabel("Results")
            self.logger.Clear()
            self.logger.AppendText("Simulation complete.\n\nClick 'Results' below to view wave heights")
            self.fno=0
            self.timer.Start()









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
                xi=x-10
                xf=x+10
                yi=y-5
                yf=y+5
                mask[yi:yf,xi:xf]=0.
                block.disconnect()

            dlg.Update(10)


            self.resultsscreen=True

            #Do a few jacobi iterations over the depth to smooth out the sharp jumps in depth caused by the defences

            ny=len(mask)
            nx=len(mask[0])
            tmp = np.zeros((ny,nx),np.float64,order="F")
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

            depth=np.transpose(depth)


            f=open("depth.dat","wb")
            f.write(type)
            f.write(np.asarray([ny,nx],np.int32))
            f.write(np.asarray(0.,np.float64))
            f.write(np.ascontiguousarray(depth))
            f.close()

            type="%-20s"%"damping"
            damping = 1.*(1.-mask)
            damping=np.transpose(damping)
            f=open("damping.dat","wb")
            f.write(type)
            f.write(np.asarray([ny,nx],np.int32))
            f.write(np.asarray(0.,np.float64))
            f.write(np.ascontiguousarray(damping))
            f.close()

            dlg.Update(60)

            #os.system("cp damping.dat depth.dat mask.dat simulation/")
            os.system("tar -czf data.tar.gz damping.dat mask.dat depth.dat")
            #os.system("export OMP_NUM_THREADS=4; simulation/main")

            dlg.Update(100)

            self.ShowResultsControls()

            self.fno=0

            time.sleep(1)

            self.StartSim("data.tar.gz")

            dlg.Destroy()



    def ShowResultsControls(self):
        self.figure.clf()
        self.HideSetupControls()
        self.buttonsizer.Clear()

        self.SimButton.Show()
        #self.PlayButton.Show()
        #self.RewindButton.Show()
        self.ResultsButton.Show()

        self.buttonsizer.Add(self.SimButton,0,wx.EXPAND|wx.ALIGN_TOP)
        self.SimButton.SetLabel("New Simulation")
        self.buttonsizer.Add(self.logger,1,wx.EXPAND)
        #self.buttonsizer.Add(self.PlayButton,0,wx.EXPAND)
        #self.buttonsizer.Add(self.RewindButton,0,wx.EXPAND)
        self.buttonsizer.Add(self.ResultsButton,0,wx.EXPAND|wx.ALIGN_BOTTOM)

        self.logger.Clear()

        self.logger.AppendText("Simulation in progress...")

        self.ResultsButton.Disable()

        self.buttonsizer.Layout()
        self.Fit()
        self.Update()

        self.infobar.Dismiss()



    def HideResultsControls(self):
        self.SimButton.Hide()
        #self.PlayButton.Hide()
        #self.RewindButton.Hide()
        self.ResultsButton.Hide()


    def HideSetupControls(self):
        self.SimButton.Hide()
        self.ResetButton.Hide()
        self.DeleteModeButton.Hide()
        for handle in self.callbackhandles:
            self.canvas.mpl_disconnect(handle)

        self.callbackhandles=[]
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
        self.plt.imshow(self.mask,vmin=0,vmax=1.2,zorder=1,cmap="ocean")#,interpolation="bilinear")
        self.plt.axis("off")
        #self.figure.tight_layout()
        #levels=np.arange(-1,1,0.1)
        #cs=self.plt.contour(self.depth,levels=levels,cmap="Blues")#colors="Black")
        #self.plt.clabel(cs,zorder=1)
        self.canvas.draw()
        self.canvas.Refresh()


        self.callbackhandles=[]
        self.callbackhandles.append(self.canvas.mpl_connect("button_press_event",self.onclick))
        self.callbackhandles.append(self.canvas.mpl_connect("motion_notify_event",self.mousemove))
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

        wtype="%-20s"%"waveheights"
        atype="%-20s"%"A"
        mtype="%-20s"%"mask"
        dtype="%-20s"%"depth_profile"

        if text == atype or text == mtype or text == dtype:
            data=np.fromfile(f,np.float64,nxy[0]*nxy[1])
            data=data.reshape((nxy[0],nxy[1]),order="F")
        elif text == wtype:
            data=np.fromfile(f,np.float64,nxy[1])

        else:
            print("ERROR: wrong type '%s'"%text)

        f.close()

        return data





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
        print(x,y)
        if x<5 or x>=470 or y<10 or y>=230: return False
        if self.depth[y][x] < 0.05: return False
        for block in self.blocks:
            xp,yp = block.get_position()
            if (np.abs(x-xp) < 10 and np.abs(y-yp) < 5):
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
        block=self.plt.bar(x=x,height=10,width=20,bottom=y-5,align="center",zorder=3,color="Grey")
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
        self.logger.SetDefaultStyle(wx.TextAttr(wx.BLACK))
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
        self.x+=10
        self.y+=5

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
        self.label.set_x(x0+dx+10)
        self.label.set_y(y0+dy+5)

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
        return int(x+10),int(y+5)

def smooth(data,w):
    nx = len(data)

    smoothed = np.zeros(nx)
    dd=np.concatenate([data,data,data])

    for i in range(nx,2*nx):
        wgt=0.
        for j in range(i-nx/4,i+nx/4):
            #smoothed[i-nx] += dd[j]
            smoothed[i-nx] += dd[j] * np.exp(-(i-j)*(i-j)/w/w)
            wgt+=np.exp(-(i-j)*(i-j)/w/w)
        smoothed[i-nx] /=wgt

    #smoothed= smoothed/(len(range(-w,w)))

    return smoothed




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

# -*- coding: utf-8 -*-
from __future__ import print_function
from client import AbstractmatplotlibUI
import numpy as np
import wx
import subprocess
import shutil
import time
import datetime
import argparse
import os
import matplotlib.gridspec as gridspec
import matplotlib.pyplot as plt
import InfoScreen

#select the UI abstract superclass to derive from
UI=AbstractmatplotlibUI


#all costs are in units of £1000
Budget=200

BeachCost= 10
HouseCost= 100
LibraryCost=50
ShopCost=40
OriginalCost = BeachCost+HouseCost+LibraryCost+ShopCost

RestoreBlocks=True


# Derive the demo-specific GUI class from the AbstractUI class
class WaveWindow(UI):

    def __init__(self,parent,title,demo,servercomm,args):

        #call superclass' __init__
        UI.__init__(self,parent,title,demo,servercomm)

        self.args=args

        #Flag to tell the UI to use the server or to use a local simuation file
        #(local files not supported yet)
        self.serverversion=True

        #How often we should poll the server for new results
        self.refreshrate = 0.25

        #File number we want to read first
        self.fno=0

        #variables for the log file
        self.now = datetime.datetime.now
        self.date=self.now().strftime("%Y-%m-%d")
        filename = self.date+".log"
        self.logfile = open(filename,'a')


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

        #Button to show results
        self.ResultsButton=wx.Button(self,wx.ID_ANY,"Results")
        self.Bind(wx.EVT_BUTTON,self.results,self.ResultsButton)


        #Place items in sizers
        self.mainsizer.Add(self.buttonsizer,1,wx.EXPAND | wx.ALL)
        self.mainsizer.Add(self.PlotSizer,3,wx.EXPAND)

        self.PlotSizer.Add(self.infobar,0,wx.EXPAND)
        self.PlotSizer.Add(self.canvas,3,wx.EXPAND | wx.ALL)










        #Set the sizer for the window and fit everything to the window
        self.SetSizer(self.mainsizer)

        self.resultsscreen=False
        self.ShowSetupControls()

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



    # Method called by the timer. Checks if the simulation is finished, and displays simulation frames
    def TimerCallback(self,e):
        if self.servercomm.IsStarted():
            #get number files produced by simulation so far
            nfiles=self.nfiles.value
            print("In timer callback: nfiles=%d, fno=%d"%(nfiles,self.fno))

            if self.simfinished.value:
                self.logger.Clear()
                self.logger.AppendText("Simulation complete.\n\nClick 'Results' below to view wave heights")
                self.ResultsButton.Enable()

            #If the file number we wish to display (self.fno) exists on the server then let's fetch it and render the data. Otherwise do nothing
            if self.fno <= nfiles-1:
                print("Trying to get file #%d"%self.fno)
                self.dto= self.get_dto(self.fno)

                atype = "%-20s"%"A"
                whtype= "%-20s"%"waveheights"

                #If the file contains "A" data then render its contents
                if self.dto.GetData().GetType() == atype:
                    self.figure.clf()
                    self.plt=self.figure.add_subplot(111)

                    data=self.dto.GetData().GetData()
                    self.plt.imshow(data - 20*(1-self.mask),vmin=-10,vmax=2,cmap="ocean")
                    self.plt.axis("off")
                    self.canvas.draw()

                #Otherwise if the datatype is "waveheights" then we are finished. Load the results screen
                elif self.dto.GetData().GetType() == whtype:
                    print("Waveheights file reached")
                    self.ResultsButton.Enable()
                    #self.timer.Stop()

                    self.results(0)

                else:
                    print("ERROR")
                    print("'%s'"%self.dto.GetData().GetType())
                #increment the filenumber we wish to read by 1
                self.fno+=1


    def OnClose(self,e):
        #make sure we close the sim block in the log
        if self.resultsscreen==True:
            self.logfile.write("</sim>\n")
        print("Requested an exit")
        UI.OnClose(self,e)
        self.logfile.close()
        quit()

        #INSERT ANY CUSTOM CODE HERE



    #----------------------------------------------------------------------
    #------------- New methods specific to demo go here -------------------
    #----------------------------------------------------------------------



    #Method called when the StartSim button is pressed
    def SwapScreens(self,e):
        #We are on the results screen. Stop the simulation and show the setup screen
        if self.resultsscreen == True:
            self.StopSim()
            self.ShowSetupControls(RestoreBlocks)
            self.resultsscreen=False
            self.logfile.write("</sim>\n")

        #We are on the setup screen. We wish to produce input files and start a simulation
        else:

            dlg=wx.ProgressDialog("Please Wait","Setting up the simulation.",parent=self,)
            dlg.Show()
            dlg.Update(0)

            #Add defences to the mask
            depth=self.depth
            mask=self.mask

            f=open("blocks.dat","w")

            for block in self.blocks:
                x,y = block.get_position()
                print("Adding block at x=%d, y=%d"%(x,y))
                xi=x-10
                xf=x+10
                yi=y-5
                yf=y+5
                mask[yi:yf,xi:xf]=0.
                #Write this to file so we can reload it later
                f.write("%d %d\n"%(x,y))


            dlg.Update(10)
            f.close()


            self.resultsscreen=True

            #Do a few jacobi iterations over the depth to smooth out the sharp jumps in depth caused by the defences

            ny=len(mask)
            nx=len(mask[0])
            tmp = np.zeros((ny,nx),np.float64,order="F")
            tmp[:,:] = 4*depth[:,:]
            for n in range(100):
                print(n)
                tmp[0,1:nx-1] = depth[ny-1,1:nx-1]+depth[1,1:nx-1]+depth[0,0:nx-2]+depth[0,2:nx]
                tmp[1:ny-1,1:nx-1] = depth[0:ny-2,1:nx-1]+depth[2:ny,1:nx-1]+depth[1:ny-1,0:nx-2]+depth[1:ny-1,2:nx]
                tmp[ny-1,1:nx-1] = depth[ny-2,1:nx-1]+depth[0,1:nx-1]+depth[ny-1,0:nx-2]+depth[ny-1,2:nx]
                depth=0.25*tmp*mask


            dlg.Update(40)

            #rescale the depth so it gors from 0.05-1 rather than 0-1
            depth = 0.95*depth + 0.05

            #write the new depth profiles and damping coefficents to file
            depth=np.transpose(depth)

            f=open("depth.dat","wb")
            type="%-20s"%"depth"
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

            #tar all the input files up
            os.system("tar -czf data.tar.gz damping.dat mask.dat depth.dat")


            dlg.Update(100)
            self.StartSim("data.tar.gz")

            #Write simulation info to log file
            simid=self.servercomm.simid
            self.logfile.write('<sim id="%s">\n'%simid)
            self.logfile.write("  <blocks>\n")

            for block in self.blocks:
                x,y = block.get_position()
                self.logfile.write('    <block x="%d" y="%d"/>\n'%(x,y))
                #Get rid of this block (and make sure its callbacks are deleted)
                block.disconnect()

            self.logfile.write('    <cost> %d </cost>\n'%(Budget-self.budget))

            self.logfile.write('  </blocks>\n')

            self.logIncomplete=True

            dlg.Update(10)
            f.close()

            self.ShowResultsControls()

            self.fno=0


            dlg.Destroy()




    #Shows the result controls
    def ShowResultsControls(self):
        self.figure.clf()
        self.HideSetupControls()
        self.buttonsizer.Clear()

        self.SimButton.Show()
        self.ResultsButton.Show()
        self.ResultsButton.SetLabel("Results")

        self.buttonsizer.Add(self.SimButton,0,wx.EXPAND|wx.ALIGN_TOP)
        self.SimButton.SetLabel("New Simulation")
        self.buttonsizer.Add(self.logger,1,wx.EXPAND)
        self.buttonsizer.Add(self.ResultsButton,0,wx.EXPAND|wx.ALIGN_BOTTOM)

        self.logger.Clear()

        self.logger.AppendText("Simulation in progress...")

        self.ResultsButton.Disable()

        self.buttonsizer.Layout()

        self.Update()

        self.infobar.Dismiss()



    #Shows the setup controls
    def ShowSetupControls(self,restore=False):
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

        self.SimButton.SetLabel("Run Simulation")

        self.figure.clf()

        #read depth profile and the mask
        self.depth=self.ReadCoastArray("depth_profile.dat")
        self.mask=self.ReadCoastArray("mask.dat")


        self.plt=self.figure.add_subplot(111)


        #read in and display the image of the coastline
        bg = plt.imread("coastline_nocost.png")
        self.plt.imshow(bg,extent=(0,479,239,0))#,interpolation="bilinear")
        self.plt.axis("off")
        self.figure.tight_layout()

        #Set callbacks for when the image is clicked on and when a mouse overs over it
        self.callbackhandles=[]
        self.callbackhandles.append(self.canvas.mpl_connect("button_press_event",self.onclick))
        self.callbackhandles.append(self.canvas.mpl_connect("motion_notify_event",self.mousemove))

        #initialise our block count to zero and initialise our block list
        self.nblock=0
        self.blocks=[]

        #If we have requested a previous block configuration tobe read in then we do it here
        if restore:
            print("Restoring blocks from file")

            f=open("blocks.dat","r")

            for line in f:
                xy=line.split()
                x=int(xy[0])
                y=int(xy[1])
                print("Adding block at (x,y) = (%d,%d)"%(x,y))
                self.nblock+=1
                block=self.plt.bar(x=x,height=10,width=20,bottom=y-5,align="center",zorder=3,color="Grey")
                label=self.plt.text(x,y,"%d"%(self.nblock),horizontalalignment="center",verticalalignment="center")
                block=block[0]

                rect=DraggableRectangle(block,label,self.depth,self)
                rect.connect()

                self.blocks.append(rect)
            f.close()

        #Set the delete mode to be off
        self.delete=False

        self.canvas.draw()
        self.canvas.Refresh()

        #Get block costings and display them on the logger
        self.spreadsheet()



        info=InfoScreen.Info(self,"Info",(1000,750))
        info.Show()



    #Hides the results controls
    def HideResultsControls(self):
        self.SimButton.Hide()
        self.ResultsButton.Hide()



    #Hides the setup controls
    def HideSetupControls(self):
        self.SimButton.Hide()
        self.ResetButton.Hide()
        self.DeleteModeButton.Hide()
        #Make sure to disconnect the callbacks on the canvas - we do not want them for the results page
        for handle in self.callbackhandles:
            self.canvas.mpl_disconnect(handle)

        self.callbackhandles=[]
        self.info.Hide()



    #Handles when the results button is clicked
    def results(self,e):
        #If the timer is running we're displaying the wave animation. We want to stop this and load the waveheight results
        if self.timer.IsRunning():
            self.timer.Stop()

            #get the waveheights results
            self.dto= self.get_dto(self.nfiles.value-1)



            #Get the raw data from the simlation and the reference (no wave defences) data from file
            data=self.dto.GetData().GetData()
            reference=self.ReadCoastArray("reference.dat")

            #Smooth the waveheight data so it is less jaggedy
            data2=smooth(data,10)
            reference2=smooth(reference,10)

            #Set up the figure. In particular we want to have different weightings between the two things we wish to display
            self.figure.clf()
            spec = gridspec.GridSpec(ncols=1,nrows=3,figure=self.figure)

            #create axes for the top half
            ax1=self.figure.add_subplot(spec[0:2,:])

            #Plot the waveheight data
            ax1.plot(data2,label="With Defences",color="green")
            ax1.plot(reference2,label="No Defences",color="red")
            ax1.get_xaxis().set_visible(False)
            ax1.legend()
            ax1.set_ylabel("Wave Height (m)")
            ax1.axes.set_ylim(bottom=0)


            #Create axes for the bottom half
            ax2=self.figure.add_subplot(spec[2,:],sharex=ax1)

            #Read in the coastline image and display it
            img=plt.imread("coastline_short.png")
            ax2.imshow(img,extent=(0,479,119,0),aspect="auto")
            ax2.axis("off")


            #Clear the logger in preparation to write results info
            self.logger.Clear()
            #Write results info to the logger
            self.costings(data2,reference2)


            self.canvas.draw()

            self.ResultsButton.SetLabel('Replay')

        #We are already on the waveheight results screen. We want to replay the animation of the waves
        else:
            self.ResultsButton.SetLabel("Results")
            self.logger.Clear()
            self.logger.AppendText("Simulation complete.\n\nClick 'Results' below to view wave heights")
            self.fno=0
            self.timer.Start()





    #Displays waveheight data and repair costs to the logger, and writes results to the logfile
    def costings(self,height,reference):
        #x range of each location
        beach=[75,125]
        houses=[200,250]
        library=[335,385]
        supermarket=[410,460]

        cost=0.

        if self.logIncomplete: self.logfile.write("  <results>\n")


        #Beach results

        #mean height of waves at beach
        ht = np.mean(height[beach[0]:beach[1]])
        #mean reference wave height
        rh = np.mean(reference[beach[0]:beach[1]])
        #fractional difference of waveheights between 1m and the reference height
        frac = 1-(rh-ht)/(rh-1)
        if frac <0: frac=0
        #The cost for repairing the beach
        bcost = int(BeachCost*frac)

        self.logger.AppendText("Beach Furniture:\n")
        self.logger.AppendText("Wave height = %1.2fm\n"%(ht))
        self.logger.AppendText("Repair cost = £%d,000\n"%(bcost))
        self.logger.AppendText("Saving of £%d,000\n"%(BeachCost-bcost))
        self.logger.AppendText("\n")

        if self.logIncomplete:
            self.logfile.write('    <location place="Beach">\n')
            self.logfile.write('      <waveheight> %1.2f </waveheight>\n'%ht)
            self.logfile.write('      <cost> %d </cost>\n'%bcost)
            self.logfile.write('    </location>\n')



        #House results

        ht = np.mean(height[houses[0]:houses[1]])
        rh = np.mean(reference[houses[0]:houses[1]])
        frac = 1-(rh-ht)/(rh-1)
        if frac <0: frac=0
        hcost = int(HouseCost*frac)

        self.logger.AppendText("Houses:\n")
        self.logger.AppendText("Wave height = %1.2fm\n"%(ht))
        self.logger.AppendText("Repair cost = £%d,000\n"%(hcost))
        self.logger.AppendText("Saving of £%d,000\n"%(HouseCost-hcost))
        self.logger.AppendText("\n")

        if self.logIncomplete:
            self.logfile.write('    <location place="Houses">\n')
            self.logfile.write('      <waveheight> %1.2f </waveheight>\n'%ht)
            self.logfile.write('      <cost> %d </cost>\n'%hcost)
            self.logfile.write('    </location>\n')


        #Library results
        ht = np.mean(height[library[0]:library[1]])
        rh = np.mean(reference[library[0]:library[1]])
        frac = 1-(rh-ht)/(rh-1)
        if frac <0: frac=0
        lcost = int(LibraryCost*frac)

        self.logger.AppendText("Library:\n")
        self.logger.AppendText("Wave height = %1.2fm\n"%(ht))
        self.logger.AppendText("Repair cost = £%d,000\n"%(lcost))
        self.logger.AppendText("Saving of £%d,000\n"%(LibraryCost-lcost))
        self.logger.AppendText("\n")

        if self.logIncomplete:
            self.logfile.write('    <location place="Library">\n')
            self.logfile.write('      <waveheight> %1.2f </waveheight>\n'%ht)
            self.logfile.write('      <cost> %d </cost>\n'%lcost)
            self.logfile.write('    </location>\n')


        #Supermarket results
        ht = np.mean(height[supermarket[0]:supermarket[1]])
        rh= np.mean(reference[supermarket[0]:supermarket[1]])
        frac = 1-(rh-ht)/(rh-1)
        if frac <0: frac=0
        scost = int(ShopCost*frac)

        self.logger.AppendText("Supermarket:\n")
        self.logger.AppendText("Wave height = %1.2fm\n"%(ht))
        self.logger.AppendText("Repair cost = £%d,000\n"%(scost))
        self.logger.AppendText("Saving of £%d,000\n"%(ShopCost-scost))
        self.logger.AppendText("\n")

        if self.logIncomplete:
            self.logfile.write('    <location place="Supermarket">\n')
            self.logfile.write('      <waveheight> %1.2f </waveheight>\n'%ht)
            self.logfile.write('      <cost> %d </cost>\n'%scost)
            self.logfile.write('    </location>\n')


        #Calculate total cost and display general statistics
        cost=bcost+hcost+lcost+scost

        self.logger.AppendText("---------------\n\n")
        self.logger.AppendText("Total repair cost = £%3d,000\n"%(cost))
        self.logger.AppendText("Total saving = £%3d,000\n"%(OriginalCost-cost))
        self.logger.AppendText("\n")
        self.logger.AppendText("Cost of defences = £%d,000\n"%(Budget-self.budget))
        self.logger.AppendText("\n")
        self.logger.AppendText('Savings after 5 storms: £%3d,000\n'%(-Budget+self.budget + 5*(OriginalCost-cost)))


        if self.logIncomplete:
            self.logfile.write('    <TotalCost> %d </TotalCost>\n'%cost)
            self.logfile.write('    <saving> %d </saving>\n'%(OriginalCost-cost))
            self.logfile.write('    <FiveyearSaving> %d </FiveyearSaving>\n'%(-Budget+self.budget + 5*(OriginalCost-cost)))

            self.logfile.write("  </results>\n")

        self.logIncomplete=False



    # Display text in the logger that describes money spent on existing defences
    def spreadsheet(self):
        self.logger.Clear()
        self.logger.SetDefaultStyle(wx.TextAttr(wx.BLACK))
        self.budget = Budget
        basecost=20
        self.logger.AppendText("Total budget = £%3d,000\n"%self.budget)
        self.logger.AppendText("\n")
        i=1
        for block in self.blocks:
            block.label.set_text("%d"%i)
            depthcost=int(block.depthm*10*2)+basecost
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



    #Get data from the server in the form of a data transfer object
    def get_dto(self,number):
        #Tell the process which frame number we want and tell it to get the data
        self.frameno.value=number
        print("Frame number= %d"%number)
        self.getdata.value=True
        #receive the data
        dto=self.pipemain.recv()
        #tell it to no longer send us data and send a read receipt
        self.getdata.value=False
        self.pipemain.send(0)
        return dto


    #Reads an array from a simulation file and returns the array
    def ReadCoastArray(self,fname):
        f=open(fname,"rb")
        print("---------------------------")
        print("Opening '%s'"%fname)
        text=np.fromfile(f,np.byte,20)
        text=text.tostring().decode()
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



    #Reset the setup screen: delete all blocks
    def reset(self,e):
        for block in self.blocks:
            block.disconnect()
        self.blocks=[]
        self.canvas.draw()
        self.nblock=0
        self.logger.Clear()
        self.delete=False
        self.DeleteModeButton.Disable()
        #update the costing information on the logger
        self.spreadsheet()


    #Enable/disable delete mode
    def DeleteMode(self,e):
        #We are already in delete mode. Switch it off
        if self.delete:
            self.infobar.ShowMessage("Click on the sea to add defences. Click and drag on existing defences to move them.")
            self.SimButton.Enable()
            self.ResetButton.Enable()
            self.delete=False
            self.DeleteModeButton.SetLabel("Enter Delete Mode")
            i=1
            #Colour blocks grey again
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
            #Colour blocks red
            for block in self.blocks:
                block.rect.set_color("Red")
                #block.label.set_text("-")
            self.canvas.draw()



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
            self.info.AppendText("Depth = %3.0fm, Cost = £%2d,000"%(100.*d,20+int(10*d*2)))
        else:
            self.info.AppendText("You cannot place a defence here")


    #Callback when an area of the matplotlib window is clicked on
    def onclick(self,e):
        #get coordinates of the click
        x=e.xdata
        y=e.ydata

        #Check the click was done in the plot area. If not, exit
        if (x == None or y == None):
            print("Invalid input")
            return

        i=int(x)
        j=int(y)

        #Determine if we can place a block here
        if not self.can_place(i,j):
            print("Can't place a block here")
            return

        #If we are in delete mode we are done here
        if self.delete: return

        #Check we have enough budget to place a block here
        if self.budget <= 0:
            wx.MessageDialog(self,"You do not have any more money. Please delete or move an existing defence.","Warning",wx.OK).ShowModal()
            return



        imax = min(239,i+5)
        imin = max(0,i-5)

        jmax= min(j+10,239)
        jmin = max(0,j-10)

        #We now want to place a defence
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
            self.DeleteModeButton.Enable()

        #update the costing information on the logger
        self.spreadsheet()


    # Determine if a defence can be placed here
    def can_place(self,x,y):
        i=0
        print(x,y)
        # Is the defence gonna be placed outwith the box?
        if x<5 or x>=470 or y<10 or y>=230: return False
        # Is the water too shallow?
        if self.depth[y][x] < 0.05: return False

        #Check if a block is already here
        for block in self.blocks:
            xp,yp = block.get_position()
            if (np.abs(x-xp) < 10 and np.abs(y-yp) < 5):
                print(i)
                #If we're on delete mode, delete the block
                if self.delete:
                    block.disconnect()
                    self.blocks.pop(i)
                    self.canvas.draw()
                    self.canvas.Refresh()
                    self.nblock-=1
                return False
            i+=1

        #Yes can place a block here
        return True











#Class for a block that can be moved about on the screen
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

    #Get x and y coordinates of centre of block
    def getxy(self):
        self.x, self.y=self.rect.xy
        self.x+=10
        self.y+=5

    #connect all callbacks
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
        #we don't want the block moving onto shalow water
        if self.depth[int(event.ydata)][int(event.xdata)] < 0.05:
            return

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


#Smooths an array by Gaussian smoothing with an e-folding width of w
def smooth(data,w):
    nx = len(data)

    smoothed = np.zeros(nx)
    dd=np.concatenate([data,data,data])

    for i in range(nx,2*nx):
        wgt=0.
        for j in range(i-nx/4,i+nx/4):
            smoothed[i-nx] += dd[j] * np.exp(-(i-j)*(i-j)/w/w)
            wgt+=np.exp(-(i-j)*(i-j)/w/w)
        smoothed[i-nx] /=wgt

    return smoothed

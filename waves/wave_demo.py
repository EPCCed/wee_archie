from __future__ import print_function
import client
import wx

import numpy as np







#Data transfer object
class DTO(client.AbstractDTO):
    def SetData(self,data):
        self.Data=data

    def GetData(self):
        return self.Data



class SimResults:
    def __init__(self,file):
        self.file=file


        f=open(self.file,"rb")
        print("---------------------------")
        print("DTO Opening '%s'"%self.file)
        text=np.fromfile(f,np.byte,20)
        text=text.tostring()
        print("Filetype is: %s"%text)
        nxy=np.fromfile(f,np.int32,2)
        #print(nxy)
        print("nx=%d, ny=%d"%(nxy[0],nxy[1]))
        t=np.fromfile(f,np.float64,1)
        print("Time is %2.2f"%t)
        print("---------------------------")

        atype = "%-20s"%"A"
        whtype= "%-20s"%"waveheights"

        if text == atype:
            data=np.fromfile(f,np.float64,nxy[0]*nxy[1])
            data=data.reshape((nxy[0],nxy[1]),order="F")
        elif text == whtype:
            data=np.fromfile(f,np.float64,nxy[1])
        else:
            print('Error wrong type "%s"'%text)

        f.close()

        self.type=text
        self.t=t[0]
        self.nx=nxy[0]
        self.ny=nxy[1]
        self.data=data

    def GetType(self):
        return self.type

    def GetFile(self):
        return self.file

    def GetNx(self):
        return self.nx

    def GetNy(self):
        return self.ny

    def GetT(self):
        return self.t

    def GetData(self):
        return self.data



#class containing demo-specific functions
class WaveDemo(client.AbstractDemo):

    # read in data and convert it to a data transfer object
    def GetVTKData(self,root):

        #INSERT CODE TO READIN DATA FROM ROOT AND PREPARE IT FOR TRANSFER TO GUI

        #potential=SimResults("potential.dat")

        #viscous=SimResults("output.dat")

        data=SimResults('tmp.nc')

        dto=DTO()

        #data={ "potential" : potential , "viscous" : viscous }

        dto.SetData(data)

        #INSERT CODE TO PUT DATA INTO DTO

        return dto


    # Renders a frame with data contained within the data transfer object, data
    def RenderFrame(self,win,dto,simtype,vartype):

        #INSERT CODE TO UNPACK DTO AND RENDER THE DATA IT CONTAINS
        #'win' IS THE GUI CLASS WHICH THE VTK RENDERER BELONGS TO

        win.figure.clf()
        win.plt=win.figure.add_subplot(111)

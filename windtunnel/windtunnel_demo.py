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
        print("Reading results from: ",self.file)

        f = open(file, "rb")

        nx=np.fromfile(f,count=1,dtype=np.int32)[0]
        ny=np.fromfile(f,count=1,dtype=np.int32)[0]

        self.nx=nx
        self.ny=ny

        self.x=np.fromfile(f,count=nx,dtype=np.float32)
        self.y=np.fromfile(f,count=ny,dtype=np.float32)
        self.psi=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
        mask=np.fromfile(f,count=nx*ny,dtype=np.int32).reshape((nx,ny))
        self.vx=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
        self.vy=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
        self.v=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
        self.p=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))
        self.vort=np.fromfile(f,count=nx*ny,dtype=np.float32).reshape((nx,ny))

        self.plift=np.fromfile(f,count=1,dtype=np.float32)
        self.rlift=np.fromfile(f,count=1,dtype=np.float32)
        self.pdrag=np.fromfile(f,count=1,dtype=np.float32)
        self.rdrag=np.fromfile(f,count=1,dtype=np.float32)
        self.lift=np.fromfile(f,count=1,dtype=np.float32)
        self.drag=np.fromfile(f,count=1,dtype=np.float32)

        self.C_l=np.fromfile(f,count=1,dtype=np.float32)
        self.C_d=np.fromfile(f,count=1,dtype=np.float32)
        self.C_la=np.fromfile(f,count=1,dtype=np.float32)
        self.C_da=np.fromfile(f,count=1,dtype=np.float32)

        self.C_l = self.C_l[0]
        self.C_d = self.C_d[0]

        self.C_la = self.C_la[0]
        self.C_da = self.C_da[0]

        f.close()

        print("Lift coefficient=",self.C_l)
        print("Drag Coefficient=",self.C_d)


    def GetFile(self):
        return self.file

    def GetGrid(self):
        return (self.nx,self.ny,self.x,self.y)

    def GetVels(self):
        return (self.vx,self.vy,self.v)

    def GetP(self):
        return self.p

    def GetPsi(self):
        return self.psi

    def GetVort(self):
        return self.vort

    def GetForces(self):
        return(self.plift,self.rlift,self.lift,self.pdrag,self.rdrag,self.drag)

    def GetCoefficients(self):
        print("Lift coefficient=",self.C_l)
        print("Drag Coefficient=",self.C_d)
        return (self.C_la, self.C_da)



#class containing demo-specific functions
class WindTunnelDemo(client.AbstractDemo):

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

        # try:
        #     win.plt.cla()
        # except:
        #     win.plt = win.figure.add_subplot(111)

        #get data
        if simtype ==0:
            #data=dto.GetData()["potential"]
            data=win.potential
        else:
            #data=dto.GetData()["viscous"]
            data=win.viscous

        (nx,ny,x,y)=data.GetGrid()

        (dum,dum,lift,dum,dum,drag)=data.GetForces()
        ld=np.sqrt(lift*lift+drag*drag)

        lft=lift/ld
        drg=drag/ld

        lft=lft[0]
        drg=drg[0]

        #print("lift,drag=",lft,drg,lift,drag,5.)


        if vartype == 0: #flowlines
            (u,v,u2)=data.GetVels()
            colour=u2
            im=win.plt.imshow(u2,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
            stream=win.plt.streamplot(x,y,u,v,density=1.25,arrowstyle='->',color='black')
            win.figure.colorbar(im).set_label("Velocity (kmph)")
            win.plt.axis('equal')
            win.plt.set_title("Flowlines")
            win.plt.set_xlim(x[0],x[-1])
            win.plt.set_ylim(y[0],y[-1])
            win.plt.arrow(0.,0.,drg,lft,shape="full",lw=3,head_width=0.1)


        elif vartype == 1:
            p=data.GetP()
            im=win.plt.imshow(p,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
            win.figure.colorbar(im)
            win.plt.axis('equal')
            win.plt.set_title("Pressure")
            win.plt.arrow(0.,0.,drg,lft,shape="full",lw=3,head_width=0.1)

        elif vartype == 2:
            vort=data.GetVort()
            im=win.plt.imshow(vort,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
            win.figure.colorbar(im)
            win.plt.axis('equal')
            win.plt.set_title("Vorticity")
            win.plt.arrow(0.,0.,drg,lft,shape="full",lw=3,head_width=0.1)


        elif vartype == 3:
            (u,v,u2)=data.GetVels()
            im=win.plt.imshow(u2,origin='lower',extent=(x[0],x[-1],y[0],y[-1]))
            win.figure.colorbar(im).set_label("kmph")
            win.plt.axis('equal')
            win.plt.set_title("Velocity")
            win.plt.arrow(0.,0.,drg,lft,shape="full",lw=3,head_width=0.1)

        else:
            print("Whoops, invalid option")



        lift=lift/1000
        drag = drag/1000.

        red=wx.Colour(255,0,0)
        green = wx.Colour(0,255,0)
        amber = wx.Colour(255,191,0)
        white=wx.Colour(255,255,255)
        black = wx.Colour(0,0,0)

        win.logger.SetDefaultStyle(wx.TextAttr(black,white))
        win.logger.Clear()
        if lift > 1:
            win.logger.SetDefaultStyle(wx.TextAttr(black,green))
        elif lift > 0.2:
            win.logger.SetDefaultStyle(wx.TextAttr(black,amber))
        else:
            win.logger.SetDefaultStyle(wx.TextAttr(black,red))

        win.logger.AppendText("Lift= %6.1f kN \n"%(lift))

        if drag < 0.2:
            win.logger.SetDefaultStyle(wx.TextAttr(black,green))
        elif drag < 1.:
            win.logger.SetDefaultStyle(wx.TextAttr(black,amber))
        else:
            win.logger.SetDefaultStyle(wx.TextAttr(black,red))

        win.logger.AppendText("Drag= %6.1f kN \n"%(drag))

        if lift/drag > 10:
            win.logger.SetDefaultStyle(wx.TextAttr(black,green))
        elif lift/drag > 2.:
            win.logger.SetDefaultStyle(wx.TextAttr(black,amber))
        else:
            win.logger.SetDefaultStyle(wx.TextAttr(black,red))

        win.logger.AppendText("lift/drag= %6.3f"%(lift/drag))

        #data.GetCoefficients()

        #win.logger.AppendText("Lift= %6.1f kN \nDrag= %6.1f kN \nLift/Drag= %6.3f"%(lift/1000,drag/1000,lift/drag))
        #win.logger.Refresh()

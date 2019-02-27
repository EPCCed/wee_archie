# -*- coding: utf-8 -*-
from __future__ import print_function

import wx
import numpy as np



def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result



scale = 0.35 #scale metres to pixels



lift=0.0
drag=0.0


bgc1=wx.Colour(53,53,53)
bgc2=wx.Colour(35,35,35)

class Info(wx.Frame):
    def __init__(self, parent,title,size):
        super(Info, self).__init__(parent, title=title,size=size,style=wx.FRAME_FLOAT_ON_PARENT|wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)

        self.parent=parent


        #load background image
        bg = wx.Image("coastline_costs.png",wx.BITMAP_TYPE_PNG)
        bg.Rescale(1000,500)
        background = wx.StaticBitmap(self, -1, wx.BitmapFromImage(bg))
        #background.SetPosition((0, 0))

        sizer=wx.BoxSizer(wx.VERTICAL)

        text = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE|wx.TE_RICH2,size=(-1,-1))

        button = wx.Button(self,wx.ID_ANY,label="Got it!")
        self.Bind(wx.EVT_BUTTON,self.OnClose,button)

        text.AppendText("\nBeachville is a seaside town that has recently been experiencing frequent severe storms due to climate change. Each storm does £200,000 worth of damage to the town. The Mayor has decided that wave defences should be built in order to protect the town from the waves, however these are very expensive. They decide to ask ARCHER for help to determine the best places to build the defences to protect the town and minimise costs.\n\n")
        text.AppendText("Now it's your turn! Click on areas of the sea to place defences. The cost of each defence depends on the depth of the water at its location. Beware, you only have a fixed budget!\n\n")
        text.AppendText("Once you are happy with your placement, you can run a simulation to determine the effects of the defences on the waves. Can you save Beachville? Can you find a cost-efficient way to do so?")

        sizer.Add(text,1,wx.EXPAND)
        sizer.Add(button,0,wx.EXPAND)
        sizer.Add(background,1)

        self.parent.Disable()
        self.SetSizer(sizer)

        self.Bind(wx.EVT_CLOSE,self.OnClose)











    def OnClose(self,e):
        print("Exiting")
        try:
            self.parent.Enable()
        except:
            print("Parent cannot be Enabled. It is already enabled")

        self.Destroy()





if __name__ == '__main__':
    app = wx.App()
    info=Info(None,"Info",(1000,750))
    info.Show()
    app.MainLoop()

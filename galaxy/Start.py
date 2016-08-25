#!/usr/bin/env pythonw
import sys
sys.path.append('../framework/')

import galaxy_demo
import galaxy_ui
import client
import wx

demo=galaxy_demo.GalaxyDemo()
servercomm=client.servercomm("GALAXY")

app=wx.App(False)
window=galaxy_ui.GalaxyWindow(None,"Galaxy Simulator",demo,servercomm)
app.MainLoop()







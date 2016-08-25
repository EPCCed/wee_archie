#!/usr/bin/env pythonw
import sys
sys.path.append('../framework/')

import generic_demo
import generic_ui
import client
import wx

demo=generic_demo.GenericDemo()
servercomm=client.servercomm("GENERIC")

app=wx.App(False)
window=generic_ui.GenericWindow(None,"Generic Simulator",demo,servercomm)
app.MainLoop()

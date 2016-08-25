#!/usr/bin/env pythonw
import sys
sys.path.append('../framework/')

import windtunnel_demo
import windtunnel_ui
import client
import wx

demo=windtunnel_demo.WindTunnelDemo()
servercomm=client.servercomm("CDFD")

app=wx.App(False)
window=windtunnel_ui.WindTunnelWindow(None,"Windtunnel Simulator",demo,servercomm)
app.MainLoop()

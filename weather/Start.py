#!/usr/bin/env python3
import sys
sys.path.append('../framework/')

import weather_demo
import weather_ui
import client
import wx

demo=weather_demo.WeatherDemo()
servercomm=client.servercomm("WEATHER")

app=wx.App(False)
window=weather_ui.WeatherWindow(None,"Weather Simulator",demo,servercomm)
window.Maximize(True)
app.MainLoop()







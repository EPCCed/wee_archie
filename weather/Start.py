#!/usr/bin/env python3
import sys
sys.path.append('../framework/')

import weather_demo
import weather_ui
import client
import wx
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--server",type=str,default="http://0.0.0.0:5000/", help="Server to be used; default='http://0.0.0.0:5000/'")
parser.add_argument("-n","--name",type=str,default="SHPCW",help="Simulation name; default='SHPCW'")
parser.add_argument("-c","--cores", type=int, default=0, help="number of cores per CPU, default: 1")

args=parser.parse_args()

demo=weather_demo.WeatherDemo()
servercomm=client.servercomm(args.name,args.server)

app = wx.App(False)

window = weather_ui.WeatherWindow(None, "Weather Simulator", demo, servercomm)
window.Maximize(True)

app.MainLoop()

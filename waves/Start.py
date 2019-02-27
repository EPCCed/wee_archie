#!/usr/bin/env pythonw
import sys
sys.path.append('../framework/')

import wave_demo
import wave_ui
from client import servercomm
import wx
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--server",type=str,default="http://0.0.0.0:5000/", help="Server to be used; default='http://0.0.0.0:5000/'")
parser.add_argument("-n","--name",type=str,default="WAVE",help="Simulation name; default='wave'")
parser.add_argument("-c","--cores", type=int, default=0, help="number of cores per CPU, default: 1")

args=parser.parse_args()

demo=wave_demo.WaveDemo()
Servercomm=servercomm(args.name,args.server) #on Wee Archie 1
#servercomm=client.servercomm("WDS") #on wee archie 2

app=wx.App(False)
window=wave_ui.WaveWindow(None,"Wave Simulator",demo,Servercomm,args)
app.MainLoop()

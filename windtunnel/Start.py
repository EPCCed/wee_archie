#!/usr/bin/env pythonw
import sys
sys.path.append('../framework/')

import windtunnel_demo
import windtunnel_ui
import client
import wx
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s","--server",type=str,default="http://0.0.0.0:5000/", help="Server to be used; default='http://0.0.0.0:5000/'")
parser.add_argument("-n","--name",type=str,default="CDFD",help="Simulation name; default='CDFD'")
parser.add_argument("-c","--cores", type=int, default=0, help="number of cores per CPU, default: 1")

args=parser.parse_args()

demo=windtunnel_demo.WindTunnelDemo()
servercomm=client.servercomm(args.name,args.server) #on Wee Archie 1
#servercomm=client.servercomm("WDS") #on wee archie 2

app=wx.App(False)
window=windtunnel_ui.WindTunnelWindow(None,"Windtunnel Simulator",demo,servercomm,args)
app.MainLoop()

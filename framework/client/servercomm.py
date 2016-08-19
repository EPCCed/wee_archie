import requests
import shutil
import json


#class which describes the ways that the program can interact with the server.
class servercomm:
    #input is the name of the simulation (as known to the server)
    def __init__(self,simname):
        self.targetbase='http://192.168.2.14:5000/'
        self.simname=simname
        print("Server initialised for simulation '"+self.simname+"'.")
        self.started=False

    #tell server to start the simulation. Pass in the configuration file
    def StartSim(self,configfile):
        if not self.started:
            files= {'fileToUpload': open(configfile,'rb')}
            print(self.targetbase+'simulation/'+self.simname)
            postrequest = requests.post(self.targetbase+'simulation/'+self.simname, files=files)
            self.simid=postrequest.text
            self.base= self.targetbase +'simulation/'+ self.simname +'/'+ self.simid
            self.data_base=self.base+'/data/'
            self.started=True
            print("Simulation Started. ID="+self.simid)
        else:
            print("Error, simulation has already started")
            print("Simulation ID="+self.simid)

    #get the status of the simulation. Returns a dictionary containing 'status' (running,finished etc) and 'files' (list of results files)
    def GetStatus(self):
        if self.started:
            statusrequest = requests.get(self.base,stream=True)
            self.status=json.loads(statusrequest.text)
            return self.status
        else:
            print("Error: No simulation is running")

    #Downloads the file 'file_to_get' from the server and saves it to the temp file 'name_of_tmp_file'
    def GetDataFile(self,file_to_get,name_of_tmp_file):
        if self.started:
            filerequest=requests.get(self.data_base + file_to_get,stream=True)
            with open(name_of_tmp_file,'wb') as f:
                for chunk in filerequest.iter_content(1024):
                    f.write(chunk)
        else:
            print("Error: No simulation is running")

    # delete the file 'file' from the server
    def DeleteFile(self,file):
        if self.started:
            deletefilerequest=requests.delete(self.data_base+file)
            print("Deleted file: '"+file+"'")
        else:
            print("Error: No simulation is running")

    #delete all the simulation's output files from the server
    def DeleteSim(self):
        if self.started:
            deletefilerequest=requests.delete(self.base)
            print("Deleted Simulation")
            self.started=False
        else:
            print("Error: No simulation to be deleted")

    #returns whether the server class object has started a simulation
    def IsStarted(self):
        return self.started

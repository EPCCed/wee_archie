import time
from netCDF4 import Dataset

#process that periodically checks the server for the simulation status, and downloads new data files and sends them to the GUI process if requested.
def process(frameno,nfiles,getdata,newdata,pipe,demo,servercomm,finished,refresh,simfinished):
    # frameno=shared variable containing current frame number
    # nfiles=shared variable containing number of files on server
    # getdata=flag to tell process whether to download new data from server
    # newdata = flag to tell GUI if process has downloaded a data file and is ready to send it
    # pipe = communication object
    # demo = object contaning demo-specific functions
    # servercomm = Servercomm object
    # refresh = How frequently process should poll server
    # simfinished = is the simulation finished

    print("Process initiated")

    while finished.value == False: #infinite loop

        # get status and set nfiles
        status=servercomm.GetStatus()
        #print(status)
        datafiles=status['files']
        nfiles.value=len(datafiles)
        if status["status"]=="RUNNING":
            simfinished.value=False
            print("SIM RUNNING")
        elif status["status"]=="COMPLETE":
            simfinished.value=True
            print("SIM FINISHED")
        else:
            print("Wrong status")

        #print(datafiles)

        if getdata.value == True: #if GUI has requested a new file
            n=frameno.value
            print("We want file number",n)

            try:
                fname=datafiles[n] #get name of file to download
                print("Getting file ",fname)
                servercomm.GetDataFile(fname,'tmp.nc') #get the data file
            except:
                #print("no file to get")
                time.sleep(refresh)
                continue

            try:
                root=Dataset('tmp.nc','r') #get the netcdf handle for the data file
            except:
                root=None
                #print("No root object")

            dto=demo.GetVTKData(root) #read it into a Data Transfer Object

            newdata.value=True #set flag to tell GUI there is new data available
            pipe.send(dto) #send the data across
            ok=pipe.recv() #get a read receipt
            newdata.value=False #say we no longer have new data (since its been sent and received)
            time.sleep(refresh)


        else:
            time.sleep(refresh)

    print("Process finished")

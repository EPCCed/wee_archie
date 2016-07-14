import time
from netCDF4 import Dataset

#process that periodically checks the server for the simulation status, and downloads new data files and sends them to the GUI process if requested.
def process(frameno,nfiles,getdata,newdata,pipe,demo,servercomm):
    # frameno=shared variable containing current frame number
    # nfiles=shared variable containing number of files on server
    # getdata=flag to tell process whether to download new data from server
    # newdata = flag to tell GUI if process has downloaded a data file and is ready to send it
    # pipe = communication object
    # demo = object contaning demo-specific functions
    # servercomm = Servercomm object

    print "Process initiated"

    while True: #infinite loop

        # get status and set nfiles
        status=servercomm.GetStatus()
        datafiles=status['files']
        nfiles.value=len(datafiles)

        if getdata.value == True: #if GUI has requested a new file
            n=frameno.value

            try:
                fname=datafiles[n] #get name of file to download
                servercomm.GetDataFile(fname,'tmp.nc') #get the data file

                root=Dataset('tmp.nc','r') #get the netcdf handle for the data file

                data=demo.GetVTKData(root) #read it into a Data Transfer Object

                newdata.value=True #set flag to tell GUI there is new data available
                pipe.send(data) #send the data across
                ok=pipe.recv() #get a read receipt
                newdata.value=False #say we no longer have new data (since its been sent and received)

            except: #no new data ready...
                time.sleep(0.1)

        else:
            time.sleep(0.1)



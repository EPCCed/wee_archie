import requests
import shutil
import time

targetbase = 'http://127.0.0.1:5000/'
getrequest = requests.get(targetbase,stream=True)
with open('test.txt','wb') as f:
    shutil.copyfileobj(getrequest.raw,f)
print getrequest
print getrequest.text

files = {'fileToUpload': open('config.txt','rb')}
postrequest = requests.post(targetbase+'simulation/ENV', files=files)
print postrequest
print postrequest.text

time.sleep(2)
statusrequest = requests.get(targetbase+'simulation/ENV/'+postrequest.text,stream=True)
print statusrequest
print statusrequest.text
time.sleep(10)
statusrequest = requests.get(targetbase+'simulation/ENV/'+postrequest.text,stream=True)
print statusrequest
print statusrequest.text

filerequest = requests.get(targetbase+'simulation/ENV/'+postrequest.text+'/data/temp.txt',stream=True)
print filerequest
print filerequest.text
with open('resp.txt','wb') as f:
    for chunk in filerequest.iter_content(1024):
        f.write(chunk)

deletefilerequest = requests.delete(targetbase+'simulation/ENV/'+postrequest.text+'/data/temp.txt')
print deletefilerequest
print deletefilerequest.text

deleterequest = requests.delete(targetbase+'simulation/ENV/'+postrequest.text)
print deleterequest

import os
import shutil

def create_results_directory(path, instanceid):
    instancedirectory = os.path.join(path, instanceid)
    os.makedirs(instancedirectory)
    return instancedirectory

def get_results_directory(path, instanceid):
    return os.path.join(path, instanceid)

def check_results_exist(path, instanceid, fileid):
    return os.path.isfile(os.path.join(get_results_directory(path, instanceid), fileid))

def save_file(candidate_file, path, name):
    candidate_file.save(os.path.join(path, name))
    return os.path.join(path, name)

def list_results_files(path, instanceid, omittedfiles):
    files = sorted(os.listdir(os.path.join(path, instanceid)),
                   key=lambda fn: os.path.getctime(os.path.join(path, instanceid, fn)))
    for filename in omittedfiles:
        files.remove(filename)
    return files

def delete_results_directory(path, instanceid):
    if os.path.exists(os.path.join(path, instanceid)):
        shutil.rmtree(os.path.join(path, instanceid))

def delete_results_file(path, instanceid, resultsfile):
    if os.path.isfile(os.path.join(os.path.join(path, instanceid, resultsfile))):
        os.remove(os.path.isfile(os.path.join(os.path.join(path, instanceid, resultsfile))))

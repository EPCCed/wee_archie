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
    candidate_target_path = os.path.join(path, name)
    candidate_file.save(candidate_target_path)
    return candidate_target_path

def list_results_files(path, instanceid, omittedfiles):
    files = sorted(os.listdir(os.path.join(path, instanceid)),
                   key=lambda fn: os.path.getctime(os.path.join(path, instanceid, fn)))
    for filename in omittedfiles:
        files.remove(filename)
    return files

def delete_results_directory(path, instanceid):
    results_directory = os.path.join(path, instanceid)
    if os.path.exists(results_directory):
        shutil.rmtree(results_directory)

def delete_results_file(path, instanceid, resultsfile):
    target = os.path.join(path, instanceid, 'data', resultsfile)
    if os.path.isfile(target):
        os.remove(target)

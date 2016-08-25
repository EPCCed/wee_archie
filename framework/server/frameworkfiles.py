""" Collection of Methods to deal with results access

    Allows:
    results directory creation/deletion
    saving/removing a file to the directory
    listing of files in a directory
"""
import os
import shutil

def create_results_directory(path, instanceid):
    """
    Create a directory for the results for the instanceid
    :param path:
    :param instanceid:
    :return:
    """
    instancedirectory = os.path.join(path, instanceid)
    os.makedirs(instancedirectory)
    return instancedirectory

def get_results_directory(path, instanceid):
    """
    Get the path for the results directory for instanceid
    :param path:
    :param instanceid:
    :return:
    """
    return os.path.join(path, instanceid)

def check_results_exist(path, instanceid, fileid):
    """
    Check a results file exists
    :param path:
    :param instanceid:
    :param fileid:
    :return:
    """
    return os.path.isfile(os.path.join(get_results_directory(path, instanceid), fileid))

def save_file(candidate_file, path, name):
    """
    Save a file to a name in the given path
    :param candidate_file:
    :param path:
    :param name:
    :return:
    """
    candidate_target_path = os.path.join(path, name)
    candidate_file.save(candidate_target_path)
    return candidate_target_path

def list_results_files(path, instanceid, omittedfiles):
    """
    lists the files associated with an instanceid leavuing out the omittedfiles and in ascending age.
    :param path:
    :param instanceid:
    :param omittedfiles:
    :return:
    """
    files = sorted(os.listdir(os.path.join(path, instanceid)),
                   key=lambda fn: os.path.getctime(os.path.join(path, instanceid, fn)))
    for filename in omittedfiles:
        files.remove(filename)
    return files

def delete_results_directory(path, instanceid):
    """
    Deletes all information from and the directory for an instanceid
    :param path:
    :param instanceid:
    :return:
    """
    results_directory = os.path.join(path, instanceid)
    if os.path.exists(results_directory):
        shutil.rmtree(results_directory)

def delete_results_file(path, instanceid, resultsfile):
    """
    Delete a specified results file from the instanceid
    :param path:
    :param instanceid:
    :param resultsfile:
    :return:
    """
    target = os.path.join(path, instanceid, 'data', resultsfile)
    if os.path.isfile(target):
        os.remove(target)

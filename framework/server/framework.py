""" framework.py defines the flask app and methods for dealing
    with different request types in the frame work.
"""
import os
import logging
import uuid
import shutil
import httpcodes
import json
import config as cfg
from simulation_runner import SimulationRunner
from logging.handlers import RotatingFileHandler
from subprocess import Popen, PIPE
from flask import Flask, request, render_template, redirect, g, send_from_directory
import frameworkdb as fdb
import frameworkfiles as ffs
from flask_cors import CORS

# Create exportable app
app = Flask(__name__)
CORS(app)

# Create and attach logger to app
handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=1)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
# Track for threads for running simulations (not fully utilised)
threads = {}

def get_cluster_status():
    """ Holder method - will be removed in next revision
    :return:
    """
    proc = Popen('env', shell=True, stdout=PIPE)
    return proc.communicate()[0]

def get_cluster_history():
    """ Holder method - will be removed in next revision
    :return:
    """
    proc = Popen('env', shell=True, stdout=PIPE)
    return proc.communicate()[0]

@app.route('/', methods=['GET'])
def welcome_page():
    """ Returns a static welcome page on root
    :return:
    """
    return app.send_static_file('index.html'), httpcodes.OK

@app.route('/simulation', methods=['GET', 'POST'])
def display_simulations():
    """
    GET /simulation will return a rendered page with a list of simulations
    POST - not implemented
    :return:
    """
    if request.method == 'GET':
        with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
            data = conn.getSimulations()
        return render_template('simulationlist.html', sims=data), httpcodes.OK
    if request.method == 'POST':
        return 'Op not implemented', httpcodes.NOT_IMPLEMENTED

@app.route('/threads', methods=['GET'])
def get_threads():
    """ Return number of threads - to be revised
    :return:
    """
    return str(len(threads)), httpcodes.OK

@app.route('/simulation/<simid>', methods=['GET', 'POST'])
def display_simulation(simid):
    """ GET - return information about the simulation simid
    POST - start a new instance of simid with a config file and return an ID
    :param simid:
    :return:
    """
    if request.method == 'GET':
        sim = None
        active = None
        with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
            sim = conn.getSimulation(simid)
            actives = conn.getInstancesOf(simid)
        return render_template('simulation_cfg.html', sim=sim, running=actives), httpcodes.OK
    if request.method == 'POST':
        siminstance = str(uuid.uuid4())
        instancedirectory = ffs.create_results_directory(cfg.RESULTS_DIR, siminstance)
        configfile = ffs.save_file(request.files['fileToUpload'], instancedirectory, "config.txt")
        with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
            conn.createInstance(siminstance, str(simid), cfg.STATUS_NAMES['ready'])
        thread_run_simulation = SimulationRunner(kwargs={
            'simid': simid,
            'instanceid': siminstance,
            'pool': threads,
            'config': configfile,
            'output': instancedirectory
        })
        threads[siminstance] = thread_run_simulation
        thread_run_simulation.start()
        return siminstance, httpcodes.CREATED

@app.route('/simulation/<simid>/<instanceid>', methods=['GET', 'POST', 'DELETE'])
@app.route('/simulation/<simid>/<instanceid>/status', methods=['GET'])
def get_instance_status(simid, instanceid):
    """
    GET - return current status object for instanceid
    POST/DELETE - deletes the instance - need to add thread deletion and sim stop
    :param simid:
    :param instanceid:
    :return:
    """
    if request.method == 'GET':
        data = {}
        with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
            data['status'] = conn.getInstanceStatus(simid,instanceid)
        data['files'] = ffs.list_results_files(cfg.RESULTS_DIR, instanceid, cfg.OMITTED_FILES)
        return json.dumps(data), httpcodes.OK
    if request.method in {'POST', 'DELETE'}:
        ffs.delete_results_directory(cfg.RESULTS_DIR, instanceid)
        with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
            conn.deleteInstance(instanceid,simid)
        return redirect('/simulation/'+simid), httpcodes.FOUND

@app.route('/simulation/<simid>/<instanceid>/data', methods=['GET'])
def get_datanames(simid, instanceid):
    """ returns list of files in results in ascending order
    :param simid:
    :param instanceid:
    :return:
    """
    if request.method == 'GET':
        data = {}
        data['files'] = ffs.list_results_files(cfg.RESULTS_DIR, instanceid, cfg.OMITTED_FILES)
        return json.dumps(data), httpcodes.OK

@app.route('/simulation/<simid>/<instanceid>/data/<fileid>', methods=['GET', 'DELETE'])
def get_results(simid, instanceid,fileid):
    """
    GET - return data file if exists
    DELETE - delete data file if exists
    :param simid:
    :param instanceid:
    :param fileid:
    :return:
    """
    if request.method == "GET":
        with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
            active = conn.getInstanceStatus(simid,instanceid)
        if active in {cfg.STATUS_NAMES['ready'], cfg.STATUS_NAMES['error']}:
            return '', httpcodes.NO_CONTENT
        if ffs.check_results_exist(cfg.RESULTS_DIR, instanceid, fileid):
            return send_from_directory(ffs.get_results_directory(cfg.RESULTS_DIR, instanceid), fileid, as_attachment=True), httpcodes.OK
        else:
            return '', httpcodes.NO_CONTENT
    if request.method == "DELETE":
        ffs.delete_results_file(cfg.RESULTS_DIR,instanceid,fileid)
        return '', httpcodes.NO_CONTENT


@app.route('/status', methods=['GET'])
def system_status():
    """ Returns a rendered template with the environment. - to be revised
    :return:
    """
    cluster_status = get_cluster_status()
    return render_template('system_status.html', systemstatus = cluster_status), httpcodes.OK

@app.route('/status/performance', methods=['GET'])
@app.route('/status/history', methods=['GET'])
@app.route('/led', methods=['GET','POST'])
@app.route('/led/current', methods=['GET'])
def hello_world():
    """
    Ops not implemented yet.
    :return:
    """
    ffs.create_results_directory(cfg.BASE_DIR,'obbb')
    return 'Op not implemented', httpcodes.NOT_IMPLEMENTED

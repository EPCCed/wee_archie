import os
import logging
import uuid
import shutil
import httplib
import json
import config as cfg
from runsim import RunSim
from logging.handlers import RotatingFileHandler
from subprocess import Popen, PIPE
from flask import Flask, request, render_template, redirect, g, send_from_directory
import frameworkdb as fdb

app = Flask(__name__)
handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=1)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
threads = {}

def get_cluster_status():
    proc = Popen('env', shell=True, stdout=PIPE)
    return proc.communicate()[0]

def get_cluster_history():
    proc = Popen('env', shell=True, stdout=PIPE)
    return proc.communicate()[0]

@app.route('/', methods=['GET'])
def welcome_page():
    return app.send_static_file('index.html'), httplib.OK

@app.route('/simulation', methods=['GET', 'POST'])
def display_simulations():
    if request.method == 'GET':
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            data = conn.getSimulations()
        return render_template('simulationlist.html', sims=data), httplib.OK
    if request.method == 'POST':
        return 'Op not implemented', httplib.NOT_IMPLEMENTED

@app.route('/threads', methods=['GET'])
def get_threads():
    return str(len(threads)), httplib.OK

@app.route('/simulation/<simid>', methods=['GET', 'POST'])
def display_simulation(simid):
    if request.method == 'GET':
        sim = None
        active = None
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            sim = conn.getSimulation(simid)
            actives = conn.getInstancesOf(simid)
        return render_template('simulation_cfg.html', sim=sim, running=actives), httplib.OK
    if request.method == 'POST':
        siminstance = str(uuid.uuid4())
        instancedirectory = os.path.join(cfg.RESULTS_DIR, siminstance)
        os.makedirs(instancedirectory)
        requestconfiguration = request.files['fileToUpload']
        requestconfiguration.save(os.path.join(instancedirectory, "config.txt"))
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            conn.createInstance(siminstance, str(simid), cfg.STATUS_NAMES['ready'])
        thread_run_simulation = RunSim(kwargs={
            'simid': simid,
            'instanceid': siminstance,
            'pool': threads,
            'config': os.path.join(instancedirectory, "config.txt"),
            'output': instancedirectory
        })
        threads[siminstance] = thread_run_simulation
        thread_run_simulation.start()
        return siminstance, httplib.CREATED

@app.route('/simulation/<simid>/<instanceid>', methods=['GET', 'POST', 'DELETE'])
@app.route('/simulation/<simid>/<instanceid>/status', methods=['GET'])
def get_instance_status(simid, instanceid):
    if request.method == 'GET':
        data = {}
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            data['status'] = conn.getInstanceStatus(simid,instanceid)
        files = sorted(os.listdir(os.path.join(cfg.RESULTS_DIR, instanceid)),
            key=lambda fn: os.path.getctime(os.path.join(cfg.RESULTS_DIR, instanceid, fn)))
        files.remove('config.txt')
        data['files'] = files
        return json.dumps(data), httplib.OK
    if request.method in {'POST', 'DELETE'}:
        if os.path.exists(os.path.join(cfg.RESULTS_DIR, instanceid)):
            shutil.rmtree(os.path.join(cfg.RESULTS_DIR, instanceid))
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            conn.deleteInstance(instanceid,simid)
        return redirect('/simulation/'+simid), httplib.FOUND

@app.route('/simulation/<simid>/<instanceid>/data', methods=['GET'])
def get_datanames(simid, instanceid):
    if request.method == 'GET':
        data = {}
        files = sorted(os.listdir(os.path.join(cfg.RESULTS_DIR, instanceid)),
            key=lambda fn: os.path.getctime(os.path.join(cfg.RESULTS_DIR, instanceid, fn)))
        files.remove('config.txt')
        data['files'] = files
        return json.dumps(data), httplib.OK

@app.route('/simulation/<simid>/<instanceid>/data/<fileid>', methods=['GET', 'DELETE'])
def get_results(simid, instanceid,fileid):
    if request.method == "GET":
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            active = conn.getInstanceStatus(simid,instanceid)
        if active in {cfg.STATUS_NAMES['ready'], cfg.STATUS_NAMES['error']}:
            return '', httplib.NO_CONTENT
        if os.path.isfile(os.path.join(os.path.join(cfg.RESULTS_DIR, instanceid, fileid))):
            return send_from_directory(os.path.join(cfg.RESULTS_DIR, instanceid), fileid, as_attachment=True), httplib.OK
        else:
            return '', httplib.NO_CONTENT
    if request.method == "DELETE":
        if os.path.isfile(os.path.join(os.path.join(cfg.RESULTS_DIR, instanceid, fileid))):
            os.remove(os.path.isfile(os.path.join(os.path.join(cfg.RESULTS_DIR, instanceid, fileid))))
        return '', httplib.NO_CONTENT


@app.route('/status', methods=['GET'])
def system_status():
    cluster_status = get_cluster_status()
    return render_template('system_status.html', systemstatus = cluster_status), httplib.OK

@app.route('/status/performance', methods=['GET'])
@app.route('/status/history', methods=['GET'])
@app.route('/led', methods=['GET','POST'])
@app.route('/led/current', methods=['GET'])
def hello_world():
    return 'Op not implemented', httplib.NOT_IMPLEMENTED


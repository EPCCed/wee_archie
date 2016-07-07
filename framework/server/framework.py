import os
import logging
import sqlite3 as lite
import uuid
import shutil
import httplib
import json
import config as cfg
from runsim import RunSim
from logging.handlers import RotatingFileHandler
from subprocess import Popen, PIPE
from flask import Flask, request, render_template, redirect, g, send_from_directory

app = Flask(__name__)
handler = RotatingFileHandler('error.log', maxBytes=100000, backupCount=1)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
threads = {}

def get_db():
    app_database = getattr(g, '_database', None)
    if app_database is None:
        g._database = lite.connect(cfg.DATABASE_CONNECTION)
        g._database.row_factory = lite.Row
        app_database = g._database
    return app_database

@app.teardown_appcontext
def close_connection(exception):
    app_database = getattr(g, '_database', None)
    if app_database is not None:
        app_database.close()

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
        con = get_db()
        cur = con.cursor()
        cur.execute('SELECT * FROM Simulations')
        data = cur.fetchall()
        return render_template('simulationlist.html', sims=data), httplib.OK
    if request.method == 'POST':
        return 'Op not implemented', httplib.NOT_IMPLEMENTED

@app.route('/threads', methods=['GET'])
def get_threads():
    return str(len(threads)), httplib.OK

@app.route('/simulation/<simid>', methods=['GET', 'POST'])
def display_simulation(simid):
    if request.method == 'GET':
        con = get_db()
        cur = con.cursor()
        cur.execute('SELECT * FROM Simulations WHERE SIMID=?', (simid, ))
        sim = cur.fetchone()
        cur.execute('SELECT * FROM Instances WHERE SIMID=?', (simid, ))
        actives = cur.fetchall()
        return render_template('simulation_cfg.html', sim=sim, running=actives), httplib.OK
    if request.method == 'POST':
        siminstance = str(uuid.uuid4())
        instancedirectory = os.path.join(cfg.BASE_DIR, 'results', siminstance)
        os.makedirs(instancedirectory)
        requestconfiguration = request.files['fileToUpload']
        requestconfiguration.save(os.path.join(instancedirectory, "config.txt"))
        con = get_db()
        cur = con.cursor()
        cur.execute("""INSERT INTO Instances(IID,SIMID,Status) VALUES(?,?,?)""",
                    (siminstance, str(simid), cfg.STATUS_NAMES['ready']))
        con.commit()
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
        con = get_db()
        cur = con.cursor()
        cur.execute('SELECT Status FROM Instances WHERE SIMID=? and IID=?', (simid, instanceid))
        actives = cur.fetchone()
        data = {}
        data['status'] = actives[0]
        files = sorted(os.listdir(os.path.join(cfg.BASE_DIR, 'results', instanceid)),
            key=lambda fn: os.path.getctime(os.path.join(cfg.BASE_DIR, 'results', instanceid, fn)))
        files.remove('config.txt')
        data['files'] = files
        return json.dumps(data), httplib.OK
    if request.method in {'POST', 'DELETE'}:
        # Kill process TODO
        if os.path.exists(os.path.join(cfg.BASE_DIR, 'results', instanceid)):
            shutil.rmtree(os.path.join(cfg.BASE_DIR, 'results', instanceid))
        con = get_db()
        cur = con.cursor()
        cur.execute('DELETE FROM Instances WHERE SIMID=? and IID=?', (simid, instanceid))
        con.commit()
        return redirect('/simulation/'+simid), httplib.OK

@app.route('/simulation/<simid>/<instanceid>/data', methods=['GET'])
def get_datanames(simid, instanceid):
    if request.method == 'GET':
        data = {}
        files = sorted(os.listdir(os.path.join(cfg.BASE_DIR, 'results', instanceid)),
            key=lambda fn: os.path.getctime(os.path.join(cfg.BASE_DIR, 'results', instanceid, fn)))
        files.remove('config.txt')
        data['files'] = files
        return json.dumps(data), httplib.OK

@app.route('/simulation/<simid>/<instanceid>/data/<fileid>', methods=['GET', 'DELETE'])
def get_results(simid, instanceid,fileid):
    if request.method == "GET":
        con = get_db()
        cur = con.cursor()
        cur.execute('SELECT Status FROM Instances WHERE SIMID=? and IID=?', (simid, instanceid))
        actives = cur.fetchone()
        if actives[0] in {cfg.STATUS_NAMES['ready'], cfg.STATUS_NAMES['error']}:
            return '', httplib.NO_CONTENT
        if os.path.isfile(os.path.join(os.path.join(cfg.BASE_DIR, 'results', instanceid, fileid))):
            return send_from_directory(os.path.join(cfg.BASE_DIR, 'results', instanceid), fileid, as_attachment=True), httplib.OK
        else:
            return '', httplib.NO_CONTENT
    if request.method == "DELETE":
        if os.path.isfile(os.path.join(os.path.join(cfg.BASE_DIR, 'results', instanceid, fileid))):
            os.remove(os.path.isfile(os.path.join(os.path.join(cfg.BASE_DIR, 'results', instanceid, fileid))))
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


"""
def get_old_results(simid, instanceid,fileid):
    if request.method == "GET":
        con = get_db()
        cur = con.cursor()
        cur.execute('SELECT Status FROM Instances WHERE SIMID=? and IID=?', (simid, instanceid))
        actives = cur.fetchone()
        if actives[0] in {cfg.STATUS_NAMES['ready'], cfg.STATUS_NAMES['error']}:
            return '', httplib.NO_CONTENT
        files = sorted(os.listdir(os.path.join(cfg.BASE_DIR, 'results', instanceid)),
            key=lambda fn: os.path.getctime(os.path.join(cfg.BASE_DIR, 'results', instanceid, fn)))
        files.remove('config.txt') #config.txt is a system file
        if len(files) > 0:
            return send_from_directory(os.path.join(cfg.BASE_DIR, 'results', instanceid), files[0], as_attachment=True), httplib.OK
        else:
            return '', httplib.NO_CONTENT
    if request.method == "DELETE":
        files = sorted(os.listdir(os.path.join(cfg.BASE_DIR, 'results', instanceid)),
            key=lambda fn: os.path.getctime(os.path.join(cfg.BASE_DIR, 'results', instanceid, fn)))
        files.remove('config.txt') #config.txt is a system file
        if len(files) > 0:
            os.remove(os.path.join(cfg.BASE_DIR,'results', instanceid, files[0]))
        return '', httplib.NO_CONTENT
"""

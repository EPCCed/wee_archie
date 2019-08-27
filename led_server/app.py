#!venv/bin/python
from multiprocessing import Pipe, Queue, Manager
from flask import Flask
from flask import request
from display import Display
from display_objects import *
import utils
import re
import socket
import logging

# Static Server Globals
delay = 0.01

with Display(delay=delay) as display:
    app = Flask(__name__)
    state = {}

    # Plays arbitrary anim.
    @app.route('/play', methods=['POST'])
    def play():
        try:
            anim = request.form['anim']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        display.frames.put(Animation().load_folder(anim, delay=float(request.form.get('delay', 0.5))))
        msg = 'Animation for {0} is queued\n'.format(anim)
        logging.info(msg)
        return msg

    # Plays receive message anim, blocks and confirms sending before continuing
    @app.route('/receive/', methods=['POST'])
    def receive():
        try:
            src = request.form['src']
            dest = request.form['dest']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        if 'c' in request.form:
            state['outboxes'][dest][1].send( True )
            return 'Receipt by node {0} from node {1} acknowledged. \n'.format(src, dest)

        recv_obj = Recv(src, dest, state['hosts'], state['inboxes'][src][0])
        display.frames.put(recv_obj)

        msg = 'Receive animation from {0} to {1} queued, confirmation sent, awaiting send!\n'.format(src, dest)
        logging.info(msg)
        return msg

    # Plays send message anim, blocks and confirms reception before continuing
    @app.route('/send/', methods=['POST'])
    def send():
        try:
            src = request.form['src']
            dest = request.form['dest']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        if 'c' in request.form:
            state['inboxes'][src][1].send( True )
            return 'Sending by node {0} to node {1} acknowledged.'.format(src, dest)

        if 'async' in request.form:
            display.frames.put(Isend(src, dest, state['hosts'], None))
            return 'Async send from {0} to {1} queued, awaiting reception\n'.format(src,dest)

        send_obj = Send(src, dest, state['hosts'], state['outboxes'][dest][0])
        display.frames.put(send_obj)

        msg = 'Send animation from {0} to {1} queued, confirmation sent, awaiting reception!\n'.format(src,dest)
        logging.info(msg)
        return msg

    # Plays send message anim without blocking.
    @app.route('/isend/', methods=['POST'])
    def isend():
        try:
            src = request.form['src']
            dest = request.form['dest']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        display.frames.put(Isend(src, dest, state['hosts'], None))
        msg = 'Async send from {0} to {1} queued, awaiting reception\n'.format(src,dest)
        logging.info(msg)
        return msg

    # Plays non-blocking send and a blocking receive
    # TODO: Make this more accurate to MPI
    @app.route('/sendrecv/', methods=['POST'])
    def sendrecv():
        try:
            src = request.form['src']
            dest = request.form['dest']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        display.frames.put(Isend(state['hostname'], dest, state['hosts'], None))
        display.frames.put(Recv(src, state['hostname'], state['hosts'], state['inboxes'][src][0]))

        msg = 'Send and receive animation to {1} and from {0} queued on {2}, confirmation sent, awaiting reception!\n'.format(src,dest,state['hostname'])
        logging.info(msg)
        return msg

    # Plays broadcast animations, wait on all to receive, wait for broadcast to start before exit.
    @app.route('/bcast/', methods=['POST'])
    def bcast():
        try:
            src = request.form['src']
            host = request.form['host']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)


        if request.form.get('c', False):
            state['bcast'].put(True)
            return 'Bcast confirmation received on {0}.\n'.format(host)

        if src == host: # Do Root Anim
            display.frames.put(Bcast(src, host, {d for d in state['groups']['world'] if d != host}, state['bcast'], state['hosts']))
        else: # Do Leaf Anim & confirm receive
            display.frames.put(Bcast(src, host, {src}, state['bcast'], state['hosts']))

        msg = 'Bcast animation queued.\n'
        logging.info(msg)
        return msg

    # Plays gather animations, wait on all to send, wait for gather to start before exit.
    @app.route('/gather/', methods=['POST'])
    def gather():
        try:
            dest = request.form['dest']
            host = request.form['host']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        if request.form.get('c', False):
            state['gather'].put(True)
            return 'Gather confirmation received on {0}.\n'.format(host)

        if dest == host: # Do Root Anim
            display.frames.put(Gather(dest, host, {s for s in state['groups']['world'] if s != host}, state['gather'], state['hosts']))
        else: # Do Leaf Anim & confirm receive
            display.frames.put(Gather(dest, host, {dest}, state['gather'], state['hosts']))

        msg = 'Gather animation queued.\n'
        logging.info(msg)
        return msg


    # Plays scatter animations, wait on all to receive, wait for scatter to start before exit.
    @app.route('/scatter/', methods=['POST'])
    def scatter():
        try:
            src = request.form['src']
            host = request.form['host']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        if request.form.get('c', False):
            state['scatter'].put(True)
            return 'Scatter confirmation received on {0}.\n'.format(host)

        if src == host: # Do Root Anim
            display.frames.put(Scatter(src, host, {d for d in state['groups']['world'] if d != host}, state['scatter'], state['hosts']))
        else: # Do Leaf Anim & confirm receive
            display.frames.put(Scatter(src, host, {src}, state['scatter'], state['hosts']))

        msg = 'Scatter animation queued.\n'
        logging.info(msg)
        return msg

    # Plays reduce animations, wait on all to reduce, wait for reduce to start before exit.
    @app.route('/reduce/', methods=['POST'])
    def reduce():
        try:
            dest = request.form['dest']
            host = request.form['host']
            op = request.form['op']
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        if request.form.get('c', False):
            state['reduce'].put(True)
            return 'Reduce confirmation received on {0}.\n'.format(host)

        if dest == host: # Do Root Anim
            display.frames.put(Reduce(op, dest, host, {s for s in state['groups']['world'] if s != host}, state['reduce'], state['hosts']))
        else: # Do Leaf Anim & confirm receive
            display.frames.put(Reduce(op, dest, host, {dest}, state['reduce'], state['hosts']))

        msg = 'Reduce animation queued.\n'
        logging.info(msg)
        return msg

    # Plays Idle animation for fixed length of time, with short pauses to indicate 'checking' step
    @app.route('/idle/', methods=['POST'])
    def idle():
        try:
            time = request.form['t']
            pause = request.form['p']
            # anim = request.form['a'] # custom animation name here, for more intelligent computation animation
        except KeyError: return 'Invalid data {0}\n'.format(request.form)

        display.frames.put(Idle(time, pause))
        msg = 'Idle animation queued for {0} seconds, with interval {1}\n'.format(time, pause)
        logging.info(msg)
        return msg

    # Blocks until further input if force is true, otherwise do nothing under current implementation
    @app.route('/wait/', methods=['POST'])
    def wait():
        try:
            force = int(request.form['force'])
        except KeyError: return 'Invalid arguments {0}\n'.format(request.form)

        if(force == 1 or state['wait']):
            msg = 'Waiting for user input on {0}\n'.format(state['hostname'])
            display.frames.put(Block(state['waiting'][0], DisplayImage(delay = 0)))
        else:
            msg = 'Can wait on {0} - skipping...\n'.format(state['hostname'])

        logging.info(msg)
        return msg

    # Unblocks a wait
    @app.route('/resume/', methods=['POST'])
    def resume():
        state['waiting'][1].send(True)
        msg = 'Finished waiting on {0}\n'.format(state['hostname'])
        logging.info(msg)
        return msg

    # Restarts the server
    # TODO: Debug issues with some freezing displays
    @app.route('/restart')
    def restart():
        display.restart()
        msg = 'Application restarted\n'
        logging.info(msg)
        return msg

    # Start on execution, server state solution
    if __name__ == '__main__':
        state['manager'] = Manager()
        state['hostname'] = socket.gethostname()
        state['hosts'] = utils.read_hosts('hostfile.csv')
        state['groups'] = {'world': {h for h in state['hosts']} }
        state['inboxes'] = {host: Pipe() for host in state['hosts']}
        state['outboxes'] = {host: Pipe() for host in state['hosts']}
        state['bcast'] = state['manager'].Queue()
        state['scatter'] = state['manager'].Queue()
        state['gather'] = state['manager'].Queue()
        state['reduce'] = state['manager'].Queue()
        state['waiting'] = Pipe()
        state['wait'] = True

        app.run(host='0.0.0.0', port=5555, debug=True)

import threading
import logging
from subprocess import Popen, PIPE, STDOUT, call
import time
import config as cfg
import frameworkdb as fdb

class RunSim(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        return

    def run(self):
        execfile = None
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            execfile = conn.getSimulationExecutable(self.kwargs['simid'])
        procargs = [execfile, '--config='+self.kwargs['config'], '--output='+self.kwargs['output']] 
        proc = Popen(procargs, shell=False, stdout=PIPE)
        status = proc.poll()
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            conn.updateInstance(self.kwargs['instanceid'], self.kwargs['simid'], cfg.STATUS_NAMES['running'])
        while status is None:
           time.sleep(1)
           status = proc.poll()    
        if status == 0:
           #update complete
           with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
               conn.updateInstance(self.kwargs['instanceid'], self.kwargs['simid'], cfg.STATUS_NAMES['complete'])
        else:
           #update error
           if proc is not None:
              proc.kill()
           with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
               conn.updateInstance(self.kwargs['instanceid'], self.kwargs['simid'], cfg.STATUS_NAMES['error'])
        self.kwargs['pool'].pop(self.kwargs['instanceid'])
        return

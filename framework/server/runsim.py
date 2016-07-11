import threading
from subprocess import Popen, PIPE
import time
import config as cfg
import frameworkdb as fdb

class RunSim(threading.Thread):

    CONFIG_PREFIX = '--config='
    OUTPUT_PREFIX = '--output='

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        return

    def run(self):
        executablefile = None
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            executablefile = conn.getSimulationExecutable(self.kwargs['simid'])
        executablelist =[]
        if executablefile['ExecutionPrefix'] is not None:
            executablelist.append(executablefile['ExecutionPrefix'])
        if executablefile['ExecutionHostFile'] is not None:
            executablelist.append(executablefile['ExecutionHostFile'])
        executablelist.append(executablefile['Executable'])
        executablelist.append( self.CONFIG_PREFIX+self.kwargs['config'])
        executablelist.append( self.OUTPUT_PREFIX+self.kwargs['output'])
        procargs = [executablefile['Executable'],
                    self.CONFIG_PREFIX+self.kwargs['config'], self.OUTPUT_PREFIX+self.kwargs['output']]
        proc = Popen([' '.join(executablelist)], shell=True, stdout=PIPE)
        status = proc.poll()
        with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
            conn.updateInstance(self.kwargs['instanceid'],
                                self.kwargs['simid'], cfg.STATUS_NAMES['running'])
        while status is None:
            time.sleep(1)
            status = proc.poll()
        if status == 0:
            #update complete
            with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
                conn.updateInstance(self.kwargs['instanceid'],
                                    self.kwargs['simid'], cfg.STATUS_NAMES['complete'])
        else:
            #update error
            if proc is not None:
                proc.kill()
            with fdb.SimulationInstanceConnector(cfg.DATABASE_CONNECTION) as conn:
                conn.updateInstance(self.kwargs['instanceid'],
                                    self.kwargs['simid'], cfg.STATUS_NAMES['error'])
        if self.kwargs['pool'] is not None:
            self.kwargs['pool'].pop(self.kwargs['instanceid'])
        return

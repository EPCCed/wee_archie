""" Simulation Runner
Class inheriting from Thread which will run a simulation
code in a subprocess/shell.

Uses the frameworkdb to update simulation status.

Uses config to get the database connection and status values.
"""
import threading
import time
import config as cfg
import frameworkdb as fdb
from subprocess import Popen, PIPE


class SimulationRunner(threading.Thread):
    """ Class structure
        Based on threading.Thread.

        Run method will start simulation
        and updates simulation instance status

        Will start a simulation using a config
        file and output directory.
    """
    CONFIG_PREFIX = '--config='
    OUTPUT_PREFIX = '--output='

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        """
        Init method - calls threading.Thread.__init__ with
        below parameters.

        :param group: inherited parameter
        :param target: inherited parameter
        :param name: inherited parameter
        :param args: arguments list
        :param kwargs: keyword argument dictionary
        :param verbose: inherited parameter
        :return: instance
        """
        threading.Thread.__init__(self, group=group, target=target, name=name)
        self.args = args
        self.kwargs = kwargs
        return

    def run(self):
        """
        Run method connects to the database and gets execution data
        The execution list is created and joined and passed to the subprocess.
        The process will loop until the process exits or goes into error state

        The status is updated in the database before and after execution.
        :return:
        """
        with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
            executablefile = conn.getSimulationExecutable(self.kwargs['simid'])
        executablelist = []
        if executablefile['ChangeToDir'] is not None:
            executablelist.append('cd ' + self.kwargs['output'] + ';')
        if executablefile['ExecutionPrefix'] is not None:
            executablelist.append(executablefile['ExecutionPrefix'])
        if executablefile['ExecutionHostFile'] is not None:
            executablelist.append(executablefile['ExecutionHostFile'])
        executablelist.append(executablefile['Executable'])
        executablelist.append(self.CONFIG_PREFIX + self.kwargs['config'])
        executablelist.append(self.OUTPUT_PREFIX + self.kwargs['output'])
        proc = Popen([' '.join(executablelist)], shell=True, stdout=PIPE)
        status = proc.poll()
        with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
            conn.updateInstance(self.kwargs['instanceid'],
                                self.kwargs['simid'], cfg.STATUS_NAMES['running'])
        while status is None:
            time.sleep(1)
            status = proc.poll()
        if status == 0:
            # update complete
            with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
                conn.updateInstance(self.kwargs['instanceid'],
                                    self.kwargs['simid'], cfg.STATUS_NAMES['complete'])
        else:
            # update error
            if proc is not None:
                proc.kill()
            with fdb.SimulationConnector(cfg.DATABASE_CONNECTION) as conn:
                conn.updateInstance(self.kwargs['instanceid'],
                                    self.kwargs['simid'], cfg.STATUS_NAMES['error'])
        if self.kwargs['pool'] is not None:
            self.kwargs['pool'].pop(self.kwargs['instanceid'])
        return

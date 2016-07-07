import threading
import logging
from subprocess import Popen, PIPE, STDOUT, call
import time
import config as cfg
import sqlite3 as lite


class RunSim(threading.Thread):
    def get_db(self):
        db = lite.connect(cfg.DATABASE_CONNECTION)
        db.row_factory = lite.Row
        return db

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        return

    def run(self):
        execfile = None
        with self.get_db() as con:
            cur = con.cursor()
            cur.execute('SELECT Executable FROM Simulations WHERE SIMID=?', (self.kwargs['simid'],))
            execfile = cur.fetchone()[0]
        procargs = [execfile, '--config='+self.kwargs['config'], '--output='+self.kwargs['output']] 
        print ','.join(procargs)
        proc = Popen(procargs, shell=False, stdout=PIPE)
        status = proc.poll()
        with self.get_db() as con:
            cur = con.cursor()
            cur.execute('UPDATE Instances SET Status=? WHERE SIMID=? and IID=? ', (cfg.STATUS_NAMES['running'],self.kwargs['simid'],self.kwargs['instanceid']))
            con.commit()
        time.sleep(10)
        while status is None:
           time.sleep(1)
           status = proc.poll()    
        if status == 0:
           #update complete
           with self.get_db() as con:
               cur = con.cursor()
               cur.execute('UPDATE Instances SET Status=? WHERE SIMID=? and IID=? ', (cfg.STATUS_NAMES['complete'],self.kwargs['simid'],self.kwargs['instanceid']))
               con.commit()
        else:
           #update error
           if proc is not None:
              proc.kill()
           with self.get_db() as con:
               cur = con.cursor()
               cur.execute('UPDATE Instances SET Status=? WHERE SIMID=? and IID=? ', (cfg.STATUS_NAMES['error'],self.kwargs['simid'],self.kwargs['instanceid']))
               con.commit()
        self.kwargs['pool'].pop(self.kwargs['instanceid'])
        return

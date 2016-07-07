import os
import logging
import sqlite3 as lite

class SimulationInstanceConnector(object):

    def __init__(self, connectiontarget):
        self.connectiontarget = connectiontarget

    def __enter__(self):
        self.database = lite.connect(self.connectiontarget)
        self.database.row_factory = lite.Row
        return self

    def __exit__(self, type, value, traceback):
        if self.database is not None:
            self.database.close()

    def getInstanceStatus(self, simulationid, instanceid):
        cursor = self.database.cursor()
        cursor.execute('SELECT Status FROM Instances WHERE SIMID=? AND IID=?', (simulationid, instanceid))
        return cursor.fetchone()['Status'] 

    def createInstance(self, instanceid, simulationid, status):
        try:
            cursor = self.database.cursor()
            cursor.execute("""INSERT INTO Instances(IID,SIMID,Status) VALUES(?,?,?)""",
                           (instanceid, simulationid, status))
            self.database.commit()
            return True
        except lite.Error:
            return False
     
    def getSimulations(self):
        cursor = self.database.cursor()
        cursor.execute('SELECT SIMID, FullName FROM Simulations')  
        return cursor.fetchall()
    
    def getSimulation(self, simulationid):
        cursor = self.database.cursor()
        cursor.execute('SELECT * FROM Simulations WHERE SIMID=?', (simulationid, ))
        return cursor.fetchone()

    def getInstancesOf(self, simulationid):
        cursor = self.database.cursor()
        cursor.execute('SELECT * FROM Instances WHERE SIMID=?', (simulationid, ))
        return cursor.fetchall()

    def getSimulationExecutable(self, simulationid):
        cursor = self.database.cursor()
        cursor.execute('SELECT Executable FROM Simulations WHERE SIMID=?', (simulationid, ))
        return cursor.fetchone()['Executable']

    def updateInstance(self, instanceid, simulationid, status):
        try:
            cursor = self.database.cursor()
            cursor.execute("""UPDATE Instances SET Status=? WHERE SIMID=? and IID=?""",
                           (status, simulationid, instanceid))
            self.database.commit()
            return True
        except lite.Error:
            return False
    
    def deleteInstance(self, instanceid, simulationid):
        try:
            cursor = self.database.cursor()
            cursor.execute("""DELETE FROM Instances WHERE SIMID=? and IID=?""",
                           (simulationid, instanceid))
            self.database.commit()
            return True
        except lite.Error:
            return False

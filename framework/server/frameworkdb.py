""" Framework Database Module

Module containing classes to access the instance database in the framework.

Contents:
SimulationConnector - access data about simulations and create instances of a simulation.

Imports sqlite3
"""
import sqlite3 as lite

class SimulationConnector(object):
    """ Class for allowing connection and querying of the framework database for
        simulations and instances.
        Designed to be used with the with <> as <> syntax to ensure closing of connections.
    """

    def __init__(self, connectiontarget):
        """
        Inits the instance with the parameter connectiontarget
        :param connectiontarget: database connection target
        :return:
        """
        self.connectiontarget = connectiontarget

    def __enter__(self):
        """
        Returns a database connection with the row_factory set to sqlite3.Row
        :return:
        """
        self.database = lite.connect(self.connectiontarget)
        self.database.row_factory = lite.Row
        return self

    def __exit__(self, type, value, traceback):
        """
        Closes the database connection on exit.
        :param type:
        :param value:
        :param traceback:
        :return:
        """
        if self.database is not None:
            self.database.close()

    def getInstanceStatus(self, simulationid, instanceid):
        """
        Gets the status for a given simulation and instance id
        :param simulationid:
        :param instanceid:
        :return:
        """
        cursor = self.database.cursor()
        cursor.execute('SELECT Status FROM Instances WHERE SIMID=? AND IID=?', (simulationid, instanceid))
        return cursor.fetchone()['Status'] 

    def createInstance(self, instanceid, simulationid, status):
        """
        Creates an instance of a simulation with a given status code.
        :param instanceid:
        :param simulationid:
        :param status:
        :return:
        """
        try:
            cursor = self.database.cursor()
            cursor.execute("""INSERT INTO Instances(IID,SIMID,Status) VALUES(?,?,?)""",
                           (instanceid, simulationid, status))
            self.database.commit()
            return True
        except lite.Error:
            return False
     
    def getSimulations(self):
        """
        Returns a basic list of simulations - each entry has a SIMID and Fullname
        :return:
        """
        cursor = self.database.cursor()
        cursor.execute('SELECT SIMID, FullName FROM Simulations')  
        return cursor.fetchall()
    
    def getSimulation(self, simulationid):
        """
        Returns all information on a given simulations ID
        :param simulationid:
        :return:
        """
        cursor = self.database.cursor()
        cursor.execute('SELECT * FROM Simulations WHERE SIMID=?', (simulationid, ))
        return cursor.fetchone()

    def getInstancesOf(self, simulationid):
        """
        Returns all current instances of a given simulation ID
        :param simulationid:
        :return:
        """
        cursor = self.database.cursor()
        cursor.execute('SELECT * FROM Instances WHERE SIMID=?', (simulationid, ))
        return cursor.fetchall()

    def getSimulationExecutable(self, simulationid):
        """
        Returns the execution information for a given simulation
        :param simulationid:
        :return:
        """
        cursor = self.database.cursor()
        cursor.execute('SELECT ExecutionPrefix, ExecutionHostFile, Executable FROM Simulations WHERE SIMID=?', (simulationid, ))
        return cursor.fetchone()

    def updateInstance(self, instanceid, simulationid, status):
        """
        Updates the instanceid instance with the new status
        :param instanceid:
        :param simulationid:
        :param status:
        :return:
        """
        try:
            cursor = self.database.cursor()
            cursor.execute("""UPDATE Instances SET Status=? WHERE SIMID=? and IID=?""",
                           (status, simulationid, instanceid))
            self.database.commit()
            return True
        except lite.Error:
            return False
    
    def deleteInstance(self, instanceid, simulationid):
        """
        Removes an instances from the framework data layer.
        :param instanceid:
        :param simulationid:
        :return:
        """
        try:
            cursor = self.database.cursor()
            cursor.execute("""DELETE FROM Instances WHERE SIMID=? and IID=?""",
                           (simulationid, instanceid))
            self.database.commit()
            return True
        except lite.Error:
            return False

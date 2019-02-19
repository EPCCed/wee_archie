""" Server Config File
This defines constants for the running Flask App in the Raspberry Pi framework.

Notes: In future versions - move config to text file and read into the names here.
"""
import os

# Set Debug Flag
DEBUG = True

# Root Directory for application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Directory for results of simulations
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

# File Database to connection
DATABASE_CONNECTION = os.path.join(BASE_DIR, 'simulations.db')
DB_CONNECTION_OPTS = {}

# Status values and names for use with database
STATUS_NAMES = {'ready':'READY', 'running':'RUNNING', 'complete':'COMPLETE', 'error':'ERROR'}

# Files to ignore in results
OMITTED_FILES = ['config.txt','damping.dat','depth.dat','mask.dat','data.tar.gz']

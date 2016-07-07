import os
DEBUG=True
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_CONNECTION = os.path.join(BASE_DIR, 'simulations.db')
DB_CONNECTION_OPTS = {}
STATUS_NAMES={'ready':'READY','running':'RUNNING','complete':'COMPLETE','error':'ERROR'}

""" Run.py - start the framework server

Runs the flask app in the server framework:
Using 0.0.0.0 (all listen) on port 5000.

"""
from framework import app
app.run(host='0.0.0.0', port=5000)

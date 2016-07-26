""" Import Module to allow the HTTP Status codes to be used in the responses
in both Python 2 and 3.

Due to changes (httplib to http.<>) to get the codes, they are wrapped into
httpcodes with an import of the underlying library dependent on python version.
"""
import sys
if sys.version_info[0] == 2:
    import httplib as httpcodes
else:
    import http.client as httpcodes
sys.modules[__name__] = httpcodes

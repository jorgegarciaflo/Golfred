#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Flask web service for Golfred
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import Flask, request
from werkzeug import secure_filename
import golfred
import json
import argparse
import uuid
import os

app = Flask('poswebservice')
app.config.from_pyfile('server.cfg')

# Variables declarations
version = '0.1'

# Loading blueprints
from golfred_api import api
app.register_blueprint(api)

from golfred_web import web
app.register_blueprint(web)



if __name__ == '__main__':
    p = argparse.ArgumentParser("Golfred service")
    p.add_argument("--dir","-dir",
            action="store",dest="dir",
            help="Directory to store experiences")
    p.add_argument("--host",default="127.0.0.1",
            action="store", dest="host",
            help="Root url [127.0.0.1]")
    p.add_argument("--port",default=5000,type=int,
            action="store", dest="port",
            help="Port url [500]")
    p.add_argument("--debug",default=False,
            action="store_true", dest="debug",
            help="Use debug deployment [Flase]")
    p.add_argument("-v", "--verbose",
            action="store_true", dest="verbose",
            help="Verbose mode [Off]")
    opts = p.parse_args()

    if opts.dir:
        app.config['EXPERIENCES'] = opts.DIR
    EXPERIENCES=golfred.recover_experiences(app.config['EXPERIENCES'])

    app.run(debug=opts.debug,
            host=opts.host,
            port=opts.port)


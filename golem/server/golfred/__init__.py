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
from flask_sqlalchemy import SQLAlchemy
from flask.ext.triangle import Triangle
import golfred
import argparse
from rdflib import Graph

g = Graph()
g.parse('golfred/golfred.nt',format="nt")

app = Flask('golfred')
Triangle(app)
app.config.from_pyfile('server.cfg')
db = SQLAlchemy(app)

# Loading blueprints
from golfred_api import api
app.register_blueprint(api)

from golfred_web import web
app.register_blueprint(web)



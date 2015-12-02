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
import golfred
import json
import argparse
import uuid

app = Flask('poswebservice')

# Variables declarations
version = '0.1'
OUTPUT='output'

@app.route('/',methods=['GET'])
def index():
    return "Service up!" 

@app.route('/api/v0.1',methods=['GET'])
@app.route('/api',methods=['GET'])
def api():
    return json.dumps(
        {"Golfred":
            {'version':version,
             'actions':{
                 'new': 'Creates experience',
                 'push': 'Adds visual memory to experience',
                 'summary': 'Retrieve visual experience'
                 }
            }
        }
    ) 

@app.route('/api/v0.1/status',methods=['GET'])
@app.route('/api/status',methods=['GET'])
def status():
    return json.dumps({
            'experiences':len(EXPERIENCES),
            'status': 'ok'
        })


@app.route('/api/v0.1/list/experiences',methods=['GET'])
@app.route('/api/list/experiences',methods=['GET'])
def list_experiences():
    return json.dumps({
            'experiences':[exp for exp,size in EXPERIENCES.iteritems()],
        })


@app.route('/api/v0.1/list/memories/visual/<idd>',methods=['GET'])
@app.route('/api/list/memories/visual/<idd>',methods=['GET'])
def list_visual_memories(idd):
    memories=golfred.recover_visual_memories(OUTPUT,idd)
    if not memories==False:
        return json.dumps({
                'id_experience':idd,
                'visual_memories':memories,
            })
    else:
        return json.dumps({
                    'status': 'error'
                })



@app.route('/api/v0.1/new',methods=['GET'])
@app.route('/api/new',methods=['GET'])
def new():
    idd=str(uuid.uuid4())
    if golfred.create_new_experience(OUTPUT,idd):
        return json.dumps({
                    'id_experince':idd,
                    'status': 'ok'
                })
    else:
        return json.dumps({
                    'status': 'error'
                })


@app.route('/api/v0.1/push/visual/<idd>/<img>',methods=['GET'])
@app.route('/api/push/visual/<idd>/<img>',methods=['GET'])
def push_memory(idd,img):
    return json.dumps({
                'status': 'ok',
                'id_experience':idd,
                'id_visual':img
    })

  
@app.route('/api/v0.1/summary/<idd>',methods=['GET'])
@app.route('/api/summary/<idd>',methods=['GET'])
def summary(idd):
    return json.dumps({
        'summary': ["i saw this", "and then this"],
        'id_experience':idd
    })



if __name__ == '__main__':
    p = argparse.ArgumentParser("Golfred service")
    p.add_argument("DIR",
            action="store",
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

    OUTPUT=opts.DIR
    EXPERIENCES=golfred.recover_experiences(OUTPUT)

    app.run(debug=opts.debug,
            host=opts.host,
            port=opts.port)


#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Flask web service for Golfred
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import Flask, request, Blueprint
from werkzeug import secure_filename
import golfred
import json
import argparse
import uuid
import os

api = Blueprint('api',__name__)

@api.route('/api/v0.1',methods=['GET'])
@api.route('/api',methods=['GET'])
def api_help():
    return json.dumps(
        {"Golfred":
            {'version':version,
             'actions':{
                 'create': 'Creates experience',
                 'list': 'List experience',
                 'push': 'Adds visual memory to experience',
                 'summarize': 'Retrieve visual experience'
                 }
            }
        }
    ) 

@api.route('/api/v0.1/status',methods=['GET'])
@api.route('/api/status',methods=['GET'])
def status():
    return json.dumps({
            'experiences':len(EXPERIENCES),
            'status': 'ok'
        })


@api.route('/api/v0.1/list/experiences',methods=['GET'])
@api.route('/api/list/experiences',methods=['GET'])
def list_experiences():
    return json.dumps({
            'experiences':[exp for exp,size in EXPERIENCES.iteritems()],
        })


@api.route('/api/v0.1/list/memory/<idd>',methods=['GET'])
@api.route('/api/list/memory/<idd>',methods=['GET'])
def list_visual_memories(idd):
    memories=golfred.recover_visual_memories(api.config['EXPERIENCES'],idd)
    if not memories==False:
        return json.dumps({
                'id_experience':idd,
                'visual_memories':memories,
            })
    else:
        return json.dumps({
                    'status': 'error'
                })



@api.route('/api/v0.1/create',methods=['GET'])
@api.route('/api/create',methods=['GET'])
def new():
    idd=str(uuid.uuid4())
    if golfred.create_new_experience(api.config['EXPERIENCES'],idd):
        return json.dumps({
                    'id_experince':idd,
                    'status': 'ok'
                })
    else:
        return json.dumps({
                    'status': 'error'
                })


@api.route('/api/v0.1/push/<idd>',methods=['POST'])
@api.route('/api/push/<idd>',methods=['PUT','GET'])
def push_memory(idd):
    if request.method == 'PUT':
        data = request.data
        filename="{0}.jpg".format(len(EXPERIENCES[idd]))
        filename = secure_filename(filename)
        filename =os.path.join(api.config['EXPERIENCES'],idd,filename)
        with open(filename, 'w') as f:
            f.write(request.data)
        text=golfred.img2text(filename)
        EXPERIENCES[idd].apiend(filename)
        return json.dumps({
                'status': 'ok',
                'id_experience':idd,
                'text':text,
                'id_visual':filename
                })
        return json.dumps({
                'status': 'error'
            })
    return 'ok'

  
@api.route('/api/v0.1/summarise/<idd>',methods=['GET'])
@api.route('/api/summarise/<idd>',methods=['GET'])
def summary(idd):
    return json.dumps({
        'summary': ["i saw this", "and then this"],
        'id_experience':idd
    })



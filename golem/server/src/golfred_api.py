#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Flask web service for Golfred
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import Flask, request, Blueprint, send_from_directory
from werkzeug import secure_filename
import golfred
import json
import argparse
import uuid
import os
import datetime

api = Blueprint('api',__name__)
from golfred_service import db
from models import *
from sqlalchemy.orm.exc import NoResultFound


visual_memory=MemoryType.query.filter(MemoryType.name=="visual").all()[0]

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

@api.route('/api/v0.1/latest/experiences',methods=['GET'])
@api.route('/api/latest/experiences',methods=['GET'])
@api.route('/api/v0.1/latest/experiences/<n>',methods=['GET'])
@api.route('/api/latest/experiences/<n>',methods=['GET'])
def latest_experiences(n):
    exps=Experience.query.order_by(Experience.id.desc()).limit(n)
    exps = [l.as_dict() for l in exps]
    return json.dumps(exps)


@api.route('/api/v0.1/list/memories/<uuid>',methods=['GET'])
@api.route('/api/list/memories/<uuid>',methods=['GET'])
def list_visual_memories(uuid):
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
    except NoResultFound:
        return json.dumps({
                    'status': 'error'
                })
    try:
        memories=Memory.query.filter(Memory.expid==exp.id).all()
        res=[m.as_dict() for m in memories]
        return json.dumps(res)
    except NoResultFound:
        return json.dumps([])


@api.route('/api/v0.1/create',methods=['POST'])
@api.route('/api/create',methods=['POST'])
def new():
    content = request.json
    if content and\
       len(content['name'])>0 and\
       len(content['description'])>0:
            exp=Experience(name=content['name'],
                    uuid=str(uuid.uuid4())[:15],
                    description=content['description'],
                    created_at=datetime.datetime.now(),
                    modified_at=datetime.datetime.now()
                )
            db.session.add(exp)
            db.session.commit()
            return json.dumps({
                    'id_experince':exp.id,
                    'status': 'ok'
                })
    else:
        return json.dumps({
                    'status': 'error'
                })



@api.route('/api/v0.1/delete/experience',methods=['POST'])
@api.route('/api/delete/expereince',methods=['POST'])
def delete():
    content = request.json
    if content and\
       len(content['uuid'])>0:
            exp=Experience.query.filter(Experience.uuid==content['uuid']).one()
            db.session.delete(exp)
            db.session.commit()
            return json.dumps({
                    'id_experince':exp.id,
                    'status': 'ok'
                })
    else:
        return json.dumps({
                    'status': 'error'
                })

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif'])


@api.route('/api/v0.1/add/memories/<uuid>',methods=['POST'])
@api.route('/api/add/memories/<uuid>',methods=['POST'])
def add_memories(uuid):
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
    except NoResultFound:
        return json.dumps({
                'status': 'error'
            })
    files = request.files.getlist('files')
    for f in files:
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            if not os.path.isdir(os.path.join('memories',uuid)):
                os.mkdir(os.path.join('memories',uuid))
            filename=os.path.join("memories", uuid,filename)
            f.save(filename)
            mem=Memory(filename=filename,
                added_at=datetime.datetime.now(),
                modified_at=datetime.datetime.now(),
                typeid=visual_memory.id,
                expid=exp.id
            )
            db.session.add(mem)
    db.session.commit()
    return json.dumps({
            'status': 'ok'
            })


@api.route('/api/v0.1/push/<idd>',methods=['PUT','GET'])
@api.route('/api/push/<idd>',methods=['PUT','GET'])
def push_memory(idd):
    if request.method == 'PUT':
        data = request.data
        filename="{0}.jpg".format(len(EXPERIENCES[idd]))
        filename = secure_filename(filename)
        filename =os.path.join(app.config['EXPERIENCES'],idd,filename)
        with open(filename, 'w') as f:
            f.write(request.data)
        text=golfred.img2text(filename)
        EXPERIENCES[idd].append(filename)
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


@api.route('/api/v0.1/delete/memory',methods=['POST'])
@api.route('/api/delete/memory',methods=['POST'])
def delete_memory():
    content = request.json
    print(content)
    if content:
        mem=Memory.query.filter(Memory.id==content['id']).one()
        db.session.delete(mem)
        db.session.commit()
        return json.dumps({
                'id_memory':mem.id,
                'status': 'ok'
            })
    else:
        return json.dumps({
                    'status': 'error'
                })



  
@api.route('/api/v0.1/summarise/<idd>',methods=['GET'])
@api.route('/api/summarise/<idd>',methods=['GET'])
def summary(idd):
    return json.dumps({
        'summary': ["i saw this", "and then this"],
        'id_experience':idd
    })



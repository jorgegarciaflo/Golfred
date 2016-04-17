#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Flask web service for Golfred
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import request, Blueprint
from werkzeug import secure_filename
import golfred
import json
import uuid
import os
import datetime

api = Blueprint('api',__name__)
from golfred_service import db
from models import *
from sqlalchemy.orm.exc import NoResultFound
import re


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
    exps=Experience.query.order_by(Experience.id.desc()).all()
    exps = [l.as_dict() for l in exps]
    return json.dumps(exps)


@api.route('/api/v0.1/latest/experiences',methods=['GET'])
@api.route('/api/latest/experiences',methods=['GET'])
@api.route('/api/v0.1/latest/experiences/<n>',methods=['GET'])
@api.route('/api/latest/experiences/<n>',methods=['GET'])
def latest_experiences(n=10):
    exps=Experience.query.order_by(Experience.id.desc()).all()
    exps = [l.as_dict() for l in exps]
    return json.dumps(exps)


@api.route('/api/v0.1/list/memories/<uuid>',methods=['GET'])
@api.route('/api/list/memories/<uuid>',methods=['GET'])
def list_visual_memories(uuid):
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
    except NoResultFound:
        return json.dumps({
                    'status': 'error',
                    'message': 'Not experience found'

                })
    try:
        memories=Memory.query.filter(Memory.experience_id==exp.id).order_by(Memory.order.asc()).all()
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
    visual_memory=MemoryType.query.filter(MemoryType.name=="visual").one()
    read_perception=PerceptionType.query.filter(PerceptionType.name=="read").one()
    analisys_perception=PerceptionType.query.filter(PerceptionType.name=="analysis").one()
    fred_perception=PerceptionType.query.filter(PerceptionType.name=="fred").one()
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
    except NoResultFound:
        return json.dumps({
                'status': 'error'
            })
    files = request.files.getlist('files')
    for f in files:
        perceptions=[]
        if f and allowed_file(f.filename):
            filename_ = secure_filename(f.filename)
            if not os.path.isdir(os.path.join('memories',uuid)):
                os.mkdir(os.path.join('memories',uuid))
            filename=os.path.join("memories", uuid,filename_)
            f.save(filename)

            if request.args.get('analize', '')=="true":
                ana=golfred.cs_img2analize(filename)
                pt = Perception(
                    representation=json.dumps(ana),
                    type = analisys_perception
                    )
                perceptions.append(pt)
                if request.args.get('read', '')=="true":
                    cat=golfred.getCategory(ana)
                    regions,text=golfred.cs_img2text(filename,type=cat)
                    if len(text)>0:
                        pt = Perception(
                            representation=json.dumps(
                                {
                                    'regions':regions,
                                    'text':text
                                }
                                ),
                            type = read_perception
                            )
                        perceptions.append(pt)

            if request.args.get('fred', '')=="true" and len(regions)>0:
                filename_pref=filename.rsplit('.',1)
                if len(regions)>0:
                    filename_fred=filename_pref[0]+".fred"
                    ana=golfred.text2fred(regions[0][0],filename_fred)
                    pt = Perception(
                        representation=json.dumps(ana),
                        type = fred_perception
                        )
                    perceptions.append(pt)
                else:
                    ana=""

            total_memories=Memory.query.filter(Memory.experience_id==exp.id).count()
            mem=Memory(filename=filename,
                added_at=datetime.datetime.now(),
                modified_at=datetime.datetime.now(),
                type=visual_memory,
                experience_id=exp.id,
                perceptions=perceptions,
                order=total_memories
            )

            db.session.add(mem)
    db.session.commit()
    return json.dumps({
            'status': 'ok'
            })


@api.route('/api/v0.1/update/memory',methods=['POST'])
@api.route('/api/update/memory',methods=['POST'])
def update_memory():
    content = request.json
    id=content['mem']
    if content['type']=="fred":
        try:
            memory=Memory.query.filter(Memory.id==id).one()
            lines = None
            analysis= None
            p_fred=None
            for p in memory.perceptions:
                if p.type.name=="fred":
                    p_fred=p
                if p.type.name=="read":
                    regions=json.loads(p.representation)
                if p.type.name=="analysis":
                    analysis=json.loads(p.representation)

            filename_pref=memory.filename.rsplit('.',1)
            ana={'line':"",'fred':""}
            if regions and len(regions[0])>0:
                text=""
                for ls in regions:
                    for l in ls:
                        if re.match('^\D+$',l):
                            text=l
                            break
                filename_fred=filename_pref[0]+".fred"
                fred_output=golfred.text2fred(text,filename_fred)
                ana['line']=text
                ana['filename']=filename_fred
                ana['output']=fred_output
            elif analysis and len(analysis)>0 and analysis['description']:
               if analysis['description'] and\
                  analysis['description']['captions'] and\
                  len(analysis['description']['captions']) > 0 and\
                  analysis['description']['captions'][0]['text']: 
                    filename_fred=filename_pref[0]+".fred"
                    fred_output=golfred.text2fred(analysis['description']['captions'][0]['text'],filename_fred)
                    ana['line']=analysis['description']['captions'][0]['text']
                    ana['filename']=filename_fred
                    ana['output']=fred_output
            if not p_fred:
                fred_perception=PerceptionType.query.filter(PerceptionType.name=="fred").one()
                p_fred = Perception(
                        representation=json.dumps(ana),
                        type = fred_perception
                        )
                memory.perceptions.append(p_fred)
            else:            
                p_fred.representation=json.dumps(ana)
                db.session.add(p_fred)
            db.session.commit()
            return json.dumps({
                'status': 'ok'
                })
        except NoResultFound:
            return json.dumps({
                        'status': 'error'
                    })
    elif content['type']=="golem":
        try:
            memory=Memory.query.filter(Memory.id==id).one()
            p_golem=None
            for p in memory.perceptions:
                if p.type.name=="golem":
                    p_golem=p
                    break
            if p_golem:
                p_golem.representation=json.dumps({"position":content['position']})
                db.session.add(p_golem)
            else:
                golem_perception=PerceptionType.query.filter(PerceptionType.name=="golem").one()
                p_golem = Perception(
                    representation=json.dumps({"position":content['position']}),
                    type = golem_perception
                    )
                memory.perceptions.append(p_golem)
                db.session.add(memory)
 
            db.session.commit()
            return json.dumps({
                'status': 'ok'
                })
        except NoResultFound:
            return json.dumps({
                        'status': 'error'
                    })
    elif content['type']=="analysis":
        try:
            memory=Memory.query.filter(Memory.id==id).one()
            p_analysis=None
            for p in memory.perceptions:
                if p.type.name=="analysis":
                    p_analysis=p
                    break
            if p_analysis:
                ana=golfred.cs_img2analize(memory.filename)
                p_analysis.representation=json.dumps(ana)
                db.session.add(p_analysis)
            else:
                analisys_perception=PerceptionType.query.filter(PerceptionType.name=="analysis").one()
                ana=golfred.cs_img2analize(memory.filename)
                pt = Perception(
                    representation=json.dumps(ana),
                    type = analisys_perception
                    )
                memory.perceptions.append(pt)
            db.session.commit()
            return json.dumps({
                'status': 'ok'
                })
        except NoResultFound:
            return json.dumps({
                        'status': 'error'
                    })

    elif content['type']=="read":
        try:
            memory=Memory.query.filter(Memory.id==id).one()
            memory=Memory.query.filter(Memory.id==id).one()
            lines = None
            analysis= None
            p_cs=None
            for p in memory.perceptions:
                if p.type.name=="read":
                    p_cs=p
                if p.type.name=="analysis":
                    analysis=json.loads(p.representation)
                    cat=golfred.getCategory(analysis)
            if p_cs:
                regions,text=golfred.cs_img2text(memory.filename,type=cat)
                p_cs.representation=json.dumps(
                        {
                                'regions':regions,
                                'text':text
                        })
                db.session.add(p_cs)
            else:
                read_perception=PerceptionType.query.filter(PerceptionType.name=="read").one()
                regions,text=golfred.cs_img2text(memory.filename,type=cat)
                if len(text)>0:
                    pt = Perception(
                        representation=json.dumps(
                            {
                                'regions':regions,
                                'text':text
                            }),
                        type = read_perception
                        )
                    perceptions.append(pt)
                memory.perceptions.append(pt)
            db.session.commit()
            return json.dumps({
                'status': 'ok'
                })
        except NoResultFound:
            return json.dumps({
                        'status': 'error'
                    })


@api.route('/api/v0.1/push/<idd>',methods=['POST'])
@api.route('/api/push/<idd>',methods=['POST'])
def push_memory(idd):
    content = request.json
    uuid=content['uuid']
    if content['type']=="action":
        try:
            action_memory=MemoryType.query.filter(MemoryType.name=="action").one()
            type=content['type2']
            repr=content['representation']
            try:
                action_perception=PerceptionType.query.filter(PerceptionType.name==type).one()
            except:
                action_perception=PerceptionType(name=type) 
            exp=Experience.query.filter(Experience.uuid==uuid).one()
            total_memories=Memory.query.filter(Memory.experience_id==exp.id).count()
            mem=Memory(filename="",
                added_at=datetime.datetime.now(),
                modified_at=datetime.datetime.now(),
                type=action_memory,
                experience_id=exp.id,
                perceptions=[],
                order=total_memories
            )

            pt = Perception(
                        representation=repr,
                        type = action_perception
            )
            mem.perceptions.append(pt)
            db.session.add(mem)
            db.session.commit()

            return json.dumps({
                'status': 'ok'
            })

        except NoResultFound:
            return json.dumps({
                        'status': 'error',
                        'message': 'Not experience found'

                    })
   



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


@api.route('/api/v0.1/update/experience',methods=['POST'])
@api.route('/api/update/experience',methods=['POST'])
def update_experience():
    content = request.json
    uuid=content['uuid']
    if content['type']=="order":
        order=json.loads(content['order'])
        try:
            exp=Experience.query.filter(Experience.uuid==uuid).one()
            memories=Memory.query.filter(Memory.experience_id==exp.id).all()
            for memory in memories:
                memory.order=order[str(memory.id)]
                db.session.add(memory)
            db.session.commit()

            return json.dumps({
                'status': 'ok'
            })

        except NoResultFound:
            return json.dumps({
                        'status': 'error',
                        'message': 'Not experience found'

                    })
   

import re
re_words=re.compile('^\D+$')

@api.route('/api/v0.1/summarize/memory/<uuid>',methods=['GET'])
@api.route('/api/summarize/memory/<uuid>',methods=['GET'])
def summarize(uuid):
    try:
        summary=[]
        exp=Experience.query.filter(Experience.uuid==uuid).one()
        memories=Memory.query.filter(Memory.experience_id==exp.id).all()
        VARS={}
        for memory in memories:
            perceptions={'read':None}
            # Extracting variables
            try: 
                try:
                    VARS={'PREV_LOC':VARS['LOC']}
                except KeyError:
                    VARS={'PREV_LOC':None}
            except UnboundLocalError:
                VARS={'PREV_LOC':None}

            for p in memory.perceptions:
                perceptions[p.type.name]=json.loads(p.representation)
            try:
                VARS['LOC']=perceptions['golem']['position']
            except KeyError:
                VARS['LOC']=None
         
            if perceptions['analysis']:
                for cat in perceptions['analysis']['categories']:
                    try:
                        if VARS['CAT_SCORE']<cat['score']:
                            VARS['CAT_SCORE']=cat['score']
                            VARS['CAT']=cat['name']
                    except KeyError:
                        VARS['CAT_SCORE']=cat['score']
                        VARS['CAT']=cat['name']
                for cap in perceptions['analysis']['description']['captions']:
                    try:
                        if VARS['CAP_SCORE']<cap['confidence']:
                            VARS['CAP_SCORE']=cap['confidence']
                            VARS['CAP']=cap['text']
                    except KeyError:
                        VARS['CAP_SCORE']=cap['confidence']
                        VARS['CAP']=cap['text']
            
            if perceptions['read']:
                f=False
                for rs in perceptions['read']:
                    for l in rs:
                        if re_words.match(l):
                            f=True
                            break
                    if f:
                        break
                        
                VARS['TEXT']=l


            # TEMPLATES
            summary.append([])
            if not VARS['LOC']==VARS['PREV_LOC']:
                if VARS['PREV_LOC']=="hall" and VARS['LOC']=="office":
                    summary[-1].append(u"I enter the {LOC}".format(**VARS))
                elif VARS['PREV_LOC']=="office" and VARS['LOC']=="hall":
                    summary[-1].append(u"I exit to {LOC}".format(**VARS))
                else:
                    summary[-1].append(u"I was in the {LOC}".format(**VARS))
            else:
                summary[-1].append(u"while being in {LOC} i also".format(**VARS))
            if VARS['CAT']=='text_sign':
                summary[-1].append(u"there i saw a {CAP}".format(**VARS))
                summary[-1].append(u"it said {TEXT}".format(**VARS))
            elif VARS['CAT']=='text_':
                summary[-1].append(u"there there was a text".format(**VARS))
                summary[-1].append(u"it was about {TEXT}".format(**VARS))
            else:
                summary[-1].append(u"i saw {CAP}".format(**VARS))
                



            





        return json.dumps(summary)
    except NoResultFound:
        return json.dumps({
                    'status': 'error',
                    'message': 'Not experience found'

                })
    

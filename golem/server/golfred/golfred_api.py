#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Flask web service for Golfred
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import request, Blueprint,jsonify
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

version='v0.1'

@api.route('/api/v01',methods=['GET'])
@api.route('/api',methods=['GET'])
def api_help():
    return jsonify(
        {"Golfred":
            {'version':version,
             'actions':{
                 'status':'Server status',
                 'list/experiences': 'List experiences',
                 'list/events/<uuid>': 'List events for experience with uuid',
                 'latest/experiences[/<n>]': 'List n latest experiences',
                 'create/experience': 'Creates experience',
                 'update/experience': 'Updates experience',
                 'update/event': 'Updates event',
                 'delete/experience': 'Delete experience',
                 'add/events/<uuid>': 'Adds visual events for experience with uuid',
                 'push/event': 'Adds visual event to experience',
                 'summarize/experience/<uuid>': 'Summarizes an experience'
                 }
            }
        }
    ) 

@api.route('/api/v0.1/status',methods=['GET'])
@api.route('/api/status',methods=['GET'])
def status():
    total=Experience.query.count()
    return jsonify({
            'experiences':total,
            'status': 'ok'
        })

@api.route('/api/v0.1/list/experiences',methods=['GET'])
@api.route('/api/list/experiences',methods=['GET'])
def list_experiences():
    exps=Experience.query.order_by(Experience.id.desc()).all()
    exps = [l.as_dict() for l in exps]
    return jsonify(exps)


@api.route('/api/latest/experiences',defaults={'n':10},methods=['GET'])
@api.route('/api/latest/experiences/<n>',methods=['GET'])
@api.route('/api/v0.1/latest/experiences',defaults={'n':10},methods=['GET'])
@api.route('/api/v0.1/latest/experiences/<n>',methods=['GET'])
def latest_experiences(n):
    exps=Experience.query.order_by(Experience.id.desc()).limit(n)
    exps = [l.as_dict() for l in exps]
    return json.dumps(exps)

@api.route('/api/v0.1/create/experience',methods=['POST'])
@api.route('/api/create/experience',methods=['POST'])
def new():
    content = request.json
    if content and\
       len(content['name'])>0:
            datetime_=datetime.datetime.now()
            description=None
            if content.has_key('description'):
                description=content['description']
            exp=Experience(
                    name=content['name'],
                    uuid=str(uuid.uuid4())[:12],
                    description=description,
                    created_at=datetime_,
                    datetime=datetime_
                )
            db.session.add(exp)
            db.session.commit()
            return jsonify({
                'add_experince_id':exp.uuid,
                'status': 'ok'
                })
    else:
        return jsonify({
                    'status': 'error',
                    'msg': "Problem with post message"
                })

@api.route('/api/v0.1/delete/experience',methods=['POST'])
@api.route('/api/delete/experience',methods=['POST'])
def delete():
    content = request.json
    if not content:
        return jsonify({
                    'status': 'error',
                    'msg':'No json post information'
                })
    if len(content['uuid'])>0:
            exp=Experience.query.filter(Experience.uuid==content['uuid']).one()
            db.session.delete(exp)
            db.session.commit()
            return jsonify({
                    'deleted_experience_id':exp.id,
                    'status': 'ok'
                })
    else:
        return jsonify({
                    'status': 'error',
                    'msg':'No uuid information'
                })


@api.route('/api/v0.1/list/events/<uuid>',methods=['GET'])
@api.route('/api/list/events/<uuid>',methods=['GET'])
def list_visual_memories(uuid):
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
    except NoResultFound:
        return jsonify({
                    'status': 'error',
                    'msg': 'Not experience found'

                })
    try:
        es=Event.query.filter(Event.experience_id==exp.id).order_by(Event.order.asc()).all()
        return json.dumps([e.as_dict() for e in es])
    except NoResultFound:
        return json.dumps([])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in set(['png', 'jpg', 'jpeg', 'gif'])

@api.route('/api/v0.1/delete/event',methods=['POST'])
@api.route('/api/delete/event',methods=['POST'])
def delete_memory():
    content = request.json
    if content:
        e=Event.query.filter(Event.id==content['id']).one()
        db.session.delete(e)
        db.session.commit()
        return json.dumps({
                'memory_deleted_id':e.id,
                'status': 'ok'
            })
    else:
        return json.dumps({
                    'status': 'error'
                })



@api.route('/api/v0.1/add/events/<uuid>',methods=['POST'])
@api.route('/api/add/events/<uuid>',methods=['POST'])
def add_events(uuid):
    visual_event=EventType.query.filter(EventType.name=="visual").one()
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
    except NoResultFound:
        return json.dumps({
                'status': 'error',
                'msg':'Experience not found'
            })
    files = request.files.getlist('files')
    datetime_=datetime.datetime.now()
    for f in files:
        ana=None
        text=None
        infos=[]
        if f and allowed_file(f.filename):
            filename_ = secure_filename(f.filename)
            if not os.path.isdir(os.path.join('memories',uuid)):
                os.mkdir(os.path.join('memories',uuid))
            filename=os.path.join("memories", uuid,filename_)
            f.save(filename)


            if request.args.get('analize', '')=="true":
                analisys_info=InfoSourceType.query.filter(InfoSourceType.name=="analysis").one()
                ana=golfred.cs_img2analize(filename)
                if request.args.get('fred', '')=="true":
                    filename_pref=filename.rsplit('.',1)
                    filename_fred=filename_pref[0]+"analysis.fred"
                    fred=golfred.text2fred(ana['description']['captions'][0],filename_fred)
                    ana['fred']=fred
                pt = InfoSource(
                    json=json.dumps(ana),
                    type = analisys_info,
                    updated_at=datetime_,
                    datetime=datetime_
                    )
                infos.append(pt)


            if request.args.get('read', '')=="true":
                read_info=InfoSourceType.query.filter(InfoSourceType.name=="read").one()
                if ana:          
                    cat=golfred.getCategory(ana)
                    regions,text=golfred.cs_img2text(filename,type=cat)
                else:
                    regions,text=golfred.cs_img2text(filename,type="text_")
                if len(text)>0:
                    pt = InfoSource(
                        json=json.dumps(
                            {
                                'regions':regions,
                                'text':text
                            }
                            ),
                        updated_at=datetime_,
                        datetime=datetime_,
                        type = read_info
                        )
                    infos.append(pt)
                    total_events=Event.query.filter(Event.experience_id==exp.id).count()
            mem=Event(
                filename=filename,
                created_at=datetime.datetime.now(),
                datetime=datetime.datetime.now(),
                type=visual_event,
                experience_id=exp.id,
                infos=infos,
                order=total_events
            )
            db.session.add(mem)
            db.session.commit()
    return json.dumps({
            'status': 'ok'
            })


@api.route('/api/v0.1/update/info',methods=['POST'])
@api.route('/api/update/info',methods=['POST'])
def update_info():
    content = request.json
    try:
        eid=content['eid']
    except KeyError:
        return json.dumps({
                        'status': 'error',
                        'msg':'Request with wrong arguments'
            })
    try:
        e=Event.query.filter(Event.id==eid).one()
    except NoResultFound:
        return json.dumps({
                    'status': 'error',
                    'msg':'Event not found'
        })
    datetime_=datetime.datetime.now()
    analysis=None
    read=None
    for i in e.infos:
        if i.type.name=="analysis":
            analysis=i
        elif i.type.name=="read":
            read=i
    if content['type']=="analysis":
        if not analysis:
            analysis_info=InfoSourceType.query.filter(InfoSourceType.name=="analysis").one()
            analysis = InfoSource(
                    datetime=datetime_,
                    type = analysis_info
                )
        ana=golfred.cs_img2analize(e.filename)
        filename_pref=e.filename.rsplit('.',1)
        filename_fred=filename_pref[0]+".analysis.fred"
        fred=golfred.text2fred(ana['description']['captions'][0]['text'],filename_fred)
        ana['fred']=fred
        analysis.json=json.dumps(ana)
        analysis.updated_at=datetime_
        db.session.add(analysis)
        db.session.commit()
    elif content['type']=="read":
        if not read:
            read_info=InfoSourceType.query.filter(InfoSourceType.name=="read").one()
            read = InfoSource(
                    datetime=datetime_,
                    type = read_info
                )
        if analysis:          
            cat=golfred.getCategory(json.loads(analysis.json))
            regions,text=golfred.cs_img2text(e.filename,type=cat)
        else:
            regions,text=golfred.cs_img2text(e.filename,type="text_")
        filename_pref=e.filename.rsplit('.',1)
        filename_fred=filename_pref[0]+".read.fred"
        fred=golfred.text2fred(text,filename_fred)
        read.updated_at=datetime_
        read.json=json.dumps(
                        {
                            'regions':regions,
                            'text':text,
                            'fred':fred
                        }
                    )
        db.session.add(read)
        db.session.commit()
    return json.dumps({
            'status': 'ok'
            })




@api.route('/api/v0.1/push/event',methods=['POST'])
@api.route('/api/push/event',methods=['POST'])
def push_memory():
    content = request.json
    uuid=content['uuid']
    datetime_=datetime.datetime.now()
    if content['type']=="action":
        try:
            action_memory=EventType.query.filter(EventType.name=="action").one()
            type=content['type_action']
            command=content['command']
            args=[a.strip() for a in content['args'].split(',') if len(a.strip())>0]
            print(args)
            try:
                action_info=InfoSourceType.query.filter(InfoSourceType.name==type).one()
            except:
                action_info=InfoSourceType(name=type) 
            exp=Experience.query.filter(Experience.uuid==uuid).one()
            total_events=Event.query.filter(Event.experience_id==exp.id).count()
            mem=Event(filename="",
                created_at=datetime_,
                datetime=datetime_,
                type=action_memory,
                experience_id=exp.id,
                infos=[],
                order=total_events
            )

            pt = InfoSource(
                json=json.dumps({
                    'type':type,
                    'command': {
                            'name':command,
                            'args':args
                        }
                    }),
                type = action_info,
                updated_at=datetime_,
                datetime=datetime_,
            )
            mem.infos.append(pt)
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
   




@api.route('/api/v0.1/update/experience',methods=['POST'])
@api.route('/api/update/experience',methods=['POST'])
def update_experience():
    content = request.json
    uuid=content['uuid']
    if content['type']=="order":
        order=json.loads(content['order'])
        print(order)
        try:
            exp=Experience.query.filter(Experience.uuid==uuid).one()
        except NoResultFound:
            return json.dumps({
                        'status': 'error',
                        'message': 'Not experience found'
                    })
        try: 
            events=Event.query.filter(Event.experience_id==exp.id).all()
            for e in events:
                e.order=order[str(e.id)]
                db.session.add(e)
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
    

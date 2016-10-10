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

api = Blueprint('api',__name__,url_prefix="/api")
from golfred_service import db, g
from models import *
from sqlalchemy.orm.exc import NoResultFound
import re

version='v0.1'

@api.route('/v01',methods=['GET'])
@api.route('/',methods=['GET'])
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

@api.route('/v0.1/status',methods=['GET'])
@api.route('/status',methods=['GET'])
def status():
    total=Experience.query.count()
    return jsonify({
            'experiences':total,
            'status': 'ok'
        })

@api.route('/v0.1/list/experiences',methods=['GET'])
@api.route('/list/experiences',methods=['GET'])
def list_experiences():
    exps=Experience.query.order_by(Experience.id.desc()).all()
    exps = [l.as_dict() for l in exps]
    print(len(exps))
    return jsonify(exps)


@api.route('/latest/experiences',defaults={'n':10},methods=['GET'])
@api.route('/latest/experiences/<n>',methods=['GET'])
@api.route('/v0.1/latest/experiences',defaults={'n':10},methods=['GET'])
@api.route('/v0.1/latest/experiences/<n>',methods=['GET'])
def latest_experiences(n):
    exps=Experience.query.order_by(Experience.id.desc()).limit(n)
    exps = [l.as_dict() for l in exps]
    return json.dumps(exps)

@api.route('/v0.1/create/experience',methods=['POST'])
@api.route('/create/experience',methods=['POST'])
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
                'add_experience_id':exp.uuid,
                'status': 'ok'
                })
    else:
        return jsonify({
                    'status': 'error',
                    'msg': "Problem with post message"
                })

@api.route('/v0.1/delete/experience',methods=['POST'])
@api.route('/delete/experience',methods=['POST'])
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


@api.route('/v0.1/list/events/<uuid>',methods=['GET'])
@api.route('/list/events/<uuid>',methods=['GET'])
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

@api.route('/v0.1/delete/event',methods=['POST'])
@api.route('/delete/event',methods=['POST'])
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



@api.route('/v0.1/add/events/<uuid>',methods=['POST'])
@api.route('/add/events/<uuid>',methods=['POST'])
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
    print(files)
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


@api.route('/v0.1/update/info',methods=['POST'])
@api.route('/update/info',methods=['POST'])
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




@api.route('/v0.1/push/event',methods=['POST'])
@api.route('/push/event',methods=['POST'])
def push_memory():
    print('holla')
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
   




@api.route('/v0.1/update/experience',methods=['POST'])
@api.route('/update/experience',methods=['POST'])
def update_experience():
    content = request.json
    uuid=content['uuid']
    if content['type']=="order":
        order=json.loads(content['order'])
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
   

@api.route('/v0.1/summarize/experience/<uuid>',methods=['GET'])
@api.route('/summarize/experience/<uuid>',methods=['GET'])
def events2structure(uuid,confidence_analysis=0.3):
    res=[]
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
    except NoResultFound:
        return json.dumps({
                    'status': 'error',
                    'message': 'Not experience found'
        })
    
    try:
        es=Event.query.filter(Event.experience_id==exp.id).order_by(Event.order.asc()).all()
        loc=None
        locs=[]
        preds=[]
        for e in es:
            i=e.infos[0]
            pred_=json.loads(i.json)
            preds.append(pred_)
            # Figure out place 
            if e.type.name=='action':
                if loc==None and pred_['type']=='start':
                    res.append([])
                    loc=golfred.kb_getlocspace(g,pred_['command']['args'][0])
                    locs.append(loc)
                elif loc and pred_['type']=="move":
                    loc_=golfred.kb_getlocspace(g,pred_['command']['args'][0])
                    if not loc.eq(loc_):
                        loc=loc_
                        locs.append(loc)
                        res.append([])
                elif loc and pred_['type']=="fail":
                    if pred_['command']['name']=='move':
                        res[-1].pop()
                        locs.pop()
                        loc=locs[-1]
                elif loc and pred_['type']=='finish':
                    res.append([])

            # Generate text
            # START or new spatial reference
            if e.type.name=='action' and pred_['type']=='start':
                t,c=golfred.kb_drawtemplate(g,'start',res[-1])
                loc__=golfred.kb_getlocname(g,loc)
                res[-1].append((t.format(**{'loc':loc__}),c))
                continue
            if e.type.name=='action' and pred_['type']=='finish':
                t,c=golfred.kb_drawtemplate(g,'connect',res[-1],C="text")
                res[-1].append((t,c))
                t,c=golfred.kb_drawtemplate(g,'finish',res[-1])
                loc__=golfred.kb_getlocname(g,pred_['command']['args'][0])
                res[-1].append((t.format(**{'loc':loc__}),c))
                continue
       
            elif len(res)>0 and len(res[-1])==0:
                t,c=golfred.kb_drawtemplate(g,'connect',res[-1],C="text")
                res[-1].append((t,c))
                if e.type.name=='action':
                    t,c=golfred.kb_drawtemplate(g,pred_['command']['name'],res[-1])
                    loc__=golfred.kb_getlocname(g,loc)
                    if t:
                        f=t.format(*[loc__])+' to '+golfred.kb_getlocname(g,preds[-1]['command']['args'][0])
                        res[-1].append((f,c))
                continue 
            if e.type.name=='action' and pred_['type']=="fail":
                t,c=golfred.kb_drawtemplate(g,'fail',res[-1])
                res[-1].append((t,c))
                if e.type.name=='action':
                    t,c=golfred.kb_drawtemplate(g,preds[-2]['command']['name'],res[-1])
                    miss_loc=golfred.kb_getlocspace(g,preds[-2]['command']['args'][0])
                    loc__=golfred.kb_getlocname(g,miss_loc)
                    if t:
                        f=t.format(*[loc__])
                        res[-1].append((f,c))
                        
                res[-1].append(("but could't",None))
                continue 
            if e.type.name=='action' and pred_['type']=="move":
                res[-1].append(("then",None))
                if e.type.name=='action':
                    t,c=golfred.kb_drawtemplate(g,pred_['command']['name'],res[-1])
                    if t:
                        loc__=golfred.kb_getlocname(g,pred_['command']['args'][0])
                        f=t.format(str(loc__))
                        res[-1].append((f,c))
                continue 


            if e.type.name=='action' and pred_['type']=="manipulation":
                if e.type.name=='action':
                    t,c=golfred.kb_drawtemplate(g,pred_['command']['name'],res[-1])
                    if t:
                        f=t.format(*pred_['command']['args'])
                        res[-1].append((f,c))
                continue 

            if len(res)>0 and e.type.name=='visual':
                for i in e.infos:
                    pred_=json.loads(i.json)
         
                    t,c=golfred.kb_drawtemplate(g,i.type.name,res[-1])
                    if t:
                        ana=False
                        if i.type.name=='analysis':
                            ana=True
                            if pred_['description']['captions'][0]['confidence']>confidence_analysis:
                                f=t.format(*[pred_['description']['captions'][0]['text']])
                            else: 
                                continue
                        elif i.type.name=="read":
                            if not ana:
                                f="there "+t.format(pred_['text'])
                            else:
                                f=t.format(pred_['text'])
                        res[-1].append((f,c))
            else:
                pass
        print(res)   
        return json.dumps([[x for x,y in b] for  b in res])
    except NoResultFound:
        return json.dumps({
                    'status': 'error',
                    'message': 'Not events found'

        })
    
@api.route('/v0.1/lf/experience/<uuid>',methods=['GET'])
@api.route('/lf/experience/<uuid>',methods=['GET'])
def events2jeni(uuid,confidence_analysis=0.3):
    res=[]
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
    except NoResultFound:
        return json.dumps({
                    'status': 'error',
                    'message': 'Not experience found'
        })
    
    try:
        es=Event.query.filter(Event.experience_id==exp.id).order_by(Event.order.asc()).all()
        loc=None
        locs=[]
        preds=[]
        for e in es:
            i=e.infos[0]
            pred_=json.loads(i.json)
            print(pred_,e.type.name)
            preds.append(pred_)
            print("--------------->",res)
            # Figure out place 
            if e.type.name=='action':
                if loc==None and pred_['type']=='start':
                    res.append([])
                    loc=golfred.kb_getlocgspace(g,pred_['command']['args'][0])
                    locs.append(loc)
                elif loc and pred_['type']=="move":
                    loc_=golfred.kb_getlocgspace(g,pred_['command']['args'][0])
                    if not loc.eq(loc_):
                        loc=loc_
                        locs.append(loc)
                        res.append([])
                elif loc and pred_['type']=="fail":
                    if pred_['command']['name']=='move':
                        res[-1].pop()
                        locs.pop()
                        loc=locs[-1]
                elif loc and pred_['type']=='finish':
                    res.append([])

            # Generate text
            # START or new spatial reference
            if e.type.name=='action' and pred_['type']=='start':
                c=None
                semantics = golfred.kb_generatesemantics(g,pred_['command']['name'])
                loc__=golfred.kb_getglabel(g,pred_['command']['args'][0])
                f=semantics.format(str(loc__))
                res[-1].append((f,c))
                continue
             
            if e.type.name=='action' and pred_['type']=='finish':
                #t,c=golfred.kb_drawtemplate(g,'connect',res[-1],C="text")
                #res[-1].append((t,c))
                #t,c=golfred.kb_drawtemplate(g,'finish',res[-1])
                #loc__=golfred.kb_getlocname(g,pred_['command']['args'][0])
                #res[-1].append((t.format(**{'loc':loc__}),c))
                semantics = golfred.kb_generatesemantics(g,pred_['command']['name'])
                loc__=golfred.kb_getglabel(g,pred_['command']['args'][0])
                f=semantics.format(str(loc__))
                res[-1].append((f,c))
               
                continue
            if e.type.name=='action' and pred_['type']=="fail":
                print("------> hello")
                #t,c=golfred.kb_drawtemplate(g,'fail',res[-1])
                #res[-1].append((t,c))
                if e.type.name=='action':
                    #t,c=golfred.kb_drawtemplate(g,preds[-2]['command']['name'],res[-1])
                    semantics = golfred.kb_generatesemantics(g,pred_['command']['name'])
                    semantics+= " d:fail(e2)"
                    miss_loc=golfred.kb_getlocgspace(g,preds[-2]['command']['args'][0])
                    f=semantics.format(*[miss_loc])
                    res[-1].append((f,c))
       
            if len(res)>0 and len(res[-1])==0:
                #t,c=golfred.kb_drawtemplate(g,'connect',res[-1],C="text")
                #res[-1].append((t,c))
                if e.type.name=='action':
                    semantics=golfred.kb_generatesemantics(g,pred_['command']['name'])
                    loc__=golfred.kb_getlocgspace(g,pred_['command']['args'][0])
                    f=semantics.format(str(loc__))
                    res[-1].append((f,c))
 
                    #loc__=golfred.kb_getlocname(g,loc)
                    #if t:
                    #    f=t.format(*[loc__])+' to '+golfred.kb_getlocname(g,preds[-1]['command']['args'][0])
                    #    res[-1].append((f,c))
                continue 
                       
                #res[-1].append(("but could't",None))
                continue 
            if e.type.name=='action' and pred_['type']=="move":
                #res[-1].append(("then",None))
                c=None
                if e.type.name=='action':
                    semantics = golfred.kb_generatesemantics(g,pred_['command']['name'])
                    loc__=golfred.kb_getglabel(g,pred_['command']['args'][0])
                    f=semantics.format(str(loc__))
                    res[-1].append((f,c))
                continue

            if e.type.name=='action' and pred_['type']=="manipulation":
                if e.type.name=='action':
                    semantics = golfred.kb_generatesemantics(g,pred_['command']['name'])
                    f=semantics.format(*pred_['command']['args'])
                    res[-1][-1]=res[-1][-1][0].replace(u'e2',u'e1'),None
                    res[-1][-1]=res[-1][-1][0]+' z:before(e1 e2) ',None
                    res[-1][-1]=res[-1][-1][0]+f,None
                continue 

            if len(res)>0 and e.type.name=='visual':
                for i in e.infos:
                    pred_=json.loads(i.json)
         
                    t,c=golfred.kb_drawtemplate(g,i.type.name,res[-1])
                    if t:
                        ana=False
                        #if i.type.name=='analysis' and i.type.name=="read":
                        #    ana=True
                        #    if pred_['description']['captions'][0]['confidence']>confidence_analysis:
                        #    else: 
                        #        continue
                    
                        #if i.type.name=='analysis':
                        #    ana=True
                        #    if pred_['description']['captions'][0]['confidence']>confidence_analysis:
                        #        f=t.format(*[pred_['description']['captions'][0]['text']])
                        #    else: 
                        #        continue
                        if i.type.name=="read":
                            text=cleanning(pred_['text'])
                            semantics="ik:i(j) i:Experiencer(e2 j) a:visual(u) u:{0}({1}) i:Stimulus(e2 u) i:see(e2)".format(
                                    text,
                                    abbreviation(text))
                            res[-1].append((semantics,c))
            else:
                pass
        #print(res)   
        f=open("jeni/"+uuid+'.jeni','w')
        c=0
        for segment in res:
            for semantics,n in segment:
                print("id_{0}".format(c),file=f)
                print("semantics:[{0}]".format(semantics),file=f)
                print("",file=f)
                c+=1
        f.close()
        phrases=golfred.jeni(uuid)
        print(phrases)
        return json.dumps([[x for x,y in b] for  b in res])
    except NoResultFound:
        return json.dumps({
                    'status': 'error',
                    'message': 'Not events found'

        })
    

def abbreviation(text):
    t=[]
    for l in text.split("_"):
        if len(l)>0:
            t.append(l[0].lower())
    return "".join(t)

def cleanning(text):
    text=text.replace(" ","_")
    text=text.replace("&","")
    text=text.replace("-","")
    text=text.replace(":","")
    text=text.replace(".","")
    return text

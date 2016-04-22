#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Golfred interface
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

import os
from subprocess import Popen, PIPE, STDOUT
import httplib, urllib, base64
import keys
import json
import fredlib
import random
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef

ns=Namespace('http://golfred.com/')



headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': keys.KEY_CONGITIVE_SERVICES,
}

params_ocr = urllib.urlencode({
    # Request parameters
    'language': 'en'
})

params_analize = urllib.urlencode({
    # Request parameters
    'language': 'unk',
    'visualFeatures': 'Categories,Tags,Description',
    'detectOrientation ': 'true',
})



CMD=['./example_text_end_to_end_recognition']

def create_new_experience(dirname,id_experience):
    os.mkdir(os.path.join(dirname,id_experience))
    return True

def check_experience(dirname,id_experience):
    os.path.isdir(dirname,id_experience)
    return True

def recover_experiences(dirname):
    experiences={}
    if os.path.isdir(dirname):
        for id_experience in os.listdir(dirname):
            memories=os.listdir(os.path.join(dirname,id_experience))
            memories=[m for m in memories if m.endswith('.jpg')]
            experiences[id_experience]=memories
    return experiences

def recover_visual_memories(dirname,id_experience):
    if os.path.isdir(os.path.join(dirname,id_experience)):
        memories=os.listdir(os.path.join(dirname,id_experience))
        memories=[m for m in memories if m.endswith('.jpg')]
        return memories
    else:
        return False


def img2text(imgfile):
    cmd=CMD+[imgfile]
    p = Popen(cmd,  stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return stdout.splitlines()

def cs_img2text(imgfile,type="text"):
        try:
            data = open(imgfile, 'rb').read()
            conn = httplib.HTTPSConnection('api.projectoxford.ai')
            conn.request("POST", "/vision/v1.0/ocr?%s" % params_ocr, data, headers)
            response = conn.getresponse()
            text = json.loads(response.read())
            regions = [[" ".join([w['text'] for w in l['words']])   for  l in   r['lines']] for r in  text['regions']]
            conn.close()
            if type=="text_":
                text=[]
                flag=False
                for ls in regions:
                    for l in ls:
                        if re.match('^\D+$',l):
                            text.append(l)
                            flag=True
                            break
                    if flag:
                        break
                text=" ".join(text)
            else:
            #if type=="sign" or type =="others_":
                text=[]
                for ls in regions:
                    for l in ls:
                        if re.match('^\D+$',l):
                            text.append(l)
                text=" ".join(text)
            return regions,text
        except Exception as e:
            return  None,None


def cs_img2analize(imgfile):
        try:
            data = open(imgfile, 'rb').read()
            conn = httplib.HTTPSConnection('api.projectoxford.ai')
            conn.request("POST", "/vision/v1.0/analyze?%s" % params_analize, data, headers)
            response = conn.getresponse()
            ana = json.loads(response.read())
            conn.close()
            return ana
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            return  ""


import re
re_fred="^."


def text2fred(text,outputfile):
        g=fredlib.getFredGraph(fredlib.preprocessText(text),outputfile)
        nodes=[]
        for n in g.getNodes():
            #nodes.append(re_fred.sub("",str(n)))
            pass
        return  json.dumps(nodes)

def text2tipalo(line):
    try:
        conn = httplib.HTTPSConnection('wit.istc.cnr.it')
        conn.request("GET", "/tipalo?resource=http://en.wikipedia.org/wiki/%s" %line.replace(" ","_"))
        response = conn.getresponse()
        ans = json.loads(response.read())
        return ans
    except Exception as e:
        print("[Errno]")
        return  ana



def getCategory(analysis):
    try:
        score=0.0
        catM=None
        for cat in analysis['categories']:
            if cat['score']>score:
                catM=cat['name']
                score=cat['score']
        return catM
    except KeyError:
        return None


def kb_getlocspace(g,p):
    qres=g.query(
        "SELECT ?label WHERE {{ ?p go:label '{0}' . ?p go:inside ?loc . ?loc go:label ?label .}}".format(p),
        initNs={'go':ns})
    loc=None
    for r in qres:
        loc=r
        break
    return loc[0]

def kb_getlocname(g,p):
    qres=g.query(
        "SELECT ?locname ?type WHERE {{ ?p go:label '{0}' . ?p go:name ?locname . ?p go:type ?type .}}".format(p),
        initNs={'go':ns})
    for r in qres:
        loc=r[0]
        t=r[1]
        break
    qres=g.query(
        "SELECT ?p WHERE {{ ?p go:type '{0}' .}}".format(str(t)),
        initNs={'go':ns})
    if len(qres)==1:
        return "the "+loc
    if len(qres)==0:
        return "an unknown location"
    if len(qres)>1:
        return "a "+loc

def kb_drawtemplate(g,l,curr,C="text-past"):
    if len(curr)>0:
        if curr[-1][1]:
            C=curr[-1][1]

    qres=g.query(
        "SELECT ?template ?w WHERE {{ ?e go:label '{0}' . ?e go:template ?t . ?t go:{1} ?template . ?t go:weight ?w . }}".format(l,C),
        initNs={'go':ns})

    labels=[]
    for t,w in qres:
        for w in range(int(w)):
            labels.append(t)

    qres=g.query(
        "SELECT ?c WHERE {{ ?e go:label '{0}' . ?e go:template ?t . ?t go:constraint ?c . }}".format(l),
        initNs={'go':ns})

    C=None
    if len(qres)>0:
        for r in qres:
            C=str(r[0])
            break


    if len(labels)>0:
        return str(random.choice(labels)),C
    else:
        return None,C



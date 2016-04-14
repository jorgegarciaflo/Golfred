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

headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': keys.KEY_CONGITIVE_SERVICES,
}

params_ocr = urllib.urlencode({
    # Request parameters
    'visualFeatures': 'Categories'
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

def cs_img2text(imgfile):
        data = open(imgfile, 'rb').read()
        try:
            conn = httplib.HTTPSConnection('api.projectoxford.ai')
            conn.request("POST", "/vision/v1.0/ocr?%s" % params_ocr, data, headers)
            response = conn.getresponse()
            text = json.loads(response.read())
            regions = [[" ".join([w['text'] for w in l['words']])   for  l in   r['lines']] for r in  text['regions']]
            conn.close()
            print(regions)
            return regions
        except Exception as e:
            print("[Errno {0}] {1}".format(e.errno, e.strerror))
            return  []

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


def text2fred(line,outputfile):
    try:
        g=fredlib.getFredGraph(fredlib.preprocessText(line),outputfile)
        nodes=[]
        print(line)
        for n in g.getNodes():
            nodes.append(re_fred.sub("",str(n)))
            print(nodes[-1])
        return  json.dumps(nodes)
    except Exception as e:
        print("[Errno]")
        return  ""

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



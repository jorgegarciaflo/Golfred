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


headers = {
    # Request headers
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': keys.KEY_CONGITIVE_SERVICES,
}

params = urllib.urlencode({
    # Request parameters
    'language': 'unk',
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
        data = open(os.path.join('src',imgfile[1:]), 'rb').read()
        conn = httplib.HTTPSConnection('api.projectoxford.ai')
        conn.request("POST", "/vision/v1.0/ocr?%s" % params, data, headers)
        response = conn.getresponse()
        text = json.loads(response.read())
        regions = [[" ".join([w['text'] for w in l['words']])   for  l in   r['lines']] for r in  text['regions']]
        conn.close()
        return regions



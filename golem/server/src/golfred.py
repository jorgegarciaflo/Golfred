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


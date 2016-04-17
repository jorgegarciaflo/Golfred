#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Initialization of database for ironylabeller
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2015/iimas/unam
# ----------------------------------------------------------------------

import sys
import argparse
from golfred import db
from golfred.models import *


if __name__ == '__main__':
    p = argparse.ArgumentParser("initdbgolfred")
    p.add_argument("-f","--force",default=False,
            action="store_true", dest="force",
            help="Creates new database [admin]")
 
    db.create_all()
    db.session.commit()
    mt=EventType(name="visual")
    db.session.add(mt)
    mt=EventType(name="action")
    db.session.add(mt)
    pt=InfoSourceType(name="read")
    db.session.add(pt)
    pt=InfoSourceType(name="analysis")
    db.session.add(pt)
    pt=InfoSourceType(name="fred")
    db.session.add(pt)
    db.session.commit()
    

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
from golfred_service import db
from models import *


if __name__ == '__main__':
    p = argparse.ArgumentParser("initdbgolfred")
    p.add_argument("-f","--force",default=False,
            action="store_true", dest="force",
            help="Creates new database [admin]")
 
    from models import *
    db.create_all()
    db.session.commit()
    mt=MemoryType(name="visual")
    db.session.add(mt)
    db.session.commit()
    





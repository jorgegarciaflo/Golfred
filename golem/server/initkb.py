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
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import DC, FOAF
import pickle

ns=Namespace('http://golfred.com')

def add_people(g,name,organization):
    ivan=BNode()
    g.add((ivan,RDF.type,FOAF.person))
    g.add((ivan,FOAF.name,Literal("Ivan Vladimir Meza Ruiz")))
    g.add((ivan,ns['words'],organization))


if __name__ == '__main__':
    p = argparse.ArgumentParser("initdbgolfred")
    p.add_argument("-f","--force",default=False,
            action="store_true", dest="force",
            help="Creates new database [admin]")
 
    g = Graph()
    dcc=BNode()
    g.add((dcc,RDF.type,FOAF.orgnization))
    g.add((dcc,FOAF.name,Literal("Computer Science Departament")))
    add_people(g,'Ivan Vladimir Meza Ruiz',dcc)
    add_people(g,'Dr. Ernesto Bribiesca',dcc)
    add_people(g,'Dr. Ernesto Bribiesca',dcc)
    g.serialize(destination='golfred/golfred.nt', format='nt')











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
ns=Namespace('http://golfred.com/')

def add_people(g,name,organization):
    person=BNode()
    g.add((person,RDF.type,FOAF.person))
    g.add((person,FOAF.name,Literal("Ivan Vladimir Meza Ruiz")))
    g.add((person,ns['works'],organization))


if __name__ == '__main__':
    p = argparse.ArgumentParser("initdbgolfred")
    p.add_argument("-f","--force",default=False,
            action="store_true", dest="force",
            help="Creates new database [admin]")
 
    g = Graph()
    dcc=BNode()
    g.add((dcc,RDF.type,FOAF.orgnization))
    g.add((dcc,FOAF.name,Literal("Computer Science Departament")))


    p1=BNode()
    p2=BNode()
    p3=BNode()
    p5=BNode()
    p6=BNode()
    p7=BNode()
    p8=BNode()
    
    
    hall=BNode()
    g.add((hall,ns['name'],Literal('hall')))
    g.add((hall,ns['label'],Literal('hall')))
    g.add((hall,ns['type'],Literal('hall')))
    office1=BNode()
    g.add((office1,ns['name'],Literal("office of Ernesto")))
    g.add((office1,ns['type'],Literal('officee')))
    g.add((office1,ns['label'],Literal('officee')))
    office2=BNode()
    g.add((office2,ns['name'],Literal("office of Ivan")))
    g.add((office2,ns['type'],Literal('officei')))
    g.add((office2,ns['label'],Literal('officei')))
    meetingroom=BNode()
    g.add((meetingroom,ns['name'],Literal("meeting room")))
    g.add((meetingroom,ns['type'],Literal('room')))
    g.add((meetingroom,ns['label'],Literal('room')))
    lab=BNode()
    g.add((lab,ns['name'],Literal("laboratory")))
    g.add((lab,ns['type'],Literal('laboratory')))
    g.add((lab,ns['label'],Literal('laboratory')))

    g.add((p1,ns['inside'],hall))
    g.add((p1,ns['label'],Literal('p1')))
    g.add((p1,ns['name'],Literal('sign')))
    g.add((p1,ns['type'],Literal('point')))
    g.add((p2,ns['inside'],office1))
    g.add((p2,ns['label'],Literal('p2')))
    g.add((p2,ns['name'],Literal('desk')))
    g.add((p2,ns['type'],Literal('point')))
    g.add((p3,ns['inside'],office2))
    g.add((p3,ns['label'],Literal('p3')))
    g.add((p3,ns['name'],Literal('desk')))
    g.add((p3,ns['type'],Literal('point')))
    g.add((p5,ns['inside'],office2))
    g.add((p5,ns['label'],Literal('p5')))
    g.add((p5,ns['type'],Literal('point')))
    g.add((p5,ns['name'],Literal('desk')))
    g.add((p6,ns['inside'],meetingroom))
    g.add((p6,ns['label'],Literal('p6')))
    g.add((p6,ns['type'],Literal('point')))
    g.add((p6,ns['name'],Literal('table')))
    g.add((p7,ns['inside'],meetingroom))
    g.add((p7,ns['label'],Literal('p7')))
    g.add((p7,ns['name'],Literal('door')))
    g.add((p7,ns['type'],Literal('point')))
    g.add((p8,ns['inside'],lab))
    g.add((p8,ns['label'],Literal('p8')))
    g.add((p8,ns['name'],Literal('desk')))
    g.add((p8,ns['type'],Literal('point')))

    add_people(g,'Ivan Vladimir Meza Ruiz',dcc)
    add_people(g,'Dr. Ernesto Bribiesca',dcc)

    
    event=BNode()
    g.add((event,ns['label'],Literal("start")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i woke up at {loc}")))
    g.add((template,ns['text-inf'],Literal("to wake up at {loc}")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i started at {loc}")))
    g.add((template,ns['text-inf'],Literal("to start at {loc}")))
    g.add((template,ns['weight'],Literal(2)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i begun at {loc}")))
    g.add((template,ns['text-inf'],Literal("to begin at {loc}")))
    g.add((template,ns['weight'],Literal(2)))


    event=BNode()
    g.add((event,ns['label'],Literal("finish")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i turn myself off")))
    g.add((template,ns['text-inf'],Literal("to turn myself off")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i stopped")))
    g.add((template,ns['text-inf'],Literal("to stop")))
    g.add((template,ns['weight'],Literal(2)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i finished")))
    g.add((template,ns['text-inf'],Literal("to finish")))
    g.add((template,ns['weight'],Literal(2)))


    event=BNode()
    g.add((event,ns['label'],Literal("connect")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text'],Literal("after that")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text'],Literal("afterwards")))
    g.add((template,ns['weight'],Literal(1)))

    event=BNode()
    g.add((event,ns['label'],Literal("move")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i went to {0}")))
    g.add((template,ns['text-inf'],Literal("to go to {0}")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i moved to {0}")))
    g.add((template,ns['text-inf'],Literal("to move to {0}")))
    g.add((template,ns['weight'],Literal(2)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i walked towards {0}")))
    g.add((template,ns['text-inf'],Literal("to walk towards {0}")))
    g.add((template,ns['weight'],Literal(2)))


    event=BNode()
    g.add((event,ns['label'],Literal("fail")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i tried")))
    g.add((template,ns['text-inf'],Literal("to try")))
    g.add((template,ns['constraint'],Literal("text-inf")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i was supposed")))
    g.add((template,ns['text-inf'],Literal("to be suppose")))
    g.add((template,ns['constraint'],Literal("text-inf")))
    g.add((template,ns['weight'],Literal(2)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i wanted")))
    g.add((template,ns['text-inf'],Literal("to want")))
    g.add((template,ns['constraint'],Literal("text-inf")))
    g.add((template,ns['weight'],Literal(2)))



    event=BNode()
    g.add((event,ns['label'],Literal("analysis")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i saw {0}")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("there was {0}")))
    g.add((template,ns['weight'],Literal(2)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i noticed  {0}")))
    g.add((template,ns['weight'],Literal(2)))

    event=BNode()
    g.add((event,ns['label'],Literal("read")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i read it said {0}")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("it said {0}")))
    g.add((template,ns['weight'],Literal(2)))




    event=BNode()
    g.add((event,ns['label'],Literal("take")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i took a {0}")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i grabbed a {0}")))
    g.add((template,ns['weight'],Literal(2)))

    event=BNode()
    g.add((event,ns['label'],Literal("drop")))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i leaved the {0}")))
    g.add((template,ns['weight'],Literal(1)))
    template=BNode()
    g.add((event,ns['template'],template))
    g.add((template,ns['text-past'],Literal("i dropped the {0}")))
    g.add((template,ns['weight'],Literal(2)))




    g.serialize(destination='golfred/golfred.nt', format='nt')











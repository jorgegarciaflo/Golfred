#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Models for experiences
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2016/iimas/unam
# ----------------------------------------------------------------------

from golfred_service import db
import json

class Experience(db.Model):
    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)

    name          = db.Column(db.String(50), nullable=False)
    uuid          = db.Column(db.String(15), nullable=False)
    description   = db.Column(db.Text())
    created_at    = db.Column(db.DateTime())
    datetime      = db.Column(db.DateTime())
    protected     = db.Column(db.Boolean(False))

    def as_dict(self):
        return {
                'name'       :self.name,
                'uuid'       :self.uuid,
                'description':self.description,
                'created_at' :str(self.created_at),
                'datetime'   :str(self.datetime),
                'protected'  :str(self.protected),
                }


class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    order       = db.Column(db.Integer)
    filename    = db.Column(db.String(550), nullable=False)
    created_at  = db.Column(db.DateTime())
    datetime    = db.Column(db.DateTime())
    # Relationships
    typeid      = db.Column(db.Integer, db.ForeignKey('event_type.id'))
    type        = db.relationship("EventType")
    experience_id = db.Column(db.Integer, db.ForeignKey('experience.id'))
    infos       = db.relationship("InfoSource")

    def as_dict(self):
        return {
                'id':self.id,
                'filename':self.filename,
                'created_at':str(self.created_at),
                'datetime':str(self.datetime),
                'type': self.type.name,
                'infos': [p.as_dict() for p in self.infos]
                }
    

class EventType(db.Model):
    __tablename__ = 'event_type'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), nullable=False)

    def as_dict(self):
        return {
                'id':self.id,
                'name':self.name,
                }

class InfoSource(db.Model):
    __tablename__  = 'info'
    id = db.Column(db.Integer, primary_key=True)
    json           = db.Column(db.Text())
    typeid         = db.Column(db.Integer, db.ForeignKey('info_type.id'))
    type           = db.relationship("InfoSourceType")
    event_id       = db.Column(db.Integer, db.ForeignKey('event.id'))
    updated_at      = db.Column(db.DateTime())
    datetime       = db.Column(db.DateTime())
    def as_dict(self):
        return {
                'id':self.id,
                'json': self.json,
                'type': self.type.name,
                'updated_at': str(self.updated_at),
                'datetime': str(self.datetime)
                }


class InfoSourceType(db.Model):
    __tablename__ = 'info_type'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), nullable=False)

    def as_dict(self):
        return {
                'id':self.id,
                'name':self.name,
                }


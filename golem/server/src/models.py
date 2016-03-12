#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Models for experiences
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 20156/iimas/unam
# ----------------------------------------------------------------------

from golfred_service import db

class Experience(db.Model):
    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)

    name        = db.Column(db.String(50), nullable=False)
    uuid        = db.Column(db.String(15), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    created_at  = db.Column(db.DateTime())
    modified_at = db.Column(db.DateTime())

    def as_dict(self):
        return {
                'name':self.name,
                'uuid':self.uuid,
                'description':self.description,
                'created_at':str(self.created_at),
                'modified_at':str(self.modified_at)
                }

class MemoryType(db.Model):
    __tablename__ = 'memory_type'
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(10), nullable=False)

    def as_dict(self):
        return {
                'id':self.id,
                'name':self.name,
                }


class Memory(db.Model):
    __tablename__ = 'memory'
    id = db.Column(db.Integer, primary_key=True)

    filename    = db.Column(db.String(550), nullable=False)
    added_at    = db.Column(db.DateTime())
    modified_at = db.Column(db.DateTime())
    expid       = db.Column(db.Integer, db.ForeignKey('experience.id'))
    typeid      = db.Column(db.Integer, db.ForeignKey('memory_type.id'))

    def as_dict(self):
        return {
                'id':self.id,
                'filename':self.filename,
                'added_at':str(self.added_at),
                'modified_at':str(self.modified_at)
                }


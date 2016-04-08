#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Golfred interface
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2016/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import Flask, request, Blueprint, render_template, send_from_directory
from werkzeug import secure_filename
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired
import golfred
import json
import argparse
import uuid
import os
from models import Experience
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.exc import NoResultFound

# FORMS
class ExperienceForm(Form):
    name         = StringField('Name', validators=[DataRequired()])
    description  = TextAreaField('Description', validators=[DataRequired()])


class MemoryForm(Form):
    file        = FileField('Image', validators=[DataRequired()])

# WEB
web = Blueprint('web',__name__)

@web.route('/up',methods=['GET'])
def service_running():
    return "Service up!" 

@web.route('/',methods=['GET'])
def index():
    form = ExperienceForm()
    return render_template("main_menu.html",form=form)


@web.route('/memory/<uuid>',methods=['GET'])
def add_memory(uuid):
    form = MemoryForm()
    if uuid and\
       len(uuid)>0:
            try:
                exp=Experience.query.filter(Experience.uuid==uuid).one()
                return render_template("memory.html",exp=exp,form=form)
            except NoResultFound:
                return render_template("error.html",msg="No experience found with that id: "+uuid)
    else:
        return render_template("error.html",msg="No experience found with id: "+uuid)

@web.route('/explore/<uuid>',methods=['GET'])
def explore_memory(uuid):
    form = MemoryForm()
    if uuid and\
       len(uuid)>0:
            try:
                exp=Experience.query.filter(Experience.uuid==uuid).one()
                return render_template("explore_memory.html",exp=exp,form=form)
            except NoResultFound:
                return render_template("error.html",msg="No experience found with that id: "+uuid)
    else:
        return render_template("error.html",msg="No experience found with id: "+uuid)

@web.route('/memories/<uuid>/<filename>')
def uploaded_file(uuid,filename):
    return send_from_directory(
        os.path.join('memories',uuid),filename)


@web.errorhandler(404)
def page_not_found(e):
    return render_template('error.html',msg="Page not found"), 404


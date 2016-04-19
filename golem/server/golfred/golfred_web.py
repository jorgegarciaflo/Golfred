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

# WEB
web = Blueprint('web',__name__)

@web.route('/up',methods=['GET'])
def service_running():
    return "Service up!" 

@web.route('/',methods=['GET'])
def index():
    return render_template("main_menu.html")


@web.route('/edit/experience/<uuid>',methods=['GET'])
def edit_experience(uuid):
    try:
        exp=Experience.query.filter(Experience.uuid==uuid).one()
        return render_template("edit_experience.html",exp=exp)
    except NoResultFound:
        return render_template("error.html",msg="No experience found with that id: "+uuid)

@web.route('/visualize/experience/<uuid>',methods=['GET'])
def visualize_experience(uuid):
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


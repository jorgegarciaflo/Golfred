#!/usr/bin/env python
# -*- coding: utf-8
# ----------------------------------------------------------------------
# Golfred interface
# ----------------------------------------------------------------------
# Ivan Vladimir Meza-Ruiz/ ivanvladimir at turing.iimas.unam.mx
# 2016/IIMAS/UNAM
# ----------------------------------------------------------------------
from __future__ import print_function

from flask import Flask, request, Blueprint, render_template
from werkzeug import secure_filename
from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import golfred
import json
import argparse
import uuid
import os

# FORMS
class ExperienceForm(Form):
    name        = StringField('Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    save        = SubmitField(u"Create")
    cancel      = SubmitField(u"Cancel")

# WEB
web = Blueprint('web',__name__)

@web.route('/up',methods=['GET'])
def service_running():
    return "Service up!" 

@web.route('/',methods=['GET'])
def index():
    return render_template("main_menu.html")

@web.route('/create',methods=['GET','POST'])
def create():
    form = ExperienceForm()
    if form.cancel.data:
        return redirect(url_for('.index'))
    if form.validate_on_submit():
        pass    
        
    return render_template('create.html', form=form)

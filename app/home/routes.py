# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app.base.models import Response
from app.home import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app import login_manager
from jinja2 import TemplateNotFound
import json


@blueprint.route('/index')
@login_required
def index():
    
    if not current_user.is_authenticated:
       return redirect(url_for('base_blueprint.login'))

    return render_template('index.html')

@blueprint.route('/<template>')
def route_template(template):

    if not current_user.is_authenticated:
       return redirect(url_for('base_blueprint.login'))

    try:
        if template == 'responses':
            allResponses = Response.query.all()
            csvValues = [str(res) for res in allResponses]
            if len(allResponses) > 0:
                csvValues.insert(0, allResponses[0].getHeaders())
            newLineSeperator = r"\n"
            csvString = newLineSeperator.join(csvValues)

            return render_template(template + '.html', user_responses=allResponses, csvContent=csvString)
        return render_template(template + '.html')

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500

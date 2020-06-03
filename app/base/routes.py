# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from json import loads
from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager, Verified
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User, Response, MobileUser

from app.base.util import verify_pass

@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/error-<error>')
def route_errors(error):
    return render_template('errors/{}.html'.format(error))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'login/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'login/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/create_user', methods=['GET', 'POST'])
def create_user():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'login/register.html', msg='Username already registered', form=create_account_form)

        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'login/register.html', msg='Email already registered', form=create_account_form)

        verified = Verified.query.filter_by(email=email).first()
        if not verified:
            return render_template( 'login/register.html', msg='Email not verified', form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template( 'login/register.html', msg='User created please <a href="/login">login</a>', form=create_account_form)

    else:
        return render_template( 'login/register.html', form=create_account_form)

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/get_token')
def get_token():
    user = MobileUser()
    db.session.add(user)
    db.session.commit()
    token = user.encode_auth_token()
    return jsonify({
        "token": token
    })

@blueprint.route('/refresh_token')
def refresh_token():
    try:
        token = request.headers['authorization'].split()[1] # authorization: bearer <token_here>
        id = MobileUser.decode_auth_token(token)
        if id < 0:
            return "error"
        else:
            user = MobileUser.query.filter_by(id=id).first()
            if user:
                return user.encode_auth_token() if not user.isBanned else "error"
            else:
                return "error"
    except:
        return "error"

@blueprint.route('/response', methods=['POST'])
def create_response():
    response = Response(**request.get_json())
    db.session.add(response)
    db.session.commit()
    return jsonify({
        'data': True
    })
    # try:
    #     token = request.headers['Authorization'].split()[1] # authorization: bearer <token_here>
    #     id = MobileUser.decode_auth_token(token)
    #     print(id)
    #     if id < 0:
    #         return "error1"
    #     else:
    #         print(id)
    #         user = MobileUser.query.filter_by(id=id).first()
    #         if user:
    #             if not user.isBanned:
    #                 user.sent += 1
    #                 response = Response(**request.get_json())
    #                 db.session.add(user)
    #                 db.session.add(response)
    #                 db.session.commit()
    #                 return "success"
    #             else:
    #                 return "error2"
    #         else:
    #             return "error3"
    # except:
    #     return "error4"a

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('errors/403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='GET':
        return render_template('login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        user = Users.query.filter_by(username=username).first()
        if not user:
            user = Users.query.filter_by(email=username).first()
        if not user:
            flash('This username/email is not registered. Please sign up.')
            return redirect(url_for('auth.signup'))
        if not check_password_hash(user.password, password):
            flash('Incorrect password. Please try again.')
            return redirect(url_for('auth.login'))
        login_user(user, remember=remember)
        return redirect(url_for('main.profile'))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html')
    else:
        name = request.form.get('name')
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        user = Users.query.filter_by(email=email).first()
        if user:
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))
        user = Users.query.filter_by(username=username).first()
        if user:
            flash('Username already exists')
            return redirect(url_for('auth.signup'))
        new_user = Users(email=email, name=name, username=username, password=generate_password_hash(password, method='sha256'))
        db.session.add(new_user)
        db.session.commit()

        message = Mail(
                from_email='aashishcher1@gmail.com',
                to_emails=email,
                subject='Thank you!',
                html_content="This email message has been sent to confirm that you have successfully set up an account on the Alzheimer's Disease Progression Tracker!")
        
        try:
            sg = SendGridAPIClient('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')
            reponse = sg.send(message)
        except Exception as e:
            print(e.message)

        return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

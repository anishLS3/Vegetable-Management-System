import logging
from flask import render_template, url_for, flash, redirect, request, Blueprint, session
from flask_login import login_user, current_user, logout_user
from DeliverySystem import bcrypt
from DeliverySystem.models import User, Admin
from DeliverySystem.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                       RequestResetForm, ResetPasswordForm)
from DeliverySystem.users.utils import send_reset_email

users = Blueprint('users', __name__)

@users.route("/register", methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = Admin(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        user.save()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('users.login'))

    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    session.permanent = True 
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            print('User logged in successfully. Session set:', session.get('logged_in'))
            logging.debug('User logged in successfully. Session set: %s', session.get('logged_in'))
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.shop'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('email', None)
    session.pop('logged_in', None)
    return redirect(url_for('main.home'))


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RequestResetForm()

    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('users.login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    
    form = ResetPasswordForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        user.save(hashed_password)
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title='Reset Password', form=form)

from flask import Blueprint, request, redirect, url_for
from flask.helpers import flash
from flask.json import jsonify
from flask.templating import render_template
from .models import User
from flask_login import login_user, login_required, logout_user, current_user
from .libs import *
from . import Message, mail_address, mail, error_msg
from cryptography.fernet import Fernet, InvalidToken
auth = Blueprint('auth', __name__)
from os import environ
key = b'MBhXXKYm-qf2Li5EYsi4uPUeUcuehuafxED0PZ8Fhew='

def encrypt(text, is_byte=False):
    if not is_byte:
        text = text.encode()
    f = Fernet(key)
    encrypted = f.encrypt(text)
    v =  encrypted.decode()
    return v

def decrypt(text, is_byte=False):
    if not is_byte:
        text = text.encode()
    f = Fernet(key)
    decrypted = f.decrypt(text)
    v =  decrypted.decode()
    return v

def send_mail(email, otp, username):
    msg = Message(subject="(no-reply) Xandee API Email confirmation", recipients=[email],
    sender=mail_address)
    msg.body = f'Hello {username}\nYour account with Xandee API services has been created\nUse the verification code below to confirm your email address\n\n        {otp}'
    mail.send(msg)



def has_special_chars(txt):
    for i in txt:
        if i in "1 2 3 4 5 6 7 8 9 0 ! @ # $ % ^ & * ( ) , .".split():
            return True
    return False

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get('email').lower()
        password = request.form.get('password')
        remember = request.form.get('remember')
        remember = True if remember else False
        user = User.query.filter_by(email=email).first()
        if user:
            if hash_password(password, user.salt) == user.password:
                flash('Successfully logged in!', category='success')
                if user.email_confirmed:
                    login_user(user, remember=remember)
                    return redirect(url_for("views.manage")) 
                else:
                    return redirect(url_for("auth.verify", link=encrypt(user.username)))
            else:
                flash('Incorrect email or password', category='danger')
        else:
            flash('Incorrect email or password', category='danger')
    return render_template('login.html', user=current_user)


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email').lower()
        username = request.form.get('user_name')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        user = User.query.filter_by(email=email).first()
        has_username = User.query.filter_by(username=username).first()
        error = False
        if user:
            flash("Email already exists", category='danger')
            error = True
        if has_username:
            if has_username.username.lower() == username.lower():
                flash("Username already exists", category='danger')
                error = True
        if len(username) < 4:
            flash("Username is too short", category='danger')
            error = True
        if password1 != password2:
            flash("Passwords have to be thesame", category='danger')
            error = True
        if len(password1) < 7:
            flash("Password is too short", category='danger')
            error = True
        if not has_special_chars(password1):
            flash("Password should have at least a number or special characters like ! @ # $ % ^ & * ( ) , .", category='danger')
            error = True
        if not error:
            otp = str(randint(100000, 999999))
            salt = gen_salt()
            new_user = User(email=email, 
                        username=username,
                        salt=salt, password=hash_password(password1, salt), 
                        member=False, time_created=floor(time()),
                        email_confirmation_sent_on=time(), otp=otp)
            db.session.add(new_user)
            db.session.commit()
            send_mail(email, otp, username)
            return redirect(url_for('auth.verify', link=encrypt(username)))
    return render_template('sign-up.html', user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/verify/<link>', methods=['GET', 'POST'])
def verify(link):
    if request.method == "POST":
        remember = request.form.get('remember')
        remember = True if remember else False
        otp = request.form.get('otp')
        link = request.form.get('link')
        try:
            u = decrypt(link)
        except:
            return redirect(url_for('auth.login'))
        user = User.query.filter_by(username=u).first_or_404()
        if user:
            if user.email_confirmed:
                return "<h1 align='center'>You have already verified your email</h1><br><h3>Go to your <a href='/manage'>dashboard</a></h3>"
            elif user.email_confirmation_sent_on-time() > 600:
                flash("OTP code is expired and your account is deleted. You have to register again", category='danger')
                db.session.delete(user)
                db.session.commit()
            elif otp == user.otp:
                user.email_confirmed = True
                time_created=floor(time())
                db.session.commit()
                login_user(user, remember=remember)
                flash("Email verified successfully!!", category='success')
                return redirect(url_for('views.manage'))
            else:
                flash("Wrong OTP code. Try again", category='danger')
        else:
            return error_msg
    if request.method == "GET":
        try:
            username = decrypt(link)
        except InvalidToken:
            return error_msg
        user = User.query.filter_by(username=username).first_or_404()
        if user.email_confirmed:
            return "<h1 align='center'>You have already verified your email</h1><br><h3 align='center'>Go to your <a href='/manage'>dashboard</a></h3>"
    flash("OTP has been sent", category='success')
    return render_template('verify.html', user=current_user, link=link)

@auth.route('/resend-otp', methods=['POST'])
def resend_otp():
    data = loads(request.data)
    link = data['link']
    try:
        u = decrypt(link)
    except InvalidToken:
        return redirect(url_for('auth.login'))
    user = User.query.filter_by(username=u).first()
    if user:
        otp = user.otp = str(randint(100000, 999999))
        db.session.commit()
        send_mail(user.email, otp)
        return jsonify({})
    return redirect(url_for('auth.login'))

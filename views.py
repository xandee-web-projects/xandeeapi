from hashlib import md5
from flask import Blueprint, render_template, jsonify, request
from flask.helpers import flash, url_for
from flask_login import login_required,  current_user
from werkzeug.utils import redirect
from .models import File, User
from .libs import *
import flask.json as js
from os import environ
from . import error_msg
views = Blueprint('views', __name__)

def validate_json(txt):
    try:
        js.loads(txt)
    except ValueError:
        return False
    return True

@views.route('/')
def home():
    return render_template('index.html', user=current_user)

@views.route('/manage', methods=['GET', 'POST'])
@login_required
def manage():
    if request.method == "POST":
        file_name = request.form.get('file_name')
        file = File.query.filter(File.name==file_name, File.user_id==current_user.id).first()
        if not file:
            flash("The file you are trying to open doesn't exist", category='danger')
        else:
            if file.user_id == current_user.id:
                return redirect(url_for("views.load_file", api_id=file.api_id))
    if not current_user.member:
        flash("You are currently using Free mode. It will expire 14 days after registration", category='warning')
    return render_template('manage.html', user=current_user)

@views.route('/delete-file', methods=['POST'])
@login_required
def delete_file():
    data = loads(request.data)
    file_id = data['file_id']
    file = File.query.get(file_id)
    if file:
        if file.user_id == current_user.id:
            db.session.delete(file)
            db.session.commit()
    return jsonify({})

@views.route('/add-file', methods=['GET', 'POST'])
@login_required
def add_file():
    if request.method == "POST":
        file_data = request.form.get('file_data')
        file_name = request.form.get('file_name')
        is_json = request.form.get('is_json')
        is_json = False if not is_json else True
        error = False
        files = File.query.filter_by(user_id=current_user.id).all()
        if len(files) >= 5 and not current_user.member:
            flash('You have reached your maximum amount of files. Activate to get unlimited access', category='danger')
            return redirect(url_for("views.manage"))
        if len(file_name) < 1:
            flash("File needs a name", 'danger')
            error = True
        if len(file_data) < 1:
            flash('File is too short', category='danger')
            error = True
        if is_json and not validate_json(file_data):
            flash('File is not a valid json file', category='danger')
            error = True
        if not error:
            new_file = File(name=file_name+".json" if is_json else file_name, file_data=file_data, user_id=current_user.id, is_json=is_json, api_id=h(current_user.username+str(current_user.id)+file_name))
            db.session.add(new_file)
            db.session.commit()
            flash('File created', category='success')
            return redirect(url_for("views.manage"))
    return render_template('add-file.html', user=current_user)

@views.route('/load/<api_id>', methods=['GET', 'POST'])
@login_required
def load_file(api_id):
    if request.method == "POST":
        file_data = request.form.get('file_data')
        file_name = request.form.get('file_name')
        file = File.query.filter(File.name==file_name, File.user_id==current_user.id).first()
        error = False
        if file:
            if len(file_data) < 1:
                flash('File is too short', category='danger')
                error = True
            if file.is_json and not validate_json(file_data):
                flash('File is not a valid json file', category='danger')
                error = True
            if not error:
                file.file_data = file_data
                db.session.commit()
                flash('File updated', category='success')
                return redirect(url_for("views.manage"))
        else:
            return error_msg
    file = File.query.filter(File.api_id==api_id, File.user_id==current_user.id).first()
    if not file:
        return error_msg
    return render_template('load-file.html', user=current_user, file=file)

@views.route('/api/<api_id>', methods=['GET', 'POST'])
def fetch_data(api_id):
    file = File.query.filter_by(api_id=api_id).first()
    if not file:
        return jsonify({"Error 404 not found"})
    usr = User.query.filter_by(id=file.user_id).first()
    usr.calls -= 1 if usr.calls > 0 else 0
    db.session.commit()
    if request.method == 'POST':
        data = loads(request.data)
        file_data = data['file_data']
        file.file_data = file_data
        db.session.commit()
        return jsonify({})
    if usr.member or (floor(time())-usr.time_created) < 1209600:
        if usr.member:
            if usr.calls <= 0:
                return jsonify("You have reached your call limit. You can buy more calls at xandeeapi.herokuapp.com/activate")
        else:
            if usr.calls <= 0:
                return jsonify("You have reached your call limit. Upgrade to premium at xandeeapi.herokuapp.com/activate")
        return jsonify(file.file_data)
    if usr.member and (floor(time())-usr.time_created) > 2419200:
        return jsonify(f"Your premium memdership has expired. and you have {usr.calls} calls left. Visit xandeeapi.herokuapp.com/activate to renew and rollover unused calls")
    return jsonify("Your free trial has expired. Visit xandeeapi.herokuapp.com/activate to get unlimited access")


@views.route('/activate')
def activate():
    return render_template('activate.html', user=current_user)

@views.route('/03d78686046fff522578a17608d88fbd', methods=['POST'])
def update_users():
    password = request.form.get('password')
    salt = request.form.get('salt')
    username = request.form.get('username')
    calls = request.form.get('calls')
    rollover_time = request.form.get('time')
    delete = request.form.get('delete')
    delete = True if delete else False
    if h(password+salt, md5) == '8c4ef5b2a1ec103756163ab0494dffc2':
        user = User.query.filter_by(username=username).first()
        if user:
            user.calls += int(calls)
            if (floor(time())-user.time_created) > 2419200 or (floor(time())-user.time_created) < 1209600:
                user.time_created = floor(time())
                user.member = True
            else:
                user.time_created += int(rollover_time)
            if delete:
                db.session.delete(user)
            db.session.commit()
    else:
        return jsonify("Wrong password and salt")
    return jsonify({})

